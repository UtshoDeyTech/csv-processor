import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QFrame,
                            QApplication)
from PyQt5.QtCore import Qt
from app.SingleProcessorWindow import MainWindow
from app.BulkProcessorWindow import BulkProcessorWindow
from app.css.launcher_style import (TITLE_STYLE, SUBTITLE_STYLE, FRAME_STYLE, 
                                   OPTION_TITLE_STYLE, OPTION_DESC_STYLE, 
                                   BUTTON_STYLE, FOOTER_STYLE)

class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Processor Launcher")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("CSV Processor")
        title.setStyleSheet(TITLE_STYLE)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Select the processing mode you need")
        subtitle.setStyleSheet(SUBTITLE_STYLE)
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Buttons container
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(20)
        
        # Single file processor
        single_frame = QFrame()
        single_frame.setFrameShape(QFrame.StyledPanel)
        single_frame.setStyleSheet(FRAME_STYLE)
        
        single_layout = QVBoxLayout(single_frame)
        single_layout.setContentsMargins(20, 20, 20, 20)
        
        single_title = QLabel("Single File Processor")
        single_title.setStyleSheet(OPTION_TITLE_STYLE)
        single_layout.addWidget(single_title)
        
        single_desc = QLabel("Process one CSV file at a time with operations like word matching, duplicate removal, and find & replace.")
        single_desc.setWordWrap(True)
        single_desc.setStyleSheet(OPTION_DESC_STYLE)
        single_layout.addWidget(single_desc)
        
        single_button = QPushButton("Launch Single File Processor")
        single_button.setStyleSheet(BUTTON_STYLE)
        single_button.clicked.connect(self.launch_single_processor)
        single_layout.addWidget(single_button)
        
        buttons_container.addWidget(single_frame)
        
        # Multiple files processor
        multi_frame = QFrame()
        multi_frame.setFrameShape(QFrame.StyledPanel)
        multi_frame.setStyleSheet(FRAME_STYLE)
        
        multi_layout = QVBoxLayout(multi_frame)
        multi_layout.setContentsMargins(20, 20, 20, 20)
        
        multi_title = QLabel("Multiple Files Processor")
        multi_title.setStyleSheet(OPTION_TITLE_STYLE)
        multi_layout.addWidget(multi_title)
        
        multi_desc = QLabel("Work with multiple CSV files at once for operations like merging files and subtracting one file from another.")
        multi_desc.setWordWrap(True)
        multi_desc.setStyleSheet(OPTION_DESC_STYLE)
        multi_layout.addWidget(multi_desc)
        
        multi_button = QPushButton("Launch Multiple Files Processor")
        multi_button.setStyleSheet(BUTTON_STYLE)
        multi_button.clicked.connect(self.launch_bulk_processor)
        multi_layout.addWidget(multi_button)
        
        buttons_container.addWidget(multi_frame)
        main_layout.addLayout(buttons_container)
        
        # Footer
        footer = QLabel("CSV Processor v1.0")
        footer.setStyleSheet(FOOTER_STYLE)
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
    
    def launch_single_processor(self):
        """Launch the single file processor using function call"""
        window = MainWindow()
        window.show()

    def launch_bulk_processor(self):
        """Launch the bulk processor using function call"""
        window = BulkProcessorWindow()
        window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec_())