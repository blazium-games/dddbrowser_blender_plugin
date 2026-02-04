"""
Transform utility functions for converting Blender transforms to scene format.
"""
import mathutils
import math

def get_world_matrix(blender_object):
    """Get object's world transformation matrix.
    
    Args:
        blender_object: bpy.types.Object
    
    Returns:
        mathutils.Matrix: World transformation matrix
    """
    return blender_object.matrix_world.copy()

def matrix_to_position(matrix):
    """Extract position (x, y, z) from transformation matrix.
    
    Args:
        matrix: mathutils.Matrix
    
    Returns:
        dict: Position dict with x, y, z keys
    """
    translation = matrix.translation
    return {
        "x": translation.x,
        "y": translation.y,
        "z": translation.z
    }

def matrix_to_rotation(matrix):
    """Extract rotation as Euler angles (degrees) from transformation matrix.
    
    Args:
        matrix: mathutils.Matrix
    
    Returns:
        dict: Rotation dict with x, y, z keys in degrees
    """
    euler = matrix.to_euler('XYZ')
    return {
        "x": math.degrees(euler.x),
        "y": math.degrees(euler.y),
        "z": math.degrees(euler.z)
    }

def matrix_to_scale(matrix):
    """Extract scale (x, y, z) from transformation matrix.
    
    Args:
        matrix: mathutils.Matrix
    
    Returns:
        dict: Scale dict with x, y, z keys
    """
    scale = matrix.to_scale()
    return {
        "x": scale.x,
        "y": scale.y,
        "z": scale.z
    }

def blender_to_scene_rotation(euler):
    """Convert Blender Euler rotation to scene format (degrees).
    
    Args:
        euler: mathutils.Euler
    
    Returns:
        dict: Rotation dict with x, y, z keys in degrees
    """
    return {
        "x": math.degrees(euler.x),
        "y": math.degrees(euler.y),
        "z": math.degrees(euler.z)
    }

def get_object_transform(blender_object):
    """Get complete transform (position, rotation, scale) for an object.
    
    Args:
        blender_object: bpy.types.Object
    
    Returns:
        tuple: (position_dict, rotation_dict, scale_dict)
    """
    matrix = get_world_matrix(blender_object)
    position = matrix_to_position(matrix)
    rotation = matrix_to_rotation(matrix)
    scale = matrix_to_scale(matrix)
    return position, rotation, scale

