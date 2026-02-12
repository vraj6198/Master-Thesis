import json
import urllib.request
from urllib.parse import quote

from . import model_catalog
from . import utils


SYSTEM_PROMPT = (
    "You are controlling the BLAINDER Range Scanner add-on in Blender. "
    "Return ONLY a JSON object that is a JSON Merge Patch for the base config. "
    "Do not include explanations, code fences, or extra text. "
    "Only use keys that already exist in the base config. "
    "Use degrees for rotation_euler_deg, and numeric values for scanner parameters."
)


def build_prompts(base_config, user_command):
    base_text = json.dumps(base_config, indent=2, sort_keys=True)
    user_prompt = (
        "Base config (JSON):\n"
        f"{base_text}\n\n"
        "User command:\n"
        f"{user_command}\n\n"
        "Output the JSON patch now."
    )
    full_prompt = SYSTEM_PROMPT + "\n\n" + user_prompt
    return SYSTEM_PROMPT, user_prompt, full_prompt


def call_ollama(endpoint, model, prompt, timeout_sec):
    endpoint = _strip_and_validate("Ollama endpoint", endpoint)
    model = _strip_and_validate("Ollama model", model)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read().decode("utf-8")
    result = json.loads(raw)
    return result.get("response", ""), raw


def call_openai_compat(endpoint, model, system_prompt, user_prompt, api_key, timeout_sec):
    endpoint = _strip_and_validate("OpenAI endpoint", endpoint)
    model = _strip_and_validate("OpenAI model", model)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read().decode("utf-8")
    result = json.loads(raw)
    choice = result.get("choices", [{}])[0]
    message = choice.get("message", {})
    return message.get("content", ""), raw


def _strip_and_validate(label, value):
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"{label} is required.")
    if any(ch.isspace() for ch in cleaned):
        raise ValueError(f"{label} contains whitespace or control characters.")
    return cleaned


def call_gemini(endpoint_base, model, prompt, api_key, timeout_sec):
    endpoint_base = _strip_and_validate("Gemini endpoint", endpoint_base)
    api_key = _strip_and_validate("Gemini API key", api_key)
    model = _strip_and_validate("Gemini model", model)
    endpoint_base = endpoint_base.rstrip("/")
    model_safe = quote(model, safe="._-")
    endpoint = f"{endpoint_base}/{model_safe}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {"temperature": 0.0},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        raw = resp.read().decode("utf-8")
    result = json.loads(raw)
    candidates = result.get("candidates", [])
    if not candidates:
        return "", raw
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return "", raw
    return parts[0].get("text", ""), raw


def resolve_model(prefs, fallback):
    if not prefs:
        return fallback
    provider = prefs.llm_provider or "OLLAMA_LOCAL"
    model_id = prefs.llm_model or model_catalog.DEFAULT_MODEL_ID
    custom = prefs.llm_custom_model or ""
    return model_catalog.resolve_model(provider, model_id, custom).strip()


def generate_patch(settings, base_config, user_command):
    prefs = utils.get_addon_prefs()
    system_prompt, user_prompt, full_prompt = build_prompts(base_config, user_command)

    provider = prefs.llm_provider if prefs else "OLLAMA_LOCAL"
    model = resolve_model(prefs, "qwen2.5-coder:7b")
    timeout_sec = prefs.llm_timeout if prefs else 60

    if provider == "OPENAI":
        endpoint = prefs.llm_endpoint_openai
        api_key = prefs.llm_api_key_openai
        if not api_key:
            raise ValueError("OpenAI API key is required.")
        text, raw = call_openai_compat(endpoint, model, system_prompt, user_prompt, api_key, timeout_sec)
    elif provider == "GEMINI":
        endpoint = prefs.llm_endpoint_gemini
        prompt = system_prompt + "\n\n" + user_prompt
        text, raw = call_gemini(endpoint, model, prompt, prefs.llm_api_key_gemini, timeout_sec)
    elif provider == "OPENAI_COMPAT":
        endpoint = prefs.llm_endpoint_openai
        api_key = prefs.llm_api_key_openai
        text, raw = call_openai_compat(endpoint, model, system_prompt, user_prompt, api_key, timeout_sec)
    else:
        endpoint = prefs.llm_endpoint_ollama
        text, raw = call_ollama(endpoint, model, full_prompt, timeout_sec)

    patch, patch_text = utils.extract_json_from_text(text)
    return patch, patch_text, raw
