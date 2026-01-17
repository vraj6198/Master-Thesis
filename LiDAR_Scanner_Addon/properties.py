# LiDAR Scanner Properties
import bpy
from bpy.props import (
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
)
from bpy.types import PropertyGroup


class LiDARScannerSettings(PropertyGroup):
    """Main settings for the LiDAR scanner"""
    
    # Sensor Presets
    sensor_preset: EnumProperty(
        name="Sensor Preset",
        description="Select a predefined sensor configuration",
        items=[
            ('AUTO', 'Auto/Custom', 'Custom configuration'),
            ('VELODYNE_VLP16', 'Velodyne VLP-16', 'Velodyne VLP-16 Puck (16 channels, 360° FOV)'),
            ('VELODYNE_HDL32', 'Velodyne HDL-32E', 'Velodyne HDL-32E (32 channels)'),
            ('VELODYNE_HDL64', 'Velodyne HDL-64E', 'Velodyne HDL-64E (64 channels)'),
            ('OUSTER_OS1_32', 'Ouster OS1-32', 'Ouster OS1 32 channels'),
            ('OUSTER_OS1_64', 'Ouster OS1-64', 'Ouster OS1 64 channels'),
            ('LIVOX_MID40', 'Livox Mid-40', 'Livox Mid-40 (non-repetitive scanning)'),
            ('GENERIC_32', 'Generic 32-Channel', 'Generic 32-channel LiDAR'),
            ('GENERIC_64', 'Generic 64-Channel', 'Generic 64-channel LiDAR'),
        ],
        default='AUTO',
        update=lambda self, ctx: apply_preset(self, ctx)
    )
    
    # Scanner Object
    scanner_object: PointerProperty(
        name="Scanner Object",
        description="Object to use as LiDAR scanner origin (typically a Camera or Empty)",
        type=bpy.types.Object,
    )
    
    # Origin Position
    origin: FloatVectorProperty(
        name="Origin",
        description="Scanner origin position (X, Y, Z)",
        default=(0.0, 0.0, 1.8),
        subtype='XYZ',
        unit='LENGTH',
    )
    
    # Rotation
    rotation_deg: FloatVectorProperty(
        name="Rotation",
        description="Scanner rotation in degrees (Rx, Ry, Rz)",
        default=(0.0, 0.0, 0.0),
        subtype='EULER',
    )
    
    # Field of View
    fov_h: FloatProperty(
        name="Horizontal FOV",
        description="Horizontal field of view in degrees (1-360)",
        default=360.0,
        min=1.0,
        max=360.0,
        subtype='ANGLE',
    )
    
    fov_v: FloatProperty(
        name="Vertical FOV",
        description="Vertical field of view in degrees (1-90)",
        default=30.0,
        min=1.0,
        max=90.0,
        subtype='ANGLE',
    )
    
    # Resolution
    resolution_h: FloatProperty(
        name="Horizontal Resolution",
        description="Horizontal resolution in degrees (0.01-5)",
        default=0.2,
        min=0.01,
        max=5.0,
        precision=3,
    )
    
    resolution_v: FloatProperty(
        name="Vertical Resolution",
        description="Vertical resolution in degrees (0.01-5)",
        default=1.0,
        min=0.01,
        max=5.0,
        precision=3,
    )
    
    # Range
    range_min: FloatProperty(
        name="Min Range",
        description="Minimum detection range in meters",
        default=0.1,
        min=0.0,
        max=500.0,
        unit='LENGTH',
    )
    
    range_max: FloatProperty(
        name="Max Range",
        description="Maximum detection range in meters",
        default=100.0,
        min=0.1,
        max=500.0,
        unit='LENGTH',
    )
    
    # Noise Settings
    enable_noise: BoolProperty(
        name="Enable Noise",
        description="Add noise to the scan results",
        default=True,
    )
    
    noise_type: EnumProperty(
        name="Noise Type",
        description="Type of noise distribution",
        items=[
            ('GAUSSIAN', 'Gaussian', 'Gaussian/Normal distribution'),
            ('UNIFORM', 'Uniform', 'Uniform random distribution'),
            ('RAYLEIGH', 'Rayleigh', 'Rayleigh distribution'),
        ],
        default='GAUSSIAN',
    )
    
    range_sigma_m: FloatProperty(
        name="Range Sigma",
        description="Standard deviation of range noise in meters (0-0.5)",
        default=0.02,
        min=0.0,
        max=0.5,
        precision=4,
    )
    
    angular_noise_deg: FloatProperty(
        name="Angular Noise",
        description="Standard deviation of angular noise in degrees",
        default=0.01,
        min=0.0,
        max=1.0,
        precision=4,
    )
    
    dropout_prob: FloatProperty(
        name="Dropout Probability",
        description="Probability of random point dropout (0-0.3)",
        default=0.02,
        min=0.0,
        max=0.3,
        precision=3,
    )
    
    # Intensity Settings
    enable_intensity: BoolProperty(
        name="Calculate Intensity",
        description="Calculate return intensity based on material and distance",
        default=True,
    )
    
    intensity_falloff: EnumProperty(
        name="Intensity Falloff",
        description="How intensity decreases with distance",
        items=[
            ('LINEAR', 'Linear', 'Linear falloff'),
            ('QUADRATIC', 'Quadratic', 'Inverse square falloff (realistic)'),
            ('NONE', 'None', 'No distance falloff'),
        ],
        default='QUADRATIC',
    )
    
    # Multi-return Settings
    enable_multi_return: BoolProperty(
        name="Multi-Return",
        description="Enable multiple returns per ray (for vegetation, etc.)",
        default=False,
    )
    
    max_returns: IntProperty(
        name="Max Returns",
        description="Maximum number of returns per ray",
        default=2,
        min=1,
        max=5,
    )
    
    # Animation Settings
    enable_animation: BoolProperty(
        name="Enable Animation",
        description="Scan across animation frames",
        default=False,
    )
    
    frame_start: IntProperty(
        name="Start Frame",
        description="First frame to scan",
        default=1,
        min=1,
    )
    
    frame_end: IntProperty(
        name="End Frame",
        description="Last frame to scan",
        default=250,
        min=1,
    )
    
    frame_step: IntProperty(
        name="Frame Step",
        description="Step between frames",
        default=1,
        min=1,
    )
    
    rotations_per_second: FloatProperty(
        name="Rotations/Second",
        description="Scanner rotations per second (for rotating scanners)",
        default=10.0,
        min=0.1,
        max=100.0,
    )
    
    # Visualization
    show_scan_preview: BoolProperty(
        name="Show Preview",
        description="Show scan preview in viewport",
        default=True,
    )
    
    preview_point_size: FloatProperty(
        name="Point Size",
        description="Size of preview points",
        default=2.0,
        min=0.5,
        max=10.0,
    )
    
    add_mesh: BoolProperty(
        name="Add Point Cloud Mesh",
        description="Add scanned point cloud as mesh to scene",
        default=True,
    )
    
    color_mode: EnumProperty(
        name="Color Mode",
        description="How to color the point cloud",
        items=[
            ('INTENSITY', 'Intensity', 'Color by return intensity'),
            ('HEIGHT', 'Height', 'Color by Z height'),
            ('DISTANCE', 'Distance', 'Color by distance from scanner'),
            ('OBJECT', 'Object', 'Color by hit object'),
            ('MATERIAL', 'Material', 'Color from object material'),
        ],
        default='INTENSITY',
    )
    
    # Export Settings
    export_ply: BoolProperty(
        name="Export PLY",
        description="Export as PLY format",
        default=True,
    )
    
    export_csv: BoolProperty(
        name="Export CSV",
        description="Export as CSV format",
        default=False,
    )
    
    export_las: BoolProperty(
        name="Export LAS",
        description="Export as LAS format (requires laspy)",
        default=False,
    )
    
    export_pcd: BoolProperty(
        name="Export PCD",
        description="Export as PCD format (Point Cloud Data)",
        default=False,
    )
    
    export_path: StringProperty(
        name="Export Path",
        description="Path for exported files (// for relative)",
        default="//scans/",
        subtype='DIR_PATH',
    )
    
    export_filename: StringProperty(
        name="Filename",
        description="Base filename for exports",
        default="scan_001",
    )
    
    include_labels: BoolProperty(
        name="Include Labels",
        description="Include object category labels in export",
        default=True,
    )
    
    include_normals: BoolProperty(
        name="Include Normals",
        description="Include surface normals in export",
        default=True,
    )
    
    include_intensity: BoolProperty(
        name="Include Intensity",
        description="Include intensity values in export",
        default=True,
    )
    
    export_single_frames: BoolProperty(
        name="Single Frame Files",
        description="Export each frame as separate file",
        default=True,
    )
    
    # Weather Simulation
    enable_weather: BoolProperty(
        name="Enable Weather",
        description="Simulate weather effects",
        default=False,
    )
    
    rain_rate: FloatProperty(
        name="Rain Rate (mm/h)",
        description="Rainfall rate in mm per hour",
        default=0.0,
        min=0.0,
        max=100.0,
    )
    
    fog_density: FloatProperty(
        name="Fog Density",
        description="Fog density (0-1)",
        default=0.0,
        min=0.0,
        max=1.0,
    )
    
    # Debug Settings
    debug_output: BoolProperty(
        name="Debug Output",
        description="Print debug information to console",
        default=False,
    )
    
    debug_rays: BoolProperty(
        name="Show Debug Rays",
        description="Visualize ray directions in viewport",
        default=False,
    )

    # LLM Prompt Parsing
    prompt_text: StringProperty(
        name="Prompt",
        description="Describe the scene and scan parameters in natural language",
        default="",
        options={'MULTILINE'},
    )

    last_llm_status: StringProperty(
        name="LLM Status",
        description="Last LLM prompt parsing status",
        default="",
    )


