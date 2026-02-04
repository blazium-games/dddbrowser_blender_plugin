"""
Add-on preferences for Blazium plugin.
"""
import bpy


class BLAZIUM_AddonPreferences(bpy.types.AddonPreferences):
    """Add-on preferences for storing persistent default settings."""
    
    bl_idname = __package__
    
    export_directory: bpy.props.StringProperty(
        name="Default Export Directory",
        description="Default directory for exports",
        subtype='DIR_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default=""
    )
    
    default_scene_name: bpy.props.StringProperty(
        name="Default Scene Name",
        description="Default name for exported scenes",
        default="Exported Scene"
    )
    
    default_scene_author: bpy.props.StringProperty(
        name="Default Scene Author",
        description="Default author for exported scenes",
        default=""
    )
    
    default_scene_rating: bpy.props.EnumProperty(
        name="Default Rating",
        description="Default content rating",
        items=[
            ('GENERAL', 'General', 'General audience'),
            ('MODERATE', 'Moderate', 'Moderate content'),
            ('ADULT', 'Adult', 'Adult content'),
        ],
        default='GENERAL'
    )
    
    default_base_url: bpy.props.StringProperty(
        name="Default Base URL",
        description="Default base URL for asset URIs",
        default=""
    )
    
    export_meshes_default: bpy.props.BoolProperty(
        name="Export Meshes (Default)",
        description="Default setting for mesh export",
        default=True
    )
    
    export_materials_default: bpy.props.BoolProperty(
        name="Export Materials (Default)",
        description="Default setting for material export",
        default=True
    )
    
    export_textures_default: bpy.props.BoolProperty(
        name="Export Textures (Default)",
        description="Default setting for texture export",
        default=True
    )
    
    export_scripts_default: bpy.props.BoolProperty(
        name="Export Scripts (Default)",
        description="Default setting for script export",
        default=False
    )
    
    generate_html_default: bpy.props.BoolProperty(
        name="Generate HTML (Default)",
        description="Default setting for HTML generation",
        default=False
    )
    
    def draw(self, context):
        """Draw preferences UI."""
        layout = self.layout
        
        layout.label(text="Default Export Settings")
        layout.prop(self, "export_directory")
        layout.prop(self, "default_scene_name")
        layout.prop(self, "default_scene_author")
        layout.prop(self, "default_scene_rating")
        layout.prop(self, "default_base_url")
        
        layout.separator()
        layout.label(text="Default Export Options")
        layout.prop(self, "export_meshes_default")
        layout.prop(self, "export_materials_default")
        layout.prop(self, "export_textures_default")
        layout.prop(self, "export_scripts_default")
        layout.prop(self, "generate_html_default")


def register():
    bpy.utils.register_class(BLAZIUM_AddonPreferences)


def unregister():
    bpy.utils.unregister_class(BLAZIUM_AddonPreferences)

