"""
UI Module
User interface panels and property groups for the LLM addon
"""

import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty
)


# Property Group to store all LLM settings
class LLMPropertyGroup(PropertyGroup):
    """Property group for LLM settings"""
    
    # Provider selection
    llm_provider: EnumProperty(
        name="LLM Provider",
        description="Select LLM provider",
        items=[
            ('ollama', "Ollama (Local)", "Use local Ollama models"),
            ('openai', "OpenAI", "Use OpenAI GPT models"),
            ('gemini', "Gemini", "Use Google Gemini models"),
        ],
        default='ollama'
    )
    
    # Model selection - Ollama
    ollama_models: EnumProperty(
        name="Ollama Model",
        description="Select Ollama model",
        items=[
            ('llama3.1:8b', "Llama 3.1 8B", "Llama 3.1 8B model"),
            ('qwen2.5-coder:7b', "Qwen 2.5 Coder 7B", "Qwen 2.5 Coder 7B model"),
            ('codellama:7b', "CodeLlama 7B", "CodeLlama 7B model"),
            ('llama3.2', "Llama 3.2", "Llama 3.2 model"),
            ('mistral', "Mistral", "Mistral model"),
            ('deepseek-coder', "DeepSeek Coder", "DeepSeek Coder model"),
        ],
        default='llama3.1:8b'
    )
    
    # Model selection - OpenAI
    openai_models: EnumProperty(
        name="OpenAI Model",
        description="Select OpenAI model",
        items=[
            ('gpt-4', "GPT-4", "GPT-4 model"),
            ('gpt-4-turbo', "GPT-4 Turbo", "GPT-4 Turbo model"),
            ('gpt-3.5-turbo', "GPT-3.5 Turbo", "GPT-3.5 Turbo model"),
        ],
        default='gpt-4'
    )
    
    # Model selection - Gemini
    gemini_models: EnumProperty(
        name="Gemini Model",
        description="Select Gemini model",
        items=[
            ('gemini-pro', "Gemini Pro", "Gemini Pro model"),
            ('gemini-1.5-pro', "Gemini 1.5 Pro", "Gemini 1.5 Pro model"),
        ],
        default='gemini-pro'
    )
    
    # Selected model property (computed)
    @property
    def selected_model(self):
        if self.llm_provider == 'ollama':
            return self.custom_model if self.custom_model else self.ollama_models
        elif self.llm_provider == 'openai':
            return self.openai_models
        elif self.llm_provider == 'gemini':
            return self.gemini_models
        return ""
    
    # Custom model for Ollama
    custom_model: StringProperty(
        name="Custom Model",
        description="Enter custom Ollama model name (optional)",
        default=""
    )
    
    # System prompt
    system_prompt: StringProperty(
        name="System Prompt",
        description="System instructions for the LLM",
        default="Generate only Python code using bpy (Blender API). No explanations. Use ```python code blocks."
    )
    
    # User prompt
    user_prompt: StringProperty(
        name="Prompt",
        description="Enter your prompt (e.g., 'create a chair')",
        default=""
    )
    
    # Library imports
    library_imports: StringProperty(
        name="Library Imports",
        description="Additional library imports (optional)",
        default=""
    )
    
    # Options
    include_last_response: BoolProperty(
        name="Include Last Response",
        description="Include the last response in context",
        default=False
    )
    
    enhance_prompt: BoolProperty(
        name="Enhance Prompt with Steps",
        description="Automatically enhance prompt with step-by-step instructions",
        default=True
    )
    
    # Response storage
    llm_response: StringProperty(
        name="Response",
        description="LLM response",
        default=""
    )
    
    last_response: StringProperty(
        name="Last Response",
        description="Store last response for context",
        default=""
    )
    
    generated_code: StringProperty(
        name="Generated Code",
        description="Extracted Python code from response",
        default=""
    )


# Main UI Panel
class VIEW3D_PT_LLM_MainPanel(Panel):
    """Main LLM panel in 3D viewport sidebar"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LLM AI"
    bl_label = "LLM 3D Generator"
    bl_idname = "VIEW3D_PT_llm_main"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.llm_props
        
        # Provider Selection
        box = layout.box()
        box.label(text="LLM Provider", icon='NETWORK_DRIVE')
        box.prop(props, "llm_provider", text="")
        
        # Model Selection
        box = layout.box()
        box.label(text="Model Selection", icon='SETTINGS')
        
        if props.llm_provider == 'ollama':
            box.prop(props, "ollama_models", text="Select Model")
            box.prop(props, "custom_model", text="Custom Model (Optional)")
        elif props.llm_provider == 'openai':
            box.prop(props, "openai_models", text="Select Model")
            # Show warning if no API key
            preferences = context.preferences.addons[__package__].preferences
            if not preferences.openai_api_key:
                box.label(text="⚠ Set API key in preferences", icon='ERROR')
        elif props.llm_provider == 'gemini':
            box.prop(props, "gemini_models", text="Select Model")
            # Show warning if no API key
            preferences = context.preferences.addons[__package__].preferences
            if not preferences.gemini_api_key:
                box.label(text="⚠ Set API key in preferences", icon='ERROR')
        
        # System Prompt
        box = layout.box()
        box.label(text="System Prompt", icon='TEXT')
        box.prop(props, "system_prompt", text="")
        
        # User Prompt
        box = layout.box()
        box.label(text="Prompt", icon='OUTLINER_DATA_FONT')
        box.prop(props, "user_prompt", text="")
        
        # Library Imports (Optional)
        box = layout.box()
        box.label(text="Specify Library (Optional)", icon='PRESET')
        box.prop(props, "library_imports", text="")
        
        # Options
        box = layout.box()
        box.prop(props, "include_last_response", text="Include Last Response")
        box.prop(props, "enhance_prompt", text="Enhance Prompt with Steps")
        
        # Main Actions
        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 1.5
        row.operator("llm.run_and_execute", text="Run & Execute", icon='PLAY')
        
        row = box.row(align=True)
        row.operator("llm.send_prompt", text="Send Prompt (Preview)", icon='EXPORT')
        row.operator("llm.execute_response", text="Execute", icon='CONSOLE')
        
        # Response Display
        box = layout.box()
        box.label(text="Response", icon='TEXT')
        
        if props.llm_response:
            # Show response in a text box
            col = box.column(align=True)
            
            # Split response into lines for display
            response_lines = props.llm_response.split('\n')
            max_lines = 15
            
            for i, line in enumerate(response_lines[:max_lines]):
                if len(line) > 50:
                    line = line[:47] + "..."
                col.label(text=line)
            
            if len(response_lines) > max_lines:
                col.label(text="... (truncated)")
            
            # Action buttons
            row = box.row(align=True)
            row.operator("llm.copy_code", text="Copy Code", icon='COPYDOWN')
            row.operator("llm.clear_response", text="Clear", icon='X')
        else:
            box.label(text="No response yet", icon='INFO')
        
        # Run in Scripting Tab button
        if props.generated_code:
            layout.operator("llm.execute_response", text="Run Response in Scripting Tab", icon='CONSOLE')


# List of classes to register
classes = [
    LLMPropertyGroup,
    VIEW3D_PT_LLM_MainPanel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register property group
    bpy.types.Scene.llm_props = bpy.props.PointerProperty(type=LLMPropertyGroup)


def unregister():
    # Unregister property group
    del bpy.types.Scene.llm_props
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
