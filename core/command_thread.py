from PyQt5.QtCore import QThread, pyqtSignal
from core.ai_engine import generate_command
from core.logger import log_action
from core.multiple_command_model import CommandSequence

class CommandThread(QThread):
    result_ready = pyqtSignal(str, object)  
    error_signal = pyqtSignal(str)

    def __init__(self, instruction: str, config: dict):
        super().__init__()
        self.instruction = instruction
        self.config = config

    def run(self):
        try:
            command_sequence = generate_command(self.instruction, self.config)
            
            if isinstance(command_sequence, dict):
                command_sequence = CommandSequence(**command_sequence)
            
            if not isinstance(command_sequence, CommandSequence):
                self.error_signal.emit(f"Invalid command sequence type: {type(command_sequence)}")
                return
            
            if not command_sequence.commands:
                self.error_signal.emit("No commands generated")
                return
                
            self.result_ready.emit(self.instruction, command_sequence)
            
        except Exception as e:
            self.error_signal.emit(f"Command generation error: {str(e)}")