from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QMessageBox, QInputDialog, QLineEdit, QFrame)
from core.logger import log_action
from core.command_thread import CommandThread
from core.overlay_widget import OverlayWidget
from core.command_handler import create_command_executor
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QApplication 


class MainWindow(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.setWindowTitle("NIDA For your service")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QTextEdit, QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QFrame {
                border: 1px solid #444;
                border-radius: 4px;
            }
            QMessageBox {
                background-color: #2d2d2d;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        header = QLabel("NIDA - Your AI UNIX Assistant")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
        header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header)

        instruction_frame = QFrame()
        instruction_frame.setStyleSheet("padding: 10px;")
        instruction_layout = QVBoxLayout()
        instruction_layout.addWidget(QLabel("Enter instruction:"))
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Type your Linux command instruction here...")
        instruction_layout.addWidget(self.input_box)
        instruction_frame.setLayout(instruction_layout)
        self.layout.addWidget(instruction_frame)

        self.submit_button = QPushButton("Generate & Execute")
        self.submit_button.clicked.connect(self.process_command)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.layout.addWidget(self.submit_button, 0, Qt.AlignCenter)

        output_frame = QFrame()
        output_frame.setStyleSheet("padding: 10px;")
        output_layout = QVBoxLayout()
        output_layout.addWidget(QLabel("Command Output:"))
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        output_layout.addWidget(self.output_box)
        output_frame.setLayout(output_layout)
        self.layout.addWidget(output_frame, 1)

        log_frame = QFrame()
        log_frame.setStyleSheet("padding: 10px;")
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Logs:"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        log_frame.setLayout(log_layout)
        self.layout.addWidget(log_frame, 1)

        self.overlay = OverlayWidget()
        self.setLayout(self.layout)

    def log(self, message):
        self.log_view.append(message)
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )
        QApplication.processEvents()

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
            self.submit_button.setEnabled(True) 

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
        if hasattr(self, 'command_executor'):
            self.command_executor.output_signal.disconnect()
            self.command_executor.finished_signal.disconnect()
            self.command_executor.prompt_signal.disconnect()
            
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
        self.submit_button.setEnabled(True)

    def on_command_error(self, error_message):
        self.overlay.hide()  
        self.log(f"❌ Error: {error_message}")
        self.output_box.setText(error_message or "Invalid input.")
        self.submit_button.setEnabled(True)
    
    def process_command(self):
        self.output_box.clear()
        self.submit_button.setEnabled(False) 
    
        instruction = self.input_box.toPlainText().strip()
        if not instruction:
            self.output_box.setText("Please enter an instruction.")
            self.submit_button.setEnabled(True)           
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