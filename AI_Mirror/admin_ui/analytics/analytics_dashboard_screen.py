from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QScrollArea, QVBoxLayout, QWidget)

from admin_ui.widgets.chart_widgets import BarChartWidget, LineChartWidget


class AnalyticsDashboardScreen(QWidget):
    def __init__(self, metrics_service, on_back):
        super().__init__(); self.metrics_service = metrics_service
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none;background:#0d151d;")
        content = QWidget(); layout = QVBoxLayout(content); layout.setContentsMargins(34, 25, 34, 28); layout.setSpacing(14)
        header = QHBoxLayout(); title = QLabel("Retail Operations & Customer Insights")
        title.setWordWrap(True); title.setStyleSheet("font-size:34px;font-weight:bold;color:white;")
        export = QPushButton("Export CSV Report"); export.clicked.connect(self.export_csv)
        back = QPushButton("Back"); back.clicked.connect(on_back)
        for button, colour in ((export, "#008f68"), (back, "#465565")):
            button.setFixedSize(190 if button is export else 130, 48)
            button.setStyleSheet(f"font-size:16px;color:white;background:{colour};border-radius:10px;")
        header.addWidget(title, 1); header.addWidget(export); header.addWidget(back)
        subtitle = QLabel("Anonymous activity, conversion flow and stock-position signals from this offline mirror.")
        subtitle.setWordWrap(True); subtitle.setStyleSheet("font-size:17px;color:#b8c4ce;")
        self.kpi_grid = QGridLayout(); self.kpi_grid.setSpacing(10); self.kpis = {}
        cards = (("sessions", "Mirror Sessions", "#2d89ef"), ("views", "Product Views", "#6c63d9"),
                 ("tryons", "Virtual Try-Ons", "#00a884"), ("baskets", "Basket Adds", "#e38b3a"),
                 ("tryon_rate", "View → Try-On", "#b15fd3"), ("basket_rate", "View → Basket", "#d3b13c"))
        for index, (key, label, colour) in enumerate(cards):
            card = QFrame(); card.setStyleSheet(f"background:{colour};border-radius:13px;")
            box = QVBoxLayout(card); value = QLabel("0"); value.setStyleSheet("font-size:28px;font-weight:bold;color:white;")
            name = QLabel(label); name.setWordWrap(True); name.setStyleSheet("font-size:14px;color:#f4f7fa;")
            box.addWidget(value); box.addWidget(name); self.kpis[key] = value
            self.kpi_grid.addWidget(card, index // 3, index % 3)
        charts = QHBoxLayout(); charts.setSpacing(12)
        self.activity_chart = LineChartWidget("14-Day Customer Activity", "Views, virtual try-ons and basket additions by day")
        self.stock_chart = BarChartWidget("Current Stock Logistics", "Products with healthy, low or zero stock")
        charts.addWidget(self.activity_chart, 2); charts.addWidget(self.stock_chart, 1)
        self.top_products = QLabel(); self.top_products.setWordWrap(True)
        self.top_products.setStyleSheet("font-size:16px;color:white;background:#18242e;padding:16px;border:1px solid #314657;border-radius:12px;")
        layout.addLayout(header); layout.addWidget(subtitle); layout.addLayout(self.kpi_grid)
        layout.addLayout(charts); layout.addWidget(self.top_products); layout.addStretch()
        scroll.setWidget(content); root.addWidget(scroll); self.setStyleSheet("background:#0d151d;")

    def refresh(self):
        metrics = self.metrics_service.summary(); dashboard = self.metrics_service.dashboard_data()
        for key in ("sessions", "views", "tryons", "baskets"):
            self.kpis[key].setText(str(metrics[key]))
        self.kpis["tryon_rate"].setText(f'{metrics["tryon_rate"]}%')
        self.kpis["basket_rate"].setText(f'{metrics["basket_rate"]}%')
        self.activity_chart.set_data(dashboard["labels"], [
            {"name": "Views", "colour": "#6c8cff", "values": dashboard["views"]},
            {"name": "Try-Ons", "colour": "#38d6a3", "values": dashboard["tryons"]},
            {"name": "Basket Adds", "colour": "#ff9f5c", "values": dashboard["baskets"]},
        ])
        self.stock_chart.set_data(["Healthy", "Low", "Out"], [
            {"name": "Products", "colour": "#42c98b", "values": dashboard["stock"]}
        ])
        rows = metrics["top_products"]
        text = "<b>Top products by customer interest</b><br>" + (
            " &nbsp; · &nbsp; ".join(f'{index}. {item["name"]} ({item["interactions"]})'
                                     for index, item in enumerate(rows, 1))
            if rows else "Insights will appear after customers begin browsing."
        )
        self.top_products.setText(text)

    def export_csv(self):
        destination = self.metrics_service.export_summary_csv()
        QMessageBox.information(self, "Report Exported", f"Retail report saved to:\n{destination}")

    def showEvent(self, event):
        super().showEvent(event); self.refresh()
