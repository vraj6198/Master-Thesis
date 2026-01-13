"""
LLM Integration Module
Handles communication with Ollama, OpenAI, and Gemini APIs
"""

import json
import requests
from typing import Dict, Optional, Tuple


class LLMIntegration:
    """Main class for LLM API integration"""
    
    @staticmethod
    def call_ollama(prompt: str, model: str, system_prompt: str = "", 
                    custom_model: str = "", server_url: str = "http://localhost:11434") -> Tuple[bool, str]:
        """
        Call Ollama local API
        
        Args:
            prompt: User prompt
            model: Model name
            system_prompt: System instructions
            custom_model: Custom model override
            server_url: Ollama server URL
            
        Returns:
            Tuple of (success: bool, response: str)
        """
        try:
            model_to_use = custom_model if custom_model else model
            
            url = f"{server_url}/api/generate"
            payload = {
                "model": model_to_use,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return True, result.get("response", "")
            
        except requests.exceptions.ConnectionError:
            return False, "Error: Cannot connect to Ollama. Make sure Ollama is running."
        except requests.exceptions.Timeout:
            return False, "Error: Request timed out. The model may be too slow."
        except Exception as e:
            return False, f"Error calling Ollama: {str(e)}"
    
    @staticmethod
    def call_openai(prompt: str, model: str, api_key: str, 
                    system_prompt: str = "") -> Tuple[bool, str]:
        """
        Call OpenAI API
        
        Args:
            prompt: User prompt
            model: Model name (e.g., gpt-4, gpt-3.5-turbo)
            api_key: OpenAI API key
            system_prompt: System instructions
            
        Returns:
            Tuple of (success: bool, response: str)
        """
        try:
            if not api_key:
                return False, "Error: OpenAI API key is required"
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return True, result["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return False, "Error: Invalid API key"
            elif e.response.status_code == 429:
                return False, "Error: Rate limit exceeded"
            else:
                return False, f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            return False, f"Error calling OpenAI: {str(e)}"
    
    @staticmethod
    def call_gemini(prompt: str, model: str, api_key: str, 
                    system_prompt: str = "") -> Tuple[bool, str]:
        """
        Call Google Gemini API
        
        Args:
            prompt: User prompt
            model: Model name (e.g., gemini-pro)
            api_key: Google API key
            system_prompt: System instructions
            
        Returns:
            Tuple of (success: bool, response: str)
        """
        try:
            if not api_key:
                return False, "Error: Gemini API key is required"
            
            # Gemini API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from Gemini response structure
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    return True, text
            
            return False, "Error: Unexpected response format from Gemini"
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                return False, "Error: Invalid API key or request"
            elif e.response.status_code == 429:
                return False, "Error: Rate limit exceeded"
            else:
                return False, f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            return False, f"Error calling Gemini: {str(e)}"


def get_llm_response(provider: str, prompt: str, model: str, api_key: str = "",
                     system_prompt: str = "", custom_model: str = "") -> Tuple[bool, str]:
    """
    Get response from specified LLM provider
    
    Args:
        provider: 'ollama', 'openai', or 'gemini'
        prompt: User prompt
        model: Model name
        api_key: API key for cloud providers
        system_prompt: System instructions
        custom_model: Custom model for Ollama
        
    Returns:
        Tuple of (success: bool, response: str)
    """
    llm = LLMIntegration()
    
    if provider == "ollama":
        return llm.call_ollama(prompt, model, system_prompt, custom_model)
    elif provider == "openai":
        return llm.call_openai(prompt, model, api_key, system_prompt)
    elif provider == "gemini":
        return llm.call_gemini(prompt, model, api_key, system_prompt)
    else:
        return False, f"Error: Unknown provider '{provider}'"
