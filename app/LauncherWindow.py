import sys
import os
import subprocess
import psutil
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QFrame, QMessageBox)
from PyQt5.QtCore import Qt

class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Processor Launcher")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("CSV Processor")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #4285f4;
            margin-bottom: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Select the processing mode you need")
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Buttons container
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(20)
        
        # Single file processor
        single_frame = QFrame()
        single_frame.setFrameShape(QFrame.StyledPanel)
        single_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QFrame:hover {
                background-color: #e8f0fe;
                border-color: #4285f4;
            }
        """)
        
        single_layout = QVBoxLayout(single_frame)
        single_layout.setContentsMargins(20, 20, 20, 20)
        
        single_title = QLabel("Single File Processor")
        single_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4285f4;")
        single_layout.addWidget(single_title)
        
        single_desc = QLabel("Process one CSV file at a time with operations like word matching, duplicate removal, and find & replace.")
        single_desc.setWordWrap(True)
        single_desc.setStyleSheet("color: #333; margin-bottom: 15px;")
        single_layout.addWidget(single_desc)
        
        single_button = QPushButton("Launch Single File Processor")
        single_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3b78e7;
            }
            QPushButton:pressed {
                background-color: #3367d6;
            }
        """)
        single_button.clicked.connect(self.launch_single_processor)
        single_layout.addWidget(single_button)
        
        buttons_container.addWidget(single_frame)
        
        # Multiple files processor
        multi_frame = QFrame()
        multi_frame.setFrameShape(QFrame.StyledPanel)
        multi_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QFrame:hover {
                background-color: #e8f0fe;
                border-color: #4285f4;
            }
        """)
        
        multi_layout = QVBoxLayout(multi_frame)
        multi_layout.setContentsMargins(20, 20, 20, 20)
        
        multi_title = QLabel("Multiple Files Processor")
        multi_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4285f4;")
        multi_layout.addWidget(multi_title)
        
        multi_desc = QLabel("Work with multiple CSV files at once for operations like merging files and subtracting one file from another.")
        multi_desc.setWordWrap(True)
        multi_desc.setStyleSheet("color: #333; margin-bottom: 15px;")
        multi_layout.addWidget(multi_desc)
        
        multi_button = QPushButton("Launch Multiple Files Processor")
        multi_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3b78e7;
            }
            QPushButton:pressed {
                background-color: #3367d6;
            }
        """)
        multi_button.clicked.connect(self.launch_bulk_processor)
        multi_layout.addWidget(multi_button)
        
        buttons_container.addWidget(multi_frame)
        main_layout.addLayout(buttons_container)
        
        # Footer
        footer = QLabel("CSV Processor v1.0")
        footer.setStyleSheet("color: #999; font-size: 12px;")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
    
    def is_script_running(self, script_name):
        """Check if a Python script is already running"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                    cmdline = proc.info['cmdline']
                    if cmdline and len(cmdline) > 1 and script_name in cmdline[1]:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    
    def launch_single_processor(self):
        """Launch the single file processor"""
        if not self.is_script_running("main_single_processor.py"):
            # Start process detached from parent
            if sys.platform == 'win32':
                # Windows - use subprocess with CREATE_NEW_PROCESS_GROUP flag
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen(
                    [sys.executable, "main_single_processor.py"],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    startupinfo=startupinfo
                )
            else:
                # Unix-like systems
                subprocess.Popen(
                    [sys.executable, "main_single_processor.py"],
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )

    def launch_bulk_processor(self):
        """Launch the bulk processor"""
        if not self.is_script_running("main_bulk_processor.py"):
            # Start process detached from parent
            if sys.platform == 'win32':
                # Windows - use subprocess with CREATE_NEW_PROCESS_GROUP flag
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen(
                    [sys.executable, "main_bulk_processor.py"],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    startupinfo=startupinfo
                )
            else:
                # Unix-like systems
                subprocess.Popen(
                    [sys.executable, "main_bulk_processor.py"],
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None
                )
    
    def run_python_script(self, script_path):
        """Run a Python script in a new process"""
        try:
            # Get the Python executable path currently running
            python_exe = sys.executable
            
            # Run the script as a separate process
            subprocess.Popen([python_exe, script_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error launching script: {e}")