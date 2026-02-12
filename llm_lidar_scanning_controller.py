bl_info = {
    "name": "LLM LiDAR Control - Scanning Controller",
    "author": "Codex",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "3D View > Sidebar > LLM LiDAR Control",
    "description": "Controller add-on for existing LiDAR/range scanner add-ons (preset, scan, export)",
    "category": "3D View",
}

"""
How to use:
1) Enable this add-on and the existing scanner add-on (for example BLAINDER Range Scanner).
2) Open 3D View > Sidebar > LLM LiDAR Control.
3) Select a JSON config file and click "Apply Config & Run Scan".
4) Use "Export Last Point Cloud" to re-export the most recent detected point cloud object.

Minimal sample JSON config:
{
  "scanner_preset": "Generic",
  "camera_name": "ScannerCam",
  "camera_position": [0.0, 0.0, 1.5],
  "camera_rotation_euler_deg": [0.0, 0.0, 0.0],
  "noise_enabled": true,
  "export": {
    "format": "CSV",
    "directory": "//scans",
    "filename": "scan_output"
  }
}
"""

import csv
import json
import math
import os
from typing import Dict, List, Optional, Sequence, Tuple

import bpy
from bpy.props import PointerProperty, StringProperty
from bpy.types import Operator, Panel, PropertyGroup
from mathutils import Vector

LOG_PREFIX = "[LLM LiDAR Control]"

ALLOWED_PRESETS = ("Generic", "Ultrabook", "Alphabook")
ALLOWED_EXPORT_FORMATS = {"CSV", "LAS", "HDF", "PLY"}
POINTCLOUD_NAME_KEYWORDS = ("point", "cloud", "scan", "real_values", "noise_values")

# Mapping for the requested fixed schema to common scanner preset labels.
PRESET_NAME_CANDIDATES = {
    "Generic": ["Generic", "Generic lidar", "Generic Lidar"],
    "Ultrabook": ["Ultrabook", "Velodyne UltraPuck", "UltraPuck"],
    "Alphabook": ["Alphabook", "Velodyne AlphaPuck", "AlphaPuck"],
}


def _log(message: str) -> None:
    print(f"{LOG_PREFIX} {message}")


def _status_append(context: bpy.types.Context, message: str, reset: bool = False) -> None:
    props = getattr(context.scene, "llm_lidar_ctrl", None)
    if props is None:
        _log(message)
        return
    if reset or not props.status_text:
        props.status_text = message
    else:
        props.status_text = f"{props.status_text}\n{message}"
    _log(message)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_vec3(value, field_name: str) -> Tuple[float, float, float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"'{field_name}' must be a list of 3 numbers.")
    if not all(_is_number(v) for v in value):
        raise ValueError(f"'{field_name}' must contain only numeric values.")
    return float(value[0]), float(value[1]), float(value[2])


