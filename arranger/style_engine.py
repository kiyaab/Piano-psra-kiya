"""
KIYA Piano Studio Pro - Arranger Style Playback Engine
Interprets style patterns in real-time synchronized to the musical clock,
dynamically transposing bass, chords, and phrases to match detected harmonic chords.
"""

from typing import Dict, List, Tuple, Optional, Set
from app.constants import (
    MIDI_CH_STYLE_DRUMS,
    MIDI_CH_STYLE_BASS,
    MIDI_CH_STYLE_CHORD1,
    MIDI_CH_STYLE_CHORD2,
    MIDI_CH_STYLE_PHRASE,
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
from arranger.chord_detector import ChordInfo
from arranger.style_loader import StyleDefinition, StyleSection, PatternEvent

class StyleEngine:
    """Real-time arranger engine transposing patterns and coordinating section transitions."""

    def __init__(self, synth: SynthesizerFacade, clock: MusicalClock):
        self.synth = synth
        self.clock = clock

        self.current_style: Optional[StyleDefinition] = None
        self.current_section_name: str = SECTION_MAIN_A
        self.queued_section_name: Optional[str] = None

        # Playback position in section
        self.section_tick = 0
        self.section_total_ticks = 96 * 2  # default 2 bars = 192 ticks

        # Harmonic state
        self.current_chord: ChordInfo = ChordInfo(
            root_name="C", root_pitch=0, quality="Maj", display_name="C",
            bass_name="C", is_inversion=False, notes=[60, 64, 67], intervals=(0, 4, 7)
        )

        # Track active sounding notes to schedule accurate note-offs
        # scheduled_note_offs[turn_off_tick] = list of (channel, note)
        self._scheduled_note_offs: Dict[int, List[Tuple[int, int]]] = {}

        # Mute / Volume per track
        self.drums_volume = 0.85
        self.bass_volume = 0.85
        self.chord1_volume = 0.75
        self.chord2_volume = 0.70
        self.phrase_volume = 0.75

        self.drums_mute = False
        self.bass_mute = False
        self.chords_mute = False

    def load_style(self, style: StyleDefinition):
        """Set current arranger style and initialize programs."""
        self.current_style = style
        self.clock.set_tempo(style.tempo)
        self.clock.set_time_signature(style.time_sig_num, style.time_sig_den)

        # Set synthesizer programs for accompaniment channels
        self.synth.set_program(MIDI_CH_STYLE_DRUMS, style.drum_program)
        self.synth.set_program(MIDI_CH_STYLE_BASS, style.bass_program)
        self.synth.set_program(MIDI_CH_STYLE_CHORD1, style.chord1_program)
        self.synth.set_program(MIDI_CH_STYLE_CHORD2, style.chord2_program)
        self.synth.set_program(MIDI_CH_STYLE_PHRASE, style.phrase_program)

        self.apply_track_volumes()
        self.set_section(SECTION_MAIN_A)

    def apply_track_volumes(self):
        """Send accompaniment track volumes to synthesizer."""
        self.synth.set_channel_volume(MIDI_CH_STYLE_DRUMS, 0.0 if self.drums_mute else self.drums_volume)
        self.synth.set_channel_volume(MIDI_CH_STYLE_BASS, 0.0 if self.bass_mute else self.bass_volume)
        self.synth.set_channel_volume(MIDI_CH_STYLE_CHORD1, 0.0 if self.chords_mute else self.chord1_volume)
        self.synth.set_channel_volume(MIDI_CH_STYLE_CHORD2, 0.0 if self.chords_mute else self.chord2_volume)
        self.synth.set_channel_volume(MIDI_CH_STYLE_PHRASE, self.phrase_volume)

    def set_chord(self, chord: ChordInfo):
        """Update active musical chord for harmonic transposition."""
        self.current_chord = chord

    def set_section(self, section_name: str, immediate: bool = False):
        """Transition to new section (e.g. MAIN_A, INTRO, etc.)."""
        if immediate or not self.clock.is_running:
            self._silence_all_accompaniment()
            self.current_section_name = section_name
            self.queued_section_name = None
            self.section_tick = 0
            self._update_section_bounds()
        else:
            self.queued_section_name = section_name

    def trigger_fill(self, fill_name: str, target_main: str):
        """Trigger fill in transition."""
        self.current_section_name = fill_name
        self.queued_section_name = target_main
        self.section_tick = 0
        self._update_section_bounds()

    def _update_section_bounds(self):
        if not self.current_style:
            self.section_total_ticks = 96 * 2
            return
        section = self.current_style.sections.get(self.current_section_name)
        bars = section.bars if section else 2
        ticks_per_bar = self.clock.numerator * self.clock.PPQ
        self.section_total_ticks = max(1, bars * ticks_per_bar)

    def on_clock_tick(self, tick_in_beat: int, current_beat: int, current_bar: int):
        """Clock callback triggered on every musical tick."""
        if not self.current_style:
            return

        # 1. Process pending note-offs for this tick
        self._process_scheduled_note_offs(self.clock.total_ticks)

        # 2. Check for section loop or transition boundary
        if self.section_tick >= self.section_total_ticks:
            self.section_tick = 0
            if self.queued_section_name:
                self.current_section_name = self.queued_section_name
                self.queued_section_name = None
                self._update_section_bounds()
            elif self.current_section_name == SECTION_INTRO:
                self.current_section_name = SECTION_MAIN_A
                self._update_section_bounds()
            elif self.current_section_name == SECTION_ENDING:
                # Stop clock at the end of the ending section
                self.clock.stop()
                self._silence_all_accompaniment()
                return

        section = self.current_style.sections.get(self.current_section_name)
        if not section:
            self.section_tick += 1
            return

        # 3. Fire drum pattern events
        if not self.drums_mute:
            for d in section.drums:
                if d.tick == self.section_tick:
                    self.synth.note_on(MIDI_CH_STYLE_DRUMS, d.note, d.vel)
                    self._schedule_note_off(MIDI_CH_STYLE_DRUMS, d.note, self.clock.total_ticks + d.duration)

        # 4. Fire bass pattern events (Harmonized to root and chord quality)
        if not self.bass_mute:
            for b in section.bass:
                if b.tick == self.section_tick:
                    bass_note = self._transpose_bass(b.note)
                    self.synth.note_on(MIDI_CH_STYLE_BASS, bass_note, b.vel)
                    self._schedule_note_off(MIDI_CH_STYLE_BASS, bass_note, self.clock.total_ticks + b.duration)

        # 5. Fire chord 1 pattern events
        if not self.chords_mute:
            for c in section.chord1:
                if c.tick == self.section_tick:
                    chord_notes = self._transpose_chord(c.degrees, base_octave=60)
                    for n in chord_notes:
                        self.synth.note_on(MIDI_CH_STYLE_CHORD1, n, c.vel)
                        self._schedule_note_off(MIDI_CH_STYLE_CHORD1, n, self.clock.total_ticks + c.duration)

        # 6. Fire chord 2 pattern events
        if not self.chords_mute:
            for c in section.chord2:
                if c.tick == self.section_tick:
                    chord_notes = self._transpose_chord(c.degrees, base_octave=48)
                    for n in chord_notes:
                        self.synth.note_on(MIDI_CH_STYLE_CHORD2, n, c.vel)
                        self._schedule_note_off(MIDI_CH_STYLE_CHORD2, n, self.clock.total_ticks + c.duration)

        # Advance section tick
        self.section_tick += 1

    def _transpose_bass(self, degree: int) -> int:
        """Transpose bass degree relative to detected chord root and quality."""
        root = self.current_chord.root_pitch
        # If minor chord and degree is major 3rd (4), adjust to minor 3rd (3)
        adj_deg = degree
        if "m" in self.current_chord.quality and adj_deg == 4:
            adj_deg = 3
        elif "dim" in self.current_chord.quality and adj_deg == 7:
            adj_deg = 6

        # Bass octave around 36 (C2)
        midi_note = 36 + root + adj_deg
        while midi_note > 52:
            midi_note -= 12
        while midi_note < 28:
            midi_note += 12
        return midi_note

    def _transpose_chord(self, degrees: List[int], base_octave: int = 60) -> List[int]:
        """Transpose chord degrees relative to detected chord root and quality."""
        root = self.current_chord.root_pitch
        transposed = []
        is_minor = ("m" in self.current_chord.quality and "Maj" not in self.current_chord.quality)
        is_dim = ("dim" in self.current_chord.quality)
        is_7th = ("7" in self.current_chord.quality and "Maj7" not in self.current_chord.quality)

        for d in degrees:
            adj = d
            if is_minor and adj == 4:
                adj = 3
            if is_dim and adj == 7:
                adj = 6
            if is_7th and adj == 11:
                adj = 10

            note = base_octave + root + adj
            transposed.append(max(0, min(127, note)))
        return transposed

    def _schedule_note_off(self, channel: int, note: int, target_tick: int):
        if target_tick not in self._scheduled_note_offs:
            self._scheduled_note_offs[target_tick] = []
        self._scheduled_note_offs[target_tick].append((channel, note))

    def _process_scheduled_note_offs(self, current_total_ticks: int):
        # Process any note-offs up to current tick
        expired_ticks = [t for t in self._scheduled_note_offs if t <= current_total_ticks]
        for t in expired_ticks:
            for ch, note in self._scheduled_note_offs.pop(t, []):
                self.synth.note_off(ch, note)

    def _silence_all_accompaniment(self):
        """Silence all active accompaniment notes across channels."""
        self._scheduled_note_offs.clear()
        for ch in [MIDI_CH_STYLE_DRUMS, MIDI_CH_STYLE_BASS, MIDI_CH_STYLE_CHORD1, MIDI_CH_STYLE_CHORD2, MIDI_CH_STYLE_PHRASE]:
            for n in range(128):
                self.synth.note_off(ch, n)
