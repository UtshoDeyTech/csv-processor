import os
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QFileDialog

class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("header_frame")
        self.setup_ui()
        
    def setup_ui(self):
        header_layout = QHBoxLayout(self)
        
        # App title
        app_title = QLabel("CSV Processor")
        app_title.setObjectName("app_title")
        header_layout.addWidget(app_title)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_label = QLabel("CSV File:")
        file_label.setObjectName("file_label")
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setObjectName("file_path_label")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.browse_file)
        
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_label, stretch=1)
        file_layout.addWidget(self.browse_button)
        
        header_layout.addLayout(file_layout)
    
    def browse_file(self):
        """Open file dialog and trigger the parent's file loading method"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            # Update file path in UI
            self.file_path_label.setText(os.path.basename(file_path))
            
            # Call the parent's method to handle file loading
            if hasattr(self.parent, 'load_csv_file') and callable(self.parent.load_csv_file):
                self.parent.load_csv_file(file_path)