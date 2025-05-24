from PyQt5.QtWidgets import QPushButton, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient
import speech_recognition as sr
import threading

class SpeechButton(QPushButton):
    speech_result = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_ended = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120) 
        self.is_listening = False
        self.angle = 0
        self.recognizer = sr.Recognizer()
        
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(16)  
        
        self.ripples = []
        self.max_ripples = 3
        
        self.clicked.connect(self.toggle_listening)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border-radius: 60px;
                border: 2px solid #4CAF50;
            }
            QPushButton:hover {
                border: 2px solid #45a049;
            }
        """)

    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.animation_timer.start()
        self.listening_started.emit()
        threading.Thread(target=self.listen_for_speech, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.animation_timer.stop()
        self.listening_ended.emit()
        self.update()

    def listen_for_speech(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                self.speech_result.emit(text)
        except sr.RequestError:
            QMessageBox.warning(self, "Error", "Could not connect to speech recognition service")
        except sr.WaitTimeoutError:
            QMessageBox.information(self, "Timeout", "No speech detected")
        except sr.UnknownValueError:
            QMessageBox.information(self, "Not Understood", "Could not understand the audio")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Speech recognition error: {str(e)}")
        finally:
            self.is_listening = False
            self.animation_timer.stop()
            self.listening_ended.emit()
            self.update()

    def update_animation(self):
        self.angle = (self.angle + 3) % 360  
        
        new_ripples = []
        for radius, opacity in self.ripples:
            if opacity > 0:
                new_ripples.append((radius + 2, max(0, opacity - 3)))  
        self.ripples = new_ripples
        
        if len(self.ripples) < self.max_ripples and (self.angle % 30 == 0):
            self.ripples.append((0, 255))
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QRadialGradient(self.rect().center(), 60)
        if self.is_listening:
            gradient.setColorAt(0, QColor(76, 175, 80, 100))
            gradient.setColorAt(1, QColor(76, 175, 80, 50))
        else:
            gradient.setColorAt(0, QColor(45, 45, 45, 100))
            gradient.setColorAt(1, QColor(45, 45, 45, 50))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect())
        
        center = self.rect().center()
        if self.is_listening:
            for radius, opacity in self.ripples:
                painter.setPen(QPen(QColor(76, 175, 80, opacity), 2))
                painter.drawEllipse(center, radius, radius)
        
        icon_color = QColor(255, 255, 255) if self.is_listening else QColor(76, 175, 80)
        painter.setPen(QPen(icon_color, 2))
        icon_rect = self.rect().adjusted(35, 35, -35, -35)
        painter.drawText(icon_rect, Qt.AlignCenter, "🎤")