from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QRadioButton, QCheckBox, QLabel, QLineEdit, QPushButton, 
                            QListWidget, QAbstractItemView)

class WordMatchTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.column_checkboxes = []
        self.setup_ui()
    
    def setup_ui(self):
        word_match_layout = QVBoxLayout(self)
        
        # Filter type section
        filter_type_group = QGroupBox("Filter Type")
        filter_type_layout = QHBoxLayout()
        self.include_radio = QRadioButton("Include matches")
        self.exclude_radio = QRadioButton("Exclude matches")
        self.include_radio.setChecked(True)
        filter_type_layout.addWidget(self.include_radio)
        filter_type_layout.addWidget(self.exclude_radio)
        filter_type_layout.addStretch()
        filter_type_group.setLayout(filter_type_layout)
        word_match_layout.addWidget(filter_type_group)
        
        # Column selection section
        columns_group = QGroupBox("Select Columns to Search")
        columns_layout = QVBoxLayout()
        
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.clicked.connect(self.toggle_all_columns)
        columns_layout.addWidget(self.select_all_checkbox)
        
        # Create scrolling area with checkboxes
        self.columns_scroll = QWidget()
        self.columns_scroll.setObjectName("columns_scroll")
        self.columns_scroll_layout = QVBoxLayout(self.columns_scroll)
        self.columns_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.columns_scroll_layout.setSpacing(2)
        
        # Hidden widget for backward compatibility
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.columns_list.setAlternatingRowColors(True)
        self.columns_list.setVisible(False)
        
        columns_layout.addWidget(self.columns_scroll)
        columns_group.setLayout(columns_layout)
        word_match_layout.addWidget(columns_group)
        
        # Search values section
        search_group = QGroupBox("Search Values")
        search_layout = QVBoxLayout()
        search_label = QLabel("Enter comma-separated values to search for:")
        search_layout.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g. cleaning, repair, maintenance")
        search_layout.addWidget(self.search_input)
        
        # Add case-insensitive option
        self.case_insensitive_checkbox = QCheckBox("Case insensitive search")
        self.case_insensitive_checkbox.setChecked(True)  # Default to case insensitive
        search_layout.addWidget(self.case_insensitive_checkbox)
        
        search_group.setLayout(search_layout)
        word_match_layout.addWidget(search_group)
        
        # Apply button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.apply_word_match_button = QPushButton("Apply Word Match")
        self.apply_word_match_button.clicked.connect(self.apply_word_match)
        button_layout.addWidget(self.apply_word_match_button)
        word_match_layout.addLayout(button_layout)
        word_match_layout.addStretch()
    
    def toggle_all_columns(self, checked):
        """Toggle all column checkboxes"""
        for checkbox in self.column_checkboxes:
            checkbox.setChecked(checked)
    
    def update_columns(self, columns):
        """Update the list of columns when a new file is loaded"""
        # Clear existing checkboxes
        for checkbox in self.column_checkboxes:
            checkbox.deleteLater()
        self.column_checkboxes = []
        
        # Clear columns list for backward compatibility
        self.columns_list.clear()
        
        # Add new columns
        for col in columns:
            # Add to original list (keep for compatibility)
            self.columns_list.addItem(col)
            
            # Add checkbox
            checkbox = QCheckBox(col)
            checkbox.setObjectName(f"col_checkbox_{col}")
            self.column_checkboxes.append(checkbox)
            self.columns_scroll_layout.addWidget(checkbox)
        
        # Add stretch to keep checkboxes at top
        self.columns_scroll_layout.addStretch()
        
        # Enable select all checkbox
        self.select_all_checkbox.setEnabled(True)
    
    def apply_word_match(self):
        """Call the parent's word match method with the selected parameters"""
        # Get selected columns
        selected_column_names = [cb.text() for cb in self.column_checkboxes if cb.isChecked()]
        
        # Get search values
        search_text = self.search_input.text().strip()
        
        # Get other settings
        include = self.include_radio.isChecked()
        case_insensitive = self.case_insensitive_checkbox.isChecked()
        
        # Call parent's method
        if hasattr(self.parent, 'apply_word_match_filter') and callable(self.parent.apply_word_match_filter):
            self.parent.apply_word_match_filter(
                selected_column_names, 
                search_text,
                include,
                case_insensitive
            )