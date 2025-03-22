from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QCheckBox, QLabel, QPushButton, QListWidget, QAbstractItemView)

class DuplicateTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.dup_column_checkboxes = []
        self.setup_ui()
    
    def setup_ui(self):
        duplicate_layout = QVBoxLayout(self)
        
        # Column selection for duplicates
        dup_columns_group = QGroupBox("Select Columns to Check for Duplicates")
        dup_columns_layout = QVBoxLayout()
        
        dup_info_label = QLabel("Select the columns that should be used to identify duplicate rows. "
                                "Rows having identical values in all selected columns will be considered duplicates.")
        dup_info_label.setWordWrap(True)
        dup_columns_layout.addWidget(dup_info_label)
        
        self.select_all_dup_checkbox = QCheckBox("Select All")
        self.select_all_dup_checkbox.clicked.connect(self.toggle_all_dup_columns)
        dup_columns_layout.addWidget(self.select_all_dup_checkbox)
        
        # Create scrolling area with checkboxes
        self.dup_columns_scroll = QWidget()
        self.dup_columns_scroll.setObjectName("dup_columns_scroll")
        self.dup_columns_scroll_layout = QVBoxLayout(self.dup_columns_scroll)
        self.dup_columns_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.dup_columns_scroll_layout.setSpacing(2)
        
        # Hidden widget for backward compatibility
        self.dup_columns_list = QListWidget()
        self.dup_columns_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dup_columns_list.setAlternatingRowColors(True)
        self.dup_columns_list.setVisible(False)
        
        dup_columns_layout.addWidget(self.dup_columns_scroll)
        dup_columns_group.setLayout(dup_columns_layout)
        duplicate_layout.addWidget(dup_columns_group)
        
        # Apply button for duplicates
        dup_button_layout = QHBoxLayout()
        dup_button_layout.addStretch()
        self.apply_dup_button = QPushButton("Remove Duplicates")
        self.apply_dup_button.clicked.connect(self.apply_remove_duplicates)
        dup_button_layout.addWidget(self.apply_dup_button)
        duplicate_layout.addLayout(dup_button_layout)
        duplicate_layout.addStretch()
    
    def toggle_all_dup_columns(self, checked):
        """Toggle all duplicate column checkboxes"""
        for checkbox in self.dup_column_checkboxes:
            checkbox.setChecked(checked)
    
    def update_columns(self, columns):
        """Update the list of columns when a new file is loaded"""
        # Clear existing checkboxes
        for checkbox in self.dup_column_checkboxes:
            checkbox.deleteLater()
        self.dup_column_checkboxes = []
        
        # Clear columns list for backward compatibility
        self.dup_columns_list.clear()
        
        # Add new columns
        for col in columns:
            # Add to original list (keep for compatibility)
            self.dup_columns_list.addItem(col)
            
            # Add checkbox for duplicate removal
            dup_checkbox = QCheckBox(col)
            dup_checkbox.setObjectName(f"dup_col_checkbox_{col}")
            self.dup_column_checkboxes.append(dup_checkbox)
            self.dup_columns_scroll_layout.addWidget(dup_checkbox)
        
        # Add stretch to keep checkboxes at top
        self.dup_columns_scroll_layout.addStretch()
        
        # Enable select all checkbox
        self.select_all_dup_checkbox.setEnabled(True)
    
    def apply_remove_duplicates(self):
        """Call the parent's duplicate removal method with the selected parameters"""
        # Get selected columns
        selected_column_names = [cb.text() for cb in self.dup_column_checkboxes if cb.isChecked()]
        
        # Call parent's method
        if hasattr(self.parent, 'apply_remove_duplicates_filter') and callable(self.parent.apply_remove_duplicates_filter):
            self.parent.apply_remove_duplicates_filter(selected_column_names)