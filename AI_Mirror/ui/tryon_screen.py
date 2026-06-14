import cv2

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

from tryon_engine.tryon_engine import TryOnEngine


class TryOnScreen(QWidget):
    def __init__(self, on_exit):
        super().__init__()

        self.on_exit = on_exit
        self.product = None
        self.engine = TryOnEngine()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 35)
        main_layout.setSpacing(18)

        title = QLabel("Virtual Try-On")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                border: none;
            }
        """)

        self.product_label = QLabel("No product selected")
        self.product_label.setAlignment(Qt.AlignCenter)
        self.product_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #00ff99;
                background-color: transparent;
                border: none;
            }
        """)

        self.camera_frame = QLabel("Starting camera...")
        self.camera_frame.setAlignment(Qt.AlignCenter)
        self.camera_frame.setMinimumSize(960, 540)
        self.camera_frame.setStyleSheet("""
            QLabel {
                background-color: #111111;
                color: #cccccc;
                font-size: 24px;
                border-radius: 18px;
                border: none;
            }
        """)

        camera_container = QFrame()
        camera_container.setStyleSheet("""
            QFrame {
                background-color: #1f1f1f;
                border-radius: 24px;
                border: none;
            }
        """)

        camera_layout = QVBoxLayout()
        camera_layout.setContentsMargins(20, 20, 20, 20)
        camera_layout.addWidget(self.camera_frame, alignment=Qt.AlignCenter)
        camera_container.setLayout(camera_layout)

        exit_button = QPushButton("Exit Try-On")
        exit_button.setFixedSize(240, 62)
        exit_button.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                background-color: #444444;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        exit_button.clicked.connect(self.exit_tryon)

        main_layout.addWidget(title)
        main_layout.addWidget(self.product_label)
        main_layout.addWidget(camera_container)
        main_layout.addWidget(exit_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #111111;")

    def set_product(self, product):
        self.product = product

        if product:
            self.product_label.setText(
                f"Trying on: {product.get('name', 'Unnamed Product')}"
            )
        else:
            self.product_label.setText("No product selected")

    def start_camera(self, product):
        self.set_product(product)
        self.camera_frame.setText("Starting camera...")

        self.engine.start(product)

        # Around 30 FPS UI refresh
        self.timer.start(33)

    def update_camera_frame(self):
        frame = self.engine.read_frame()

        if frame is None:
            self.camera_frame.setText("Camera frame not available.")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        qt_image = QImage(
            rgb_frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qt_image)

        pixmap = pixmap.scaled(
            self.camera_frame.width(),
            self.camera_frame.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.camera_frame.setPixmap(pixmap)

    def stop_camera(self):
        self.timer.stop()
        self.engine.stop()
        self.camera_frame.clear()
        self.camera_frame.setText("Camera stopped.")

    def exit_tryon(self):
        self.stop_camera()
        self.on_exit()