"""
JSON Validator for SceneGen specifications.
Validates structure, types, and values.
"""

import json
from typing import Tuple, Any, List


def validate_json_spec(json_string: str) -> Tuple[bool, str]:
    """
    Validate a JSON specification string.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Try to parse JSON
    try:
        spec = json.loads(json_string)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON syntax: {e}"
    
    errors = []
    
    # Validate top-level structure
    if not isinstance(spec, dict):
        return False, "JSON root must be an object"
    
    # Check version
    if "version" in spec:
        if spec["version"] != "1.0":
            errors.append(f"Unsupported version: {spec['version']} (expected 1.0)")
    
    # Validate objects array
    if "objects" in spec:
        if not isinstance(spec["objects"], list):
            errors.append("'objects' must be an array")
        else:
            for i, obj in enumerate(spec["objects"]):
                obj_errors = validate_object(obj, i)
                errors.extend(obj_errors)
    
    if errors:
        return False, "\n".join(errors)
    
    # Build summary
    summary_lines = ["Validation passed:"]
    if "objects" in spec:
        summary_lines.append(f"  - {len(spec['objects'])} object(s)")
    
    return True, "\n".join(summary_lines)


def validate_object(obj: dict, index: int) -> List[str]:
    """Validate a single object in the spec."""
    errors = []
    prefix = f"objects[{index}]"
    
    if not isinstance(obj, dict):
        return [f"{prefix}: must be an object"]
    
    # Check required fields
    if "name" not in obj:
        errors.append(f"{prefix}: missing 'name'")
    
    if "type" not in obj:
        errors.append(f"{prefix}: missing 'type'")
    else:
        valid_types = ["chair", "cube", "cylinder", "plane"]
        if obj["type"] not in valid_types:
            errors.append(f"{prefix}: invalid type '{obj['type']}' (allowed: {valid_types})")
    
    # Validate transform
    if "transform" in obj:
        transform_errors = validate_transform(obj["transform"], f"{prefix}.transform")
        errors.extend(transform_errors)
    
    # Validate material
    if "material" in obj:
        mat_errors = validate_material(obj["material"], f"{prefix}.material")
        errors.extend(mat_errors)
    
    # Validate chair params
    if obj.get("type") == "chair" and "params" in obj:
        chair_errors = validate_chair_params(obj["params"], f"{prefix}.params")
        errors.extend(chair_errors)
    
    return errors


def validate_transform(transform: dict, prefix: str) -> List[str]:
    """Validate a transform object."""
    errors = []
    
    if not isinstance(transform, dict):
        return [f"{prefix}: must be an object"]
    
    # Validate location (3 floats)
    if "location" in transform:
        loc_error = validate_vector3(transform["location"], f"{prefix}.location")
        if loc_error:
            errors.append(loc_error)
    
    # Validate rotation_euler (3 floats)
    if "rotation_euler" in transform:
        rot_error = validate_vector3(transform["rotation_euler"], f"{prefix}.rotation_euler")
        if rot_error:
            errors.append(rot_error)
    
    # Validate scale (3 floats)
    if "scale" in transform:
        scale_error = validate_vector3(transform["scale"], f"{prefix}.scale")
        if scale_error:
            errors.append(scale_error)
    
    return errors


def validate_material(material: dict, prefix: str) -> List[str]:
    """Validate a material object."""
    errors = []
    
    if not isinstance(material, dict):
        return [f"{prefix}: must be an object"]
    
    # Validate base_color_rgba (4 floats)
    if "base_color_rgba" in material:
        color_error = validate_rgba(material["base_color_rgba"], f"{prefix}.base_color_rgba")
        if color_error:
            errors.append(color_error)
    
    # Validate roughness (0-1)
    if "roughness" in material:
        r = material["roughness"]
        if not isinstance(r, (int, float)):
            errors.append(f"{prefix}.roughness: must be a number")
        elif not (0 <= r <= 1):
            errors.append(f"{prefix}.roughness: must be between 0 and 1")
    
    # Validate metallic (0-1)
    if "metallic" in material:
        m = material["metallic"]
        if not isinstance(m, (int, float)):
            errors.append(f"{prefix}.metallic: must be a number")
        elif not (0 <= m <= 1):
            errors.append(f"{prefix}.metallic: must be between 0 and 1")
    
    return errors


def validate_chair_params(params: dict, prefix: str) -> List[str]:
    """Validate chair-specific parameters."""
    errors = []
    
    if not isinstance(params, dict):
        return [f"{prefix}: must be an object"]
    
    # Validate seat
    if "seat" in params:
        seat = params["seat"]
        if isinstance(seat, dict):
            for key in ["width", "depth", "thickness"]:
                if key in seat:
                    val = seat[key]
                    if not isinstance(val, (int, float)):
                        errors.append(f"{prefix}.seat.{key}: must be a number")
                    elif val <= 0:
                        errors.append(f"{prefix}.seat.{key}: must be positive")
    
    # Validate legs
    if "legs" in params:
        legs = params["legs"]
        if isinstance(legs, dict):
            for key in ["radius", "height", "spread"]:
                if key in legs:
                    val = legs[key]
                    if not isinstance(val, (int, float)):
                        errors.append(f"{prefix}.legs.{key}: must be a number")
                    elif val <= 0:
                        errors.append(f"{prefix}.legs.{key}: must be positive")
            
            if "count" in legs and legs["count"] != 4:
                errors.append(f"{prefix}.legs.count: must be 4 in v1")
    
    # Validate back
    if "back" in params:
        back = params["back"]
        if isinstance(back, dict):
            for key in ["height", "thickness"]:
                if key in back:
                    val = back[key]
                    if not isinstance(val, (int, float)):
                        errors.append(f"{prefix}.back.{key}: must be a number")
                    elif val <= 0:
                        errors.append(f"{prefix}.back.{key}: must be positive")
    
    return errors


def validate_vector3(value: Any, path: str) -> str:
    """Validate a 3-element vector (location, rotation, scale)."""
    if not isinstance(value, list):
        return f"{path}: must be an array"
    if len(value) != 3:
        return f"{path}: must have exactly 3 elements (got {len(value)})"
    for i, v in enumerate(value):
        if not isinstance(v, (int, float)):
            return f"{path}[{i}]: must be a number"
    return ""


def validate_rgba(value: Any, path: str) -> str:
    """Validate an RGBA color (4 floats, 0-1 range)."""
    if not isinstance(value, list):
        return f"{path}: must be an array"
    if len(value) != 4:
        return f"{path}: must have exactly 4 elements for RGBA (got {len(value)})"
    for i, v in enumerate(value):
        if not isinstance(v, (int, float)):
            return f"{path}[{i}]: must be a number"
        if not (0 <= v <= 1):
            return f"{path}[{i}]: must be between 0 and 1"
    return ""
