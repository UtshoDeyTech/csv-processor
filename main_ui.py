import sys
import os
import polars as pl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QFileDialog, QLabel, QComboBox, QLineEdit, QCheckBox, QListWidget,
                            QWidget, QGroupBox, QMessageBox, QTableView, QAbstractItemView, QHeaderView,
                            QSplitter, QFrame, QSizePolicy, QProgressBar, QTabWidget, QRadioButton,
                            QDialog, QListWidgetItem, QScrollArea)
from PyQt5.QtCore import Qt, QAbstractTableModel, QSize, QTimer, QRect
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QResizeEvent
import main  # Import the original main.py functionality
from styles import STYLESHEET

class PolarsTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else pl.DataFrame()
        
    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._data = dataframe
        self.endResetModel()
        
    def rowCount(self, parent=None):
        return self._data.shape[0]
    
    def columnCount(self, parent=None):
        return self._data.shape[1]
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            return str(self._data[index.row(), index.column()])
        
        elif role == Qt.BackgroundRole:
            # Alternate row colors for better readability
            if index.row() % 2 == 0:
                return QColor(245, 245, 245)
            return QColor(255, 255, 255)
            
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._data.columns[section])
        return str(section + 1)

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Processor")
        self.setMinimumSize(1000, 700)
        
        # Set window to maximize on startup
        self.showMaximized()
        
        # Apply the imported stylesheet directly
        self.setStyleSheet(STYLESHEET)
        print("Applied stylesheet from imported STYLESHEET")
        
        # State variables
        self.csv_file = None
        self.df = None
        self.output_df = None
        self.original_df = None  # Store the original dataframe
        self.output_file = None
        self.row_count = 0
        self.operations_history = []  # Track applied operations
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header area with app title and file selection
        header_frame = QFrame()
        header_frame.setObjectName("header_frame")
        header_layout = QHBoxLayout(header_frame)
        
        app_title = QLabel("CSV Processor")
        app_title.setObjectName("app_title")
        header_layout.addWidget(app_title)
        
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
        main_layout.addWidget(header_frame)
        
        # Main content with tabs and data view
        content_layout = QVBoxLayout()
        
        # Tab widget for operations
        self.tab_widget = QTabWidget()
        
        # Word Match Tab
        word_match_tab = QWidget()
        word_match_layout = QVBoxLayout(word_match_tab)
        
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
        columns_scroll = QWidget()
        columns_scroll.setObjectName("columns_scroll")
        columns_scroll_layout = QVBoxLayout(columns_scroll)
        columns_scroll_layout.setContentsMargins(0, 0, 0, 0)
        columns_scroll_layout.setSpacing(2)
        
        self.column_checkboxes = []
        self.columns_list = QListWidget()
        self.columns_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.columns_list.setAlternatingRowColors(True)
        self.columns_list.setVisible(False)  # Hide original list widget
        
        columns_layout.addWidget(columns_scroll)
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
        
        # Add to tab widget
        self.tab_widget.addTab(word_match_tab, "Word Match")
        
        # Duplicate Remover Tab
        duplicate_tab = QWidget()
        duplicate_layout = QVBoxLayout(duplicate_tab)
        
        # Column selection for duplicates
        dup_columns_group = QGroupBox("Select Columns to Check for Duplicates")
        dup_columns_layout = QVBoxLayout()
        
        dup_info_label = QLabel("Select the columns that should be used to identify duplicate rows. Rows having identical values in all selected columns will be considered duplicates.")
        dup_info_label.setWordWrap(True)
        dup_columns_layout.addWidget(dup_info_label)
        
        self.select_all_dup_checkbox = QCheckBox("Select All")
        self.select_all_dup_checkbox.clicked.connect(self.toggle_all_dup_columns)
        dup_columns_layout.addWidget(self.select_all_dup_checkbox)
        
        # Create scrolling area with checkboxes
        dup_columns_scroll = QWidget()
        dup_columns_scroll.setObjectName("dup_columns_scroll")
        dup_columns_scroll_layout = QVBoxLayout(dup_columns_scroll)
        dup_columns_scroll_layout.setContentsMargins(0, 0, 0, 0)
        dup_columns_scroll_layout.setSpacing(2)
        
        self.dup_column_checkboxes = []
        self.dup_columns_list = QListWidget()
        self.dup_columns_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dup_columns_list.setAlternatingRowColors(True)
        self.dup_columns_list.setVisible(False)  # Hide original list widget
        
        dup_columns_layout.addWidget(dup_columns_scroll)
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
        
        # Add to tab widget
        self.tab_widget.addTab(duplicate_tab, "Duplicate Remover")
        
        # Find and Replace Tab
        find_replace_tab = QWidget()
        find_replace_layout = QVBoxLayout(find_replace_tab)
        
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
        
        # Add to tab widget
        self.tab_widget.addTab(find_replace_tab, "Find and Replace")
        
        content_layout.addWidget(self.tab_widget)
        
        # Status and results section
        result_group = QFrame()
        result_group.setFrameShape(QFrame.StyledPanel)
        result_layout = QVBoxLayout(result_group)
        
        # Results header with operations history and reset button
        results_header = QHBoxLayout()
        
        # Left side with title
        header_left = QVBoxLayout()
        self.results_title = QLabel("Filtered Data Preview")
        self.results_title.setObjectName("results_title")
        header_left.addWidget(self.results_title)
        
        # Operations history below title
        self.history_label = QLabel("Operations: None")
        self.history_label.setObjectName("history_label")
        header_left.addWidget(self.history_label)
        
        results_header.addLayout(header_left)
        results_header.addStretch()
        
        # Right side with action buttons
        header_right = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Original")
        self.reset_button.setObjectName("reset_button")
        self.reset_button.clicked.connect(self.reset_to_original)
        self.reset_button.setEnabled(False)
        
        self.status_label = QLabel("No operation performed yet")
        self.status_label.setObjectName("status_label")
        
        self.download_button = QPushButton("Download Result")
        self.download_button.clicked.connect(self.download_result)
        self.download_button.setEnabled(False)
        
        header_right.addWidget(self.reset_button)
        header_right.addWidget(self.status_label)
        header_right.addWidget(self.download_button)
        
        results_header.addLayout(header_right)
        result_layout.addLayout(results_header)
        
        # Table view for data
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_model = PolarsTableModel()
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
        
        content_layout.addWidget(result_group)
        
        # Add the content layout to the main layout
        main_layout.addLayout(content_layout)

    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize events to adjust the UI for responsiveness"""
        super().resizeEvent(event)
        
        # Get the current window size
        width = event.size().width()
        height = event.size().height()
        
        # Adjust UI elements based on window size
        if width < 800:  # Small screen
            # Make column lists taller and narrower
            for scroll in [self.findChild(QWidget, "columns_scroll"), 
                          self.findChild(QWidget, "dup_columns_scroll")]:
                if scroll:
                    scroll.setMaximumWidth(200)
        else:  # Large screen
            # Reset to default
            for scroll in [self.findChild(QWidget, "columns_scroll"), 
                          self.findChild(QWidget, "dup_columns_scroll")]:
                if scroll:
                    scroll.setMaximumWidth(16777215)  # Default max width
        
        # Adjust table columns
        if hasattr(self, 'table_view'):
            self.table_view.resizeColumnsToContents()
    
    def toggle_all_columns(self, checked):
        for checkbox in self.column_checkboxes:
            checkbox.setChecked(checked)
    
    def toggle_all_dup_columns(self, checked):
        for checkbox in self.dup_column_checkboxes:
            checkbox.setChecked(checked)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            # Update file path in UI
            self.csv_file = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            
            # Reset operations history
            self.operations_history = []
            self.update_history_label()
            
            # Create processing dialog
            progress_dialog = ProcessingDialog(self, "Loading CSV file, please wait...")
            progress_dialog.set_progress(10)
            progress_dialog.show()
            QApplication.processEvents()
            
            try:
                # Load the file using the original function
                self.df = main.load_csv(file_path)
                self.original_df = self.df.clone()  # Store a copy of the original data
                progress_dialog.set_progress(80)
                progress_dialog.set_message("Updating UI...")
                QApplication.processEvents()
                
                if self.df is not None:
                    # Update column lists
                    self.columns_list.clear()
                    self.dup_columns_list.clear()
                    self.fr_column_combo.clear()
                    
                    # Clear existing checkboxes
                    for checkbox in self.column_checkboxes:
                        checkbox.deleteLater()
                    self.column_checkboxes = []
                    
                    for checkbox in self.dup_column_checkboxes:
                        checkbox.deleteLater()
                    self.dup_column_checkboxes = []
                    
                    # Create scrolling area with checkboxes
                    scroll_widget = self.findChild(QWidget, "columns_scroll")
                    scroll_layout = scroll_widget.layout()
                    
                    dup_scroll_widget = self.findChild(QWidget, "dup_columns_scroll")
                    dup_scroll_layout = dup_scroll_widget.layout()
                    
                    # Add columns with checkboxes
                    for col in self.df.columns:
                        # Add to original lists (keep for compatibility)
                        self.columns_list.addItem(col)
                        self.dup_columns_list.addItem(col)
                        self.fr_column_combo.addItem(col)
                        
                        # Add checkboxes for word match
                        checkbox = QCheckBox(col)
                        checkbox.setObjectName(f"col_checkbox_{col}")
                        self.column_checkboxes.append(checkbox)
                        scroll_layout.addWidget(checkbox)
                        
                        # Add checkboxes for duplicate removal
                        dup_checkbox = QCheckBox(col)
                        dup_checkbox.setObjectName(f"dup_col_checkbox_{col}")
                        self.dup_column_checkboxes.append(dup_checkbox)
                        dup_scroll_layout.addWidget(dup_checkbox)
                    
                    # Add stretches to keep checkboxes at top
                    scroll_layout.addStretch()
                    dup_scroll_layout.addStretch()
                    
                    # Show preview
                    preview_df = self.df.head(100)
                    self.table_model.setDataFrame(preview_df)
                    self.table_view.resizeColumnsToContents()
                    
                    # Update status information
                    self.status_label.setText("File loaded successfully")
                    self.results_title.setText(f"Data Preview - {os.path.basename(file_path)}")
                    self.row_count_label.setText(f"Rows: {self.df.shape[0]} | Columns: {self.df.shape[1]}")
                    
                    # Enable select all checkboxes
                    self.select_all_checkbox.setEnabled(True)
                    self.select_all_dup_checkbox.setEnabled(True)
                    self.reset_button.setEnabled(False)
                    self.download_button.setEnabled(False)
                
                progress_dialog.set_progress(100)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
            finally:
                progress_dialog.close()
    
    def apply_word_match(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        # Get selected columns from checkboxes
        selected_column_names = []
        for checkbox in self.column_checkboxes:
            if checkbox.isChecked():
                selected_column_names.append(checkbox.text())
        
        if not selected_column_names:
            QMessageBox.warning(self, "Warning", "Please select at least one column")
            return
        
        # Get search values
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "Warning", "Please enter search values")
            return
        
        search_values = [value.strip() for value in search_text.split(',')]
        include = self.include_radio.isChecked()
        case_insensitive = self.case_insensitive_checkbox.isChecked()
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Applying word match filter, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Implement case-insensitive search with polars
            progress_dialog.set_progress(30)
            progress_dialog.set_message("Filtering data...")
            QApplication.processEvents()
            
            # Create a search pattern for each value with case handling
            if not case_insensitive:
                # Case sensitive search using the original method
                search_pattern = "|".join(search_values)
                masks = [pl.col(col).cast(str).str.contains(search_pattern) for col in selected_column_names]
            else:
                # Case insensitive search - convert everything to lowercase
                masks = []
                for col in selected_column_names:
                    col_masks = [pl.col(col).cast(str).str.to_lowercase().str.contains(val.lower()) 
                                for val in search_values]
                    # Combine masks for this column with OR
                    masks.append(pl.any_horizontal(col_masks))
            
            # Combine all column masks with OR
            mask = pl.any_horizontal(masks)
            
            # Apply filter
            filtered_df = self.df.filter(mask if include else ~mask)
            
            # Update the current dataframe
            self.df = filtered_df
            self.row_count = filtered_df.shape[0]
            
            progress_dialog.set_progress(80)
            progress_dialog.set_message("Updating results view...")
            QApplication.processEvents()
            
            # Store operation in history
            filter_type = "including" if include else "excluding"
            case_str = "case insensitive" if case_insensitive else "case sensitive"
            op_description = f"Word match {filter_type} '{search_text}' ({case_str})"
            self.operations_history.append(op_description)
            self.update_history_label()
            
            # Show preview of results
            preview_df = self.df.head(100)
            self.table_model.setDataFrame(preview_df)
            self.table_view.resizeColumnsToContents()
            
            # Update status information
            cols_display = ", ".join(selected_column_names[:3])
            if len(selected_column_names) > 3:
                cols_display += f" and {len(selected_column_names) - 3} more"
            
            values_display = ", ".join([f"'{v}'" for v in search_values[:3]])
            if len(search_values) > 3:
                values_display += f" and {len(search_values) - 3} more"
            
            self.status_label.setText(f"Word match applied {filter_type} {values_display} in columns: {cols_display}")
            self.results_title.setText("Filtered Data Preview")
            self.row_count_label.setText(f"Rows: {self.row_count} | Columns: {self.df.shape[1]}")
            self.download_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying word match: {str(e)}")
        finally:
            progress_dialog.close()
    
    def apply_remove_duplicates(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        # Get selected columns from checkboxes
        selected_column_names = []
        for checkbox in self.dup_column_checkboxes:
            if checkbox.isChecked():
                selected_column_names.append(checkbox.text())
        
        if not selected_column_names:
            QMessageBox.warning(self, "Warning", "Please select at least one column")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Removing duplicates, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Process using the dataframe we currently have (could be filtered already)
            progress_dialog.set_progress(30)
            progress_dialog.set_message("Identifying and removing duplicates...")
            QApplication.processEvents()
            
            # Store row count before deduplication
            before_count = self.df.shape[0]
            
            # Remove duplicates
            cleaned_df = self.df.unique(subset=selected_column_names)
            
            # Update the current dataframe
            self.df = cleaned_df
            self.row_count = cleaned_df.shape[0]
            
            # Calculate removed rows
            removed_count = before_count - self.row_count
            
            progress_dialog.set_progress(80)
            progress_dialog.set_message("Updating results view...")
            QApplication.processEvents()
            
            # Store operation in history
            cols_display = ", ".join(selected_column_names[:3])
            if len(selected_column_names) > 3:
                cols_display += f" and {len(selected_column_names) - 3} more"
            
            op_description = f"Removed {removed_count} duplicates based on {cols_display}"
            self.operations_history.append(op_description)
            self.update_history_label()
            
            # Show preview of results
            preview_df = self.df.head(100)
            self.table_model.setDataFrame(preview_df)
            self.table_view.resizeColumnsToContents()
            
            # Update status information
            self.status_label.setText(f"Removed {removed_count} duplicate rows based on columns: {cols_display}")
            self.results_title.setText("Processed Data Preview")
            self.row_count_label.setText(f"Rows: {self.row_count} | Columns: {self.df.shape[1]}")
            self.download_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error removing duplicates: {str(e)}")
        finally:
            progress_dialog.close()
    
    def update_history_label(self):
        if not self.operations_history:
            self.history_label.setText("Operations: None")
        else:
            history_text = "Operations: " + " → ".join(self.operations_history)
            self.history_label.setText(history_text)
    
    def reset_to_original(self):
        if self.original_df is not None:
            # Reset to original data
            self.df = self.original_df.clone()
            self.row_count = self.df.shape[0]
            
            # Clear operations history
            self.operations_history = []
            self.update_history_label()
            
            # Update view
            preview_df = self.df.head(100)
            self.table_model.setDataFrame(preview_df)
            self.table_view.resizeColumnsToContents()
            
            # Update status
            self.status_label.setText("Reset to original data")
            self.results_title.setText("Original Data Preview")
            self.row_count_label.setText(f"Rows: {self.row_count} | Columns: {self.df.shape[1]}")
            self.reset_button.setEnabled(False)
    
    def download_result(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "No results to download")
            return
        
        # Create column selection dialog
        column_dialog = QDialog(self)
        column_dialog.setObjectName("column_export_dialog")
        column_dialog.setWindowTitle("Select Columns to Export")
        column_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(column_dialog)
        dialog_layout.setContentsMargins(20, 20, 20, 20)
        dialog_layout.setSpacing(15)
        
        # Column selection header
        header_label = QLabel("Select columns to include in export:")
        dialog_layout.addWidget(header_label)
        
        # Scrollable area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Box)
        scroll_area.setMaximumHeight(300)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(2)
        scroll_layout.setAlignment(Qt.AlignTop)
        
        # Add checkboxes for each column
        column_checkboxes = []
        for col in self.df.columns:
            checkbox = QCheckBox(col)
            checkbox.setChecked(True)  # Select by default
            column_checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
        
        scroll_area.setWidget(scroll_content)
        dialog_layout.addWidget(scroll_area)
        
        # Select all / Deselect all options
        check_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.setObjectName("select_all_btn")
        select_all_btn.clicked.connect(lambda: [cb.setChecked(True) for cb in column_checkboxes])
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.setObjectName("deselect_all_btn")
        deselect_all_btn.clicked.connect(lambda: [cb.setChecked(False) for cb in column_checkboxes])
        
        check_layout.addWidget(select_all_btn)
        check_layout.addWidget(deselect_all_btn)
        dialog_layout.addLayout(check_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        button_box.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(column_dialog.reject)
        
        export_btn = QPushButton("Export")
        export_btn.setObjectName("export_btn")
        export_btn.setDefault(True)
        export_btn.clicked.connect(column_dialog.accept)
        
        button_box.addWidget(cancel_btn)
        button_box.addWidget(export_btn)
        dialog_layout.addLayout(button_box)
        
        # Show dialog
        if column_dialog.exec_() != QDialog.Accepted:
            return
        
        # Get selected columns
        selected_columns = [cb.text() for cb in column_checkboxes if cb.isChecked()]
        
        if not selected_columns:
            QMessageBox.warning(self, "Warning", "Please select at least one column to export")
            return
        
        # Get file path
        suggested_name = os.path.splitext(os.path.basename(self.csv_file))[0] + "_processed.csv"
        save_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", suggested_name, "CSV Files (*.csv)")
        if not save_path:
            return
            
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Saving CSV file, please wait...")
        progress_dialog.set_progress(30)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Export only selected columns
            export_df = self.df.select(selected_columns)
            export_df.write_csv(save_path)
            
            progress_dialog.set_progress(100)
            progress_dialog.close()
            
            QMessageBox.information(
                self, 
                "Success", 
                f"File saved successfully to:\n{save_path}\n\nRows: {export_df.shape[0]}\nColumns: {len(selected_columns)}"
            )
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")
    
    def apply_find_replace(self):
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        # Get selected column
        column_name = self.fr_column_combo.currentText()
        if not column_name:
            QMessageBox.warning(self, "Warning", "Please select a column")
            return
        
        # Get find and replace values
        old_value = self.find_input.text().strip()
        new_value = self.replace_input.text().strip()
        
        if not new_value:
            QMessageBox.warning(self, "Warning", "Please enter a replacement value")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Applying find and replace, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            progress_dialog.set_progress(50)
            progress_dialog.set_message("Updating data...")
            QApplication.processEvents()
            
            # Create a copy of the dataframe to work with
            result_df = self.df.clone()
            
            # Determine column data type
            col_dtype = result_df.schema[column_name]
            print(f"Column data type: {col_dtype}")
            
            # Handle null values first if needed
            if not old_value:
                result_df = result_df.with_columns(
                    pl.col(column_name).fill_null(new_value)
                )
            else:
                # Convert both sides to strings for comparison
                expr = (
                    pl.when(pl.col(column_name).is_not_null())
                    .then(
                        pl.when(pl.col(column_name).cast(pl.Utf8).eq(old_value))
                        .then(pl.lit(new_value))
                        .otherwise(pl.col(column_name))
                    )
                    .otherwise(pl.col(column_name))
                )
                
                result_df = result_df.with_columns([
                    expr.alias(column_name)
                ])
            
            # Update the current dataframe
            self.df = result_df
            
            progress_dialog.set_progress(80)
            progress_dialog.set_message("Updating results view...")
            QApplication.processEvents()
            
            # Store operation in history
            if old_value:
                op_description = f"Replaced '{old_value}' with '{new_value}' in column '{column_name}'"
            else:
                op_description = f"Replaced NULL values with '{new_value}' in column '{column_name}'"
            
            self.operations_history.append(op_description)
            self.update_history_label()
            
            # Show preview of results
            preview_df = self.df.head(100)
            self.table_model.setDataFrame(preview_df)
            self.table_view.resizeColumnsToContents()
            
            # Update status information
            self.status_label.setText(op_description)
            self.results_title.setText("Processed Data Preview")
            self.row_count_label.setText(f"Rows: {self.df.shape[0]} | Columns: {self.df.shape[1]}")
            self.download_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying find and replace: {str(e)}")
        finally:
            progress_dialog.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())