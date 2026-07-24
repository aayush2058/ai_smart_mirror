from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QScrollArea, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)
from admin_ui.widgets.chart_widgets import BarChartWidget, LineChartWidget
from admin_ui.widgets.chart_detail_dialog import open_chart_detail


class PredictionDashboardScreen(QWidget):
    def __init__(self, prediction_service, current_user, on_back):
        super().__init__(); self.prediction_service = prediction_service; self.current_user = current_user; self.result = None
        root = QVBoxLayout(self); root.setContentsMargins(30, 22, 30, 26); root.setSpacing(12)
        header = QHBoxLayout(); title = QLabel("Predictive Retail Intelligence")
        title.setWordWrap(True)
        title.setStyleSheet("font-size:34px;font-weight:bold;color:white;")
        self.horizon = QComboBox(); self.horizon.addItems(["7", "14", "30"]); self.horizon.setFixedSize(90, 46)
        self.minimum_rows = QComboBox(); self.minimum_rows.addItems(["30", "60", "90", "180"]); self.minimum_rows.setFixedSize(95, 46)
        generate = QPushButton("Generate Predictions"); generate.clicked.connect(self.generate)
        export = QPushButton("Export CSV"); export.clicked.connect(self.export)
        back = QPushButton("Back"); back.clicked.connect(on_back)
        for widget in (self.horizon, self.minimum_rows):
            widget.setStyleSheet("font-size:16px;color:white;background:#263441;border:1px solid #4b6072;border-radius:9px;padding:7px;")
        for button in (generate, export, back):
            button.setMinimumSize(135, 46); button.setStyleSheet("font-size:16px;color:white;background:#6c54c7;border-radius:9px;")
        header.addWidget(title, 1); header.addWidget(generate); header.addWidget(back)
        toolbar = QHBoxLayout(); toolbar.setSpacing(10)
        forecast_label = QLabel("Forecast days"); training_label = QLabel("Minimum training rows")
        for label in (forecast_label, training_label):
            label.setStyleSheet("font-size:15px;color:#c7d1d9;")
        toolbar.addWidget(forecast_label); toolbar.addWidget(self.horizon)
        toolbar.addSpacing(12); toolbar.addWidget(training_label); toolbar.addWidget(self.minimum_rows)
        toolbar.addStretch(); toolbar.addWidget(export)
        self.model_status = QLabel("No prediction run loaded."); self.model_status.setWordWrap(True)
        self.model_status.setStyleSheet("font-size:17px;color:white;background:#19242e;padding:14px;border:1px solid #34495e;border-radius:12px;")
        privacy = QLabel(
            "Data used: anonymous product views, virtual try-on starts, basket additions, price, discount and stock. "
            "No camera images, faces, names or customer identities are collected. Low-data results are explicitly marked Low confidence."
        )
        privacy.setWordWrap(True); privacy.setStyleSheet("font-size:15px;color:#b9c4ce;background:#14201b;padding:12px;border-radius:10px;")
        filters = QHBoxLayout(); filters.setSpacing(10)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search product...")
        self.risk = QComboBox(); self.risk.addItems(["All risks", "Critical", "High", "Medium", "Low"])
        self.confidence = QComboBox(); self.confidence.addItems(["All confidence", "High", "Medium", "Low"])
        clear = QPushButton("Clear"); clear.setObjectName("clearButton"); clear.clicked.connect(self.clear_filters); self.result_count = QLabel("0 results")
        for widget in (self.search, self.risk, self.confidence):
            widget.setMinimumHeight(44); widget.setStyleSheet("font-size:15px;color:white;background:#263441;border:1px solid #4b6072;border-radius:9px;padding:7px;")
        self.search.setMinimumWidth(240); filters.addWidget(self.search, 1); filters.addWidget(self.risk); filters.addWidget(self.confidence); filters.addWidget(clear); filters.addWidget(self.result_count)
        self.search.textChanged.connect(self.apply_filters); self.risk.currentIndexChanged.connect(self.apply_filters); self.confidence.currentIndexChanged.connect(self.apply_filters)
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(
            ["Product", "Demand", "Conversion", "Stock", "Risk", "Confidence", "Views", "Try-Ons", "Recommended Action"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True); self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet(
            "QTableWidget{font-size:15px;color:white;background:#111820;alternate-background-color:#18232d;"
            "gridline-color:#34495e;} QHeaderView::section{background:#263746;color:white;padding:9px;font-weight:bold;}"
        )
        charts = QHBoxLayout(); charts.setSpacing(12)
        self.demand_chart = BarChartWidget("Forecast Demand vs Available Stock", "Top products by predicted demand")
        self.conversion_chart = LineChartWidget("Predicted Conversion Profile", "Basket-conversion likelihood by product")
        self.demand_chart.set_compact(); self.conversion_chart.set_compact()
        self.demand_chart.clicked.connect(lambda: open_chart_detail(self.demand_chart, self))
        self.conversion_chart.clicked.connect(lambda: open_chart_detail(self.conversion_chart, self))
        charts.addWidget(self.demand_chart); charts.addWidget(self.conversion_chart)
        root.addLayout(header); root.addLayout(charts); root.addStretch()
        self.setStyleSheet("background:#0d131a;color:white;")
        settings = self.prediction_service.settings()
        self.horizon.setCurrentText(str(settings["horizon_days"]))
        self.minimum_rows.setCurrentText(str(settings["minimum_training_rows"]))

    def refresh(self):
        latest = self.prediction_service.latest()
        if latest:
            self.result = latest; self.render(latest)

    def generate(self):
        try:
            self.prediction_service.save_settings(self.horizon.currentText(), self.minimum_rows.currentText())
            QApplicationOverride.set_busy(True)
            self.result = self.prediction_service.generate(self.current_user()["id"])
            self.render(self.result)
        except Exception as error:
            QMessageBox.warning(self, "Prediction Error", str(error))
        finally:
            QApplicationOverride.set_busy(False)

    def render(self, result):
        metrics = result["metrics"]; model = result["model_type"]
        accuracy = f' | Time-series MAE: {metrics["validation_mae"]}' if metrics.get("validation_mae") is not None else ""
        self.model_status.setText(
            f'<b>Model:</b> {model} | <b>Training rows:</b> {metrics.get("training_rows", 0)} | '
            f'<b>Events:</b> {metrics.get("event_count", 0)}{accuracy} | <b>Generated:</b> {result.get("generated_at", "")}'
        )
        self.apply_filters()

    def apply_filters(self):
        rows = list(self.result["predictions"]) if self.result else []
        query = self.search.text().strip().lower(); risk = self.risk.currentText(); confidence = self.confidence.currentText()
        rows = [item for item in rows if (not query or query in item["name"].lower())
                and (risk == "All risks" or item["stock_risk"] == risk)
                and (confidence == "All confidence" or item["confidence"] == confidence)]
        self.result_count.setText(f"{len(rows)} results"); self.table.setRowCount(len(rows))
        chart_rows = sorted(rows, key=lambda item: item["expected_demand"], reverse=True)[:8]
        labels = [item["name"] for item in chart_rows]
        self.demand_chart.set_data(labels, [
            {"name": "Forecast Demand", "colour": "#8c72e8", "values": [item["expected_demand"] for item in chart_rows]},
            {"name": "Available Stock", "colour": "#42c98b", "values": [item["stock"] for item in chart_rows]},
        ])
        self.conversion_chart.set_data(labels, [
            {"name": "Conversion %", "colour": "#ffad5c", "values": [item["conversion_probability"] for item in chart_rows]}
        ])
        colours = {"Critical": "#ff6666", "High": "#ff9f5c", "Medium": "#ffd166", "Low": "#72df9b"}
        for row_index, item in enumerate(rows):
            values = (item["name"], f'{item["expected_demand"]} / {item["horizon_days"]}d',
                      f'{item["conversion_probability"]}%', item["stock"], item["stock_risk"],
                      item["confidence"], item["views_30d"], item["tryons_30d"], item["recommendation"])
            for column, value in enumerate(values):
                cell = QTableWidgetItem(str(value)); cell.setToolTip(str(value))
                if column == 4: cell.setForeground(QColor(colours[item["stock_risk"]]))
                self.table.setItem(row_index, column, cell)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(8, max(320, self.table.columnWidth(8)))

    def clear_filters(self):
        self.search.clear(); self.risk.setCurrentIndex(0); self.confidence.setCurrentIndex(0)

    def export(self):
        if not self.result:
            QMessageBox.information(self, "No Predictions", "Generate predictions before exporting."); return
        path = self.prediction_service.export_csv(self.result)
        QMessageBox.information(self, "Predictions Exported", f"Saved to:\n{path}")


class QApplicationOverride:
    @staticmethod
    def set_busy(enabled):
        from PySide6.QtWidgets import QApplication
        if enabled:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            QApplication.processEvents()
        else:
            while QApplication.overrideCursor() is not None:
                QApplication.restoreOverrideCursor()
