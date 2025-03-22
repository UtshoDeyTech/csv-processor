import os
import polars as pl
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QTabWidget,
                            QTableView, QHeaderView, QFrame, QComboBox,
                            QGroupBox, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from app.css.bulk_style import BULK_STYLESHEET
from app.PolarsTableModel import PolarsTableModel
from app.components.FileListWidget import FileListWidget
from app.ProcessingDialog import ProcessingDialog

class DropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("drop_area")
        self.setMinimumHeight(100)
        self.setFrameShape(QFrame.StyledPanel)
        self.setAcceptDrops(True)
        
        # Setup UI
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.drop_label = QLabel("Drop CSV files here or click Add CSV Files button", self)
        self.drop_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.drop_label)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls() and self._has_valid_csv_files(event.mimeData()):
            event.acceptProposedAction()
            self.setStyleSheet("""
                #drop_area {
                    border: 2px dashed #4285f4;
                    border-radius: 5px;
                    background-color: #e8f0fe;
                }
            """)
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("")  # Reset to stylesheet from parent
        event.accept()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        if event.mimeData().hasUrls() and self._has_valid_csv_files(event.mimeData()):
            # Get list of CSV file paths
            file_paths = []
            for url in event.mimeData().urls():
                local_file = url.toLocalFile()
                if local_file.lower().endswith('.csv'):
                    file_paths.append(local_file)
            
            event.acceptProposedAction()
            
            # Reset style
            self.setStyleSheet("")  # Reset to stylesheet from parent
            
            # Process the files
            if hasattr(self.parent, 'process_files') and callable(self.parent.process_files):
                self.parent.process_files(file_paths)
    
    def _has_valid_csv_files(self, mime_data: QMimeData):
        """Check if the dragged files include valid CSV files"""
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.toLocalFile().lower().endswith('.csv'):
                    return True
        return False

class BulkProcessorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Bulk Processor")
        self.setMinimumSize(1200, 800)
        
        # Maximize window
        self.showMaximized()
        
        # Apply stylesheet
        self.setStyleSheet(BULK_STYLESHEET)
        
        # State variables
        self.csv_files = []
        self.df_map = {}  # Map of filename to DataFrame
        self.result_df = None
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with title
        header = QFrame()
        header.setObjectName("header_frame")
        header_layout = QHBoxLayout(header)
        
        title = QLabel("CSV Bulk Processor")
        title.setObjectName("app_title")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        main_layout.addWidget(header)
        
        # Content area with split layout
        content_layout = QHBoxLayout()
        
        # Left panel (file selection & operations)
        left_panel = QFrame()
        left_panel.setObjectName("left_panel")
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_panel)
        
        # Add file section
        file_group = QGroupBox("CSV Files")
        file_layout = QVBoxLayout()
        
        # Drop area for files
        self.drop_area = DropArea(self)
        file_layout.addWidget(self.drop_area)
        
        # File selection buttons
        file_buttons_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Add CSV Files")
        self.add_file_button.clicked.connect(self.add_files)
        clear_button = QPushButton("Clear Files")
        clear_button.clicked.connect(self.clear_files)
        clear_button.setObjectName("reset_button")
        
        file_buttons_layout.addWidget(self.add_file_button)
        file_buttons_layout.addWidget(clear_button)
        file_layout.addLayout(file_buttons_layout)
        
        # File list
        self.file_list_widget = FileListWidget()
        self.file_list_widget.fileRemoved.connect(self.handle_file_removed)
        file_layout.addWidget(self.file_list_widget)
        
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)
        
        # Operations section
        op_group = QGroupBox("Operations")
        op_layout = QVBoxLayout()
        
        # Tabs for different operations
        self.op_tabs = QTabWidget()
        
        # Merge tab
        merge_tab = QWidget()
        merge_layout = QVBoxLayout(merge_tab)
        
        merge_info = QLabel("Merge multiple CSVs with similar column structure into a single file.")
        merge_info.setWordWrap(True)
        merge_layout.addWidget(merge_info)
        
        # Column selection for merge key
        merge_key_group = QGroupBox("Select Common Column")
        merge_key_layout = QVBoxLayout()
        merge_key_label = QLabel("Select a column to use as the common key:")
        self.merge_column_combo = QComboBox()
        
        merge_key_layout.addWidget(merge_key_label)
        merge_key_layout.addWidget(self.merge_column_combo)
        merge_key_group.setLayout(merge_key_layout)
        merge_layout.addWidget(merge_key_group)
        
        # Apply merge button
        merge_button_layout = QHBoxLayout()
        merge_button_layout.addStretch()
        self.apply_merge_button = QPushButton("Merge CSV Files")
        self.apply_merge_button.clicked.connect(self.apply_merge)
        merge_button_layout.addWidget(self.apply_merge_button)
        merge_layout.addLayout(merge_button_layout)
        merge_layout.addStretch()
        
        self.op_tabs.addTab(merge_tab, "Merge CSVs")
        
        # Subtract tab
        subtract_tab = QWidget()
        subtract_layout = QVBoxLayout(subtract_tab)
        
        subtract_info = QLabel("Subtract CSV2 from CSV1 based on a common column (e.g., remove rows with matching emails).")
        subtract_info.setWordWrap(True)
        subtract_layout.addWidget(subtract_info)
        
        # File selection for subtraction
        files_group = QGroupBox("Select Files")
        files_layout = QVBoxLayout()
        
        # File 1 selection (minuend)
        file1_layout = QHBoxLayout()
        file1_label = QLabel("File 1 (keep rows from):")
        self.file1_combo = QComboBox()
        file1_layout.addWidget(file1_label)
        file1_layout.addWidget(self.file1_combo, stretch=1)
        files_layout.addLayout(file1_layout)
        
        # File 2 selection (subtrahend)
        file2_layout = QHBoxLayout()
        file2_label = QLabel("File 2 (remove matches from):")
        self.file2_combo = QComboBox()
        file2_layout.addWidget(file2_label)
        file2_layout.addWidget(self.file2_combo, stretch=1)
        files_layout.addLayout(file2_layout)
        
        files_group.setLayout(files_layout)
        subtract_layout.addWidget(files_group)
        
        # Column selection for subtraction
        subtract_key_group = QGroupBox("Select Matching Column")
        subtract_key_layout = QVBoxLayout()
        subtract_key_label = QLabel("Select a column to match rows:")
        self.subtract_column_combo = QComboBox()
        
        subtract_key_layout.addWidget(subtract_key_label)
        subtract_key_layout.addWidget(self.subtract_column_combo)
        subtract_key_group.setLayout(subtract_key_layout)
        subtract_layout.addWidget(subtract_key_group)
        
        # Apply subtraction button
        subtract_button_layout = QHBoxLayout()
        subtract_button_layout.addStretch()
        self.apply_subtract_button = QPushButton("Subtract CSVs")
        self.apply_subtract_button.clicked.connect(self.apply_subtract)
        subtract_button_layout.addWidget(self.apply_subtract_button)
        subtract_layout.addLayout(subtract_button_layout)
        subtract_layout.addStretch()
        
        self.op_tabs.addTab(subtract_tab, "Subtract CSVs")
        
        op_layout.addWidget(self.op_tabs)
        op_group.setLayout(op_layout)
        left_layout.addWidget(op_group)
        
        # Right panel (result preview)
        right_panel = QFrame()
        right_panel.setObjectName("results_container")
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        
        # Result header
        result_header = QHBoxLayout()
        self.result_title = QLabel("Results Preview")
        self.result_title.setObjectName("results_title")
        result_header.addWidget(self.result_title)
        result_header.addStretch()
        
        # Action buttons
        self.download_button = QPushButton("Download Result")
        self.download_button.clicked.connect(self.download_result)
        self.download_button.setEnabled(False)
        result_header.addWidget(self.download_button)
        
        right_layout.addLayout(result_header)
        
        # Result status
        self.status_label = QLabel("No operation performed yet")
        self.status_label.setObjectName("status_label")
        right_layout.addWidget(self.status_label)
        
        # Results table
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_model = PolarsTableModel()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        
        right_layout.addWidget(self.table_view)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.row_count_label = QLabel("Rows: 0 | Columns: 0")
        status_layout.addWidget(self.row_count_label)
        status_layout.addStretch()
        right_layout.addLayout(status_layout)
        
        # Add panels to content layout with 40/60 split
        content_layout.addWidget(left_panel, 40)
        content_layout.addWidget(right_panel, 60)
        
        main_layout.addLayout(content_layout)
    
    def process_files(self, file_paths):
        """Process multiple CSV files"""
        if not file_paths:
            return
        
        progress_dialog = ProcessingDialog(self, "Loading CSV files, please wait...")
        progress_dialog.set_progress(0)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                # Update progress
                progress = int((i / total_files) * 100)
                progress_dialog.set_progress(progress)
                progress_dialog.set_message(f"Loading {os.path.basename(file_path)}...")
                QApplication.processEvents()
                
                # Skip if already loaded
                if file_path in self.csv_files:
                    continue
                
                # Load file
                df = self._load_csv(file_path)
                
                if df is not None:
                    self.csv_files.append(file_path)
                    self.df_map[file_path] = df
                    self.file_list_widget.add_file(file_path)
            
            # Update UI with new files
            self._update_ui_with_files()
            
            progress_dialog.set_progress(100)
            progress_dialog.set_message("Files loaded successfully")
            QApplication.processEvents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading files: {str(e)}")
        finally:
            progress_dialog.close()
    
    def add_files(self):
        """Add CSV files to the processor"""
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select CSV Files", "", "CSV Files (*.csv)")
        if file_paths:
            self.process_files(file_paths)
    
    def clear_files(self):
        """Clear all loaded files"""
        self.csv_files = []
        self.df_map = {}
        self.file_list_widget.clear()
        self._update_ui_with_files()
        
        # Clear result
        self.result_df = None
        self.table_model.setDataFrame(pl.DataFrame())
        self.row_count_label.setText("Rows: 0 | Columns: 0")
        self.status_label.setText("No operation performed yet")
        self.download_button.setEnabled(False)
    
    def handle_file_removed(self, file_path):
        """Handle file removed from list"""
        if file_path in self.csv_files:
            self.csv_files.remove(file_path)
            if file_path in self.df_map:
                del self.df_map[file_path]
            
            self._update_ui_with_files()
    
    def apply_merge(self):
        """Apply merge operation on selected CSV files"""
        if len(self.csv_files) < 2:
            QMessageBox.warning(self, "Warning", "Please add at least two CSV files to merge")
            return
        
        # Get selected column
        merge_column = self.merge_column_combo.currentText()
        if not merge_column:
            QMessageBox.warning(self, "Warning", "Please select a column for merging")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Merging CSV files, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Get all dataframes
            dataframes = [self.df_map[file] for file in self.csv_files]
            
            # Ensure all dataframes have the merge column
            if not all(merge_column in df.columns for df in dataframes):
                raise ValueError(f"Not all files have the column: {merge_column}")
            
            progress_dialog.set_progress(40)
            progress_dialog.set_message("Concatenating dataframes...")
            QApplication.processEvents()
            
            # Concatenate dataframes
            merged_df = pl.concat(dataframes, how="vertical")
            
            # Remove duplicates based on the merge column
            progress_dialog.set_progress(70)
            progress_dialog.set_message("Removing duplicates...")
            QApplication.processEvents()
            
            merged_df = merged_df.unique(subset=[merge_column])
            
            # Update result
            self.result_df = merged_df
            
            progress_dialog.set_progress(90)
            progress_dialog.set_message("Updating preview...")
            QApplication.processEvents()
            
            # Update UI
            preview_df = merged_df.head(100)
            self.table_model.setDataFrame(preview_df)
            self.table_view.resizeColumnsToContents()
            
            self.status_label.setText(f"Merged {len(self.csv_files)} files based on column '{merge_column}'")
            self.result_title.setText("Merged Data Preview")
            self.row_count_label.setText(f"Rows: {merged_df.shape[0]} | Columns: {merged_df.shape[1]}")
            self.download_button.setEnabled(True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error merging files: {str(e)}")
        finally:
            progress_dialog.close()
    
    def apply_subtract(self):
        """Apply subtraction operation (CSV1 - CSV2)"""
        if len(self.csv_files) < 2:
            QMessageBox.warning(self, "Warning", "Please add at least two CSV files for subtraction")
            return
        
        # Get selected files
        file1 = self.file1_combo.currentText()
        file2 = self.file2_combo.currentText()
        
        if not file1 or not file2:
            QMessageBox.warning(self, "Warning", "Please select both files for subtraction")
            return
        
        if file1 == file2:
            QMessageBox.warning(self, "Warning", "Please select different files for subtraction")
            return
        
        # Get full file paths
        file1_path = None
        file2_path = None
        for path in self.csv_files:
            if os.path.basename(path) == file1:
                file1_path = path
            elif os.path.basename(path) == file2:
                file2_path = path
        
        if not file1_path or not file2_path:
            QMessageBox.warning(self, "Warning", "Error finding selected files")
            return
        
        # Get selected column
        subtract_column = self.subtract_column_combo.currentText()
        if not subtract_column:
            QMessageBox.warning(self, "Warning", "Please select a column for matching")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Subtracting CSV files, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Get dataframes
            df1 = self.df_map[file1_path]
            df2 = self.df_map[file2_path]
            
            # Ensure both dataframes have the selected column
            if subtract_column not in df1.columns or subtract_column not in df2.columns:
                raise ValueError(f"Both files must have the column: {subtract_column}")
            
            progress_dialog.set_progress(40)
            progress_dialog.set_message("Performing subtraction operation...")
            QApplication.processEvents()
            
            # Get unique values from the second dataframe
            values_to_exclude = df2.select(pl.col(subtract_column)).unique().to_series()
            
            # Filter the first dataframe to exclude rows matching values from the second
            result_df = df1.filter(~pl.col(subtract_column).is_in(values_to_exclude))
            
            # Update result
            self.result_df = result_df
            
            progress_dialog.set_progress(90)
            progress_dialog.set_message("Updating preview...")
            QApplication.processEvents()
            
            # Update UI
            preview_df = result_df.head(100)
            self.table_model.setDataFrame(preview_df)
            self.table_view.resizeColumnsToContents()
            
            removed_count = df1.shape[0] - result_df.shape[0]
            self.status_label.setText(f"Removed {removed_count} rows from '{file1}' with '{subtract_column}' matching '{file2}'")
            self.result_title.setText("Subtraction Result Preview")
            self.row_count_label.setText(f"Rows: {result_df.shape[0]} | Columns: {result_df.shape[1]}")
            self.download_button.setEnabled(True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error subtracting files: {str(e)}")
        finally:
            progress_dialog.close()
    
    def download_result(self):
        """Download the result dataframe to a CSV file"""
        if self.result_df is None:
            QMessageBox.warning(self, "Warning", "No results to download")
            return
        
        # Create ExportDialog for column selection
        from app.dialogs.ExportDialog import ExportDialog
        export_dialog = ExportDialog(self, self.result_df.columns)
        
        # Show dialog
        if export_dialog.exec_() != export_dialog.Accepted:
            return
        
        # Get selected columns
        selected_columns = export_dialog.get_selected_columns()
        
        if not selected_columns:
            QMessageBox.warning(self, "Warning", "Please select at least one column to export")
            return
        
        # Get file path
        save_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "result.csv", "CSV Files (*.csv)")
        if not save_path:
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Saving CSV file, please wait...")
        progress_dialog.set_progress(30)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Select only the columns user has chosen
            export_df = self.result_df.select(selected_columns)
            
            # Save the dataframe to CSV
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
    
    def _load_csv(self, file_path):
        """Load a CSV file using polars"""
        try:
            # Load CSV using polars
            df = pl.read_csv(file_path)
            return df
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
            return None
    
    def _update_ui_with_files(self):
        """Update UI elements based on loaded files"""
        # Update file dropdown lists for subtract operation
        self.file1_combo.clear()
        self.file2_combo.clear()
        
        # Update column dropdown for merge and subtract operations
        self.merge_column_combo.clear()
        self.subtract_column_combo.clear()
        
        if not self.csv_files:
            # Disable operation buttons
            self.apply_merge_button.setEnabled(False)
            self.apply_subtract_button.setEnabled(False)
            return
        
        # Enable operation buttons
        self.apply_merge_button.setEnabled(len(self.csv_files) >= 2)
        self.apply_subtract_button.setEnabled(len(self.csv_files) >= 2)
        
        # Get common columns across all files
        common_columns = set()
        first = True
        
        for file_path, df in self.df_map.items():
            if first:
                common_columns = set(df.columns)
                first = False
            else:
                common_columns &= set(df.columns)
        
        # Add file names to dropdown lists
        for file_path in self.csv_files:
            file_name = os.path.basename(file_path)
            self.file1_combo.addItem(file_name)
            self.file2_combo.addItem(file_name)
        
        # Add common columns to dropdown lists
        for column in common_columns:
            self.merge_column_combo.addItem(column)
            self.subtract_column_combo.addItem(column)