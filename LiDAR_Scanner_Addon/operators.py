# LiDAR Scanner Operators
import bpy
import math
import json
import urllib.request
import urllib.error
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty


def _clamp(value, min_v, max_v):
    return max(min_v, min(max_v, value))


def _map_sensor_preset(preset_name):
    if preset_name == "Velodyne":
        return "VELODYNE_VLP16"
    if preset_name == "Generic32":
        return "GENERIC_32"
    return "AUTO"


def _apply_llm_config(config, context):
    settings = context.scene.lidar_scanner
    scene_settings = context.scene.lidar_scene

    if not config:
        return

    if "scene" in config and "create_object" in config["scene"]:
        obj_cfg = config["scene"]["create_object"]
        obj_type = (obj_cfg.get("type") or "cube").lower()

        if obj_type == "cube":
            scene_settings.object_type = 'CUBE'
        elif obj_type == "sphere":
            scene_settings.object_type = 'SPHERE'
        elif obj_type == "cylinder":
            scene_settings.object_type = 'CYLINDER'
        elif obj_type == "import_glb":
            scene_settings.object_type = 'IMPORT_GLB'
            scene_settings.asset_path = obj_cfg.get("asset_path", "")

        loc = obj_cfg.get("location", [0, 0, 0])
        rot = obj_cfg.get("rotation_deg", [0, 0, 0])
        scale = obj_cfg.get("scale", [1, 1, 1])

        scene_settings.location = loc
        scene_settings.rotation_deg = rot
        scene_settings.scale = scale

    if "scan" in config:
        scan = config["scan"]

        preset = scan.get("sensor_preset", "AUTO")
        if preset in ("AUTO", "Velodyne", "Generic32"):
            settings.sensor_preset = _map_sensor_preset(preset)

        if "origin" in scan:
            settings.origin = scan["origin"]
        if "rotation_deg" in scan:
            settings.rotation_deg = scan["rotation_deg"]

        if "fov_deg" in scan:
            fov = scan.get("fov_deg", {})
            settings.fov_h = _clamp(float(fov.get("h", settings.fov_h)), 1.0, 360.0)
            settings.fov_v = _clamp(float(fov.get("v", settings.fov_v)), 1.0, 90.0)

        if "resolution_deg" in scan:
            res = scan.get("resolution_deg", {})
            settings.resolution_h = _clamp(float(res.get("h", settings.resolution_h)), 0.01, 5.0)
            settings.resolution_v = _clamp(float(res.get("v", settings.resolution_v)), 0.01, 5.0)

        if "range_m" in scan:
            settings.range_max = _clamp(float(scan.get("range_m", settings.range_max)), 0.1, 500.0)

        if "noise" in scan:
            noise = scan.get("noise", {})
            settings.range_sigma_m = _clamp(float(noise.get("range_sigma_m", settings.range_sigma_m)), 0.0, 0.5)
            settings.dropout_prob = _clamp(float(noise.get("dropout_prob", settings.dropout_prob)), 0.0, 0.3)

        if "output" in scan:
            output = scan.get("output", {})
            formats = output.get("formats", [])
            settings.export_ply = "ply" in formats
            settings.export_csv = "csv" in formats
            settings.export_las = "las" in formats
            settings.export_pcd = "pcd" in formats
            if "path" in output:
                settings.export_path = output.get("path", settings.export_path)
            if "include_labels" in output:
                settings.include_labels = bool(output.get("include_labels", True))


def _call_llm(prompt_text, prefs):
    system_prompt = (
        "You are a Blender LiDAR scanning assistant inside a Blender add-on. "
        "Return ONLY valid JSON (no markdown, no comments). "
        "Schema: {"
        "\"scene\": {\"create_object\": {\"type\":\"cube|sphere|cylinder|import_glb\", "
        "\"asset_path\":\"\", \"location\":[x,y,z], \"rotation_deg\":[rx,ry,rz], \"scale\":[sx,sy,sz]}}, "
        "\"scan\": {\"sensor_preset\":\"AUTO|Velodyne|Generic32\", "
        "\"origin\":[x,y,z], \"rotation_deg\":[rx,ry,rz], "
        "\"fov_deg\":{\"h\":number,\"v\":number}, "
        "\"resolution_deg\":{\"h\":number,\"v\":number}, "
        "\"range_m\":number, "
        "\"noise\":{\"range_sigma_m\":number, \"dropout_prob\":number}, "
        "\"output\":{\"formats\":[\"ply\",\"csv\"], \"path\":\"//scans/run_001/\", \"include_labels\":true}}} "
        "Rules: fill defaults if missing. Clamp: fov h 1..360, fov v 1..90, "
        "resolution 0.01..5, range 0.1..500, range_sigma_m 0..0.5, dropout_prob 0..0.3. "
        "If type is import_glb, require asset_path."
    )

    payload = {
        "model": prefs.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ],
        "temperature": prefs.llm_temperature,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(prefs.llm_endpoint, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if prefs.llm_api_key:
        req.add_header("Authorization", f"Bearer {prefs.llm_api_key}")

    with urllib.request.urlopen(req, timeout=prefs.llm_timeout_s) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    # Strip markdown code blocks if present
    if content.startswith("```"):
        lines = content.strip().split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines)
    return content


