# LiDAR Scanner Sensor Presets
"""
Predefined sensor configurations for common LiDAR sensors.
These presets define the default FOV, resolution, and range for each sensor model.
"""

SENSOR_PRESETS = {
    # Velodyne Sensors
    'VELODYNE_VLP16': {
        'name': 'Velodyne VLP-16 Puck',
        'fov_h': 360.0,
        'fov_v': 30.0,
        'resolution_h': 0.2,
        'resolution_v': 2.0,
        'range_max': 100.0,
        'channels': 16,
        'points_per_second': 300000,
        'description': '16-channel low-cost spinning LiDAR',
    },
    'VELODYNE_VLP16_HI_RES': {
        'name': 'Velodyne VLP-16 Hi-Res',
        'fov_h': 360.0,
        'fov_v': 20.0,
        'resolution_h': 0.1,
        'resolution_v': 1.33,
        'range_max': 100.0,
        'channels': 16,
        'points_per_second': 600000,
        'description': '16-channel high-resolution spinning LiDAR',
    },
    'VELODYNE_HDL32': {
        'name': 'Velodyne HDL-32E',
        'fov_h': 360.0,
        'fov_v': 41.33,
        'resolution_h': 0.16,
        'resolution_v': 1.33,
        'range_max': 100.0,
        'channels': 32,
        'points_per_second': 700000,
        'description': '32-channel spinning LiDAR',
    },
    'VELODYNE_HDL64': {
        'name': 'Velodyne HDL-64E',
        'fov_h': 360.0,
        'fov_v': 26.8,
        'resolution_h': 0.08,
        'resolution_v': 0.42,
        'range_max': 120.0,
        'channels': 64,
        'points_per_second': 1300000,
        'description': '64-channel high-end spinning LiDAR',
    },
    'VELODYNE_VLS128': {
        'name': 'Velodyne VLS-128 (Alpha Prime)',
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.1,
        'resolution_v': 0.31,
        'range_max': 300.0,
        'channels': 128,
        'points_per_second': 2400000,
        'description': '128-channel premium LiDAR',
    },
    
    # Ouster Sensors
    'OUSTER_OS0_32': {
        'name': 'Ouster OS0-32',
        'fov_h': 360.0,
        'fov_v': 90.0,
        'resolution_h': 0.35,
        'resolution_v': 2.8,
        'range_max': 50.0,
        'channels': 32,
        'points_per_second': 655360,
        'description': 'Wide FOV short-range LiDAR',
    },
    'OUSTER_OS1_32': {
        'name': 'Ouster OS1-32',
        'fov_h': 360.0,
        'fov_v': 45.0,
        'resolution_h': 0.35,
        'resolution_v': 1.4,
        'range_max': 120.0,
        'channels': 32,
        'points_per_second': 655360,
        'description': '32-channel mid-range LiDAR',
    },
    'OUSTER_OS1_64': {
        'name': 'Ouster OS1-64',
        'fov_h': 360.0,
        'fov_v': 45.0,
        'resolution_h': 0.35,
        'resolution_v': 0.7,
        'range_max': 120.0,
        'channels': 64,
        'points_per_second': 1310720,
        'description': '64-channel mid-range LiDAR',
    },
    'OUSTER_OS1_128': {
        'name': 'Ouster OS1-128',
        'fov_h': 360.0,
        'fov_v': 45.0,
        'resolution_h': 0.35,
        'resolution_v': 0.35,
        'range_max': 120.0,
        'channels': 128,
        'points_per_second': 2621440,
        'description': '128-channel mid-range LiDAR',
    },
    'OUSTER_OS2_64': {
        'name': 'Ouster OS2-64',
        'fov_h': 360.0,
        'fov_v': 22.5,
        'resolution_h': 0.18,
        'resolution_v': 0.35,
        'range_max': 240.0,
        'channels': 64,
        'points_per_second': 1310720,
        'description': '64-channel long-range LiDAR',
    },
    
    # Livox Sensors (non-repetitive scanning)
    'LIVOX_MID40': {
        'name': 'Livox Mid-40',
        'fov_h': 38.4,
        'fov_v': 38.4,
        'resolution_h': 0.05,
        'resolution_v': 0.05,
        'range_max': 260.0,
        'channels': 1,
        'points_per_second': 100000,
        'description': 'Non-repetitive solid-state LiDAR',
    },
    'LIVOX_MID70': {
        'name': 'Livox Mid-70',
        'fov_h': 70.4,
        'fov_v': 77.2,
        'resolution_h': 0.05,
        'resolution_v': 0.05,
        'range_max': 260.0,
        'channels': 1,
        'points_per_second': 100000,
        'description': 'Wide-angle solid-state LiDAR',
    },
    'LIVOX_HORIZON': {
        'name': 'Livox Horizon',
        'fov_h': 81.7,
        'fov_v': 25.1,
        'resolution_h': 0.03,
        'resolution_v': 0.03,
        'range_max': 260.0,
        'channels': 6,
        'points_per_second': 240000,
        'description': 'Automotive-grade solid-state LiDAR',
    },
    'LIVOX_AVIA': {
        'name': 'Livox Avia',
        'fov_h': 70.4,
        'fov_v': 77.2,
        'resolution_h': 0.05,
        'resolution_v': 0.05,
        'range_max': 450.0,
        'channels': 1,
        'points_per_second': 240000,
        'description': 'Long-range solid-state LiDAR',
    },
    
    # Hesai Sensors
    'HESAI_PANDAR40P': {
        'name': 'Hesai Pandar40P',
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.2,
        'resolution_v': 1.0,
        'range_max': 200.0,
        'channels': 40,
        'points_per_second': 720000,
        'description': '40-channel spinning LiDAR',
    },
    'HESAI_PANDAR64': {
        'name': 'Hesai Pandar64',
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.2,
        'resolution_v': 0.625,
        'range_max': 200.0,
        'channels': 64,
        'points_per_second': 1152000,
        'description': '64-channel spinning LiDAR',
    },
    'HESAI_PANDAR128': {
        'name': 'Hesai Pandar128',
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.1,
        'resolution_v': 0.31,
        'range_max': 200.0,
        'channels': 128,
        'points_per_second': 2304000,
        'description': '128-channel spinning LiDAR',
    },
    'HESAI_AT128': {
        'name': 'Hesai AT128',
        'fov_h': 120.0,
        'fov_v': 25.4,
        'resolution_h': 0.1,
        'resolution_v': 0.2,
        'range_max': 200.0,
        'channels': 128,
        'points_per_second': 1536000,
        'description': 'Solid-state automotive LiDAR',
    },
    
    # RoboSense Sensors
    'ROBOSENSE_RS16': {
        'name': 'RoboSense RS-16',
        'fov_h': 360.0,
        'fov_v': 30.0,
        'resolution_h': 0.2,
        'resolution_v': 2.0,
        'range_max': 150.0,
        'channels': 16,
        'points_per_second': 320000,
        'description': '16-channel spinning LiDAR',
    },
    'ROBOSENSE_RS32': {
        'name': 'RoboSense RS-32',
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.2,
        'resolution_v': 1.25,
        'range_max': 200.0,
        'channels': 32,
        'points_per_second': 640000,
        'description': '32-channel spinning LiDAR',
    },
    'ROBOSENSE_RS128': {
        'name': 'RoboSense RS-128',
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.1,
        'resolution_v': 0.31,
        'range_max': 250.0,
        'channels': 128,
        'points_per_second': 2304000,
        'description': '128-channel high-end LiDAR',
    },
    
    # SICK Sensors
    'SICK_LMS511': {
        'name': 'SICK LMS511',
        'fov_h': 190.0,
        'fov_v': 0.0,
        'resolution_h': 0.167,
        'resolution_v': 0.0,
        'range_max': 80.0,
        'channels': 1,
        'points_per_second': 29000,
        'description': '2D safety laser scanner',
    },
    
    # Generic Configurations
    'GENERIC_16': {
        'name': 'Generic 16-Channel',
        'fov_h': 360.0,
        'fov_v': 30.0,
        'resolution_h': 0.2,
        'resolution_v': 2.0,
        'range_max': 100.0,
        'channels': 16,
        'points_per_second': 300000,
        'description': 'Generic 16-channel configuration',
    },
    'GENERIC_32': {
        'name': 'Generic 32-Channel',
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.2,
        'resolution_v': 1.25,
        'range_max': 100.0,
        'channels': 32,
        'points_per_second': 600000,
        'description': 'Generic 32-channel configuration',
    },
    'GENERIC_64': {
        'name': 'Generic 64-Channel',
        'fov_h': 360.0,
        'fov_v': 26.8,
        'resolution_h': 0.1,
        'resolution_v': 0.42,
        'range_max': 120.0,
        'channels': 64,
        'points_per_second': 1200000,
        'description': 'Generic 64-channel configuration',
    },
}


def get_preset_names():
    """Get list of preset names for enum generation"""
    return [(key, data['name'], data['description']) 
            for key, data in SENSOR_PRESETS.items()]


def apply_preset_to_settings(settings, preset_key):
    """Apply a preset configuration to scanner settings"""
    if preset_key not in SENSOR_PRESETS:
        return False
    
    preset = SENSOR_PRESETS[preset_key]
    
    settings.fov_h = preset['fov_h']
    settings.fov_v = preset['fov_v']
    settings.resolution_h = preset['resolution_h']
    settings.resolution_v = preset['resolution_v']
    settings.range_max = preset['range_max']
    
    return True


def estimate_scan_points(preset_key):
    """Estimate the number of points for a given preset"""
    if preset_key not in SENSOR_PRESETS:
        return 0
    
    preset = SENSOR_PRESETS[preset_key]
    h_points = int(preset['fov_h'] / preset['resolution_h']) + 1
    v_points = int(preset['fov_v'] / preset['resolution_v']) + 1 if preset['fov_v'] > 0 else 1
    
    return h_points * v_points
