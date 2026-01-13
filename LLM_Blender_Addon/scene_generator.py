"""
Scene Generator Module
Converts LLM responses into Blender 3D scenes and Python scripts
"""

import bpy
import re
import mathutils
from typing import Optional


class SceneGenerator:
    """Handles 3D scene generation from LLM responses"""
    
    @staticmethod
    def extract_python_code(response: str) -> Optional[str]:
        """
        Extract Python code from LLM response
        
        Args:
            response: LLM response text
            
        Returns:
            Extracted Python code or None
        """
        # Try to extract code from markdown code blocks
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Try without language specification
        pattern = r'```\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            # Check if it looks like Python code
            code = matches[0].strip()
            if 'bpy.' in code or 'import' in code:
                return code
        
        # If no code blocks found, check if the entire response is code
        if 'bpy.' in response or ('import' in response and 'def' in response):
            return response.strip()
        
        return None
    
    @staticmethod
    def execute_blender_script(code: str, library_imports: str = "") -> tuple[bool, str]:
        """
        Execute Python code in Blender
        
        Args:
            code: Python code to execute
            library_imports: Additional library imports
            
        Returns:
            Tuple of (success: bool, message: str)
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
            
            # Execute the code
            exec(full_code, exec_globals)
            
            return True, "Script executed successfully!"
            
        except Exception as e:
            return False, f"Error executing script: {str(e)}"
    
    @staticmethod
    def generate_enhanced_prompt(prompt: str, with_steps: bool = False) -> str:
        """
        Enhance user prompt with additional context for better 3D generation
        
        Args:
            prompt: Original user prompt
            with_steps: Whether to add step-by-step instructions
            
        Returns:
            Enhanced prompt
        """
        base_context = (
            "You are a Blender Python script generator. "
            "Generate complete, executable Python code using the Blender API (bpy) "
            "to create 3D objects and scenes in Blender. "
            "The code should be production-ready and handle common edge cases. "
            "Always use bpy.ops, bpy.data, and bpy.context appropriately.\n\n"
        )
        
        if with_steps:
            steps = (
                "Follow these steps:\n"
                "1. Import necessary modules (bpy, mathutils, etc.)\n"
                "2. Delete default objects if needed (optional)\n"
                "3. Create the requested 3D objects with proper materials\n"
                "4. Set up lighting and camera if appropriate\n"
                "5. Apply transformations and modifiers as needed\n\n"
            )
            base_context += steps
        
        enhanced = base_context + f"User request: {prompt}\n\n"
        enhanced += "Provide only the Python code wrapped in ```python code blocks."
        
        return enhanced
    
    @staticmethod
    def create_simple_object_fallback(object_name: str) -> tuple[bool, str]:
        """
        Create a simple 3D object as fallback when LLM doesn't return valid code
        
        Args:
            object_name: Name/type of object to create
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            object_name = object_name.lower()
            
            # Determine object type from name
            if 'cube' in object_name or 'box' in object_name:
                bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
            elif 'sphere' in object_name or 'ball' in object_name:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
            elif 'cylinder' in object_name:
                bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 1))
            elif 'cone' in object_name:
                bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(0, 0, 1))
            elif 'torus' in object_name:
                bpy.ops.mesh.primitive_torus_add(location=(0, 0, 1))
            elif 'plane' in object_name or 'floor' in object_name:
                bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
            elif 'monkey' in object_name or 'suzanne' in object_name:
                bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 1))
            else:
                # Default to cube
                bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
            
            # Get the active object
            obj = bpy.context.active_object
            obj.name = object_name.title()
            
            return True, f"Created simple {object_name}"
            
        except Exception as e:
            return False, f"Error creating fallback object: {str(e)}"


def process_llm_response(response: str, library_imports: str = "", 
                         create_fallback: bool = False) -> tuple[bool, str, Optional[str]]:
    """
    Process LLM response and execute in Blender
    
    Args:
        response: LLM response text
        library_imports: Additional library imports
        create_fallback: Whether to create fallback object if no code found
        
    Returns:
        Tuple of (success: bool, message: str, code: Optional[str])
    """
    generator = SceneGenerator()
    
    # Extract Python code
    code = generator.extract_python_code(response)
    
    if code:
        success, message = generator.execute_blender_script(code, library_imports)
        return success, message, code
    else:
        if create_fallback:
            # Try to create a simple object based on response
            success, message = generator.create_simple_object_fallback(response)
            return success, message, None
        else:
            return False, "No executable Python code found in LLM response.", None
