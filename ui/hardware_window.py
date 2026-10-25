"""
KIYA Piano Studio Pro - Master Hardware Window (PSR-S975 Workstation)
The top-level widescreen desktop application window.
Renders the realistic Yamaha PSR-S975 arranger workstation chassis, LCD screen,
hardware panels, middle strip, and 61-key piano keybed.
"""

from typing import Optional
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStatusBar, QLabel, QApplication
)
from PySide6.QtGui import QKeyEvent, QCloseEvent, QIcon

from audio.engine import AudioEngine
from keyboard.split_layer import SplitLayerManager
from keyboard.computer_keymap import ComputerKeymap
from arranger.accompaniment import AccompanimentCoordinator
from presets.registrations import RegistrationManager
from midi.input_manager import MidiInputManager
from storage.database import DatabaseManager

from ui.hardware_shell import HardwareShell
from ui.interaction_controller import InteractionController
from ui.hardware_theme import HardwareColors, HardwareFonts


class HardwareWindow(QMainWindow):
    """
    KIYA Piano Studio Pro - Master Hardware Instrument Window.
    Widescreen realistic virtual arranger workstation adapting cleanly to display size.
    """
    def __init__(
        self,
        audio_engine: AudioEngine,
        split_layer: SplitLayerManager,
        arranger: AccompanimentCoordinator,
        reg_manager: RegistrationManager,
        db_manager: DatabaseManager,
        midi_engine: Optional[MidiInputManager] = None,
        parent=None
    ):
        super().__init__(parent)
        self.audio = audio_engine
        self.split_layer = split_layer
        self.arranger = arranger
        self.reg_manager = reg_manager
        self.db = db_manager
        self.midi = midi_engine

        self.setWindowTitle("KIYA Piano Studio Pro — PSR-S975 Arranger Workstation")

        # Dynamic screen-aware initial sizing
        screen = QApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1600, max(1100, int(avail.width() * 0.95)))
            target_h = min(900, max(640, int(avail.height() * 0.92)))
            self.resize(target_w, target_h)
        else:
            self.resize(1400, 800)

        self.setMinimumSize(1024, 600)
        self.setStyleSheet(f"background-color: {HardwareColors.CHASSIS_BG};")

        # Computer Keyboard mapping
        self.keymap = ComputerKeymap(base_note=48)

        # Central widget: Hardware Shell
        self.shell = HardwareShell(self)
        self.setCentralWidget(self.shell)

        # Interaction Controller
        self.controller = InteractionController(
            shell=self.shell,
            audio_engine=self.audio,
            split_layer=self.split_layer,
            arranger=self.arranger,
            reg_manager=self.reg_manager,
            computer_keymap=self.keymap,
            midi_engine=self.midi,
            parent=self
        )

        # Subtle bottom status bar
        status = QStatusBar(self)
        status.setStyleSheet("background: #08090B; color: #5D6C7B; font-size: 11px; border-top: 1px solid #14161A;")
        lbl_info = QLabel("  KIYA Piano Studio Pro  |  PSR-S975 Hardware Engine  |  [F11] Fullscreen  |  [ESC] Panic  |  PC Keys: Z-M / Q-U")
        lbl_info.setFont(HardwareFonts.micro_regular())
        status.addWidget(lbl_info)
        self.setStatusBar(status)

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
            event.accept()
            return
        elif event.key() == Qt.Key_Escape:
            # Panic action: silence all notes
            self.audio.synth.panic()
            self.shell.keybed.release_all_keys()
            event.accept()
            return

        # Route to musical computer keyboard
        self.controller.handle_key_press(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        self.controller.handle_key_release(event)
        super().keyReleaseEvent(event)

    def changeEvent(self, event):
        # On focus loss, prevent stuck keys
        if event.type() == event.Type.ActivationChange and not self.isActiveWindow():
            self.audio.synth.panic()
            self.shell.keybed.release_all_keys()
        super().changeEvent(event)

    def closeEvent(self, event: QCloseEvent):
        # Clean shutdown of audio, synthesizer, and arranger clock
        try:
            if self.arranger.is_playing:
                self.arranger.stop_playback()
            if self.audio.is_recording:
                self.audio.stop_recording()
            self.audio.synth.panic()
            self.audio.stop()
            if self.midi:
                self.midi.close_port()
        except Exception:
            pass
        event.accept()
