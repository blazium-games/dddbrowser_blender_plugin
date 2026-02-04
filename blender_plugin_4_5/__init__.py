import importlib
import sys
import os
from itertools import groupby

bl_info = {
    "name": "Blazium Scene Exporter",
    "author": "DDDBrowser Team",
    "version": (1, 1, 0),
    "blender": (4, 5, 0),
    "location": "Properties > Scene > Blazium Scene Export",
    "description": "Export Blender scenes to Blazium/DDDBrowser format (OBJ, MTL, JSON). Blender 4.5.",
    "category": "Import-Export",
}

# get folder name
__folder_name__ = __name__
__dict__ = {}
addon_dir = os.path.dirname(__file__)

# get all .py file paths
py_paths = [
    os.path.join(root, f)
    for root, dirs, files in os.walk(addon_dir)
    for f in sorted(files)
    if f.endswith(".py") and f != "__init__.py" and f != "test.py"
]

for path in py_paths:
    name = os.path.basename(path)[:-3]
    correct_path = path.replace("\\", "/")
    # split path with folder name
    dir_list = [
        list(g)
        for k, g in groupby(correct_path.split("/"), lambda x: x == __folder_name__)
        if not k
    ]
    # combine path and make dict like this: 'name:folder.name'
    if "preset" not in dir_list[-1]:
        r_name_raw = __folder_name__ + "." + ".".join(dir_list[-1])
        __dict__[name] = r_name_raw[:-3]

# auto reload
for name in __dict__.values():
    if name in sys.modules:
        importlib.reload(sys.modules[name])
    else:
        globals()[name] = importlib.import_module(name)
        setattr(globals()[name], "modules", __dict__)


def register_scene_properties():
    """Register custom properties on bpy.types.Scene."""
    import bpy
    
    bpy.types.Scene.blazium_scene_name = bpy.props.StringProperty(
        name="Scene Name",
        description="Name of the exported scene",
        default="Exported Scene"
    )
    
    bpy.types.Scene.blazium_scene_author = bpy.props.StringProperty(
        name="Scene Author",
        description="Author of the scene",
        default=""
    )
    
    bpy.types.Scene.blazium_scene_description = bpy.props.StringProperty(
        name="Scene Description",
        description="Description of the scene",
        default=""
    )
    
    bpy.types.Scene.blazium_scene_id = bpy.props.StringProperty(
        name="Scene ID",
        description="Unique identifier for the scene (auto-generated if empty)",
        default=""
    )
    
    bpy.types.Scene.blazium_scene_rating = bpy.props.EnumProperty(
        name="Rating",
        description="Content rating",
        items=[
            ('GENERAL', 'General', 'General audience'),
            ('MODERATE', 'Moderate', 'Moderate content'),
            ('ADULT', 'Adult', 'Adult content'),
        ],
        default='GENERAL'
    )
    
    bpy.types.Scene.blazium_scene_version = bpy.props.StringProperty(
        name="Version",
        description="Scene version",
        default="1.0"
    )
    
    bpy.types.Scene.blazium_schema_version = bpy.props.StringProperty(
        name="Schema Version",
        description="Scene schema version",
        default="1.0"
    )
    
    bpy.types.Scene.blazium_thumbnail_url = bpy.props.StringProperty(
        name="Thumbnail URL",
        description="URL to scene thumbnail image",
        default=""
    )


def unregister_scene_properties():
    """Unregister custom scene properties."""
    import bpy
    
    del bpy.types.Scene.blazium_scene_name
    del bpy.types.Scene.blazium_scene_author
    del bpy.types.Scene.blazium_scene_description
    del bpy.types.Scene.blazium_scene_id
    del bpy.types.Scene.blazium_scene_rating
    del bpy.types.Scene.blazium_scene_version
    del bpy.types.Scene.blazium_schema_version
    del bpy.types.Scene.blazium_thumbnail_url


def register():
    register_scene_properties()
    for module_name in __dict__.values():
        if module_name in sys.modules and hasattr(sys.modules[module_name], "register"):
            try:
                sys.modules[module_name].register()
            except ValueError:
                pass


def unregister():
    for module_name in reversed(list(__dict__.values())):
        if module_name in sys.modules and hasattr(sys.modules[module_name], "unregister"):
            try:
                sys.modules[module_name].unregister()
            except:
                pass
    unregister_scene_properties()


if __name__ == "__main__":
    register()
