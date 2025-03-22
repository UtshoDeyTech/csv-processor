from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QComboBox, QLineEdit, QPushButton)

class FindReplaceTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        find_replace_layout = QVBoxLayout(self)
        
        # Column selection for find and replace
        fr_column_group = QGroupBox("Select Column for Find and Replace")
        fr_column_layout = QVBoxLayout()
        
        column_label = QLabel("Choose the column you want to modify:")
        fr_column_layout.addWidget(column_label)
        
        self.fr_column_combo = QComboBox()
        fr_column_layout.addWidget(self.fr_column_combo)
        fr_column_group.setLayout(fr_column_layout)
        find_replace_layout.addWidget(fr_column_group)
        
        # Find and replace values
        fr_values_group = QGroupBox("Find and Replace Values")
        fr_values_layout = QVBoxLayout()
        
        find_label = QLabel("Find:")
        fr_values_layout.addWidget(find_label)
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Leave empty to replace NULL values")
        fr_values_layout.addWidget(self.find_input)
        
        replace_label = QLabel("Replace with:")
        fr_values_layout.addWidget(replace_label)
        self.replace_input = QLineEdit()
        fr_values_layout.addWidget(self.replace_input)
        
        fr_values_group.setLayout(fr_values_layout)
        find_replace_layout.addWidget(fr_values_group)
        
        # Apply button for find and replace
        fr_button_layout = QHBoxLayout()
        fr_button_layout.addStretch()
        self.apply_fr_button = QPushButton("Apply Find and Replace")
        self.apply_fr_button.clicked.connect(self.apply_find_replace)
        fr_button_layout.addWidget(self.apply_fr_button)
        find_replace_layout.addLayout(fr_button_layout)
        find_replace_layout.addStretch()
    
    def update_columns(self, columns):
        """Update the combo box with columns from loaded file"""
        self.fr_column_combo.clear()
        for col in columns:
            self.fr_column_combo.addItem(col)
    
    def apply_find_replace(self):
        """Call the parent's find and replace method"""
        # Get selected column
        column_name = self.fr_column_combo.currentText()
        
        # Get find and replace values
        old_value = self.find_input.text().strip()
        new_value = self.replace_input.text().strip()
        
        # Call parent's method
        if hasattr(self.parent, 'apply_find_replace_filter') and callable(self.parent.apply_find_replace_filter):
            self.parent.apply_find_replace_filter(column_name, old_value, new_value)