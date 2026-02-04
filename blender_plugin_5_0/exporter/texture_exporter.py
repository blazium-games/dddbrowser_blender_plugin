"""
Texture export functionality for converting Blender images to supported formats.
"""
import bpy
import os

# Supported texture formats (whitelist)
SUPPORTED_FORMATS = {'PNG', 'JPG', 'JPEG', 'TGA'}

def sanitize_filename(name):
    """Sanitize a filename to be safe for filesystem.
    
    Args:
        name: str - Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    return name

def export_texture(blender_image, output_path, target_format='PNG'):
    """Export a Blender image to a supported format.
    
    Args:
        blender_image: bpy.types.Image - Blender image to export
        output_path: str - Directory to save the texture
        target_format: str - Target format (PNG, JPG, JPEG, TGA)
        
    Returns:
        str: Path to exported texture file, or None if export failed
    """
    if not blender_image:
        return None
    
    # Validate format
    format_upper = target_format.upper()
    if format_upper not in SUPPORTED_FORMATS:
        format_upper = 'PNG'
    
    # Map format to file extension
    format_map = {
        'PNG': '.png',
        'JPG': '.jpg',
        'JPEG': '.jpg',
        'TGA': '.tga'
    }
    
    ext = format_map[format_upper]
    
    # Generate filename from image name
    image_name = blender_image.name
    if not image_name or image_name == "Render Result":
        image_name = "texture"
    
    # Remove Blender's image extension if present
    base_name = os.path.splitext(image_name)[0]
    sanitized_name = sanitize_filename(base_name)
    
    # Generate full filepath
    filename = f"{sanitized_name}{ext}"
    filepath = os.path.join(output_path, filename)
    
    try:
        # Ensure directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Save image
        # Note: For packed images, we may need to unpack first
        # For external images, we can copy or save directly
        if blender_image.packed_file:
            # Unpack if packed
            blender_image.unpack(method='USE_LOCAL')
        
        # Save the image
        blender_image.save_render(filepath=filepath)
        
        return filepath
    except Exception:
        return None

def collect_textures_from_materials(materials):
    """Collect all unique textures from materials.
    
    Args:
        materials: list of bpy.types.Material
        
    Returns:
        list: List of unique bpy.types.Image objects
    """
    images = set()
    
    for material in materials:
        # Blender 5.0: use_nodes removed; getattr for compatibility.
        if not material or not getattr(material, 'use_nodes', True):
            continue
        
        # Traverse node tree to find image textures
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                images.add(node.image)
            elif node.type == 'BSDF_PRINCIPLED':
                # Check base color input
                if node.inputs['Base Color'].links:
                    input_node = node.inputs['Base Color'].links[0].from_node
                    if input_node.type == 'TEX_IMAGE' and input_node.image:
                        images.add(input_node.image)
    
    return list(images)

def export_all_textures(materials, output_path, target_format='PNG'):
    """Export all textures from materials to files.
    
    Args:
        materials: list of bpy.types.Material
        output_path: str - Directory to save textures
        target_format: str - Target format (PNG, JPG, JPEG, TGA)
        
    Returns:
        dict: Mapping of image name/ID to exported filepath
    """
    textures_dict = {}
    
    # Collect unique images
    images = collect_textures_from_materials(materials)
    
    # Export each image
    for image in images:
        filepath = export_texture(image, output_path, target_format)
        if filepath:
            # Use image name as key
            image_id = sanitize_filename(image.name)
            textures_dict[image_id] = filepath
    
    return textures_dict