def load_config(config_path: str) -> Dict:
    """
    Load and validate the required JSON config schema.
    """
    if not config_path:
        raise ValueError("Config path is empty.")

    resolved_path = bpy.path.abspath(config_path)
    if not os.path.isfile(resolved_path):
        raise ValueError(f"Config file not found: {resolved_path}")

    try:
        with open(resolved_path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Failed to read config: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Config root must be a JSON object.")

    if "scanner_preset" not in raw:
        raise ValueError("Missing required field 'scanner_preset'.")
    if "export" not in raw:
        raise ValueError("Missing required field 'export'.")

    preset = raw["scanner_preset"]
    if not isinstance(preset, str) or preset not in ALLOWED_PRESETS:
        allowed = ", ".join(ALLOWED_PRESETS)
        raise ValueError(f"'scanner_preset' must be one of: {allowed}")

    export_cfg = raw["export"]
    if not isinstance(export_cfg, dict):
        raise ValueError("'export' must be an object.")

    for required_key in ("format", "directory", "filename"):
        if required_key not in export_cfg:
            raise ValueError(f"Missing required export field '{required_key}'.")

    export_format = str(export_cfg["format"]).upper()
    if export_format not in ALLOWED_EXPORT_FORMATS:
        allowed = ", ".join(sorted(ALLOWED_EXPORT_FORMATS))
        raise ValueError(f"'export.format' must be one of: {allowed}")

    export_directory = export_cfg["directory"]
    if not isinstance(export_directory, str) or not export_directory.strip():
        raise ValueError("'export.directory' must be a non-empty string.")

    export_filename = export_cfg["filename"]
    if not isinstance(export_filename, str) or not export_filename.strip():
        raise ValueError("'export.filename' must be a non-empty string.")
    if "/" in export_filename or "\\" in export_filename:
        raise ValueError("'export.filename' must not contain path separators.")

    normalized = {
        "scanner_preset": preset,
        "export": {
            "format": export_format,
            "directory": export_directory.strip(),
            "filename": export_filename.strip(),
        },
    }

    if "camera_name" in raw:
        if not isinstance(raw["camera_name"], str) or not raw["camera_name"].strip():
            raise ValueError("'camera_name' must be a non-empty string when provided.")
        normalized["camera_name"] = raw["camera_name"].strip()

    if "camera_position" in raw:
        normalized["camera_position"] = _validate_vec3(raw["camera_position"], "camera_position")

    if "camera_rotation_euler_deg" in raw:
        normalized["camera_rotation_euler_deg"] = _validate_vec3(
            raw["camera_rotation_euler_deg"],
            "camera_rotation_euler_deg",
        )

    if "noise_enabled" in raw:
        if not isinstance(raw["noise_enabled"], bool):
            raise ValueError("'noise_enabled' must be true or false when provided.")
        normalized["noise_enabled"] = raw["noise_enabled"]

    return normalized


def ensure_camera(context: bpy.types.Context, config: Dict) -> Tuple[bpy.types.Object, List[str]]:
    """
    Resolve camera from config or scene, creating ScannerCam if needed.
    """
    scene = context.scene
    warnings: List[str] = []
    camera_obj: Optional[bpy.types.Object] = None

    requested_name = config.get("camera_name")
    if requested_name:
        candidate = bpy.data.objects.get(requested_name)
        if candidate and candidate.type == "CAMERA":
            camera_obj = candidate
        else:
            warnings.append(
                f"camera_name '{requested_name}' was not found as a camera. Falling back to scene camera."
            )

    if camera_obj is None and scene.camera and scene.camera.type == "CAMERA":
        camera_obj = scene.camera

    if camera_obj is None:
        cam_data = bpy.data.cameras.new(name="ScannerCam")
        camera_obj = bpy.data.objects.new(name="ScannerCam", object_data=cam_data)
        scene.collection.objects.link(camera_obj)
        warnings.append("No valid camera found. Created camera 'ScannerCam'.")

    scene.camera = camera_obj
    return camera_obj, warnings


def apply_transforms(camera_obj: bpy.types.Object, config: Dict) -> List[str]:
    """
    Apply optional camera transform fields from config.
    """
    messages: List[str] = []
    if "camera_position" in config:
        camera_obj.location = Vector(config["camera_position"])
        messages.append(f"Applied camera_position to '{camera_obj.name}'.")

    if "camera_rotation_euler_deg" in config:
        rx, ry, rz = config["camera_rotation_euler_deg"]
        camera_obj.rotation_mode = "XYZ"
        camera_obj.rotation_euler = (
            math.radians(rx),
            math.radians(ry),
            math.radians(rz),
        )
        messages.append(f"Applied camera_rotation_euler_deg to '{camera_obj.name}'.")

    return messages


def _iter_operator_idnames() -> List[str]:
    idnames: List[str] = []
    for category_name in dir(bpy.ops):
        if category_name.startswith("_"):
            continue
        category = getattr(bpy.ops, category_name, None)
        if category is None:
            continue
        for op_name in dir(category):
            if op_name.startswith("_"):
                continue
            idnames.append(f"{category_name}.{op_name}")
    return idnames


def _score_scan_candidate(idname: str) -> int:
    low = idname.lower()
    score = 0
    if "scan" in low:
        score += 8
    if "execute" in low or "run" in low or "generate" in low:
        score += 3
    if "scanner" in low or "range" in low or "lidar" in low:
        score += 5
    if idname.startswith("wm."):
        score += 2
    return score


def _score_preset_candidate(idname: str) -> int:
    low = idname.lower()
    score = 0
    if "preset" in low:
        score += 8
    if "load" in low:
        score += 5
    if "load_preset" in low:
        score += 8
    if "scanner" in low or "range" in low or "lidar" in low:
        score += 5
    if idname.startswith("wm."):
        score += 2
    return score


def find_scanner_ops() -> Dict[str, List[str]]:
    """
    Discover scanner-related operators dynamically using keyword heuristics.
    """
    all_ops = _iter_operator_idnames()
    related_keywords = ("scanner", "range", "lidar", "scan", "preset")

    related = sorted(
        {
            op
            for op in all_ops
            if any(keyword in op.lower() for keyword in related_keywords)
        }
    )

    preset_candidates = sorted(
        [
            op
            for op in related
            if (
                ("preset" in op.lower() or "load" in op.lower())
                and (
                    any(k in op.lower() for k in ("scanner", "range", "lidar"))
                    or "load_preset" in op.lower()
                )
            )
        ],
        key=_score_preset_candidate,
        reverse=True,
    )

    scan_candidates = sorted(
        [
            op
            for op in related
            if (
                "scan" in op.lower()
                or (
                    any(k in op.lower() for k in ("scanner", "range", "lidar"))
                    and ("execute" in op.lower() or "generate" in op.lower())
                )
            )
        ],
        key=_score_scan_candidate,
        reverse=True,
    )

    return {
        "all_candidates": related,
        "preset_candidates": preset_candidates,
        "scan_candidates": scan_candidates,
    }


def _get_operator_callable(op_idname: str):
    if "." not in op_idname:
        return None
    category_name, op_name = op_idname.split(".", 1)
    category = getattr(bpy.ops, category_name, None)
    if category is None:
        return None
    return getattr(category, op_name, None)


def _view3d_override(context: bpy.types.Context) -> Optional[Dict]:
    window = getattr(context, "window", None)
    if window is None:
        return None

    screen = window.screen
    if screen is None:
        return None

    for area in screen.areas:
        if area.type != "VIEW_3D":
            continue
        region = next((reg for reg in area.regions if reg.type == "WINDOW"), None)
        if region is not None:
            return {"window": window, "screen": screen, "area": area, "region": region}
    return None


def _invoke_operator(op_callable) -> Tuple[bool, str]:
    last_error = ""
    attempts = ("EXEC_DEFAULT", "INVOKE_DEFAULT", None)

    for mode in attempts:
        try:
            if mode is None:
                result = op_callable()
            else:
                result = op_callable(mode)
            if result and ("FINISHED" in result or "RUNNING_MODAL" in result):
                return True, f"Returned {set(result)}"
            last_error = f"Returned non-finished state: {result}"
        except Exception as exc:
            last_error = str(exc)

    return False, last_error or "Unknown operator invocation error."


def _call_operator_safe(context: bpy.types.Context, op_idname: str) -> Tuple[bool, str]:
    op_callable = _get_operator_callable(op_idname)
    if op_callable is None:
        return False, "Operator not found."

    override = _view3d_override(context)
    override_error = ""
    if override is not None:
        try:
            with context.temp_override(**override):
                ok, detail = _invoke_operator(op_callable)
                if ok:
                    return True, detail
        except Exception as exc:
            override_error = f"Context override failed: {exc}"

    ok, detail = _invoke_operator(op_callable)
    if ok:
        return True, detail
    if override_error:
        return False, f"{override_error}; fallback call failed: {detail}"
    return False, detail


def _get_scanner_properties(scene) -> Optional[object]:
    return getattr(scene, "scannerProperties", None)


def _try_set_prop(owner, prop_name: str, value) -> bool:
    if owner is None or not hasattr(owner, prop_name):
        return False
    try:
        setattr(owner, prop_name, value)
        return True
    except Exception:
        return False


def _get_enum_identifiers(owner, prop_name: str) -> List[str]:
    if owner is None:
        return []
    try:
        enum_items = owner.bl_rna.properties[prop_name].enum_items
        return [item.identifier for item in enum_items]
    except Exception:
        return []


def _assign_preset_name(scanner_props, requested_preset: str) -> Tuple[Optional[str], str]:
    candidates = PRESET_NAME_CANDIDATES.get(requested_preset, [requested_preset])

    for candidate in candidates:
        if _try_set_prop(scanner_props, "scannerName", candidate):
            return candidate, "set directly"

    enum_ids = _get_enum_identifiers(scanner_props, "scannerName")
    lowered_candidates = [c.lower() for c in candidates]

    for enum_id in enum_ids:
        enum_low = enum_id.lower()
        if enum_low in lowered_candidates:
            if _try_set_prop(scanner_props, "scannerName", enum_id):
                return enum_id, "matched enum identifier"

        if any(c in enum_low or enum_low in c for c in lowered_candidates):
            if _try_set_prop(scanner_props, "scannerName", enum_id):
                return enum_id, "fuzzy enum match"

    return None, "no matching scannerName enum value"


def _apply_noise_toggle(scene, enabled: bool) -> Tuple[bool, Optional[str]]:
    scanner_props = _get_scanner_properties(scene)
    if scanner_props is None:
        return False, None

    property_candidates = (
        "addNoise",
        "noise_enabled",
        "enableNoise",
        "useNoise",
        "use_noise",
    )
    for prop_name in property_candidates:
        if _try_set_prop(scanner_props, prop_name, bool(enabled)):
            return True, prop_name
    return False, None


def _resolve_export_directory(directory: str) -> str:
    if not directory:
        raise ValueError("Export directory is empty.")

    if directory.startswith("//"):
        resolved = bpy.path.abspath(directory)
    elif os.path.isabs(directory):
        resolved = directory
    else:
        blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
        resolved = os.path.join(blend_dir, directory)

    return os.path.abspath(resolved)


def _apply_scanner_runtime_hints(
    scene,
    camera_obj: bpy.types.Object,
    export_cfg: Dict,
    warnings: List[str],
) -> None:
    scanner_props = _get_scanner_properties(scene)
    if scanner_props is None:
        warnings.append("scannerProperties not found. Could not set scanner add-on properties directly.")
        return

    _try_set_prop(scanner_props, "scannerObject", camera_obj)
    _try_set_prop(scanner_props, "scannerCategory", "lidar")
    _try_set_prop(scanner_props, "addMesh", True)

    # Keep scanner add-on exports disabled; this controller exports explicitly after scan.
    # This avoids dependency/API mismatches across scanner add-on versions.
    for prop in ("exportCSV", "exportLAS", "exportHDF", "exportPLY"):
        _try_set_prop(scanner_props, prop, False)

    resolved_dir = None
    try:
        resolved_dir = _resolve_export_directory(export_cfg["directory"])
    except Exception as exc:
        warnings.append(f"Could not resolve scanner export directory for scanner add-on properties: {exc}")

    if resolved_dir:
        _try_set_prop(scanner_props, "dataFilePath", resolved_dir)
    _try_set_prop(scanner_props, "dataFileName", export_cfg["filename"])


def _snapshot_objects() -> Dict:
    objects = list(bpy.data.objects)
    return {
        "pointers": {obj.as_pointer() for obj in objects},
        "index_by_pointer": {obj.as_pointer(): idx for idx, obj in enumerate(objects)},
    }


def run_scan(context: bpy.types.Context, scan_candidates: Sequence[str]) -> str:
    """
    Try candidate scan operators and execute the first successful one.
    Returns the operator idname used.
    """
    if not scan_candidates:
        raise RuntimeError("No scan operator candidates were discovered.")

    errors: List[str] = []
    for op_idname in scan_candidates:
        ok, detail = _call_operator_safe(context, op_idname)
        if ok:
            _log(f"Scan operator succeeded: {op_idname} ({detail})")
            return op_idname
        errors.append(f"{op_idname}: {detail}")

    short_errors = "; ".join(errors[:8])
    raise RuntimeError(f"Failed to execute any scan operator. Attempts: {short_errors}")


def find_pointcloud_obj(before_snapshot: Optional[Dict] = None) -> Tuple[Optional[bpy.types.Object], str]:
    """
    Heuristic:
    1) Prefer newly created MESH/POINTCLOUD objects after scan call.
    2) Prefer names containing point/cloud/scan keywords.
    3) Prefer latest object index.
    """
    before_pointers = set()
    if before_snapshot:
        before_pointers = set(before_snapshot.get("pointers", set()))

    all_objects = list(bpy.data.objects)
    candidates: List[Tuple[float, bpy.types.Object, bool, bool]] = []

    for idx, obj in enumerate(all_objects):
        if obj.type not in {"MESH", "POINTCLOUD"}:
            continue

        name_low = obj.name.lower()
        is_new = obj.as_pointer() not in before_pointers
        has_keyword = any(k in name_low for k in POINTCLOUD_NAME_KEYWORDS)

        score = 0.0
        if is_new:
            score += 100.0
        if has_keyword:
            score += 40.0
        if obj.type == "POINTCLOUD":
            score += 5.0
        score += idx / 1000.0

        candidates.append((score, obj, is_new, has_keyword))

    if not candidates:
        return None, "No MESH or POINTCLOUD objects found."

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, best_obj, is_new, has_keyword = candidates[0]

    reason_parts = []
    if is_new:
        reason_parts.append("newly created after scan")
    if has_keyword:
        reason_parts.append("name matched point/cloud/scan heuristic")
    reason_parts.append(f"type={best_obj.type}")
    return best_obj, ", ".join(reason_parts)


def _collect_world_points(point_obj: bpy.types.Object) -> List[Vector]:
    points: List[Vector] = []

    if point_obj.type == "MESH":
        mesh = point_obj.data
        for vertex in mesh.vertices:
            points.append(point_obj.matrix_world @ vertex.co)
        return points

    if point_obj.type == "POINTCLOUD":
        point_data = getattr(point_obj.data, "points", None)
        if point_data is None:
            return points
        for point in point_data:
            co = getattr(point, "co", None)
            if co is None:
                co = getattr(point, "position", None)
            if co is None:
                continue
            try:
                points.append(point_obj.matrix_world @ Vector(co))
            except Exception:
                continue
        return points

    return points


def _export_csv_points(point_obj: bpy.types.Object, csv_path: str) -> int:
    points = _collect_world_points(point_obj)
    if not points:
        raise RuntimeError(f"No points available to export from object '{point_obj.name}'.")

    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("x", "y", "z"))
        for point in points:
            writer.writerow((point.x, point.y, point.z))

    return len(points)


