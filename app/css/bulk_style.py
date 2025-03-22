# CSS styling for the CSV Bulk Processor application
BULK_STYLESHEET = """
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

/* Results styling */
#results_title {
    font-size: 16px;
    font-weight: bold;
    color: #4285f4;
    padding: 5px 0;
}

#status_label {
    font-style: italic;
    color: #666666;
    padding: 5px 0;
}

/* Panel styling */
#left_panel, #results_container {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
}

/* Drop area styling */
#drop_area {
    border: 2px dashed #aaa;
    border-radius: 5px;
    background-color: #f8f8f8;
    padding: 15px;
    margin-bottom: 10px;
}

#drop_area:hover {
    border-color: #4285f4;
    background-color: #e8f0fe;
}

/* Special buttons */
#reset_button {
    background-color: #f5f5f5;
    color: #333333;
    border: 1px solid #e0e0e0;
}

#reset_button:hover {
    background-color: #e0e0e0;
}

/* Processing dialog */
#processing_dialog {
    background-color: white;
    border-radius: 5px;
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

/* File list item styling */
#file_item {
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 3px;
    margin: 2px 0;
    padding: 5px;
}

#file_item:hover {
    background-color: #e8f0fe;
}

#file_name {
    font-weight: bold;
    color: #333;
}

#file_size {
    color: #666;
    font-size: 12px;
}

#remove_file_button {
    background-color: #f0f0f0;
    border-radius: 12px;
    border: none;
    color: #666;
    font-weight: bold;
    font-size: 16px;
    min-height: 24px;
    min-width: 24px;
    padding: 0;
}

#remove_file_button:hover {
    background-color: #e0e0e0;
    color: #333;
}
"""