# LiDAR Scanner Core - Ray Casting and Point Cloud Generation
import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix, Euler
import time


class ScanPoint:
    """Represents a single LiDAR scan point"""
    __slots__ = ['position', 'distance', 'intensity', 'normal', 'object_name', 
                 'category_id', 'return_number', 'angle_h', 'angle_v']
    
    def __init__(self, position, distance, intensity=1.0, normal=None, 
                 object_name="", category_id="", return_number=1,
                 angle_h=0.0, angle_v=0.0):
        self.position = position
        self.distance = distance
        self.intensity = intensity
        self.normal = normal if normal else Vector((0, 0, 1))
        self.object_name = object_name
        self.category_id = category_id
        self.return_number = return_number
        self.angle_h = angle_h
        self.angle_v = angle_v


class LiDARScanner:
    """Main LiDAR scanner simulation class"""
    
    def __init__(self, settings):
        self.settings = settings
        self.points = []
        self.scan_time = 0.0
        
    def get_scanner_matrix(self):
        """Get the transformation matrix for the scanner"""
        if self.settings.scanner_object:
            return self.settings.scanner_object.matrix_world.copy()
        else:
            loc = Vector(self.settings.origin)
            rot = Euler([math.radians(r) for r in self.settings.rotation_deg], 'XYZ')
            return Matrix.Translation(loc) @ rot.to_matrix().to_4x4()
    
    def generate_ray_directions(self):
        """Generate ray directions based on FOV and resolution settings"""
        directions = []
        
        fov_h = self.settings.fov_h
        fov_v = self.settings.fov_v
        res_h = max(0.01, self.settings.resolution_h)
        res_v = max(0.01, self.settings.resolution_v)
        
        h_steps = int(fov_h / res_h)
        v_steps = int(fov_v / res_v)
        
        h_start = -fov_h / 2
        v_start = -fov_v / 2
        
        for v_idx in range(v_steps + 1):
            for h_idx in range(h_steps + 1):
                angle_h = h_start + h_idx * res_h
                angle_v = v_start + v_idx * res_v
                
                h_rad = math.radians(angle_h)
                v_rad = math.radians(angle_v)
                
                x = math.cos(v_rad) * math.sin(h_rad)
                y = math.cos(v_rad) * math.cos(h_rad)
                z = math.sin(v_rad)
                
                direction = Vector((x, y, z)).normalized()
                directions.append((angle_h, angle_v, direction))
        
        return directions
    
    def apply_noise_to_distance(self, distance):
        """Apply noise to distance measurement"""
        if not self.settings.enable_noise:
            return distance
        
        sigma = self.settings.range_sigma_m
        
        if self.settings.noise_type == 'GAUSSIAN':
            noise = random.gauss(0, sigma)
        elif self.settings.noise_type == 'UNIFORM':
            noise = random.uniform(-sigma * 2, sigma * 2)
        elif self.settings.noise_type == 'RAYLEIGH':
            noise = math.sqrt(random.gauss(0, sigma) ** 2 + random.gauss(0, sigma) ** 2)
            noise = noise * (1 if random.random() > 0.5 else -1)
        else:
            noise = 0
        
        return max(0, distance + noise)
    
    def apply_noise_to_direction(self, direction):
        """Apply angular noise to ray direction"""
        if not self.settings.enable_noise or self.settings.angular_noise_deg <= 0:
            return direction
        
        sigma = math.radians(self.settings.angular_noise_deg)
        
        noise_x = random.gauss(0, sigma)
        noise_y = random.gauss(0, sigma)
        noise_z = random.gauss(0, sigma)
        
        noise_euler = Euler((noise_x, noise_y, noise_z), 'XYZ')
        noisy_dir = noise_euler.to_matrix() @ direction
        
        return noisy_dir.normalized()
    
    def should_dropout(self):
        """Determine if a point should be dropped"""
        if not self.settings.enable_noise:
            return False
        return random.random() < self.settings.dropout_prob
    
    def calculate_intensity(self, distance, hit_obj, normal, ray_dir):
        """Calculate return intensity based on distance, material, and angle"""
        if not self.settings.enable_intensity:
            return 1.0
        
        base_intensity = 1.0
        if hit_obj and hit_obj.active_material:
            mat = hit_obj.active_material
            if mat.use_nodes and mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        color = node.inputs['Base Color'].default_value
                        base_intensity = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
                        break
        
        if normal:
            cos_angle = abs(normal.dot(-ray_dir))
            angle_factor = max(0.1, cos_angle)
        else:
            angle_factor = 1.0
        
        if self.settings.intensity_falloff == 'QUADRATIC':
            distance_factor = 1.0 / max(1.0, distance ** 2) * 100
        elif self.settings.intensity_falloff == 'LINEAR':
            distance_factor = 1.0 / max(1.0, distance) * 10
        else:
            distance_factor = 1.0
        
        intensity = base_intensity * angle_factor * distance_factor
        return min(1.0, max(0.0, intensity))
    
    def apply_weather_effects(self, distance, intensity):
        """Apply weather effects (rain, fog) to measurements"""
        if not self.settings.enable_weather:
            return distance, intensity, True
        
        if self.settings.rain_rate > 0:
            rain_atten = math.exp(-0.01 * self.settings.rain_rate * distance)
            intensity *= rain_atten
            
            if random.random() < self.settings.rain_rate / 1000 * distance / 10:
                distance = distance * random.uniform(0.3, 0.9)
        
        if self.settings.fog_density > 0:
            fog_atten = math.exp(-self.settings.fog_density * distance / 50)
            intensity *= fog_atten
            
            if intensity < 0.05:
                return distance, intensity, False
        
        return distance, intensity, True
    
    def get_category_id(self, obj):
        """Get category ID from object custom properties"""
        if obj is None:
            return ""
        
        if "categoryID" in obj:
            return str(obj["categoryID"])
        if "category_id" in obj:
            return str(obj["category_id"])
        
        return obj.name
    
    def cast_ray(self, origin, direction, angle_h, angle_v):
        """Cast a single ray and return scan point if hit"""
        
        noisy_dir = self.apply_noise_to_direction(direction)
        
        depsgraph = bpy.context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = bpy.context.scene.ray_cast(
            depsgraph, origin, noisy_dir
        )
        
        if not result:
            return None
        
        distance = (location - origin).length
        
        if distance < self.settings.range_min or distance > self.settings.range_max:
            return None
        
        if self.should_dropout():
            return None
        
        noisy_distance = self.apply_noise_to_distance(distance)
        noisy_position = origin + noisy_dir * noisy_distance
        
        intensity = self.calculate_intensity(distance, obj, normal, noisy_dir)
        
        noisy_distance, intensity, valid = self.apply_weather_effects(noisy_distance, intensity)
        if not valid:
            return None
        
        category = self.get_category_id(obj)
        
        return ScanPoint(
            position=noisy_position,
            distance=noisy_distance,
            intensity=intensity,
            normal=normal.copy() if normal else None,
            object_name=obj.name if obj else "",
            category_id=category,
            return_number=1,
            angle_h=angle_h,
            angle_v=angle_v
        )
    
    def scan(self, progress_callback=None):
        """Perform the full LiDAR scan"""
        start_time = time.time()
        self.points = []
        
        scanner_matrix = self.get_scanner_matrix()
        origin = scanner_matrix.translation.copy()
        
        directions = self.generate_ray_directions()
        total_rays = len(directions)
        
        if self.settings.debug_output:
            print(f"LiDAR Scan: {total_rays} rays to cast")
        
        for i, (angle_h, angle_v, local_dir) in enumerate(directions):
            world_dir = (scanner_matrix.to_3x3() @ local_dir).normalized()
            
            point = self.cast_ray(origin, world_dir, angle_h, angle_v)
            
            if point:
                self.points.append(point)
            
            if progress_callback and i % 1000 == 0:
                progress_callback(i / total_rays)
        
        self.scan_time = time.time() - start_time
        
        if self.settings.debug_output:
            print(f"LiDAR Scan complete: {len(self.points)} points in {self.scan_time:.2f}s")
        
        return self.points
    
    def get_points_as_array(self):
        """Get points as a list of [x, y, z, intensity, distance] lists"""
        return [
            [p.position.x, p.position.y, p.position.z, p.intensity, p.distance]
            for p in self.points
        ]
    
    def create_point_cloud_mesh(self, name="LiDAR_PointCloud"):
        """Create a mesh object from the scan points"""
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        
        bm = bmesh.new()
        
        for point in self.points:
            bm.verts.new(point.position)
        
        bm.to_mesh(mesh)
        bm.free()
        
        bpy.context.collection.objects.link(obj)
        
        if self.points:
            if not mesh.attributes.get("intensity"):
                mesh.attributes.new(name="intensity", type='FLOAT', domain='POINT')
            
            intensity_attr = mesh.attributes["intensity"]
            for i, point in enumerate(self.points):
                intensity_attr.data[i].value = point.intensity
            
            if not mesh.attributes.get("distance"):
                mesh.attributes.new(name="distance", type='FLOAT', domain='POINT')
            
            distance_attr = mesh.attributes["distance"]
            for i, point in enumerate(self.points):
                distance_attr.data[i].value = point.distance
        
        return obj
    
    def get_scan_statistics(self):
        """Get statistics about the scan"""
        if not self.points:
            return {'total_points': 0, 'scan_time': self.scan_time}
        
        distances = [p.distance for p in self.points]
        intensities = [p.intensity for p in self.points]
        
        return {
            'total_points': len(self.points),
            'scan_time': self.scan_time,
            'min_distance': min(distances),
            'max_distance': max(distances),
            'mean_distance': sum(distances) / len(distances),
            'min_intensity': min(intensities),
            'max_intensity': max(intensities),
            'mean_intensity': sum(intensities) / len(intensities),
            'unique_objects': len(set(p.object_name for p in self.points)),
        }


