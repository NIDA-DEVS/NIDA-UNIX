from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from core import ollama_installer  
from ui.main_window import MainWindow


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
        self.setWindowTitle("AI Linux Assistant - Setup")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("🤖 Select a model to install:"))

        self.model_selector = QComboBox()
        self.model_selector.addItems(["llama2", "codellama", "mistral"])
        self.layout.addWidget(self.model_selector)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: monospace;")
        self.layout.addWidget(self.log_view)

        self.start_button = QPushButton("Start Assistant")
        self.start_button.clicked.connect(self.start_install)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)

    def start_install(self):
        self.start_button.setDisabled(True)
        model_name = self.model_selector.currentText()

        self.thread = PullModelThread(model_name)
        self.thread.log_signal.connect(self.append_log)
        self.thread.finished_signal.connect(self.launch_main_app)
        self.thread.start()

    def append_log(self, message):
        self.log_view.append(message)
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())

    def launch_main_app(self):
        self.log_view.append("\n✅ Setup complete! Launching Assistant...\n")
        selected_model = self.model_selector.currentText()
        self.main_window = MainWindow(model_name=selected_model)
        self.main_window.show()
        self.close()
