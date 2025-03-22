import sys
from PyQt5.QtWidgets import QApplication
from app.BulkProcessorWindow import BulkProcessorWindow

def main():
    app = QApplication(sys.argv)
    window = BulkProcessorWindow()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()