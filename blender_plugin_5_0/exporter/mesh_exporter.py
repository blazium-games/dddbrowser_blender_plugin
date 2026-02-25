"""
Mesh export functionality for converting Blender meshes to OBJ format.
Blender 4.0+ uses bpy.ops.wm.obj_export (replaces deprecated export_scene.obj).
Blender 5.0 uses the same operator (C++ implementation).
"""
import bpy
import os
import mathutils
import traceback # Added to see actual errors

def sanitize_filename(name):
    """Sanitize a filename to be safe for filesystem."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    name = name.strip('. ')
    return name

def export_mesh_to_obj_simple(blender_object, output_path, materials_dict=None):
    """Simpler OBJ export using Blender's export functionality (alternative approach)."""
    if not blender_object or blender_object.type != 'MESH':
        return None
    
    # Use Blender's built-in OBJ exporter via operator
    # Save current selection
    old_active = bpy.context.active_object
    old_selected = bpy.context.selected_objects.copy()
    
    try:
        # Select only this object
        bpy.ops.object.select_all(action='DESELECT')
        blender_object.select_set(True)
        bpy.context.view_layer.objects.active = blender_object
        
        # Generate filename
        object_name = blender_object.name
        sanitized_name = sanitize_filename(object_name)
        filepath = os.path.join(output_path, f"{sanitized_name}.obj")
        
        os.makedirs(output_path, exist_ok=True)
        
        # Blender 4.0+: use wm.obj_export (export_scene.obj was removed)
        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=True,
            export_materials=True,
            export_normals=True,
            export_uv=True,
            export_triangulated_mesh=True,
            forward_axis='NEGATIVE_Z',     # FIXED: was axis_forward
            up_axis='Y'                    # FIXED: was axis_up
        )
        
        return filepath
    except Exception as e:
        print(f"FAILED to export {blender_object.name}")
        print(f"Error: {e}")
        traceback.print_exc() # Print full error to console
        return None
        
    finally:
        # Restore selection
        try:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in old_selected:
                try:
                    obj.select_set(True)
                except ReferenceError:
                    pass # Object might have been deleted
            
            if old_active:
                 try:
                    bpy.context.view_layer.objects.active = old_active
                 except:
                    pass
        except Exception as e:
            print(f"Error restoring selection: {e}")

def export_all_meshes(objects, output_path, materials_dict=None):
    """Export all mesh objects to OBJ files using Blender's built-in exporter."""
    meshes_dict = {}
    
    # Ensure absolute path
    output_path = os.path.abspath(output_path)
    
    old_active = bpy.context.active_object
    old_selected = bpy.context.selected_objects.copy()
    old_mode = bpy.context.active_object.mode if bpy.context.active_object else None
    
    try:
        # Switch to object mode
        if old_mode and old_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        for obj in objects:
            if obj.type == 'MESH':
                # Deselect all
                bpy.ops.object.select_all(action='DESELECT')
                # Select and activate this object
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                
                # Generate filename
                object_name = obj.name
                sanitized_name = sanitize_filename(object_name)
                filepath = os.path.join(output_path, f"{sanitized_name}.obj")
                
                os.makedirs(output_path, exist_ok=True)
                
                try:
                    # Blender 4.0+: use wm.obj_export
                    bpy.ops.wm.obj_export(
                        filepath=filepath,
                        export_selected_objects=True,
                        export_materials=True,
                        export_normals=True,
                        export_uv=True,
                        # FIX IS HERE: Changed from 'triangular' to 'triangulated'
                        export_triangulated_mesh=True, 
                        forward_axis='NEGATIVE_Z',     # FIXED: was axis_forward
                        up_axis='Y'                    # FIXED: was axis_up
                    )
                    
                    if os.path.exists(filepath):
                        meshes_dict[sanitized_name] = filepath
                        print(f"Exported: {sanitized_name}")
                    else:
                        print(f"Warning: File not found after export: {filepath}")

                except Exception as e:
                    print(f"Error exporting {sanitized_name}: {e}")
                    # This will show you exactly why it failed in the system console
                    traceback.print_exc() 
    
    except Exception as e:
        print(f"Global export error: {e}")
        traceback.print_exc()
        
    finally:
        # Restore selection state
        try:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in old_selected:
                try:
                    obj.select_set(True)
                except: pass
            if old_active:
                try:
                    bpy.context.view_layer.objects.active = old_active
                except: pass
            if old_mode and old_mode != 'OBJECT':
                try:
                    bpy.ops.object.mode_set(mode=old_mode)
                except: pass
        except: pass
    
    return meshes_dict