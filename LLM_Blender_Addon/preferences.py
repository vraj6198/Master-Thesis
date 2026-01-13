"""
Preferences Module
Addon preferences for API keys and settings
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty


class LLMAddonPreferences(AddonPreferences):
    """Preferences for LLM 3D Generator addon"""
    bl_idname = __package__
    
    # API Keys
    openai_api_key: StringProperty(
        name="OpenAI API Key",
        description="Your OpenAI API key for GPT models",
        default="",
        subtype='PASSWORD'
    )
    
    gemini_api_key: StringProperty(
        name="Gemini API Key",
        description="Your Google Gemini API key",
        default="",
        subtype='PASSWORD'
    )
    
    ollama_server_url: StringProperty(
        name="Ollama Server URL",
        description="URL of your Ollama server",
        default="http://localhost:11434"
    )
    
    def draw(self, context):
        layout = self.layout
        
        # OpenAI Section
        box = layout.box()
        box.label(text="OpenAI Settings", icon='COMMUNITY')
        box.prop(self, "openai_api_key")
        box.label(text="Get your API key from: https://platform.openai.com/api-keys", icon='URL')
        
        # Gemini Section
        box = layout.box()
        box.label(text="Google Gemini Settings", icon='COMMUNITY')
        box.prop(self, "gemini_api_key")
        box.label(text="Get your API key from: https://makersuite.google.com/app/apikey", icon='URL')
        
        # Ollama Section
        box = layout.box()
        box.label(text="Ollama Settings", icon='COMMUNITY')
        box.prop(self, "ollama_server_url")
        box.label(text="Make sure Ollama is running locally", icon='INFO')


def register():
    bpy.utils.register_class(LLMAddonPreferences)


def unregister():
    bpy.utils.unregister_class(LLMAddonPreferences)
