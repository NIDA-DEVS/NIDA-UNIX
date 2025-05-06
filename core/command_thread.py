from PyQt5.QtCore import QThread, pyqtSignal
from core.ai_engine import generate_command
from core.logger import log_action

class CommandThread(QThread):
    result_ready = pyqtSignal(str, str)  
    error_signal = pyqtSignal(str)

    def __init__(self, instruction: str, config: dict):
        super().__init__()
        self.instruction = instruction
        self.config = config

    def run(self):
        try:
            command = generate_command(self.instruction, self.config)

            if not command or "Failed to generate" in command:
                self.error_signal.emit("Invalid input.")
                return

            self.result_ready.emit(self.instruction, command)
        except Exception as e:
            self.error_signal.emit(str(e))
