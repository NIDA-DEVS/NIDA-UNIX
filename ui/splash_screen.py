from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import os
import sys

class SplashScreen(QWidget):
    def __init__(self, on_close_callback):
        super().__init__()
        self.on_close_callback = on_close_callback
        self.setWindowTitle("AI Linux Assistant")
        self.setFixedSize(800, 750)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        
        self.splash_image = QLabel(self)
        self.splash_image.setMinimumSize(800, 600)  
        self.splash_image.setStyleSheet("background-color: black;")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(__file__))
        
        splash_image_path = os.path.join(base_path, 'splash_screen.png')
        pixmap = QPixmap(splash_image_path)
        scaled_pixmap = pixmap.scaled(
            800, 600,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )
        self.splash_image.setPixmap(scaled_pixmap)
        self.splash_image.setScaledContents(True) 
        
        layout.addWidget(self.splash_image)
        self.setLayout(layout)
        
        QTimer.singleShot(4000, self.close)

    def closeEvent(self, event):
        self.on_close_callback()
        event.accept()
