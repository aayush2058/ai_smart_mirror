from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt


class MapScreen(QWidget):
    def __init__(self, on_back):
        super().__init__()

        self.on_back = on_back
        self.product = None

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 35, 50, 40)
        main_layout.setSpacing(25)

        title = QLabel("Store Map")
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

        self.product_location_label = QLabel("Select a product to see its exact store location.")
        self.product_location_label.setAlignment(Qt.AlignCenter)
        self.product_location_label.setWordWrap(True)
        self.product_location_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        map_card = QFrame()
        map_card.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 24px;
                border: none;
            }
        """)

        map_layout = QVBoxLayout()
        map_layout.setContentsMargins(40, 35, 40, 35)
        map_layout.setSpacing(20)

        # -------------------------
        # SIMPLE STORE MAP BLOCKS
        # -------------------------
        row_1 = QHBoxLayout()
        row_1.setSpacing(20)

        row_2 = QHBoxLayout()
        row_2.setSpacing(20)

        row_3 = QHBoxLayout()
        row_3.setSpacing(20)

        you_are_here = self.create_map_block("YOU ARE HERE\nSmart Mirror", "#00a86b")
        men_upper = self.create_map_block("MEN\nUpper Fit\nShirts", "#2d89ef")
        men_lower = self.create_map_block("MEN\nLower Fit\nPants / Shorts", "#2d89ef")

        discount = self.create_map_block("DISCOUNT\nSale Area", "#ffcc00")
        changing = self.create_map_block("CHANGING\nROOM", "#555555")
        checkout = self.create_map_block("CHECKOUT", "#555555")

        row_1.addWidget(men_upper)
        row_1.addWidget(men_lower)

        row_2.addWidget(you_are_here)
        row_2.addWidget(discount)

        row_3.addWidget(changing)
        row_3.addWidget(checkout)

        map_layout.addLayout(row_1)
        map_layout.addLayout(row_2)
        map_layout.addLayout(row_3)

        map_card.setLayout(map_layout)

        bottom_bar = QHBoxLayout()

        back_button = QPushButton("Back")
        back_button.setFixedSize(180, 60)
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

        bottom_bar.addWidget(back_button, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()

        main_layout.addWidget(title)
        main_layout.addWidget(self.product_location_label)
        main_layout.addWidget(map_card)
        main_layout.addLayout(bottom_bar)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #111111;")

    def create_map_block(self, text, accent_colour):
        block = QFrame()
        block.setFixedSize(420, 140)
        block.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border-radius: 18px;
                border: 3px solid {accent_colour};
            }}
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        layout.addWidget(label)
        block.setLayout(layout)

        return block

    def set_product(self, product):
        self.product = product

        if product:
            self.product_location_label.setText(
                f"Selected product: {product.get('name', 'Unnamed Product')}  |  "
                f"Location: {product.get('location', 'Location unavailable')}"
            )
        else:
            self.product_location_label.setText(
                "No product selected. You can still use this map to find store sections."
            )