"""
Scene JSON construction module for building scene JSON following the schema.
"""
import json
import os
from . import mesh_exporter
from . import material_exporter
from . import texture_exporter
from . import light_exporter
from . import transform_utils

def sanitize_filename(name):
    """Sanitize a filename to be safe for filesystem."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    name = name.strip('. ')
    return name

def build_asset_uri(filepath, base_url, export_dir):
    """Build asset URI from filepath and base URL.
    
    Args:
        filepath: str - Local filepath (absolute or relative)
        base_url: str - Base URL (if empty, use relative path from export_dir)
        export_dir: str - Export directory root
        
    Returns:
        str: URI string
    """
    if base_url:
        # Use base URL + relative path from export_dir
        try:
            # Get relative path from export_dir
            rel_path = os.path.relpath(filepath, export_dir)
            # Normalize path separators (use forward slashes for URLs)
            rel_path = rel_path.replace('\\', '/')
            # Remove trailing slash from base_url if present
            base = base_url.rstrip('/')
            return f"{base}/{rel_path}"
        except ValueError:
            # If paths are on different drives (Windows), just use filename
            filename = os.path.basename(filepath)
            base = base_url.rstrip('/')
            return f"{base}/{filename}"
    else:
        # Use relative path from export_dir
        try:
            rel_path = os.path.relpath(filepath, export_dir)
            rel_path = rel_path.replace('\\', '/')
            return rel_path
        except ValueError:
            # If paths are on different drives (Windows), just use filename
            return os.path.basename(filepath)

def build_scene_json(scene_data, export_settings):
    """Build scene JSON following the schema.
    
    Args:
        scene_data: dict with keys:
            - objects: list of bpy.types.Object
            - materials: list of bpy.types.Material (optional)
            - textures: list of bpy.types.Image (optional)
        export_settings: dict with keys:
            - export_directory: str
            - scene_name: str
            - scene_author: str
            - scene_description: str
            - scene_id: str
            - scene_rating: str
            - scene_version: str
            - schema_version: str
            - thumbnail_url: str
            - base_url: str
            - export_meshes: bool
            - export_materials: bool
            - export_textures: bool
            - export_scripts: bool
    
    Returns:
        dict: Scene JSON dict ready for serialization
    """
    export_dir = export_settings['export_directory']
    base_url = export_settings.get('base_url', '')
    
    # Create subdirectories
    # MTL files must be in same directory as OBJ files for mtllib references
    meshes_dir = os.path.join(export_dir, 'meshes')
    textures_dir = os.path.join(export_dir, 'meshes')  # Textures co-located with MTL files
    
    os.makedirs(meshes_dir, exist_ok=True)
    os.makedirs(textures_dir, exist_ok=True)
    
    # Collect all objects
    objects = scene_data.get('objects', [])
    mesh_objects = [obj for obj in objects if obj.type == 'MESH']
    light_objects = [obj for obj in objects if obj.type == 'LIGHT']
    
    # Collect all unique materials
    all_materials = set()
    for obj in mesh_objects:
        if obj.data and obj.data.materials:
            for mat in obj.data.materials:
                if mat:
                    all_materials.add(mat)
    all_materials = list(all_materials)
    
    # Export textures first (needed for materials)
    textures_dict = {}
    if export_settings.get('export_textures', True) and all_materials:
        textures_dict = texture_exporter.export_all_textures(
            all_materials,
            textures_dir,
            target_format='PNG'
        )
    
    # Export materials (to meshes_dir so they're co-located with OBJ files)
    materials_dict = {}
    if export_settings.get('export_materials', True) and all_materials:
        materials_dict = material_exporter.export_all_materials(
            all_materials,
            meshes_dir,  # Export MTL files to meshes directory
            textures_dict=textures_dict,
            textures_dir=textures_dir  # Pass textures directory for path calculation
        )
    
    # Export meshes
    meshes_dict = {}
    if export_settings.get('export_meshes', True) and mesh_objects:
        meshes_dict = mesh_exporter.export_all_meshes(
            mesh_objects,
            meshes_dir,
            materials_dict=materials_dict
        )
    
    # Build assets array
    assets = []
    
    # Model assets
    for asset_id, filepath in meshes_dict.items():
        assets.append({
            'id': asset_id,
            'type': 'model',
            'uri': build_asset_uri(filepath, base_url, export_dir),
            'mediaType': 'model/obj'
        })
    
    # Material assets
    for material_name, filepath in materials_dict.items():
        assets.append({
            'id': material_name,
            'type': 'material',
            'uri': build_asset_uri(filepath, base_url, export_dir),
            'mediaType': 'model/mtl'
        })
    
    # Texture assets
    for texture_id, filepath in textures_dict.items():
        # Determine media type from extension
        ext = os.path.splitext(filepath)[1].lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tga': 'image/tga'
        }
        media_type = media_type_map.get(ext, 'image/png')
        
        assets.append({
            'id': texture_id,
            'type': 'texture',
            'uri': build_asset_uri(filepath, base_url, export_dir),
            'mediaType': media_type
        })
    
    # Build instances array
    instances = []
    
    # Model instances
    for obj in mesh_objects:
        # Check if this object was exported (using sanitized name)
        obj_name_sanitized = sanitize_filename(obj.name)
        if obj_name_sanitized in meshes_dict:
            asset_id = obj_name_sanitized
            position, rotation, scale = transform_utils.get_object_transform(obj)
            
            instance = {
                'id': asset_id,
                'type': 'model',
                'asset': asset_id,
                'position': position,
                'rotation': rotation,
                'scale': scale
            }
            
            instances.append(instance)
    
    # Light instances
    light_instances = light_exporter.export_all_lights(light_objects)
    instances.extend(light_instances)
    
    # Build scene JSON
    scene_json = {
        'name': export_settings.get('scene_name', 'Exported Scene'),
        'version': export_settings.get('scene_version', '1.0'),
        'schemaVersion': export_settings.get('schema_version', '1.0'),
        'assets': assets
    }
    
    # Add optional metadata
    if export_settings.get('scene_description'):
        scene_json['description'] = export_settings['scene_description']
    
    if export_settings.get('scene_id'):
        scene_json['id'] = export_settings['scene_id']
    elif not scene_json.get('id'):
        # Auto-generate ID from name
        scene_json['id'] = sanitize_filename(export_settings.get('scene_name', 'exported_scene')).lower()
    
    if export_settings.get('scene_author'):
        scene_json['author'] = export_settings['scene_author']
    
    if export_settings.get('scene_rating'):
        scene_json['rating'] = export_settings['scene_rating']
    
    if export_settings.get('thumbnail_url'):
        scene_json['thumbnail'] = export_settings['thumbnail_url']
    
    # Add instances (required if any exist)
    if instances:
        scene_json['instances'] = instances
    
    return scene_json

def write_scene_json(scene_json, output_path):
    """Write scene JSON to file.
    
    Args:
        scene_json: dict - Scene JSON dict
        output_path: str - Path to output JSON file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scene_json, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        return False

