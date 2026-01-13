bl_info = {
    "name": "LLM 3D Generator Simple",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > LLM AI",
    "description": "Simple 3D object generator with LLM support",
    "category": "3D View",
}

import bpy
import requests
from bpy.props import StringProperty, EnumProperty, BoolProperty

# ============================================
# SIMPLE OBJECT CREATION FUNCTIONS
# ============================================

def create_chair():
    """Create a simple chair"""
    # Seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    bpy.context.object.name = 'Chair_Seat'
    bpy.context.object.scale = (0.5, 0.5, 0.05)
    
    # Back
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.225, 0.85))
    bpy.context.object.name = 'Chair_Back'
    bpy.context.object.scale = (0.5, 0.05, 0.35)
    
    # Legs
    positions = [(0.2, 0.2, 0.225), (-0.2, 0.2, 0.225), (0.2, -0.2, 0.225), (-0.2, -0.2, 0.225)]
    for i, pos in enumerate(positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        bpy.context.object.name = f'Chair_Leg_{i+1}'
        bpy.context.object.scale = (0.05, 0.05, 0.225)

def create_table():
    """Create a simple table"""
    # Top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
    bpy.context.object.name = 'Table_Top'
    bpy.context.object.scale = (1.0, 0.6, 0.05)
    
    # Legs
    positions = [(0.45, 0.25, 0.35), (-0.45, 0.25, 0.35), (0.45, -0.25, 0.35), (-0.45, -0.25, 0.35)]
    for i, pos in enumerate(positions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
        bpy.context.object.name = f'Table_Leg_{i+1}'
        bpy.context.object.scale = (0.05, 0.05, 0.35)

def create_house():
    """Create a simple house"""
    # Base
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
    bpy.context.object.name = 'House_Base'
    
    # Roof
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.8, depth=1.2, location=(0, 0, 2.6))
    bpy.context.object.name = 'House_Roof'
    bpy.context.object.rotation_euler = (0, 0, 0.785)

def create_tree():
    """Create a simple tree"""
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=2, location=(0, 0, 1))
    bpy.context.object.name = 'Tree_Trunk'
    
    # Foliage
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 2.5))
    bpy.context.object.name = 'Tree_Foliage'

def create_car():
    """Create a simple car"""
    # Body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.4))
    bpy.context.object.name = 'Car_Body'
    bpy.context.object.scale = (2, 1, 0.5)
    
    # Top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.2, 0, 0.9))
    bpy.context.object.name = 'Car_Top'
    bpy.context.object.scale = (1, 0.9, 0.3)
    
    # Wheels
    wheel_pos = [(0.7, 0.6, 0.2), (-0.7, 0.6, 0.2), (0.7, -0.6, 0.2), (-0.7, -0.6, 0.2)]
    for i, pos in enumerate(wheel_pos):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.15, location=pos)
        bpy.context.object.name = f'Car_Wheel_{i+1}'
        bpy.context.object.rotation_euler = (1.5708, 0, 0)

# ============================================
# OPERATORS
# ============================================

class SIMPLE_OT_CreateChair(bpy.types.Operator):
    bl_idname = "simple.create_chair"
    bl_label = "Create Chair"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        create_chair()
        self.report({'INFO'}, "Chair created!")
        return {'FINISHED'}

class SIMPLE_OT_CreateTable(bpy.types.Operator):
    bl_idname = "simple.create_table"
    bl_label = "Create Table"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        create_table()
        self.report({'INFO'}, "Table created!")
        return {'FINISHED'}

class SIMPLE_OT_CreateCube(bpy.types.Operator):
    bl_idname = "simple.create_cube"
    bl_label = "Create Cube"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
        bpy.context.object.name = 'Cube'
        self.report({'INFO'}, "Cube created!")
        return {'FINISHED'}

class SIMPLE_OT_CreateSphere(bpy.types.Operator):
    bl_idname = "simple.create_sphere"
    bl_label = "Create Sphere"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
        bpy.context.object.name = 'Sphere'
        self.report({'INFO'}, "Sphere created!")
        return {'FINISHED'}

class SIMPLE_OT_CreateHouse(bpy.types.Operator):
    bl_idname = "simple.create_house"
    bl_label = "Create House"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        create_house()
        self.report({'INFO'}, "House created!")
        return {'FINISHED'}

class SIMPLE_OT_CreateTree(bpy.types.Operator):
    bl_idname = "simple.create_tree"
    bl_label = "Create Tree"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        create_tree()
        self.report({'INFO'}, "Tree created!")
        return {'FINISHED'}

class SIMPLE_OT_CreateCar(bpy.types.Operator):
    bl_idname = "simple.create_car"
    bl_label = "Create Car"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        create_car()
        self.report({'INFO'}, "Car created!")
        return {'FINISHED'}

