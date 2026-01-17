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


def register():
    from . import properties
    from . import preferences
    from . import operators
    from . import panels
    
    preferences.register()
    properties.register()
    operators.register()
    panels.register()


def unregister():
    from . import properties
    from . import preferences
    from . import operators
    from . import panels
    
    panels.unregister()
    operators.unregister()
    properties.unregister()
    preferences.unregister()


if __name__ == "__main__":
    register()
