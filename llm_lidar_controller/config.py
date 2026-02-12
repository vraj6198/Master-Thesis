import copy
import math
import os

import bpy

from . import utils


DEFAULT_CONFIG = {
    "scanner_object": "",
    "pose": {"location": [0.0, 0.0, 0.0], "rotation_euler_deg": [0.0, 0.0, 0.0]},
    "scanner_properties": {},
}


def load_base_config(path):
    resolved = path
    if not resolved or not os.path.exists(resolved):
        resolved = utils.get_bundled_config_path()
    data = utils.read_json(resolved)
    return ensure_base_keys(data)


def ensure_base_keys(data):
    normalized = copy.deepcopy(DEFAULT_CONFIG)
    if isinstance(data, dict):
        normalized.update({k: data.get(k) for k in normalized.keys()})
        if isinstance(data.get("pose"), dict):
            normalized["pose"].update(data["pose"])
        if isinstance(data.get("scanner_properties"), dict):
            normalized["scanner_properties"] = data["scanner_properties"]
    return normalized


def merge_patch(base, patch):
    if not isinstance(patch, dict):
        return patch
    merged = copy.deepcopy(base)
    for key, value in patch.items():
        if value is None:
            merged.pop(key, None)
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_patch(merged[key], value)
        else:
            merged[key] = value
    return merged


def coerce_value(prop, value):
    if prop.type == "BOOLEAN":
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "on"}
        return bool(value)
    if prop.type == "INT":
        return int(value)
    if prop.type == "FLOAT":
        return float(value)
    if prop.type == "STRING":
        return str(value)
    if prop.type == "ENUM":
        return str(value)
    return value


def clamp_numeric(prop, value):
    if prop.type not in {"INT", "FLOAT"}:
        return value
    min_val = getattr(prop, "hard_min", None)
    max_val = getattr(prop, "hard_max", None)
    if min_val is not None:
        value = max(value, min_val)
    if max_val is not None:
        value = min(value, max_val)
    if prop.type == "INT":
        return int(value)
    return float(value)


def validate_and_clamp_config(context, config):
    errors = []
    warnings = []
    sanitized = ensure_base_keys(config)

    if not hasattr(bpy.types.Scene, "scannerProperties"):
        errors.append("BLAINDER Range Scanner add-on is not enabled.")
        return sanitized, errors, warnings

    props = context.scene.scannerProperties
    scanner_props = sanitized.get("scanner_properties")
    if not isinstance(scanner_props, dict):
        errors.append("scanner_properties must be a JSON object.")
        scanner_props = {}

    # Validate scanner object
    scanner_object_name = sanitized.get("scanner_object")
    if scanner_object_name:
        obj = bpy.data.objects.get(scanner_object_name)
        if obj is None:
            errors.append(f"Scanner object '{scanner_object_name}' not found.")
        elif obj.type != "CAMERA":
            warnings.append(f"Scanner object '{scanner_object_name}' is not a camera.")

    # Pose validation
    pose = sanitized.get("pose", {})
    location = pose.get("location")
    rotation = pose.get("rotation_euler_deg")
    if location is not None:
        if not (isinstance(location, (list, tuple)) and len(location) == 3):
            warnings.append("pose.location must be a 3-element list.")
            pose["location"] = [0.0, 0.0, 0.0]
    if rotation is not None:
        if not (isinstance(rotation, (list, tuple)) and len(rotation) == 3):
            warnings.append("pose.rotation_euler_deg must be a 3-element list.")
            pose["rotation_euler_deg"] = [0.0, 0.0, 0.0]

    cleaned_props = {}
    for key, value in scanner_props.items():
        prop = props.bl_rna.properties.get(key)
        if prop is None:
            warnings.append(f"Unknown scanner property '{key}' ignored.")
            continue

        if prop.is_array:
            if not isinstance(value, (list, tuple)) or len(value) != prop.array_length:
                warnings.append(f"Property '{key}' must be a list of length {prop.array_length}.")
                continue
            try:
                coerced = [float(item) for item in value]
            except (TypeError, ValueError):
                warnings.append(f"Property '{key}' contains non-numeric values.")
                continue
            cleaned_props[key] = coerced
            continue

        try:
            coerced = coerce_value(prop, value)
        except (TypeError, ValueError):
            warnings.append(f"Property '{key}' has invalid value '{value}'.")
            continue

        if prop.type == "ENUM":
            allowed = {item.identifier for item in prop.enum_items}
            if coerced not in allowed:
                warnings.append(f"Property '{key}' value '{coerced}' not in {sorted(allowed)}.")
                continue

        if prop.type in {"INT", "FLOAT"}:
            coerced = clamp_numeric(prop, coerced)

        cleaned_props[key] = coerced

    sanitized["scanner_properties"] = cleaned_props
    return sanitized, errors, warnings


def apply_config(context, config):
    if not hasattr(bpy.types.Scene, "scannerProperties"):
        return False, ["BLAINDER Range Scanner add-on is not enabled."], []

    props = context.scene.scannerProperties
    errors = []
    warnings = []

    scanner_object_name = config.get("scanner_object")
    if scanner_object_name:
        obj = bpy.data.objects.get(scanner_object_name)
        if obj is None:
            errors.append(f"Scanner object '{scanner_object_name}' not found.")
        else:
            props.scannerObject = obj

    pose = config.get("pose", {})
    scanner_obj = props.scannerObject
    if scanner_obj:
        location = pose.get("location")
        rotation = pose.get("rotation_euler_deg")
        if location is not None:
            try:
                scanner_obj.location = [float(v) for v in location]
            except (TypeError, ValueError):
                warnings.append("Failed to apply pose.location.")
        if rotation is not None:
            try:
                scanner_obj.rotation_euler = [math.radians(float(v)) for v in rotation]
            except (TypeError, ValueError):
                warnings.append("Failed to apply pose.rotation_euler_deg.")

    for key, value in config.get("scanner_properties", {}).items():
        if hasattr(props, key):
            try:
                setattr(props, key, value)
            except Exception:
                warnings.append(f"Failed to set scanner property '{key}'.")

    return True, errors, warnings
