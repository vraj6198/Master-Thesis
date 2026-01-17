# LiDAR Sensor Presets
# Contains predefined configurations for popular LiDAR sensors

SENSOR_PRESETS = {
    # Velodyne Family
    'VELODYNE_VLP16': {
        'name': 'Velodyne VLP-16 Puck',
        'manufacturer': 'Velodyne',
        'channels': 16,
        'fov_h': 360.0,
        'fov_v': 30.0,  # ±15°
        'resolution_h': 0.1,  # 0.1° - 0.4°
        'resolution_v': 2.0,  # 16 channels over 30°
        'range_min': 0.5,
        'range_max': 100.0,
        'points_per_second': 300000,
        'rotations_per_second': 5,  # 5-20 Hz
        'range_accuracy': 0.03,  # ±3cm
    },
    'VELODYNE_HDL32': {
        'name': 'Velodyne HDL-32E',
        'manufacturer': 'Velodyne',
        'channels': 32,
        'fov_h': 360.0,
        'fov_v': 41.33,  # +10.67° to -30.67°
        'resolution_h': 0.16,
        'resolution_v': 1.33,  # 32 channels
        'range_min': 1.0,
        'range_max': 100.0,
        'points_per_second': 700000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
    'VELODYNE_HDL64': {
        'name': 'Velodyne HDL-64E',
        'manufacturer': 'Velodyne',
        'channels': 64,
        'fov_h': 360.0,
        'fov_v': 26.8,  # +2° to -24.8°
        'resolution_h': 0.08,
        'resolution_v': 0.4,
        'range_min': 0.9,
        'range_max': 120.0,
        'points_per_second': 1300000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
    'VELODYNE_VLS128': {
        'name': 'Velodyne VLS-128',
        'manufacturer': 'Velodyne',
        'channels': 128,
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.11,
        'resolution_v': 0.31,
        'range_min': 0.5,
        'range_max': 300.0,
        'points_per_second': 2400000,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    
    # Ouster Family
    'OUSTER_OS0_32': {
        'name': 'Ouster OS0-32',
        'manufacturer': 'Ouster',
        'channels': 32,
        'fov_h': 360.0,
        'fov_v': 90.0,  # Ultra-wide FOV
        'resolution_h': 0.35,
        'resolution_v': 2.8,
        'range_min': 0.3,
        'range_max': 50.0,
        'points_per_second': 655360,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'OUSTER_OS1_32': {
        'name': 'Ouster OS1-32',
        'manufacturer': 'Ouster',
        'channels': 32,
        'fov_h': 360.0,
        'fov_v': 45.0,
        'resolution_h': 0.35,
        'resolution_v': 1.4,
        'range_min': 0.3,
        'range_max': 120.0,
        'points_per_second': 655360,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'OUSTER_OS1_64': {
        'name': 'Ouster OS1-64',
        'manufacturer': 'Ouster',
        'channels': 64,
        'fov_h': 360.0,
        'fov_v': 45.0,
        'resolution_h': 0.35,
        'resolution_v': 0.7,
        'range_min': 0.3,
        'range_max': 120.0,
        'points_per_second': 1310720,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'OUSTER_OS1_128': {
        'name': 'Ouster OS1-128',
        'manufacturer': 'Ouster',
        'channels': 128,
        'fov_h': 360.0,
        'fov_v': 45.0,
        'resolution_h': 0.35,
        'resolution_v': 0.35,
        'range_min': 0.3,
        'range_max': 120.0,
        'points_per_second': 2621440,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'OUSTER_OS2_128': {
        'name': 'Ouster OS2-128',
        'manufacturer': 'Ouster',
        'channels': 128,
        'fov_h': 360.0,
        'fov_v': 22.5,
        'resolution_h': 0.18,
        'resolution_v': 0.18,
        'range_min': 0.3,
        'range_max': 240.0,
        'points_per_second': 2621440,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    
    # Livox Family (Non-repetitive scanning)
    'LIVOX_MID40': {
        'name': 'Livox Mid-40',
        'manufacturer': 'Livox',
        'channels': 1,  # Non-repetitive pattern
        'fov_h': 38.4,
        'fov_v': 38.4,
        'resolution_h': 0.05,
        'resolution_v': 0.05,
        'range_min': 0.1,
        'range_max': 260.0,
        'points_per_second': 100000,
        'rotations_per_second': 0,  # Non-rotating
        'range_accuracy': 0.02,
    },
    'LIVOX_MID70': {
        'name': 'Livox Mid-70',
        'manufacturer': 'Livox',
        'channels': 1,
        'fov_h': 70.4,
        'fov_v': 77.2,
        'resolution_h': 0.05,
        'resolution_v': 0.05,
        'range_min': 0.1,
        'range_max': 260.0,
        'points_per_second': 100000,
        'rotations_per_second': 0,
        'range_accuracy': 0.02,
    },
    'LIVOX_HORIZON': {
        'name': 'Livox Horizon',
        'manufacturer': 'Livox',
        'channels': 6,
        'fov_h': 81.7,
        'fov_v': 25.1,
        'resolution_h': 0.03,
        'resolution_v': 0.03,
        'range_min': 0.1,
        'range_max': 260.0,
        'points_per_second': 240000,
        'rotations_per_second': 0,
        'range_accuracy': 0.02,
    },
    'LIVOX_AVIA': {
        'name': 'Livox Avia',
        'manufacturer': 'Livox',
        'channels': 6,
        'fov_h': 70.4,
        'fov_v': 77.2,
        'resolution_h': 0.05,
        'resolution_v': 0.05,
        'range_min': 0.1,
        'range_max': 450.0,
        'points_per_second': 240000,
        'rotations_per_second': 0,
        'range_accuracy': 0.02,
    },
    
    # Hesai Family
    'HESAI_PANDAR64': {
        'name': 'Hesai Pandar64',
        'manufacturer': 'Hesai',
        'channels': 64,
        'fov_h': 360.0,
        'fov_v': 40.0,  # +15° to -25°
        'resolution_h': 0.2,
        'resolution_v': 0.63,
        'range_min': 0.3,
        'range_max': 200.0,
        'points_per_second': 1152000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
    'HESAI_PANDAR128': {
        'name': 'Hesai Pandar128',
        'manufacturer': 'Hesai',
        'channels': 128,
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.1,
        'resolution_v': 0.31,
        'range_min': 0.3,
        'range_max': 200.0,
        'points_per_second': 2304000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
    'HESAI_XT32': {
        'name': 'Hesai XT32',
        'manufacturer': 'Hesai',
        'channels': 32,
        'fov_h': 360.0,
        'fov_v': 31.0,
        'resolution_h': 0.18,
        'resolution_v': 1.0,
        'range_min': 0.5,
        'range_max': 120.0,
        'points_per_second': 640000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
    'HESAI_AT128': {
        'name': 'Hesai AT128',
        'manufacturer': 'Hesai',
        'channels': 128,
        'fov_h': 120.0,
        'fov_v': 25.4,
        'resolution_h': 0.1,
        'resolution_v': 0.2,
        'range_min': 0.5,
        'range_max': 200.0,
        'points_per_second': 1536000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
    
    # RoboSense Family
    'ROBOSENSE_RS16': {
        'name': 'RoboSense RS-LiDAR-16',
        'manufacturer': 'RoboSense',
        'channels': 16,
        'fov_h': 360.0,
        'fov_v': 30.0,
        'resolution_h': 0.2,
        'resolution_v': 2.0,
        'range_min': 0.2,
        'range_max': 150.0,
        'points_per_second': 320000,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'ROBOSENSE_RS32': {
        'name': 'RoboSense RS-LiDAR-32',
        'manufacturer': 'RoboSense',
        'channels': 32,
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.2,
        'resolution_v': 1.25,
        'range_min': 0.2,
        'range_max': 200.0,
        'points_per_second': 640000,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'ROBOSENSE_RS128': {
        'name': 'RoboSense RS-Ruby',
        'manufacturer': 'RoboSense',
        'channels': 128,
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.1,
        'resolution_v': 0.31,
        'range_min': 0.2,
        'range_max': 250.0,
        'points_per_second': 2304000,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    
    # SICK Family (Industrial)
    'SICK_LMS511': {
        'name': 'SICK LMS511',
        'manufacturer': 'SICK',
        'channels': 1,
        'fov_h': 190.0,
        'fov_v': 0.0,  # 2D scanner
        'resolution_h': 0.167,
        'resolution_v': 0.0,
        'range_min': 0.05,
        'range_max': 80.0,
        'points_per_second': 71000,
        'rotations_per_second': 25,
        'range_accuracy': 0.025,
    },
    'SICK_MRS6000': {
        'name': 'SICK MRS6000',
        'manufacturer': 'SICK',
        'channels': 24,
        'fov_h': 120.0,
        'fov_v': 15.0,
        'resolution_h': 0.13,
        'resolution_v': 0.63,
        'range_min': 0.5,
        'range_max': 200.0,
        'points_per_second': 660000,
        'rotations_per_second': 30,
        'range_accuracy': 0.03,
    },
    
    # Generic Presets
    'GENERIC_16': {
        'name': 'Generic 16-Channel',
        'manufacturer': 'Generic',
        'channels': 16,
        'fov_h': 360.0,
        'fov_v': 30.0,
        'resolution_h': 0.2,
        'resolution_v': 2.0,
        'range_min': 0.5,
        'range_max': 100.0,
        'points_per_second': 300000,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'GENERIC_32': {
        'name': 'Generic 32-Channel',
        'manufacturer': 'Generic',
        'channels': 32,
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.2,
        'resolution_v': 1.25,
        'range_min': 0.5,
        'range_max': 100.0,
        'points_per_second': 600000,
        'rotations_per_second': 10,
        'range_accuracy': 0.03,
    },
    'GENERIC_64': {
        'name': 'Generic 64-Channel',
        'manufacturer': 'Generic',
        'channels': 64,
        'fov_h': 360.0,
        'fov_v': 26.8,
        'resolution_h': 0.1,
        'resolution_v': 0.42,
        'range_min': 0.5,
        'range_max': 120.0,
        'points_per_second': 1200000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
    'GENERIC_128': {
        'name': 'Generic 128-Channel',
        'manufacturer': 'Generic',
        'channels': 128,
        'fov_h': 360.0,
        'fov_v': 40.0,
        'resolution_h': 0.1,
        'resolution_v': 0.31,
        'range_min': 0.5,
        'range_max': 200.0,
        'points_per_second': 2400000,
        'rotations_per_second': 10,
        'range_accuracy': 0.02,
    },
}


def get_preset(preset_name: str) -> dict:
    """Get a sensor preset by name"""
    return SENSOR_PRESETS.get(preset_name, SENSOR_PRESETS['GENERIC_32'])


def get_preset_names() -> list:
    """Get list of all preset names"""
    return list(SENSOR_PRESETS.keys())


def get_preset_by_manufacturer(manufacturer: str) -> dict:
    """Get all presets from a specific manufacturer"""
    return {
        name: preset for name, preset in SENSOR_PRESETS.items()
        if preset['manufacturer'].lower() == manufacturer.lower()
    }


def apply_preset_to_settings(settings, preset_name: str) -> bool:
    """Apply a preset to scanner settings"""
    if preset_name not in SENSOR_PRESETS:
        return False
    
    preset = SENSOR_PRESETS[preset_name]
    
    settings.fov_h = preset['fov_h']
    settings.fov_v = preset['fov_v']
    settings.resolution_h = preset['resolution_h']
    settings.resolution_v = preset['resolution_v']
    settings.range_min = preset['range_min']
    settings.range_max = preset['range_max']
    settings.rotations_per_second = preset['rotations_per_second']
    settings.range_sigma_m = preset['range_accuracy']
    
    return True
