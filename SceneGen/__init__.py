bl_info = {
    "name": "SceneGen",
    "author": "SceneGen Developer",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > SceneGen",
    "description": "Generate 3D scenes from JSON specifications",
    "category": "3D View",
}

import bpy
from . import operators
from . import panels
from . import properties


def register():
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == "__main__":
    register()
