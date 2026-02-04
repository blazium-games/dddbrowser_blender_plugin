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
    # Blender 5.0: use_nodes removed; materials always use nodes. getattr for compatibility.
    if not getattr(material, 'use_nodes', True):
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
    if not getattr(material, 'use_nodes', True):
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
    if not getattr(material, 'use_nodes', True):
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
    if not getattr(material, 'use_nodes', True):
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

def get_metallic_texture(material):
    """Get metallic texture image name from Principled BSDF Metallic input.
    
    Returns:
        str: Sanitized image name or None
    """
    if not getattr(material, 'use_nodes', True):
        return None
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            metallic_input = node.inputs.get('Metallic')
            if metallic_input and metallic_input.links:
                input_node = metallic_input.links[0].from_node
                if input_node.type == 'TEX_IMAGE' and input_node.image:
                    return sanitize_filename(input_node.image.name)
    return None

def get_normal_texture(material):
    """Get normal map image name from Principled BSDF Normal input (via NORMAL_MAP or direct TEX_IMAGE).
    
    Returns:
        str: Sanitized image name or None
    """
    if not getattr(material, 'use_nodes', True):
        return None
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            normal_input = node.inputs.get('Normal')
            if not normal_input or not normal_input.links:
                continue
            input_node = normal_input.links[0].from_node
            if input_node.type == 'NORMAL_MAP':
                color_input = input_node.inputs.get('Color')
                if color_input and color_input.links:
                    tex_node = color_input.links[0].from_node
                    if tex_node.type == 'TEX_IMAGE' and tex_node.image:
                        return sanitize_filename(tex_node.image.name)
            elif input_node.type == 'TEX_IMAGE' and input_node.image:
                return sanitize_filename(input_node.image.name)
    return None

def get_height_texture(material):
    """Get height/displacement texture image name from Displacement node Height input.
    
    Returns:
        str: Sanitized image name or None
    """
    if not getattr(material, 'use_nodes', True):
        return None
    for node in material.node_tree.nodes:
        if node.type == 'DISPLACEMENT':
            height_input = node.inputs.get('Height')
            if height_input and height_input.links:
                input_node = height_input.links[0].from_node
                if input_node.type == 'TEX_IMAGE' and input_node.image:
                    return sanitize_filename(input_node.image.name)
    return None

def get_ao_texture(material):
    """Get ambient occlusion texture by naming convention (image name contains 'ao' or 'occlusion').
    
    Returns:
        str: Sanitized image name or None
    """
    if not getattr(material, 'use_nodes', True):
        return None
    name_lower = None
    for node in material.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image:
            name_lower = node.image.name.lower()
            if 'ao' in name_lower or 'occlusion' in name_lower:
                return sanitize_filename(node.image.name)
    return None

def get_roughness_texture(material):
    """Get roughness texture image name from Principled BSDF Roughness input.
    
    Returns:
        str: Sanitized image name or None
    """
    if not getattr(material, 'use_nodes', True):
        return None
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            roughness_input = node.inputs.get('Roughness')
            if roughness_input and roughness_input.links:
                input_node = roughness_input.links[0].from_node
                if input_node.type == 'TEX_IMAGE' and input_node.image:
                    return sanitize_filename(input_node.image.name)
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
    if not getattr(material, 'use_nodes', True):
        return 1.0 - material.diffuse_color[3] if len(material.diffuse_color) > 3 else 1.0
    
    # Look for Principled BSDF
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            alpha_input = node.inputs.get('Alpha')
            if alpha_input:
                return alpha_input.default_value
    
    return 1.0

def export_material_to_mtl(blender_material, output_path, textures_dict=None, textures_dir=None, export_pbr_maps=True):
    """Export a Blender material to MTL format.
    
    Args:
        blender_material: bpy.types.Material
        output_path: str - Directory to save MTL file (should be meshes_dir)
        textures_dict: dict - Mapping of texture names to filepaths
        textures_dir: str - Directory where textures are stored (same as output_path for co-location)
        export_pbr_maps: bool - If True, write PBR map lines (metallic, normal, AO, height, roughness)
        
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
            
            # PBR maps (metallic, normal, AO, height, roughness)
            if export_pbr_maps:
                for map_name, mtl_key in [
                    (get_metallic_texture(blender_material), "map_Pm"),
                    (get_normal_texture(blender_material), "norm"),
                    (get_ao_texture(blender_material), "map_Ka"),
                    (get_height_texture(blender_material), "map_disp"),
                    (get_roughness_texture(blender_material), "map_Pr"),
                ]:
                    if map_name:
                        texture_path = textures_dict.get(map_name)
                        if texture_path:
                            texture_filename = os.path.basename(texture_path)
                            f.write(f"{mtl_key} {texture_filename}\n")
        
        return filepath
    except Exception:
        return None

def export_all_materials(materials, output_path, textures_dict=None, textures_dir=None, export_pbr_maps=True):
    """Export all materials to MTL files.
    
    Args:
        materials: list of bpy.types.Material
        output_path: str - Directory to save MTL files (should be meshes_dir)
        textures_dict: dict - Mapping of texture names to filepaths
        textures_dir: str - Directory where textures are stored (same as output_path for co-location)
        export_pbr_maps: bool - If True, write PBR map lines in MTL files
        
    Returns:
        dict: Mapping of material name to exported MTL filepath
    """
    materials_dict = {}
    
    for material in materials:
        if material:
            filepath = export_material_to_mtl(material, output_path, textures_dict, textures_dir, export_pbr_maps=export_pbr_maps)
            if filepath:
                material_name = sanitize_filename(material.name)
                materials_dict[material_name] = filepath
    
    return materials_dict

