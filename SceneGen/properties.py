import bpy
from bpy.props import StringProperty, PointerProperty
from bpy.types import PropertyGroup


class SceneGenProperties(PropertyGroup):
    """Properties for the SceneGen add-on."""
    
    user_prompt: StringProperty(
        name="User Prompt",
        description="Describe the scene you want to generate",
        default="A simple wooden chair"
    )
    
    json_spec: StringProperty(
        name="JSON Spec",
        description="JSON specification for the scene",
        default=""
    )
    
    log_output: StringProperty(
        name="Log Output",
        description="Validation and build log messages",
        default=""
    )


def register():
    bpy.utils.register_class(SceneGenProperties)
    bpy.types.Scene.scene_gen = PointerProperty(type=SceneGenProperties)


def unregister():
    del bpy.types.Scene.scene_gen
    bpy.utils.unregister_class(SceneGenProperties)
