import json
import os
from openai import OpenAI

CONFIG_PATH = "config.json"

def get_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Missing {CONFIG_PATH}. Please provide it with your OPENAI_API_KEY.")
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    defaults = {
        "MODEL": "gpt-4o-mini",
        "TEMPERATURE_ANALYSIS": 0.2,
        "TEMPERATURE_GENERATION": 0.7,
        "PORT": 8000
    }
    
    needs_update = False
    for k, v in defaults.items():
        if k not in config:
            config[k] = v
            needs_update = True
            
    if needs_update:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
    return config

def get_openai_client() -> OpenAI:
    config = get_config()
    api_key = config.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is empty in config.json. Please add your key.")
    
    return OpenAI(api_key=api_key)

def build_chat_kwargs(config: dict, messages: list, temp_key: str, response_format: dict = None) -> dict:
    """Safely builds kwargs for the OpenAI client, omitting temperature if it's 1 or unsupported."""
    kwargs = {
        "model": config.get("MODEL", "gpt-4o-mini"),
        "messages": messages
    }
    if response_format:
        kwargs["response_format"] = response_format
        
    temp = config.get(temp_key)
    model_name = str(kwargs.get("model", "")).lower()
    
    # Advanced reasoning models (like o1, o3, gpt-5) do not support explicit temperature floats.
    is_reasoning_model = any(x in model_name for x in ["o1", "o3", "gpt-5"])
    
    if is_reasoning_model:
        # Strictly omit temperature for reasoning models regardless of config value
        pass
    elif temp is not None and temp != 1 and temp != 1.0:
        kwargs["temperature"] = temp
        
    return kwargs
