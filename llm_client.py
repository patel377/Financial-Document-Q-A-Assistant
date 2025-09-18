# llm_client.py
import requests
import json

def ask_llm(prompt: str, llm_endpoint="http://localhost:11434/generate", model=None, max_tokens=512, temperature=0.0):
    """
    Generic LLM call. llm_endpoint should accept a POST with JSON like:
    { "model": "my-model", "prompt": "...", "max_tokens": 512, ... }
    If your local LLM (e.g., Ollama) has a different API, adapt this function.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(llm_endpoint, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        # Attempt common response formats:
        if isinstance(data, dict):
            # If Ollama-like: may return {"results": [{"content": "..."}]} or {"text": "..."}
            if "results" in data and isinstance(data["results"], list) and data["results"]:
                return data["results"][0].get("content") or data["results"][0].get("text") or str(data)
            if "text" in data:
                return data["text"]
            if "output" in data:
                return data["output"]
            # last fallback:
            return json.dumps(data)
        else:
            return str(data)
    except Exception as e:
        return f"Error calling LLM endpoint: {e}"
