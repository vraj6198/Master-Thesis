import bpy
from bpy.types import Panel


class SCENEGEN_PT_main_panel(Panel):
    """Main panel for SceneGen add-on."""
    
    bl_label = "SceneGen"
    bl_idname = "SCENEGEN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SceneGen"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.scene_gen
        
        # User Prompt Section
        layout.label(text="User Prompt:")
        layout.prop(props, "user_prompt", text="")
        
        layout.separator()
        
        # Action Buttons
        row = layout.row(align=True)
        row.operator("scene_gen.generate_json", text="Generate JSON", icon='FILE_TEXT')
        row.operator("scene_gen.validate_json", text="Validate", icon='CHECKMARK')
        
        row = layout.row(align=True)
        row.operator("scene_gen.build_scene", text="Build Scene", icon='MESH_CUBE')
        row.operator("scene_gen.clear_scene", text="Clear", icon='TRASH')
        
        layout.separator()
        
        # JSON Spec Text Area
        layout.label(text="JSON Specification:")
        box = layout.box()
        col = box.column()
        
        # Display JSON in multiple lines (split by newlines)
        json_text = props.json_spec
        if json_text:
            lines = json_text.split('\n')
            for line in lines[:30]:  # Limit display lines
                col.label(text=line[:80])  # Limit line length
            if len(lines) > 30:
                col.label(text="... (truncated)")
        else:
            col.label(text="(No JSON yet)")
        
        layout.separator()
        
        # Log Output
        layout.label(text="Log Output:")
        box = layout.box()
        col = box.column()
        
        log_text = props.log_output
        if log_text:
            lines = log_text.split('\n')
            for line in lines[:10]:
                col.label(text=line[:80])
        else:
            col.label(text="(No log messages)")


def register():
    bpy.utils.register_class(SCENEGEN_PT_main_panel)


def unregister():
    bpy.utils.unregister_class(SCENEGEN_PT_main_panel)
