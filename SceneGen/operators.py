import bpy
import json
from bpy.types import Operator
from . import builder
from . import validator


# Hardcoded demo JSON for a simple chair
DEMO_CHAIR_JSON = {
    "version": "1.0",
    "seed": 42,
    "units": "METERS",
    "objects": [
        {
            "name": "SimpleChair",
            "type": "chair",
            "transform": {
                "location": [0.0, 0.0, 0.0],
                "rotation_euler": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0]
            },
            "params": {
                "style": "simple",
                "seat": {
                    "width": 0.45,
                    "depth": 0.45,
                    "thickness": 0.05
                },
                "legs": {
                    "count": 4,
                    "radius": 0.025,
                    "height": 0.45,
                    "spread": 0.18
                },
                "back": {
                    "height": 0.4,
                    "thickness": 0.04,
                    "tilt_deg": 5.0
                }
            },
            "material": {
                "name": "WoodMaterial",
                "base_color_rgba": [0.55, 0.35, 0.2, 1.0],
                "roughness": 0.7,
                "metallic": 0.0
            }
        }
    ]
}


class SCENEGEN_OT_generate_json(Operator):
    """Generate demo JSON specification (hardcoded for prototype)."""
    
    bl_idname = "scene_gen.generate_json"
    bl_label = "Generate JSON"
    bl_description = "Generate a demo JSON specification"
    
    def execute(self, context):
        props = context.scene.scene_gen
        
        # For prototype: use hardcoded demo JSON
        props.json_spec = json.dumps(DEMO_CHAIR_JSON, indent=2)
        props.log_output = "✓ Generated demo chair JSON specification"
        
        self.report({'INFO'}, "Demo JSON generated")
        return {'FINISHED'}


class SCENEGEN_OT_validate_json(Operator):
    """Validate the JSON specification."""
    
    bl_idname = "scene_gen.validate_json"
    bl_label = "Validate JSON"
    bl_description = "Validate the JSON specification"
    
    def execute(self, context):
        props = context.scene.scene_gen
        
        if not props.json_spec.strip():
            props.log_output = "✗ Error: No JSON to validate"
            self.report({'ERROR'}, "No JSON to validate")
            return {'CANCELLED'}
        
        # Parse and validate
        success, result = validator.validate_json_spec(props.json_spec)
        
        if success:
            props.log_output = "✓ JSON is valid!\n" + result
            self.report({'INFO'}, "JSON is valid")
        else:
            props.log_output = "✗ Validation Error:\n" + result
            self.report({'ERROR'}, f"Validation failed: {result}")
        
        return {'FINISHED'}


class SCENEGEN_OT_build_scene(Operator):
    """Build the scene from JSON specification."""
    
    bl_idname = "scene_gen.build_scene"
    bl_label = "Build Scene"
    bl_description = "Build the 3D scene from JSON specification"
    
    def execute(self, context):
        props = context.scene.scene_gen
        
        if not props.json_spec.strip():
            props.log_output = "✗ Error: No JSON specification"
            self.report({'ERROR'}, "No JSON to build from")
            return {'CANCELLED'}
        
        # Validate first
        success, result = validator.validate_json_spec(props.json_spec)
        if not success:
            props.log_output = "✗ Cannot build - validation failed:\n" + result
            self.report({'ERROR'}, "Validation failed")
            return {'CANCELLED'}
        
        # Parse JSON
        try:
            spec = json.loads(props.json_spec)
        except json.JSONDecodeError as e:
            props.log_output = f"✗ JSON parse error: {e}"
            self.report({'ERROR'}, "JSON parse error")
            return {'CANCELLED'}
        
        # Build the scene
        try:
            log = builder.build_scene(spec)
            props.log_output = "✓ Scene built successfully!\n" + log
            self.report({'INFO'}, "Scene built")
        except Exception as e:
            props.log_output = f"✗ Build error: {str(e)}"
            self.report({'ERROR'}, f"Build error: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class SCENEGEN_OT_clear_scene(Operator):
    """Clear objects created by SceneGen."""
    
    bl_idname = "scene_gen.clear_scene"
    bl_label = "Clear Scene"
    bl_description = "Remove only objects created by SceneGen"
    
    def execute(self, context):
        props = context.scene.scene_gen
        
        # Find and remove objects with our tag
        removed_count = 0
        objects_to_remove = []
        
        for obj in bpy.data.objects:
            if obj.get("scene_gen_id") == "v1":
                objects_to_remove.append(obj)
        
        for obj in objects_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)
            removed_count += 1
        
        # Clean up orphan meshes
        for mesh in bpy.data.meshes:
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        
        # Clean up orphan materials
        for mat in bpy.data.materials:
            if mat.users == 0 and mat.get("scene_gen_id") == "v1":
                bpy.data.materials.remove(mat)
        
        props.log_output = f"✓ Cleared {removed_count} SceneGen objects"
        self.report({'INFO'}, f"Cleared {removed_count} objects")
        
        return {'FINISHED'}


# List of classes to register
classes = [
    SCENEGEN_OT_generate_json,
    SCENEGEN_OT_validate_json,
    SCENEGEN_OT_build_scene,
    SCENEGEN_OT_clear_scene,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
