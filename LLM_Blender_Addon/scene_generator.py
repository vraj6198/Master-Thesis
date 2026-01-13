"""
Scene Generator Module
Converts LLM responses into Blender 3D scenes and Python scripts
"""

import bpy
import re
import mathutils
from typing import Optional


# Pre-built templates for common 3D objects - these ALWAYS work
OBJECT_TEMPLATES = {
    'chair': """import bpy
# Create chair seat
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
seat = bpy.context.object
seat.name = 'Chair_Seat'
seat.scale = (0.5, 0.5, 0.05)

# Create chair back
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.225, 0.85))
back = bpy.context.object
back.name = 'Chair_Back'
back.scale = (0.5, 0.05, 0.35)

# Create chair legs
leg_positions = [(0.2, 0.2, 0.225), (-0.2, 0.2, 0.225), (0.2, -0.2, 0.225), (-0.2, -0.2, 0.225)]
for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.object
    leg.name = f'Chair_Leg_{i+1}'
    leg.scale = (0.05, 0.05, 0.225)
""",

    'table': """import bpy
# Create table top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
top = bpy.context.object
top.name = 'Table_Top'
top.scale = (1.0, 0.6, 0.05)

# Create table legs
leg_positions = [(0.45, 0.25, 0.35), (-0.45, 0.25, 0.35), (0.45, -0.25, 0.35), (-0.45, -0.25, 0.35)]
for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.object
    leg.name = f'Table_Leg_{i+1}'
    leg.scale = (0.05, 0.05, 0.35)
""",

    'cube': """import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
bpy.context.object.name = 'Cube'
""",

    'sphere': """import bpy
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
bpy.context.object.name = 'Sphere'
""",

    'cylinder': """import bpy
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(0, 0, 1))
bpy.context.object.name = 'Cylinder'
""",

    'cone': """import bpy
bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(0, 0, 1))
bpy.context.object.name = 'Cone'
""",

    'torus': """import bpy
bpy.ops.mesh.primitive_torus_add(location=(0, 0, 1))
bpy.context.object.name = 'Torus'
""",

    'plane': """import bpy
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
bpy.context.object.name = 'Plane'
""",

    'monkey': """import bpy
bpy.ops.mesh.primitive_monkey_add(size=1, location=(0, 0, 1))
bpy.context.object.name = 'Suzanne'
""",

    'house': """import bpy
# Create house base
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
base = bpy.context.object
base.name = 'House_Base'
base.scale = (1, 0.8, 0.5)

# Create roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.2, depth=0.6, location=(0, 0, 1.05))
roof = bpy.context.object
roof.name = 'House_Roof'
roof.rotation_euler = (0, 0, 0.785)
""",

    'tree': """import bpy
# Create trunk
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=1.5, location=(0, 0, 0.75))
trunk = bpy.context.object
trunk.name = 'Tree_Trunk'

# Create foliage
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, 0, 1.8))
foliage = bpy.context.object
foliage.name = 'Tree_Foliage'
""",

    'car': """import bpy
# Create car body
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.4))
body = bpy.context.object
body.name = 'Car_Body'
body.scale = (1, 0.5, 0.25)

# Create car top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.1, 0, 0.65))
top = bpy.context.object
top.name = 'Car_Top'
top.scale = (0.5, 0.45, 0.15)

# Create wheels
wheel_positions = [(0.35, 0.3, 0.15), (-0.35, 0.3, 0.15), (0.35, -0.3, 0.15), (-0.35, -0.3, 0.15)]
for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.1, location=pos)
    wheel = bpy.context.object
    wheel.name = f'Car_Wheel_{i+1}'
    wheel.rotation_euler = (1.5708, 0, 0)
""",

    'bed': """import bpy
# Create mattress
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.3))
mattress = bpy.context.object
mattress.name = 'Bed_Mattress'
mattress.scale = (1, 0.6, 0.15)

# Create headboard
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.45, 0, 0.55))
headboard = bpy.context.object
headboard.name = 'Bed_Headboard'
headboard.scale = (0.05, 0.6, 0.25)

# Create legs
leg_positions = [(0.45, 0.25, 0.1), (-0.45, 0.25, 0.1), (0.45, -0.25, 0.1), (-0.45, -0.25, 0.1)]
for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.object
    leg.name = f'Bed_Leg_{i+1}'
    leg.scale = (0.05, 0.05, 0.1)
""",

    'lamp': """import bpy
# Create lamp base
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.05, location=(0, 0, 0.025))
base = bpy.context.object
base.name = 'Lamp_Base'

# Create lamp pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.8, location=(0, 0, 0.45))
pole = bpy.context.object
pole.name = 'Lamp_Pole'

# Create lamp shade
bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.1, depth=0.25, location=(0, 0, 0.95))
shade = bpy.context.object
shade.name = 'Lamp_Shade'
""",

    'desk': """import bpy
# Create desk top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
top = bpy.context.object
top.name = 'Desk_Top'
top.scale = (1.2, 0.6, 0.04)

# Create desk legs
leg_positions = [(0.55, 0.25, 0.365), (-0.55, 0.25, 0.365), (0.55, -0.25, 0.365), (-0.55, -0.25, 0.365)]
for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.object
    leg.name = f'Desk_Leg_{i+1}'
    leg.scale = (0.04, 0.04, 0.365)
""",

    'bookshelf': """import bpy
# Create bookshelf sides
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.45, 0, 0.75))
left = bpy.context.object
left.name = 'Shelf_Left'
left.scale = (0.03, 0.25, 0.75)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0.45, 0, 0.75))
right = bpy.context.object
right.name = 'Shelf_Right'
right.scale = (0.03, 0.25, 0.75)

# Create shelves
shelf_heights = [0.0, 0.35, 0.7, 1.05, 1.4]
for i, h in enumerate(shelf_heights):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, h + 0.05))
    shelf = bpy.context.object
    shelf.name = f'Shelf_{i+1}'
    shelf.scale = (0.45, 0.25, 0.025)

# Create back
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.24, 0.75))
back = bpy.context.object
back.name = 'Shelf_Back'
back.scale = (0.45, 0.01, 0.75)
""",
}


