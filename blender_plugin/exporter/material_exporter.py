"""
Material export functionality for converting Blender materials to MTL format.
"""
import bpy
import os
import mathutils

def sanitize_filename(name):
    """Sanitize a filename to be safe for filesystem."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    name = name.strip('. ')
    return name

def get_material_color(material):
    """Get base color from material (from Principled BSDF or default).
    
    Args:
        material: bpy.types.Material
        
    Returns:
        mathutils.Color: Base color (RGB)
    """
    if not material.use_nodes:
        # Fallback to material color
        return material.diffuse_color
    
    # Look for Principled BSDF node
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            base_color_input = node.inputs.get('Base Color')
            if base_color_input:
                if base_color_input.links:
                    # Connected to another node, try to get default value
                    return mathutils.Color(base_color_input.default_value[:3])
                else:
                    # Direct color value
                    return mathutils.Color(base_color_input.default_value[:3])
        
        elif node.type == 'BSDF_DIFFUSE':
            color_input = node.inputs.get('Color')
            if color_input:
                if color_input.links:
                    return mathutils.Color(color_input.default_value[:3])
                else:
                    return mathutils.Color(color_input.default_value[:3])
    
    # Fallback to material diffuse color
    return material.diffuse_color

def get_material_specular(material):
    """Get specular color/intensity from material.
    
    Args:
        material: bpy.types.Material
        
    Returns:
        mathutils.Color: Specular color
    """
    if not material.use_nodes:
        return mathutils.Color((0.5, 0.5, 0.5))
    
    # Look for Principled BSDF
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            specular_input = node.inputs.get('Specular')
            if specular_input:
                spec_value = specular_input.default_value
                # Specular is a single value in Principled, convert to color
                return mathutils.Color((spec_value, spec_value, spec_value))
    
    return mathutils.Color((0.5, 0.5, 0.5))

def get_material_roughness(material):
    """Get roughness value from material (for shininess conversion).
    
    Args:
        material: bpy.types.Material
        
    Returns:
        float: Roughness value (0-1)
    """
    if not material.use_nodes:
        return 0.5
    
    # Look for Principled BSDF
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            roughness_input = node.inputs.get('Roughness')
            if roughness_input:
                return roughness_input.default_value
    
    return 0.5

def get_diffuse_texture(material):
    """Get diffuse texture image name from material.
    
    Args:
        material: bpy.types.Material
        
    Returns:
        str: Image name (sanitized) or None
    """
    if not material.use_nodes:
        return None
    
    # Look for Principled BSDF
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            base_color_input = node.inputs.get('Base Color')
            if base_color_input and base_color_input.links:
                input_node = base_color_input.links[0].from_node
                if input_node.type == 'TEX_IMAGE' and input_node.image:
                    return sanitize_filename(input_node.image.name)
        
        elif node.type == 'BSDF_DIFFUSE':
            color_input = node.inputs.get('Color')
            if color_input and color_input.links:
                input_node = color_input.links[0].from_node
                if input_node.type == 'TEX_IMAGE' and input_node.image:
                    return sanitize_filename(input_node.image.name)
        
        elif node.type == 'TEX_IMAGE' and node.image:
            # Direct image texture node
            return sanitize_filename(node.image.name)
    
    return None

def roughness_to_shininess(roughness):
    """Convert roughness (0-1) to shininess (Ns) for MTL.
    
    Args:
        roughness: float - Roughness value (0-1)
        
    Returns:
        float: Shininess value (Ns, typically 0-1000)
    """
    # Inverse relationship: low roughness = high shininess
    # Map 0.0 roughness -> 1000 shininess, 1.0 roughness -> 0 shininess
    return (1.0 - roughness) * 1000.0

def get_alpha(material):
    """Get alpha/transparency value from material.
    
    Args:
        material: bpy.types.Material
        
    Returns:
        float: Alpha value (0-1)
    """
    if not material.use_nodes:
        return 1.0 - material.diffuse_color[3] if len(material.diffuse_color) > 3 else 1.0
    
    # Look for Principled BSDF
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            alpha_input = node.inputs.get('Alpha')
            if alpha_input:
                return alpha_input.default_value
    
    return 1.0

def export_material_to_mtl(blender_material, output_path, textures_dict=None, textures_dir=None):
    """Export a Blender material to MTL format.
    
    Args:
        blender_material: bpy.types.Material
        output_path: str - Directory to save MTL file (should be meshes_dir)
        textures_dict: dict - Mapping of texture names to filepaths
        textures_dir: str - Directory where textures are stored (same as output_path for co-location)
        
    Returns:
        str: Path to exported MTL file, or None if export failed
    """
    if not blender_material:
        return None
    
    if textures_dict is None:
        textures_dict = {}
    
    # Textures are co-located with MTL files (in meshes_dir)
    if textures_dir is None:
        textures_dir = output_path
    
    # Generate filename
    material_name = blender_material.name
    sanitized_name = sanitize_filename(material_name)
    filepath = os.path.join(output_path, f"{sanitized_name}.mtl")
    
    try:
        os.makedirs(output_path, exist_ok=True)
        
        # Get material properties
        base_color = get_material_color(blender_material)
        specular = get_material_specular(blender_material)
        roughness = get_material_roughness(blender_material)
        shininess = roughness_to_shininess(roughness)
        alpha = get_alpha(blender_material)
        texture_name = get_diffuse_texture(blender_material)
        
        # Write MTL file
        with open(filepath, 'w') as f:
            f.write(f"# Blender 3.6 LTS MTL File: '{blender_material.name}'\n")
            f.write(f"# www.blender.org\n\n")
            f.write(f"newmtl {sanitized_name}\n")
            
            # Ambient color (Ka) - use base color
            f.write(f"Ka {base_color.r:.6f} {base_color.g:.6f} {base_color.b:.6f}\n")
            
            # Diffuse color (Kd) - use base color
            f.write(f"Kd {base_color.r:.6f} {base_color.g:.6f} {base_color.b:.6f}\n")
            
            # Specular color (Ks) - use specular
            f.write(f"Ks {specular.r:.6f} {specular.g:.6f} {specular.b:.6f}\n")
            
            # Shininess (Ns)
            f.write(f"Ns {shininess:.6f}\n")
            
            # Transparency (Tr) - 1.0 = opaque, 0.0 = transparent
            f.write(f"Tr {alpha:.6f}\n")
            f.write(f"d {alpha:.6f}\n")  # Also write 'd' (dissolve)
            
            # Illumination model (illum) - 2 = Phong
            f.write(f"illum 2\n")
            
            # Diffuse texture map (map_Kd)
            # Textures are in same directory as MTL files, so use just filename
            # This matches DDDBrowser's isSafeRelativePath which rejects paths with ".."
            if texture_name:
                # Get texture filepath from textures_dict
                texture_path = textures_dict.get(texture_name)
                if texture_path:
                    # Use just filename (textures are co-located with MTL files)
                    # This ensures paths are safe relative paths (no ".." components)
                    texture_filename = os.path.basename(texture_path)
                    f.write(f"map_Kd {texture_filename}\n")
        
        return filepath
    except Exception:
        return None

def export_all_materials(materials, output_path, textures_dict=None, textures_dir=None):
    """Export all materials to MTL files.
    
    Args:
        materials: list of bpy.types.Material
        output_path: str - Directory to save MTL files (should be meshes_dir)
        textures_dict: dict - Mapping of texture names to filepaths
        textures_dir: str - Directory where textures are stored (same as output_path for co-location)
        
    Returns:
        dict: Mapping of material name to exported MTL filepath
    """
    materials_dict = {}
    
    for material in materials:
        if material:
            filepath = export_material_to_mtl(material, output_path, textures_dict, textures_dir)
            if filepath:
                material_name = sanitize_filename(material.name)
                materials_dict[material_name] = filepath
    
    return materials_dict

