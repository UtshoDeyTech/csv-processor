from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QSlider,
                            QCheckBox, QGridLayout, QGroupBox)
from PyQt5.QtCore import Qt

class DomainSimilarityTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        
    def init_ui(self):
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Create description
        description_label = QLabel(
            "Find emails where the domain matches the website name with specified similarity. "
            "Select the email column and domain/website column below."
        )
        description_label.setWordWrap(True)
        description_label.setObjectName("description_label")
        main_layout.addWidget(description_label)
        
        # Create column selection group
        columns_group = QGroupBox("Select Columns")
        columns_layout = QGridLayout()
        
        # Email column selection
        email_label = QLabel("Email Column:")
        self.email_combo = QComboBox()
        self.email_combo.setMinimumWidth(200)
        columns_layout.addWidget(email_label, 0, 0)
        columns_layout.addWidget(self.email_combo, 0, 1)
        
        # Domain column selection
        domain_label = QLabel("Domain/Website Column:")
        self.domain_combo = QComboBox()
        self.domain_combo.setMinimumWidth(200)
        columns_layout.addWidget(domain_label, 1, 0)
        columns_layout.addWidget(self.domain_combo, 1, 1)
        
        columns_group.setLayout(columns_layout)
        main_layout.addWidget(columns_group)
        
        # Create similarity settings group
        similarity_group = QGroupBox("Similarity Settings")
        similarity_layout = QVBoxLayout()
        
        # Similarity threshold slider
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Similarity Threshold:")
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setRange(0, 100)
        self.threshold_slider.setValue(75)  # Default to 75%
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(10)
        
        self.threshold_value_label = QLabel("75%")
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value_label)
        similarity_layout.addLayout(threshold_layout)
        
        # Additional options
        self.check_username = QCheckBox("Check email username for domain name (e.g. domain.support@gmail.com)")
        self.check_username.setChecked(True)
        similarity_layout.addWidget(self.check_username)
        
        similarity_group.setLayout(similarity_layout)
        main_layout.addWidget(similarity_group)
        
        # Add apply button
        self.apply_button = QPushButton("Find Similar Domains")
        self.apply_button.setObjectName("primary_button")
        self.apply_button.clicked.connect(self.apply_filter)
        main_layout.addWidget(self.apply_button)
        
        # Add spacing
        main_layout.addStretch()
        
    def update_columns(self, columns):
        """Update column dropdowns with the available columns"""
        self.email_combo.clear()
        self.domain_combo.clear()
        
        # Find potential email and domain columns
        email_columns = []
        domain_columns = []
        other_columns = []
        
        for col in columns:
            col_lower = col.lower()
            if 'email' in col_lower or 'mail' in col_lower:
                email_columns.append(col)
            elif any(term in col_lower for term in ['domain', 'website', 'site', 'url', 'web']):
                domain_columns.append(col)
            else:
                other_columns.append(col)
        
        # Add columns to dropdowns with appropriate grouping
        if email_columns:
            self.email_combo.addItem("-- Select Email Column --")
            for col in email_columns:
                self.email_combo.addItem(col)
            
            for col in other_columns:
                self.email_combo.addItem(col)
        else:
            self.email_combo.addItem("-- Select Column --")
            for col in columns:
                self.email_combo.addItem(col)
        
        if domain_columns:
            self.domain_combo.addItem("-- Select Domain Column --")
            for col in domain_columns:
                self.domain_combo.addItem(col)
            
            for col in other_columns:
                self.domain_combo.addItem(col)
        else:
            self.domain_combo.addItem("-- Select Column --")
            for col in columns:
                self.domain_combo.addItem(col)
    
    def update_threshold_label(self, value):
        """Update the threshold label to show current value"""
        self.threshold_value_label.setText(f"{value}%")
    
    def apply_filter(self):
        """Apply the domain similarity filter"""
        # Get selected columns
        email_column = self.email_combo.currentText()
        domain_column = self.domain_combo.currentText()
        
        # Check if placeholders are selected
        if email_column.startswith("-- Select") or domain_column.startswith("-- Select"):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select both email and domain columns")
            return
        
        # Get threshold value
        threshold = self.threshold_slider.value() / 100.0  # Convert to decimal
        
        # Get checkbox value
        check_username = self.check_username.isChecked()
        
        # Call the main function to apply the filter
        self.parent.apply_domain_similarity_filter(
            email_column, 
            domain_column, 
            threshold,
            check_username
        )