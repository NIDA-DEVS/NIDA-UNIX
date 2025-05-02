from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox
from core.command_handler import execute_command
from core.logger import log_action
from core.command_thread import CommandThread
from core.overlay_widget import OverlayWidget

class MainWindow(QWidget):
    def __init__(self, model_name):
        super().__init__()
        self.model = model_name
        self.setWindowTitle("NIDA For your service")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QVBoxLayout()
        self.label = QLabel("Enter instruction:")
        self.input_box = QTextEdit()

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        self.submit_button = QPushButton("Generate & Execute")
        self.submit_button.clicked.connect(self.process_command)

        self.overlay = OverlayWidget()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(QLabel("Logs:"))
        self.layout.addWidget(self.output_box)

        self.setLayout(self.layout)

    def log(self, message):
        self.output_box.append(message)

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
        """Execute the command after confirmation."""
        try:
            self.log("⚙️ Executing command...")

            output = execute_command(command)
            log_action(instruction, command, output)

            if output:
                self.log(f"✅ Execution Result: {output}")
                self.output_box.setText(output)
            else:
                self.log(f"✅ Command Executed Successfully.")
                self.output_box.setText("Command Executed Successfully.")
        except Exception as e:
            self.log(f"❌ Error executing command: {e}")
            self.output_box.setText("Error executing the command.")


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

        self.command_thread = CommandThread(instruction, self.model)
        self.command_thread.result_ready.connect(self.on_command_done)
        self.command_thread.error_signal.connect(self.on_command_error)
        self.command_thread.start()



    # def process_command(self):
    #     instruction = self.input_box.toPlainText().strip()
    #     if not instruction:
    #         self.output_box.setText("Please enter an instruction.")
    #         return

    #     self.overlay.show_overlay()
    #     self.repaint()

    #     try:
    #         command = generate_command(instruction, model=self.model)

    #         if not command or "Failed to generate" in command:
    #             self.output_box.setText("Invalid input.")
    #             self.overlay.hide_overlay()
    #             return

    #         reply = QMessageBox.question(self, "Confirm Command",
    #                                     f"Generated Command:\n\n{command}\n\nProceed?",
    #                                     QMessageBox.Yes | QMessageBox.No)

    #         if reply == QMessageBox.Yes:
    #             output = execute_command(command)
    #             if "command not found" in output.lower() or "error" in output.lower():
    #                 self.output_box.setText("Invalid input.")
    #             else:
    #                 self.output_box.setText(output)
    #             log_action(instruction, command, output)
    #         else:
    #             self.output_box.setText("Operation cancelled.")
    #     except Exception as e:
    #         self.output_box.setText(f"Error occurred: {str(e)}")
    #     finally:
    #         self.overlay.hide_overlay()



    # def process_command(self):
    #     instruction = self.input_box.toPlainText()
    #     self.output_box.clear()
    #     self.loading_label.setVisible(True)
    #     self.log("🧠 Generating command from AI...")

    #     try:
    #         command = generate_command(instruction, model=self.model)
    #         self.log(f"✅ Command Generated:\n{command}")
    #     except Exception as e:
    #         self.log(f"❌ Error generating command: {e}")
    #         self.loading_label.setVisible(False)
    #         return

    #     reply = QMessageBox.question(self, "Confirm Command",
    #                                  f"Generated Command:\n\n{command}\n\nProceed?",
    #                                  QMessageBox.Yes | QMessageBox.No)
    #     if reply == QMessageBox.Yes:
    #         self.log("⚙️ Executing command...")
    #         try:
    #             output = execute_command(command)
    #             log_action(instruction, command, output)
    #             if output:
    #                 self.log(f"✅ Execution Result:\n{output}")
    #             else:
    #                 self.log(f"✅ Command Executed Successfully.")

    #         except Exception as e:
    #             self.log(f"❌ Error executing command: {e}")
    #     else:
    #         self.log("🚫 Operation cancelled.")

    #     self.loading_label.setVisible(False)

