from PyQt5.QtWidgets import (QVBoxLayout, QLabel, QProgressBar, QDialog)
from PyQt5.QtCore import Qt


class ProcessingDialog(QDialog):
    def __init__(self, parent=None, message="Processing..."):
        super().__init__(parent)
        self.setWindowTitle("Processing")
        self.setFixedSize(400, 120)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setObjectName("processing_dialog")
        
        layout = QVBoxLayout(self)
        
        # Icon and message
        icon_label = QLabel("🔄")
        icon_label.setObjectName("icon_label")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        self.message_label = QLabel(message)
        self.message_label.setObjectName("message_label")
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress_bar")
        layout.addWidget(self.progress_bar)
    
    def set_progress(self, value):
        self.progress_bar.setValue(value)
    
    def set_message(self, message):
        self.message_label.setText(message)