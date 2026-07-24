from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class ChartBase(QWidget):
    def __init__(self, title, subtitle=""):
        super().__init__(); self.title = title; self.subtitle = subtitle
        self.labels = []; self.series = []
        self.setMinimumHeight(260)

    def set_data(self, labels, series):
        self.labels = list(labels)
        self.series = list(series)
        self.update()

    def _frame(self, painter):
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#192631")); gradient.setColorAt(1, QColor("#111a22"))
        painter.setBrush(gradient); painter.setPen(QPen(QColor("#344b5e"), 1))
        painter.drawRoundedRect(QRectF(1, 1, self.width() - 2, self.height() - 2), 16, 16)
        painter.setPen(QColor("#ffffff")); painter.setFont(QFont("Segoe UI", 15, QFont.Bold))
        painter.drawText(QRectF(18, 12, self.width() - 36, 25), Qt.AlignLeft | Qt.AlignVCenter, self.title)
        painter.setPen(QColor("#9fb0bf")); painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(QRectF(18, 37, self.width() - 36, 20), Qt.AlignLeft | Qt.AlignVCenter, self.subtitle)
        return QRectF(54, 72, max(10, self.width() - 76), max(10, self.height() - 115))

    def _empty(self, painter, plot):
        painter.setPen(QColor("#8fa0ad")); painter.setFont(QFont("Segoe UI", 11))
        painter.drawText(plot, Qt.AlignCenter, "Not enough recorded activity to draw this chart yet.")

    def _axes(self, painter, plot, maximum):
        painter.setFont(QFont("Segoe UI", 8))
        for step in range(5):
            ratio = step / 4
            y = plot.bottom() - ratio * plot.height()
            painter.setPen(QPen(QColor("#2a3c49"), 1, Qt.DashLine))
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
            painter.setPen(QColor("#8294a2"))
            painter.drawText(QRectF(4, y - 8, 45, 16), Qt.AlignRight | Qt.AlignVCenter,
                             f"{maximum * ratio:.0f}")

    def _legend(self, painter):
        x = 18
        painter.setFont(QFont("Segoe UI", 8))
        for item in self.series:
            painter.setBrush(QColor(item["colour"])); painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(x, self.height() - 25, 10, 10), 2, 2)
            painter.setPen(QColor("#c7d1d9"))
            text = item["name"]
            width = painter.fontMetrics().horizontalAdvance(text)
            painter.drawText(QRectF(x + 14, self.height() - 29, width + 4, 18), Qt.AlignVCenter, text)
            x += width + 34


class BarChartWidget(ChartBase):
    def paintEvent(self, event):
        painter = QPainter(self); plot = self._frame(painter)
        values = [float(value) for item in self.series for value in item.get("values", [])]
        if not self.labels or not values:
            self._empty(painter, plot); return
        maximum = max(1.0, max(values) * 1.15); self._axes(painter, plot, maximum)
        group_width = plot.width() / max(1, len(self.labels))
        bar_width = min(28.0, group_width * 0.68 / max(1, len(self.series)))
        for index, label in enumerate(self.labels):
            total_width = bar_width * len(self.series)
            start_x = plot.left() + index * group_width + (group_width - total_width) / 2
            for series_index, item in enumerate(self.series):
                value = float(item["values"][index]) if index < len(item["values"]) else 0
                height = value / maximum * plot.height()
                rect = QRectF(start_x + series_index * bar_width, plot.bottom() - height,
                              max(3, bar_width - 3), height)
                gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
                colour = QColor(item["colour"]); gradient.setColorAt(0, colour.lighter(120)); gradient.setColorAt(1, colour.darker(115))
                painter.setBrush(gradient); painter.setPen(Qt.NoPen); painter.drawRoundedRect(rect, 4, 4)
            if len(self.labels) <= 12 or index % 2 == 0:
                painter.setPen(QColor("#91a4b2")); painter.setFont(QFont("Segoe UI", 7))
                short = painter.fontMetrics().elidedText(str(label), Qt.ElideRight, int(group_width - 4))
                painter.drawText(QRectF(plot.left() + index * group_width, plot.bottom() + 5,
                                        group_width, 20), Qt.AlignHCenter | Qt.AlignTop, short)
        self._legend(painter)


class LineChartWidget(ChartBase):
    def paintEvent(self, event):
        painter = QPainter(self); plot = self._frame(painter)
        values = [float(value) for item in self.series for value in item.get("values", [])]
        if len(self.labels) < 2 or not values:
            self._empty(painter, plot); return
        maximum = max(1.0, max(values) * 1.15); self._axes(painter, plot, maximum)
        step_x = plot.width() / max(1, len(self.labels) - 1)
        for item in self.series:
            points = []
            for index, value in enumerate(item["values"]):
                x = plot.left() + index * step_x
                y = plot.bottom() - float(value) / maximum * plot.height()
                points.append(QPointF(x, y))
            path = QPainterPath(points[0])
            for point in points[1:]: path.lineTo(point)
            colour = QColor(item["colour"]); painter.setPen(QPen(colour, 3)); painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
            painter.setBrush(colour)
            for point in points: painter.drawEllipse(point, 3.5, 3.5)
        painter.setFont(QFont("Segoe UI", 7)); painter.setPen(QColor("#91a4b2"))
        for index, label in enumerate(self.labels):
            if len(self.labels) <= 10 or index % 2 == 0:
                painter.drawText(QRectF(plot.left() + index * step_x - 28, plot.bottom() + 5, 56, 18),
                                 Qt.AlignHCenter | Qt.AlignTop, str(label))
        self._legend(painter)