class LIDAR_OT_scan(Operator):
    """Perform LiDAR scan of the scene"""
    bl_idname = "lidar.scan"
    bl_label = "Run LiDAR Scan"
    bl_description = "Perform a LiDAR scan of the current scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from . import scanner_core
        from . import export_utils
        
        settings = context.scene.lidar_scanner
        
        scanner = scanner_core.LiDARScanner(settings)
        
        self.report({'INFO'}, "Starting LiDAR scan...")
        
        def progress_callback(progress):
            pass
        
        points = scanner.scan(progress_callback)
        
        if not points:
            self.report({'WARNING'}, "No points detected in scan")
            return {'CANCELLED'}
        
        if settings.add_mesh:
            obj = scanner.create_point_cloud_mesh("LiDAR_Scan")
            context.view_layer.objects.active = obj
            obj.select_set(True)
        
        if settings.export_ply or settings.export_csv or settings.export_las or settings.export_pcd:
            results = export_utils.export_all_formats(points, settings)
            exported = [fmt for fmt, success in results.items() if success]
            if exported:
                self.report({'INFO'}, f"Exported: {', '.join(exported)}")
        
        stats = scanner.get_scan_statistics()
        self.report({'INFO'}, 
            f"Scan complete: {stats['total_points']} points in {stats['scan_time']:.2f}s")
        
        return {'FINISHED'}


class LIDAR_OT_scan_animation(Operator):
    """Perform LiDAR scan across animation frames"""
    bl_idname = "lidar.scan_animation"
    bl_label = "Scan Animation"
    bl_description = "Perform LiDAR scans across multiple animation frames"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from . import scanner_core
        from . import export_utils
        
        settings = context.scene.lidar_scanner
        
        if not settings.enable_animation:
            self.report({'ERROR'}, "Animation scanning not enabled")
            return {'CANCELLED'}
        
        scanner = scanner_core.LiDARScanner(settings)
        all_points = []
        
        frame_start = settings.frame_start
        frame_end = settings.frame_end
        frame_step = settings.frame_step
        
        original_frame = context.scene.frame_current
        
        for frame in range(frame_start, frame_end + 1, frame_step):
            context.scene.frame_set(frame)
            points = scanner.scan()
            if points:
                all_points.extend(points)
                if settings.export_single_frames:
                    export_utils.export_all_formats(points, settings, frame)
        
        context.scene.frame_set(original_frame)
        
        if settings.add_mesh and all_points:
            scanner.points = all_points
            obj = scanner.create_point_cloud_mesh("LiDAR_Animation_Scan")
            context.view_layer.objects.active = obj
            obj.select_set(True)
        
        if not settings.export_single_frames and all_points:
            scanner.points = all_points
            export_utils.export_all_formats(all_points, settings)
        
        self.report({'INFO'}, f"Animation scan complete: {len(all_points)} total points")
        return {'FINISHED'}


class LIDAR_OT_create_scanner_object(Operator):
    """Create a scanner empty object at the specified origin"""
    bl_idname = "lidar.create_scanner_object"
    bl_label = "Create Scanner Object"
    bl_description = "Create an empty object to use as scanner origin"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.lidar_scanner
        
        bpy.ops.object.empty_add(type='ARROWS', location=settings.origin)
        scanner_obj = context.active_object
        scanner_obj.name = "LiDAR_Scanner"
        
        scanner_obj.rotation_euler = [
            math.radians(settings.rotation_deg[0]),
            math.radians(settings.rotation_deg[1]),
            math.radians(settings.rotation_deg[2]),
        ]
        
        settings.scanner_object = scanner_obj
        
        self.report({'INFO'}, f"Created scanner object: {scanner_obj.name}")
        return {'FINISHED'}


