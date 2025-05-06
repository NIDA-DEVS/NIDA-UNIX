from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

class SplashScreen(QWidget):
    def __init__(self, on_close_callback):
        super().__init__()
        self.on_close_callback = on_close_callback
        self.setWindowTitle("AI Linux Assistant")
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        
        self.splash_image = QLabel(self)
        self.splash_image.setMinimumSize(800, 600)  
        
        pixmap = QPixmap("splash.png")
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