def _export_as_ply(context: bpy.types.Context, point_obj: bpy.types.Object, ply_path: str) -> Tuple[bool, str]:
    export_mesh_ops = getattr(bpy.ops, "export_mesh", None)
    if export_mesh_ops is None or not hasattr(export_mesh_ops, "ply"):
        return False, "bpy.ops.export_mesh.ply is unavailable."
    if point_obj.type != "MESH":
        return False, f"PLY exporter requires MESH object, got {point_obj.type}."

    view_layer = context.view_layer
    prev_active = view_layer.objects.active
    prev_selected = list(context.selected_objects)

    try:
        for obj in prev_selected:
            try:
                obj.select_set(False)
            except Exception:
                pass

        point_obj.select_set(True)
        view_layer.objects.active = point_obj

        result = bpy.ops.export_mesh.ply(
            "EXEC_DEFAULT",
            filepath=ply_path,
            use_selection=True,
            check_existing=False,
        )
        if result and "FINISHED" in result:
            return True, "PLY export succeeded."
        return False, f"PLY export returned: {result}"
    except Exception as exc:
        return False, str(exc)
    finally:
        try:
            point_obj.select_set(False)
        except Exception:
            pass
        for obj in prev_selected:
            try:
                obj.select_set(True)
            except Exception:
                pass
        try:
            view_layer.objects.active = prev_active
        except Exception:
            pass


