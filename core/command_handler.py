from core.interactive_command import InteractiveCommandThread
from core.multiple_command_model import CommandSequence

def create_command_executor(command_sequence: CommandSequence) -> InteractiveCommandThread:
    if not isinstance(command_sequence, CommandSequence):
        if isinstance(command_sequence, dict):
            command_sequence = CommandSequence(**command_sequence)
        else:
            raise ValueError(f"Invalid command sequence type: {type(command_sequence)}")
            
    print(f"Creating command executor with sequence: {command_sequence}")
    return InteractiveCommandThread(command_sequence)