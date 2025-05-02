from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt5.QtCore import Qt

class OverlayWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);") 
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        self.label = QLabel("⏳ Processing...")
        self.label.setStyleSheet("color: white; font-size: 18px;")
        layout.addWidget(self.label)
        self.setLayout(layout)