def export_pointcloud(
    context: bpy.types.Context,
    point_obj: bpy.types.Object,
    export_cfg: Dict,
) -> Tuple[str, str]:
    """
    Export point cloud according to config format.
    CSV: direct writer (always supported here).
    PLY: bpy.ops.export_mesh.ply for MESH, else CSV fallback.
    LAS/HDF: clear message + CSV fallback.
    """
    if point_obj is None:
        raise ValueError("No point cloud object provided for export.")

    export_format = export_cfg["format"].upper()
    output_dir = _resolve_export_directory(export_cfg["directory"])
    file_stem = os.path.basename(export_cfg["filename"].strip())
    if not file_stem:
        raise ValueError("Export filename is empty after sanitization.")

    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, f"{file_stem}.csv")

    if export_format == "CSV":
        point_count = _export_csv_points(point_obj, csv_path)
        return csv_path, f"CSV export complete ({point_count} points)."

    if export_format == "PLY":
        ply_path = os.path.join(output_dir, f"{file_stem}.ply")
        ok, detail = _export_as_ply(context, point_obj, ply_path)
        if ok:
            return ply_path, detail
        point_count = _export_csv_points(point_obj, csv_path)
        message = f"PLY not available ({detail}). CSV fallback written ({point_count} points)."
        return csv_path, message

    if export_format in {"LAS", "HDF"}:
        point_count = _export_csv_points(point_obj, csv_path)
        message = f"{export_format} is not available in Blender core. CSV fallback written ({point_count} points)."
        return csv_path, message

    raise ValueError(f"Unsupported export format: {export_format}")