class SceneGenerator:
    """Handles 3D scene generation from LLM responses"""
    
    @staticmethod
    def find_matching_template(prompt: str) -> Optional[str]:
        """
        Find a matching template for the given prompt
        
        Args:
            prompt: User prompt
            
        Returns:
            Template code or None
        """
        prompt_lower = prompt.lower()
        
        # Check for exact matches first
        for key in OBJECT_TEMPLATES:
            if key in prompt_lower:
                print(f"[DEBUG] Found matching template: {key}")
                return OBJECT_TEMPLATES[key]
        
        # Check for similar terms
        synonyms = {
            'chair': ['seat', 'stool'],
            'table': ['desk', 'surface'],
            'sphere': ['ball', 'orb', 'globe'],
            'cube': ['box', 'block'],
            'house': ['building', 'home'],
            'tree': ['plant'],
            'car': ['vehicle', 'automobile'],
            'lamp': ['light', 'lantern'],
        }
        
        for key, terms in synonyms.items():
            for term in terms:
                if term in prompt_lower:
                    print(f"[DEBUG] Found synonym match: {term} -> {key}")
                    return OBJECT_TEMPLATES[key]
        
        return None
    
    @staticmethod
    def sanitize_code(code: str) -> str:
        """
        Sanitize and fix common Blender API mistakes in generated code
        
        Args:
            code: Raw Python code from LLM
            
        Returns:
            Sanitized code with common errors fixed
        """
        print("[DEBUG] Sanitizing code...")
        
        # Remove problematic lines that cause common errors
        lines_to_remove = [
            'active_layer_collection',
            'view_layer.active_layer_collection',
            '.link(light)',
            '.link(camera)',
            '.link(lamp)',
            'collection.objects.link(',
            'scene.collection.objects.link(',
            'mathutils.Vector(',
            'bpy.data.lights.new(',
            'bpy.data.cameras.new(',
            'bpy.data.objects.new(',
            '.modifiers.add',
            'bpy.ops.object.modifier_add',
        ]
        
        sanitized_lines = []
        for line in code.split('\n'):
            skip_line = False
            for problematic in lines_to_remove:
                if problematic in line:
                    print(f"[DEBUG] Removing problematic line: {line.strip()}")
                    skip_line = True
                    break
            if not skip_line:
                sanitized_lines.append(line)
        
        code = '\n'.join(sanitized_lines)
        
        # Ensure import bpy is present
        if 'import bpy' not in code:
            code = 'import bpy\n' + code
        
        print("[DEBUG] Code sanitization complete")
        return code
    
    @staticmethod
    def extract_python_code(response: str) -> Optional[str]:
        """
        Extract Python code from LLM response
        """
        print("[DEBUG] Attempting code extraction...")
        
        # Try to extract code from markdown code blocks with python
        pattern = r'```python\s*(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            print(f"[DEBUG] Found {len(matches)} python code block(s)")
            return matches[0].strip()
        
        # Try without language specification
        pattern = r'```\s*(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            code = matches[0].strip()
            if 'bpy' in code.lower() or 'import' in code.lower():
                return code
        
        # If no code blocks found, check if the entire response is code
        if 'bpy.' in response or 'import bpy' in response.lower():
            return response.strip()
        
        return None
    
    @staticmethod
    def execute_blender_script(code: str, library_imports: str = "") -> tuple[bool, str]:
        """
        Execute Python code in Blender
        """
        try:
            # Prepare the execution environment
            exec_globals = {
                'bpy': bpy,
                'mathutils': mathutils,
                '__name__': '__main__'
            }
            
            # Add custom library imports if specified
            full_code = code
            if library_imports:
                full_code = f"{library_imports}\n\n{code}"
            
            print("\n" + "="*50)
            print("Executing Blender Script:")
            print("="*50)
            print(full_code)
            print("="*50 + "\n")
            
            # Execute the code
            exec(full_code, exec_globals)
            
            # Update scene
            bpy.context.view_layer.update()
            
            return True, "Script executed successfully!"
            
        except Exception as e:
            error_msg = f"Error executing script: {str(e)}"
            print(f"\n[ERROR] {error_msg}\n")
            return False, error_msg
    
    @staticmethod
    def generate_enhanced_prompt(prompt: str, with_steps: bool = False) -> str:
        """
        Enhance user prompt for better LLM response
        """
        base_context = (
            "Generate ONLY simple Python code for Blender. Use bpy.ops ONLY.\n"
            "RULES:\n"
            "- Use bpy.ops.mesh.primitive_cube_add() for cubes\n"
            "- Use bpy.ops.mesh.primitive_uv_sphere_add() for spheres\n"
            "- Use bpy.ops.mesh.primitive_cylinder_add() for cylinders\n"
            "- Use bpy.context.object to get last created object\n"
            "- Use .scale = (x, y, z) for scaling\n"
            "- Use .location = (x, y, z) for positioning\n"
            "- Do NOT use collection.objects.link()\n"
            "- Do NOT use mathutils.Vector()\n"
            "- Do NOT use bpy.data.objects.new()\n"
            "- Do NOT use modifiers\n"
            "Wrap code in ```python blocks.\n\n"
        )
        
        if with_steps:
            steps = (
                "EXAMPLE:\n"
                "```python\n"
                "import bpy\n"
                "bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))\n"
                "bpy.context.object.name = 'MyCube'\n"
                "bpy.context.object.scale = (1, 1, 0.1)\n"
                "```\n\n"
            )
            base_context += steps
        
        enhanced = base_context + f"CREATE: {prompt}\n"
        return enhanced
    
    @staticmethod
    def create_simple_object_fallback(object_name: str) -> tuple[bool, str]:
        """
        Create a simple 3D object as fallback
        """
        try:
            object_name = object_name.lower()
            
            if 'cube' in object_name or 'box' in object_name:
                bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
            elif 'sphere' in object_name or 'ball' in object_name:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
            elif 'cylinder' in object_name:
                bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(0, 0, 1))
            elif 'cone' in object_name:
                bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(0, 0, 1))
            elif 'torus' in object_name:
                bpy.ops.mesh.primitive_torus_add(location=(0, 0, 1))
            elif 'plane' in object_name or 'floor' in object_name:
                bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
            elif 'monkey' in object_name or 'suzanne' in object_name:
                bpy.ops.mesh.primitive_monkey_add(size=1, location=(0, 0, 1))
            else:
                bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
            
            obj = bpy.context.object
            obj.name = object_name.title()
            
            return True, f"Created simple {object_name}"
            
        except Exception as e:
            return False, f"Error creating fallback object: {str(e)}"