def clamp_settings(settings):
    """Clamp settings to valid ranges and return a dict"""
    return {
        'fov_h': max(1.0, min(360.0, settings.fov_h)),
        'fov_v': max(1.0, min(90.0, settings.fov_v)),
        'resolution_h': max(0.01, min(5.0, settings.resolution_h)),
        'resolution_v': max(0.01, min(5.0, settings.resolution_v)),
        'range_max': max(0.1, min(500.0, settings.range_max)),
        'range_sigma_m': max(0.0, min(0.5, settings.range_sigma_m)),
        'dropout_prob': max(0.0, min(0.3, settings.dropout_prob)),
    }


def generate_scan_json(scene_config, scan_config):
    """Generate JSON configuration for LiDAR scan"""
    
    fov_h = max(1, min(360, scan_config.get('fov_h', 360)))
    fov_v = max(1, min(90, scan_config.get('fov_v', 30)))
    res_h = max(0.01, min(5, scan_config.get('resolution_h', 0.2)))
    res_v = max(0.01, min(5, scan_config.get('resolution_v', 1.0)))
    range_m = max(0.1, min(500, scan_config.get('range_m', 100)))
    range_sigma = max(0, min(0.5, scan_config.get('range_sigma_m', 0.02)))
    dropout = max(0, min(0.3, scan_config.get('dropout_prob', 0.02)))
    
    result = {}
    
    if scene_config:
        result['scene'] = {
            'create_object': {
                'type': scene_config.get('type', 'cube'),
                'asset_path': scene_config.get('asset_path', ''),
                'location': scene_config.get('location', [0, 0, 0]),
                'rotation_deg': scene_config.get('rotation_deg', [0, 0, 0]),
                'scale': scene_config.get('scale', [1, 1, 1]),
            }
        }
    
    result['scan'] = {
        'sensor_preset': scan_config.get('sensor_preset', 'AUTO'),
        'origin': scan_config.get('origin', [0, 0, 1.8]),
        'rotation_deg': scan_config.get('rotation_deg', [0, 0, 0]),
        'fov_deg': {'h': fov_h, 'v': fov_v},
        'resolution_deg': {'h': res_h, 'v': res_v},
        'range_m': range_m,
        'noise': {
            'range_sigma_m': range_sigma,
            'dropout_prob': dropout,
        },
        'output': {
            'formats': scan_config.get('formats', ['ply']),
            'path': scan_config.get('path', '//scans/'),
            'include_labels': scan_config.get('include_labels', True),
        }
    }
    
    return result