class LIDAR_OT_create_scene_object(Operator):
    """Create a scene object for scanning"""
    bl_idname = "lidar.create_scene_object"
    bl_label = "Create Scene Object"
    bl_description = "Create a primitive object in the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene_settings = context.scene.lidar_scene
        
        obj_type = scene_settings.object_type
        loc = scene_settings.location
        rot = scene_settings.rotation_deg
        scale = scene_settings.scale
        
        if obj_type == 'CUBE':
            bpy.ops.mesh.primitive_cube_add(location=loc, scale=scale)
        elif obj_type == 'SPHERE':
            bpy.ops.mesh.primitive_uv_sphere_add(location=loc, scale=scale)
        elif obj_type == 'CYLINDER':
            bpy.ops.mesh.primitive_cylinder_add(location=loc, scale=scale)
        elif obj_type == 'PLANE':
            bpy.ops.mesh.primitive_plane_add(location=loc, scale=scale)
        elif obj_type == 'IMPORT_GLB':
            if not scene_settings.asset_path:
                self.report({'ERROR'}, "Asset path required for GLB import")
                return {'CANCELLED'}
            try:
                bpy.ops.import_scene.gltf(filepath=scene_settings.asset_path)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to import GLB: {e}")
                return {'CANCELLED'}
        
        obj = context.active_object
        if obj:
            obj.rotation_euler = [
                math.radians(rot[0]),
                math.radians(rot[1]),
                math.radians(rot[2]),
            ]
            if scene_settings.category_id:
                obj["categoryID"] = scene_settings.category_id
        
        self.report({'INFO'}, f"Created object: {obj.name if obj else 'Unknown'}")
        return {'FINISHED'}


class LIDAR_OT_load_preset(Operator):
    """Load a sensor preset configuration"""
    bl_idname = "lidar.load_preset"
    bl_label = "Load Preset"
    bl_description = "Load the selected sensor preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.lidar_scanner
        self.report({'INFO'}, f"Loaded preset: {settings.sensor_preset}")
        return {'FINISHED'}


class LIDAR_OT_export_json(Operator):
    """Export current scan configuration as JSON"""
    bl_idname = "lidar.export_json"
    bl_label = "Export JSON Config"
    bl_description = "Export the current scanner configuration as JSON"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(
        name="File Path",
        description="Path for JSON export",
        default="//lidar_config.json",
        subtype='FILE_PATH',
    )
    
    def execute(self, context):
        from . import scanner_core
        
        settings = context.scene.lidar_scanner
        
        scan_config = {
            'sensor_preset': settings.sensor_preset,
            'origin': list(settings.origin),
            'rotation_deg': list(settings.rotation_deg),
            'fov_h': settings.fov_h,
            'fov_v': settings.fov_v,
            'resolution_h': settings.resolution_h,
            'resolution_v': settings.resolution_v,
            'range_m': settings.range_max,
            'range_sigma_m': settings.range_sigma_m,
            'dropout_prob': settings.dropout_prob,
            'formats': [],
            'path': settings.export_path,
            'include_labels': settings.include_labels,
        }
        
        if settings.export_ply:
            scan_config['formats'].append('ply')
        if settings.export_csv:
            scan_config['formats'].append('csv')
        if settings.export_las:
            scan_config['formats'].append('las')
        if settings.export_pcd:
            scan_config['formats'].append('pcd')
        
        result = scanner_core.generate_scan_json(None, scan_config)
        
        filepath = bpy.path.abspath(self.filepath)
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        self.report({'INFO'}, f"Exported config to: {filepath}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LIDAR_OT_import_json(Operator):
    """Import scan configuration from JSON"""
    bl_idname = "lidar.import_json"
    bl_label = "Import JSON Config"
    bl_description = "Import scanner configuration from JSON file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(
        name="File Path",
        description="Path to JSON config file",
        subtype='FILE_PATH',
    )
    
    def execute(self, context):
        settings = context.scene.lidar_scanner
        
        try:
            with open(bpy.path.abspath(self.filepath), 'r') as f:
                config = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load JSON: {e}")
            return {'CANCELLED'}
        
        if 'scan' in config:
            scan = config['scan']
            if 'sensor_preset' in scan:
                settings.sensor_preset = scan['sensor_preset']
            if 'origin' in scan:
                settings.origin = scan['origin']
            if 'rotation_deg' in scan:
                settings.rotation_deg = scan['rotation_deg']
            if 'fov_deg' in scan:
                settings.fov_h = scan['fov_deg'].get('h', 360)
                settings.fov_v = scan['fov_deg'].get('v', 30)
            if 'resolution_deg' in scan:
                settings.resolution_h = scan['resolution_deg'].get('h', 0.2)
                settings.resolution_v = scan['resolution_deg'].get('v', 1.0)
            if 'range_m' in scan:
                settings.range_max = scan['range_m']
            if 'noise' in scan:
                settings.range_sigma_m = scan['noise'].get('range_sigma_m', 0.02)
                settings.dropout_prob = scan['noise'].get('dropout_prob', 0.02)
            if 'output' in scan:
                output = scan['output']
                formats = output.get('formats', [])
                settings.export_ply = 'ply' in formats
                settings.export_csv = 'csv' in formats
                settings.export_las = 'las' in formats
                settings.export_pcd = 'pcd' in formats
                settings.export_path = output.get('path', '//scans/')
                settings.include_labels = output.get('include_labels', True)
        
        self.report({'INFO'}, "Imported configuration from JSON")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LIDAR_OT_clear_point_clouds(Operator):
    """Clear all LiDAR point cloud meshes from the scene"""
    bl_idname = "lidar.clear_point_clouds"
    bl_label = "Clear Point Clouds"
    bl_description = "Remove all LiDAR scan point cloud objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        to_delete = [obj for obj in bpy.data.objects if obj.name.startswith("LiDAR_")]
        for obj in to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.report({'INFO'}, f"Removed {len(to_delete)} point cloud objects")
        return {'FINISHED'}


