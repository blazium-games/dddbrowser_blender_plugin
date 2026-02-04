"""
UI panel for Blazium scene export settings.
"""
import bpy


class BLAZIUM_PT_export_panel(bpy.types.Panel):
    """UI panel for Blazium scene export."""
    
    bl_label = "Blazium Scene Export"
    bl_idname = "BLAZIUM_PT_export_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    
    def draw(self, context):
        """Draw the UI panel."""
        layout = self.layout
        scene = context.scene
        export_settings = scene.blazium_export_settings
        
        # Scene Metadata Section
        box = layout.box()
        box.label(text="Scene Metadata", icon='SCENE_DATA')
        box.prop(scene, "blazium_scene_name")
        box.prop(scene, "blazium_scene_author")
        box.prop(scene, "blazium_scene_description")
        box.prop(scene, "blazium_scene_id")
        box.prop(scene, "blazium_scene_rating")
        box.prop(scene, "blazium_scene_version")
        box.prop(scene, "blazium_schema_version")
        box.prop(scene, "blazium_thumbnail_url")
        
        layout.separator()
        
        # Export Options Section
        box = layout.box()
        box.label(text="Export Options", icon='EXPORT')
        box.prop(export_settings, "export_meshes", text="Export Meshes (OBJ)")
        box.prop(export_settings, "export_materials", text="Export Materials (MTL)")
        box.prop(export_settings, "export_textures", text="Export Textures")
        box.prop(export_settings, "export_scripts", text="Export Scripts")
        box.prop(export_settings, "generate_html", text="Generate HTML Wrapper")
        
        layout.separator()
        
        # Asset URL Configuration
        box = layout.box()
        box.label(text="Asset URL Configuration", icon='URL')
        box.prop(export_settings, "base_url")
        box.label(text="Base URL for constructing asset URIs", icon='INFO')
        
        layout.separator()
        
        # Export Directory
        box = layout.box()
        box.label(text="Export Directory", icon='FILEBROWSER')
        row = box.row()
        row.operator("blazium.export_directory", icon='FILEBROWSER', text="Select Export Directory")
        if export_settings.export_directory:
            box.label(text=f"Current: {export_settings.export_directory}", icon='FILE_FOLDER')
        
        layout.separator()
        
        # Export Button (Prominent)
        row = layout.row()
        row.scale_y = 2.0
        row.operator("export_scene.blazium_scene", icon='EXPORT', text="Export Blazium Scene")
        
        # Scene statistics (optional)
        if context.scene.objects:
            mesh_count = sum(1 for obj in context.scene.objects if obj.type == 'MESH')
            light_count = sum(1 for obj in context.scene.objects if obj.type == 'LIGHT')
            if mesh_count > 0 or light_count > 0:
                layout.separator()
                box = layout.box()
                box.label(text="Scene Statistics", icon='INFO')
                box.label(text=f"Meshes: {mesh_count}, Lights: {light_count}")


def register():
    bpy.utils.register_class(BLAZIUM_PT_export_panel)


def unregister():
    bpy.utils.unregister_class(BLAZIUM_PT_export_panel)

