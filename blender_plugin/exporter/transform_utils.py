"""
Transform utility functions for converting Blender transforms to scene format.
Exports position, rotation, scale in Y-up space to match OBJ export (axis_forward='-Z', axis_up='Y').
"""
import mathutils
import math
from bpy_extras.io_utils import axis_conversion


def get_world_matrix(blender_object):
    """Get object's world transformation matrix.
    
    Args:
        blender_object: bpy.types.Object
    
    Returns:
        mathutils.Matrix: World transformation matrix
    """
    return blender_object.matrix_world.copy()


def _get_object_transform_yup(blender_object):
    """Get transform in Y-up space (matches OBJ export), with native float for JSON.
    
    Returns:
        tuple: (position_dict, rotation_dict, scale_dict) with float values
    """
    matrix_world = blender_object.matrix_world.copy()
    # Blender: Y forward, Z up -> OBJ/glTF style: -Z forward, Y up
    M_conv = axis_conversion(
        from_forward='Y', from_up='Z',
        to_forward='-Z', to_up='Y'
    ).to_4x4()
    matrix_yup = M_conv @ matrix_world
    loc, rot_quat, scale = matrix_yup.decompose()
    euler = rot_quat.to_euler('XYZ')
    position = {
        "x": float(loc.x),
        "y": float(loc.y),
        "z": float(loc.z)
    }
    rotation = {
        "x": float(math.degrees(euler.x)),
        "y": float(math.degrees(euler.y)),
        "z": float(math.degrees(euler.z))
    }
    scale_dict = {
        "x": float(scale.x),
        "y": float(scale.y),
        "z": float(scale.z)
    }
    return position, rotation, scale_dict


def matrix_to_position(matrix):
    """Extract position (x, y, z) from transformation matrix.
    
    Args:
        matrix: mathutils.Matrix
    
    Returns:
        dict: Position dict with x, y, z keys
    """
    translation = matrix.translation
    return {
        "x": float(translation.x),
        "y": float(translation.y),
        "z": float(translation.z)
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
        "x": float(math.degrees(euler.x)),
        "y": float(math.degrees(euler.y)),
        "z": float(math.degrees(euler.z))
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
        "x": float(scale.x),
        "y": float(scale.y),
        "z": float(scale.z)
    }


def blender_to_scene_rotation(euler):
    """Convert Blender Euler rotation to scene format (degrees).
    
    Args:
        euler: mathutils.Euler
    
    Returns:
        dict: Rotation dict with x, y, z keys in degrees
    """
    return {
        "x": float(math.degrees(euler.x)),
        "y": float(math.degrees(euler.y)),
        "z": float(math.degrees(euler.z))
    }


def get_object_transform(blender_object):
    """Get complete transform (position, rotation, scale) for an object in Y-up space.
    
    Matches OBJ export coordinate system (axis_forward='-Z', axis_up='Y').
    All values are native float for JSON serialization.
    
    Args:
        blender_object: bpy.types.Object
    
    Returns:
        tuple: (position_dict, rotation_dict, scale_dict)
    """
    return _get_object_transform_yup(blender_object)
