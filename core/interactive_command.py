import pexpect
import re
from dataclasses import dataclass
from typing import List
from PyQt5.QtCore import QThread, pyqtSignal
from core.multiple_command_model import CommandSequence

@dataclass
class PromptInfo:
    type: str
    message: str
    options: List[str] = None

class InteractiveCommandThread(QThread):
    output_signal = pyqtSignal(str)
    prompt_signal = pyqtSignal(object)
    finished_signal = pyqtSignal(str)

    def __init__(self, command_sequence: CommandSequence):
        super().__init__()
        self.command_sequence = command_sequence
        self.current_command = 0
        self.collected_output = []
        self.response = None
        self.current_dir = None 

    def run(self):
        try:
            shell = pexpect.spawn('/bin/bash', ['--noediting'], encoding='utf-8')
            shell.setecho(False) 
            shell.expect('.*\$')  
            
            ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
            
            all_outputs = []
            for cmd_entry in self.command_sequence.commands:
                self.output_signal.emit(f"\n🔄 Executing command {cmd_entry.order}/{self.command_sequence.total_commands}:")
                self.output_signal.emit(f"$ {cmd_entry.command}\n")
                
                shell.sendline(cmd_entry.command)
                current_output = []
                
                while True:
                    index = shell.expect([
                        '.*\$',  
                        pexpect.EOF,
                        '(?i)password.*:',
                        '(?i)are you sure.*\\?\\s*\\[y/n\\]',
                        '(?i)do you want to continue.*\\?\\s*\\[y/n\\]',
                        '\n'
                    ])

                    if shell.before:
                        cleaned_output = ansi_escape.sub('', shell.before).strip()
                        if cleaned_output:
                            current_output.append(cleaned_output)
                            self.output_signal.emit(cleaned_output)

                    if index == 0:  
                        break
                    elif index == 1:  
                        break
                    elif index == 2:  
                        self.prompt_signal.emit(PromptInfo("password", shell.after))
                        self.wait_for_response()
                        shell.sendline(self.response)
                    elif index in [3, 4]:  
                        self.prompt_signal.emit(PromptInfo("yesno", shell.after, ["yes", "no"]))
                        self.wait_for_response()
                        shell.sendline(self.response)

                if current_output:
                    all_outputs.append('\n'.join(current_output))
            
            shell.close()
            
            final_output = '\n'.join(all_outputs).strip()
            self.finished_signal.emit(final_output if final_output else "No output")

        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(str(e))

    def wait_for_response(self):
        while self.response is None:
            self.msleep(100)
        self.child.sendline(self.response)
        self.response = None

    def send_response(self, text):
        self.response = text