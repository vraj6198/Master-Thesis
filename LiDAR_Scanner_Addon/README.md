# LiDAR Scanner Simulator for Blender

A comprehensive Blender add-on for simulating LiDAR (Light Detection and Ranging) sensor scanning. This add-on enables realistic point cloud generation with customizable sensor parameters, noise models, and multiple export formats.

Inspired by [blainder-range-scanner](https://github.com/ln-12/blainder-range-scanner).

## Features

### Scanner Simulation
- **Customizable Field of View (FOV)**: Configure horizontal (1-360°) and vertical (1-90°) scanning angles
- **Adjustable Resolution**: Set angular resolution for both horizontal and vertical axes (0.01-5°)
- **Range Configuration**: Define minimum and maximum detection ranges (0.1-500m)
- **Sensor Presets**: Pre-configured settings for popular LiDAR sensors:
  - Velodyne (VLP-16, HDL-32E, HDL-64E, VLS-128)
  - Ouster (OS0, OS1, OS2 series)
  - Livox (Mid-40, Mid-70, Horizon, Avia)
  - Hesai (Pandar64, Pandar128, XT32, AT128)
  - RoboSense (RS-16, RS-32, Ruby)
  - SICK (LMS511, MRS6000)

### Noise Simulation
- **Range Noise**: Gaussian, Uniform, or Rayleigh distribution
- **Angular Noise**: Configurable angular uncertainty
- **Point Dropout**: Random point removal to simulate sensor limitations
- **Weather Effects**: Rain and fog attenuation simulation

### Intensity Calculation
- **Material-based Reflectivity**: Uses Blender material properties
- **Distance Falloff**: Linear, Quadratic, or None
- **Angle of Incidence**: Lambert's law for realistic intensity

### Export Formats
- **PLY** (Polygon File Format) - ASCII and Binary
- **CSV** (Comma-Separated Values)
- **PCD** (Point Cloud Data)
- **LAS** (LiDAR Data Exchange Format - requires laspy)

### Additional Features
- **Animation Support**: Scan across multiple frames
- **Object Classification**: Label points by hit object
- **JSON Configuration**: Import/Export scanner settings
- **Visualization**: Add point clouds directly to scene

## Installation

1. Download the `LiDAR_Scanner_Addon` folder
2. Zip the entire folder
3. In Blender: `Edit` → `Preferences` → `Add-ons` → `Install`
4. Select the zip file and enable the add-on
5. Access via `3D View` → `Sidebar` → `LiDAR` tab

## Usage

### Basic Scan

1. Open the LiDAR panel in the 3D View sidebar
2. Create or select a scanner object (Empty or Camera)
3. Configure scanner parameters:
   - Field of View
   - Resolution
   - Range
4. Click "Run LiDAR Scan"

### Using Presets

1. Expand "Sensor Presets" panel
2. Select a sensor from the dropdown
3. Click "Apply Preset"

### JSON Configuration

Export current settings:
```json
{
  "scan": {
    "sensor_preset": "AUTO",
    "origin": [0, 0, 1.8],
    "rotation_deg": [0, 0, 0],
    "fov_deg": {"h": 360, "v": 30},
    "resolution_deg": {"h": 0.2, "v": 1.0},
    "range_m": 80,
    "noise": {
      "range_sigma_m": 0.1,
      "dropout_prob": 0.02
    },
    "output": {
      "formats": ["ply", "csv"],
      "path": "//scans/test_01/",
      "include_labels": true
    }
  }
}
```

### Animation Scanning

1. Enable "Animation" panel
2. Set start/end frames
3. Configure frame step
4. Click "Scan Animation"

## API Reference

### Scanner Settings

| Property | Type | Range | Description |
|----------|------|-------|-------------|
| `fov_h` | float | 1-360 | Horizontal FOV (degrees) |
| `fov_v` | float | 1-90 | Vertical FOV (degrees) |
| `resolution_h` | float | 0.01-5 | Horizontal resolution (degrees) |
| `resolution_v` | float | 0.01-5 | Vertical resolution (degrees) |
| `range_min` | float | 0-500 | Minimum range (meters) |
| `range_max` | float | 0.1-500 | Maximum range (meters) |
| `range_sigma_m` | float | 0-0.5 | Range noise sigma (meters) |
| `dropout_prob` | float | 0-0.3 | Point dropout probability |

### Operators

- `lidar.scan` - Run single-frame scan
- `lidar.scan_animation` - Scan across animation
- `lidar.create_scanner_object` - Create scanner empty
- `lidar.export_json` - Export configuration
- `lidar.import_json` - Import configuration
- `lidar.clear_point_clouds` - Remove scan results

## Example: Complete Scan Setup

```python
import bpy

# Get settings
settings = bpy.context.scene.lidar_scanner

# Configure scanner
settings.origin = (0, 0, 1.8)
settings.rotation_deg = (0, 0, 0)
settings.fov_h = 360
settings.fov_v = 30
settings.resolution_h = 0.2
settings.resolution_v = 1.0
settings.range_max = 80

# Configure noise
settings.enable_noise = True
settings.range_sigma_m = 0.1
settings.dropout_prob = 0.02

# Configure export
settings.export_ply = True
settings.export_csv = True
settings.export_path = "//scans/test_01/"
settings.include_labels = True

# Run scan
bpy.ops.lidar.scan()
```

## Dependencies

- **Blender 4.0+**
- **Optional**: `laspy` for LAS export

## Performance Tips

1. **Reduce Resolution**: Lower resolution = fewer rays = faster scans
2. **Limit Range**: Smaller range reduces ray traversal time
3. **Disable Unused Features**: Turn off intensity, normals if not needed
4. **Use Binary PLY**: Smaller files, faster export

## Troubleshooting

### No Points Detected
- Ensure scene has visible mesh objects
- Check range settings (min/max)
- Verify scanner is not inside an object

### Slow Performance
- Reduce FOV or increase resolution values
- Disable debug options
- Use simpler scene geometry

### Export Issues
- Check export path exists
- Verify write permissions
- For LAS export, install laspy: `pip install laspy`

## License

GPL-3.0 License

## Credits

- Inspired by [blainder-range-scanner](https://github.com/ln-12/blainder-range-scanner) by Lorenzo Neumann
- Reference paper: Reitmann, S.; Neumann, L.; Jung, B. "BLAINDER—A Blender AI Add-On for Generation of Semantically Labeled Depth-Sensing Data". Sensors 2021, 21, 2144
