"""
KIYA Piano Studio Pro - Central Audio Engine
Runs the real-time SoundDevice audio stream callback, routes audio through DSP effects,
provides audio buffer taps for UI waveform displays and VU meters, and handles WAV recording taps.
"""

import threading
import sounddevice as sd
import numpy as np
from typing import Optional, Callable
from audio.synthesizer import SynthesizerFacade
from audio.effects import EffectsChain
from app.constants import DEFAULT_SAMPLE_RATE, DEFAULT_BUFFER_SIZE

class AudioEngine:
    """Master audio engine managing the audio output stream and visual taps."""

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE, buffer_size: int = DEFAULT_BUFFER_SIZE, device_index: Optional[int] = None, auto_start: bool = True):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.device_index = device_index
        self._lock = threading.RLock()

        # Core synthesizer and effects
        self.synth = SynthesizerFacade(sample_rate=sample_rate)
        self.effects = EffectsChain(sample_rate=sample_rate)

        # Audio stream
        self.stream: Optional[sd.OutputStream] = None
        self.is_running = False
        self.master_volume = 0.85

        # Visual Taps (Thread-safe buffers for GUI update)
        self.waveform_buffer = np.zeros(512, dtype=np.float32)
        self.peak_left = 0.0
        self.peak_right = 0.0
        self.rms_left = 0.0
        self.rms_right = 0.0

        # Audio Recording Tap callback: func(buffer: np.ndarray)
        self._record_tap: Optional[Callable[[np.ndarray], None]] = None

        # Start audio stream if requested
        if auto_start:
            self.start()

    def start(self) -> bool:
        """Start or restart the audio output stream."""
        with self._lock:
            self.stop()
            try:
                self.stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    blocksize=self.buffer_size,
                    device=self.device_index,
                    channels=2,
                    dtype='float32',
                    callback=self._audio_callback
                )
                self.stream.start()
                self.is_running = True
                print(f"[AudioEngine] Audio stream started ({self.sample_rate}Hz, buffer={self.buffer_size})")
                return True
            except Exception as e:
                print(f"[AudioEngine] Failed to start audio stream: {e}")
                self.stream = None
                self.is_running = False
                return False

    def stop(self):
        """Stop the audio stream safely."""
        with self._lock:
            if self.stream is not None:
                try:
                    self.stream.stop()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None
            self.is_running = False

    def restart_with_config(self, sample_rate: int, buffer_size: int, device_index: Optional[int] = None) -> bool:
        """Reconfigure audio engine with new sample rate, buffer size or device."""
        with self._lock:
            self.sample_rate = sample_rate
            self.buffer_size = buffer_size
            self.device_index = device_index
            self.synth.sample_rate = sample_rate
            self.synth.dsp_synth.sample_rate = sample_rate
            self.effects = EffectsChain(sample_rate=sample_rate)
            return self.start()

    def set_master_volume(self, volume: float):
        """Set master audio output volume (0.0 to 1.5)."""
        self.master_volume = max(0.0, min(1.5, volume))
        self.synth.dsp_synth.master_volume = self.master_volume

    def set_record_tap(self, callback: Optional[Callable[[np.ndarray], None]]):
        """Attach a callback to receive every output audio buffer for WAV recording."""
        with self._lock:
            self._record_tap = callback

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status):
        """Real-time sounddevice callback executing on dedicated high-priority audio thread."""
        try:
            # 1. Render raw audio buffer from DSP synth
            raw_buf = self.synth.dsp_synth.render(frames)

            # 2. Apply master effects chain (EQ -> Chorus -> Delay -> Reverb -> Limiter)
            proc_buf = self.effects.process(raw_buf)

            # 3. Apply master volume
            if abs(self.master_volume - 1.0) > 0.01:
                proc_buf *= self.master_volume

            # 4. Fill output stream
            outdata[:] = proc_buf

            # 5. Capture peak levels for UI meters
            p_l = float(np.max(np.abs(proc_buf[:, 0])))
            p_r = float(np.max(np.abs(proc_buf[:, 1])))
            self.peak_left = max(p_l, self.peak_left * 0.85)
            self.peak_right = max(p_r, self.peak_right * 0.85)

            # 6. Capture downsampled waveform for visual oscilloscope
            downsample = max(1, frames // 256)
            mono_sample = (proc_buf[::downsample, 0] + proc_buf[::downsample, 1]) * 0.5
            n_take = min(len(mono_sample), len(self.waveform_buffer))
            self.waveform_buffer = np.roll(self.waveform_buffer, -n_take)
            self.waveform_buffer[-n_take:] = mono_sample[:n_take]

            # 7. Route to audio recording tap if active
            tap = self._record_tap
            if tap is not None:
                tap(proc_buf.copy())

        except Exception as e:
            # Prevent audio callback from throwing unhandled exception
            outdata.fill(0.0)

    def panic(self):
        """Master Panic button - kills all notes immediately."""
        self.synth.panic()

    def close(self):
        """Cleanup and shutdown audio engine."""
        self.stop()
        self.synth.close()
