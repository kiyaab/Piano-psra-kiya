"""
KIYA Piano Studio Pro - Voice & Instrument Browser Page
Allows browsing 128 GM instruments, searching, favorites, and routing to Right 1, Right 2, or Left Split.
"""

from typing import Optional, List, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QSpinBox, QSlider, QFrame
)
from app.constants import COLOR_ACCENT_ORANGE, COLOR_ACCENT_BLUE, COLOR_TEXT_PRIMARY, COLOR_BORDER
from presets.voice_browser import VoiceBrowser

class VoicesPage(QWidget):
    """Voice browser and layer/split configuration page."""

    voice_assigned = Signal(str, int)   # target ("right1", "right2", "left"), program (0-127)
    voice_preview_requested = Signal(int) # program
    layer_octave_changed = Signal(str, int) # target, octave (-2 to +2)
    layer_volume_changed = Signal(str, float) # target, volume (0.0 to 1.5)

    def __init__(self, voice_browser: VoiceBrowser, parent=None):
        super().__init__(parent)
        self.browser = voice_browser

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # -------------------------------------------------------------
        # LEFT COLUMN: Category Selector
        # -------------------------------------------------------------
        cat_group = QGroupBox("CATEGORIES")
        cat_layout = QVBoxLayout(cat_group)
        self.cat_list = QListWidget()
        self.cat_list.addItem("★ All Voices")
        self.cat_list.addItem("♥ Favorites")
        self.cat_list.addItem("⏱ Recent")
        for cat in self.browser.get_categories():
            self.cat_list.addItem(cat)
        self.cat_list.setCurrentRow(0)
        self.cat_list.currentRowChanged.connect(self._on_category_selected)
        cat_layout.addWidget(self.cat_list)
        main_layout.addWidget(cat_group, 2)

        # -------------------------------------------------------------
        # CENTER COLUMN: Search & Voice Table
        # -------------------------------------------------------------
        center_layout = QVBoxLayout()
        search_box = QHBoxLayout()
        search_box.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter instruments by name or keyword...")
        self.search_input.textChanged.connect(self._filter_voices)
        search_box.addWidget(self.search_input)
        center_layout.addLayout(search_box)

        self.voice_table = QTableWidget()
        self.voice_table.setColumnCount(3)
        self.voice_table.setHorizontalHeaderLabels(["#", "Instrument Name", "Category"])
        self.voice_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.voice_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.voice_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.voice_table.itemDoubleClicked.connect(self._on_table_double_clicked)
        self.voice_table.itemSelectionChanged.connect(self._on_selection_changed)
        center_layout.addWidget(self.voice_table)

        # Bottom buttons row
        btn_row = QHBoxLayout()
        self.btn_preview = QPushButton("♫ Preview Voice")
        self.btn_preview.clicked.connect(self._on_preview_clicked)
        btn_row.addWidget(self.btn_preview)

        self.btn_fav = QPushButton("♥ Add to Favorites")
        self.btn_fav.clicked.connect(self._on_fav_clicked)
        btn_row.addWidget(self.btn_fav)

        btn_row.addStretch()

        self.btn_assign_r1 = QPushButton("Set as RIGHT 1")
        self.btn_assign_r1.setStyleSheet(f"background-color: {COLOR_ACCENT_ORANGE}; color: #101216; font-weight: bold;")
        self.btn_assign_r1.clicked.connect(lambda: self._assign_selected("right1"))
        btn_row.addWidget(self.btn_assign_r1)

        self.btn_assign_r2 = QPushButton("Set as RIGHT 2 (Layer)")
        self.btn_assign_r2.setStyleSheet(f"background-color: {COLOR_ACCENT_BLUE}; color: #101216; font-weight: bold;")
        self.btn_assign_r2.clicked.connect(lambda: self._assign_selected("right2"))
        btn_row.addWidget(self.btn_assign_r2)

        self.btn_assign_left = QPushButton("Set as LEFT (Split)")
        self.btn_assign_left.clicked.connect(lambda: self._assign_selected("left"))
        btn_row.addWidget(self.btn_assign_left)

        center_layout.addLayout(btn_row)
        main_layout.addLayout(center_layout, 5)

        self._refresh_table()

    def _get_current_selected_program(self) -> Optional[int]:
        row = self.voice_table.currentRow()
        if row >= 0:
            prog_item = self.voice_table.item(row, 0)
            if prog_item:
                return int(prog_item.text()) - 1
        return None

    def _refresh_table(self, filter_text: str = ""):
        self.voice_table.setRowCount(0)
        current_cat_idx = self.cat_list.currentRow()
        cat_text = self.cat_list.currentItem().text() if self.cat_list.currentItem() else "★ All Voices"

        voices: List[Tuple[int, str, str]] = []
        if cat_text == "★ All Voices":
            voices = self.browser.search_voices(filter_text)
        elif cat_text == "♥ Favorites":
            for prog in self.browser.favorites:
                name = self.browser.get_voice_name(prog)
                cat = self.browser.get_voice_category(prog)
                if not filter_text or filter_text.lower() in name.lower():
                    voices.append((prog, name, cat))
        elif cat_text == "⏱ Recent":
            for prog in self.browser.recents:
                name = self.browser.get_voice_name(prog)
                cat = self.browser.get_voice_category(prog)
                if not filter_text or filter_text.lower() in name.lower():
                    voices.append((prog, name, cat))
        else:
            cat_voices = self.browser.get_voices_in_category(cat_text)
            for prog, name in cat_voices:
                if not filter_text or filter_text.lower() in name.lower():
                    voices.append((prog, name, cat_text))

        self.voice_table.setRowCount(len(voices))
        for row, (prog, name, cat) in enumerate(voices):
            item_prog = QTableWidgetItem(f"{prog + 1:03d}")
            item_prog.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_name = QTableWidgetItem(name)
            item_cat = QTableWidgetItem(cat)

            self.voice_table.setItem(row, 0, item_prog)
            self.voice_table.setItem(row, 1, item_name)
            self.voice_table.setItem(row, 2, item_cat)

        if len(voices) > 0:
            self.voice_table.selectRow(0)

    def _on_category_selected(self, index: int):
        self._refresh_table(self.search_input.text())

    def _filter_voices(self, text: str):
        self._refresh_table(text)

    def _on_selection_changed(self):
        prog = self._get_current_selected_program()
        if prog is not None:
            is_fav = self.browser.is_favorite(prog)
            self.btn_fav.setText("💔 Remove Favorite" if is_fav else "♥ Add to Favorites")

    def _on_table_double_clicked(self, item: QTableWidgetItem):
        prog = self._get_current_selected_program()
        if prog is not None:
            self.voice_assigned.emit("right1", prog)
            self.browser.record_usage(prog)

    def _on_preview_clicked(self):
        prog = self._get_current_selected_program()
        if prog is not None:
            self.voice_preview_requested.emit(prog)

    def _on_fav_clicked(self):
        prog = self._get_current_selected_program()
        if prog is not None:
            self.browser.toggle_favorite(prog)
            self._on_selection_changed()

    def _assign_selected(self, target: str):
        prog = self._get_current_selected_program()
        if prog is not None:
            self.voice_assigned.emit(target, prog)
            self.browser.record_usage(prog)
