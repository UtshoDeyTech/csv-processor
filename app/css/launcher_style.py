"""
CSS styling for the CSV Processor Launcher window.
"""

TITLE_STYLE = """
    font-size: 24px;
    font-weight: bold;
    color: #4285f4;
    margin-bottom: 10px;
"""

SUBTITLE_STYLE = """
    font-size: 16px;
    color: #666;
    margin-bottom: 20px;
"""

FRAME_STYLE = """
    QFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background-color: #f8f9fa;
    }
    QFrame:hover {
        background-color: #e8f0fe;
        border-color: #4285f4;
    }
"""

OPTION_TITLE_STYLE = "font-size: 18px; font-weight: bold; color: #4285f4;"

OPTION_DESC_STYLE = "color: #333; margin-bottom: 15px;"

BUTTON_STYLE = """
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
"""

FOOTER_STYLE = "color: #999; font-size: 12px;"