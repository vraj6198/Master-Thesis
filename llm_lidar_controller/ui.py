import bpy

from . import utils


class LLM_PT_MainPanel(bpy.types.Panel):
    bl_label = "LLM LiDAR Controller"
    bl_idname = "LLM_PT_LidarController"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "LLM LiDAR"

    def draw(self, context):
        layout = self.layout
        settings = utils.get_settings(context)
        prefs = utils.get_addon_prefs(context)

        if not hasattr(bpy.types.Scene, "scannerProperties"):
            layout.label(text="BLAINDER Range Scanner is not enabled.", icon="ERROR")
            return

        box = layout.box()
        box.label(text="Base Config")
        row = box.row()
        row.prop(settings, "base_config_path", text="")
        row.operator("llm_lidar.use_bundled_config", text="Use Bundled")

        box = layout.box()
        box.label(text="LLM Request")
        box.prop(settings, "command_text", text="User Prompt")
        box.operator("llm_lidar.generate_patch", text="Generate Patch")
        box.prop(settings, "llm_patch", text="Patch JSON")

        box = layout.box()
        box.label(text="Apply + Scan")
        row = box.row()
        row.operator("llm_lidar.apply_patch", text="Validate + Apply")
        row.operator("llm_lidar.run_scan", text="Run Scan")
        box.operator("llm_lidar.run_pipeline", text="Run Full Pipeline")

        box = layout.box()
        box.label(text="Analysis")
        box.operator("llm_lidar.analyze_scan", text="Analyze Last Scan")
        if settings.last_analysis_path:
            box.label(text=f"Last analysis: {settings.last_analysis_path}")

        box = layout.box()
        box.label(text="Scan Operator")
        row = box.row()
        row.prop(settings, "scan_operator_id", text="ID")
        row.operator("llm_lidar.detect_scan_operator", text="Detect")

        if prefs:
            box = layout.box()
            box.label(text="LLM Settings")
            box.prop(prefs, "llm_provider", text="Provider")
            if prefs.llm_provider == "OPENAI":
                box.prop(prefs, "llm_endpoint_openai", text="Endpoint")
                box.prop(prefs, "llm_api_key_openai", text="API Key")
            elif prefs.llm_provider == "GEMINI":
                box.prop(prefs, "llm_endpoint_gemini", text="Endpoint")
                box.prop(prefs, "llm_api_key_gemini", text="API Key")
            elif prefs.llm_provider == "OPENAI_COMPAT":
                box.prop(prefs, "llm_endpoint_openai", text="Endpoint")
                box.prop(prefs, "llm_api_key_openai", text="API Key")
            else:
                box.prop(prefs, "llm_endpoint_ollama", text="Endpoint")
            box.prop(prefs, "llm_model", text="Model")
            if prefs.llm_model == "CUSTOM":
                box.prop(prefs, "llm_custom_model", text="Custom Model")
            box.prop(prefs, "llm_timeout", text="Timeout (s)")

        if settings.last_status:
            layout.label(text=settings.last_status)
