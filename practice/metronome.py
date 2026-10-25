"""
KIYA Piano Studio Pro - Audible & Visual Metronome
Provides high-precision audible metronome clicks with accented downbeat,
configurable time signatures, count-in, and visual beat indicators.
"""

from typing import Optional, Callable
from arranger.clock import MusicalClock
from audio.synthesizer import SynthesizerFacade
from app.constants import MIDI_CH_STYLE_DRUMS, DRUM_SIDE_STICK, DRUM_HI_WOOD_BLOCK, DRUM_LOW_WOOD_BLOCK

class Metronome:
    """Metronome engine coordinating audible clicks and visual beat signals."""

    def __init__(self, clock: MusicalClock, synth: SynthesizerFacade):
        self.clock = clock
        self.synth = synth
        self.is_audible = True
        self.is_count_in = False
        self.count_in_bars = 1
        self.remaining_count_in_beats = 0

        self.on_beat_flash: Optional[Callable[[int, bool], None]] = None # beat, is_downbeat
        self.on_count_in_finished: Optional[Callable[[], None]] = None

        # Hook to clock beat callback
        old_beat_cb = self.clock.on_beat
        def _beat_handler(beat: int, bar: int):
            if old_beat_cb:
                old_beat_cb(beat, bar)
            self._handle_beat(beat, bar)
        self.clock.on_beat = _beat_handler

    def set_audible(self, enabled: bool):
        self.is_audible = enabled

    def start(self, with_count_in: bool = False):
        if with_count_in:
            self.is_count_in = True
            self.remaining_count_in_beats = self.count_in_bars * self.clock.numerator
        else:
            self.is_count_in = False
        self.clock.start()

    def stop(self):
        self.is_count_in = False
        self.clock.stop()

    def _handle_beat(self, beat: int, bar: int):
        is_downbeat = (beat == 1)

        # 1. Trigger audible woodblock click on drum channel
        if self.is_audible:
            click_note = DRUM_HI_WOOD_BLOCK if is_downbeat else DRUM_LOW_WOOD_BLOCK
            velocity = 115 if is_downbeat else 90
            self.synth.note_on(MIDI_CH_STYLE_DRUMS, click_note, velocity)
            # Short release
            self.synth.note_off(MIDI_CH_STYLE_DRUMS, click_note)

        # 2. Trigger visual beat notification
        if self.on_beat_flash:
            self.on_beat_flash(beat, is_downbeat)

        # 3. Handle Count-In countdown
        if self.is_count_in:
            self.remaining_count_in_beats -= 1
            if self.remaining_count_in_beats <= 0:
                self.is_count_in = False
                if self.on_count_in_finished:
                    self.on_count_in_finished()
