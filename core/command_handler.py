from core.interactive_command import InteractiveCommandThread

def create_command_executor(command: str) -> InteractiveCommandThread:
    return InteractiveCommandThread(command)