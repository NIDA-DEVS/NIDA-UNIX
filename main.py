from PyQt5.QtWidgets import QApplication
from ui.setup_window import SetupWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_window = SetupWindow()
    setup_window.show()
    sys.exit(app.exec_())
