"""
Light export functionality for converting Blender lights to scene format.
"""
import bpy
import mathutils
import math
from . import transform_utils

def export_light_instance(blender_light, transform=None):
    """Export a Blender light to scene format light instance.
    
    Args:
        blender_light: bpy.types.Object with type='LIGHT'
        transform: tuple (position, rotation, scale) or None to extract from object
        
    Returns:
        dict: Light instance dict following lightProperties schema, or None if invalid
    """
    if not blender_light or blender_light.type != 'LIGHT':
        return None
    
    light_data = blender_light.data
    if not light_data:
        return None
    
    # Get transform if not provided
    if transform is None:
        position, rotation, scale = transform_utils.get_object_transform(blender_light)
    else:
        position, rotation, scale = transform
    
    # Determine light type
    light_type = light_data.type
    
    # Map Blender light types to scene format
    type_map = {
        'POINT': 'pointLight',
        'SUN': 'directionalLight',
        'SPOT': 'spotLight',
        'AREA': 'pointLight'  # Convert area lights to point lights
    }
    
    scene_light_type = type_map.get(light_type, 'pointLight')
    
    # Build light properties
    light_props = {}
    
    # Color (RGB 0-1)
    light_color = light_data.color
    light_props['color'] = {
        'x': light_color.r,
        'y': light_color.g,
        'z': light_color.b
    }
    
    # Intensity (Energy in Blender)
    # Blender's energy is typically 0-100+, scene format expects > 0
    energy = light_data.energy
    if light_type == 'SUN':
        # Sun lights often have higher energy values
        light_props['intensity'] = max(0.1, energy / 10.0)
    else:
        light_props['intensity'] = max(0.1, energy)
    
    # Enabled - check if object is visible
    light_props['enabled'] = not blender_light.hide_viewport
    
    # Range (Distance for point/spot lights)
    if light_type in ('POINT', 'SPOT', 'AREA'):
        if hasattr(light_data, 'distance'):
            light_props['range'] = max(0.1, light_data.distance)
        else:
            # Default range if not specified
            light_props['range'] = 25.0
    
    # Attenuation (for point/spot lights)
    if light_type in ('POINT', 'SPOT', 'AREA'):
        # Blender uses linear falloff, convert to constant/linear/quadratic
        # Default attenuation values
        light_props['attenuation'] = {
            'constant': 1.0,
            'linear': 0.09,
            'quadratic': 0.032
        }
        
        # Map Blender's falloff type if available
        if hasattr(light_data, 'falloff_type'):
            falloff = light_data.falloff_type
            if falloff == 'INVERSE_LINEAR':
                light_props['attenuation'] = {
                    'constant': 1.0,
                    'linear': 0.1,
                    'quadratic': 0.0
                }
            elif falloff == 'INVERSE_SQUARE':
                light_props['attenuation'] = {
                    'constant': 1.0,
                    'linear': 0.0,
                    'quadratic': 0.1
                }
    
    # Direction (for directional/spot lights)
    if light_type in ('SUN', 'SPOT'):
        # Get light direction from object rotation
        # In Blender, lights point in -Z direction by default
        direction_vec = mathutils.Vector((0, 0, -1))
        direction_vec.rotate(blender_light.matrix_world.to_3x3())
        direction_vec.normalize()
        
        light_props['direction'] = {
            'x': direction_vec.x,
            'y': direction_vec.y,
            'z': direction_vec.z
        }
    
    # Cutoff/OuterCutoff (for spot lights)
    if light_type == 'SPOT':
        spot_size = light_data.spot_size  # Angle in radians
        spot_blend = light_data.spot_blend  # Blend factor 0-1
        
        # Convert spot size to degrees
        cutoff_degrees = math.degrees(spot_size)
        # Outer cutoff is typically slightly larger
        outer_cutoff_degrees = cutoff_degrees * (1.0 + spot_blend)
        
        light_props['cutoff'] = max(0.0, min(90.0, cutoff_degrees))
        light_props['outerCutoff'] = max(0.0, min(90.0, outer_cutoff_degrees))
    
    # Shadow settings
    if hasattr(light_data, 'use_shadow'):
        light_props['shadowEnabled'] = light_data.use_shadow
        
        if light_data.use_shadow:
            # Shadow bias
            if hasattr(light_data, 'shadow_buffer_bias'):
                light_props['shadowBias'] = max(0.0, light_data.shadow_buffer_bias)
            else:
                light_props['shadowBias'] = 0.01
            
            # Shadow map resolution
            if hasattr(light_data, 'shadow_buffer_soft'):
                # Approximate resolution based on softness
                light_props['shadowMapResolution'] = 2048
            else:
                light_props['shadowMapResolution'] = 2048
            
            # Shadow ortho size (for directional lights)
            if light_type == 'SUN':
                if hasattr(light_data, 'shadow_buffer_clip_start') and hasattr(light_data, 'shadow_buffer_clip_end'):
                    clip_range = light_data.shadow_buffer_clip_end - light_data.shadow_buffer_clip_start
                    light_props['shadowOrthoSize'] = max(1.0, clip_range)
                else:
                    light_props['shadowOrthoSize'] = 100.0
    
    # Build instance dict
    instance = {
        'id': blender_light.name.replace(' ', '_').replace('.', '_'),
        'type': scene_light_type,
        'position': position,
        'rotation': rotation,
        'scale': scale,
        'light': light_props
    }
    
    return instance

def export_all_lights(objects):
    """Export all light objects to scene format.
    
    Args:
        objects: list of bpy.types.Object
        
    Returns:
        list: List of light instance dicts
    """
    light_instances = []
    
    for obj in objects:
        if obj.type == 'LIGHT':
            light_instance = export_light_instance(obj)
            if light_instance:
                light_instances.append(light_instance)
    
    return light_instances