class SIMPLE_OT_CreateFromPrompt(bpy.types.Operator):
    bl_idname = "simple.create_from_prompt"
    bl_label = "Create from Prompt"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prompt = context.scene.simple_prompt.lower()
        
        if 'chair' in prompt:
            create_chair()
            msg = "Chair"
        elif 'table' in prompt:
            create_table()
            msg = "Table"
        elif 'house' in prompt:
            create_house()
            msg = "House"
        elif 'tree' in prompt:
            create_tree()
            msg = "Tree"
        elif 'car' in prompt:
            create_car()
            msg = "Car"
        elif 'sphere' in prompt or 'ball' in prompt:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
            bpy.context.object.name = 'Sphere'
            msg = "Sphere"
        elif 'cylinder' in prompt:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(0, 0, 1))
            bpy.context.object.name = 'Cylinder'
            msg = "Cylinder"
        elif 'cone' in prompt:
            bpy.ops.mesh.primitive_cone_add(radius1=1, depth=2, location=(0, 0, 1))
            bpy.context.object.name = 'Cone'
            msg = "Cone"
        else:
            bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
            bpy.context.object.name = 'Cube'
            msg = "Cube (default)"
        
        self.report({'INFO'}, f"{msg} created!")
        return {'FINISHED'}

class SIMPLE_OT_RunWithLLM(bpy.types.Operator):
    bl_idname = "simple.run_with_llm"
    bl_label = "Generate with LLM"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prompt = context.scene.simple_prompt
        model = context.scene.simple_model
        
        if not prompt:
            self.report({'ERROR'}, "Enter a prompt first!")
            return {'CANCELLED'}
        
        self.report({'INFO'}, "Calling Ollama...")
        
        try:
            # Call Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": f"Generate simple Blender Python code using ONLY bpy.ops.mesh.primitive_cube_add or bpy.ops.mesh.primitive_uv_sphere_add. Create: {prompt}. Return ONLY code in ```python blocks.",
                    "stream": False,
                    "options": {"num_predict": 256, "temperature": 0.1}
                },
                timeout=30
            )
            
            result = response.json().get("response", "")
            context.scene.simple_response = result
            
            # Try to extract and run code
            import re
            code_match = re.search(r'```python\s*(.*?)```', result, re.DOTALL)
            
            if code_match:
                code = code_match.group(1).strip()
                # Only allow safe operations
                if 'bpy.ops.mesh.primitive' in code:
                    exec(code, {'bpy': bpy})
                    self.report({'INFO'}, "Object created from LLM!")
                else:
                    self.report({'WARNING'}, "LLM code not safe, using template")
                    bpy.ops.simple.create_from_prompt()
            else:
                self.report({'WARNING'}, "No code found, using template")
                bpy.ops.simple.create_from_prompt()
                
        except Exception as e:
            self.report({'WARNING'}, f"LLM failed: {str(e)}, using template")
            bpy.ops.simple.create_from_prompt()
        
        return {'FINISHED'}

# ============================================
# UI PANEL
# ============================================

class VIEW3D_PT_SimplePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM AI"
    bl_label = "LLM 3D Generator"
    
    def draw(self, context):
        layout = self.layout
        
        # Quick Create Buttons
        box = layout.box()
        box.label(text="⚡ Quick Create (Click to Create)", icon='ADD')
        
        row = box.row(align=True)
        row.operator("simple.create_chair", text="Chair")
        row.operator("simple.create_table", text="Table")
        
        row = box.row(align=True)
        row.operator("simple.create_cube", text="Cube")
        row.operator("simple.create_sphere", text="Sphere")
        
        row = box.row(align=True)
        row.operator("simple.create_house", text="House")
        row.operator("simple.create_tree", text="Tree")
        
        row = box.row(align=True)
        row.operator("simple.create_car", text="Car")
        
        # Prompt Input
        box = layout.box()
        box.label(text="📝 Text Prompt", icon='TEXT')
        box.prop(context.scene, "simple_prompt", text="")
        
        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("simple.create_from_prompt", text="⚡ Create (Template)", icon='ADD')
        
        # LLM Section
        box = layout.box()
        box.label(text="🤖 LLM Settings", icon='SETTINGS')
        box.prop(context.scene, "simple_model", text="Model")
        
        row = box.row()
        row.scale_y = 1.3
        row.operator("simple.run_with_llm", text="🤖 Generate with LLM", icon='PLAY')
        
        # Response
        if context.scene.simple_response:
            box = layout.box()
            box.label(text="Response:", icon='TEXT')
            lines = context.scene.simple_response.split('\n')[:8]
            for line in lines:
                if len(line) > 40:
                    line = line[:37] + "..."
                box.label(text=line)

# ============================================
# REGISTRATION
# ============================================

classes = [
    SIMPLE_OT_CreateChair,
    SIMPLE_OT_CreateTable,
    SIMPLE_OT_CreateCube,
    SIMPLE_OT_CreateSphere,
    SIMPLE_OT_CreateHouse,
    SIMPLE_OT_CreateTree,
    SIMPLE_OT_CreateCar,
    SIMPLE_OT_CreateFromPrompt,
    SIMPLE_OT_RunWithLLM,
    VIEW3D_PT_SimplePanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.simple_prompt = StringProperty(name="Prompt", default="")
    bpy.types.Scene.simple_model = StringProperty(name="Model", default="llama3.1:8b")
    bpy.types.Scene.simple_response = StringProperty(name="Response", default="")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.simple_prompt
    del bpy.types.Scene.simple_model
    del bpy.types.Scene.simple_response

if __name__ == "__main__":
    register()
