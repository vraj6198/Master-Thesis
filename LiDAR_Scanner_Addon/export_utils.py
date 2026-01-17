# LiDAR Scanner Export Utilities
import bpy
import os
import csv
import struct
from typing import List, Optional
from .scanner_core import ScanPoint


def ensure_directory(path: str) -> str:
    """Ensure the export directory exists"""
    # Convert Blender relative path
    if path.startswith("//"):
        path = bpy.path.abspath(path)
    
    os.makedirs(path, exist_ok=True)
    return path


def get_export_filepath(settings, extension: str, frame: Optional[int] = None) -> str:
    """Generate the full export file path"""
    base_path = ensure_directory(settings.export_path)
    filename = settings.export_filename
    
    if frame is not None:
        filename = f"{filename}_{frame:04d}"
    
    return os.path.join(base_path, f"{filename}.{extension}")


def export_ply(points: List[ScanPoint], filepath: str, 
               include_normals: bool = True, 
               include_intensity: bool = True,
               include_labels: bool = True) -> bool:
    """Export point cloud to PLY format"""
    try:
        with open(filepath, 'w') as f:
            # Write header
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {len(points)}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            
            if include_normals:
                f.write("property float nx\n")
                f.write("property float ny\n")
                f.write("property float nz\n")
            
            if include_intensity:
                f.write("property float intensity\n")
                f.write("property float distance\n")
            
            if include_labels:
                f.write("property uchar red\n")
                f.write("property uchar green\n")
                f.write("property uchar blue\n")
            
            f.write("end_header\n")
            
            # Write vertex data
            for point in points:
                line = f"{point.position.x:.6f} {point.position.y:.6f} {point.position.z:.6f}"
                
                if include_normals:
                    line += f" {point.normal.x:.6f} {point.normal.y:.6f} {point.normal.z:.6f}"
                
                if include_intensity:
                    line += f" {point.intensity:.6f} {point.distance:.6f}"
                
                if include_labels:
                    # Convert intensity to grayscale color
                    gray = int(point.intensity * 255)
                    line += f" {gray} {gray} {gray}"
                
                f.write(line + "\n")
        
        return True
    except Exception as e:
        print(f"Error exporting PLY: {e}")
        return False


def export_ply_binary(points: List[ScanPoint], filepath: str,
                      include_normals: bool = True,
                      include_intensity: bool = True) -> bool:
    """Export point cloud to binary PLY format (more compact)"""
    try:
        with open(filepath, 'wb') as f:
            # Write header
            header = "ply\n"
            header += "format binary_little_endian 1.0\n"
            header += f"element vertex {len(points)}\n"
            header += "property float x\n"
            header += "property float y\n"
            header += "property float z\n"
            
            if include_normals:
                header += "property float nx\n"
                header += "property float ny\n"
                header += "property float nz\n"
            
            if include_intensity:
                header += "property float intensity\n"
            
            header += "end_header\n"
            f.write(header.encode('ascii'))
            
            # Write binary vertex data
            for point in points:
                data = struct.pack('<fff', point.position.x, point.position.y, point.position.z)
                
                if include_normals:
                    data += struct.pack('<fff', point.normal.x, point.normal.y, point.normal.z)
                
                if include_intensity:
                    data += struct.pack('<f', point.intensity)
                
                f.write(data)
        
        return True
    except Exception as e:
        print(f"Error exporting binary PLY: {e}")
        return False


def export_csv(points: List[ScanPoint], filepath: str,
               include_normals: bool = True,
               include_intensity: bool = True,
               include_labels: bool = True) -> bool:
    """Export point cloud to CSV format"""
    try:
        with open(filepath, 'w', newline='') as f:
            # Define columns
            columns = ['x', 'y', 'z']
            
            if include_normals:
                columns.extend(['nx', 'ny', 'nz'])
            
            if include_intensity:
                columns.extend(['intensity', 'distance'])
            
            if include_labels:
                columns.extend(['object_name', 'category_id'])
            
            columns.extend(['angle_h', 'angle_v', 'return_number'])
            
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for point in points:
                row = {
                    'x': f"{point.position.x:.6f}",
                    'y': f"{point.position.y:.6f}",
                    'z': f"{point.position.z:.6f}",
                }
                
                if include_normals:
                    row['nx'] = f"{point.normal.x:.6f}"
                    row['ny'] = f"{point.normal.y:.6f}"
                    row['nz'] = f"{point.normal.z:.6f}"
                
                if include_intensity:
                    row['intensity'] = f"{point.intensity:.6f}"
                    row['distance'] = f"{point.distance:.6f}"
                
                if include_labels:
                    row['object_name'] = point.object_name
                    row['category_id'] = point.category_id
                
                row['angle_h'] = f"{point.angle_h:.4f}"
                row['angle_v'] = f"{point.angle_v:.4f}"
                row['return_number'] = point.return_number
                
                writer.writerow(row)
        
        return True
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return False


