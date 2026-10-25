"""
KIYA Piano Studio Pro - Registration Memory System
Saves and recalls complete workstation setups across 8 quick-access slots per bank (A to H).
Captures voices, layers, split points, arranger styles, tempos, mixer levels, and DSP effects.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List

@dataclass
class RegistrationSlot:
    name: str = "Empty Slot"
    is_empty: bool = True

    # Voices & Performance
    right1_voice: int = 0
    right1_volume: float = 1.0
    right1_octave: int = 0
    right1_pan: float = 0.0

    layer_enabled: bool = False
    right2_voice: int = 48
    right2_volume: float = 0.70
    right2_octave: int = 0
    right2_pan: float = 0.0

    split_enabled: bool = False
    split_point: int = 54
    left_voice: int = 32
    left_volume: float = 0.85
    left_octave: int = 0
    left_pan: float = 0.0

    transpose: int = 0

    # Arranger Style
    style_name: str = "Pop Groove"
    tempo: int = 120
    section: str = "MAIN_A"
    acmp_enabled: bool = True
    chord_mode: str = "full"

    # Mixer
    master_volume: float = 0.85
    drums_volume: float = 0.85
    bass_volume: float = 0.85
    chords_volume: float = 0.75

    # Effects
    reverb_mix: float = 0.30
    chorus_mix: float = 0.15
    delay_mix: float = 0.0

class RegistrationManager:
    """Manages 8 registration slots across Banks A through H."""

    BANKS = ["A", "B", "C", "D", "E", "F", "G", "H"]

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path("d:/PIANO GAME PY/resources/registrations")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.current_bank = "A"
        # slots[slot_index 0-7] = RegistrationSlot
        self.banks_data: Dict[str, List[RegistrationSlot]] = {
            b: [RegistrationSlot(name=f"Slot {i + 1}") for i in range(8)]
            for b in self.BANKS
        }

        self._init_factory_presets()
        self.load_bank(self.current_bank)

    def _init_factory_presets(self):
        """Populate Bank A with high-quality demonstration setups."""
        bank_a = self.banks_data["A"]

        # Slot 1: Concert Grand
        bank_a[0] = RegistrationSlot(
            name="Concert Grand", is_empty=False,
            right1_voice=0, right1_volume=1.0, right1_octave=0,
            layer_enabled=False, split_enabled=False,
            style_name="Slow Ballad", tempo=72, section="MAIN_A"
        )

        # Slot 2: Piano & Strings Layer
        bank_a[1] = RegistrationSlot(
            name="Piano & Warm Strings", is_empty=False,
            right1_voice=0, right1_volume=1.0, right1_octave=0,
            layer_enabled=True, right2_voice=48, right2_volume=0.65, right2_octave=0,
            split_enabled=False,
            style_name="Slow Ballad", tempo=68, section="MAIN_A",
            reverb_mix=0.45
        )

        # Slot 3: Jazz Trio (Upright Bass Split + Jazz Guitar Layer)
        bank_a[2] = RegistrationSlot(
            name="Jazz Trio Split", is_empty=False,
            right1_voice=26, right1_volume=0.95, right1_octave=0,
            layer_enabled=False,
            split_enabled=True, split_point=54, left_voice=32, left_volume=0.90, left_octave=0,
            style_name="Jazz Swing", tempo=144, section="MAIN_A",
            reverb_mix=0.25
        )

        # Slot 4: Bossa Nova Cafe
        bank_a[3] = RegistrationSlot(
            name="Bossa Nova Nylon", is_empty=False,
            right1_voice=24, right1_volume=1.0, right1_octave=0,
            layer_enabled=True, right2_voice=73, right2_volume=0.55, right2_octave=0, # Flute layer
            split_enabled=True, split_point=54, left_voice=33, left_volume=0.85, left_octave=0,
            style_name="Latin Bossa", tempo=128, section="MAIN_A"
        )

        # Slot 5: Classic Rock Organ
        bank_a[4] = RegistrationSlot(
            name="Rock Organ & Overdrive", is_empty=False,
            right1_voice=18, right1_volume=1.0, right1_octave=0,
            layer_enabled=True, right2_voice=29, right2_volume=0.70, right2_octave=0,
            split_enabled=False,
            style_name="Classic Rock", tempo=132, section="MAIN_A",
            chorus_mix=0.35
        )

        # Slot 6: Ethiopian Tizita
        bank_a[5] = RegistrationSlot(
            name="Ethiopian Traditional", is_empty=False,
            right1_voice=108, right1_volume=1.0, right1_octave=0, # Kalimba / Krar
            layer_enabled=True, right2_voice=16, right2_volume=0.60, right2_octave=0,
            split_enabled=True, split_point=54, left_voice=33, left_volume=0.90, left_octave=0,
            style_name="Ethiopian Tizita", tempo=105, section="MAIN_A"
        )

        # Slot 7: Rhodes & Synth Pad
        bank_a[6] = RegistrationSlot(
            name="Rhodes & Chill Pad", is_empty=False,
            right1_voice=4, right1_volume=0.95, right1_octave=0,
            layer_enabled=True, right2_voice=89, right2_volume=0.60, right2_octave=0,
            split_enabled=False,
            style_name="Pop Groove", tempo=115, section="MAIN_A",
            chorus_mix=0.25, reverb_mix=0.40
        )

        # Slot 8: Pop Anthem
        bank_a[7] = RegistrationSlot(
            name="Pop Anthem Lead", is_empty=False,
            right1_voice=81, right1_volume=0.95, right1_octave=0,
            layer_enabled=False, split_enabled=True, split_point=54, left_voice=38, left_volume=0.95, left_octave=0,
            style_name="Pop Groove", tempo=124, section="MAIN_B",
            delay_mix=0.30
        )

    def select_bank(self, bank_letter: str):
        b = bank_letter.upper()
        if b in self.BANKS:
            self.current_bank = b
            self.load_bank(b)

    def get_slot(self, slot_index: int) -> RegistrationSlot:
        idx = max(0, min(7, slot_index))
        return self.banks_data[self.current_bank][idx]

    def save_slot(self, slot_index: int, slot_data: RegistrationSlot):
        idx = max(0, min(7, slot_index))
        slot_data.is_empty = False
        self.banks_data[self.current_bank][idx] = slot_data
        self.save_bank(self.current_bank)

    def clear_slot(self, slot_index: int):
        idx = max(0, min(7, slot_index))
        self.banks_data[self.current_bank][idx] = RegistrationSlot(name=f"Slot {idx + 1}")
        self.save_bank(self.current_bank)

    def save_bank(self, bank_letter: str) -> bool:
        """Save bank slots to JSON."""
        file_path = self.storage_dir / f"bank_{bank_letter.upper()}.json"
        try:
            data = [asdict(s) for s in self.banks_data[bank_letter.upper()]]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[RegistrationManager] Error saving bank {bank_letter}: {e}")
            return False

    def load_bank(self, bank_letter: str) -> bool:
        """Load bank slots from JSON."""
        file_path = self.storage_dir / f"bank_{bank_letter.upper()}.json"
        if not file_path.exists():
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            slots = []
            for d in data[:8]:
                slots.append(RegistrationSlot(**d))
            while len(slots) < 8:
                slots.append(RegistrationSlot(name=f"Slot {len(slots) + 1}"))
            self.banks_data[bank_letter.upper()] = slots
            return True
        except Exception as e:
            print(f"[RegistrationManager] Error loading bank {bank_letter}: {e}")
            return False
