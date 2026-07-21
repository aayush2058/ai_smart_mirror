<<<<<<< HEAD
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame
=======
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QSizePolicy, QScrollArea
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
from PySide6.QtCore import Qt


class AdminDashboardScreen(QWidget):
<<<<<<< HEAD
    def __init__(self, on_products, on_add_product, on_inventory, on_discounts, on_locations, on_tryon_settings, on_logout):
=======
    def __init__(self, on_products, on_add_product, on_inventory, on_discounts, on_locations, on_tryon_settings, on_diagnostics, on_undo, on_logout):
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
        super().__init__()

        self.on_products = on_products
        self.on_add_product = on_add_product
        self.on_inventory = on_inventory
        self.on_discounts = on_discounts
        self.on_locations = on_locations
        self.on_tryon_settings = on_tryon_settings
<<<<<<< HEAD
        self.on_logout = on_logout

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 35, 50, 40)
        main_layout.setSpacing(25)
=======
        self.on_diagnostics = on_diagnostics
        self.on_undo = on_undo
        self.on_logout = on_logout

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 22, 30, 24)
        main_layout.setSpacing(14)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

        top_bar = QHBoxLayout()

        title = QLabel("Admin Dashboard")
        title.setStyleSheet("""
            QLabel {
<<<<<<< HEAD
                font-size: 40px;
=======
                font-size: 32px;
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
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
<<<<<<< HEAD
                font-size: 21px;
=======
                font-size: 17px;
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
                color: #bbbbbb;
                background-color: transparent;
                border: none;
            }
        """)

        summary_row = QHBoxLayout()
<<<<<<< HEAD
        summary_row.setSpacing(18)
=======
        summary_row.setSpacing(12)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

        self.total_card = self.create_summary_card("Total Products", "0")
        self.available_card = self.create_summary_card("Available", "0")
        self.discount_card = self.create_summary_card("Discounted", "0")
        self.tryon_card = self.create_summary_card("Try-On Enabled", "0")

        summary_row.addWidget(self.total_card)
        summary_row.addWidget(self.available_card)
        summary_row.addWidget(self.discount_card)
        summary_row.addWidget(self.tryon_card)

        grid = QGridLayout()
<<<<<<< HEAD
        grid.setSpacing(22)
=======
        grid.setSpacing(12)
        for column in range(3):
            grid.setColumnStretch(column, 1)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

        grid.addWidget(self.create_action_button("Manage Products", "View, edit and delete products", self.on_products), 0, 0)
        grid.addWidget(self.create_action_button("Add Product", "Add clothes and upload images", self.on_add_product), 0, 1)
        grid.addWidget(self.create_action_button("Stock & Sizes", "Update availability and sizes", self.on_inventory), 0, 2)

        grid.addWidget(self.create_action_button("Discounts", "Manage sale products", self.on_discounts), 1, 0)
        grid.addWidget(self.create_action_button("Store Locations", "Update product locations", self.on_locations), 1, 1)
        grid.addWidget(self.create_action_button("Try-On Settings", "Adjust fitting settings", self.on_tryon_settings), 1, 2)
<<<<<<< HEAD
=======
        grid.addWidget(self.create_action_button("Undo Last Data Change", "Restore the last recorded correction", self.on_undo), 2, 0)
        grid.addWidget(self.create_action_button("System Diagnostics", "Camera, database and device health", self.on_diagnostics), 2, 1)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(summary_row)
<<<<<<< HEAD
        main_layout.addSpacing(20)
        main_layout.addLayout(grid)
        main_layout.addStretch()

        self.setLayout(main_layout)
=======
        main_layout.addSpacing(6)
        main_layout.addLayout(grid)
        main_layout.addStretch()

        content = QWidget()
        content.setLayout(main_layout)
        content.setStyleSheet("background-color: #10151c;")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(content)
        scroll_area.setStyleSheet("QScrollArea { background-color: #10151c; border: none; }")

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(scroll_area)
        self.setLayout(root_layout)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
        self.setStyleSheet("background-color: #10151c;")

    def create_summary_card(self, title, value):
        card = QFrame()
<<<<<<< HEAD
        card.setFixedHeight(120)
=======
        card.setFixedHeight(90)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
        card.setStyleSheet("""
            QFrame {
                background-color: #1c2530;
                border-radius: 18px;
                border: 1px solid #34404d;
            }
        """)

        layout = QVBoxLayout()
<<<<<<< HEAD
        layout.setContentsMargins(22, 18, 22, 18)
=======
        layout.setContentsMargins(18, 12, 18, 12)
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)

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
<<<<<<< HEAD
                font-size: 34px;
=======
                font-size: 27px;
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
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
<<<<<<< HEAD
        button = QPushButton(f"{title}\n\n{description}")
        button.setFixedSize(350, 165)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                text-align: left;
                padding: 20px;
=======
        button = QPushButton(f"{title}\n{description}")
        button.setMinimumSize(240, 96)
        button.setMaximumHeight(110)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                padding: 14px;
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
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
<<<<<<< HEAD
        self.tryon_card.value_label.setText(str(tryon_enabled))
=======
        self.tryon_card.value_label.setText(str(tryon_enabled))
>>>>>>> c40243b (Old versions to a archive repo. Only active files here)
