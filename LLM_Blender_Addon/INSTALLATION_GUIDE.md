# Installation and Setup Guide

## Step 1: Install the Addon

### Method 1: Direct Folder Installation
1. Copy the entire `LLM_Blender_Addon` folder to your Blender addons directory:
   - **Windows**: `C:\Users\<YourUsername>\AppData\Roaming\Blender Foundation\Blender\<version>\scripts\addons\`
   - **macOS**: `/Users/<YourUsername>/Library/Application Support/Blender/<version>/scripts/addons/`
   - **Linux**: `~/.config/blender/<version>/scripts/addons/`

2. Restart Blender
3. Go to `Edit > Preferences > Add-ons`
4. Search for "LLM"
5. Enable the addon by checking the checkbox

### Method 2: ZIP Installation
1. Zip the `LLM_Blender_Addon` folder
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...`
4. Select the ZIP file
5. Enable the addon

## Step 2: Install Python Dependencies

The addon requires the `requests` library. Blender usually includes it, but if you get import errors:

### Windows
```powershell
# Navigate to Blender's Python directory
cd "C:\Program Files\Blender Foundation\Blender <version>\<version>\python\bin"

# Install requests
.\python.exe -m pip install requests
```

### macOS/Linux
```bash
# Navigate to Blender's Python
cd /Applications/Blender.app/Contents/Resources/<version>/python/bin

# Install requests
./python3.10 -m pip install requests
```

## Step 3: Configure LLM Providers

### Option A: Ollama (Local - Recommended for beginners)

1. **Download and Install Ollama**
   - Visit [ollama.ai](https://ollama.ai)
   - Download for your OS
   - Install and run

2. **Pull a Model**
   ```bash
   ollama pull qwen2.5-coder:7b
   ```
   
   Other recommended models:
   ```bash
   ollama pull codellama:7b
   ollama pull llama3.2
   ollama pull deepseek-coder
   ```

3. **Verify Ollama is Running**
   - Ollama runs automatically after installation
   - Test: Open browser to `http://localhost:11434`
   - You should see "Ollama is running"

4. **In Blender**
   - The default settings should work
   - If needed, check server URL in `Edit > Preferences > Add-ons > LLM 3D Generator`

### Option B: OpenAI (Cloud-based)

1. **Get API Key**
   - Go to [platform.openai.com](https://platform.openai.com)
   - Sign up / Log in
   - Go to API Keys section
   - Create new secret key
   - Copy the key (you won't see it again!)

2. **Add to Blender**
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Find "LLM 3D Generator"
   - Expand the preferences
   - Paste your API key in "OpenAI API Key"
   - Click outside or press Enter to save

3. **Add Credits**
   - OpenAI requires payment
   - Add at least $5 to your account
   - Go to [platform.openai.com/account/billing](https://platform.openai.com/account/billing)

### Option C: Google Gemini (Cloud-based)

1. **Get API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with Google account
   - Click "Create API Key"
   - Copy the key

2. **Add to Blender**
   - Open Blender
   - Go to `Edit > Preferences > Add-ons`
   - Find "LLM 3D Generator"
   - Expand the preferences
   - Paste your API key in "Gemini API Key"
   - Save

3. **Note**
   - Gemini has a free tier with rate limits
   - Check [pricing](https://ai.google.dev/pricing) for details

## Step 4: First Use

1. **Open Blender**
2. Switch to any workspace (e.g., Layout)
3. In the 3D Viewport, press `N` to open the sidebar
4. Click on the "LLM AI" tab
5. Select your provider:
   - Choose "Ollama (Local)" if you set up Ollama
   - Choose "OpenAI" if you have an API key
   - Choose "Gemini" if you have a Google API key
6. Select a model from the dropdown
7. Enter a simple prompt: "create a cube"
8. Click "Run & Execute"

## Verification

If everything works correctly:
- ✅ A cube should appear in your 3D viewport
- ✅ The response section shows the LLM's output
- ✅ No error messages appear

## Common Issues

### "Module 'requests' not found"
- Install requests library (see Step 2)

### "Cannot connect to Ollama"
- Make sure Ollama is running
- Check if you can access `http://localhost:11434` in a browser
- On Mac/Linux, you may need to start Ollama manually: `ollama serve`

### "Invalid API key" (OpenAI/Gemini)
- Double-check you copied the full key
- Make sure there are no extra spaces
- Verify the key is active in your provider's dashboard

### "No executable code found"
- Enable "Enhance Prompt with Steps"
- Try a more specific prompt
- Check the Response section to see what the LLM returned

### Addon not appearing
- Make sure you enabled it in preferences
- Try restarting Blender
- Check Blender console for error messages (`Window > Toggle System Console` on Windows)

## Next Steps

Once installed and verified:
1. Try more complex prompts
2. Experiment with system prompts
3. Use "Send Prompt" to preview before execution
4. Check generated code in the Response section
5. Customize parameters for better results

## Support

For issues or questions:
1. Check the main README.md
2. Review the troubleshooting section
3. Check Blender console for detailed error messages
4. Verify your LLM provider is working outside of Blender