def apply_preset(settings, context):
    """Apply preset sensor configurations"""
    preset = settings.sensor_preset
    
    presets = {
        'VELODYNE_VLP16': {
            'fov_h': 360.0,
            'fov_v': 30.0,
            'resolution_h': 0.2,
            'resolution_v': 2.0,
            'range_max': 100.0,
        },
        'VELODYNE_HDL32': {
            'fov_h': 360.0,
            'fov_v': 41.33,
            'resolution_h': 0.16,
            'resolution_v': 1.33,
            'range_max': 100.0,
        },
        'VELODYNE_HDL64': {
            'fov_h': 360.0,
            'fov_v': 26.8,
            'resolution_h': 0.08,
            'resolution_v': 0.4,
            'range_max': 120.0,
        },
        'OUSTER_OS1_32': {
            'fov_h': 360.0,
            'fov_v': 45.0,
            'resolution_h': 0.35,
            'resolution_v': 1.4,
            'range_max': 120.0,
        },
        'OUSTER_OS1_64': {
            'fov_h': 360.0,
            'fov_v': 45.0,
            'resolution_h': 0.35,
            'resolution_v': 0.7,
            'range_max': 120.0,
        },
        'LIVOX_MID40': {
            'fov_h': 38.4,
            'fov_v': 38.4,
            'resolution_h': 0.05,
            'resolution_v': 0.05,
            'range_max': 260.0,
        },
        'GENERIC_32': {
            'fov_h': 360.0,
            'fov_v': 40.0,
            'resolution_h': 0.2,
            'resolution_v': 1.25,
            'range_max': 100.0,
        },
        'GENERIC_64': {
            'fov_h': 360.0,
            'fov_v': 26.8,
            'resolution_h': 0.1,
            'resolution_v': 0.42,
            'range_max': 120.0,
        },
    }
    
    if preset in presets:
        for key, value in presets[preset].items():
            setattr(settings, key, value)


