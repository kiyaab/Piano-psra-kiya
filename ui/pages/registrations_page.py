"""
KIYA Piano Studio Pro - Registration Memory Manager Page
Full manager for 8 quick-access slots across Banks A to H.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QGroupBox, QListWidget, QInputDialog, QMessageBox,
    QFileDialog, QFrame
)
from app.constants import (
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY
)
from presets.registrations import RegistrationManager, RegistrationSlot

class RegistrationsPage(QWidget):
    """Registration memory bank editor and manager."""

    recall_slot_requested = Signal(int) # slot_idx (0-7)
    store_slot_requested = Signal(int, str) # slot_idx, slot_name
    bank_changed = Signal(str) # bank_letter

    def __init__(self, reg_manager: RegistrationManager, parent=None):
        super().__init__(parent)
        self.reg_manager = reg_manager

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # LEFT COLUMN: Bank Selector & 8 Slots List
        # -------------------------------------------------------------
        slots_group = QGroupBox("REGISTRATION SLOTS")
        slots_layout = QVBoxLayout(slots_group)

        # Bank selector row (A-H)
        bank_bar = QHBoxLayout()
        bank_bar.addWidget(QLabel("BANK:"))
        self.bank_buttons: list[QPushButton] = []
        for b in self.reg_manager.BANKS:
            btn = QPushButton(b)
            btn.setCheckable(True)
            btn.setFixedSize(28, 28)
            letter = b
            btn.clicked.connect(lambda checked, l=letter: self._on_bank_clicked(l))
            self.bank_buttons.append(btn)
            bank_bar.addWidget(btn)
        self.bank_buttons[0].setChecked(True)
        slots_layout.addLayout(bank_bar)

        # Slots List Widget
        self.slots_list = QListWidget()
        self.slots_list.currentRowChanged.connect(self._on_slot_row_changed)
        slots_layout.addWidget(self.slots_list)

        main_layout.addWidget(slots_group, 3)

        # -------------------------------------------------------------
        # RIGHT COLUMN: Slot Details & Action Controls
        # -------------------------------------------------------------
        details_group = QGroupBox("SLOT DETAILS & PERFORMANCE STATE")
        details_layout = QVBoxLayout(details_group)
        details_layout.setSpacing(12)

        self.slot_title_lbl = QLabel("Slot 1: Concert Grand")
        self.slot_title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLOR_ACCENT_ORANGE};")
        details_layout.addWidget(self.slot_title_lbl)

        # Performance summary labels
        self.info_voices_lbl = QLabel("Voices: Right 1: Acoustic Grand | Right 2: Off | Left: Off")
        self.info_style_lbl = QLabel("Arranger: Pop Groove (120 BPM - Main A)")
        self.info_mixer_lbl = QLabel("Mixer: Master 85% | Reverb 30% | Chorus 15%")
        for lbl in (self.info_voices_lbl, self.info_style_lbl, self.info_mixer_lbl):
            lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px;")
            details_layout.addWidget(lbl)

        details_layout.addSpacing(16)

        # Primary Action Buttons
        btn_grid = QGridLayout()
        btn_grid.setSpacing(10)

        self.btn_recall = QPushButton("▶ RECALL SLOT (LOAD SETUP)")
        self.btn_recall.setStyleSheet(f"background-color: {COLOR_ACCENT_ORANGE}; color: #101216; font-weight: bold; min-height: 36px;")
        self.btn_recall.clicked.connect(self._on_recall_clicked)
        btn_grid.addWidget(self.btn_recall, 0, 0, 1, 2)

        self.btn_store = QPushButton("💾 STORE CURRENT SETUP TO SLOT")
        self.btn_store.setStyleSheet(f"background-color: {COLOR_ACCENT_BLUE}; color: #101216; font-weight: bold; min-height: 36px;")
        self.btn_store.clicked.connect(self._on_store_clicked)
        btn_grid.addWidget(self.btn_store, 1, 0, 1, 2)

        self.btn_rename = QPushButton("Rename Slot...")
        self.btn_rename.clicked.connect(self._on_rename_clicked)
        btn_grid.addWidget(self.btn_rename, 2, 0)

        self.btn_clear = QPushButton("Clear Slot")
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        btn_grid.addWidget(self.btn_clear, 2, 1)

        details_layout.addLayout(btn_grid)
        details_layout.addStretch()

        # Import / Export
        io_bar = QHBoxLayout()
        self.btn_export_bank = QPushButton("Export Bank to JSON...")
        self.btn_export_bank.clicked.connect(self._on_export_bank)
        io_bar.addWidget(self.btn_export_bank)

        self.btn_import_bank = QPushButton("Import Bank from JSON...")
        self.btn_import_bank.clicked.connect(self._on_import_bank)
        io_bar.addWidget(self.btn_import_bank)
        details_layout.addLayout(io_bar)

        main_layout.addWidget(details_group, 4)

        self._refresh_slots_list()

    def _refresh_slots_list(self):
        self.slots_list.clear()
        bank_slots = self.reg_manager.banks_data[self.reg_manager.current_bank]
        for i, s in enumerate(bank_slots):
            status = f"Slot {i + 1}: {s.name}"
            if s.is_empty:
                status += " (Empty)"
            self.slots_list.addItem(status)
        self.slots_list.setCurrentRow(0)

    def _on_bank_clicked(self, letter: str):
        for btn in self.bank_buttons:
            btn.setChecked(btn.text() == letter)
        self.reg_manager.select_bank(letter)
        self.bank_changed.emit(letter)
        self._refresh_slots_list()

    def _on_slot_row_changed(self, row: int):
        if 0 <= row < 8:
            slot = self.reg_manager.get_slot(row)
            self.slot_title_lbl.setText(f"Slot {row + 1}: {slot.name}")
            self.info_voices_lbl.setText(
                f"Voices: R1 Program #{slot.right1_voice + 1} | "
                f"Layer: {'ON (#' + str(slot.right2_voice + 1) + ')' if slot.layer_enabled else 'OFF'} | "
                f"Split: {'ON (#' + str(slot.left_voice + 1) + ')' if slot.split_enabled else 'OFF'}"
            )
            self.info_style_lbl.setText(f"Arranger: {slot.style_name} ({slot.tempo} BPM - {slot.section})")
            self.info_mixer_lbl.setText(
                f"Mixer: Vol {int(slot.master_volume * 100)}% | "
                f"Reverb {int(slot.reverb_mix * 100)}% | Chorus {int(slot.chorus_mix * 100)}%"
            )

    def _on_recall_clicked(self):
        row = self.slots_list.currentRow()
        if 0 <= row < 8:
            self.recall_slot_requested.emit(row)

    def _on_store_clicked(self):
        row = self.slots_list.currentRow()
        if 0 <= row < 8:
            name, ok = QInputDialog.getText(self, "Store Registration", "Enter registration name:", text=f"Setup {row + 1}")
            if ok and name:
                self.store_slot_requested.emit(row, name)
                self._refresh_slots_list()

    def _on_rename_clicked(self):
        row = self.slots_list.currentRow()
        if 0 <= row < 8:
            slot = self.reg_manager.get_slot(row)
            name, ok = QInputDialog.getText(self, "Rename Registration", "Enter new name:", text=slot.name)
            if ok and name:
                slot.name = name
                self.reg_manager.save_bank(self.reg_manager.current_bank)
                self._refresh_slots_list()

    def _on_clear_clicked(self):
        row = self.slots_list.currentRow()
        if 0 <= row < 8:
            self.reg_manager.clear_slot(row)
            self._refresh_slots_list()

    def _on_export_bank(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Bank", f"bank_{self.reg_manager.current_bank}.json", "JSON Files (*.json)")
        if path:
            self.reg_manager.save_bank(self.reg_manager.current_bank)
            QMessageBox.information(self, "Export Bank", "Bank exported successfully.")

    def _on_import_bank(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Bank", "", "JSON Files (*.json)")
        if path:
            self.reg_manager.load_bank(self.reg_manager.current_bank)
            self._refresh_slots_list()
