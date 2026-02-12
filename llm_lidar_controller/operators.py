import json
import os
import traceback

import bpy

from . import analysis
from . import config
from . import llm_client
from . import utils


class LLM_OT_UseBundledConfig(bpy.types.Operator):
    bl_idname = "llm_lidar.use_bundled_config"
    bl_label = "Use Bundled Config"
    bl_description = "Use the bundled base_config.json"

    def execute(self, context):
        settings = utils.get_settings(context)
        settings.base_config_path = utils.get_bundled_config_path()
        settings.last_status = "Bundled base config selected."
        return {'FINISHED'}


class LLM_OT_GeneratePatch(bpy.types.Operator):
    bl_idname = "llm_lidar.generate_patch"
    bl_label = "Generate Patch"
    bl_description = "Generate a JSON patch using the configured LLM"

    def execute(self, context):
        settings = utils.get_settings(context)
        if not settings.command_text.strip():
            self.report({'WARNING'}, "Enter a natural-language command first.")
            return {'CANCELLED'}

        try:
            base_config = config.load_base_config(settings.base_config_path)
            patch, patch_text, _raw = llm_client.generate_patch(settings, base_config, settings.command_text)
            settings.llm_patch = json.dumps(patch, indent=2, sort_keys=True)
            settings.last_status = "Patch generated."
        except Exception as exc:
            settings.last_status = f"Patch generation failed: {exc}"
            self.report({'ERROR'}, settings.last_status)
            return {'CANCELLED'}

        return {'FINISHED'}


class LLM_OT_ApplyPatch(bpy.types.Operator):
    bl_idname = "llm_lidar.apply_patch"
    bl_label = "Validate + Apply Patch"
    bl_description = "Validate, clamp, and apply the patch to BLAINDER"

    @classmethod
    def poll(cls, context):
        return hasattr(bpy.types.Scene, "scannerProperties")

    def execute(self, context):
        settings = utils.get_settings(context)
        if not settings.llm_patch.strip():
            self.report({'WARNING'}, "No patch JSON to apply.")
            return {'CANCELLED'}

        try:
            patch_data = json.loads(settings.llm_patch)
        except json.JSONDecodeError as exc:
            self.report({'ERROR'}, f"Invalid JSON patch: {exc}")
            return {'CANCELLED'}

        base_config = config.load_base_config(settings.base_config_path)
        merged = config.merge_patch(base_config, patch_data)
        sanitized, errors, warnings = config.validate_and_clamp_config(context, merged)

        if errors:
            settings.last_status = utils.format_status("Patch validation failed", warnings)
            for err in errors:
                self.report({'ERROR'}, err)
            return {'CANCELLED'}

        applied, apply_errors, apply_warnings = config.apply_config(context, sanitized)
        warnings.extend(apply_warnings)
        if apply_errors:
            for err in apply_errors:
                self.report({'ERROR'}, err)
            settings.last_status = utils.format_status("Apply failed", warnings)
            return {'CANCELLED'}

        if not applied:
            settings.last_status = utils.format_status("Apply failed", warnings)
            return {'CANCELLED'}

        settings.last_status = utils.format_status("Patch applied", warnings)
        if warnings:
            for warn in warnings:
                self.report({'WARNING'}, warn)
        return {'FINISHED'}


class LLM_OT_RunScan(bpy.types.Operator):
    bl_idname = "llm_lidar.run_scan"
    bl_label = "Run Scan"
    bl_description = "Trigger the BLAINDER scan operator"

    @classmethod
    def poll(cls, context):
        return hasattr(bpy.types.Scene, "scannerProperties")

    def execute(self, context):
        settings = utils.get_settings(context)
        prefs = utils.get_addon_prefs(context)
        preferred = settings.scan_operator_id or (prefs.scan_operator_id if prefs else "")
        op_id = utils.resolve_scan_operator(preferred)
        if not op_id:
            self.report({'ERROR'}, "Scan operator not found. Use Detect Operator.")
            return {'CANCELLED'}

        settings.scan_operator_id = op_id
        module_name, op_name = op_id.split(".", 1)
        try:
            op_func = getattr(getattr(bpy.ops, module_name), op_name)
            result = op_func()
        except Exception as exc:
            self.report({'ERROR'}, f"Scan failed: {exc}")
            return {'CANCELLED'}

        settings.last_status = f"Scan triggered ({op_id})."
        return result


