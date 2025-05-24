from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
                            QMessageBox, QInputDialog, QLineEdit, QFrame, QHBoxLayout)
from core.logger import log_action
from core.command_thread import CommandThread
from core.overlay_widget import OverlayWidget
from core.command_handler import create_command_executor
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtWidgets import QApplication 
from ui.speech_button import SpeechButton


class MainWindow(QWidget):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        
        self.input_box = QTextEdit()
        self.submit_button = QPushButton("Generate and Execute")
        self.log_view = QTextEdit() 
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        
        self.setWindowTitle("NIDA - Neural Integrated Desktop Assistant")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
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

        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #363636;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        input_layout = QVBoxLayout(input_frame)

        input_row = QHBoxLayout()
        
        manual_input_layout = QVBoxLayout()
        self.input_box.setPlaceholderText("Type your Linux command instruction here...")
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-size: 14px;
                min-height: 80px;
            }
        """)
        self.submit_button.clicked.connect(self.process_command)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666;
            }
        """)
        manual_input_layout.addWidget(self.input_box)
        manual_input_layout.addWidget(self.submit_button)
        input_row.addLayout(manual_input_layout, stretch=2)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("background-color: #444;")
        input_row.addWidget(line)
        
        voice_input_layout = QVBoxLayout()
        voice_label = QLabel("Or use voice input")
        voice_label.setStyleSheet("color: #aaa; font-size: 12px; margin-bottom: 5px;")
        voice_label.setAlignment(Qt.AlignCenter)
        self.speech_button = SpeechButton()
        self.speech_button.speech_result.connect(self.handle_speech_result)
        self.speech_button.listening_started.connect(self.on_listening_started)
        self.speech_button.listening_ended.connect(self.on_listening_ended)
        voice_input_layout.addWidget(voice_label)
        voice_input_layout.addWidget(self.speech_button, 0, Qt.AlignCenter)
        input_row.addLayout(voice_input_layout, stretch=1)

        input_layout.addLayout(input_row)
        
        self.layout.addWidget(input_frame)
        
        log_frame = QFrame()
        log_frame.setStyleSheet("""
            QFrame {
                padding: 10px;
                margin-top: 20px;
            }
        """)
        log_layout = QVBoxLayout()
        log_label = QLabel("Complete Logs:")
        log_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        log_layout.addWidget(log_label)
        
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
            }
        """)
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        log_frame.setLayout(log_layout)
        self.layout.addWidget(log_frame, 1)

        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 4px;
            }
        """)
        self.overlay.hide()
        
        self.loading_label = QLabel("Processing...", self.overlay)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                background-color: transparent;
            }
        """)
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.addWidget(self.loading_label)

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

    def handle_speech_result(self, text):
        self.input_box.setText(text)
        self.log("🎤 Speech recognized: " + text)
        self.process_command()

    def on_listening_started(self):
        self.log("🎤 Listening...")
        self.input_box.setPlaceholderText("Listening...")
        self.submit_button.setEnabled(False)

    def on_listening_ended(self):
        self.input_box.setPlaceholderText("Type your Linux command instruction here...")
        self.submit_button.setEnabled(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.size())