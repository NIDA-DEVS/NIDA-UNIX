from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from core.command_handler import create_command_executor
from core.logger import log_action
from core.command_thread import CommandThread
from core.overlay_widget import OverlayWidget
from PyQt5.QtWidgets import (QInputDialog, QLineEdit, QMessageBox)

class MainWindow(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.setWindowTitle("NIDA For your service")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QVBoxLayout()
        self.label = QLabel("Enter instruction:")
        self.input_box = QTextEdit()
        self.submit_button = QPushButton("Generate & Execute")
        self.submit_button.clicked.connect(self.process_command)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.submit_button)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.layout.addWidget(QLabel("Command Output:"))
        self.layout.addWidget(self.output_box)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.layout.addWidget(QLabel("Logs:"))
        self.layout.addWidget(self.log_view)

        self.overlay = OverlayWidget()

        self.setLayout(self.layout)

    def log(self, message):
        self.log_view.append(message)

    def on_command_done(self, instruction, command):
        self.overlay.hide() 
        self.log(f"✅ Command Generated: {command}")  

        reply = QMessageBox.question(self, "Confirm Command",
                                     f"Generated Command:\n\n{command}\n\nProceed?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.execute_command(instruction, command)
        else:
            self.log("🚫 Operation cancelled.")
            self.output_box.setText("Operation cancelled.")

    def execute_command(self, instruction, command):
        try:
            self.log("⚙️ Executing command...")
            
            self.command_executor = create_command_executor(command)
            self.command_executor.output_signal.connect(self.update_output)
            self.command_executor.prompt_signal.connect(self.handle_prompt)
            self.command_executor.finished_signal.connect(
                lambda output: self.handle_command_finished(instruction, command, output)
            )
            self.command_executor.start()

        except Exception as e:
            self.log(f"❌ Error executing command: {e}")
            self.output_box.setText(f"Error executing command: {e}")

    def update_output(self, text):
        self.output_box.append(text)



    def handle_prompt(self, prompt_info):
        if prompt_info.type == "password":
            password, ok = QInputDialog.getText(
                self, 
                "Password Required",
                prompt_info.message,
                QLineEdit.Password
            )
            if ok:
                self.command_executor.send_response(password)
            else:
                self.command_executor.send_response("")

        elif prompt_info.type == "yesno":
            reply, ok = QInputDialog.getItem(
                self,
                "Confirmation Required",
                prompt_info.message,
                prompt_info.options,
                editable=False
            )
            if ok:
                self.command_executor.send_response(reply)
            else:
                self.command_executor.send_response("no")


    def handle_command_finished(self, instruction, command, output):
        """Handle command completion"""
        self.log("✅ Command executed successfully")
        
        if output and output.strip():
            self.log(f"Output:\n{output}")
            self.output_box.setText(output)
            log_action(instruction, command, output)
        else:
            message = "Command executed successfully (no output)"
            self.log(message)
            self.output_box.setText(message)
            log_action(instruction, command, "No output")
        
        self.overlay.hide()

    def on_command_error(self, error_message):
        self.overlay.hide()  
        self.log(f"❌ Error: {error_message}")
        self.output_box.setText(error_message or "Invalid input.")

    def process_command(self):
        instruction = self.input_box.toPlainText().strip()
        if not instruction:
            self.output_box.setText("Please enter an instruction.")
            return

        self.overlay.show()  
        self.overlay.setGeometry(0, 0, self.width(), self.height())  
        self.overlay.show()  
        self.repaint()  

        self.log("Generating command from AI...")

        self.command_thread = CommandThread(instruction, self.config)
        self.command_thread.result_ready.connect(self.on_command_done)
        self.command_thread.error_signal.connect(self.on_command_error)
        self.command_thread.start()