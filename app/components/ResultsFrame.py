from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableView, QAbstractItemView, QHeaderView)
from ..PolarsTableModel import PolarsTableModel

class ResultsFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFrameShape(QFrame.NoFrame)  # No frame as container has frame
        self.setObjectName("results_frame")
        self.table_model = PolarsTableModel()
        self.setup_ui()
    
    def setup_ui(self):
        result_layout = QVBoxLayout(self)
        result_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to fit in container
        
        # Header with title
        header = QFrame()
        header.setObjectName("data_preview_header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        self.results_title = QLabel("Data Preview")
        self.results_title.setObjectName("results_title")
        header_layout.addWidget(self.results_title)
        
        # Operations history
        self.history_label = QLabel("Operations: None")
        self.history_label.setObjectName("history_label")
        header_layout.addWidget(self.history_label)
        
        result_layout.addWidget(header)
        
        # Action buttons in a styled bar
        button_bar = QFrame()
        button_bar.setObjectName("button_bar")
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(5, 0, 5, 0)
        
        self.reset_button = QPushButton("Reset to Original")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset_to_original)
        self.reset_button.setEnabled(False)
        
        self.undo_button = QPushButton("Undo Last Operation")
        self.undo_button.setObjectName("undo_button")
        self.undo_button.clicked.connect(self.undo_last_operation)
        self.undo_button.setEnabled(False)
        
        self.download_button = QPushButton("Download Result")
        self.download_button.setObjectName("download_button")
        self.download_button.clicked.connect(self.download_result)
        self.download_button.setEnabled(False)
        
        self.status_label = QLabel("No operation performed yet")
        self.status_label.setObjectName("status_label")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.undo_button)
        button_layout.addStretch()
        button_layout.addWidget(self.status_label)
        button_layout.addWidget(self.download_button)
        
        result_layout.addWidget(button_bar)
        
        # Table view for data
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        
        result_layout.addWidget(self.table_view)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.row_count_label = QLabel("Rows: 0 | Columns: 0")
        status_layout.addWidget(self.row_count_label)
        status_layout.addStretch()
        result_layout.addLayout(status_layout)
    
    def update_preview(self, df):
        """Update the data preview with the current DataFrame"""
        if df is not None:
            preview_df = df.head(100)
            self.table_model.setDataFrame(preview_df)
            self.table_view.resizeColumnsToContents()
            
            # Update row count
            self.row_count_label.setText(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
    
    def update_history(self, operations_history):
        """Update the operations history label"""
        if not operations_history:
            self.history_label.setText("Operations: None")
        else:
            history_text = "Operations: " + " → ".join(operations_history)
            self.history_label.setText(history_text)
    
    def update_status(self, status_text):
        """Update the status label"""
        self.status_label.setText(status_text)
    
    def update_title(self, title_text):
        """Update the results title"""
        self.results_title.setText(title_text)
    
    def enable_buttons(self, reset=True, download=True, undo=False):
        """Enable or disable action buttons"""
        self.reset_button.setEnabled(reset)
        self.download_button.setEnabled(download)
        self.undo_button.setEnabled(undo)
    
    def reset_to_original(self):
        """Call parent's reset method"""
        if hasattr(self.parent, 'reset_to_original_data') and callable(self.parent.reset_to_original_data):
            self.parent.reset_to_original_data()
    
    def download_result(self):
        """Call parent's download method"""
        if hasattr(self.parent, 'download_result_data') and callable(self.parent.download_result_data):
            self.parent.download_result_data()
    
    def undo_last_operation(self):
        """Call parent's undo method"""
        if hasattr(self.parent, 'undo_last_operation') and callable(self.parent.undo_last_operation):
            self.parent.undo_last_operation()