def process_llm_response(response: str, library_imports: str = "", 
                         create_fallback: bool = True, 
                         original_prompt: str = "") -> tuple[bool, str, Optional[str]]:
    """
    Process LLM response and execute in Blender
    """
    generator = SceneGenerator()
    
    print("\n" + "#"*60)
    print("[DEBUG] Processing LLM Response")
    print("#"*60)
    
    # FIRST: Try to use a pre-built template (most reliable)
    if original_prompt:
        template = generator.find_matching_template(original_prompt)
        if template:
            print("[DEBUG] Using pre-built template (most reliable)")
            success, message = generator.execute_blender_script(template, library_imports)
            if success:
                return True, message + " (Used optimized template)", template
    
    # SECOND: Try to extract and execute LLM code
    code = generator.extract_python_code(response)
    
    if code:
        print(f"[DEBUG] Extracted LLM code ({len(code)} chars)")
        sanitized_code = generator.sanitize_code(code)
        success, message = generator.execute_blender_script(sanitized_code, library_imports)
        
        if success:
            return True, message, sanitized_code
        else:
            print(f"[DEBUG] LLM code failed: {message}")
            # Try template as fallback
            if original_prompt:
                template = generator.find_matching_template(original_prompt)
                if template:
                    print("[DEBUG] Falling back to template")
                    success2, message2 = generator.execute_blender_script(template, library_imports)
                    if success2:
                        return True, message2 + " (Template fallback)", template
    
    # THIRD: Create simple fallback object
    if create_fallback and original_prompt:
        print("[DEBUG] Using simple fallback")
        success, message = generator.create_simple_object_fallback(original_prompt)
        return success, message, None
    
    return False, "Could not generate 3D scene. Try a simpler prompt like 'chair', 'table', or 'cube'.", None
