import sys
from PyQt5.QtWidgets import QApplication
from app.LauncherWindow import LauncherWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec_())