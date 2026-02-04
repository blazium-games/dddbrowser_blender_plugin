"""
Main export operator for Blazium scene export.
"""
import bpy
import os
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper
from .. import scene_builder


class EXPORT_SCENE_OT_blazium_scene(bpy.types.Operator, ExportHelper):
    """Export Blender scene to Blazium/DDDBrowser format."""
    
    bl_idname = "export_scene.blazium_scene"
    bl_label = "Blazium Scene"
    bl_description = "Export current scene to Blazium/DDDBrowser format (OBJ, MTL, JSON)"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}
    
    filename_ext = ".json"
    
    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    export_directory: StringProperty(
        name="Export Directory",
        description="Directory to export assets to",
        default="",
        subtype='DIR_PATH'
    )
    
    def invoke(self, context, event):
        """Invoke the operator (opens file browser)."""
        return super().invoke(context, event)
    
    def draw(self, context):
        """Draw export settings in the file browser dialog."""
        layout = self.layout
        scene = context.scene
        export_settings = scene.blazium_export_settings
        
        # Build file list preview
        export_file_list = []
        if self.filepath:
            file_directory = os.path.dirname(self.filepath)
            file_prefix = os.path.basename(self.filepath)
            if file_prefix.endswith('.json'):
                file_prefix = file_prefix[:-5]
            
            # Scene JSON file
            export_file_list.append(f"{file_prefix}.json")
            
            # HTML wrapper
            if export_settings.generate_html:
                export_file_list.append("index.html")
            
            # Meshes directory (if exporting meshes)
            if export_settings.export_meshes:
                export_file_list.append("meshes/ (OBJ files)")
            
            # Materials (if exporting materials)
            if export_settings.export_materials:
                export_file_list.append("meshes/ (MTL files)")
            
            # Textures (if exporting textures)
            if export_settings.export_textures:
                export_file_list.append("meshes/ (texture files)")
        
        # Export Options Section
        box = layout.box()
        box.label(text="Export Options", icon='EXPORT')
        box.prop(export_settings, "export_meshes", text="Export Meshes (OBJ)")
        box.prop(export_settings, "export_materials", text="Export Materials (MTL)")
        box.prop(export_settings, "export_textures", text="Export Textures")
        box.prop(export_settings, "export_pbr_maps", text="Export PBR Maps")
        box.prop(export_settings, "export_scripts", text="Export Scripts")
        box.prop(export_settings, "generate_html", text="Generate HTML Wrapper")
        
        layout.separator()
        
        # Asset URL Configuration
        box = layout.box()
        box.label(text="Asset URL Configuration", icon='URL')
        box.prop(export_settings, "base_url")
        
        layout.separator()
        
        # Scene Metadata (collapsed by default)
        box = layout.box()
        box.prop(scene, "blazium_scene_name", text="Scene Name")
        box.prop(scene, "blazium_scene_author", text="Author")
        
        layout.separator()
        
        # Files to be exported preview
        if len(export_file_list) > 0:
            box = layout.box()
            box.label(text=f"Files to Export ({len(export_file_list)})", icon='FILEBROWSER')
            for filename in export_file_list:
                if self.filepath:
                    full_filepath = os.path.join(os.path.dirname(self.filepath), filename)
                    if os.path.exists(full_filepath) and not filename.endswith('/'):
                        box.row().label(text=f"{filename} (overwrite)", icon="ERROR")
                    else:
                        box.row().label(text=filename)
                else:
                    box.row().label(text=filename)
        else:
            box = layout.box()
            box.label(text="Select a file path to see export preview", icon='INFO')
    
    def execute(self, context):
        """Execute the export operation."""
        scene = context.scene
        
        # Get export directory from filepath (directory where scene.json will be saved)
        export_directory = os.path.dirname(self.filepath)
        
        # Validate export directory
        if not export_directory:
            self.report({'ERROR'}, "Export directory not set")
            return {'CANCELLED'}
        
        # Update scene export settings with export directory
        export_settings = scene.blazium_export_settings
        export_settings.export_directory = export_directory
        
        # Check if directory exists or can be created
        try:
            os.makedirs(export_directory, exist_ok=True)
            # Test write permissions
            test_file = os.path.join(export_directory, '.write_test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except:
                self.report({'ERROR'}, f"Cannot write to directory: {export_directory}")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Invalid export directory: {e}")
            return {'CANCELLED'}
        
        # Collect scene data
        objects = list(scene.objects)
        
        scene_data = {
            'objects': objects
        }
        
        # Prepare export settings dict
        export_settings_dict = {
            'export_directory': export_directory,
            'scene_name': scene.blazium_scene_name,
            'scene_author': scene.blazium_scene_author,
            'scene_description': scene.blazium_scene_description,
            'scene_id': scene.blazium_scene_id,
            'scene_rating': scene.blazium_scene_rating,
            'scene_version': scene.blazium_scene_version,
            'schema_version': scene.blazium_schema_version,
            'thumbnail_url': scene.blazium_thumbnail_url,
            'base_url': export_settings.base_url,
            'export_meshes': export_settings.export_meshes,
            'export_materials': export_settings.export_materials,
            'export_textures': export_settings.export_textures,
            'export_pbr_maps': export_settings.export_pbr_maps,
            'export_scripts': export_settings.export_scripts,
            'generate_html': export_settings.generate_html
        }
        
        try:
            # Build scene JSON
            scene_json = scene_builder.build_scene_json(scene_data, export_settings_dict)
            
            # Write scene JSON to the selected filepath
            if not scene_builder.write_scene_json(scene_json, self.filepath):
                self.report({'ERROR'}, "Failed to write scene.json")
                return {'CANCELLED'}
            
            # Generate HTML wrapper if requested
            if export_settings_dict['generate_html']:
                from .. import html_wrapper
                html_path = os.path.join(export_directory, 'index.html')
                if not html_wrapper.generate_html_wrapper(scene_json, export_settings_dict, html_path):
                    self.report({'WARNING'}, "Failed to generate HTML wrapper")
            
            # Update preferences with export directory
            # Use __package__ to get the addon name dynamically
            addon_name = __package__.split('.')[0] if __package__ else "blender"
            if addon_name in context.preferences.addons:
                prefs = context.preferences.addons[addon_name].preferences
                if hasattr(prefs, 'export_directory'):
                    prefs.export_directory = export_directory
            
            # Report success
            self.report({'INFO'}, f"Export completed successfully to {export_directory}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}


def menu_func_export(self, context):
    """Menu function to add export option to File > Export menu."""
    self.layout.operator(
        EXPORT_SCENE_OT_blazium_scene.bl_idname,
        text="Blazium Scene (.json)"
    )


def register():
    bpy.utils.register_class(EXPORT_SCENE_OT_blazium_scene)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(EXPORT_SCENE_OT_blazium_scene)

