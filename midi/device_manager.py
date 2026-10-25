"""
KIYA Piano Studio Pro - MIDI Device Manager
Queries available MIDI input and output ports, handles device discovery,
and provides connection status.
"""

from typing import List, Dict, Optional
import mido

class MidiDeviceManager:
    """Manages system MIDI input and output port discovery."""

    @staticmethod
    def get_input_devices() -> List[str]:
        """Return list of available MIDI input port names."""
        try:
            return mido.get_input_names()
        except Exception as e:
            print(f"[MidiDeviceManager] Error enumerating inputs: {e}")
            return []

    @staticmethod
    def get_output_devices() -> List[str]:
        """Return list of available MIDI output port names."""
        try:
            return mido.get_output_names()
        except Exception as e:
            print(f"[MidiDeviceManager] Error enumerating outputs: {e}")
            return []

    @classmethod
    def get_device_summary(cls) -> Dict[str, List[str]]:
        return {
            "inputs": cls.get_input_devices(),
            "outputs": cls.get_output_devices()
        }
