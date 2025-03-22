from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QCheckBox, QScrollArea, QWidget, QFrame)
from PyQt5.QtCore import Qt

class ExportDialog(QDialog):
    def __init__(self, parent=None, columns=None):
        super().__init__(parent)
        self.columns = columns or []
        self.selected_columns = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("column_export_dialog")
        self.setWindowTitle("Select Columns to Export")
        self.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        dialog_layout.setSpacing(15)
        
        # Column selection header
        header_label = QLabel("Select columns to include in export:")
        dialog_layout.addWidget(header_label)
        
        # Scrollable area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Box)  # Changed from QDialog.Box to QFrame.Box
        scroll_area.setMaximumHeight(300)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(2)
        scroll_layout.setAlignment(Qt.AlignTop)
        
        # Add checkboxes for each column
        self.column_checkboxes = []
        for col in self.columns:
            checkbox = QCheckBox(col)
            checkbox.setChecked(True)  # Select by default
            self.column_checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
        
        scroll_area.setWidget(scroll_content)
        dialog_layout.addWidget(scroll_area)
        
        # Select all / Deselect all options
        check_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.setObjectName("select_all_btn")
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in self.column_checkboxes])
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setObjectName("deselect_all_btn")
        deselect_all_btn.clicked.connect(lambda: [cb.setChecked(False) for cb in self.column_checkboxes])
        
        check_layout.addWidget(select_all_btn)
        check_layout.addWidget(deselect_all_btn)
        dialog_layout.addLayout(check_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        button_box.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        
        export_btn = QPushButton("Export")
        export_btn.setObjectName("export_btn")
        export_btn.setDefault(True)
        export_btn.clicked.connect(self.accept)
        
        button_box.addWidget(cancel_btn)
        button_box.addWidget(export_btn)
        dialog_layout.addLayout(button_box)
    
    def get_selected_columns(self):
        """Return the list of selected column names"""
        return [cb.text() for cb in self.column_checkboxes if cb.isChecked()]