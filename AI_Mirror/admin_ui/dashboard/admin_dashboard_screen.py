from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QSizePolicy, QScrollArea
from PySide6.QtCore import Qt


class AdminDashboardScreen(QWidget):
    def __init__(self, on_products, on_add_product, on_inventory, on_discounts, on_locations, on_tryon_settings, on_diagnostics, on_analytics, on_undo, on_history, on_logout, on_super_back=None):
        super().__init__()

        self.on_products = on_products
        self.on_add_product = on_add_product
        self.on_inventory = on_inventory
        self.on_discounts = on_discounts
        self.on_locations = on_locations
        self.on_tryon_settings = on_tryon_settings
        self.on_diagnostics = on_diagnostics
        self.on_analytics = on_analytics
        self.on_undo = on_undo
        self.on_history = on_history
        self.on_logout = on_logout
        self.on_super_back = on_super_back

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 22, 30, 24)
        main_layout.setSpacing(14)

        top_bar = QHBoxLayout()

        title = QLabel("Admin Dashboard")
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
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

        self.super_back_button = QPushButton("← Super Admin")
        self.super_back_button.setFixedSize(170, 52)
        self.super_back_button.setStyleSheet(
            "font-size:17px;font-weight:bold;background:#7b5cd6;color:white;"
            "border-radius:12px;"
        )
        if self.on_super_back:
            self.super_back_button.clicked.connect(self.on_super_back)
        self.super_back_button.hide()

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.super_back_button)
        top_bar.addWidget(logout_button)

        subtitle = QLabel("Manage products, stock, discounts, store locations and virtual try-on settings.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: #bbbbbb;
                background-color: transparent;
                border: none;
            }
        """)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)

        self.total_card = self.create_summary_card("Total Products", "0", "#4f8cff")
        self.available_card = self.create_summary_card("Available", "0", "#35c98b")
        self.discount_card = self.create_summary_card("Discounted", "0", "#e8b84c")
        self.tryon_card = self.create_summary_card("Try-On Enabled", "0", "#a36de0")
        self.low_stock_card = self.create_summary_card("Low Stock", "0", "#ef8b45")
        self.out_stock_card = self.create_summary_card("Out of Stock", "0", "#df5c69")

        summary_row.addWidget(self.total_card)
        summary_row.addWidget(self.available_card)
        summary_row.addWidget(self.discount_card)
        summary_row.addWidget(self.tryon_card)
        summary_row.addWidget(self.low_stock_card)
        summary_row.addWidget(self.out_stock_card)

        grid = QGridLayout()
        grid.setSpacing(12)
        for column in range(3):
            grid.setColumnStretch(column, 1)

        grid.addWidget(self.create_action_button("Manage Products", "View, edit and delete products", self.on_products, "#2d6fa8"), 0, 0)
        grid.addWidget(self.create_action_button("Add Product", "Add clothes and upload images", self.on_add_product, "#008f68"), 0, 1)
        grid.addWidget(self.create_action_button("Stock & Sizes", "Update availability and sizes", self.on_inventory, "#6b5bc7"), 0, 2)

        grid.addWidget(self.create_action_button("Discounts", "Manage sale products", self.on_discounts, "#b57a25"), 1, 0)
        grid.addWidget(self.create_action_button("Store Locations", "Update product locations", self.on_locations, "#367f92"), 1, 1)
        grid.addWidget(self.create_action_button("Try-On Settings", "Adjust fitting settings", self.on_tryon_settings, "#a35186"), 1, 2)
        grid.addWidget(self.create_action_button("Change History & Undo", "Undo any section saved within 24 hours", self.on_history, "#a55d32"), 2, 0)
        grid.addWidget(self.create_action_button("System Diagnostics", "Camera, database and device health", self.on_diagnostics, "#4d705a"), 2, 1)
        grid.addWidget(self.create_action_button("Retail Insights", "Engagement, try-on and basket KPIs", self.on_analytics, "#5368b5"), 2, 2)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(summary_row)
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
        self.setStyleSheet("background-color: #10151c;")

    def create_summary_card(self, title, value, accent):
        card = QFrame()
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1c2530;
                border-radius: 18px;
                border: 2px solid {accent};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 12, 18, 12)

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
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 27px;
                font-weight: bold;
                color: {accent};
                background-color: transparent;
                border: none;
            }}
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.setLayout(layout)
        card.value_label = value_label

        return card

    def create_action_button(self, title, description, callback, colour):
        button = QPushButton(f"{title}\n{description}")
        button.setMinimumSize(240, 96)
        button.setMaximumHeight(110)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                padding: 14px;
                background-color: {colour};
                color: white;
                border: 2px solid rgba(255, 255, 255, 45);
                border-radius: 18px;
            }}
            QPushButton:hover {{
                background-color: {colour};
                border: 2px solid white;
            }}
        """)
        button.clicked.connect(callback)
        return button

    def update_summary(self, total, available, discounted, tryon_enabled, low_stock=0, out_of_stock=0):
        self.total_card.value_label.setText(str(total))
        self.available_card.value_label.setText(str(available))
        self.discount_card.value_label.setText(str(discounted))
        self.tryon_card.value_label.setText(str(tryon_enabled))
        self.low_stock_card.value_label.setText(str(low_stock))
        self.out_stock_card.value_label.setText(str(out_of_stock))

    def set_super_mode(self, enabled):
        self.super_back_button.setVisible(bool(enabled and self.on_super_back))
