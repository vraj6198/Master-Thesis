# Add-on preferences for LLM prompt parsing
import bpy
from bpy.props import StringProperty, FloatProperty, IntProperty


class LIDAR_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "LiDAR_Scanner_Addon"

    llm_endpoint: StringProperty(
        name="LLM Endpoint",
        description="OpenAI-compatible chat completions endpoint (e.g. Ollama: http://localhost:11434/v1/chat/completions)",
        default="http://localhost:11434/v1/chat/completions",
    )

    llm_model: StringProperty(
        name="LLM Model",
        description="Model name to use at the endpoint",
        default="llama3.1",
    )

    llm_api_key: StringProperty(
        name="API Key",
        description="API key for hosted LLMs (leave empty for local endpoints)",
        default="",
        subtype='PASSWORD',
    )

    llm_temperature: FloatProperty(
        name="Temperature",
        description="LLM sampling temperature",
        default=0.0,
        min=0.0,
        max=2.0,
    )

    llm_timeout_s: IntProperty(
        name="Timeout (s)",
        description="Request timeout in seconds",
        default=30,
        min=5,
        max=300,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="LLM settings moved to the LiDAR panel")


def register():
    bpy.utils.register_class(LIDAR_AddonPreferences)


def unregister():
    bpy.utils.unregister_class(LIDAR_AddonPreferences)