class LiDARSceneSettings(PropertyGroup):
    """Settings for scene object creation"""
    
    object_type: EnumProperty(
        name="Object Type",
        description="Type of object to create",
        items=[
            ('CUBE', 'Cube', 'Create a cube'),
            ('SPHERE', 'Sphere', 'Create a sphere'),
            ('CYLINDER', 'Cylinder', 'Create a cylinder'),
            ('PLANE', 'Plane', 'Create a plane'),
            ('IMPORT_GLB', 'Import GLB', 'Import a GLB/GLTF file'),
        ],
        default='CUBE',
    )
    
    asset_path: StringProperty(
        name="Asset Path",
        description="Path to GLB file for import",
        default="",
        subtype='FILE_PATH',
    )
    
    location: FloatVectorProperty(
        name="Location",
        description="Object location",
        default=(0.0, 0.0, 0.0),
        subtype='XYZ',
    )
    
    rotation_deg: FloatVectorProperty(
        name="Rotation",
        description="Object rotation in degrees",
        default=(0.0, 0.0, 0.0),
        subtype='EULER',
    )
    
    scale: FloatVectorProperty(
        name="Scale",
        description="Object scale",
        default=(1.0, 1.0, 1.0),
        subtype='XYZ',
    )
    
    category_id: StringProperty(
        name="Category ID",
        description="Category label for this object",
        default="",
    )


# Registration
classes = [
    LiDARScannerSettings,
    LiDARSceneSettings,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.lidar_scanner = PointerProperty(type=LiDARScannerSettings)
    bpy.types.Scene.lidar_scene = PointerProperty(type=LiDARSceneSettings)


def unregister():
    del bpy.types.Scene.lidar_scene
    del bpy.types.Scene.lidar_scanner
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
