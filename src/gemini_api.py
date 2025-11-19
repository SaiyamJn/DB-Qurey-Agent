import requests
from config import GEMINI_API_KEY, MODEL_PRIORITY

def call_gemini(model_name, system_prompt, user_prompt):
    """Call Gemini API with error handling"""
    if not GEMINI_API_KEY:
        return -1, {"error": "API key not configured"}
    
    url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"parts": [{"text": system_prompt + "\n\nUSER:\n" + user_prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
    }
    
    try:
        response = requests.post(url, json=body, timeout=30)
        return response.status_code, response.json()
    except requests.exceptions.Timeout:
        return -1, {"error": "Request timeout"}
    except Exception as e:
        return -1, {"error": str(e)}


def call_gemini_auto(system_prompt, user_prompt):
    """Auto-fallback through model list"""
    for model in MODEL_PRIORITY:
        status, response = call_gemini(model, system_prompt, user_prompt)
        
        if status == 200 and isinstance(response, dict):
            try:
                text = response["candidates"][0]["content"]["parts"][0]["text"]
                return model, text
            except (KeyError, IndexError):
                continue
        
        if status in [500, 503]:  # Server errors, try next model
            continue
    
    return None, "<chat>All models unavailable. Please check your API key and try again.</chat>"