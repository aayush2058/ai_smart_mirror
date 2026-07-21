from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget
from admin_ui.analytics.metrics_service import MetricsService


class AnalyticsDashboardScreen(QWidget):
    def __init__(self, on_back, metrics_service=None):
        super().__init__()
        self.metrics_service = metrics_service or MetricsService()
        layout = QVBoxLayout(self); layout.setContentsMargins(40, 30, 40, 30)
        header = QHBoxLayout(); title = QLabel("Retail Insights")
        title.setStyleSheet("font-size:34px; font-weight:bold; color:white;")
        back = QPushButton("Back"); back.setFixedSize(140, 48); back.clicked.connect(on_back)
        back.setStyleSheet("font-size:17px; color:white; background:#44515f; border-radius:10px;")
        header.addWidget(title); header.addStretch(); header.addWidget(back); layout.addLayout(header)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:#10151c;")
        container = QWidget(); self.content = QVBoxLayout(container); self.content.setSpacing(16)
        scroll.setWidget(container); layout.addWidget(scroll); self.setStyleSheet("background:#10151c;")

    def refresh(self):
        while self.content.count():
            item = self.content.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        metrics = self.metrics_service.summary(); grid = QGridLayout()
        cards = (("Sessions", metrics["sessions"]), ("Product Views", metrics["views"]),
                 ("Virtual Try-Ons", metrics["tryons"]), ("Basket Adds", metrics["baskets"]),
                 ("Try-On Rate", f'{metrics["tryon_rate"]}%'), ("Basket Rate", f'{metrics["basket_rate"]}%'))
        for index, (label, value) in enumerate(cards):
            card = QFrame(); card.setStyleSheet("background:#1c2530; border:1px solid #34495e; border-radius:14px;")
            box = QVBoxLayout(card); value_label = QLabel(str(value)); value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-size:30px; font-weight:bold; color:#00ff99; border:none;")
            name_label = QLabel(label); name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("font-size:17px; color:#d7dde3; border:none;")
            box.addWidget(value_label); box.addWidget(name_label); grid.addWidget(card, index // 3, index % 3)
        self.content.addLayout(grid)
        rows = metrics["top_products"]
        text = "Top products\n" + ("\n".join(f'{i + 1}. {row["name"]} — {row["interactions"]} interactions' for i, row in enumerate(rows)) if rows else "No interaction data yet.")
        top = QLabel(text); top.setStyleSheet("font-size:18px; color:white; background:#1c2530; padding:20px; border-radius:14px;")
        self.content.addWidget(top); self.content.addStretch()
