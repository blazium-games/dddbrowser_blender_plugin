"""
Optional JSON schema validation for exported scene JSON.
"""
import json
import os

def validate_scene_json(scene_json, schema_path=None):
    """Validate scene JSON against schema (optional, requires jsonschema library).
    
    Args:
        scene_json: dict - Scene JSON dict to validate
        schema_path: str - Path to schema JSON file (optional)
        
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    try:
        import jsonschema
    except ImportError:
        # jsonschema not available, skip validation
        return True, []
    
    # Load schema if path provided
    if schema_path and os.path.exists(schema_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
        except Exception:
            return True, []  # Skip validation if schema can't be loaded
    else:
        # No schema path provided, skip validation
        return True, []
    
    # Validate
    try:
        jsonschema.validate(instance=scene_json, schema=schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [str(e)]
    except jsonschema.SchemaError:
        return True, []  # Skip validation if schema is invalid

def validate_with_schema_file(scene_json, schema_file_path):
    """Validate scene JSON with a specific schema file.
    
    Args:
        scene_json: dict - Scene JSON dict
        schema_file_path: str - Path to schema.json file
        
    Returns:
        bool: True if valid, False otherwise
    """
    is_valid, errors = validate_scene_json(scene_json, schema_file_path)
    if not is_valid:
        for error in errors:
            pass
    return is_valid

