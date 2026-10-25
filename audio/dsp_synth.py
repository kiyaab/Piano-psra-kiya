"""
KIYA Piano Studio Pro - Real-Time Polyphonic Software DSP Synthesizer
Generates multi-timbral polyphonic audio for melodic instruments and Channel 10 drums.
Includes ADSR envelopes, FM / harmonic modeling, and voice allocation.
Operates at 44.1kHz float32 stereo.
"""

import math
import random
import threading
from typing import Dict, List, Optional
import numpy as np

class DSPVoice:
    """Individual polyphonic voice instance with ADSR and synthesis model."""

    __slots__ = (
        'channel', 'note', 'velocity', 'freq', 'program',
        'phase', 'phase2', 'phase_mod', 'mod_idx',
        'env_stage', 'env_level', 'env_step',
        'attack_frames', 'decay_frames', 'sustain_level', 'release_frames',
        'decay_rate', 'is_drum', 'age', 'pan_l', 'pan_r', 'is_dead'
    )

    STAGE_OFF = 0
    STAGE_ATTACK = 1
    STAGE_DECAY = 2
    STAGE_SUSTAIN = 3
    STAGE_RELEASE = 4

    def __init__(self, channel: int, note: int, velocity: int, program: int, sample_rate: int = 44100):
        self.channel = channel
        self.note = note
        self.velocity = velocity / 127.0
        self.program = program
        self.freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
        self.phase = 0.0
        self.phase2 = 0.0
        self.phase_mod = 0.0
        self.mod_idx = 1.5
        self.age = 0
        self.is_dead = False
        self.is_drum = (channel == 9)

        # Stereo Panning (default center)
        self.pan_l = 0.707
        self.pan_r = 0.707

        # ADSR Envelope Setup based on instrument category / program
        self.env_stage = self.STAGE_ATTACK
        self.env_level = 0.0

        if self.is_drum:
            # Drum presets (percussive short envelopes)
            self.attack_frames = max(1, int(0.002 * sample_rate))
            if note in (35, 36):  # Bass Drum
                self.decay_frames = int(0.28 * sample_rate)
            elif note in (38, 40): # Snare
                self.decay_frames = int(0.22 * sample_rate)
            elif note in (42, 44): # Closed Hat / Pedal Hat
                self.decay_frames = int(0.06 * sample_rate)
            elif note == 46:       # Open Hat
                self.decay_frames = int(0.35 * sample_rate)
            elif note in (49, 51, 57): # Cymbals
                self.decay_frames = int(0.85 * sample_rate)
            else:
                self.decay_frames = int(0.18 * sample_rate)
            self.sustain_level = 0.0
            self.release_frames = int(0.02 * sample_rate)
            self.decay_rate = 0.999
        elif program in range(0, 8):  # Pianos
            self.attack_frames = max(1, int(0.005 * sample_rate))
            self.decay_frames = int(1.8 * sample_rate)
            self.sustain_level = 0.45
            self.release_frames = int(0.25 * sample_rate)
            self.decay_rate = 0.9998
        elif program in range(16, 24):  # Organs
            self.attack_frames = max(1, int(0.012 * sample_rate))
            self.decay_frames = int(0.05 * sample_rate)
            self.sustain_level = 0.85
            self.release_frames = int(0.08 * sample_rate)
            self.decay_rate = 1.0
        elif program in range(24, 32):  # Guitars
            self.attack_frames = max(1, int(0.008 * sample_rate))
            self.decay_frames = int(1.2 * sample_rate)
            self.sustain_level = 0.25
            self.release_frames = int(0.15 * sample_rate)
            self.decay_rate = 0.9995
        elif program in range(32, 40):  # Basses
            self.attack_frames = max(1, int(0.008 * sample_rate))
            self.decay_frames = int(0.8 * sample_rate)
            self.sustain_level = 0.50
            self.release_frames = int(0.12 * sample_rate)
            self.decay_rate = 0.9996
        elif program in range(40, 56):  # Strings & Ensemble
            self.attack_frames = max(1, int(0.12 * sample_rate))
            self.decay_frames = int(0.3 * sample_rate)
            self.sustain_level = 0.75
            self.release_frames = int(0.40 * sample_rate)
            self.decay_rate = 1.0
        elif program in range(56, 64):  # Brass
            self.attack_frames = max(1, int(0.035 * sample_rate))
            self.decay_frames = int(0.25 * sample_rate)
            self.sustain_level = 0.70
            self.release_frames = int(0.18 * sample_rate)
            self.decay_rate = 1.0
        elif program in range(88, 96):  # Synth Pads
            self.attack_frames = max(1, int(0.25 * sample_rate))
            self.decay_frames = int(0.4 * sample_rate)
            self.sustain_level = 0.80
            self.release_frames = int(0.60 * sample_rate)
            self.decay_rate = 1.0
        else:  # Default melodic
            self.attack_frames = max(1, int(0.01 * sample_rate))
            self.decay_frames = int(0.6 * sample_rate)
            self.sustain_level = 0.60
            self.release_frames = int(0.20 * sample_rate)
            self.decay_rate = 0.9997

        self.env_step = 1.0 / self.attack_frames

    def release(self):
        """Transition voice to release stage."""
        if self.env_stage != self.STAGE_OFF and self.env_stage != self.STAGE_RELEASE:
            self.env_stage = self.STAGE_RELEASE
            if self.release_frames > 0:
                self.env_step = self.env_level / self.release_frames
            else:
                self.env_step = 1.0
                self.env_stage = self.STAGE_OFF
                self.is_dead = True


