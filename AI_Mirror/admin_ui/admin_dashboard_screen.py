from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt


class AdminDashboardScreen(QWidget):
    def __init__(self, on_products, on_add_product, on_inventory, on_discounts, on_locations, on_tryon_settings, on_logout):
        super().__init__()

        self.on_products = on_products
        self.on_add_product = on_add_product
        self.on_inventory = on_inventory
        self.on_discounts = on_discounts
        self.on_locations = on_locations
        self.on_tryon_settings = on_tryon_settings
        self.on_logout = on_logout

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 35, 50, 40)
        main_layout.setSpacing(25)

        top_bar = QHBoxLayout()

        title = QLabel("Admin Dashboard")
        title.setStyleSheet("""
            QLabel {
                font-size: 40px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        logout_button = QPushButton("Log Out")
        logout_button.setFixedSize(150, 52)
        logout_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                background-color: #8b2d2d;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #b13b3b;
            }
        """)
        logout_button.clicked.connect(self.on_logout)

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(logout_button)

        subtitle = QLabel("Manage products, stock, discounts, store locations and virtual try-on settings.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 21px;
                color: #bbbbbb;
                background-color: transparent;
                border: none;
            }
        """)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(18)

        self.total_card = self.create_summary_card("Total Products", "0")
        self.available_card = self.create_summary_card("Available", "0")
        self.discount_card = self.create_summary_card("Discounted", "0")
        self.tryon_card = self.create_summary_card("Try-On Enabled", "0")

        summary_row.addWidget(self.total_card)
        summary_row.addWidget(self.available_card)
        summary_row.addWidget(self.discount_card)
        summary_row.addWidget(self.tryon_card)

        grid = QGridLayout()
        grid.setSpacing(22)

        grid.addWidget(self.create_action_button("Manage Products", "View, edit and delete products", self.on_products), 0, 0)
        grid.addWidget(self.create_action_button("Add Product", "Add clothes and upload images", self.on_add_product), 0, 1)
        grid.addWidget(self.create_action_button("Stock & Sizes", "Update availability and sizes", self.on_inventory), 0, 2)

        grid.addWidget(self.create_action_button("Discounts", "Manage sale products", self.on_discounts), 1, 0)
        grid.addWidget(self.create_action_button("Store Locations", "Update product locations", self.on_locations), 1, 1)
        grid.addWidget(self.create_action_button("Try-On Settings", "Adjust fitting settings", self.on_tryon_settings), 1, 2)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(summary_row)
        main_layout.addSpacing(20)
        main_layout.addLayout(grid)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #10151c;")

    def create_summary_card(self, title, value):
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet("""
            QFrame {
                background-color: #1c2530;
                border-radius: 18px;
                border: 1px solid #34404d;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: #aab4bf;
                background-color: transparent;
                border: none;
            }
        """)

        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 34px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.setLayout(layout)
        card.value_label = value_label

        return card

    def create_action_button(self, title, description, callback):
        button = QPushButton(f"{title}\n\n{description}")
        button.setFixedSize(350, 165)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                text-align: left;
                padding: 20px;
                background-color: #1f2b38;
                color: white;
                border: 2px solid #34495e;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #2b3d4f;
                border: 2px solid #2d89ef;
            }
        """)
        button.clicked.connect(callback)
        return button

    def update_summary(self, total, available, discounted, tryon_enabled):
        self.total_card.value_label.setText(str(total))
        self.available_card.value_label.setText(str(available))
        self.discount_card.value_label.setText(str(discounted))
        self.tryon_card.value_label.setText(str(tryon_enabled))