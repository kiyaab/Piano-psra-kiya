"""
KIYA Piano Studio Pro - Application Lifecycle Manager
Launches the realistic Yamaha PSR-S975 hardware workstation interface (HardwareWindow).
Supports fallback to Studio view if '--studio' argument is supplied.
"""

import sys
import signal
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.constants import APP_NAME, ORGANIZATION_NAME, APP_VERSION
from app.config import AppConfig
from ui.theme import get_dark_stylesheet
from ui.hardware_window import HardwareWindow
from ui.main_window import MainWindow

from audio.engine import AudioEngine
from keyboard.split_layer import SplitLayerManager
from arranger.accompaniment import AccompanimentCoordinator
from presets.registrations import RegistrationManager
from storage.database import DatabaseManager


class KiyaApplication:
    """Manages application lifecycle, theming, and top-level window hosting."""

    def __init__(self, argv=None):
        if argv is None:
            argv = sys.argv

        # High DPI attributes
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(argv)

        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        self.app.setOrganizationName(ORGANIZATION_NAME)

        # Apply dark styling
        self.app.setStyleSheet(get_dark_stylesheet())

        # Load Configuration
        self.config = AppConfig()

        # Check launch flags
        use_studio = "--studio" in argv

        if use_studio:
            # Classic studio dashboard
            self.window = MainWindow(self.config)
        else:
            # Realistic PSR-S975 Hardware Workstation
            self.db = DatabaseManager()
            self.audio_engine = AudioEngine(
                sample_rate=self.config.get("sample_rate", 44100),
                buffer_size=self.config.get("buffer_size", 512),
                device_index=self.config.get("audio_device_index", None),
                auto_start=True
            )
            self.split_layer = SplitLayerManager(synth=self.audio_engine.synth)
            self.arranger = AccompanimentCoordinator(synth=self.audio_engine.synth)
            self.reg_manager = RegistrationManager()

            self.window = HardwareWindow(
                audio_engine=self.audio_engine,
                split_layer=self.split_layer,
                arranger=self.arranger,
                reg_manager=self.reg_manager,
                db_manager=self.db,
                midi_engine=None
            )

        # Handle Ctrl+C cleanly
        signal.signal(signal.SIGINT, lambda sig, frame: self.quit())

    def run(self) -> int:
        """Display window and start Qt event loop."""
        self.window.show()
        return self.app.exec()

    def quit(self):
        """Clean shutdown."""
        if self.window:
            self.window.close()
        if self.app:
            self.app.quit()
