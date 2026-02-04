"""
Main menu bar menu for Blazium addon.
"""
import bpy


class BLAZIUM_MT_main_menu(bpy.types.Menu):
    """Main Blazium menu in the top menu bar."""
    
    bl_idname = "BLAZIUM_MT_main_menu"
    bl_label = "Blazium"
    
    def draw(self, context):
        """Draw the menu items."""
        layout = self.layout
        
        # Export Scene (main action)
        layout.operator("export_scene.blazium_scene", text="Export Blazium Scene", icon='EXPORT')
        
        layout.separator()
        
        # Open Properties Panel (to show settings)
        layout.operator("blazium.show_export_panel", text="Export Settings", icon='PREFERENCES')
        
        layout.separator()
        
        # Help/Info
        layout.label(text="Blazium Scene Exporter v1.0")


def draw_blazium_menu(self, context):
    """Draw function to add Blazium menu to top menu bar."""
    self.layout.menu("BLAZIUM_MT_main_menu", text="Blazium", icon='EXPORT')


def register():
    bpy.utils.register_class(BLAZIUM_MT_main_menu)
    bpy.types.TOPBAR_MT_editor_menus.append(draw_blazium_menu)


def unregister():
    bpy.types.TOPBAR_MT_editor_menus.remove(draw_blazium_menu)
    bpy.utils.unregister_class(BLAZIUM_MT_main_menu)

