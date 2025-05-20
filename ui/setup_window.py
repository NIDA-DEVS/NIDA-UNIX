
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, 
                           QComboBox, QLineEdit, QStackedWidget, QHBoxLayout, QFrame, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont
from core import ollama_installer  
from ui.main_window import MainWindow
from core.api_client import LLMClient   
from PyQt5.QtWidgets import QApplication 
from core.db import APIKeyDB 

class PullModelThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def log_callback(self, message):
        self.log_signal.emit(message)

    def run(self):
        if not ollama_installer.is_ollama_installed():
            self.log_callback("🔍 Ollama not found. Installing...\n")
            ollama_installer.install_ollama(self.log_callback)

        self.log_callback(f"\n📦 Preparing model '{self.model_name}'...\n")
        ollama_installer.pull_model(self.model_name, self.log_callback)

        self.finished_signal.emit()


class SetupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NIDA - Neural Integrated Desktop Assistant")
        self.setGeometry(200, 200, 800, 600)
        self.api_db = APIKeyDB() 
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox, QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #555;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                font-family: 'Consolas', monospace;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
            }
            QFrame {
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        header = QLabel("NIDA Setup")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
        header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header)

        provider_frame = QFrame()
        provider_frame.setStyleSheet("padding: 10px;")
        provider_layout = QHBoxLayout()
        provider_layout.addWidget(QLabel("Select Provider:"))
        self.provider_selector = QComboBox()
        self.provider_selector.addItems(["ollama", "groq"])
        self.provider_selector.currentTextChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_selector, 1)
        provider_frame.setLayout(provider_layout)
        self.layout.addWidget(provider_frame)

        self.settings_stack = QStackedWidget()
        
        ollama_frame = QFrame()
        ollama_frame.setStyleSheet("padding: 10px;")
        ollama_layout = QVBoxLayout()
        ollama_layout.addWidget(QLabel("Select Model:"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama2", "codellama", "mistral", "gemma:2b"])
        ollama_layout.addWidget(self.model_selector)
        ollama_frame.setLayout(ollama_layout)
        
        groq_frame = QFrame()
        groq_frame.setStyleSheet("padding: 10px;")
        groq_layout = QVBoxLayout()
        groq_layout.addWidget(QLabel("Groq API Key"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Groq API key here")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        groq_layout.addWidget(self.api_key_input)
        groq_frame.setLayout(groq_layout)
        
        self.settings_stack.addWidget(ollama_frame)
        self.settings_stack.addWidget(groq_frame)
        self.layout.addWidget(self.settings_stack)

        log_frame = QFrame()
        log_frame.setStyleSheet("padding: 10px;")
        log_layout = QVBoxLayout()
        log_layout.addWidget(QLabel("Setup Log:"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        log_frame.setLayout(log_layout)
        self.layout.addWidget(log_frame, 1)

        self.start_button = QPushButton("Start Assistant")
        self.start_button.clicked.connect(self.start_install)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)
        
    def append_log(self, message: str):
        """Append message to log view"""
        self.log_view.append(message)
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )
        QApplication.processEvents()

    def on_provider_changed(self, provider):
        self.settings_stack.setCurrentIndex(0 if provider == "ollama" else 1)
        if provider == "groq":
            existing_key = self.api_db.get_key("groq")
            if existing_key:
                if not hasattr(self, 'api_status_label'):
                    self.api_status_label = QLabel()
                    self.api_status_label.setStyleSheet("color: #4CAF50; margin-top: 10px;")
                    groq_frame_layout = self.settings_stack.widget(1).layout()
                    groq_frame_layout.addWidget(self.api_status_label)
                    
                    self.update_key_button = QPushButton("Update API Key")
                    self.update_key_button.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            padding: 8px 16px;
                        }
                        QPushButton:hover {
                            background-color: #1976D2;
                        }
                    """)
                    self.update_key_button.clicked.connect(self.toggle_api_input)
                    groq_frame_layout.addWidget(self.update_key_button)
                
                self.api_status_label.setText("✅ API Key already configured")
                self.api_key_input.hide()
                self.api_key_input.setText(existing_key)
            else:
                if hasattr(self, 'api_status_label'):
                    self.api_status_label.hide()
                    self.update_key_button.hide()
                self.api_key_input.show()
                self.api_key_input.clear()
                self.api_key_input.setFocus()

    def toggle_api_input(self):
        """Toggle between showing existing key and allowing input of new key"""
        if self.api_key_input.isHidden():
            self.api_status_label.setText("Enter new API key:")
            self.api_key_input.show()
            self.api_key_input.clear()
            self.api_key_input.setFocus()
            self.update_key_button.setText("Cancel Update")
        else:
            existing_key = self.api_db.get_key("groq")
            self.api_status_label.setText("✅ API Key already configured")
            self.api_key_input.hide()
            self.api_key_input.setText(existing_key)
            self.update_key_button.setText("Update API Key")

    def start_install(self):
        self.start_button.setDisabled(True)
        provider = self.provider_selector.currentText()

        if provider == "ollama":
            model_name = self.model_selector.currentText()
            self.thread = PullModelThread(model_name)
            self.thread.log_signal.connect(self.append_log)
            self.thread.finished_signal.connect(
                lambda: self.launch_main_app(provider)
            )
            self.thread.start()
            pass
        else:
            api_key = self.api_key_input.text()
            if not api_key:
                self.append_log("❌ Please enter Groq API key")
                self.start_button.setEnabled(True)
                return
            
            self.append_log("🔍 Validating Groq API key...")
            is_valid, message = LLMClient.validate_groq_key(api_key)
            
            if not is_valid:
                self.append_log(f"❌ {message}")
                self.start_button.setEnabled(True)
                return
            if self.api_db.save_key("groq", api_key):
                self.append_log("✅ API key saved successfully")
            else:
                self.append_log("⚠️ Warning: Could not save API key to database")
                
            self.append_log("✅ API key validated successfully")
            self.launch_main_app(provider)

    def launch_main_app(self, provider):
        self.log_view.append("\nSetup complete! Launching Assistant...\n")
        config = {
            "provider": provider,
            "model_name": self.model_selector.currentText() if provider == "ollama" else None,
            "api_key": self.api_key_input.text() if provider == "groq" else None
        }
        self.main_window = MainWindow(config=config)
        self.main_window.show()
        self.close()