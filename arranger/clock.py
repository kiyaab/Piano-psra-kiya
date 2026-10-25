"""
KIYA Piano Studio Pro - High-Precision Musical Clock
Generates musical ticks, beats, and bars for the Arranger, Metronome, and MIDI playback.
Includes Tap Tempo detection and quantize timing.
"""

import time
import threading
from typing import Callable, Optional, List

class MusicalClock:
    """Thread-safe musical clock providing tick, beat, and bar notifications."""

    PPQ = 24  # Standard MIDI Pulses Per Quarter note (24 ticks per beat)

    def __init__(self, bpm: float = 120.0, time_sig_numerator: int = 4, time_sig_denominator: int = 4):
        self.bpm = max(30.0, min(300.0, bpm))
        self.numerator = time_sig_numerator
        self.denominator = time_sig_denominator
        self.is_running = False

        # Counters
        self.total_ticks = 0
        self.tick_in_beat = 0
        self.current_beat = 1  # 1-indexed (1 to numerator)
        self.current_bar = 1   # 1-indexed

        # Callbacks: on_tick(tick, beat, bar), on_beat(beat, bar), on_bar(bar)
        self.on_tick: Optional[Callable[[int, int, int], None]] = None
        self.on_beat: Optional[Callable[[int, int], None]] = None
        self.on_bar: Optional[Callable[[int], None]] = None

        # Background clock thread
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Tap tempo history
        self._tap_times: List[float] = []

    def set_tempo(self, bpm: float):
        """Set tempo in beats per minute."""
        with self._lock:
            self.bpm = max(30.0, min(300.0, float(bpm)))

    def set_time_signature(self, numerator: int, denominator: int = 4):
        """Set time signature (e.g. 4/4, 3/4, 6/8)."""
        with self._lock:
            self.numerator = max(1, min(16, numerator))
            self.denominator = max(1, min(16, denominator))

    def tap_tempo(self) -> float:
        """Register a tap and calculate BPM based on recent taps."""
        now = time.perf_counter()
        # Keep taps within last 2.5 seconds
        self._tap_times = [t for t in self._tap_times if (now - t) < 2.5]
        self._tap_times.append(now)

        if len(self._tap_times) >= 2:
            intervals = [self._tap_times[i] - self._tap_times[i - 1] for i in range(1, len(self._tap_times))]
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval > 0:
                calc_bpm = round(60.0 / avg_interval, 1)
                self.set_tempo(calc_bpm)
                return self.bpm
        return self.bpm

    def start(self):
        """Start the musical clock."""
        with self._lock:
            if self.is_running:
                return
            self.is_running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="MusicalClockThread")
            self._thread.start()

    def stop(self):
        """Stop the clock and reset counters to beat 1, bar 1."""
        with self._lock:
            self.is_running = False
            self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.3)
        self._thread = None
        self.reset()

    def pause(self):
        """Pause the clock without resetting position."""
        with self._lock:
            self.is_running = False
            self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.3)
        self._thread = None

    def reset(self):
        """Reset counters to start."""
        with self._lock:
            self.total_ticks = 0
            self.tick_in_beat = 0
            self.current_beat = 1
            self.current_bar = 1

    def _run_loop(self):
        """Precision timing loop utilizing perf_counter."""
        # Calculate seconds per tick: (60 / bpm) / PPQ
        next_tick_time = time.perf_counter()

        while not self._stop_event.is_set():
            now = time.perf_counter()
            if now < next_tick_time:
                sleep_sec = next_tick_time - now
                if sleep_sec > 0.001:
                    time.sleep(sleep_sec * 0.7)  # Sleep part of the interval to avoid CPU spin
                continue

            sec_per_beat = 60.0 / self.bpm
            sec_per_tick = sec_per_beat / self.PPQ
            next_tick_time += sec_per_tick

            # Process tick
            tick = self.tick_in_beat
            beat = self.current_beat
            bar = self.current_bar

            # Fire tick callback
            if self.on_tick:
                try:
                    self.on_tick(tick, beat, bar)
                except Exception as e:
                    print(f"[MusicalClock] Error in on_tick: {e}")

            # Fire beat callback on first tick of beat
            if tick == 0 and self.on_beat:
                try:
                    self.on_beat(beat, bar)
                except Exception as e:
                    print(f"[MusicalClock] Error in on_beat: {e}")

            # Fire bar callback on first tick of beat 1
            if tick == 0 and beat == 1 and self.on_bar:
                try:
                    self.on_bar(bar)
                except Exception as e:
                    print(f"[MusicalClock] Error in on_bar: {e}")

            # Advance clock counters
            self.total_ticks += 1
            self.tick_in_beat += 1
            if self.tick_in_beat >= self.PPQ:
                self.tick_in_beat = 0
                self.current_beat += 1
                if self.current_beat > self.numerator:
                    self.current_beat = 1
                    self.current_bar += 1
