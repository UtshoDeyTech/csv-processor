import os
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QFileDialog, QVBoxLayout
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("drop_area")
        self.setMinimumHeight(60)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setAcceptDrops(True)
        
        # Setup UI
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.drop_label = QLabel("Drop CSV file here", self)
        self.drop_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.drop_label)
        
        # Set default style
        self.setStyleSheet("""
            #drop_area {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f8f8f8;
            }
            #drop_area:hover {
                border-color: #2a82da;
            }
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls() and self._is_valid_csv_file(event.mimeData()):
            event.acceptProposedAction()
            self.setStyleSheet("""
                #drop_area {
                    border: 2px dashed #2a82da;
                    border-radius: 5px;
                    background-color: #e6f2ff;
                }
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("""
            #drop_area {
                border: 2px dashed #aaa;
                border-radius: 5px;
                background-color: #f8f8f8;
            }
            #drop_area:hover {
                border-color: #2a82da;
            }
        """)
        event.accept()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        if event.mimeData().hasUrls() and self._is_valid_csv_file(event.mimeData()):
            file_path = event.mimeData().urls()[0].toLocalFile()
            event.acceptProposedAction()
            
            # Reset style
            self.setStyleSheet("""
                #drop_area {
                    border: 2px dashed #aaa;
                    border-radius: 5px;
                    background-color: #f8f8f8;
                }
                #drop_area:hover {
                    border-color: #2a82da;
                }
            """)
            
            # Update file path in UI
            if hasattr(self.parent, 'file_path_label'):
                self.parent.file_path_label.setText(os.path.basename(file_path))
            
            # Call the parent's method to handle file loading
            if hasattr(self.parent.parent, 'load_csv_file') and callable(self.parent.parent.load_csv_file):
                self.parent.parent.load_csv_file(file_path)
    
    def _is_valid_csv_file(self, mime_data: QMimeData):
        """Check if the dragged file is a valid CSV file"""
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            file_path = mime_data.urls()[0].toLocalFile()
            return file_path.lower().endswith('.csv')
        return False


class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("header_frame")
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with title and file selection
        header_layout = QHBoxLayout()
        
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
        main_layout.addLayout(header_layout)
        
        # Drag and drop area
        self.drop_area = DropArea(self)
        main_layout.addWidget(self.drop_area)
    
    def browse_file(self):
        """Open file dialog and trigger the parent's file loading method"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            # Update file path in UI
            self.file_path_label.setText(os.path.basename(file_path))
            
            # Call the parent's method to handle file loading
            if hasattr(self.parent, 'load_csv_file') and callable(self.parent.load_csv_file):
                self.parent.load_csv_file(file_path)