# Troubleshooting Guide

## Problem: "Nothing appears in viewport" when using complex prompts

### Why This Happens:
When you write "create a chair and table", the LLM might:
1. Return explanatory text instead of code
2. Generate incomplete code
3. Use incorrect Blender API syntax

### Solutions:

#### ✅ Solution 1: Always Enable "Enhance Prompt with Steps"
- Check the box: **"Enhance Prompt with Steps"**
- This adds examples and clear instructions to your prompt
- The LLM will understand better what code format to use

#### ✅ Solution 2: Use Better Prompts
**Instead of:** "create a chair and table"
**Try:**
- "Generate Python code to create a cube as chair seat at position (0,0,0.5) and another cube as table at position (3,0,1)"
- "Make a simple chair using cubes"
- "Create 2 cubes: one for chair, one for table"

**Simple prompts that work well:**
- "create a cube"
- "make a sphere"
- "add a cylinder"
- "create 3 cubes in a row"

#### ✅ Solution 3: Check the Response
After clicking "Run & Execute":
1. Look at the **Response** section in the panel
2. Check if there's Python code in the response
3. If you see explanations instead of code, try Solution 1

#### ✅ Solution 4: Use Send Prompt First
1. Click **"Send Prompt (Preview)"** instead of "Run & Execute"
2. Check the response
3. If you see code with ```python blocks, click **"Execute"**
4. If not, modify your prompt and try again

#### ✅ Solution 5: Check Blender Console
- **Windows**: `Window > Toggle System Console`
- Look for errors or the printed code
- You'll see the exact code being executed

## Problem: Simple object names work but complex requests don't

### Why This Works:
When you type just "cube" or "sphere", the system recognizes simple objects and can create basic primitives directly.

### Why Complex Prompts Fail:
Complex requests like "chair and table" require the LLM to generate proper code. If the LLM:
- Doesn't understand the format needed
- Returns text explanations instead of code
- Uses wrong API syntax

Then nothing appears.

### Fix:
Use the solutions above, especially:
- **Enable "Enhance Prompt with Steps"**
- **Use more specific prompts**

## Recommended Settings for Best Results

### For Ollama (Llama 3.1):
```
Provider: Ollama (Local)
Model: Llama 3.1 8B
System Prompt: "Generate only Python code using bpy (Blender API). No explanations. Use ```python code blocks."
✓ Enhance Prompt with Steps: CHECKED
```

### Example Good Prompts:
1. **Simple objects:**
   - "create a cube"
   - "add a sphere"
   - "make a cylinder"

2. **Multiple objects:**
   - "create 3 cubes in different positions"
   - "make a cube and a sphere"
   - "add 5 spheres in a row"

3. **More complex (with enhancement enabled):**
   - "create a simple chair using cubes"
   - "make a basic table"
   - "create a house structure"

## Debug Checklist

When something doesn't work:

- [ ] Is "Enhance Prompt with Steps" **checked**?
- [ ] Did you use a clear, specific prompt?
- [ ] Did you check the Response section for code?
- [ ] Is Ollama running? (for local models)
- [ ] Did you check Blender console for errors?
- [ ] Try "Send Prompt" first to preview the response

## Understanding the Response

### ✅ Good Response (will work):
```python
import bpy
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
bpy.context.active_object.name = 'Chair'
```

### ❌ Bad Response (won't work):
```
To create a chair and table in Blender, you should use the following approach:
First, think about the chair design...
[lots of text without code]
```

## Still Not Working?

### Try This Test:
1. Set prompt to: **"create a cube"**
2. Check: **"Enhance Prompt with Steps"**
3. Click: **"Run & Execute"**
4. **Expected:** A cube appears in the viewport

If this works, your setup is fine. Use better prompts for complex objects.

If this doesn't work:
- Check Blender console for errors
- Verify Ollama is running (for local models)
- Check API keys (for cloud models)
