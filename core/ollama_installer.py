import subprocess
import shutil
import json

def is_ollama_installed():
    return shutil.which("ollama") is not None

def install_ollama(log_callback):
    log_callback("🔧 Installing Ollama...")
    command = "curl -fsSL https://ollama.com/install.sh | sh"
    subprocess.run(command, shell=True)
    log_callback("✅ Ollama installed.")

def is_model_pulled(model_name):
    try:
        result = subprocess.run(
            ["ollama", "list", "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            models = json.loads(result.stdout)
            return any(model["name"].startswith(model_name) for model in models.get("models", []))
        else:
            return False
    except Exception:
        return False

def pull_model(model_name, log_callback):
    if is_model_pulled(model_name):
        log_callback(f"✅ Model '{model_name}' already exists. Skipping pull.")
        return

    log_callback(f"📥 Pulling model: {model_name}...")
    process = subprocess.Popen(
        ["ollama", "pull", model_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in iter(process.stdout.readline, ''):
        if line:
            log_callback(line.strip())
    process.stdout.close()
    process.wait()
    log_callback("✅ Model pulling complete.")
