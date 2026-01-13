bl_info = {
    "name": "LLM 3D Generator",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > LLM AI",
    "description": "Generate 3D scenes using Local (Ollama) and Cloud-based LLMs (OpenAI, Gemini)",
    "category": "3D View",
}

import bpy
from . import preferences
from . import operators
from . import ui
from . import llm_integration
from . import scene_generator

modules = [
    preferences,
    operators,
    ui,
]

def register():
    """Register all addon classes"""
    for module in modules:
        module.register()

def unregister():
    """Unregister all addon classes"""
    for module in reversed(modules):
        module.unregister()

if __name__ == "__main__":
    register()
