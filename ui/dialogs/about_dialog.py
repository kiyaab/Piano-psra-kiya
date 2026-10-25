"""
KIYA Piano Studio Pro - About Dialog
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from app.constants import APP_NAME, APP_VERSION, APP_SUBTITLE, ORGANIZATION_NAME, COLOR_ACCENT_ORANGE, COLOR_TEXT_SECONDARY

class AboutDialog(QDialog):
    """About dialog showing application credentials."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedSize(460, 320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel(APP_NAME)
        title.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLOR_ACCENT_ORANGE};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(f"{APP_SUBTITLE} — Version {APP_VERSION}")
        subtitle.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLOR_TEXT_SECONDARY};")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        info = QLabel(
            "Inspired by the workflow and capabilities of professional arranger workstations.\n\n"
            "• 61-Key Virtual Piano with velocity-sensitive glissando\n"
            "• Real-Time Multi-Timbral DSP and Windows General MIDI\n"
            "• Automatic Accompaniment & Chord Recognition Engine\n"
            "• Multi-Track MIDI & WAV Performance Recording Studio\n"
            "• Piano Roll Editor, Multi-Channel Mixer & DSP Effects\n\n"
            f"Developed by {ORGANIZATION_NAME} for Windows 10 & 11."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #D1D7E0; line-height: 1.4;")
        layout.addWidget(info)
        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)
