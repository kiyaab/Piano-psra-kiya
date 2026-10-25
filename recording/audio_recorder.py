"""
KIYA Piano Studio Pro - Direct WAV Audio Performance Recorder
Captures real-time output audio stream and writes broadcast-quality standard WAV files.
"""

import os
import wave
import struct
import threading
from typing import List, Optional
import numpy as np

class AudioRecorder:
    """Records master audio stream directly to standard WAV files."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.is_recording = False
        self.is_paused = False
        self._lock = threading.Lock()
        self.recorded_chunks: List[np.ndarray] = []
        self.total_frames = 0
        self.output_filepath: Optional[str] = None

    def start_recording(self, output_filepath: str):
        """Begin recording incoming audio buffers."""
        with self._lock:
            self.output_filepath = output_filepath
            self.recorded_chunks.clear()
            self.total_frames = 0
            self.is_recording = True
            self.is_paused = False
            print(f"[AudioRecorder] Recording started -> {output_filepath}")

    def pause_recording(self):
        with self._lock:
            self.is_paused = True

    def resume_recording(self):
        with self._lock:
            self.is_paused = False

    def add_audio_buffer(self, buffer: np.ndarray):
        """Called by AudioEngine stream callback with chunk [frames, 2]."""
        if not self.is_recording or self.is_paused:
            return
        with self._lock:
            self.recorded_chunks.append(buffer)
            self.total_frames += len(buffer)

    def get_elapsed_seconds(self) -> float:
        return self.total_frames / float(self.sample_rate)

    def stop_and_finalize(self) -> bool:
        """Stop recording and write standard 16-bit stereo WAV file."""
        with self._lock:
            self.is_recording = False
            self.is_paused = False

            if not self.recorded_chunks or not self.output_filepath:
                print("[AudioRecorder] Error: No audio recorded.")
                return False

            try:
                # Concatenate all chunks
                full_audio = np.concatenate(self.recorded_chunks, axis=0)

                # Clamp and convert float32 (-1.0 to +1.0) to 16-bit integer (-32767 to +32767)
                clamped = np.clip(full_audio, -1.0, 1.0)
                int16_audio = (clamped * 32767.0).astype(np.int16)

                # Ensure output directory exists
                out_dir = os.path.dirname(self.output_filepath)
                if out_dir:
                    os.makedirs(out_dir, exist_ok=True)

                # Write standard WAV file
                with wave.open(self.output_filepath, 'wb') as wf:
                    wf.setnchannels(2)      # Stereo
                    wf.setsampwidth(2)      # 16-bit (2 bytes)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(int16_audio.tobytes())

                print(f"[AudioRecorder] Successfully saved WAV file: {self.output_filepath} ({len(int16_audio)} frames)")
                return True
            except Exception as e:
                print(f"[AudioRecorder] Failed to finalize WAV file: {e}")
                return False