class LLM_LIDAR_ControllerProps(PropertyGroup):
    config_path: StringProperty(
        name="Config JSON",
        description="Path to scanner control JSON config",
        subtype="FILE_PATH",
        default="",
    )
    status_text: StringProperty(
        name="Status",
        description="Last run status",
        default="Idle.",
    )
    last_pointcloud_name: StringProperty(
        name="Last Point Cloud Object",
        default="",
    )
    last_export_path: StringProperty(
        name="Last Export Path",
        default="",
    )
    last_preset: StringProperty(
        name="Last Preset",
        default="",
    )
    last_export_format: StringProperty(
        name="Last Export Format",
        default="CSV",
    )
    last_export_directory: StringProperty(
        name="Last Export Directory",
        default="",
    )
    last_export_filename: StringProperty(
        name="Last Export Filename",
        default="scan_output",
    )


class LLM_LIDAR_OT_ApplyConfigRunScan(Operator):
    bl_idname = "llm_lidar.apply_config_run_scan"
    bl_label = "Apply Config & Run Scan"
    bl_description = "Read JSON config, apply scanner/camera settings, run scan, and export detected point cloud"

    def execute(self, context):
        scene = context.scene
        ctrl = scene.llm_lidar_ctrl
        warnings: List[str] = []

        try:
            config = load_config(ctrl.config_path)
            _status_append(context, "Config loaded and validated.", reset=True)
        except Exception as exc:
            message = f"Config validation failed: {exc}"
            _status_append(context, message, reset=True)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        ctrl.last_preset = config["scanner_preset"]
        ctrl.last_export_format = config["export"]["format"]
        ctrl.last_export_directory = config["export"]["directory"]
        ctrl.last_export_filename = config["export"]["filename"]

        try:
            camera_obj, camera_warnings = ensure_camera(context, config)
            warnings.extend(camera_warnings)
            _status_append(context, f"Using camera: {camera_obj.name}")
            for msg in apply_transforms(camera_obj, config):
                _status_append(context, msg)
        except Exception as exc:
            message = f"Camera setup failed: {exc}"
            _status_append(context, message)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        scanner_props = _get_scanner_properties(scene)
        if scanner_props is None:
            warnings.append(
                "Could not find scene.scannerProperties. Ensure the scanner add-on is enabled."
            )
        else:
            _try_set_prop(scanner_props, "scannerObject", camera_obj)
            _try_set_prop(scanner_props, "scannerCategory", "lidar")

        discovered_ops = find_scanner_ops()
        _log(f"Discovered scanner-related operators: {discovered_ops['all_candidates']}")

        preset_assigned = None
        preset_assign_detail = ""
        if scanner_props is not None:
            preset_assigned, preset_assign_detail = _assign_preset_name(
                scanner_props,
                config["scanner_preset"],
            )
            if preset_assigned:
                _status_append(
                    context,
                    f"Preset mapped to scannerName='{preset_assigned}' ({preset_assign_detail}).",
                )
            else:
                warnings.append(
                    f"Could not map preset '{config['scanner_preset']}' to scannerName ({preset_assign_detail})."
                )

        preset_loaded = False
        preset_op_used = ""
        for preset_op in discovered_ops["preset_candidates"]:
            ok, detail = _call_operator_safe(context, preset_op)
            if ok:
                preset_loaded = True
                preset_op_used = preset_op
                _status_append(context, f"Loaded preset via operator: {preset_op}")
                break

        if not preset_loaded:
            warnings.append(
                f"No working preset loader was found. Stored preset '{config['scanner_preset']}' only."
            )

        if "noise_enabled" in config:
            noise_ok, noise_prop = _apply_noise_toggle(scene, config["noise_enabled"])
            if noise_ok:
                _status_append(context, f"Noise toggle applied via property '{noise_prop}'.")
            else:
                warnings.append("Noise toggle property was not found on scanner add-on. Ignored.")

        _apply_scanner_runtime_hints(scene, camera_obj, config["export"], warnings)

        before_snapshot = _snapshot_objects()

        try:
            scan_op_used = run_scan(context, discovered_ops["scan_candidates"])
            _status_append(context, f"Scan executed via operator: {scan_op_used}")
        except Exception as exc:
            candidate_ops = ", ".join(discovered_ops["scan_candidates"][:20]) or "none"
            message = (
                f"Scan execution failed: {exc}. "
                f"Discovered scan operator candidates: {candidate_ops}"
            )
            _status_append(context, message)
            self.report({"ERROR"}, "Scan failed. See status panel for details.")
            return {"CANCELLED"}

        point_obj, detection_reason = find_pointcloud_obj(before_snapshot)
        if point_obj is None:
            message = "Scan finished but no point cloud object was detected."
            _status_append(context, message)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        ctrl.last_pointcloud_name = point_obj.name
        _status_append(context, f"Detected point cloud object: {point_obj.name} ({detection_reason}).")

        try:
            export_path, export_detail = export_pointcloud(context, point_obj, config["export"])
            ctrl.last_export_path = export_path
            _status_append(context, f"{export_detail}")
            _status_append(context, f"Export path: {export_path}")
        except Exception as exc:
            message = f"Export failed: {exc}"
            _status_append(context, message)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        if warnings:
            for warning in warnings:
                _status_append(context, f"Warning: {warning}")
            self.report({"WARNING"}, "Completed with warnings. Check status panel.")
        else:
            self.report({"INFO"}, "Scan and export completed.")

        return {"FINISHED"}