class DSPSynthesizer:
    """Real-time polyphonic synthesizer with vectorized voice rendering."""

    def __init__(self, sample_rate: int = 44100, max_polyphony: int = 64):
        self.sample_rate = sample_rate
        self.max_polyphony = max_polyphony
        self._lock = threading.RLock()
        self.voices: List[DSPVoice] = []

        # Channel configurations: program, volume, pan
        self.channel_programs: Dict[int, int] = {ch: 0 for ch in range(16)}
        self.channel_programs[9] = 0  # Drums
        self.channel_programs[8] = 32 # Bass
        self.channel_volumes: Dict[int, float] = {ch: 1.0 for ch in range(16)}
        self.channel_pans: Dict[int, float] = {ch: 0.0 for ch in range(16)}  # -1.0 left to +1.0 right
        self.master_volume: float = 0.85

        # Note queue for thread-safe cross-thread event pushing
        self._event_queue: List[tuple] = []

    def set_program(self, channel: int, program: int):
        with self._lock:
            self.channel_programs[channel] = max(0, min(127, program))

    def set_volume(self, channel: int, volume: float):
        with self._lock:
            self.channel_volumes[channel] = max(0.0, min(1.5, volume))

    def set_pan(self, channel: int, pan: float):
        with self._lock:
            self.channel_pans[channel] = max(-1.0, min(1.0, pan))

    def note_on(self, channel: int, note: int, velocity: int):
        with self._lock:
            self._event_queue.append(('on', channel, note, velocity))

    def note_off(self, channel: int, note: int):
        with self._lock:
            self._event_queue.append(('off', channel, note, 0))

    def all_notes_off(self):
        with self._lock:
            self._event_queue.append(('panic', 0, 0, 0))

    def _process_queue(self):
        """Process incoming note events before rendering audio chunk."""
        if not self._event_queue:
            return
        with self._lock:
            events = self._event_queue[:]
            self._event_queue.clear()

        for evt, ch, note, vel in events:
            if evt == 'on':
                # Voice stealing if max polyphony exceeded
                if len(self.voices) >= self.max_polyphony:
                    # Remove oldest or quietest voice
                    oldest_idx = 0
                    oldest_age = -1
                    for i, v in enumerate(self.voices):
                        if v.env_stage == DSPVoice.STAGE_RELEASE:
                            oldest_idx = i
                            break
                        if v.age > oldest_age:
                            oldest_age = v.age
                            oldest_idx = i
                    if self.voices:
                        self.voices.pop(oldest_idx)

                # Create new voice
                prog = self.channel_programs.get(ch, 0)
                v = DSPVoice(ch, note, vel, prog, self.sample_rate)
                # Apply channel pan
                pan = self.channel_pans.get(ch, 0.0)
                # Equal power pan
                angle = (pan + 1.0) * 0.25 * math.pi
                v.pan_l = math.cos(angle)
                v.pan_r = math.sin(angle)
                self.voices.append(v)

            elif evt == 'off':
                for v in self.voices:
                    if v.channel == ch and v.note == note and not v.is_dead:
                        v.release()

            elif evt == 'panic':
                for v in self.voices:
                    v.release()
                self.voices.clear()

    def render(self, frames: int) -> np.ndarray:
        """Render 'frames' number of float32 stereo audio samples [frames, 2]."""
        self._process_queue()
        buffer = np.zeros((frames, 2), dtype=np.float32)

        if not self.voices:
            return buffer

        dt = 1.0 / self.sample_rate
        alive_voices: List[DSPVoice] = []

        for v in self.voices:
            if v.is_dead:
                continue

            v.age += frames
            ch_vol = self.channel_volumes.get(v.channel, 1.0) * self.master_volume * v.velocity
            if ch_vol <= 0.0001:
                continue

            # Render individual voice waveform
            t_chunk = np.arange(frames, dtype=np.float32)
            
            # --- Synthesis Engine per instrument type ---
            if v.is_drum:
                # Drum synthesis
                if v.note in (35, 36):  # Bass Drum (Punchy pitch-dropping sine)
                    pitch_env = np.exp(-t_chunk * (40.0 / self.sample_rate) - (v.age * 40.0 / self.sample_rate))
                    freq_arr = 55.0 + 130.0 * pitch_env
                    phase_arr = v.phase + 2.0 * np.pi * np.cumsum(freq_arr) * dt
                    wave = np.sin(phase_arr)
                    v.phase = phase_arr[-1] % (2.0 * np.pi)
                elif v.note in (38, 40):  # Snare (body + noise)
                    phase_arr = v.phase + 2.0 * np.pi * 185.0 * t_chunk * dt
                    tone = np.sin(phase_arr) * 0.4
                    noise = (np.random.uniform(-1.0, 1.0, frames).astype(np.float32)) * 0.6
                    wave = tone + noise
                    v.phase = (v.phase + 2.0 * np.pi * 185.0 * frames * dt) % (2.0 * np.pi)
                elif v.note in (42, 44, 46):  # Hi-Hats (metallic noise)
                    noise = np.random.uniform(-1.0, 1.0, frames).astype(np.float32)
                    wave = noise
                elif v.note in (49, 51, 57):  # Cymbals
                    noise = np.random.uniform(-1.0, 1.0, frames).astype(np.float32)
                    wave = noise * 0.8
                else:  # Toms / Percussion
                    freq_t = max(70.0, 320.0 - (v.note - 41) * 20.0)
                    phase_arr = v.phase + 2.0 * np.pi * freq_t * t_chunk * dt
                    wave = np.sin(phase_arr)
                    v.phase = (v.phase + 2.0 * np.pi * freq_t * frames * dt) % (2.0 * np.pi)

            elif v.program in range(0, 8):  # Acoustic & Electric Pianos
                # Rich multi-harmonic model with hammer transient
                f = v.freq
                p = v.phase + 2.0 * np.pi * f * t_chunk * dt
                # Fundamental + harmonics 2, 3, 4, 5 with acoustic decay
                wave = (
                    0.55 * np.sin(p) +
                    0.25 * np.sin(2.0 * p) +
                    0.12 * np.sin(3.0 * p) +
                    0.06 * np.sin(4.0 * p) +
                    0.02 * np.sin(5.0 * p)
                )
                v.phase = p[-1] % (2.0 * np.pi)

            elif v.program in range(16, 24):  # Organs (Hammond drawbars)
                f = v.freq
                p = v.phase + 2.0 * np.pi * f * t_chunk * dt
                wave = (
                    0.40 * np.sin(p) +
                    0.30 * np.sin(2.0 * p) +
                    0.15 * np.sin(3.0 * p) +
                    0.10 * np.sin(4.0 * p) +
                    0.05 * np.sin(6.0 * p)
                )
                v.phase = p[-1] % (2.0 * np.pi)

            elif v.program in range(24, 32):  # Guitars (Bright plucked tone)
                f = v.freq
                p = v.phase + 2.0 * np.pi * f * t_chunk * dt
                wave = (
                    0.50 * np.sin(p) +
                    0.30 * np.sin(2.0 * p) +
                    0.15 * np.sin(3.0 * p) +
                    0.05 * np.sin(5.0 * p)
                )
                v.phase = p[-1] % (2.0 * np.pi)

            elif v.program in range(32, 40):  # Bass (Warm sub + fundamental)
                f = v.freq
                p = v.phase + 2.0 * np.pi * f * t_chunk * dt
                wave = 0.65 * np.sin(p) + 0.35 * np.sin(2.0 * p)
                v.phase = p[-1] % (2.0 * np.pi)

            elif v.program in range(40, 56) or v.program in range(88, 96):  # Strings & Pads
                # Detuned lush sawtooth ensemble
                f = v.freq
                p1 = (v.phase + f * t_chunk * dt) % 1.0
                p2 = (v.phase2 + (f * 1.006) * t_chunk * dt) % 1.0
                saw1 = 2.0 * p1 - 1.0
                saw2 = 2.0 * p2 - 1.0
                wave = (saw1 + saw2) * 0.45
                v.phase = p1[-1]
                v.phase2 = p2[-1]

            elif v.program in range(56, 64):  # Brass
                f = v.freq
                p = (v.phase + f * t_chunk * dt) % 1.0
                saw = 2.0 * p - 1.0
                wave = saw * 0.65
                v.phase = p[-1]

            else:  # Generic melodic
                f = v.freq
                p = v.phase + 2.0 * np.pi * f * t_chunk * dt
                wave = 0.7 * np.sin(p) + 0.3 * np.sin(2.0 * p)
                v.phase = p[-1] % (2.0 * np.pi)

            # ADSR Envelope evaluation across the chunk
            env = np.empty(frames, dtype=np.float32)
            lvl = v.env_level
            step = v.env_step

            for i in range(frames):
                if v.env_stage == DSPVoice.STAGE_ATTACK:
                    lvl += step
                    if lvl >= 1.0:
                        lvl = 1.0
                        v.env_stage = DSPVoice.STAGE_DECAY
                        decay_span = max(1, v.decay_frames)
                        step = (1.0 - v.sustain_level) / decay_span
                elif v.env_stage == DSPVoice.STAGE_DECAY:
                    lvl -= step
                    if lvl <= v.sustain_level:
                        lvl = v.sustain_level
                        v.env_stage = DSPVoice.STAGE_SUSTAIN
                elif v.env_stage == DSPVoice.STAGE_SUSTAIN:
                    # Gradual natural decay during sustain
                    lvl *= v.decay_rate
                    if lvl < 0.001:
                        v.env_stage = DSPVoice.STAGE_OFF
                        v.is_dead = True
                        lvl = 0.0
                elif v.env_stage == DSPVoice.STAGE_RELEASE:
                    lvl -= step
                    if lvl <= 0.001:
                        lvl = 0.0
                        v.env_stage = DSPVoice.STAGE_OFF
                        v.is_dead = True
                else:
                    lvl = 0.0
                    v.is_dead = True

                env[i] = lvl

            v.env_level = lvl
            v.env_step = step

            # Multiply synthesized wave by envelope and channel volume
            sig = wave * env * ch_vol
            buffer[:, 0] += sig * v.pan_l
            buffer[:, 1] += sig * v.pan_r

            if not v.is_dead:
                alive_voices.append(v)

        self.voices = alive_voices
        return buffer
