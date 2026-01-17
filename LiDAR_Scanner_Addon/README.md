# LiDAR Scanner Addon for Blender

A comprehensive LiDAR scanner simulation add-on for Blender, inspired by the [blainder-range-scanner](https://github.com/ln-12/blainder-range-scanner) project.

## Features

- **Realistic LiDAR Simulation**: Ray-casting based scanning with configurable parameters
- **Sensor Presets**: Pre-configured settings for Velodyne, Ouster, Livox, Hesai, RoboSense, and SICK sensors
- **LLM Prompt Parsing**: Natural language configuration using OpenAI-compatible LLMs (e.g., Ollama)
- **Noise Simulation**: Gaussian, uniform, and Rayleigh noise models
- **Multiple Export Formats**: PLY, CSV, PCD, and LAS
- **Animation Support**: Scan across multiple frames
- **Weather Effects**: Rain and fog simulation
- **Intensity Calculation**: Realistic intensity based on distance, angle, and materials

## Installation

1. Download or create a ZIP file of the `LiDAR_Scanner_Addon` folder
2. In Blender: Edit → Preferences → Add-ons → Install
3. Select the ZIP file and click "Install Add-on"
4. Enable the add-on by checking the checkbox

## Usage

1. Open the 3D Viewport sidebar (press N)
2. Navigate to the "LiDAR" tab
3. Configure scanner settings or use a preset
4. Click "Run LiDAR Scan" to perform a scan

### LLM Prompt Parsing

You can describe scan parameters in natural language:

1. Go to Preferences → Add-ons → LiDAR Scanner Simulator
2. Configure your LLM endpoint (default: Ollama at localhost:11434)
3. In the LiDAR panel, expand "LLM Prompt"
4. Type your description, e.g., "Scan with Velodyne VLP-16, 50m range, high noise"
5. Click "Apply Prompt"

## Parameters

### Scanner Settings
- **Origin**: Scanner position (X, Y, Z)
- **Rotation**: Scanner rotation in degrees
- **Horizontal FOV**: 1-360 degrees
- **Vertical FOV**: 1-90 degrees
- **Horizontal Resolution**: 0.01-5 degrees
- **Vertical Resolution**: 0.01-5 degrees
- **Range**: 0.1-500 meters

### Noise Settings
- **Range Sigma**: Standard deviation of range noise (0-0.5m)
- **Angular Noise**: Standard deviation of angular noise (0-1°)
- **Dropout Probability**: Random point dropout rate (0-0.3)

### Export Formats
- **PLY**: Standard point cloud format
- **CSV**: Comma-separated values with all attributes
- **PCD**: Point Cloud Data format
- **LAS**: LASer format (requires laspy package)

## Requirements

- Blender 4.0 or newer
- Optional: `laspy` package for LAS export
- Optional: Ollama or other OpenAI-compatible LLM for prompt parsing

## License

MIT License
