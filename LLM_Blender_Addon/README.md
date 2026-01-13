# LLM 3D Generator - Blender Addon

A comprehensive Blender addon that integrates both local (Ollama) and cloud-based (OpenAI, Gemini) LLM models to generate 3D scenes directly from text prompts.

## Features

- 🤖 **Multiple LLM Providers**: Support for Ollama (local), OpenAI, and Google Gemini
- 🎨 **Direct 3D Generation**: Generate 3D objects and scenes directly in Blender viewport
- 💻 **Python Script Generation**: Automatically generates reusable Python scripts
- ⚙️ **Customizable Parameters**: System prompts, library imports, and enhancement options
- 🔑 **Secure API Management**: Store API keys securely in addon preferences
- 📝 **Response Preview**: Preview LLM responses before execution

## Installation

1. Download or clone this repository
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...` and select the `LLM_Blender_Addon` folder (or zip it first)
4. Enable the addon by checking the checkbox next to "LLM 3D Generator"

## Setup

### For Ollama (Local)
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull your desired model: `ollama pull qwen2.5-coder:7b`
3. Make sure Ollama is running (it runs automatically on startup)

### For OpenAI
1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. In Blender: `Edit > Preferences > Add-ons > LLM 3D Generator`
3. Enter your OpenAI API key

### For Google Gemini
1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. In Blender: `Edit > Preferences > Add-ons > LLM 3D Generator`
3. Enter your Gemini API key

## Usage

1. Open Blender and switch to the 3D Viewport
2. Press `N` to open the sidebar
3. Click on the "LLM AI" tab
4. Select your LLM provider (Ollama/OpenAI/Gemini)
5. Choose a model from the dropdown
6. (Optional) Enter a system prompt
7. Enter your prompt (e.g., "create a chair")
8. Click "Run & Execute" to generate and create the 3D scene

## Interface Elements

- **LLM Provider**: Choose between Ollama, OpenAI, or Gemini
- **Model Selection**: Select from available models for each provider
- **Custom Model** (Ollama only): Override with a custom model name
- **System Prompt**: Instructions for the LLM behavior
- **Prompt**: Your main request (e.g., "create a table")
- **Specify Library**: Optional Python imports (e.g., "import random")
- **Include Last Response**: Use previous response as context
- **Enhance Prompt with Steps**: Auto-add detailed instructions
- **Run & Execute**: Generate and immediately create in viewport
- **Send Prompt**: Get response without execution
- **Execute**: Run the generated code
- **Response**: View the LLM's response
- **Copy Code**: Copy generated Python code to clipboard

## Example Prompts

- "create a chair"
- "make a table with 4 legs"
- "generate a sphere with a smooth material"
- "create a simple house with a roof"
- "make a tree with branches"

## File Structure

```
LLM_Blender_Addon/
├── __init__.py           # Main addon entry point
├── preferences.py        # API key management and settings
├── ui.py                # User interface panels
├── operators.py         # Button actions and operations
├── llm_integration.py   # LLM API calls (Ollama, OpenAI, Gemini)
├── scene_generator.py   # 3D scene generation and script execution
└── README.md           # This file
```

## Requirements

- Blender 3.0 or higher
- Python `requests` library (usually included with Blender)
- For Ollama: Ollama installed and running locally
- For OpenAI: Valid API key with credits
- For Gemini: Valid Google API key

## Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is installed and running
- Check the server URL in preferences (default: http://localhost:11434)

### "Invalid API key" (OpenAI/Gemini)
- Verify your API key in addon preferences
- Ensure you have credits/quota available

### "No executable Python code found"
- Try enabling "Enhance Prompt with Steps"
- Make your prompt more specific
- Add context in the system prompt

## License

This addon is provided as-is for educational and commercial use.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Credits

Created for Master Thesis project - LLM Integration in 3D Modeling Software
