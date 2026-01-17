# LiDAR Scanner UI Panels
import bpy
from bpy.types import Panel


class LIDAR_PT_main_panel(Panel):
    """Main LiDAR Scanner Panel"""
    bl_label = "LiDAR Scanner"
    bl_idname = "LIDAR_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator("lidar.scan", text="Run LiDAR Scan", icon='OUTLINER_OB_POINTCLOUD')
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Scanner Object", icon='EMPTY_ARROWS')
        box.prop(settings, "scanner_object", text="")
        box.operator("lidar.create_scanner_object", text="Create Scanner", icon='ADD')


class LIDAR_PT_prompt_panel(Panel):
    """LLM Prompt Panel"""
    bl_label = "LLM Prompt"
    bl_idname = "LIDAR_PT_prompt_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner

        layout.label(text="Describe scan parameters:")
        layout.prop(settings, "prompt_text", text="")
        layout.operator("lidar.apply_prompt", text="Apply Prompt", icon='CHECKMARK')

        if settings.last_llm_status:
            box = layout.box()
            box.label(text=settings.last_llm_status, icon='INFO')


class LIDAR_PT_presets_panel(Panel):
    """Sensor Presets Panel"""
    bl_label = "Sensor Presets"
    bl_idname = "LIDAR_PT_presets_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        layout.prop(settings, "sensor_preset", text="Preset")
        layout.operator("lidar.load_preset", text="Apply Preset", icon='CHECKMARK')


class LIDAR_PT_scanner_panel(Panel):
    """Scanner Settings Panel"""
    bl_label = "Scanner Settings"
    bl_idname = "LIDAR_PT_scanner_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        col = layout.column(align=True)
        col.label(text="Position & Orientation:")
        col.prop(settings, "origin", text="Origin")
        col.prop(settings, "rotation_deg", text="Rotation")
        
        layout.separator()
        
        col = layout.column(align=True)
        col.label(text="Field of View (degrees):")
        row = col.row(align=True)
        row.prop(settings, "fov_h", text="Horizontal")
        row.prop(settings, "fov_v", text="Vertical")
        
        col = layout.column(align=True)
        col.label(text="Resolution (degrees):")
        row = col.row(align=True)
        row.prop(settings, "resolution_h", text="Horizontal")
        row.prop(settings, "resolution_v", text="Vertical")
        
        layout.separator()
        
        col = layout.column(align=True)
        col.label(text="Range (meters):")
        row = col.row(align=True)
        row.prop(settings, "range_min", text="Min")
        row.prop(settings, "range_max", text="Max")
        
        layout.operator("lidar.estimate_points", text="Estimate Points", icon='STICKY_UVS_DISABLE')


class LIDAR_PT_noise_panel(Panel):
    """Noise Settings Panel"""
    bl_label = "Noise Simulation"
    bl_idname = "LIDAR_PT_noise_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        settings = context.scene.lidar_scanner
        self.layout.prop(settings, "enable_noise", text="")
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        layout.enabled = settings.enable_noise
        
        layout.prop(settings, "noise_type")
        
        col = layout.column(align=True)
        col.prop(settings, "range_sigma_m", text="Range Noise (m)")
        col.prop(settings, "angular_noise_deg", text="Angular Noise (°)")
        col.prop(settings, "dropout_prob", text="Dropout Probability")


class LIDAR_PT_intensity_panel(Panel):
    """Intensity Settings Panel"""
    bl_label = "Intensity"
    bl_idname = "LIDAR_PT_intensity_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        settings = context.scene.lidar_scanner
        self.layout.prop(settings, "enable_intensity", text="")
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        layout.enabled = settings.enable_intensity
        
        layout.prop(settings, "intensity_falloff")
        
        layout.separator()
        layout.prop(settings, "enable_multi_return")
        if settings.enable_multi_return:
            layout.prop(settings, "max_returns")


class LIDAR_PT_animation_panel(Panel):
    """Animation Settings Panel"""
    bl_label = "Animation"
    bl_idname = "LIDAR_PT_animation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        settings = context.scene.lidar_scanner
        self.layout.prop(settings, "enable_animation", text="")
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        layout.enabled = settings.enable_animation
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(settings, "frame_start", text="Start")
        row.prop(settings, "frame_end", text="End")
        col.prop(settings, "frame_step", text="Step")
        
        layout.separator()
        layout.prop(settings, "rotations_per_second")
        
        layout.separator()
        layout.operator("lidar.scan_animation", text="Scan Animation", icon='RENDER_ANIMATION')


