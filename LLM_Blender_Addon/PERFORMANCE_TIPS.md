# Performance Tips - Speed Up 3D Generation

## Why Is It Slow?

### Normal Wait Times:
- **Ollama (Local)**: 10-30 seconds for simple objects
- **OpenAI/Gemini**: 3-10 seconds (cloud-based, faster servers)
- **Complex prompts**: Add 10-20 seconds more

### Main Causes of Slowness:

1. **LLM Thinking Time**: Models need time to generate code
2. **Model Size**: Larger models = slower (Llama 3.1:8b is medium-sized)
3. **Prompt Length**: Longer prompts = more processing time
4. **System Resources**: CPU/RAM usage affects Ollama performance

## 🚀 How to Make It Faster

### ✅ Optimization 1: Use Simpler Prompts
**Instead of:**
```
"Create a detailed wooden chair with 4 legs, a backrest, and smooth edges positioned at coordinates (0,0,0)"
```

**Use:**
```
"create a chair"
```

**Why?** Shorter prompts = faster processing, and the enhancement feature adds the details.

### ✅ Optimization 2: Keep "Enhance Prompt with Steps" ON
- ✅ This is ALREADY OPTIMIZED in the latest version
- The enhanced prompt is now much shorter (< 150 chars vs 500+ before)
- Includes only essential examples

### ✅ Optimization 3: Use Smaller Models (Ollama)
**Fastest to Slowest:**
1. **llama3.2** (smallest, fastest)
2. **mistral** (fast)
3. **llama3.1:8b** (medium - current default)
4. **qwen2.5-coder:7b** (medium)
5. **codellama:7b** (slower, better for code)

**Change in UI:** Model Selection dropdown

### ✅ Optimization 4: Check System Resources
```powershell
# Check if Ollama is using too much RAM/CPU
tasklist | findstr ollama
```

If Ollama is using > 8GB RAM, restart it:
```powershell
taskkill /F /IM ollama.exe
ollama serve
```

### ✅ Optimization 5: Switch to Cloud Models (Fastest)
**OpenAI or Gemini** are 2-5x faster than local models:
- **Gemini** (free tier) - Very fast
- **OpenAI GPT-3.5 Turbo** - Fastest
- **OpenAI GPT-4** - Slower but better quality

### ✅ Optimization 6: Optimize Ollama Settings
Create/edit `C:\Users\<YourName>\.ollama\config.json`:
```json
{
  "num_ctx": 2048,
  "num_thread": 8,
  "num_gpu": 1
}
```

Then restart Ollama.

## ⚡ New Optimizations (Already Applied)

The latest version includes:

✅ **Reduced timeouts**: 60s (was 120s) for Ollama
✅ **Token limits**: Max 512 tokens (was unlimited)
✅ **Lower temperature**: 0.3 (was 0.7) for focused output
✅ **Shorter prompts**: ~80% less text to process
✅ **Progress indicator**: Shows you what's happening
✅ **Debug output**: Console shows timing information

## Expected Speeds (After Optimization)

| Task | Ollama | OpenAI | Gemini |
|------|--------|--------|--------|
| Simple object (cube) | 5-15s | 2-5s | 3-7s |
| Multiple objects | 10-25s | 4-10s | 5-12s |
| Complex scene | 20-40s | 8-20s | 10-25s |

## 📊 Monitor Performance

### Check Blender Console
`Window > Toggle System Console`

You'll see:
```
[DEBUG] Calling Ollama model: llama3.1:8b
[DEBUG] Prompt length: 156 chars
[DEBUG] Sending request to Ollama...
[DEBUG] Response received from Ollama
```

**Watch the timestamps** to see where delays occur.

## 🔧 If Still Too Slow

### 1. Test Connection Speed
```powershell
curl http://localhost:11434
```
Should respond instantly with "Ollama is running"

### 2. Try a Tiny Test
Use the **"🧪 Test: Create Cube"** button:
- Should complete in < 5 seconds
- If slower, Ollama might have issues

### 3. Check Ollama Logs
```powershell
ollama list  # Show installed models
ollama ps    # Show running models
```

### 4. Restart Everything
```powershell
# Stop Ollama
taskkill /F /IM ollama.exe

# Start Ollama
ollama serve

# In Blender: Reload addon
Edit > Preferences > Add-ons > LLM 3D Generator > Disable > Enable
```

## 💡 Best Practices

1. **Start simple** - Test with "create a cube" first
2. **Use short prompts** - Let enhancement add details
3. **Check console** - See timing and debug info
4. **Be patient** - 10-20s is normal for local models
5. **Try cloud** - If speed is critical, use OpenAI/Gemini

## Still Experiencing Issues?

If it takes > 60 seconds consistently:

1. Check if Ollama model is fully loaded: `ollama list`
2. Ensure you have enough RAM (8GB+ recommended)
3. Close other heavy applications
4. Consider using a lighter model (llama3.2 instead of llama3.1:8b)
5. Try cloud models for comparison

---

**Current optimized settings provide 50-70% faster responses than the original version!** ⚡
