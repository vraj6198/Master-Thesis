import json
import os
import re

import bpy

ADDON_NAME = __package__.split(".")[0]

DEFAULT_SCAN_HINTS = (
    "wm.execute_scan",
    "execute_scan",
    "range_scanner",
    "scanner",
    "scan",
)


def get_addon_prefs(context=None):
    context = context or bpy.context
    addon = context.preferences.addons.get(ADDON_NAME)
    if addon is None:
        return None
    return addon.preferences


def get_settings(context=None):
    context = context or bpy.context
    return getattr(context.scene, "llm_lidar_settings", None)


def get_bundled_config_path():
    return os.path.join(os.path.dirname(__file__), "data", "base_config.json")


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, payload):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def remove_invalid_filename_chars(name):
    for char in " !@#$%^&*(){}:\";'[]<>,.\\/?":
        name = name.replace(char, "_")
    return name.lower().strip()


def operator_exists(idname):
    try:
        module_name, op_name = idname.split(".", 1)
    except ValueError:
        return False
    if not hasattr(bpy.ops, module_name):
        return False
    return hasattr(getattr(bpy.ops, module_name), op_name)


def iter_operator_idnames():
    for module_name in dir(bpy.ops):
        module = getattr(bpy.ops, module_name)
        if module is None:
            continue
        for op_name in dir(module):
            op = getattr(module, op_name)
            try:
                idname = op.idname()
            except Exception:
                continue
            if idname:
                yield idname


def resolve_scan_operator(preferred=None):
    idnames = list(iter_operator_idnames())
    if preferred and preferred in idnames:
        return preferred
    if "wm.execute_scan" in idnames:
        return "wm.execute_scan"

    candidates = []
    for idname in idnames:
        lowered = idname.lower()
        if "execute_scan" in lowered:
            candidates.append(idname)
        elif "scan" in lowered and ("range" in lowered or "scanner" in lowered):
            candidates.append(idname)

    if candidates:
        candidates.sort()
        return candidates[0]
    return None


def extract_json_from_text(text):
    cleaned = text.strip()
    if "```" in cleaned:
        blocks = re.findall(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
        if blocks:
            cleaned = blocks[0].strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response")
    json_text = cleaned[start:end + 1]
    return json.loads(json_text), json_text


def ensure_within_dir(path, directory):
    path_real = os.path.realpath(path)
    dir_real = os.path.realpath(directory)
    return path_real == dir_real or path_real.startswith(dir_real + os.sep)


def format_status(message, warnings=None):
    if not warnings:
        return message
    return f"{message} (warnings: {len(warnings)})"
