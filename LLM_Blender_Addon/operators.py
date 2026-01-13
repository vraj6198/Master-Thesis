"""
Operators Module
Blender operators for LLM integration actions
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from . import llm_integration
from . import scene_generator


class LLM_OT_RunAndExecute(Operator):
    """Run LLM prompt and execute generated code in Blender viewport"""
    bl_idname = "llm.run_and_execute"
    bl_label = "Run & Execute"
    bl_description = "Generate and execute 3D scene from LLM"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        props = scene.llm_props
        
        # Validate inputs
        if not props.user_prompt:
            self.report({'ERROR'}, "Please enter a prompt")
            return {'CANCELLED'}
        
        # Check API key for cloud providers
        preferences = context.preferences.addons[__package__].preferences
        
        if props.llm_provider == 'openai' and not preferences.openai_api_key:
            self.report({'ERROR'}, "Please set OpenAI API key in addon preferences")
            return {'CANCELLED'}
        
        if props.llm_provider == 'gemini' and not preferences.gemini_api_key:
            self.report({'ERROR'}, "Please set Gemini API key in addon preferences")
            return {'CANCELLED'}
        
        # Prepare prompt
        prompt = props.user_prompt
        if props.enhance_prompt:
            prompt = scene_generator.SceneGenerator.generate_enhanced_prompt(
                props.user_prompt, 
                with_steps=True
            )
        
        # Get system prompt
        system_prompt = props.system_prompt
        
        # Get API key based on provider
        api_key = ""
        if props.llm_provider == 'openai':
            api_key = preferences.openai_api_key
        elif props.llm_provider == 'gemini':
            api_key = preferences.gemini_api_key
        
        # Get model
        model = props.selected_model
        custom_model = props.custom_model if props.llm_provider == 'ollama' else ""
        
        # Call LLM
        self.report({'INFO'}, f"Calling {props.llm_provider.upper()}...")
        success, response = llm_integration.get_llm_response(
            provider=props.llm_provider,
            prompt=prompt,
            model=model,
            api_key=api_key,
            system_prompt=system_prompt,
            custom_model=custom_model
        )
        
        if not success:
            self.report({'ERROR'}, response)
            props.llm_response = response
            return {'CANCELLED'}
        
        # Store response
        props.llm_response = response
        
        # Add to history if enabled
        if props.include_last_response:
            props.last_response = response
        
        # Process and execute response
        exec_success, message, code = scene_generator.process_llm_response(
            response,
            library_imports=props.library_imports
        )
        
        if exec_success:
            self.report({'INFO'}, message)
            if code:
                props.generated_code = code
        else:
            self.report({'WARNING'}, message)
        
        return {'FINISHED'}


class LLM_OT_SendPrompt(Operator):
    """Send prompt to LLM and get response (without execution)"""
    bl_idname = "llm.send_prompt"
    bl_label = "Send Prompt"
    bl_description = "Send prompt to LLM and receive response"
    
    def execute(self, context):
        scene = context.scene
        props = scene.llm_props
        
        if not props.user_prompt:
            self.report({'ERROR'}, "Please enter a prompt")
            return {'CANCELLED'}
        
        # Check API key for cloud providers
        preferences = context.preferences.addons[__package__].preferences
        
        if props.llm_provider == 'openai' and not preferences.openai_api_key:
            self.report({'ERROR'}, "Please set OpenAI API key in addon preferences")
            return {'CANCELLED'}
        
        if props.llm_provider == 'gemini' and not preferences.gemini_api_key:
            self.report({'ERROR'}, "Please set Gemini API key in addon preferences")
            return {'CANCELLED'}
        
        # Prepare prompt
        prompt = props.user_prompt
        if props.enhance_prompt:
            prompt = scene_generator.SceneGenerator.generate_enhanced_prompt(
                props.user_prompt,
                with_steps=True
            )
        
        # Get API key
        api_key = ""
        if props.llm_provider == 'openai':
            api_key = preferences.openai_api_key
        elif props.llm_provider == 'gemini':
            api_key = preferences.gemini_api_key
        
        # Get model
        model = props.selected_model
        custom_model = props.custom_model if props.llm_provider == 'ollama' else ""
        
        # Call LLM
        self.report({'INFO'}, f"Calling {props.llm_provider.upper()}...")
        success, response = llm_integration.get_llm_response(
            provider=props.llm_provider,
            prompt=prompt,
            model=model,
            api_key=api_key,
            system_prompt=props.system_prompt,
            custom_model=custom_model
        )
        
        if success:
            props.llm_response = response
            if props.include_last_response:
                props.last_response = response
            
            # Extract code if present
            code = scene_generator.SceneGenerator.extract_python_code(response)
            if code:
                props.generated_code = code
            
            self.report({'INFO'}, "Response received")
        else:
            props.llm_response = response
            self.report({'ERROR'}, response)
        
        return {'FINISHED'}


class LLM_OT_ExecuteResponse(Operator):
    """Execute the LLM response in Blender"""
    bl_idname = "llm.execute_response"
    bl_label = "Run Response in Scripting Tab"
    bl_description = "Execute the generated code from LLM response"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        props = scene.llm_props
        
        if not props.llm_response:
            self.report({'ERROR'}, "No response to execute")
            return {'CANCELLED'}
        
        # Process and execute
        success, message, code = scene_generator.process_llm_response(
            props.llm_response,
            library_imports=props.library_imports
        )
        
        if success:
            self.report({'INFO'}, message)
            if code:
                props.generated_code = code
        else:
            self.report({'ERROR'}, message)
        
        return {'FINISHED'}


class LLM_OT_ClearResponse(Operator):
    """Clear the LLM response"""
    bl_idname = "llm.clear_response"
    bl_label = "Clear Response"
    bl_description = "Clear the response text"
    
    def execute(self, context):
        context.scene.llm_props.llm_response = ""
        return {'FINISHED'}


class LLM_OT_CopyCode(Operator):
    """Copy generated code to clipboard"""
    bl_idname = "llm.copy_code"
    bl_label = "Copy Code"
    bl_description = "Copy generated Python code to clipboard"
    
    def execute(self, context):
        props = context.scene.llm_props
        if props.generated_code:
            context.window_manager.clipboard = props.generated_code
            self.report({'INFO'}, "Code copied to clipboard")
        else:
            self.report({'WARNING'}, "No code to copy")
        return {'FINISHED'}


# List of classes to register
classes = [
    LLM_OT_RunAndExecute,
    LLM_OT_SendPrompt,
    LLM_OT_ExecuteResponse,
    LLM_OT_ClearResponse,
    LLM_OT_CopyCode,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
