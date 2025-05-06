from PyQt5.QtWidgets import QApplication
from ui.setup_window import SetupWindow
from ui.splash_screen import SplashScreen
import sys

class ApplicationController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.splash = None
        self.setup_window = None

    def show_splash(self):
        self.splash = SplashScreen(self.show_main_window)
        self.splash.show()

    def show_main_window(self):
        self.setup_window = SetupWindow()
        self.setup_window.show()
        if self.splash:
            self.splash.close()

    def run(self):
        self.show_splash()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    controller = ApplicationController()
    controller.run()