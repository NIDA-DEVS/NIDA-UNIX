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
        return "success"
    elif system in ["darwin", "windows"]:
        os_name = "macOS" if system == "darwin" else "Windows"
        log_callback(f"⚠️ Manual installation required for {os_name}")
        log_callback("\nPlease follow these steps:")
        log_callback(f"1. A download page for {os_name} will open in your browser")
        log_callback("2. Download and run the Ollama installer")
        log_callback("3. Wait for the installation to complete")
        log_callback("4. Start the Ollama application")
        log_callback("\nOnce Ollama is installed and running:")
        log_callback("5. Return to this window")
        log_callback("6. Click 'Start Assistant' to proceed")
        return "manual"
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
