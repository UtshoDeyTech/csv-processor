# CSS styling for the CSV Processor application
STYLESHEET = """
/* Global styles */
QMainWindow, QWidget {
    background-color: white;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* GroupBox styling */
QGroupBox {
    border: 1px solid #e0e0e0;
    border-radius: 3px;
    margin-top: 16px;
    padding-top: 16px;
    background-color: white;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #4285f4;
}

QLabel {
    color: #333333;
}

/* Table styling */
QTableView {
    border: 1px solid #e0e0e0;
    border-radius: 2px;
    alternate-background-color: #f9f9f9;
    gridline-color: #e5e5e5;
    selection-background-color: #4285f4;
    selection-color: white;
}

QHeaderView::section {
    background-color: #f5f5f5;
    color: #333333;
    padding: 8px;
    border: 1px solid #e0e0e0;
    font-weight: bold;
}

/* List widget styling */
QListWidget, QScrollArea {
    border: 1px solid #e0e0e0;
    border-radius: 2px;
    background-color: white;
    selection-background-color: #e8f0fe;
    selection-color: #333333;
}

QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #f5f5f5;
}

QListWidget::item:selected {
    background-color: #e8f0fe;
    color: #333333;
}

QListWidget::item:hover {
    background-color: #f5f5f5;
}

QCheckBox {
    padding: 4px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #d0d0d0;
    border-radius: 2px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #4285f4;
    border-color: #4285f4;
}

QCheckBox::indicator:hover {
    border-color: #4285f4;
}

/* Input styling */
QLineEdit, QComboBox {
    border: 1px solid #e0e0e0;
    border-radius: 2px;
    padding: 8px;
    background-color: white;
    min-height: 24px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #4285f4;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right;
    width: 20px;
    border-left: 1px solid #e0e0e0;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

/* Button styling */
QPushButton {
    background-color: #4285f4;
    color: white;
    border: none;
    border-radius: 3px;
    padding: 8px 16px;
    font-weight: normal;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #3b78e7;
}

QPushButton:pressed {
    background-color: #3367d6;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #888888;
}

/* Tab styling */
QTabWidget::pane {
    border: 1px solid #e0e0e0;
    background-color: white;
    top: -1px;
}

QTabBar::tab {
    background-color: #f5f5f5;
    padding: 10px 18px;
    border: 1px solid #e0e0e0;
    border-bottom: none;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    margin-right: 2px;
    min-width: 120px;
    text-align: center;
}

QTabBar::tab:selected {
    background-color: white;
    color: #4285f4;
    font-weight: bold;
    border-bottom: 2px solid #4285f4;
}

QTabBar::tab:hover:!selected {
    background-color: #e8f0fe;
}

/* RadioButton and Checkbox styling */
QRadioButton, QCheckBox {
    spacing: 8px;
    padding: 4px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background-color: #4285f4;
}

/* Header styling */
#header_frame {
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
    padding: 10px;
    margin-bottom: 15px;
}

#app_title {
    font-size: 18px;
    font-weight: bold;
    color: #4285f4;
}

#file_label, #file_path_label {
    padding: 0 10px;
}

#browse_button {
    background-color: #4285f4;
    color: white;
    border-radius: 3px;
    padding: 8px 16px;
}

#browse_button:hover {
    background-color: #3b78e7;
}

/* Results styling */
#results_title {
    font-size: 16px;
    font-weight: bold;
    color: #4285f4;
    padding: 5px 0;
}

#status_label, #history_label {
    font-style: italic;
    color: #666666;
    padding: 5px 0;
}

/* Action buttons */
#reset_button {
    background-color: #f5f5f5;
    color: #333333;
    border: 1px solid #e0e0e0;
}

#reset_button:hover {
    background-color: #e0e0e0;
}

#apply_word_match_button, #apply_dup_button, #apply_fr_button {
    min-width: 150px;
}

/* Processing dialog */
#processing_dialog {
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

#icon_label {
    font-size: 24px;
    color: #4285f4;
    padding: 10px;
}

#message_label {
    font-size: 14px;
    color: #333333;
    padding: 10px;
}

#progress_bar {
    border: none;
    border-radius: 3px;
    background-color: #f5f5f5;
    text-align: center;
    height: 8px;
    margin: 0 15px 15px 15px;
}

#progress_bar::chunk {
    background-color: #4285f4;
    border-radius: 3px;
}

/* Dialog styling for column selection */
QDialog#column_export_dialog {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    min-width: 400px;
}

QDialog#column_export_dialog QLabel {
    font-weight: bold;
    color: #4285f4;
    padding: 8px 0;
}

QDialog#column_export_dialog QScrollArea {
    border: 1px solid #e0e0e0;
    background-color: white;
}

QDialog#column_export_dialog QCheckBox {
    padding: 6px;
    background-color: transparent;
}

QDialog#column_export_dialog QCheckBox:hover {
    background-color: #f5f5f5;
}

QDialog#column_export_dialog QPushButton {
    border-radius: 2px;
    padding: 8px 16px;
    min-width: 100px;
}

QDialog#column_export_dialog QPushButton#cancel_btn {
    background-color: #f5f5f5;
    color: #333333;
    border: 1px solid #e0e0e0;
}

QDialog#column_export_dialog QPushButton#cancel_btn:hover {
    background-color: #e0e0e0;
}

QDialog#column_export_dialog QPushButton#export_btn {
    background-color: #4285f4;
    color: white;
}

# Add these styles to your existing STYLESHEET string

/* Split layout styling */
#results_container {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
}

/* Adjust tab width for side panel */
QTabBar::tab {
    min-width: 100px;
}

/* Make sure results frame fills its container */
#results_frame {
    background-color: transparent;
    border: none;
}

/* Style the data preview header */
#data_preview_header {
    margin-top: 5px;
    margin-bottom: 10px;
}

/* Adjust button bar in results frame */
#button_bar {
    margin: 10px 0;
    background-color: #f8f9fa;
    border-radius: 3px;
    padding: 8px;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
    QTabBar::tab {
        min-width: 80px;
        padding: 8px 12px;
    }
}
"""