class LLM_LIDAR_OT_ExportLastPointCloud(Operator):
    bl_idname = "llm_lidar.export_last_pointcloud"
    bl_label = "Export Last Point Cloud"
    bl_description = "Export the last detected point cloud object using the current config export settings"

    def execute(self, context):
        scene = context.scene
        ctrl = scene.llm_lidar_ctrl

        if not ctrl.last_pointcloud_name:
            message = "No previously detected point cloud object is stored."
            _status_append(context, message, reset=True)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        point_obj = bpy.data.objects.get(ctrl.last_pointcloud_name)
        if point_obj is None:
            message = f"Stored point cloud object '{ctrl.last_pointcloud_name}' no longer exists."
            _status_append(context, message, reset=True)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        export_cfg = None
        try:
            config = load_config(ctrl.config_path)
            export_cfg = config["export"]
            _status_append(context, "Loaded export settings from config file.", reset=True)
        except Exception:
            if (
                ctrl.last_export_directory
                and ctrl.last_export_filename
                and ctrl.last_export_format in ALLOWED_EXPORT_FORMATS
            ):
                export_cfg = {
                    "format": ctrl.last_export_format,
                    "directory": ctrl.last_export_directory,
                    "filename": ctrl.last_export_filename,
                }
                _status_append(
                    context,
                    "Config unavailable. Using last successful export settings.",
                    reset=True,
                )

        if export_cfg is None:
            message = "Could not determine export settings from config or cached values."
            _status_append(context, message)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}

        try:
            export_path, detail = export_pointcloud(context, point_obj, export_cfg)
            ctrl.last_export_path = export_path
            _status_append(context, detail)
            _status_append(context, f"Export path: {export_path}")
            self.report({"INFO"}, "Export completed.")
            return {"FINISHED"}
        except Exception as exc:
            message = f"Export failed: {exc}"
            _status_append(context, message)
            self.report({"ERROR"}, message)
            return {"CANCELLED"}