class LIDAR_OT_estimate_points(Operator):
    """Estimate the number of points that will be generated"""
    bl_idname = "lidar.estimate_points"
    bl_label = "Estimate Points"
    bl_description = "Calculate estimated number of scan points"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        settings = context.scene.lidar_scanner
        h_points = int(settings.fov_h / max(0.01, settings.resolution_h)) + 1
        v_points = int(settings.fov_v / max(0.01, settings.resolution_v)) + 1
        total = h_points * v_points
        self.report({'INFO'}, f"Estimated rays: {total:,} ({h_points} H × {v_points} V)")
        return {'FINISHED'}


class LIDAR_OT_apply_prompt(Operator):
    """Parse prompt with LLM and apply settings"""
    bl_idname = "lidar.apply_prompt"
    bl_label = "Apply Prompt"
    bl_description = "Use LLM to convert prompt to scanner parameters"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.lidar_scanner
        prefs = context.preferences.addons["LiDAR_Scanner_Addon"].preferences

        if not settings.prompt_text.strip():
            self.report({'ERROR'}, "Prompt is empty")
            return {'CANCELLED'}

        try:
            content = _call_llm(settings.prompt_text, prefs)
            config = json.loads(content)
        except urllib.error.URLError as e:
            settings.last_llm_status = f"LLM request failed: {e}"
            self.report({'ERROR'}, settings.last_llm_status)
            return {'CANCELLED'}
        except json.JSONDecodeError as e:
            settings.last_llm_status = f"LLM returned invalid JSON: {e}"
            self.report({'ERROR'}, settings.last_llm_status)
            return {'CANCELLED'}
        except Exception as e:
            settings.last_llm_status = f"LLM error: {e}"
            self.report({'ERROR'}, settings.last_llm_status)
            return {'CANCELLED'}

        _apply_llm_config(config, context)
        settings.last_llm_status = "Prompt applied successfully"
        self.report({'INFO'}, "Prompt applied")

        if isinstance(config, dict) and "scene" in config:
            scene_cfg = config.get("scene", {})
            if scene_cfg.get("create_object"):
                try:
                    bpy.ops.lidar.create_scene_object()
                except Exception as e:
                    self.report({'WARNING'}, f"Scene object create failed: {e}")

        context.view_layer.update()

        if settings.enable_animation:
            bpy.ops.lidar.scan_animation()
        else:
            bpy.ops.lidar.scan()

        self.report({'INFO'}, "Prompt applied and scan started")
        return {'FINISHED'}


classes = [
    LIDAR_OT_scan,
    LIDAR_OT_scan_animation,
    LIDAR_OT_create_scanner_object,
    LIDAR_OT_create_scene_object,
    LIDAR_OT_load_preset,
    LIDAR_OT_export_json,
    LIDAR_OT_import_json,
    LIDAR_OT_clear_point_clouds,
    LIDAR_OT_estimate_points,
    LIDAR_OT_apply_prompt,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
