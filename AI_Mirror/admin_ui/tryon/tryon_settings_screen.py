from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QLineEdit,
    QDialog, QSlider, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from paths import resolve_project_path

FIT_PRESETS = {
    "Custom": None,

    "Regular Shirt": {
        "width_scale": 2.0,
        "height_scale": 1.30,
        "vertical_offset": 0.16,
        "horizontal_offset": 0,
    },

    "Slim Shirt": {
        "width_scale": 1.80,
        "height_scale": 1.35,
        "vertical_offset": 0.15,
        "horizontal_offset": 0,
    },

    "Oversized Shirt": {
        "width_scale": 2.40,
        "height_scale": 1.45,
        "vertical_offset": 0.18,
        "horizontal_offset": 0,
    },

    "Regular Pants": {
        "width_scale": 3.80,
        "height_scale": 1.35,
        "vertical_offset": 0.20,
        "horizontal_offset": 0,
    },

    "Slim Jeans": {
        "width_scale": 3.40,
        "height_scale": 1.45,
        "vertical_offset": 0.20,
        "horizontal_offset": 0,
    },

    "Loose Pants": {
        "width_scale": 4.30,
        "height_scale": 1.40,
        "vertical_offset": 0.22,
        "horizontal_offset": 0,
    },

    "Shorts": {
        "width_scale": 3.80,
        "height_scale": 1.00,
        "vertical_offset": 0.34,
        "horizontal_offset": 0,
    },
}

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

        self.image_preview = QLabel("No Product Image")
        self.image_preview.setFixedSize(220, 280)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                background-color: #1c2530;
                color: #cccccc;
                border: 1px solid #34495e;
                border-radius: 14px;
                font-size: 16px;
            }
        """)

        self.load_product_image()

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

        preset_row = QHBoxLayout()
        preset_row.setSpacing(12)

        preset_label = QLabel("Fit Preset")
        preset_label.setStyleSheet("""
            QLabel {
                font-size: 17px;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(FIT_PRESETS.keys())
        self.preset_combo.setFixedHeight(48)
        self.preset_combo.setStyleSheet("""
            QComboBox {
                font-size: 17px;
                color: white;
                background-color: #1c2530;
                border: 1px solid #34495e;
                border-radius: 10px;
                padding-left: 12px;
            }

            QComboBox QAbstractItemView {
                background-color: #1c2530;
                color: white;
                selection-background-color: #2d89ef;
            }
        """)

        self.apply_preset_button = QPushButton("Apply Preset")
        self.apply_preset_button.setFixedSize(150, 48)
        self.apply_preset_button.setStyleSheet(
            self.blue_button_style()
        )
        self.apply_preset_button.clicked.connect(
            self.apply_selected_preset
        )

        preset_row.addWidget(preset_label)
        preset_row.addWidget(self.preset_combo)
        preset_row.addWidget(self.apply_preset_button)

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

        reset_button = QPushButton("Reset Default")
        reset_button.setFixedSize(160, 50)
        reset_button.setStyleSheet(self.grey_button_style())
        reset_button.clicked.connect(self.reset_to_default)

        save_button = QPushButton("Save Fit")
        save_button.setFixedSize(170, 50)
        save_button.setStyleSheet(self.green_button_style())
        save_button.clicked.connect(self.handle_save)

        button_row.addWidget(reset_button)
        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)
        
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(16)

        controls_layout.addLayout(preset_row)
        controls_layout.addWidget(self.width_label)
        controls_layout.addWidget(self.width_slider)
        controls_layout.addWidget(self.height_label)
        controls_layout.addWidget(self.height_slider)
        controls_layout.addWidget(self.vertical_label)
        controls_layout.addWidget(self.vertical_slider)
        controls_layout.addWidget(self.horizontal_label)
        controls_layout.addWidget(self.horizontal_slider)
        controls_layout.addStretch()

        

        calibration_row = QHBoxLayout()
        calibration_row.setSpacing(30)

        calibration_row.addWidget(
            self.image_preview,
            alignment=Qt.AlignTop
        )
        calibration_row.addLayout(controls_layout)

        main_layout.addWidget(title)
        main_layout.addLayout(calibration_row)
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
    
    def apply_selected_preset(self):
        preset_name = self.preset_combo.currentText()
        preset = FIT_PRESETS.get(preset_name)

        if not preset:
            return

        self.width_slider.setValue(
            int(preset["width_scale"] * 100)
        )

        self.height_slider.setValue(
            int(preset["height_scale"] * 100)
        )

        self.vertical_slider.setValue(
            int(preset["vertical_offset"] * 100)
        )

        self.horizontal_slider.setValue(
            int(preset["horizontal_offset"])
        )

        self.update_labels()


    def reset_to_default(self):
        self.preset_combo.setCurrentText("Custom")

        self.width_slider.setValue(100)
        self.height_slider.setValue(100)
        self.vertical_slider.setValue(0)
        self.horizontal_slider.setValue(0)

        self.update_labels()

    def blue_button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #2d89ef;
                color: white;
                border-radius: 10px;
            }

            QPushButton:hover {
                background-color: #1b5fbd;
            }
        """
    
    def load_product_image(self):
        image_path = (
            self.product.get("image_path")
            or self.product.get("image")
            or ""
        )

        full_path = resolve_project_path(image_path)

        if not full_path or not full_path.exists():
            self.image_preview.setText("Image Not Found")
            return

        pixmap = QPixmap(str(full_path))

        if pixmap.isNull():
            self.image_preview.setText("Image Error")
            return

        self.image_preview.setPixmap(
            pixmap.scaled(
                200,
                260,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )