"""
Export settings PropertyGroup for Blazium plugin.
"""
import bpy
from bpy.props import (
    BoolProperty,
    StringProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup


class BlaziumExportSettings(PropertyGroup):
    """Export settings data class."""
    
    export_meshes: BoolProperty(
        name="Export Meshes",
        description="Export mesh objects as OBJ files",
        default=True,
    )
    
    export_materials: BoolProperty(
        name="Export Materials",
        description="Export materials as MTL files",
        default=True,
    )
    
    export_textures: BoolProperty(
        name="Export Textures",
        description="Export textures as image files",
        default=True,
    )
    
    export_pbr_maps: BoolProperty(
        name="Export PBR Maps",
        description="Export PBR texture maps (metallic, normal, AO, height, roughness) in MTL files",
        default=True,
    )
    
    export_scripts: BoolProperty(
        name="Export Scripts",
        description="Export script files",
        default=False,
    )
    
    generate_html: BoolProperty(
        name="Generate HTML",
        description="Generate HTML wrapper file",
        default=False,
    )
    
    base_url: StringProperty(
        name="Base URL",
        description="Base URL for asset URIs (e.g., https://example.com/assets)",
        default="",
    )
    
    export_directory: StringProperty(
        name="Export Directory",
        description="Directory to export scene files",
        subtype='DIR_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default="",
    )


def register():
    bpy.utils.register_class(BlaziumExportSettings)
    bpy.types.Scene.blazium_export_settings = bpy.props.PointerProperty(type=BlaziumExportSettings)


def unregister():
    del bpy.types.Scene.blazium_export_settings
    bpy.utils.unregister_class(BlaziumExportSettings)

