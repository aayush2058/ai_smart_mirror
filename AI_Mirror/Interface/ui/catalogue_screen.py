from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from ui.common_widgets import create_map_button


class ClickableProductCard(QFrame):
    def __init__(self, product, on_clicked):
        super().__init__()
        self.product = product
        self.on_clicked = on_clicked

    def mousePressEvent(self, event):
        self.on_clicked(self.product)


class CatalogueScreen(QWidget):
    def __init__(self, on_product_selected, on_back, on_map):
        super().__init__()

        self.on_product_selected = on_product_selected
        self.on_back = on_back
        self.on_map = on_map

        self.department = None
        self.category = None
        self.products = []

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(20)

        self.title = QLabel("Catalogue")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        # -------------------------
        # VERTICAL SCROLL AREA
        # -------------------------
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #111111;
            }

            QScrollBar:vertical {
                width: 18px;
                background: #222222;
                border-radius: 9px;
            }

            QScrollBar::handle:vertical {
                background: #666666;
                border-radius: 9px;
                min-height: 80px;
            }

            QScrollBar::handle:vertical:hover {
                background: #888888;
            }
        """)

        self.product_container = QWidget()

        self.product_grid = QGridLayout()
        self.product_grid.setSpacing(28)
        self.product_grid.setContentsMargins(20, 20, 20, 20)

        self.product_container.setLayout(self.product_grid)
        self.scroll_area.setWidget(self.product_container)

        # -------------------------
        # BOTTOM BAR
        # -------------------------
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
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addLayout(bottom_bar)

        self.setLayout(self.main_layout)
        self.setStyleSheet("background-color: #111111;")

    def get_project_root(self):
        return Path(__file__).resolve().parents[1]

    def set_products(self, department, category, products):
        self.department = department
        self.category = category
        self.products = products

        self.title.setText(f"{department} / {category}")
        self.load_product_cards()

    def load_product_cards(self):
        self.clear_products()

        if not self.products:
            empty_label = QLabel("No products available in this section.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    color: #cccccc;
                    padding: 80px;
                    border: none;
                    background-color: transparent;
                }
            """)
            self.product_grid.addWidget(empty_label, 0, 0, 1, 2)
            return

        # 2 columns, vertical scrolling
        for index, product in enumerate(self.products):
            card = self.create_product_card(product)

            row = index // 2
            col = index % 2

            self.product_grid.addWidget(card, row, col)

    def create_product_card(self, product):
        card = ClickableProductCard(product, self.on_product_selected)

        card.setFixedSize(520, 340)
        card.setCursor(Qt.PointingHandCursor)
        card.setObjectName("productCard")

        card.setStyleSheet("""
            QFrame#productCard {
                background-color: #1f1f1f;
                border: 2px solid #333333;
                border-radius: 22px;
            }

            QFrame#productCard:hover {
                background-color: #252525;
                border: 3px solid #2d89ef;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        image_box = QLabel()
        image_box.setFixedSize(475, 225)
        image_box.setAlignment(Qt.AlignCenter)
        image_box.setStyleSheet("""
            QLabel {
                background-color: #333333;
                color: #aaaaaa;
                border-radius: 16px;
                font-size: 18px;
                border: none;
            }
        """)

        image_from_json = product.get("image", "")
        image_path = self.get_project_root() / image_from_json

        if image_path.exists():
            pixmap = QPixmap(str(image_path))

            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    455,
                    210,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_box.setPixmap(pixmap)
            else:
                image_box.setText("Image Error")
        else:
            image_box.setText("No Image")

        name = QLabel(product.get("name", "Unnamed Product"))
        name.setAlignment(Qt.AlignCenter)
        name.setWordWrap(True)
        name.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        price = QLabel(str(product.get("price", "N/A")))
        price.setAlignment(Qt.AlignCenter)
        price.setStyleSheet("""
            QLabel {
                font-size: 21px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        layout.addWidget(image_box, alignment=Qt.AlignCenter)
        layout.addWidget(name)
        layout.addWidget(price)

        card.setLayout(layout)

        return card

    def clear_products(self):
        while self.product_grid.count():
            item = self.product_grid.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()