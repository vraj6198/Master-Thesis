bl_info = {
    "name": "LLM LiDAR Controller (BLAINDER)",
    "author": "Codex",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > LLM LiDAR",
    "description": "LLM-driven controller for the BLAINDER Range Scanner add-on",
    "category": "3D View",
}

import bpy

from . import model_catalog

from . import operators
from . import properties
from . import ui


class LLMLidarPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    llm_provider: bpy.props.EnumProperty(
        name="LLM Provider",
        items=[
            ("OLLAMA_LOCAL", "Ollama Local", "Use a local Ollama server"),
            ("OPENAI", "OpenAI", "Use the OpenAI API"),
            ("GEMINI", "Gemini", "Use the Google Gemini API"),
            ("OPENAI_COMPAT", "OpenAI-Compatible", "Use a custom OpenAI-compatible endpoint"),
        ],
        default="OLLAMA_LOCAL",
    )

    llm_endpoint_ollama: bpy.props.StringProperty(
        name="Ollama Endpoint",
        default="http://localhost:11434/api/generate",
    )

    llm_endpoint_openai: bpy.props.StringProperty(
        name="OpenAI Endpoint",
        default="https://api.openai.com/v1/chat/completions",
    )

    llm_endpoint_gemini: bpy.props.StringProperty(
        name="Gemini Endpoint",
        default="https://generativelanguage.googleapis.com/v1beta/models",
    )

    llm_model: bpy.props.EnumProperty(
        name="Model",
        items=model_catalog.ALL_ITEMS,
        default=model_catalog.DEFAULT_MODEL_ID,
    )

    llm_custom_model: bpy.props.StringProperty(
        name="Custom Model",
        default="",
    )

    llm_api_key_openai: bpy.props.StringProperty(
        name="OpenAI API Key",
        subtype='PASSWORD',
        default="",
    )

    llm_api_key_gemini: bpy.props.StringProperty(
        name="Gemini API Key",
        subtype='PASSWORD',
        default="",
    )

    llm_timeout: bpy.props.IntProperty(
        name="Timeout",
        description="Request timeout in seconds",
        default=60,
        min=5,
        max=600,
    )

    scan_operator_id: bpy.props.StringProperty(
        name="Scan Operator",
        description="Preferred scan operator idname",
        default="",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "llm_provider")
        if self.llm_provider == "OPENAI":
            layout.prop(self, "llm_endpoint_openai")
            layout.prop(self, "llm_api_key_openai")
        elif self.llm_provider == "GEMINI":
            layout.prop(self, "llm_endpoint_gemini")
            layout.prop(self, "llm_api_key_gemini")
        elif self.llm_provider == "OPENAI_COMPAT":
            layout.prop(self, "llm_endpoint_openai")
            layout.prop(self, "llm_api_key_openai")
        else:
            layout.prop(self, "llm_endpoint_ollama")
        layout.prop(self, "llm_model")
        if self.llm_model == model_catalog.CUSTOM_ID:
            layout.prop(self, "llm_custom_model")
        layout.prop(self, "llm_timeout")
        layout.prop(self, "scan_operator_id")


CLASSES = (
    LLMLidarPreferences,
    properties.LLMLidarSettings,
    operators.LLM_OT_UseBundledConfig,
    operators.LLM_OT_GeneratePatch,
    operators.LLM_OT_ApplyPatch,
    operators.LLM_OT_RunScan,
    operators.LLM_OT_RunPipeline,
    operators.LLM_OT_AnalyzeScan,
    operators.LLM_OT_DetectScanOperator,
    ui.LLM_PT_MainPanel,
)

def _safe_unregister(cls):
    existing = getattr(bpy.types, cls.__name__, None)
    if existing:
        try:
            bpy.utils.unregister_class(existing)
            return
        except Exception:
            pass
    try:
        bpy.utils.unregister_class(cls)
    except Exception:
        pass


def register():
    for cls in CLASSES:
        _safe_unregister(cls)
        bpy.utils.register_class(cls)

    if hasattr(bpy.types.Scene, "llm_lidar_settings"):
        try:
            del bpy.types.Scene.llm_lidar_settings
        except Exception:
            pass
    bpy.types.Scene.llm_lidar_settings = bpy.props.PointerProperty(
        type=properties.LLMLidarSettings
    )


def unregister():
    if hasattr(bpy.types.Scene, "llm_lidar_settings"):
        del bpy.types.Scene.llm_lidar_settings

    for cls in reversed(CLASSES):
        _safe_unregister(cls)


if __name__ == "__main__":
    register()
