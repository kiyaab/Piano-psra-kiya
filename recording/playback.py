"""
KIYA Piano Studio Pro - Performance Playback Controller
Coordinates playback of recorded takes or session history.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from audio.synthesizer import SynthesizerFacade

class SessionPlayback:
    """Plays back recorded MIDI events through the synthesizer."""

    def __init__(self, synth: SynthesizerFacade):
        self.synth = synth
        self.is_playing = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.on_progress: Optional[Callable[[float, float], None]] = None
        self.on_finished: Optional[Callable[[], None]] = None

    def play(self, events: List[Dict[str, Any]]):
        """Play back a list of recorded events."""
        self.stop()
        if not events:
            return
        self.is_playing = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._play_loop, args=(events,), daemon=True, name="SessionPlaybackThread")
        self._thread.start()

    def stop(self):
        """Stop playback immediately and panic notes."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.3)
        self._thread = None
        self.is_playing = False
        self.synth.panic()

    def _play_loop(self, events: List[Dict[str, Any]]):
        sorted_events = sorted(events, key=lambda e: e['time_sec'])
        if not sorted_events:
            self.is_playing = False
            return

        total_duration = sorted_events[-1]['time_sec']
        start_time = time.perf_counter()

        for e in sorted_events:
            if self._stop_event.is_set():
                break

            target_time = start_time + e['time_sec']
            while time.perf_counter() < target_time:
                if self._stop_event.is_set():
                    break
                time.sleep(0.001)

            if self._stop_event.is_set():
                break

            # Dispatch event
            etype = e['type']
            ch = e['channel']
            if etype == 'note_on':
                self.synth.note_on(ch, e['note'], e['velocity'])
            elif etype == 'note_off':
                self.synth.note_off(ch, e['note'])
            elif etype == 'control_change':
                if e['control'] == 64:
                    self.synth.set_sustain(ch, e['value'] >= 64)
            elif etype == 'pitchwheel':
                self.synth.pitch_bend(ch, e['pitch'])

            if self.on_progress:
                elapsed = time.perf_counter() - start_time
                self.on_progress(elapsed, total_duration)

        self.synth.panic()
        self.is_playing = False
        if self.on_finished and not self._stop_event.is_set():
            self.on_finished()
