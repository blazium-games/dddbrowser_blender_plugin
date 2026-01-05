"""
Operators for Blazium addon.
"""
import bpy


class BLAZIUM_OT_export_directory(bpy.types.Operator):
    """Open file browser to select export directory."""
    
    bl_idname = "blazium.export_directory"
    bl_label = "Select Export Directory"
    bl_description = "Open file browser to select export directory"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory: bpy.props.StringProperty(
        name="Directory",
        description="Export directory",
        subtype='DIR_PATH',
        default=""
    )
    
    def invoke(self, context, event):
        """Invoke the operator (opens file browser)."""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        """Execute the operator."""
        if self.directory:
            context.scene.blazium_export_settings.export_directory = self.directory
            self.report({'INFO'}, f"Export directory set to: {self.directory}")
        return {'FINISHED'}


class BLAZIUM_OT_show_export_panel(bpy.types.Operator):
    """Switch to Properties area and show Blazium export panel."""
    
    bl_idname = "blazium.show_export_panel"
    bl_label = "Show Export Settings"
    bl_description = "Open the Blazium export settings panel"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Switch to Properties area."""
        # Try to switch to Properties area
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()
                break
        else:
            # If no Properties area visible, inform user
            self.report({'INFO'}, "Open Properties panel (N key) to see Blazium Export Settings")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BLAZIUM_OT_export_directory)
    bpy.utils.register_class(BLAZIUM_OT_show_export_panel)


def unregister():
    bpy.utils.unregister_class(BLAZIUM_OT_show_export_panel)
    bpy.utils.unregister_class(BLAZIUM_OT_export_directory)

