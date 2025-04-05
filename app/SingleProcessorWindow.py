import os
import polars as pl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QFrame,
                             QWidget, QTabWidget, QMessageBox, QFileDialog, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent

import app.main as main  # Import the original main.py functionality
from app.css.styles import STYLESHEET

from app.ProcessingDialog import ProcessingDialog
from app.components.HeaderFrame import HeaderFrame
from app.components.WordMatchTab import WordMatchTab
from app.components.DuplicateTab import DuplicateTab
from app.components.FindReplaceTab import FindReplaceTab
from app.components.EmailValidationTab import EmailValidationTab
from app.components.DomainSimilarityTab import DomainSimilarityTab
from app.components.ResultsFrame import ResultsFrame
from app.dialogs.ExportDialog import ExportDialog


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
        self.operation_states = []  # Store dataframe states for undo
        
        # Initialize UI components
        self.header_frame = None
        self.word_match_tab = None
        self.duplicate_tab = None
        self.find_replace_tab = None
        self.results_frame = None
        self.splitter = None  # Add splitter as class attribute
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header area with app title and file selection
        self.header_frame = HeaderFrame(self)
        main_layout.addWidget(self.header_frame)
        
        # Create a splitter for the main content (better than QHBoxLayout for maintaining proportions)
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Operations panel
        operations_panel = QWidget()
        operations_layout = QVBoxLayout(operations_panel)
        operations_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for operations
        self.tab_widget = QTabWidget()
        
        # Word Match Tab
        self.word_match_tab = WordMatchTab(self)
        self.tab_widget.addTab(self.word_match_tab, "Word Match")
        
        # Duplicate Remover Tab
        self.duplicate_tab = DuplicateTab(self)
        self.tab_widget.addTab(self.duplicate_tab, "Duplicate Remover")
        
        # Find and Replace Tab
        self.find_replace_tab = FindReplaceTab(self)
        self.tab_widget.addTab(self.find_replace_tab, "Find and Replace")
        
        # Email Validation Tab
        self.email_validation_tab = EmailValidationTab(self)
        self.tab_widget.addTab(self.email_validation_tab, "Unformatted Email")
        
        # Domain Similarity Tab
        self.domain_similarity_tab = DomainSimilarityTab(self)
        self.tab_widget.addTab(self.domain_similarity_tab, "Domain Similarity")
        
        operations_layout.addWidget(self.tab_widget)
        
        # Right side - Results panel with border and styling
        results_container = QFrame()
        results_container.setFrameShape(QFrame.StyledPanel)
        results_container.setObjectName("results_container")
        results_container_layout = QVBoxLayout(results_container)
        results_container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add results frame to container
        self.results_frame = ResultsFrame(self)
        results_container_layout.addWidget(self.results_frame)
        
        # Add both panels to the splitter
        self.splitter.addWidget(operations_panel)
        self.splitter.addWidget(results_container)
        
        # Set initial sizes (60% for operations, 40% for results)
        self.splitter.setSizes([60, 40])
        
        # Add the splitter to the main layout
        main_layout.addWidget(self.splitter)
        
        # Set stretch factor to maintain proportions
        self.reset_splitter_sizes()
    
    def reset_splitter_sizes(self):
        """Reset splitter to the original 60/40 proportion"""
        total_width = self.splitter.width()
        self.splitter.setSizes([int(total_width * 0.6), int(total_width * 0.4)])
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize events to adjust the UI for responsiveness"""
        super().resizeEvent(event)
        
        # Get the current window size
        width = event.size().width()
        
        # Check if UI components are initialized
        if not hasattr(self, 'word_match_tab') or not hasattr(self, 'duplicate_tab'):
            return
        
        if self.word_match_tab is None or self.duplicate_tab is None:
            return
        
        # Check if UI components have the required attributes
        if not hasattr(self.word_match_tab, 'columns_scroll') or not hasattr(self.duplicate_tab, 'dup_columns_scroll'):
            return
                
        # Adjust UI elements based on window size
        if width < 800:  # Small screen
            # Make column lists taller and narrower
            if self.word_match_tab.columns_scroll:
                self.word_match_tab.columns_scroll.setMaximumWidth(200)
            if self.duplicate_tab.dup_columns_scroll:
                self.duplicate_tab.dup_columns_scroll.setMaximumWidth(200)
        else:  # Large screen
            # Reset to default
            if self.word_match_tab.columns_scroll:
                self.word_match_tab.columns_scroll.setMaximumWidth(16777215)  # Default max width
            if self.duplicate_tab.dup_columns_scroll:
                self.duplicate_tab.dup_columns_scroll.setMaximumWidth(16777215)  # Default max width
        
        # Adjust table columns
        if hasattr(self, 'results_frame') and self.results_frame and hasattr(self.results_frame, 'table_view'):
            self.results_frame.table_view.resizeColumnsToContents()
        
        # Reset splitter sizes to maintain proportions on resize
        self.reset_splitter_sizes()
    
    def load_csv_file(self, file_path):
        """Load CSV file and setup UI with data"""
        self.csv_file = file_path
        
        # Reset operations history and states
        self.operations_history = []
        self.operation_states = []
        self.results_frame.update_history(self.operations_history)
        
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
                self.word_match_tab.update_columns(self.df.columns)
                self.duplicate_tab.update_columns(self.df.columns)
                self.find_replace_tab.update_columns(self.df.columns)
                self.email_validation_tab.update_columns(self.df.columns)
                self.domain_similarity_tab.update_columns(self.df.columns)
                
                # Update results frame
                self.results_frame.update_preview(self.df)
                self.results_frame.update_status("File loaded successfully")
                self.results_frame.update_title(f"Data Preview - {os.path.basename(file_path)}")
                self.results_frame.enable_buttons(reset=False, download=False, undo=False)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load CSV file: {str(e)}")
        finally:
            progress_dialog.close()
            # Reset splitter proportions
            self.reset_splitter_sizes()
    
    def apply_word_match_filter(self, selected_column_names, search_text, include, case_insensitive):
        """Apply word match filter to the data"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        if not selected_column_names:
            QMessageBox.warning(self, "Warning", "Please select at least one column")
            return
        
        if not search_text:
            QMessageBox.warning(self, "Warning", "Please enter search values")
            return
        
        search_values = [value.strip() for value in search_text.split(',')]
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Applying word match filter, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Save the current state for undo
            self.operation_states.append(self.df.clone())
            
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
            
            # Update results frame
            self.results_frame.update_history(self.operations_history)
            self.results_frame.update_preview(self.df)
            
            # Update status information
            cols_display = ", ".join(selected_column_names[:3])
            if len(selected_column_names) > 3:
                cols_display += f" and {len(selected_column_names) - 3} more"
            
            values_display = ", ".join([f"'{v}'" for v in search_values[:3]])
            if len(search_values) > 3:
                values_display += f" and {len(search_values) - 3} more"
            
            self.results_frame.update_status(f"Word match applied {filter_type} {values_display} in columns: {cols_display}")
            self.results_frame.update_title("Filtered Data Preview")
            self.results_frame.enable_buttons(reset=True, download=True, undo=True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying word match: {str(e)}")
        finally:
            progress_dialog.close()
            # Reset splitter proportions
            self.reset_splitter_sizes()
    
    def apply_remove_duplicates_filter(self, selected_column_names):
        """Apply duplicate removal filter to the data"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        if not selected_column_names:
            QMessageBox.warning(self, "Warning", "Please select at least one column")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Removing duplicates, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Save the current state for undo
            self.operation_states.append(self.df.clone())
            
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
            
            # Update results frame
            self.results_frame.update_history(self.operations_history)
            self.results_frame.update_preview(self.df)
            self.results_frame.update_status(f"Removed {removed_count} duplicate rows based on columns: {cols_display}")
            self.results_frame.update_title("Processed Data Preview")
            self.results_frame.enable_buttons(reset=True, download=True, undo=True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error removing duplicates: {str(e)}")
        finally:
            progress_dialog.close()
            # Reset splitter proportions
            self.reset_splitter_sizes()
    
    def apply_find_replace_filter(self, column_name, old_value, new_value):
        """Apply find and replace to the data"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        if not column_name:
            QMessageBox.warning(self, "Warning", "Please select a column")
            return
        
        if not new_value:
            QMessageBox.warning(self, "Warning", "Please enter a replacement value")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Applying find and replace, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Save the current state for undo
            self.operation_states.append(self.df.clone())
            
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
            
            # Update results frame
            self.results_frame.update_history(self.operations_history)
            self.results_frame.update_preview(self.df)
            self.results_frame.update_status(op_description)
            self.results_frame.update_title("Processed Data Preview")
            self.results_frame.enable_buttons(reset=True, download=True, undo=True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying find and replace: {str(e)}")
        finally:
            progress_dialog.close()
            # Reset splitter proportions
            self.reset_splitter_sizes()
    
    def apply_email_validation_filter(self, column_name):
        """Remove rows with invalid email formats"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        if not column_name:
            QMessageBox.warning(self, "Warning", "Please select a column")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Validating emails, please wait...")
        progress_dialog.set_progress(20)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Save the current state for undo
            self.operation_states.append(self.df.clone())
            
            progress_dialog.set_progress(30)
            progress_dialog.set_message("Validating emails...")
            QApplication.processEvents()
            
            # Store row count before filtering
            before_count = self.df.shape[0]
            
            # Use the main.py function to filter valid emails
            valid_emails = main.filter_valid_emails(self.df, column_name)
            
            # Update the current dataframe
            self.df = valid_emails
            self.row_count = valid_emails.shape[0]
            
            # Calculate removed rows
            removed_count = before_count - self.row_count
            
            progress_dialog.set_progress(80)
            progress_dialog.set_message("Updating results view...")
            QApplication.processEvents()
            
            # Store operation in history
            op_description = f"Removed {removed_count} rows with invalid emails in column '{column_name}'"
            self.operations_history.append(op_description)
            
            # Update results frame
            self.results_frame.update_history(self.operations_history)
            self.results_frame.update_preview(self.df)
            self.results_frame.update_status(op_description)
            self.results_frame.update_title("Processed Data Preview")
            self.results_frame.enable_buttons(reset=True, download=True, undo=True)
            
            progress_dialog.set_progress(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error validating emails: {str(e)}")
        finally:
            progress_dialog.close()
            # Reset splitter proportions
            self.reset_splitter_sizes()
            
    def apply_domain_similarity_filter(self, email_column, domain_column, threshold=0.75, check_username=True):
        """Apply domain similarity filter to the data"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "Please load a CSV file first")
            return
        
        if not email_column or not domain_column:
            QMessageBox.warning(self, "Warning", "Please select both email and domain columns")
            return
        
        # Show processing dialog
        progress_dialog = ProcessingDialog(self, "Analyzing domain similarity, please wait...")
        progress_dialog.set_progress(0)
        progress_dialog.show()
        QApplication.processEvents()
        
        try:
            # Save the current state for undo
            self.operation_states.append(self.df.clone())
            
            # Define progress callback
            def update_progress(percent, message):
                progress_dialog.set_progress(percent)
                progress_dialog.set_message(message)
                QApplication.processEvents()
                
            # Apply domain similarity filter with progress updates
            filtered_df = main.domain_similarity_filter(
                self.df, 
                email_column, 
                domain_column, 
                threshold,
                check_username,
                update_progress
            )
            
            # Update the current dataframe
            self.df = filtered_df
            self.row_count = filtered_df.shape[0]
            
            # Store operation in history
            check_username_str = "checked email usernames" if check_username else "checked domains only"
            op_description = f"Found {self.row_count} emails with {int(threshold*100)}% domain similarity ({check_username_str})"
            self.operations_history.append(op_description)
            
            # Update results frame
            self.results_frame.update_history(self.operations_history)
            self.results_frame.update_preview(self.df)
            self.results_frame.update_status(f"Found {self.row_count} emails with domain similarity >= {int(threshold*100)}%")
            self.results_frame.update_title("Domain Similarity Results")
            self.results_frame.enable_buttons(reset=True, download=True, undo=True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error analyzing domain similarity: {str(e)}")
        finally:
            progress_dialog.close()
            # Reset splitter proportions
            self.reset_splitter_sizes()
    
    def reset_to_original_data(self):
        """Reset to original data"""
        if self.original_df is not None:
            # Reset to original data
            self.df = self.original_df.clone()
            self.row_count = self.df.shape[0]
            
            # Clear operations history and states
            self.operations_history = []
            self.operation_states = []
            
            # Update results frame
            self.results_frame.update_history(self.operations_history)
            self.results_frame.update_preview(self.df)
            self.results_frame.update_status("Reset to original data")
            self.results_frame.update_title("Original Data Preview")
            self.results_frame.enable_buttons(reset=False, download=False, undo=False)
            
            # Reset splitter proportions
            self.reset_splitter_sizes()
    
    def download_result_data(self):
        """Export filtered data to CSV file"""
        if self.df is None:
            QMessageBox.warning(self, "Warning", "No results to download")
            return
        
        # Create column selection dialog
        export_dialog = ExportDialog(self, self.df.columns)
        
        # Show dialog
        if export_dialog.exec_() != export_dialog.Accepted:
            return
        
        # Get selected columns
        selected_columns = export_dialog.get_selected_columns()
        
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
            
    def undo_last_operation(self):
        """Undo the last operation"""
        if not self.operations_history:
            QMessageBox.information(self, "Info", "No operations to undo")
            return
            
        # Get the last operation
        last_op = self.operations_history.pop()
        
        # If we have operations history but no saved states, create one for original
        if self.operation_states and len(self.operations_history) >= len(self.operation_states):
            # This shouldn't normally happen, but just in case
            self.operation_states.insert(0, self.original_df.clone())
        
        # If there are no operations left, restore original dataframe
        if not self.operations_history:
            self.df = self.original_df.clone()
            self.results_frame.update_status(f"Undid operation: {last_op}")
            self.results_frame.update_title("Original Data Preview")
            self.results_frame.enable_buttons(reset=False, download=False, undo=False)
        else:
            # Get the previous dataframe state
            self.df = self.operation_states.pop()
            self.results_frame.update_status(f"Undid operation: {last_op}")
            self.results_frame.update_title("Processed Data Preview")
            self.results_frame.enable_buttons(reset=True, download=True, undo=True)
        
        # Update the UI
        self.results_frame.update_history(self.operations_history)
        self.results_frame.update_preview(self.df)
        
        # Reset splitter proportions
        self.reset_splitter_sizes()