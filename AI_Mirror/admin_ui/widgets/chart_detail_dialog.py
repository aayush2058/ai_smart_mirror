from PySide6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel,
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                               QVBoxLayout)

from admin_ui.widgets.chart_widgets import BarChartWidget, LineChartWidget


class ChartDetailDialog(QDialog):
    def __init__(self, source_chart, parent=None):
        super().__init__(parent); self.source = source_chart
        self.setWindowTitle(source_chart.title); self.setMinimumSize(1000, 700)
        root = QVBoxLayout(self); root.setContentsMargins(28, 22, 28, 24); root.setSpacing(12)
        header = QHBoxLayout(); title = QLabel(source_chart.title); title.setWordWrap(True)
        title.setStyleSheet("font-size:30px;font-weight:bold;color:white;")
        close = QPushButton("Close"); close.setMinimumSize(120, 44); close.clicked.connect(self.accept)
        header.addWidget(title, 1); header.addWidget(close)
        filters = QHBoxLayout(); self.search = QLineEdit(); self.search.setPlaceholderText("Filter labels...")
        self.series_filter = QComboBox(); self.series_filter.addItem("All data series", None)
        for series in source_chart.series: self.series_filter.addItem(series["name"], series["name"])
        clear = QPushButton("Clear"); clear.setObjectName("clearButton"); clear.clicked.connect(self.clear_filters)
        self.count = QLabel(); filters.addWidget(self.search, 1); filters.addWidget(self.series_filter); filters.addWidget(clear); filters.addWidget(self.count)
        chart_type = BarChartWidget if isinstance(source_chart, BarChartWidget) else LineChartWidget
        self.chart = chart_type(source_chart.title, source_chart.subtitle); self.chart.setMinimumHeight(390); self.chart.setCursor(self.cursor())
        self.table = QTableWidget(); self.table.setEditTriggers(QTableWidget.NoEditTriggers); self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget{font-size:15px;color:white;background:#111820;alternate-background-color:#18232d;gridline-color:#34495e;} QHeaderView::section{background:#263746;color:white;padding:8px;font-weight:bold;}")
        root.addLayout(header); root.addLayout(filters); root.addWidget(self.chart, 2); root.addWidget(self.table, 1)
        self.setStyleSheet("background:#0d151d;color:white;")
        self.search.textChanged.connect(self.apply_filters); self.series_filter.currentIndexChanged.connect(self.apply_filters)
        self.apply_filters()

    def apply_filters(self):
        query = self.search.text().strip().lower(); selected = self.series_filter.currentData()
        indexes = [index for index, label in enumerate(self.source.labels) if not query or query in str(label).lower()]
        labels = [self.source.labels[index] for index in indexes]
        series = [{**item, "values": [item.get("values", [])[index] for index in indexes if index < len(item.get("values", []))]}
                  for item in self.source.series if not selected or item["name"] == selected]
        self.chart.set_data(labels, series); self.count.setText(f"{len(labels)} points")
        self.table.setColumnCount(1 + len(series)); self.table.setHorizontalHeaderLabels(["Label"] + [item["name"] for item in series]); self.table.setRowCount(len(labels))
        for row, label in enumerate(labels):
            self.table.setItem(row, 0, QTableWidgetItem(str(label)))
            for column, item in enumerate(series, 1):
                value = item["values"][row] if row < len(item["values"]) else ""
                self.table.setItem(row, column, QTableWidgetItem(str(value)))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def clear_filters(self):
        self.search.clear(); self.series_filter.setCurrentIndex(0)


def open_chart_detail(chart, parent):
    dialog = ChartDetailDialog(chart, parent); dialog.showMaximized(); dialog.exec()