def export_pcd(points: List[ScanPoint], filepath: str,
               include_intensity: bool = True) -> bool:
    """Export point cloud to PCD (Point Cloud Data) format"""
    try:
        with open(filepath, 'w') as f:
            # Write PCD header
            f.write("# .PCD v0.7 - Point Cloud Data file format\n")
            f.write("VERSION 0.7\n")
            
            if include_intensity:
                f.write("FIELDS x y z intensity\n")
                f.write("SIZE 4 4 4 4\n")
                f.write("TYPE F F F F\n")
                f.write("COUNT 1 1 1 1\n")
            else:
                f.write("FIELDS x y z\n")
                f.write("SIZE 4 4 4\n")
                f.write("TYPE F F F\n")
                f.write("COUNT 1 1 1\n")
            
            f.write(f"WIDTH {len(points)}\n")
            f.write("HEIGHT 1\n")
            f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
            f.write(f"POINTS {len(points)}\n")
            f.write("DATA ascii\n")
            
            # Write point data
            for point in points:
                if include_intensity:
                    f.write(f"{point.position.x:.6f} {point.position.y:.6f} {point.position.z:.6f} {point.intensity:.6f}\n")
                else:
                    f.write(f"{point.position.x:.6f} {point.position.y:.6f} {point.position.z:.6f}\n")
        
        return True
    except Exception as e:
        print(f"Error exporting PCD: {e}")
        return False


def export_las(points: List[ScanPoint], filepath: str,
               include_intensity: bool = True) -> bool:
    """Export point cloud to LAS format (requires laspy)"""
    try:
        import laspy
        
        # Create LAS file
        header = laspy.LasHeader(point_format=3, version="1.4")
        
        las = laspy.LasData(header)
        
        # Set coordinates
        las.x = [p.position.x for p in points]
        las.y = [p.position.y for p in points]
        las.z = [p.position.z for p in points]
        
        if include_intensity:
            # Scale intensity to 16-bit range
            las.intensity = [int(p.intensity * 65535) for p in points]
        
        las.write(filepath)
        return True
        
    except ImportError:
        print("laspy not installed. Install with: pip install laspy")
        return False
    except Exception as e:
        print(f"Error exporting LAS: {e}")
        return False


def export_xyz(points: List[ScanPoint], filepath: str,
               include_intensity: bool = True) -> bool:
    """Export point cloud to simple XYZ format"""
    try:
        with open(filepath, 'w') as f:
            for point in points:
                if include_intensity:
                    f.write(f"{point.position.x:.6f} {point.position.y:.6f} {point.position.z:.6f} {point.intensity:.6f}\n")
                else:
                    f.write(f"{point.position.x:.6f} {point.position.y:.6f} {point.position.z:.6f}\n")
        return True
    except Exception as e:
        print(f"Error exporting XYZ: {e}")
        return False


def export_all_formats(points: List[ScanPoint], settings, frame: Optional[int] = None) -> dict:
    """Export to all enabled formats"""
    results = {}
    
    if settings.export_ply:
        filepath = get_export_filepath(settings, 'ply', frame)
        results['ply'] = export_ply(
            points, filepath,
            include_normals=settings.include_normals,
            include_intensity=settings.include_intensity,
            include_labels=settings.include_labels
        )
        if results['ply']:
            print(f"Exported PLY: {filepath}")
    
    if settings.export_csv:
        filepath = get_export_filepath(settings, 'csv', frame)
        results['csv'] = export_csv(
            points, filepath,
            include_normals=settings.include_normals,
            include_intensity=settings.include_intensity,
            include_labels=settings.include_labels
        )
        if results['csv']:
            print(f"Exported CSV: {filepath}")
    
    if settings.export_las:
        filepath = get_export_filepath(settings, 'las', frame)
        results['las'] = export_las(
            points, filepath,
            include_intensity=settings.include_intensity
        )
        if results['las']:
            print(f"Exported LAS: {filepath}")
    
    if settings.export_pcd:
        filepath = get_export_filepath(settings, 'pcd', frame)
        results['pcd'] = export_pcd(
            points, filepath,
            include_intensity=settings.include_intensity
        )
        if results['pcd']:
            print(f"Exported PCD: {filepath}")
    
    return results


class PointCloudExporter:
    """Class to manage point cloud export operations"""
    
    def __init__(self, settings):
        self.settings = settings
    
    def export(self, points: List[ScanPoint], frame: Optional[int] = None) -> dict:
        """Export points to all enabled formats"""
        return export_all_formats(points, self.settings, frame)
    
    def get_export_summary(self, points: List[ScanPoint]) -> str:
        """Get a summary of what will be exported"""
        formats = []
        if self.settings.export_ply:
            formats.append("PLY")
        if self.settings.export_csv:
            formats.append("CSV")
        if self.settings.export_las:
            formats.append("LAS")
        if self.settings.export_pcd:
            formats.append("PCD")
        
        return f"{len(points)} points to {', '.join(formats)} in {self.settings.export_path}"
