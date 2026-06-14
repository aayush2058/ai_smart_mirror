from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from ui.common_widgets import create_map_button


class DepartmentScreen(QWidget):
    def __init__(self, on_department_selected, on_back, on_map):
        super().__init__()

        self.on_department_selected = on_department_selected
        self.on_back = on_back
        self.on_map = on_map

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(30)

        title = QLabel("Choose Department")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 42px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        grid = QGridLayout()
        grid.setSpacing(25)

        departments = [
            "Men",
            "Women",
            "Kids",
            "Decors",
            "Accessories",
            "Sale / Discounts"
        ]

        for index, department in enumerate(departments):
            button = QPushButton(department)
            button.setFixedSize(300, 140)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 26px;
                    font-weight: bold;
                    background-color: #222222;
                    color: white;
                    border: 2px solid #444444;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: #2d89ef;
                    border: 2px solid #2d89ef;
                }
            """)

            button.clicked.connect(
                lambda checked=False, d=department: self.on_department_selected(d)
            )

            row = index // 3
            col = index % 3
            grid.addWidget(button, row, col, alignment=Qt.AlignCenter)

        bottom_bar = QHBoxLayout()

        self.map_button = create_map_button()
        self.map_button.clicked.connect(self.on_map)

        back_button = QPushButton("Back")
        back_button.setFixedSize(180, 55)
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: #444444;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        back_button.clicked.connect(self.on_back)

        bottom_bar.addWidget(self.map_button, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        bottom_bar.addWidget(back_button, alignment=Qt.AlignRight)

        main_layout.addWidget(title)
        main_layout.addLayout(grid)
        main_layout.addStretch()
        main_layout.addLayout(bottom_bar)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #111111;")