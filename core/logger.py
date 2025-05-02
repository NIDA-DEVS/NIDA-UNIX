import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_action(user_input: str, command: str, result: str):
    log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y_%m_%d')}.txt")
    with open(log_file, "a") as f:
        f.write(f"\n[{datetime.now()}]\n")
        f.write(f"User Input: {user_input}\n")
        f.write(f"Command: {command}\n")
        f.write(f"Result: {result}\n")
        f.write("-" * 40)