class LLM_LIDAR_PT_ControlPanel(Panel):
    bl_label = "LLM LiDAR Control"
    bl_idname = "LLM_LIDAR_PT_control_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LLM LiDAR Control"

    def draw(self, context):
        layout = self.layout
        ctrl = context.scene.llm_lidar_ctrl

        layout.prop(ctrl, "config_path", text="JSON Config")

        layout.operator(LLM_LIDAR_OT_ApplyConfigRunScan.bl_idname, icon="PLAY")
        layout.operator(LLM_LIDAR_OT_ExportLastPointCloud.bl_idname, icon="EXPORT")

        if ctrl.last_pointcloud_name:
            layout.label(text=f"Last point cloud: {ctrl.last_pointcloud_name}")
        if ctrl.last_export_path:
            layout.label(text=f"Last export: {ctrl.last_export_path}")

        box = layout.box()
        box.label(text="Status")
        status_lines = ctrl.status_text.splitlines() if ctrl.status_text else ["Idle."]
        for line in status_lines[-12:]:
            box.label(text=line[:130])


CLASSES = (
    LLM_LIDAR_ControllerProps,
    LLM_LIDAR_OT_ApplyConfigRunScan,
    LLM_LIDAR_OT_ExportLastPointCloud,
    LLM_LIDAR_PT_ControlPanel,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.llm_lidar_ctrl = PointerProperty(type=LLM_LIDAR_ControllerProps)
    _log("Registered add-on.")


def unregister():
    if hasattr(bpy.types.Scene, "llm_lidar_ctrl"):
        del bpy.types.Scene.llm_lidar_ctrl
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
    _log("Unregistered add-on.")


if __name__ == "__main__":
    register()
