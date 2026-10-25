"""
KIYA Piano Studio Pro - MIDI Song Player
Plays standard MIDI files with track muting, soloing, tempo scaling, and transposition.
"""

import time
import threading
from typing import List, Dict, Optional, Callable
import mido
from audio.synthesizer import SynthesizerFacade

class MidiSongPlayer:
    """Multi-track MIDI song player with real-time controls."""

    def __init__(self, synth: SynthesizerFacade):
        self.synth = synth
        self.mid_file: Optional[mido.MidiFile] = None
        self.is_playing = False
        self.is_paused = False
        self.file_path: str = ""

        # Playback parameters
        self.tempo_multiplier = 1.0  # 0.5x to 2.0x
        self.transpose_semitones = 0  # -12 to +12
        self.loop = False

        # Track status: track_idx -> bool
        self.track_mutes: Dict[int, bool] = {}
        self.track_solos: Dict[int, bool] = {}

        # Meta properties
        self.duration_seconds = 0.0
        self.current_position_seconds = 0.0
        self.track_names: List[str] = []
        self.initial_bpm = 120.0

        # Control thread
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_position_changed: Optional[Callable[[float, float], None]] = None
        self.on_playback_ended: Optional[Callable[[], None]] = None

    def load_file(self, file_path: str) -> bool:
        """Load and parse standard MIDI file."""
        self.stop()
        try:
            mid = mido.MidiFile(file_path)
            self.mid_file = mid
            self.file_path = file_path
            self.duration_seconds = mid.length
            self.current_position_seconds = 0.0

            self.track_names = []
            self.track_mutes.clear()
            self.track_solos.clear()

            for idx, track in enumerate(mid.tracks):
                self.track_names.append(track.name.strip() if track.name else f"Track {idx + 1}")
                self.track_mutes[idx] = False
                self.track_solos[idx] = False

            # Extract initial tempo
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        self.initial_bpm = round(mido.tempo2bpm(msg.tempo), 1)
                        break

            print(f"[MidiSongPlayer] Loaded '{file_path}' ({len(mid.tracks)} tracks, {round(mid.length, 1)}s)")
            return True
        except Exception as e:
            print(f"[MidiSongPlayer] Failed to load MIDI file: {e}")
            self.mid_file = None
            return False

    def play(self):
        """Start or resume playback."""
        if not self.mid_file:
            return
        if self.is_paused:
            self.is_paused = False
            return

        self.stop()
        self.is_playing = True
        self.is_paused = False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._play_loop, daemon=True, name="MidiSongPlayerThread")
        self._thread.start()

    def pause(self):
        if self.is_playing:
            self.is_paused = True

    def stop(self):
        """Stop playback and panic synthesizer."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.3)
        self._thread = None
        self.is_playing = False
        self.is_paused = False
        self.current_position_seconds = 0.0
        self.synth.panic()

    def set_tempo_multiplier(self, multiplier: float):
        self.tempo_multiplier = max(0.25, min(3.0, multiplier))

    def set_transpose(self, semitones: int):
        self.transpose_semitones = max(-24, min(24, semitones))

    def set_track_mute(self, track_idx: int, mute: bool):
        self.track_mutes[track_idx] = mute

    def set_track_solo(self, track_idx: int, solo: bool):
        self.track_solos[track_idx] = solo

    def _play_loop(self):
        """Playback loop iterating through mido messages with precise timing."""
        while not self._stop_event.is_set():
            start_time = time.perf_counter()
            elapsed_sim = 0.0

            # Iterate over messages
            for msg in self.mid_file.play(meta_messages=True):
                if self._stop_event.is_set():
                    break

                while self.is_paused and not self._stop_event.is_set():
                    time.sleep(0.02)

                # Skip meta messages or route musical events
                if not msg.is_meta:
                    # Check channel & transpose
                    if msg.type == 'note_on':
                        if msg.velocity > 0:
                            trans_note = max(0, min(127, msg.note + self.transpose_semitones))
                            self.synth.note_on(msg.channel, trans_note, msg.velocity)
                        else:
                            trans_note = max(0, min(127, msg.note + self.transpose_semitones))
                            self.synth.note_off(msg.channel, trans_note)
                    elif msg.type == 'note_off':
                        trans_note = max(0, min(127, msg.note + self.transpose_semitones))
                        self.synth.note_off(msg.channel, trans_note)
                    elif msg.type == 'control_change':
                        if msg.control == 64:
                            self.synth.set_sustain(msg.channel, msg.value >= 64)
                        elif msg.control == 7:
                            self.synth.set_channel_volume(msg.channel, msg.value / 127.0)
                    elif msg.type == 'program_change':
                        self.synth.set_program(msg.channel, msg.program)
                    elif msg.type == 'pitchwheel':
                        self.synth.pitch_bend(msg.channel, msg.pitch)

                self.current_position_seconds = time.perf_counter() - start_time
                if self.on_position_changed:
                    self.on_position_changed(self.current_position_seconds, self.duration_seconds)

            if not self.loop or self._stop_event.is_set():
                break

        self.synth.panic()
        self.is_playing = False
        if self.on_playback_ended and not self._stop_event.is_set():
            self.on_playback_ended()
