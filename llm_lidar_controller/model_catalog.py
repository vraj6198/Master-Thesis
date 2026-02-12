OLLAMA_MODELS = [
    ("OLLAMA_QWEN_2_5_CODER_7B", "qwen2.5-coder:7b"),
    ("OLLAMA_LLAMA_3_2_LATEST", "llama3.2:latest"),
    ("OLLAMA_LLAMA_3_1_8B", "llama3.1:8b"),
    ("OLLAMA_DEEPSEEK_CODER_V2_16B", "deepseek-coder-v2:16b"),
    ("OLLAMA_MISTRAL_7B", "mistral:7b"),
    ("OLLAMA_PHI4_LATEST", "phi4:latest"),
    ("OLLAMA_CODELLAMA_13B", "codellama:13b"),
    ("OLLAMA_GEMMA2_9B", "gemma2:9b"),
    ("OLLAMA_STARCODER2_7B", "starcoder2:7b"),
]

OPENAI_MODELS = [
    ("OPENAI_GPT_4O", "gpt-4o"),
    ("OPENAI_GPT_4O_MINI", "gpt-4o-mini"),
    ("OPENAI_GPT_4_1", "gpt-4.1"),
    ("OPENAI_GPT_4_1_MINI", "gpt-4.1-mini"),
    ("OPENAI_GPT_4_1_NANO", "gpt-4.1-nano"),
    ("OPENAI_GPT_3_5_TURBO", "gpt-3.5-turbo"),
]

GEMINI_MODELS = [
    ("GEMINI_3_PRO", "gemini-3-pro"),
    ("GEMINI_2_5_PRO", "gemini-2.5-pro"),
    ("GEMINI_2_5_FLASH", "gemini-2.5-flash"),
    ("GEMINI_2_0_PRO", "gemini-2.0-pro"),
    ("GEMINI_2_0_FLASH", "gemini-2.0-flash"),
    ("GEMINI_1_5_FLASH", "gemini-1.5-flash"),
    ("GEMINI_1_5_FLASH_8B", "gemini-1.5-flash-8b"),
    ("GEMINI_1_5_PRO", "gemini-1.5-pro"),
]

CUSTOM_ID = "CUSTOM"
DEFAULT_MODEL_ID = OLLAMA_MODELS[0][0]

ALL_MODELS = OLLAMA_MODELS + OPENAI_MODELS + GEMINI_MODELS
ALL_ITEMS = [(model_id, label, "") for model_id, label in ALL_MODELS] + [
    (CUSTOM_ID, "Custom", "Use a custom model name"),
]


def _model_list_for(provider):
    if provider == "OPENAI":
        return OPENAI_MODELS
    if provider == "GEMINI":
        return GEMINI_MODELS
    return OLLAMA_MODELS


def get_items(provider=None):
    if provider:
        items = [(model_id, label, "") for model_id, label in _model_list_for(provider)]
        items.append((CUSTOM_ID, "Custom", "Use a custom model name"))
        return items
    return list(ALL_ITEMS)


def resolve_model(provider, model_id, custom_value):
    lookup = {mid: label for mid, label in ALL_MODELS}
    if model_id == CUSTOM_ID:
        return custom_value.strip() if custom_value else OLLAMA_MODELS[0][1]
    return lookup.get(model_id, OLLAMA_MODELS[0][1])
