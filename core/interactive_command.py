import pexpect
from dataclasses import dataclass
from typing import List
from PyQt5.QtCore import QThread, pyqtSignal

@dataclass
class PromptInfo:
    type: str
    message: str
    options: List[str] = None

class InteractiveCommandThread(QThread):
    output_signal = pyqtSignal(str)
    prompt_signal = pyqtSignal(object)
    finished_signal = pyqtSignal(str)

    def __init__(self, command: str):
        super().__init__()
        self.command = command
        self.response = None
        self.child = None
        self.collected_output = []

    def run(self):
        try:
            self.child = pexpect.spawn(self.command, encoding='utf-8')
            while True:
                index = self.child.expect([
                    pexpect.EOF,
                    '(?i)password.*:',
                    '(?i)are you sure.*\\?\\s*\\[y/n\\]',
                    '(?i)do you want to continue.*\\?\\s*\\[y/n\\]',
                    '\n'
                ])

                if self.child.before:
                    self.collected_output.append(self.child.before)
                    self.output_signal.emit(self.child.before)

                if index == 0:  
                    final_output = ''.join(self.collected_output).strip()
                    self.finished_signal.emit(final_output)
                    break
                elif index == 1: 
                    self.prompt_signal.emit(PromptInfo("password", self.child.after))
                    self.wait_for_response()
                elif index in [2, 3]:  
                    self.prompt_signal.emit(PromptInfo("yesno", self.child.after, ["yes", "no"]))
                    self.wait_for_response()

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