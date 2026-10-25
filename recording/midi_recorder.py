"""
KIYA Piano Studio Pro - Multi-Track MIDI Performance Recorder
Captures live note-on, note-off, velocity, sustain, and pitch bend with precision timing.
Exports Standard MIDI Files (.mid) using mido.
"""

import time
import threading
from typing import List, Tuple, Dict, Optional
import mido

class MidiRecorder:
    """Records multi-track performance events and generates standard MIDI files."""

    def __init__(self, ppq: int = 480):
        self.ppq = ppq
        self.is_recording = False
        self.is_paused = False
        self._lock = threading.Lock()

        # Track events: list of (delta_ticks, message)
        # We record separate tracks:
        # Track 0: Master tempo & time sig
        # Track 1: Right Hand Main (Ch 1)
        # Track 2: Right Hand Layer (Ch 2)
        # Track 3: Left Hand (Ch 3)
        # Track 4: Arranger Accompaniment (Drums Ch 10, Bass Ch 9, Chords Ch 11/12)
        self.recorded_events: List[Dict[str, Any]] = []
        self.start_time: float = 0.0
        self.pause_time: float = 0.0
        self.total_paused_duration: float = 0.0
        self.current_bpm: float = 120.0

    def start_recording(self, bpm: float = 120.0):
        """Begin recording."""
        with self._lock:
            self.current_bpm = bpm
            self.recorded_events.clear()
            self.start_time = time.perf_counter()
            self.total_paused_duration = 0.0
            self.is_recording = True
            self.is_paused = False
            print("[MidiRecorder] Recording started.")

    def pause_recording(self):
        with self._lock:
            if self.is_recording and not self.is_paused:
                self.is_paused = True
                self.pause_time = time.perf_counter()

    def resume_recording(self):
        with self._lock:
            if self.is_recording and self.is_paused:
                self.total_paused_duration += (time.perf_counter() - self.pause_time)
                self.is_paused = False

    def stop_recording(self) -> int:
        """Stop recording and return count of captured events."""
        with self._lock:
            self.is_recording = False
            self.is_paused = False
            count = len(self.recorded_events)
            print(f"[MidiRecorder] Recording stopped. Total events: {count}")
            return count

    def record_note_on(self, channel: int, note: int, velocity: int):
        if not self.is_recording or self.is_paused:
            return
        now = time.perf_counter() - self.start_time - self.total_paused_duration
        with self._lock:
            self.recorded_events.append({
                'type': 'note_on',
                'channel': channel,
                'note': note,
                'velocity': velocity,
                'time_sec': max(0.0, now)
            })

    def record_note_off(self, channel: int, note: int):
        if not self.is_recording or self.is_paused:
            return
        now = time.perf_counter() - self.start_time - self.total_paused_duration
        with self._lock:
            self.recorded_events.append({
                'type': 'note_off',
                'channel': channel,
                'note': note,
                'velocity': 0,
                'time_sec': max(0.0, now)
            })

    def record_cc(self, channel: int, control: int, value: int):
        if not self.is_recording or self.is_paused:
            return
        now = time.perf_counter() - self.start_time - self.total_paused_duration
        with self._lock:
            self.recorded_events.append({
                'type': 'control_change',
                'channel': channel,
                'control': control,
                'value': value,
                'time_sec': max(0.0, now)
            })

    def record_pitch_bend(self, channel: int, pitch: int):
        if not self.is_recording or self.is_paused:
            return
        now = time.perf_counter() - self.start_time - self.total_paused_duration
        with self._lock:
            self.recorded_events.append({
                'type': 'pitchwheel',
                'channel': channel,
                'pitch': pitch,
                'time_sec': max(0.0, now)
            })

    def export_to_midi_file(self, file_path: str) -> bool:
        """Export recorded session to standard Type 1 MIDI file."""
        with self._lock:
            if not self.recorded_events:
                print("[MidiRecorder] Warning: No events to export.")
                return False

            try:
                mid = mido.MidiFile(type=1, ticks_per_beat=self.ppq)

                # Track 0: Tempo and conductor
                conductor_track = mido.MidiTrack()
                mid.tracks.append(conductor_track)
                tempo_val = mido.bpm2tempo(self.current_bpm)
                conductor_track.append(mido.MetaMessage('set_tempo', tempo=tempo_val, time=0))
                conductor_track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
                conductor_track.append(mido.MetaMessage('track_name', name="Conductor", time=0))
                conductor_track.append(mido.MetaMessage('end_of_track', time=0))

                # Track 1: Performance Track
                perf_track = mido.MidiTrack()
                mid.tracks.append(perf_track)
                perf_track.append(mido.MetaMessage('track_name', name="KIYA Performance", time=0))

                # Sort events chronologically by time_sec
                sorted_events = sorted(self.recorded_events, key=lambda e: e['time_sec'])

                last_tick = 0
                sec_per_tick = (60.0 / self.current_bpm) / self.ppq

                for e in sorted_events:
                    event_tick = int(round(e['time_sec'] / sec_per_tick))
                    delta = max(0, event_tick - last_tick)
                    last_tick = event_tick

                    etype = e['type']
                    if etype == 'note_on':
                        msg = mido.Message('note_on', channel=e['channel'], note=e['note'], velocity=e['velocity'], time=delta)
                    elif etype == 'note_off':
                        msg = mido.Message('note_off', channel=e['channel'], note=e['note'], velocity=0, time=delta)
                    elif etype == 'control_change':
                        msg = mido.Message('control_change', channel=e['channel'], control=e['control'], value=e['value'], time=delta)
                    elif etype == 'pitchwheel':
                        msg = mido.Message('pitchwheel', channel=e['channel'], pitch=e['pitch'], time=delta)
                    else:
                        continue

                    perf_track.append(msg)

                perf_track.append(mido.MetaMessage('end_of_track', time=self.ppq))
                mid.save(file_path)
                print(f"[MidiRecorder] Exported MIDI file successfully: {file_path}")
                return True
            except Exception as e:
                print(f"[MidiRecorder] Error exporting MIDI file: {e}")
                return False