class LLM_OT_RunPipeline(bpy.types.Operator):
    bl_idname = "llm_lidar.run_pipeline"
    bl_label = "Run Full Pipeline"
    bl_description = "Apply patch, run scan, and analyze output"

    @classmethod
    def poll(cls, context):
        return hasattr(bpy.types.Scene, "scannerProperties")

    def execute(self, context):
        apply_result = bpy.ops.llm_lidar.apply_patch()
        if apply_result != {'FINISHED'}:
            return {'CANCELLED'}

        scan_result = bpy.ops.llm_lidar.run_scan()
        if scan_result != {'FINISHED'}:
            return {'CANCELLED'}

        analyze_result = bpy.ops.llm_lidar.analyze_scan()
        return analyze_result


class LLM_OT_AnalyzeScan(bpy.types.Operator):
    bl_idname = "llm_lidar.analyze_scan"
    bl_label = "Analyze Last Scan"
    bl_description = "Analyze the exported point cloud and save JSON next to it"

    @classmethod
    def poll(cls, context):
        return hasattr(bpy.types.Scene, "scannerProperties")

    def execute(self, context):
        settings = utils.get_settings(context)
        props = context.scene.scannerProperties
        output_dir = bpy.path.abspath(props.dataFilePath)

        if not output_dir:
            self.report({'ERROR'}, "Output directory is empty.")
            return {'CANCELLED'}

        if not os.path.isdir(output_dir):
            self.report({'ERROR'}, f"Output directory does not exist: {output_dir}")
            return {'CANCELLED'}

        base_name = analysis.resolve_expected_basename(props)
        preferred_exts = []
        if props.exportCSV:
            preferred_exts.append(".csv")
        if props.exportPLY:
            preferred_exts.append(".ply")
        if not preferred_exts:
            preferred_exts = [".csv", ".ply"]

        data_path = analysis.find_latest_export(output_dir, base_name, preferred_exts)
        if not data_path:
            self.report({'ERROR'}, "No exported point cloud found in output directory.")
            return {'CANCELLED'}

        try:
            summary = analysis.analyze_point_cloud(data_path)
        except Exception as exc:
            self.report({'ERROR'}, f"Analysis failed: {exc}")
            return {'CANCELLED'}

        analysis_name = f"{base_name}_analysis.json"
        analysis_path = os.path.join(output_dir, analysis_name)
        if not utils.ensure_within_dir(analysis_path, output_dir):
            self.report({'ERROR'}, "Refusing to write outside output directory.")
            return {'CANCELLED'}

        try:
            utils.write_json(analysis_path, summary)
        except Exception as exc:
            self.report({'ERROR'}, f"Failed to write analysis JSON: {exc}")
            return {'CANCELLED'}

        settings.last_analysis_path = analysis_path
        settings.last_status = f"Analysis saved: {analysis_path}"
        return {'FINISHED'}


class LLM_OT_DetectScanOperator(bpy.types.Operator):
    bl_idname = "llm_lidar.detect_scan_operator"
    bl_label = "Detect Scan Operator"
    bl_description = "Find the registered scan operator"

    def execute(self, context):
        settings = utils.get_settings(context)
        prefs = utils.get_addon_prefs(context)
        preferred = settings.scan_operator_id or (prefs.scan_operator_id if prefs else "")
        op_id = utils.resolve_scan_operator(preferred)
        if not op_id:
            self.report({'ERROR'}, "Scan operator not found.")
            return {'CANCELLED'}
        settings.scan_operator_id = op_id
        settings.last_status = f"Detected scan operator: {op_id}"
        return {'FINISHED'}
