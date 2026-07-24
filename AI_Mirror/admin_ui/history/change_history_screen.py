from datetime import datetime, timezone

from PySide6.QtCore import QDateTime, Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDateTimeEdit, QFrame, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)


class ChangeHistoryScreen(QWidget):
    def __init__(self, history_service, on_back, on_changed):
        super().__init__()
        self.history_service = history_service
        self.on_changed = on_changed
        root = QVBoxLayout(self); root.setContentsMargins(32, 24, 32, 24); root.setSpacing(14)
        header = QHBoxLayout(); title = QLabel("Product Change History")
        title.setStyleSheet("font-size:32px;font-weight:bold;color:white;")
        back = QPushButton("Back"); back.setFixedSize(140, 48); back.clicked.connect(on_back)
        back.setStyleSheet("font-size:17px;color:white;background:#465565;border-radius:10px;")
        header.addWidget(title); header.addStretch(); header.addWidget(back); root.addLayout(header)
        help_text = QLabel("Each section is saved separately. Undo is available for 24 hours. A full safety backup is kept at most once per hour.")
        help_text.setStyleSheet("font-size:17px;color:#c4ccd4;"); root.addWidget(help_text)
        filter_row = QHBoxLayout(); filter_row.setSpacing(9)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search item or change..."); self.search.setMinimumWidth(230)
        self.section = QComboBox(); self.section.addItem("All sections")
        self.status = QComboBox(); self.status.addItems(["All status", "Undo available", "Undone", "Expired"])
        clear = QPushButton("Clear"); clear.setObjectName("clearButton"); clear.clicked.connect(self.clear_filters)
        filter_row.addWidget(self.search, 1); filter_row.addWidget(self.section); filter_row.addWidget(self.status); filter_row.addWidget(clear)
        date_row = QHBoxLayout(); self.use_dates = QCheckBox("Use date/time range")
        self.date_from = QDateTimeEdit(QDateTime.currentDateTime().addDays(-1)); self.date_to = QDateTimeEdit(QDateTime.currentDateTime())
        for editor in (self.date_from, self.date_to):
            editor.setDisplayFormat("dd MMM yyyy  HH:mm"); editor.setCalendarPopup(True); editor.setEnabled(False)
        date_row.addWidget(self.use_dates); date_row.addWidget(QLabel("From")); date_row.addWidget(self.date_from)
        date_row.addWidget(QLabel("To")); date_row.addWidget(self.date_to); date_row.addStretch()
        for widget in (self.search, self.section, self.status, self.date_from, self.date_to):
            widget.setMinimumHeight(42); widget.setStyleSheet("font-size:15px;color:white;background:#263441;border:1px solid #4b6072;border-radius:8px;padding:6px;")
        root.addLayout(filter_row); root.addLayout(date_row)
        self.result_count = QLabel(); self.result_count.setStyleSheet("font-size:14px;color:#aeb8c2;"); root.addWidget(self.result_count)
        self.search.textChanged.connect(self.apply_filters); self.section.currentIndexChanged.connect(self.apply_filters)
        self.status.currentIndexChanged.connect(self.apply_filters); self.use_dates.toggled.connect(self.toggle_dates)
        self.date_from.dateTimeChanged.connect(self.apply_filters); self.date_to.dateTimeChanged.connect(self.apply_filters)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setStyleSheet("border:none;background:#10151c;")
        self.container = QWidget(); self.list_layout = QVBoxLayout(self.container); self.list_layout.setSpacing(12)
        self.scroll.setWidget(self.container); root.addWidget(self.scroll); self.setStyleSheet("background:#10151c;")

    def refresh(self):
        self.history = self.history_service.get_change_history(limit=1000)
        selected = self.section.currentText(); sections = sorted({item["section"] for item in self.history})
        self.section.blockSignals(True); self.section.clear(); self.section.addItem("All sections"); self.section.addItems(sections)
        if selected in sections: self.section.setCurrentText(selected)
        self.section.blockSignals(False); self.apply_filters()

    def apply_filters(self):
        history = getattr(self, "history", [])
        query = self.search.text().strip().lower(); section = self.section.currentText(); status = self.status.currentText()
        start = self.date_from.dateTime().toSecsSinceEpoch(); end = self.date_to.dateTime().toSecsSinceEpoch()
        filtered = []
        for change in history:
            searchable = f'{change["product_name"]} {change["section"]} {change["description"]}'.lower()
            created = datetime.strptime(change["created_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            state_ok = (status == "All status" or (status == "Undo available" and change["can_undo"])
                        or (status == "Undone" and change["undone"])
                        or (status == "Expired" and not change["undone"] and not change["can_undo"]))
            if (not query or query in searchable) and (section == "All sections" or change["section"] == section) \
                    and state_ok and (not self.use_dates.isChecked() or start <= created <= end):
                filtered.append(change)
        self._render(filtered)

    def _render(self, history):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.result_count.setText(f"{len(history)} changes shown")
        if not history:
            empty = QLabel("No recorded product changes yet."); empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("font-size:20px;color:#9ba6b2;padding:50px;"); self.list_layout.addWidget(empty)
        for change in history:
            self.list_layout.addWidget(self._card(change))
        self.list_layout.addStretch()

    def toggle_dates(self, enabled):
        self.date_from.setEnabled(enabled); self.date_to.setEnabled(enabled); self.apply_filters()

    def clear_filters(self):
        self.search.clear(); self.section.setCurrentIndex(0); self.status.setCurrentIndex(0)
        self.use_dates.setChecked(False); self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-1)); self.date_to.setDateTime(QDateTime.currentDateTime())

    def _card(self, change):
        card = QFrame(); card.setStyleSheet("QFrame{background:#1c2530;border:1px solid #34495e;border-radius:14px;}")
        layout = QHBoxLayout(card); layout.setContentsMargins(18, 14, 18, 14); layout.setSpacing(18)
        before = self._summary(change["before_values"]); after = self._summary(change["after_values"])
        text = QLabel(f'<b>{change["section"]}</b>  ·  {change["product_name"]}<br>'
                      f'{change["description"]}<br><span style="color:#aeb8c2;">Saved: {change["created_display"]}  ·  Undo expires: {change["expires_display"]}</span><br>'
                      f'<span style="color:#ffbf69;">Before:</span> {before}<br><span style="color:#70e1a1;">After:</span> {after}')
        text.setTextFormat(Qt.RichText); text.setWordWrap(True); text.setStyleSheet("font-size:16px;color:white;border:none;")
        button = QPushButton("Undo This Section" if change["can_undo"] else ("Undone" if change["undone"] else "Undo Expired"))
        button.setFixedSize(180, 48); button.setEnabled(change["can_undo"])
        button.setStyleSheet("font-size:15px;font-weight:bold;color:white;background:#b26a25;border-radius:10px;disabled{background:#46505a;color:#9aa2aa;}")
        button.clicked.connect(lambda checked=False, item=change: self._undo(item))
        layout.addWidget(text, 1); layout.addWidget(button); return card

    def _summary(self, values):
        if isinstance(values, list):
            return ", ".join(f'{item.get("size")}: {item.get("quantity")}' for item in values) or "None"
        return ", ".join(f'{key.replace("_", " ").title()}: {value}' for key, value in values.items()) or "None"

    def _undo(self, change):
        answer = QMessageBox.question(self, "Undo Section Change",
                                      f'Undo only the {change["section"]} change for {change["product_name"]}?',
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes: return
        success, message = self.history_service.undo_history_change(change["id"])
        QMessageBox.information(self, "Change Undone" if success else "Cannot Undo", message)
        if success: self.on_changed()
        self.refresh()
