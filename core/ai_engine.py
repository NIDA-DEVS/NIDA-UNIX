import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def generate_command(prompt: str, model: str = "llama2") -> str:
    try:
        payload = {
            "model": model,
            "prompt": f"You are a helpful Linux assistant. Convert this request into a bash command only. Do not add explanations.\nRequest: {prompt}\nCommand:",
            "stream": False
        }
        response = requests.post(OLLAMA_API_URL, json=payload)

        if response.status_code == 200:
            result = response.json()
            command = result.get("response", "").strip()
            return command
        else:
            return "echo 'Failed to generate command'"
    except Exception as e:
        return f"echo 'Error: {e}'"
