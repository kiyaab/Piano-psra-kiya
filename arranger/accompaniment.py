"""
KIYA Piano Studio Pro - Automatic Accompaniment Coordinator
Binds the Musical Clock, Chord Detector, and Style Engine into a unified arranger workstation.
Provides Start/Stop, Sync Start, Sync Stop, Section selection, and Chord processing.
"""

from pathlib import Path
from typing import Optional, List, Callable
from app.constants import (
    SECTION_INTRO,
    SECTION_MAIN_A,
    SECTION_MAIN_B,
    SECTION_MAIN_C,
    SECTION_MAIN_D,
    SECTION_FILL_AA,
    SECTION_FILL_BB,
    SECTION_FILL_CC,
    SECTION_FILL_DD,
    SECTION_BREAK,
    SECTION_ENDING
)
from audio.synthesizer import SynthesizerFacade
from arranger.clock import MusicalClock
from arranger.chord_detector import ChordDetector, ChordInfo
from arranger.style_loader import StyleLoader, StyleDefinition
from arranger.style_engine import StyleEngine

class AccompanimentCoordinator:
    """Master controller for auto-accompaniment and arranger functions."""

    def __init__(self, synth: SynthesizerFacade):
        self.synth = synth
        self.clock = MusicalClock(bpm=120.0)
        self.chord_detector = ChordDetector(mode="full")
        self.style_engine = StyleEngine(synth=self.synth, clock=self.clock)

        # Accompaniment Toggles
        self.acmp_enabled = True
        self.sync_start = False
        self.sync_stop = False

        # Available styles list
        self.available_styles: List[StyleDefinition] = []
        self._load_styles()

        # Connect clock tick callback to style engine
        self.clock.on_tick = self._on_clock_tick

        # UI Notification Callbacks
        self.on_chord_changed: Optional[Callable[[ChordInfo], None]] = None
        self.on_beat_changed: Optional[Callable[[int, int], None]] = None
        self.on_section_changed: Optional[Callable[[str], None]] = None

        self.clock.on_beat = self._on_clock_beat

    def _load_styles(self):
        styles_dir = Path(__file__).resolve().parent.parent / "resources" / "styles"
        self.available_styles = StyleLoader.load_all_styles(str(styles_dir))
        if self.available_styles:
            self.select_style(self.available_styles[0])

    def select_style(self, style: StyleDefinition):
        """Set active accompaniment style."""
        self.style_engine.load_style(style)

    def select_style_by_name(self, name: str) -> bool:
        norm = name.strip().lower()
        for s in self.available_styles:
            if s.name.lower() == norm:
                self.select_style(s)
                return True
        for s in self.available_styles:
            s_norm = s.name.lower()
            if norm in s_norm or s_norm in norm:
                self.select_style(s)
                return True
        return False

    def start_accompaniment(self, initial_section: Optional[str] = None):
        """Start rhythm and accompaniment."""
        if not self.clock.is_running:
            sec = initial_section or self.style_engine.current_section_name or SECTION_MAIN_A
            self.style_engine.set_section(sec, immediate=True)
            self.clock.start()
            if self.on_section_changed:
                self.on_section_changed(sec)

    def stop_accompaniment(self):
        """Stop rhythm and accompaniment."""
        self.clock.stop()
        self.style_engine._silence_all_accompaniment()

    def toggle_start_stop(self):
        if self.clock.is_running:
            self.stop_accompaniment()
        else:
            self.start_accompaniment()

    def set_sync_start(self, enabled: bool):
        self.sync_start = enabled

    def set_sync_stop(self, enabled: bool):
        self.sync_stop = enabled

    def set_acmp_enabled(self, enabled: bool):
        self.acmp_enabled = enabled
        self.style_engine.bass_mute = not enabled
        self.style_engine.chords_mute = not enabled
        if not enabled:
            self.style_engine._silence_all_accompaniment()

    def set_accompaniment_enabled(self, enabled: bool):
        self.set_acmp_enabled(enabled)

    def set_section(self, section_name: str):
        """Trigger section change (Intro, Main A-D, Break, Ending)."""
        self.style_engine.set_section(section_name)
        if self.on_section_changed:
            self.on_section_changed(section_name)

    def trigger_fill(self, fill_name: str, target_main: str):
        self.style_engine.trigger_fill(fill_name, target_main)
        if self.on_section_changed:
            self.on_section_changed(fill_name)

    def process_chord_notes(self, active_chord_notes: List[int]):
        """Analyze notes played in chord zone and update harmonic accompaniment."""
        if not self.acmp_enabled:
            return

        if active_chord_notes:
            # Sync start: if waiting for chord to start accompaniment
            if self.sync_start and not self.clock.is_running:
                self.sync_start = False
                self.start_accompaniment()

            chord = self.chord_detector.detect_from_notes(active_chord_notes)
            if chord:
                self.style_engine.set_chord(chord)
                if self.on_chord_changed:
                    self.on_chord_changed(chord)
        else:
            # Keys lifted
            if self.sync_stop and self.clock.is_running:
                self.stop_accompaniment()

    def _on_clock_tick(self, tick_in_beat: int, current_beat: int, current_bar: int):
        self.style_engine.on_clock_tick(tick_in_beat, current_beat, current_bar)

    def _on_clock_beat(self, beat: int, bar: int):
        if self.on_beat_changed:
            self.on_beat_changed(beat, bar)
        if self.on_section_changed:
            self.on_section_changed(self.style_engine.current_section_name)

    @property
    def is_playing(self) -> bool:
        return self.clock.is_running

    @property
    def tempo(self) -> int:
        return int(round(self.clock.bpm))

    def set_tempo(self, bpm: int):
        self.clock.set_tempo(bpm)

    def start_playback(self):
        self.start_accompaniment()

    def stop_playback(self):
        self.stop_accompaniment()

    def set_variation(self, var: str):
        section_key = f"MAIN_{var.upper()}"
        self.set_section(section_key)

    def trigger_intro(self):
        if not self.is_playing:
            self.start_accompaniment(initial_section=SECTION_INTRO)
        else:
            self.set_section(SECTION_INTRO)

    def trigger_ending(self):
        self.set_section("ENDING")

    def trigger_break(self):
        self.set_section("BREAK")

    def load_style(self, name: str):
        self.select_style_by_name(name)

    @property
    def current_style_name(self) -> str:
        if self.style_engine.current_style:
            return self.style_engine.current_style.name
        return ""
