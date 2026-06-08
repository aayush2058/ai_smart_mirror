from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from ui.common_widgets import create_map_button


class CategoryScreen(QWidget):
    def __init__(self, on_category_selected, on_back, on_map):
        super().__init__()

        self.on_category_selected = on_category_selected
        self.on_back = on_back
        self.on_map = on_map
        self.department = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(60, 40, 60, 40)
        self.main_layout.setSpacing(30)

        self.title = QLabel("Choose Category")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-size: 42px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.grid = QGridLayout()
        self.grid.setSpacing(25)

        bottom_bar = QHBoxLayout()

        self.map_button = create_map_button()
        self.map_button.clicked.connect(self.on_map)

        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(180, 55)
        self.back_button.setStyleSheet("""
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
        self.back_button.clicked.connect(self.on_back)

        bottom_bar.addWidget(self.map_button, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.back_button, alignment=Qt.AlignRight)

        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.grid)
        self.main_layout.addStretch()
        self.main_layout.addLayout(bottom_bar)

        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: #111111;")

    def set_department(self, department):
        self.department = department
        self.title.setText(f"{department} Categories")
        self.load_categories()

    def load_categories(self):
        self.clear_grid()

        categories = self.get_categories_for_department(self.department)

        for index, category in enumerate(categories):
            button = QPushButton(category)
            button.setFixedSize(300, 140)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 25px;
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
                lambda checked=False, c=category: self.on_category_selected(c)
            )

            row = index // 3
            col = index % 3
            self.grid.addWidget(button, row, col, alignment=Qt.AlignCenter)

    def get_categories_for_department(self, department):
        category_map = {
            "Men": [
                "Upper Fit",
                "Lower Fit",
                "Footwear",
                "Accessories",
                "Miscellaneous",
                "Discounts"
            ],
            "Women": [
                "Tops",
                "Dresses",
                "Lower Fit",
                "Footwear",
                "Bags",
                "Discounts"
            ],
            "Kids": [
                "Boys",
                "Girls",
                "Baby Clothing",
                "Footwear",
                "School Wear",
                "Discounts"
            ],
            "Decors": [
                "Bedroom",
                "Kitchen",
                "Living Room",
                "Lighting",
                "Storage",
                "Discounts"
            ],
            "Accessories": [
                "Bags",
                "Hats",
                "Belts",
                "Socks",
                "Jewellery",
                "Discounts"
            ],
            "Sale / Discounts": [
                "Men Sale",
                "Women Sale",
                "Kids Sale",
                "Footwear Sale",
                "Home Sale",
                "Clearance"
            ]
        }

        return category_map.get(department, ["Discounts"])

    def clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()