class LIDAR_PT_weather_panel(Panel):
    """Weather Simulation Panel"""
    bl_label = "Weather Simulation"
    bl_idname = "LIDAR_PT_weather_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context):
        settings = context.scene.lidar_scanner
        self.layout.prop(settings, "enable_weather", text="")
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        layout.enabled = settings.enable_weather
        
        col = layout.column(align=True)
        col.prop(settings, "rain_rate")
        col.prop(settings, "fog_density")


class LIDAR_PT_visualization_panel(Panel):
    """Visualization Settings Panel"""
    bl_label = "Visualization"
    bl_idname = "LIDAR_PT_visualization_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        layout.prop(settings, "add_mesh")
        layout.prop(settings, "color_mode")
        
        layout.separator()
        layout.prop(settings, "show_scan_preview")
        if settings.show_scan_preview:
            layout.prop(settings, "preview_point_size")
        
        layout.separator()
        layout.operator("lidar.clear_point_clouds", text="Clear Point Clouds", icon='TRASH')


class LIDAR_PT_export_panel(Panel):
    """Export Settings Panel"""
    bl_label = "Export"
    bl_idname = "LIDAR_PT_export_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        col = layout.column(align=True)
        col.label(text="Export Formats:")
        row = col.row(align=True)
        row.prop(settings, "export_ply", text="PLY", toggle=True)
        row.prop(settings, "export_csv", text="CSV", toggle=True)
        row = col.row(align=True)
        row.prop(settings, "export_las", text="LAS", toggle=True)
        row.prop(settings, "export_pcd", text="PCD", toggle=True)
        
        layout.separator()
        
        col = layout.column(align=True)
        col.prop(settings, "export_path", text="Path")
        col.prop(settings, "export_filename", text="Filename")
        
        layout.separator()
        
        col = layout.column(align=True)
        col.label(text="Include:")
        col.prop(settings, "include_labels")
        col.prop(settings, "include_normals")
        col.prop(settings, "include_intensity")
        
        if settings.enable_animation:
            layout.prop(settings, "export_single_frames")


class LIDAR_PT_config_panel(Panel):
    """Configuration Import/Export Panel"""
    bl_label = "Configuration"
    bl_idname = "LIDAR_PT_config_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.operator("lidar.export_json", text="Export JSON Config", icon='EXPORT')
        col.operator("lidar.import_json", text="Import JSON Config", icon='IMPORT')


class LIDAR_PT_scene_panel(Panel):
    """Scene Object Creation Panel"""
    bl_label = "Scene Objects"
    bl_idname = "LIDAR_PT_scene_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene_settings = context.scene.lidar_scene
        
        layout.prop(scene_settings, "object_type")
        
        if scene_settings.object_type == 'IMPORT_GLB':
            layout.prop(scene_settings, "asset_path")
        
        col = layout.column(align=True)
        col.prop(scene_settings, "location")
        col.prop(scene_settings, "rotation_deg", text="Rotation")
        col.prop(scene_settings, "scale")
        
        layout.separator()
        layout.prop(scene_settings, "category_id")
        
        layout.separator()
        layout.operator("lidar.create_scene_object", text="Create Object", icon='ADD')


class LIDAR_PT_debug_panel(Panel):
    """Debug Settings Panel"""
    bl_label = "Debug"
    bl_idname = "LIDAR_PT_debug_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'LiDAR'
    bl_parent_id = "LIDAR_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.lidar_scanner
        
        col = layout.column(align=True)
        col.prop(settings, "debug_output")
        col.prop(settings, "debug_rays")


classes = [
    LIDAR_PT_main_panel,
    LIDAR_PT_prompt_panel,
    LIDAR_PT_presets_panel,
    LIDAR_PT_scanner_panel,
    LIDAR_PT_noise_panel,
    LIDAR_PT_intensity_panel,
    LIDAR_PT_animation_panel,
    LIDAR_PT_weather_panel,
    LIDAR_PT_visualization_panel,
    LIDAR_PT_export_panel,
    LIDAR_PT_config_panel,
    LIDAR_PT_scene_panel,
    LIDAR_PT_debug_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
