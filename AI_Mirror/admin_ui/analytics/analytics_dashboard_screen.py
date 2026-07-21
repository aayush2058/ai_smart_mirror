from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class AnalyticsDashboardScreen(QWidget):
    def __init__(self, metrics_service, on_back):
        super().__init__()
        self.metrics_service = metrics_service
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 35, 50, 40)
        layout.setSpacing(20)
        title = QLabel("Retail Insights")
        title.setStyleSheet("font-size: 38px; font-weight: bold; color: white;")
        subtitle = QLabel("Anonymous local engagement signals for merchandising decisions.")
        subtitle.setStyleSheet("font-size: 19px; color: #bbbbbb;")
        self.summary = QLabel()
        self.summary.setAlignment(Qt.AlignTop)
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet(
            "font-size: 22px; color: white; background: #1c2530; padding: 28px; border-radius: 18px;"
        )
        back = QPushButton("Back")
        back.setFixedSize(160, 54)
        back.clicked.connect(on_back)
        back.setStyleSheet("font-size: 17px; color: white; background: #444; border-radius: 11px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.summary, stretch=1)
        layout.addWidget(back, alignment=Qt.AlignRight)
        self.setStyleSheet("background: #10151c;")

    def refresh(self):
        metrics = self.metrics_service.summary()
        lines = [
            f"Mirror sessions: {metrics['sessions']}",
            f"Product views: {metrics['views']}",
            f"Virtual try-ons: {metrics['tryons']}",
            f"Basket additions: {metrics['baskets']}",
            f"View to try-on rate: {metrics['tryon_rate']}%",
            f"View to basket rate: {metrics['basket_rate']}%",
            "", "Top products by customer interest",
        ]
        lines.extend(
            f"{index}. {item['name']} - {item['interactions']} interactions"
            for index, item in enumerate(metrics["top_products"], 1)
        )
        if not metrics["top_products"]:
            lines.append("Insights will appear after customers begin browsing.")
        self.summary.setText("\n".join(lines))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
