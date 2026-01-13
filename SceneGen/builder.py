"""
Deterministic Scene Builder for SceneGen.
Uses bpy.data and bmesh APIs (no bpy.ops, no edit mode).
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix


# Tag for identifying SceneGen objects
SCENE_GEN_TAG = "scene_gen_id"
SCENE_GEN_VERSION = "v1"


def build_scene(spec: dict) -> str:
    """
    Build a 3D scene from a validated JSON specification.
    
    Args:
        spec: Validated JSON specification dictionary
        
    Returns:
        Log string describing what was built
    """
    log_lines = []
    
    # Process objects
    objects = spec.get("objects", [])
    for obj_spec in objects:
        obj_type = obj_spec.get("type", "")
        name = obj_spec.get("name", "Object")
        
        if obj_type == "chair":
            created = build_chair(obj_spec)
            log_lines.append(f"Built chair: {name} ({len(created)} meshes)")
        elif obj_type == "cube":
            obj = build_cube(obj_spec)
            log_lines.append(f"Built cube: {name}")
        elif obj_type == "cylinder":
            obj = build_cylinder(obj_spec)
            log_lines.append(f"Built cylinder: {name}")
        elif obj_type == "plane":
            obj = build_plane(obj_spec)
            log_lines.append(f"Built plane: {name}")
        else:
            log_lines.append(f"Skipped unknown type: {obj_type}")
    
    return "\n".join(log_lines)


def tag_object(obj):
    """Tag an object as created by SceneGen."""
    obj[SCENE_GEN_TAG] = SCENE_GEN_VERSION


def get_or_create_material(mat_spec: dict) -> bpy.types.Material:
    """Create or get a material based on specification."""
    name = mat_spec.get("name", "SceneGenMaterial")
    
    # Check if material already exists
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        mat[SCENE_GEN_TAG] = SCENE_GEN_VERSION
    
    # Get the Principled BSDF node
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if bsdf:
        # Set base color (RGBA)
        color = mat_spec.get("base_color_rgba", [0.8, 0.8, 0.8, 1.0])
        bsdf.inputs["Base Color"].default_value = color
        
        # Set roughness
        roughness = mat_spec.get("roughness", 0.5)
        bsdf.inputs["Roughness"].default_value = roughness
        
        # Set metallic
        metallic = mat_spec.get("metallic", 0.0)
        bsdf.inputs["Metallic"].default_value = metallic
    
    return mat


def apply_transform(obj, transform_spec: dict):
    """Apply transform to an object."""
    if not transform_spec:
        return
    
    loc = transform_spec.get("location", [0, 0, 0])
    rot = transform_spec.get("rotation_euler", [0, 0, 0])
    scale = transform_spec.get("scale", [1, 1, 1])
    
    obj.location = Vector(loc)
    obj.rotation_euler = rot
    obj.scale = Vector(scale)


def link_to_collection(obj, collection_name: str = None):
    """Link object to a collection."""
    if collection_name:
        # Get or create collection
        coll = bpy.data.collections.get(collection_name)
        if coll is None:
            coll = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(coll)
        coll.objects.link(obj)
    else:
        # Link to scene collection
        bpy.context.scene.collection.objects.link(obj)


def create_mesh_object(name: str, mesh: bpy.types.Mesh) -> bpy.types.Object:
    """Create and link a mesh object."""
    obj = bpy.data.objects.new(name, mesh)
    link_to_collection(obj)
    tag_object(obj)
    return obj


# ============================================================
# Primitive Builders (using bmesh, no bpy.ops)
# ============================================================

def build_cube(spec: dict) -> bpy.types.Object:
    """Build a cube using bmesh."""
    name = spec.get("name", "Cube")
    transform = spec.get("transform", {})
    mat_spec = spec.get("material", {})
    
    # Create mesh with bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = create_mesh_object(name, mesh)
    apply_transform(obj, transform)
    
    if mat_spec:
        mat = get_or_create_material(mat_spec)
        obj.data.materials.append(mat)
    
    return obj


def build_cylinder(spec: dict, segments: int = 16) -> bpy.types.Object:
    """Build a cylinder using bmesh."""
    name = spec.get("name", "Cylinder")
    transform = spec.get("transform", {})
    mat_spec = spec.get("material", {})
    params = spec.get("params", {})
    
    radius = params.get("radius", 0.5)
    depth = params.get("depth", 2.0)
    
    # Create mesh with bmesh
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth
    )
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = create_mesh_object(name, mesh)
    apply_transform(obj, transform)
    
    if mat_spec:
        mat = get_or_create_material(mat_spec)
        obj.data.materials.append(mat)
    
    return obj


def build_plane(spec: dict) -> bpy.types.Object:
    """Build a plane using mesh.from_pydata."""
    name = spec.get("name", "Plane")
    transform = spec.get("transform", {})
    mat_spec = spec.get("material", {})
    params = spec.get("params", {})
    
    size = params.get("size", 2.0)
    half = size / 2
    
    # Create mesh from vertices and faces
    verts = [
        (-half, -half, 0),
        (half, -half, 0),
        (half, half, 0),
        (-half, half, 0)
    ]
    faces = [(0, 1, 2, 3)]
    
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = create_mesh_object(name, mesh)
    apply_transform(obj, transform)
    
    if mat_spec:
        mat = get_or_create_material(mat_spec)
        obj.data.materials.append(mat)
    
    return obj


# ============================================================
# Chair Builder (procedural, bmesh-based)
# ============================================================

def build_chair(spec: dict) -> list:
    """
    Build a chair procedurally using bmesh.
    
    Chair structure:
    - Seat (scaled cube)
    - 4 Legs (cylinders)
    - Backrest (tilted cube)
    
    Returns list of created objects.
    """
    name = spec.get("name", "Chair")
    transform = spec.get("transform", {})
    params = spec.get("params", {})
    mat_spec = spec.get("material", {})
    
    # Get parameters with defaults
    seat = params.get("seat", {})
    seat_width = seat.get("width", 0.45)
    seat_depth = seat.get("depth", 0.45)
    seat_thickness = seat.get("thickness", 0.05)
    
    legs = params.get("legs", {})
    leg_radius = legs.get("radius", 0.025)
    leg_height = legs.get("height", 0.45)
    leg_spread = legs.get("spread", 0.18)
    
    back = params.get("back", {})
    back_height = back.get("height", 0.4)
    back_thickness = back.get("thickness", 0.04)
    back_tilt_deg = back.get("tilt_deg", 5.0)
    
    # Get base transform
    base_loc = Vector(transform.get("location", [0, 0, 0]))
    base_rot = transform.get("rotation_euler", [0, 0, 0])
    base_scale = Vector(transform.get("scale", [1, 1, 1]))
    
    # Create material
    material = None
    if mat_spec:
        material = get_or_create_material(mat_spec)
    
    created_objects = []
    
    # 1. Build Seat
    seat_obj = build_chair_seat(
        name=f"{name}_Seat",
        width=seat_width,
        depth=seat_depth,
        thickness=seat_thickness,
        location=base_loc + Vector([0, 0, leg_height]),
        material=material
    )
    created_objects.append(seat_obj)
    
    # 2. Build 4 Legs
    leg_positions = [
        (-leg_spread, -leg_spread),  # Front left
        (leg_spread, -leg_spread),   # Front right
        (leg_spread, leg_spread),    # Back right
        (-leg_spread, leg_spread),   # Back left
    ]
    
    for i, (x_off, y_off) in enumerate(leg_positions):
        leg_loc = base_loc + Vector([x_off, y_off, leg_height / 2])
        leg_obj = build_chair_leg(
            name=f"{name}_Leg{i+1}",
            radius=leg_radius,
            height=leg_height,
            location=leg_loc,
            material=material
        )
        created_objects.append(leg_obj)
    
    # 3. Build Backrest
    back_z = leg_height + seat_thickness + back_height / 2
    back_y = seat_depth / 2 - back_thickness / 2
    back_loc = base_loc + Vector([0, back_y, back_z])
    
    back_obj = build_chair_back(
        name=f"{name}_Back",
        width=seat_width,
        height=back_height,
        thickness=back_thickness,
        tilt_deg=back_tilt_deg,
        location=back_loc,
        material=material
    )
    created_objects.append(back_obj)
    
    return created_objects


def build_chair_seat(name: str, width: float, depth: float, thickness: float,
                     location: Vector, material=None) -> bpy.types.Object:
    """Build the seat as a scaled cube."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    
    # Scale the cube to seat dimensions
    bmesh.ops.scale(
        bm,
        vec=(width, depth, thickness),
        verts=bm.verts
    )
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = create_mesh_object(name, mesh)
    obj.location = location
    
    if material:
        obj.data.materials.append(material)
    
    return obj


def build_chair_leg(name: str, radius: float, height: float,
                    location: Vector, material=None) -> bpy.types.Object:
    """Build a leg as a cylinder."""
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=12,
        radius1=radius,
        radius2=radius,
        depth=height
    )
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = create_mesh_object(name, mesh)
    obj.location = location
    
    if material:
        obj.data.materials.append(material)
    
    return obj


def build_chair_back(name: str, width: float, height: float, thickness: float,
                     tilt_deg: float, location: Vector, material=None) -> bpy.types.Object:
    """Build the backrest as a tilted cube."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    
    # Scale to backrest dimensions
    bmesh.ops.scale(
        bm,
        vec=(width, thickness, height),
        verts=bm.verts
    )
    
    # Apply tilt rotation around X axis
    tilt_rad = math.radians(tilt_deg)
    rot_matrix = Matrix.Rotation(tilt_rad, 4, 'X')
    bmesh.ops.transform(bm, matrix=rot_matrix, verts=bm.verts)
    
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = create_mesh_object(name, mesh)
    obj.location = location
    
    if material:
        obj.data.materials.append(material)
    
    return obj
