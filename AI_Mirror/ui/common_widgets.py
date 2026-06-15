from PySide6.QtWidgets import QPushButton


def create_map_button():
    button = QPushButton("Find in Store")
    button.setFixedSize(230, 55)
    button.setStyleSheet("""
        QPushButton {
            font-size: 18px;
            font-weight: bold;
            background-color: #2d89ef;
            color: white;
            border-radius: 14px;
        }
        QPushButton:hover {
            background-color: #1b5fbd;
        }
    """)
    return button