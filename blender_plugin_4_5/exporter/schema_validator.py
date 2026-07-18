"""
JSON schema validation for exported scene JSON.
"""
import json
import os


def default_schema_path():
    """Return path to vendored scene.schema.json beside this addon."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema", "scene.schema.json")


def validate_scene_json(scene_json, schema_path=None):
    """Validate scene JSON against schema (optional, requires jsonschema library).
    
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    try:
        import jsonschema
        from jsonschema import Draft202012Validator
    except ImportError:
        return True, ["jsonschema not installed; skipped validation"]

    if schema_path is None:
        schema_path = default_schema_path()

    if not schema_path or not os.path.exists(schema_path):
        return True, [f"schema not found at {schema_path}; skipped validation"]

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception as exc:
        return True, [f"schema load failed: {exc}"]

    validator = Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(scene_json), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{loc}: {err.message}")
    return (len(errors) == 0), errors


def validate_with_schema_file(scene_json, schema_file_path=None):
    """Validate scene JSON with a specific schema file."""
    is_valid, errors = validate_scene_json(scene_json, schema_file_path)
    return is_valid
