from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit,
    QDialog, QSlider, QMessageBox
)
from PySide6.QtCore import Qt


class TryOnSettingsScreen(QWidget):
    def __init__(self, on_back, on_update_tryon):
        super().__init__()

        self.on_back = on_back
        self.on_update_tryon = on_update_tryon
        self.products = []

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(45, 35, 45, 35)
        main_layout.setSpacing(20)

        title = QLabel("Try-On Settings")
        title.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search try-on products...")
        self.search_input.setFixedHeight(52)
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                color: white;
                background-color: #1f2b38;
                border: 1px solid #34495e;
                border-radius: 12px;
                padding-left: 16px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_products)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #10151c;
                border: none;
            }
        """)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(14)
        self.list_layout.setContentsMargins(5, 5, 5, 5)

        self.list_container.setLayout(self.list_layout)
        self.scroll_area.setWidget(self.list_container)

        back_button = QPushButton("Back")
        back_button.setFixedSize(170, 55)
        back_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #444444;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        back_button.clicked.connect(self.on_back)

        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(back_button)
        bottom_bar.addStretch()

        main_layout.addWidget(title)
        main_layout.addWidget(self.search_input)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(bottom_bar)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #10151c;")

    def set_products(self, products):
        self.products = products
        self.render_products(products)

    def filter_products(self):
        query = self.search_input.text().strip().lower()

        if not query:
            self.render_products(self.products)
            return

        filtered = []

        for product in self.products:
            search_text = " ".join([
                str(product.get("name", "")),
                str(product.get("category", "")),
                str(product.get("tryon_category", "")),
            ]).lower()

            if query in search_text:
                filtered.append(product)

        self.render_products(filtered)

    def render_products(self, products):
        self.clear_products()

        tryon_products = [
            product for product in products
            if product.get("tryon_enabled") or product.get("tryon_category")
        ]

        if not tryon_products:
            empty_label = QLabel("No try-on products found.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 22px;
                    color: #cccccc;
                    background-color: transparent;
                    border: none;
                    padding: 60px;
                }
            """)
            self.list_layout.addWidget(empty_label)
            self.list_layout.addStretch()
            return

        for product in tryon_products:
            self.list_layout.addWidget(self.create_product_row(product))

        self.list_layout.addStretch()

    def create_product_row(self, product):
        row = QFrame()
        row.setStyleSheet("""
            QFrame {
                background-color: #1c2530;
                border-radius: 16px;
                border: 1px solid #34404d;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        info = QLabel(
            f"{product.get('name', 'Unnamed Product')}\n"
            f"{product.get('category', 'N/A')} | {product.get('tryon_category', 'N/A')}"
        )
        info.setFixedWidth(360)
        info.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        settings = product.get("tryon_settings") or {}

        values = QLabel(
            f"Width: {settings.get('width_scale', product.get('width_scale', 1.0))}\n"
            f"Height: {settings.get('height_scale', product.get('height_scale', 1.0))}\n"
            f"Vertical: {settings.get('vertical_offset', product.get('vertical_offset', 0.0))}\n"
            f"Horizontal: {settings.get('horizontal_offset', product.get('horizontal_offset', 0))}"
        )
        values.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #dddddd;
                background-color: transparent;
                border: none;
            }
        """)

        edit_button = QPushButton("Adjust Fit")
        edit_button.setFixedSize(140, 45)
        edit_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #2d89ef;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """)
        edit_button.clicked.connect(
            lambda checked=False, p=product: self.open_settings_dialog(p)
        )

        layout.addWidget(info)
        layout.addWidget(values)
        layout.addStretch()
        layout.addWidget(edit_button)

        row.setLayout(layout)
        return row

    def open_settings_dialog(self, product):
        dialog = TryOnSettingsDialog(
            product=product,
            on_save=self.on_update_tryon
        )
        dialog.exec()

    def clear_products(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class TryOnSettingsDialog(QDialog):
    def __init__(self, product, on_save):
        super().__init__()

        self.product = product
        self.on_save = on_save

        self.setWindowTitle("Adjust Try-On Fit")
        self.setMinimumWidth(620)

        settings = product.get("tryon_settings") or {}

        self.width_value = float(settings.get("width_scale", product.get("width_scale", 1.0)) or 1.0)
        self.height_value = float(settings.get("height_scale", product.get("height_scale", 1.0)) or 1.0)
        self.vertical_value = float(settings.get("vertical_offset", product.get("vertical_offset", 0.0)) or 0.0)
        self.horizontal_value = int(settings.get("horizontal_offset", product.get("horizontal_offset", 0)) or 0)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        title = QLabel(f"Adjust Fit\n{product.get('name', 'Unnamed Product')}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
        """)

        self.width_label, self.width_slider = self.create_slider(
            "Width Scale",
            50,
            700,
            int(self.width_value * 100)
        )

        self.height_label, self.height_slider = self.create_slider(
            "Height Scale",
            50,
            400,
            int(self.height_value * 100)
        )

        self.vertical_label, self.vertical_slider = self.create_slider(
            "Vertical Offset",
            -100,
            100,
            int(self.vertical_value * 100)
        )

        self.horizontal_label, self.horizontal_slider = self.create_slider(
            "Horizontal Offset",
            -100,
            100,
            int(self.horizontal_value)
        )

        self.width_slider.valueChanged.connect(self.update_labels)
        self.height_slider.valueChanged.connect(self.update_labels)
        self.vertical_slider.valueChanged.connect(self.update_labels)
        self.horizontal_slider.valueChanged.connect(self.update_labels)

        button_row = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(150, 50)
        cancel_button.setStyleSheet(self.grey_button_style())
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save Fit")
        save_button.setFixedSize(170, 50)
        save_button.setStyleSheet(self.green_button_style())
        save_button.clicked.connect(self.handle_save)

        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        main_layout.addWidget(title)
        main_layout.addWidget(self.width_label)
        main_layout.addWidget(self.width_slider)
        main_layout.addWidget(self.height_label)
        main_layout.addWidget(self.height_slider)
        main_layout.addWidget(self.vertical_label)
        main_layout.addWidget(self.vertical_slider)
        main_layout.addWidget(self.horizontal_label)
        main_layout.addWidget(self.horizontal_slider)
        main_layout.addLayout(button_row)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #10151c;")

        self.update_labels()

    def create_slider(self, label_text, minimum, maximum, value):
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: white;
            }
        """)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(minimum)
        slider.setMaximum(maximum)
        slider.setValue(value)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #34495e;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #2d89ef;
                width: 22px;
                margin: -8px 0;
                border-radius: 11px;
            }
        """)

        return label, slider

    def update_labels(self):
        self.width_label.setText(f"Width Scale: {self.width_slider.value() / 100:.2f}")
        self.height_label.setText(f"Height Scale: {self.height_slider.value() / 100:.2f}")
        self.vertical_label.setText(f"Vertical Offset: {self.vertical_slider.value() / 100:.2f}")
        self.horizontal_label.setText(f"Horizontal Offset: {self.horizontal_slider.value()} px")

    def handle_save(self):
        try:
            values = {
                "width_scale": self.width_slider.value() / 100,
                "height_scale": self.height_slider.value() / 100,
                "vertical_offset": self.vertical_slider.value() / 100,
                "horizontal_offset": self.horizontal_slider.value(),
            }

            self.on_save(self.product, values)
            self.accept()

        except Exception as error:
            QMessageBox.warning(self, "Try-On Settings Error", str(error))

    def green_button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #00a86b;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #007a4d;
            }
        """

    def grey_button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                background-color: #444444;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """