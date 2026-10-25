"""
KIYA Piano Studio Pro - Main Application Workstation Window
Binds together the Top Toolbar, Navigation Pages, 61-Key Virtual Piano Keyboard,
and Bottom Performance Strip with real-time synthesizer and arranger engines.
"""

from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QToolBar, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtGui import QAction, QIcon, QKeyEvent
from app.constants import (
    APP_NAME,
    APP_VERSION,
    APP_SUBTITLE,
    COLOR_BG,
    COLOR_PANEL_MAIN,
    COLOR_BORDER,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    midi_to_note_name
)
from app.config import AppConfig
from audio.engine import AudioEngine
from keyboard.split_layer import SplitLayerManager
from keyboard.computer_keymap import ComputerKeymap
from arranger.accompaniment import AccompanimentCoordinator
from presets.voice_browser import VoiceBrowser
from presets.registrations import RegistrationManager, RegistrationSlot
from recording.midi_recorder import MidiRecorder
from recording.audio_recorder import AudioRecorder
from recording.playback import SessionPlayback
from songs.midi_player import MidiSongPlayer
from storage.project_repository import ProjectRepository
from storage.database import DatabaseManager

from ui.widgets.piano_widget import PianoKeyboardWidget
from ui.widgets.performance_strip import PerformanceStripWidget
from ui.widgets.pitch_mod_wheels import PitchModWheelsWidget
from ui.pages.performance_page import PerformancePage
from ui.pages.voices_page import VoicesPage
from ui.pages.arranger_page import ArrangerPage
from ui.pages.mixer_page import MixerPage
from ui.pages.effects_page import EffectsPage
from ui.pages.recording_page import RecordingPage
from ui.pages.song_player_page import SongPlayerPage
from ui.pages.practice_page import PracticePage
from ui.pages.registrations_page import RegistrationsPage
from ui.pages.settings_page import SettingsPage
from ui.dialogs.soundfont_wizard import SoundFontWizardDialog
from ui.dialogs.about_dialog import AboutDialog

class MainWindow(QMainWindow):
    """Master Arranger Workstation window."""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.setWindowTitle(f"{APP_NAME} — {APP_SUBTITLE}")
        self.resize(self.config.get("window_width", 1280), self.config.get("window_height", 840))

        # -------------------------------------------------------------
        # 1. Initialize Core Engines
        # -------------------------------------------------------------
        self.db = DatabaseManager()
        self.audio_engine = AudioEngine(
            sample_rate=self.config.get("sample_rate", 44100),
            buffer_size=self.config.get("buffer_size", 512),
            device_index=self.config.get("audio_device_index", None)
        )
        self.split_layer = SplitLayerManager(synth=self.audio_engine.synth)
        self.computer_keymap = ComputerKeymap(base_note=48)
        self.arranger = AccompanimentCoordinator(synth=self.audio_engine.synth)
        self.voice_browser = VoiceBrowser(
            favorites=self.config.get("favorite_voices", []),
            recents=self.config.get("recent_voices", [])
        )
        self.reg_manager = RegistrationManager()
        self.midi_recorder = MidiRecorder()
        self.audio_recorder = AudioRecorder(sample_rate=self.audio_engine.sample_rate)
        self.session_playback = SessionPlayback(synth=self.audio_engine.synth)
        self.song_player = MidiSongPlayer(synth=self.audio_engine.synth)

        # Connect audio recorder tap
        self.audio_engine.set_record_tap(self.audio_recorder.add_audio_buffer)

        # Track currently held computer keys to prevent auto-repeat re-trigger
        self._pressed_pc_keys = set()
        self._is_sustain_down = False
        self._metronome_enabled = False

        # -------------------------------------------------------------
        # 2. Build User Interface Layout
        # -------------------------------------------------------------
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top Toolbar
        self._build_top_toolbar(root_layout)

        # Navigation Tabs Area (The 10 Pages)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        root_layout.addWidget(self.tabs, 1)

        # Build & Add Pages
        self.page_performance = PerformancePage()
        self.page_voices = VoicesPage(self.voice_browser)
        self.page_arranger = ArrangerPage(self.arranger.available_styles)
        self.page_mixer = MixerPage()
        self.page_effects = EffectsPage()
        self.page_recording = RecordingPage()
        self.page_song_player = SongPlayerPage()
        self.page_practice = PracticePage()
        self.page_registrations = RegistrationsPage(self.reg_manager)
        self.page_settings = SettingsPage()

        self.tabs.addTab(self.page_performance, "🎹 Arranger Workstation")
        self.tabs.addTab(self.page_voices, "🎵 Voices")
        self.tabs.addTab(self.page_arranger, "🥁 Styles & Arranger")
        self.tabs.addTab(self.page_mixer, "🎚 Mixer")
        self.tabs.addTab(self.page_effects, "✨ Effects")
        self.tabs.addTab(self.page_recording, "🎙 Recording")
        self.tabs.addTab(self.page_song_player, "🎼 Song Player")
        self.tabs.addTab(self.page_practice, "📚 Practice & Learn")
        self.tabs.addTab(self.page_registrations, "💾 Registrations")
        self.tabs.addTab(self.page_settings, "⚙ Settings")

        # Playing Surface Deck (Pitch & Mod Wheels + 61-Key Keyboard)
        deck_frame = QFrame()
        deck_frame.setObjectName("PlayingDeck")
        deck_frame.setStyleSheet(f"background-color: {COLOR_PANEL_MAIN}; border-top: 1px solid {COLOR_BORDER}; padding: 2px;")
        deck_layout = QHBoxLayout(deck_frame)
        deck_layout.setContentsMargins(6, 4, 6, 4)
        deck_layout.setSpacing(6)

        self.wheels_widget = PitchModWheelsWidget()
        deck_layout.addWidget(self.wheels_widget)

        self.piano_widget = PianoKeyboardWidget()
        self.piano_widget.set_split_point(self.split_layer.split_point, show_marker=self.split_layer.split_enabled)
        deck_layout.addWidget(self.piano_widget, 1)

        root_layout.addWidget(deck_frame)

        # Bottom Performance Strip
        self.performance_strip = PerformanceStripWidget()
        root_layout.addWidget(self.performance_strip)

        # -------------------------------------------------------------
        # 3. Connect Signals and Events
        # -------------------------------------------------------------
        self._connect_signals()

        # UI Visual Refresh Timer (30 FPS for waveform and VU meters)
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._on_ui_timer)
        self.ui_timer.start(33)

        # Load initial registration slot 1
        self._recall_registration_slot(0)

    def _build_top_toolbar(self, parent_layout: QVBoxLayout):
        """Build sleek top workstation header and toolbar."""
        bar_frame = QFrame()
        bar_frame.setStyleSheet(f"background-color: {COLOR_PANEL_MAIN}; border-bottom: 1px solid {COLOR_BORDER}; padding: 4px 12px;")
        bar_layout = QHBoxLayout(bar_frame)
        bar_layout.setContentsMargins(8, 4, 8, 4)
        bar_layout.setSpacing(12)

        # App Logo & Branding
        logo_lbl = QLabel(f"KIYA PIANO STUDIO PRO")
        logo_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLOR_ACCENT_ORANGE}; letter-spacing: 1px;")
        bar_layout.addWidget(logo_lbl)

        # Project File Actions
        btn_new = QPushButton("New")
        btn_new.clicked.connect(self._new_project)
        bar_layout.addWidget(btn_new)

        btn_open = QPushButton("Open...")
        btn_open.clicked.connect(self._open_project)
        bar_layout.addWidget(btn_open)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self._save_project)
        bar_layout.addWidget(btn_save)

        bar_layout.addStretch()

        # Engine Status Indicators
        self.lbl_audio_status = QLabel("● Audio: 44.1kHz | 512f (~11.6ms)")
        self.lbl_audio_status.setStyleSheet(f"color: {COLOR_SUCCESS}; font-size: 11px; font-weight: bold;")
        bar_layout.addWidget(self.lbl_audio_status)

        self.lbl_midi_status = QLabel("● MIDI: Windows GS Synth")
        self.lbl_midi_status.setStyleSheet(f"color: {COLOR_ACCENT_BLUE}; font-size: 11px;")
        bar_layout.addWidget(self.lbl_midi_status)

        # SoundFont Wizard Button
        btn_wizard = QPushButton("🧙 SoundFont Wizard")
        btn_wizard.clicked.connect(self._open_soundfont_wizard)
        bar_layout.addWidget(btn_wizard)

        # About Dialog Button
        btn_about = QPushButton("ℹ About")
        btn_about.clicked.connect(self._open_about_dialog)
        bar_layout.addWidget(btn_about)

        parent_layout.addWidget(bar_frame)

    def _connect_signals(self):
        """Hook up signals between UI controls and music/audio engines."""
        # --- Keyboard Interactions ---
        self.piano_widget.note_pressed.connect(self._on_user_note_pressed)
        self.piano_widget.note_released.connect(self._on_user_note_released)

        # --- Performance Strip ---
        self.performance_strip.layer_toggled.connect(self._on_layer_toggled)
        self.performance_strip.split_toggled.connect(self._on_split_toggled)
        self.performance_strip.registration_selected.connect(self._recall_registration_slot)
        self.performance_strip.panic_triggered.connect(self._on_panic)
        self.performance_strip.record_toggled.connect(self._toggle_recording)
        self.performance_strip.tap_tempo_clicked.connect(self._on_tap_tempo)

        # --- Performance Wheels ---
        self.wheels_widget.pitch_bend_changed.connect(lambda val: self.audio_engine.synth.pitch_bend(0, val))
        self.wheels_widget.modulation_changed.connect(lambda val: self.audio_engine.synth.modulation(0, val))

        # --- Performance Page (Master Arranger Console) ---
        self.page_performance.start_stop_requested.connect(self._toggle_arranger_playback)
        self.page_performance.section_requested.connect(self.arranger.set_section)
        self.page_performance.fill_requested.connect(self.arranger.trigger_fill)
        self.page_performance.sync_start_toggled.connect(self.arranger.set_sync_start)
        self.page_performance.sync_stop_toggled.connect(self.arranger.set_sync_stop)
        self.page_performance.acmp_toggled.connect(self.arranger.set_acmp_enabled)
        self.page_performance.style_selected.connect(self._on_style_selected)
        self.page_performance.tempo_changed.connect(self.arranger.clock.set_tempo)
        self.page_performance.tap_tempo_clicked.connect(self._on_tap_tempo)
        self.page_performance.metronome_toggled.connect(self._toggle_metronome)
        self.page_performance.transpose_changed.connect(self._on_transpose_changed)
        self.page_performance.octave_changed.connect(self._on_octave_changed)
        self.page_performance.voice_assigned.connect(self._on_voice_assigned)
        self.page_performance.layer_toggled.connect(self._on_layer_toggled)
        self.page_performance.split_toggled.connect(self._on_split_toggled)
        self.page_performance.sustain_toggled.connect(self._on_sustain_toggled)
        self.page_performance.touch_curve_changed.connect(self.audio_engine.synth.note_manager.set_velocity_curve)
        self.page_performance.open_voice_browser_requested.connect(lambda: self.tabs.setCurrentIndex(1))
        self.page_performance.registration_selected.connect(self._recall_registration_slot)
        self.page_performance.registration_store_requested.connect(lambda idx: self._store_registration_slot(idx, f"Reg {idx + 1}"))
        self.page_performance.multipad_triggered.connect(self._on_multipad_triggered)
        self.page_performance.chord_mode_changed.connect(self.arranger.chord_detector.set_mode)
        self.page_performance.master_vol_changed.connect(self.audio_engine.set_master_volume)
        self.page_performance.acmp_vol_changed.connect(self._on_acmp_volume_changed)
        self.page_performance.keyboard_vol_changed.connect(self._on_keyboard_volume_changed)
        self.page_performance.split_vol_changed.connect(self._on_split_volume_changed)
        self.page_performance.reverb_changed.connect(lambda mix: self.audio_engine.effects.reverb.set_params(mix=mix))

        # --- Voices Page ---
        self.page_voices.voice_assigned.connect(self._on_voice_assigned)
        self.page_voices.voice_preview_requested.connect(self._preview_voice)

        # --- Arranger Page ---
        self.page_arranger.style_selected.connect(self.arranger.select_style_by_name)
        self.page_arranger.section_selected.connect(self.arranger.set_section)
        self.page_arranger.tempo_changed.connect(self.arranger.clock.set_tempo)
        self.page_arranger.chord_mode_changed.connect(self.arranger.chord_detector.set_mode)
        self.page_arranger.track_volume_changed.connect(self._on_arranger_track_volume)

        # --- Mixer Page ---
        self.page_mixer.master_volume_changed.connect(self.audio_engine.set_master_volume)
        self.page_mixer.channel_volume_changed.connect(self._on_channel_volume_changed)
        self.page_mixer.channel_pan_changed.connect(self._on_channel_pan_changed)

        # --- Effects Page ---
        self.page_effects.eq_changed.connect(self._on_eq_changed)
        self.page_effects.reverb_changed.connect(self.audio_engine.effects.reverb.set_params)
        self.page_effects.chorus_changed.connect(self.audio_engine.effects.chorus.set_params)
        self.page_effects.delay_changed.connect(self.audio_engine.effects.delay.set_params)

        # --- Recording Page ---
        self.page_recording.start_recording_requested.connect(self._start_recording)
        self.page_recording.pause_recording_requested.connect(self._pause_recording)
        self.page_recording.resume_recording_requested.connect(self._resume_recording)
        self.page_recording.stop_recording_requested.connect(self._stop_recording)
        self.page_recording.export_take_requested.connect(self._export_take)

        # --- Song Player Page ---
        self.page_song_player.load_midi_requested.connect(self._load_song_file)
        self.page_song_player.play_requested.connect(self.song_player.play)
        self.page_song_player.pause_requested.connect(self.song_player.pause)
        self.page_song_player.stop_requested.connect(self.song_player.stop)
        self.page_song_player.tempo_scale_changed.connect(self.song_player.set_tempo_multiplier)
        self.page_song_player.note_preview_requested.connect(self._preview_note)

        # --- Practice Page ---
        self.page_practice.metronome_start_stop_requested.connect(self._toggle_metronome)
        self.page_practice.metronome_tempo_changed.connect(self.arranger.clock.set_tempo)
        self.page_practice.play_chord_requested.connect(self._play_chord_notes)
        self.page_practice.highlight_keys_requested.connect(self.piano_widget.set_highlighted_notes)

        # --- Registrations Page ---
        self.page_registrations.recall_slot_requested.connect(self._recall_registration_slot)
        self.page_registrations.store_slot_requested.connect(self._store_registration_slot)

        # --- Settings Page ---
        self.page_settings.audio_config_changed.connect(self._on_audio_config_changed)
        self.page_settings.audio_backend_changed.connect(self.audio_engine.synth.set_engine_mode)
        self.page_settings.midi_output_changed.connect(self.audio_engine.synth.midi_synth.open_port)
        self.page_settings.play_test_tone_requested.connect(lambda: self.audio_engine.synth.note_on(0, 60, 100))
        self.page_settings.velocity_curve_changed.connect(self.audio_engine.synth.note_manager.set_velocity_curve)
        self.page_settings.open_soundfont_wizard_requested.connect(self._open_soundfont_wizard)

        # --- Arranger & Clock UI Callbacks ---
        self.arranger.on_chord_changed = self._on_chord_detected
        self.arranger.on_beat_changed = self._on_beat_changed
        self.arranger.on_section_changed = self._on_section_changed

    # -------------------------------------------------------------
    # Note Handling & Dispatching
    # -------------------------------------------------------------
    def _on_user_note_pressed(self, note: int, velocity: int):
        """User played note via mouse, computer keyboard, or MIDI device."""
        self.split_layer.route_note_on(note, velocity)
        self.midi_recorder.record_note_on(0, note, velocity)
        self.page_practice.evaluate_played_note(note)

        # Pass notes played in left zone to chord recognizer (with transpose)
        tr = self.split_layer.master_transpose
        if self.split_layer.split_enabled:
            left_notes = [n + tr for n in self.split_layer._sounding_routes.keys() if n <= self.split_layer.split_point]
            self.arranger.process_chord_notes(left_notes)
        else:
            # Full keyboard chord recognition
            all_active = [n + tr for n in self.split_layer._sounding_routes.keys()]
            self.arranger.process_chord_notes(all_active)

    def _on_user_note_released(self, note: int):
        self.split_layer.route_note_off(note)
        self.midi_recorder.record_note_off(0, note)

        tr = self.split_layer.master_transpose
        if self.split_layer.split_enabled:
            left_notes = [n + tr for n in self.split_layer._sounding_routes.keys() if n <= self.split_layer.split_point]
            self.arranger.process_chord_notes(left_notes)
        else:
            all_active = [n + tr for n in self.split_layer._sounding_routes.keys()]
            self.arranger.process_chord_notes(all_active)

    def _on_panic(self):
        """Emergency panic kill."""
        self.split_layer.panic()
        self.piano_widget.release_all_visual_keys()
        self.page_performance.chord_widget.clear()
        print("[MainWindow] Panic reset executed.")

    def _on_tap_tempo(self):
        bpm = self.arranger.clock.tap_tempo()
        self.page_performance.update_style_display(self.arranger.style_engine.current_style.name if self.arranger.style_engine.current_style else "Pop Groove", int(bpm), "4/4")

    # -------------------------------------------------------------
    # Computer Keyboard Events
    # -------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        key_text = event.text()

        # Sustain toggle via Spacebar
        if event.key() == Qt.Key.Key_Space:
            self._is_sustain_down = True
            self.page_performance.btn_sustain.setChecked(True)
            self.audio_engine.synth.set_sustain(0, True)
            return

        # Octave shift hotkeys
        if event.key() == Qt.Key.Key_BracketLeft or key_text == "[":
            self.page_performance._octave_down()
            return
        elif event.key() == Qt.Key.Key_BracketRight or key_text == "]":
            self.page_performance._octave_up()
            return

        if key_text:
            note = self.computer_keymap.key_to_note(key_text)
            if note is not None and note not in self._pressed_pc_keys:
                self._pressed_pc_keys.add(note)
                self.piano_widget.set_key_sounding(note, True)
                self._on_user_note_pressed(note, 100)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        if event.key() == Qt.Key.Key_Space:
            self._is_sustain_down = False
            self.page_performance.btn_sustain.setChecked(False)
            self.audio_engine.synth.set_sustain(0, False)
            return

        key_text = event.text()
        if key_text:
            note = self.computer_keymap.key_to_note(key_text)
            if note is not None and note in self._pressed_pc_keys:
                self._pressed_pc_keys.remove(note)
                self.piano_widget.set_key_sounding(note, False)
                self._on_user_note_released(note)

    # -------------------------------------------------------------
    # Arranger & Registration Callbacks
    # -------------------------------------------------------------
    def _toggle_arranger_playback(self):
        self.arranger.toggle_start_stop()
        self.page_performance.set_start_stop_state(self.arranger.clock.is_running)

    def _on_chord_detected(self, chord):
        self.page_performance.chord_widget.set_chord(chord)

    def _on_beat_changed(self, beat: int, bar: int):
        self.page_performance.update_beat(beat, bar, is_downbeat=(beat == 1))
        if getattr(self, '_metronome_enabled', False):
            click_note = 76 if (beat == 1) else 77
            self.audio_engine.synth.note_on(9, click_note, 100)
            QTimer.singleShot(80, lambda note=click_note: self.audio_engine.synth.note_off(9, note))

    def _on_section_changed(self, section: str):
        pass

    def _on_transpose_changed(self, semitones: int):
        self.split_layer.master_transpose = semitones

    def _on_octave_changed(self, octaves: int):
        self.computer_keymap.set_octave_offset(octaves)
        self.split_layer.right1_octave = octaves

    def _on_sustain_toggled(self, active: bool):
        self._is_sustain_down = active
        self.audio_engine.synth.set_sustain(0, active)

    def _toggle_metronome(self, enabled: bool):
        self._metronome_enabled = enabled

    def _on_style_selected(self, style_name: str):
        success = self.arranger.select_style_by_name(style_name)
        if success and self.arranger.style_engine.current_style:
            s = self.arranger.style_engine.current_style
            self.page_performance.update_style_display(s.name, s.tempo, f"{s.time_sig_num}/{s.time_sig_den}")

    def _on_multipad_triggered(self, pad_idx: int):
        pad_notes = [39, 38, 49, 29]
        if 0 <= pad_idx < len(pad_notes):
            n = pad_notes[pad_idx]
            self.audio_engine.synth.note_on(9, n, 115)
            QTimer.singleShot(250, lambda note=n: self.audio_engine.synth.note_off(9, note))

    def _on_acmp_volume_changed(self, vol: float):
        self.arranger.style_engine.drums_volume = vol
        self.arranger.style_engine.bass_volume = vol
        self.arranger.style_engine.chord1_volume = vol * 0.90
        self.arranger.style_engine.chord2_volume = vol * 0.85
        self.arranger.style_engine.phrase_volume = vol * 0.90
        self.arranger.style_engine.apply_track_volumes()

    def _on_keyboard_volume_changed(self, vol: float):
        self.split_layer.right1_volume = vol
        self.split_layer.right2_volume = vol * 0.75
        self.split_layer.apply_all_programs()

    def _on_split_volume_changed(self, vol: float):
        self.split_layer.left_volume = vol
        self.split_layer.apply_all_programs()

    def _on_layer_toggled(self, enabled: bool):
        self.split_layer.set_layer_enabled(enabled)
        self.performance_strip.btn_layer.setChecked(enabled)
        self._refresh_voices_display()

    def _on_split_toggled(self, enabled: bool):
        self.split_layer.set_split_enabled(enabled)
        self.performance_strip.btn_split.setChecked(enabled)
        self.piano_widget.set_split_point(self.split_layer.split_point, show_marker=enabled)
        self._refresh_voices_display()

    def _on_voice_assigned(self, target: str, program: int):
        if target == "right1":
            self.split_layer.right1_program = program
        elif target == "right2":
            self.split_layer.right2_program = program
            self.split_layer.set_layer_enabled(True)
            self.performance_strip.btn_layer.setChecked(True)
        elif target == "left":
            self.split_layer.left_program = program
            self.split_layer.set_split_enabled(True)
            self.performance_strip.btn_split.setChecked(True)

        self.split_layer.apply_all_programs()
        self._refresh_voices_display()

    def _preview_voice(self, program: int):
        self.audio_engine.synth.set_program(0, program)
        self.audio_engine.synth.note_on(0, 60, 100)
        QTimer.singleShot(400, lambda: self.audio_engine.synth.note_off(0, 60))

    def _preview_note(self, note: int, velocity: int):
        self.audio_engine.synth.note_on(0, note, velocity)
        QTimer.singleShot(350, lambda: self.audio_engine.synth.note_off(0, note))

    def _play_chord_notes(self, notes: list):
        for n in notes:
            self.audio_engine.synth.note_on(0, n, 95)
        QTimer.singleShot(600, lambda: [self.audio_engine.synth.note_off(0, n) for n in notes])

    def _refresh_voices_display(self):
        r1_name = self.voice_browser.get_voice_name(self.split_layer.right1_program)
        r2_name = self.voice_browser.get_voice_name(self.split_layer.right2_program)
        left_name = self.voice_browser.get_voice_name(self.split_layer.left_program)
        split_name = midi_to_note_name(self.split_layer.split_point)
        self.page_performance.update_voices_display(
            r1_name, r2_name, left_name,
            self.split_layer.layer_enabled,
            self.split_layer.split_enabled,
            split_name
        )

    def _recall_registration_slot(self, slot_idx: int):
        slot = self.reg_manager.get_slot(slot_idx)
        if slot.is_empty:
            return

        self._on_panic()
        self.split_layer.right1_program = slot.right1_voice
        self.split_layer.right1_volume = slot.right1_volume
        self.split_layer.layer_enabled = slot.layer_enabled
        self.split_layer.right2_program = slot.right2_voice
        self.split_layer.right2_volume = slot.right2_volume
        self.split_layer.split_enabled = slot.split_enabled
        self.split_layer.split_point = slot.split_point
        self.split_layer.left_voice = slot.left_voice
        self.split_layer.left_volume = slot.left_volume
        self.split_layer.apply_all_programs()

        self.performance_strip.btn_layer.setChecked(slot.layer_enabled)
        self.performance_strip.btn_split.setChecked(slot.split_enabled)
        self.performance_strip.set_active_slot(slot_idx)
        self.piano_widget.set_split_point(slot.split_point, show_marker=slot.split_enabled)

        self.arranger.select_style_by_name(slot.style_name)
        self.arranger.clock.set_tempo(slot.tempo)
        self.audio_engine.set_master_volume(slot.master_volume)

        self.audio_engine.effects.reverb.set_params(mix=slot.reverb_mix)
        self.audio_engine.effects.chorus.set_params(mix=slot.chorus_mix)
        self.audio_engine.effects.delay.set_params(mix=slot.delay_mix)

        self._refresh_voices_display()
        self.page_performance.update_style_display(slot.style_name, slot.tempo, "4/4")

    def _store_registration_slot(self, slot_idx: int, slot_name: str):
        slot = RegistrationSlot(
            name=slot_name,
            is_empty=False,
            right1_voice=self.split_layer.right1_program,
            right1_volume=self.split_layer.right1_volume,
            layer_enabled=self.split_layer.layer_enabled,
            right2_voice=self.split_layer.right2_program,
            right2_volume=self.split_layer.right2_volume,
            split_enabled=self.split_layer.split_enabled,
            split_point=self.split_layer.split_point,
            left_voice=self.split_layer.left_program,
            left_volume=self.split_layer.left_volume,
            style_name=self.arranger.style_engine.current_style.name if self.arranger.style_engine.current_style else "Pop Groove",
            tempo=int(self.arranger.clock.bpm),
            master_volume=self.audio_engine.master_volume,
            reverb_mix=self.audio_engine.effects.reverb.mix,
            chorus_mix=self.audio_engine.effects.chorus.mix,
            delay_mix=self.audio_engine.effects.delay.mix
        )
        self.reg_manager.save_slot(slot_idx, slot)

    # -------------------------------------------------------------
    # Recording Studio Handling
    # -------------------------------------------------------------
    def _toggle_recording(self):
        if not self.page_recording.is_recording:
            self.tabs.setCurrentWidget(self.page_recording)
            self.page_recording._on_rec_clicked()
        else:
            self.page_recording._on_stop_clicked()

    def _start_recording(self, mode: str, count_in: bool):
        if mode == "midi":
            self.midi_recorder.start_recording(bpm=self.arranger.clock.bpm)
        else:
            tmp_wav = str(Path("d:/PIANO GAME PY/temp_take.wav"))
            self.audio_recorder.start_recording(tmp_wav)
        self.performance_strip.btn_record.setChecked(True)

    def _pause_recording(self):
        self.midi_recorder.pause_recording()
        self.audio_recorder.pause_recording()

    def _resume_recording(self):
        self.midi_recorder.resume_recording()
        self.audio_recorder.resume_recording()

    def _stop_recording(self):
        self.performance_strip.btn_record.setChecked(False)
        self.midi_recorder.stop_recording()
        self.audio_recorder.stop_and_finalize()
        take_num = self.page_recording.takes_list.count() + 1
        self.page_recording.add_take_item(f"Take {take_num:02d} ({self.page_recording.combo_mode.currentText()})")

    def _export_take(self, take_idx: int, path: str):
        if path.lower().endswith(".mid"):
            self.midi_recorder.export_to_midi_file(path)
        else:
            self.audio_recorder.stop_and_finalize()
            # Copy temp file to target path
            import shutil
            shutil.copy("d:/PIANO GAME PY/temp_take.wav", path)
        QMessageBox.information(self, "Export", f"File exported successfully to:\n{path}")

    # -------------------------------------------------------------
    # Song Player & Practice
    # -------------------------------------------------------------
    def _load_song_file(self, filepath: str):
        success = self.song_player.load_file(filepath)
        if success:
            self.page_song_player.set_song_info(
                Path(filepath).stem,
                self.song_player.duration_seconds,
                self.song_player.initial_bpm
            )

    def _toggle_metronome(self, running: bool):
        if running:
            self.arranger.clock.start()
        else:
            self.arranger.clock.stop()

    # -------------------------------------------------------------
    # Audio Engine & Mixer Routing
    # -------------------------------------------------------------
    def _on_channel_volume_changed(self, key: str, vol: float):
        if key == "right1":
            self.split_layer.right1_volume = vol
            self.split_layer.apply_all_programs()
        elif key == "right2":
            self.split_layer.right2_volume = vol
            self.split_layer.apply_all_programs()
        elif key == "left":
            self.split_layer.left_volume = vol
            self.split_layer.apply_all_programs()
        elif key == "drums":
            self.arranger.style_engine.drums_volume = vol
            self.arranger.style_engine.apply_track_volumes()
        elif key == "bass":
            self.arranger.style_engine.bass_volume = vol
            self.arranger.style_engine.apply_track_volumes()
        elif key == "chords":
            self.arranger.style_engine.chord1_volume = vol
            self.arranger.style_engine.chord2_volume = vol
            self.arranger.style_engine.apply_track_volumes()

    def _on_channel_pan_changed(self, key: str, pan: float):
        if key == "right1":
            self.split_layer.right1_pan = pan
            self.split_layer.apply_all_programs()
        elif key == "right2":
            self.split_layer.right2_pan = pan
            self.split_layer.apply_all_programs()
        elif key == "left":
            self.split_layer.left_pan = pan
            self.split_layer.apply_all_programs()

    def _on_arranger_track_volume(self, track_key: str, vol: float):
        if track_key == "drums":
            self.arranger.style_engine.drums_volume = vol
        elif track_key == "bass":
            self.arranger.style_engine.bass_volume = vol
        elif track_key == "chords":
            self.arranger.style_engine.chord1_volume = vol
            self.arranger.style_engine.chord2_volume = vol
        self.arranger.style_engine.apply_track_volumes()

    def _on_eq_changed(self, band: str, gain_db: float):
        if band == "low":
            self.audio_engine.effects.eq_low.set_params(gain_db=gain_db)
        elif band == "mid":
            self.audio_engine.effects.eq_mid.set_params(gain_db=gain_db)
        elif band == "high":
            self.audio_engine.effects.eq_high.set_params(gain_db=gain_db)

    def _on_audio_config_changed(self, sr: int, bs: int, dev):
        self.audio_engine.restart_with_config(sr, bs, dev)
        self.lbl_audio_status.setText(f"● Audio: {sr}Hz | {bs}f (~{round((bs / sr) * 1000, 1)}ms)")

    # -------------------------------------------------------------
    # UI Timer (Peak Meters & Waveform update)
    # -------------------------------------------------------------
    def _on_ui_timer(self):
        # Update Oscilloscope Waveform on performance page
        self.page_performance.waveform_widget.set_audio_data(self.audio_engine.waveform_buffer)
        # Update Mixer VU meters
        self.page_mixer.update_meters(self.audio_engine.peak_left, self.audio_engine.peak_right)

    # -------------------------------------------------------------
    # Dialogs & Projects
    # -------------------------------------------------------------
    def _open_soundfont_wizard(self):
        dlg = SoundFontWizardDialog(self.audio_engine.synth.fluidsynth, self)
        dlg.exec()

    def _open_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def _new_project(self):
        self._on_panic()
        self._recall_registration_slot(0)
        QMessageBox.information(self, "New Project", "New workstation project initialized.")

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open KIYA Project", "", "KIYA Project Files (*.kiya)")
        if path:
            data = ProjectRepository.load_project(path)
            if data:
                QMessageBox.information(self, "Project Loaded", f"Loaded project: {data.get('name', 'Project')}")

    def _save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save KIYA Project", "MySong.kiya", "KIYA Project Files (*.kiya)")
        if path:
            project_data = {
                "name": Path(path).stem,
                "version": APP_VERSION,
                "tempo": self.arranger.clock.bpm,
                "right1": self.split_layer.right1_program,
                "right2": self.split_layer.right2_program,
                "left": self.split_layer.left_program,
                "style": self.arranger.style_engine.current_style.name if self.arranger.style_engine.current_style else "Pop Groove"
            }
            ProjectRepository.save_project(path, project_data)
            QMessageBox.information(self, "Project Saved", f"Project saved to:\n{path}")

    def closeEvent(self, event):
        """Clean shutdown and resource release."""
        self._on_panic()
        self.audio_engine.close()
        self.arranger.clock.stop()
        self.song_player.stop()
        super().closeEvent(event)
