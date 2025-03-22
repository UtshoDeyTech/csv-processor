from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QComboBox, QPushButton)
import re

class EmailValidationTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        email_layout = QVBoxLayout(self)
        
        # Column selection for email validation
        email_column_group = QGroupBox("Select Email Column")
        email_column_layout = QVBoxLayout()
        
        info_label = QLabel("Select the column containing email addresses. Rows with invalid email formats will be removed.")
        info_label.setWordWrap(True)
        email_column_layout.addWidget(info_label)
        
        column_label = QLabel("Choose the email column:")
        email_column_layout.addWidget(column_label)
        
        self.email_column_combo = QComboBox()
        email_column_layout.addWidget(self.email_column_combo)
        email_column_group.setLayout(email_column_layout)
        email_layout.addWidget(email_column_group)
        
        # Apply button for email validation
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.apply_email_validation_button = QPushButton("Remove Invalid Emails")
        self.apply_email_validation_button.clicked.connect(self.apply_email_validation)
        button_layout.addWidget(self.apply_email_validation_button)
        email_layout.addLayout(button_layout)
        email_layout.addStretch()
    
    def update_columns(self, columns):
        """Update the combo box with columns from loaded file"""
        self.email_column_combo.clear()
        for col in columns:
            self.email_column_combo.addItem(col)
    
    def apply_email_validation(self):
        """Call the parent's email validation method"""
        # Get selected column
        column_name = self.email_column_combo.currentText()
        
        # Call parent's method
        if hasattr(self.parent, 'apply_email_validation_filter') and callable(self.parent.apply_email_validation_filter):
            self.parent.apply_email_validation_filter(column_name)