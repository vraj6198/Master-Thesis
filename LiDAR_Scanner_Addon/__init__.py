# LiDAR Scanner Addon for Blender
# Inspired by blainder-range-scanner (https://github.com/ln-12/blainder-range-scanner)

bl_info = {
    "name": "LiDAR Scanner Simulator",
    "author": "MT Project",
    "description": "Simulate LiDAR scanning with customizable parameters, noise, and export options",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "location": "3D View > Sidebar > LiDAR Scanner",
    "warning": "",
    "category": "3D View",
}

import bpy

from . import properties
from . import operators
from . import panels
from . import scanner_core
from . import export_utils
from . import preferences


def register():
    bpy.utils.register_class(preferences.LIDAR_AddonPreferences)
    properties.register()
    operators.register()
    panels.register()


def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
    bpy.utils.unregister_class(preferences.LIDAR_AddonPreferences)


if __name__ == "__main__":
    register()
