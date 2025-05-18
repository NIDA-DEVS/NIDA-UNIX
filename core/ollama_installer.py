import subprocess
import shutil
import json
import platform

def get_os_type():
    system = platform.system().lower()
    return system

def is_ollama_installed():
    return shutil.which("ollama") is not None

def install_ollama(log_callback):
    system = get_os_type()

    if system == "linux":
        log_callback("🔧 Installing Ollama on Linux...")
        command = "curl -fsSL https://ollama.com/install.sh | sh"
        subprocess.run(command, shell=True)
        log_callback("✅ Ollama installed successfully.")
    elif system == "darwin":  
        log_callback("ℹ️ Manual installation required for macOS")
        log_callback("Please follow these steps:")
        log_callback("1. Visit https://ollama.com/download/mac")
        log_callback("2. Download and install the Ollama package")
        log_callback("3. Once installed, click 'Continue' to proceed")
        return "manual_mac"
    elif system == "windows":
        log_callback("ℹ️ Manual installation required for Windows")
        log_callback("Please follow these steps:")
        log_callback("1. Visit https://ollama.com/download/windows")
        log_callback("2. Download and install the Ollama package")
        log_callback("3. Once installed, click 'Continue' to proceed")
        return "manual_windows"
    else:
        log_callback("❌ Unsupported operating system")
        return "unsupported"


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
