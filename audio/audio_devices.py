"""
KIYA Piano Studio Pro - Audio Device Enumeration & Configuration
Handles sounddevice device queries, latency calculation, and audio testing.
"""

from typing import List, Dict, Any, Optional, Tuple
import sounddevice as sd
import numpy as np

class AudioDeviceManager:
    """Manages audio host APIs, output devices, and latency estimation."""

    @staticmethod
    def get_output_devices() -> List[Dict[str, Any]]:
        """List all available audio output devices."""
        devices = []
        try:
            device_list = sd.query_devices()
            hostapis = sd.query_hostapis()
            default_out = sd.default.device[1]

            for idx, dev in enumerate(device_list):
                if dev.get('max_output_channels', 0) > 0:
                    api_name = hostapis[dev['hostapi']]['name'] if dev['hostapi'] < len(hostapis) else ""
                    devices.append({
                        'index': idx,
                        'name': f"{dev['name']} ({api_name})",
                        'raw_name': dev['name'],
                        'hostapi': api_name,
                        'channels': dev['max_output_channels'],
                        'default_sample_rate': int(dev['default_samplerate']),
                        'low_latency': dev.get('default_low_output_latency', 0.0),
                        'high_latency': dev.get('default_high_output_latency', 0.0),
                        'is_default': (idx == default_out)
                    })
        except Exception as e:
            print(f"[AudioDeviceManager] Error querying devices: {e}")
        return devices

    @staticmethod
    def play_test_tone(device_index: Optional[int] = None, sample_rate: int = 44100, duration: float = 0.4) -> bool:
        """Play a smooth test note (C4 261.63Hz) to verify audio output path."""
        try:
            n_frames = int(sample_rate * duration)
            t = np.linspace(0.0, duration, n_frames, False, dtype=np.float32)
            # Smooth attack and decay envelope
            env = np.sin(np.pi * (t / duration)) ** 1.5
            freq = 261.63  # Middle C
            signal = (0.25 * env * np.sin(2.0 * np.pi * freq * t)).astype(np.float32)
            # Stereo
            stereo = np.column_stack([signal, signal])
            sd.play(stereo, samplerate=sample_rate, device=device_index)
            return True
        except Exception as e:
            print(f"[AudioDeviceManager] Test tone failed: {e}")
            return False

    @staticmethod
    def estimate_latency_ms(buffer_size: int, sample_rate: int, device_index: Optional[int] = None) -> float:
        """Calculate estimated audio output latency in milliseconds."""
        buffer_ms = (buffer_size / float(sample_rate)) * 1000.0
        try:
            dev_info = sd.query_devices(device_index if device_index is not None else sd.default.device[1])
            driver_latency_ms = dev_info.get('default_low_output_latency', 0.01) * 1000.0
            return round(buffer_ms + driver_latency_ms, 1)
        except Exception:
            return round(buffer_ms + 10.0, 1)
