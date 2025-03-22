import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal

class FileItem(QFrame):
    """Widget representing a file in the list"""
    removed = pyqtSignal(str)
    
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("file_item")
        
        # Apply styles
        self.setStyleSheet("""
            #file_item {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                margin: 2px 0;
            }
            #file_item:hover {
                background-color: #e8f0fe;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # File name and size
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        size_str = self._format_size(file_size)
        
        name_label = QLabel(file_name)
        name_label.setObjectName("file_name")
        name_label.setStyleSheet("font-weight: bold;")
        
        size_label = QLabel(size_str)
        size_label.setObjectName("file_size")
        size_label.setStyleSheet("color: #666;")
        
        layout.addWidget(name_label, stretch=1)
        layout.addWidget(size_label)
        
        # Remove button
        remove_button = QPushButton("×")
        remove_button.setObjectName("remove_file_button")
        remove_button.setFixedSize(24, 24)
        remove_button.setStyleSheet("""
            #remove_file_button {
                background-color: #f0f0f0;
                border-radius: 12px;
                border: none;
                color: #666;
                font-weight: bold;
                font-size: 16px;
            }
            #remove_file_button:hover {
                background-color: #e0e0e0;
                color: #333;
            }
        """)
        remove_button.clicked.connect(self._remove_file)
        
        layout.addWidget(remove_button)
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _remove_file(self):
        """Emit signal to remove file"""
        self.removed.emit(self.file_path)


class FileListWidget(QWidget):
    """Widget for displaying a list of files"""
    fileRemoved = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Scroll area for files
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Container for file items
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setContentsMargins(0, 0, 0, 0)
        self.files_layout.setSpacing(5)
        self.files_layout.setAlignment(Qt.AlignTop)
        
        # Empty state label
        self.empty_label = QLabel("No files added yet. Click 'Add CSV Files' to begin.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #666; padding: 20px;")
        self.files_layout.addWidget(self.empty_label)
        
        self.scroll_area.setWidget(self.files_container)
        layout.addWidget(self.scroll_area)
    
    def add_file(self, file_path):
        """Add a new file to the list"""
        if file_path in self.files:
            return
        
        # Remove empty state if this is the first file
        if not self.files:
            self.empty_label.setVisible(False)
        
        self.files.append(file_path)
        
        # Create file item widget
        file_item = FileItem(file_path)
        file_item.removed.connect(self._handle_file_removed)
        
        self.files_layout.addWidget(file_item)
    
    def _handle_file_removed(self, file_path):
        """Handle file removed by the user"""
        if file_path in self.files:
            self.files.remove(file_path)
            
            # Find and remove the widget
            for i in range(self.files_layout.count()):
                widget = self.files_layout.itemAt(i).widget()
                if isinstance(widget, FileItem) and widget.file_path == file_path:
                    widget.deleteLater()
                    break
            
            # Show empty state if no files left
            if not self.files:
                self.empty_label.setVisible(True)
            
            # Emit signal
            self.fileRemoved.emit(file_path)
    
    def clear(self):
        """Clear all files"""
        self.files = []
        
        # Remove all file items
        while self.files_layout.count() > 1:  # Keep the empty label
            item = self.files_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        # Show empty state
        self.empty_label.setVisible(True)