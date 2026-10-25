"""
KIYA Piano Studio Pro - Arranger Style Loader & Model
Loads, validates, and parses structured JSON accompaniment style definitions.
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class PatternEvent:
    tick: int          # Tick within section (0 to section_total_ticks - 1)
    note: int = 0      # Fixed MIDI note (for drums) or base degree offset
    degrees: List[int] = field(default_factory=list) # Relative scale degrees for chords
    vel: int = 90      # Velocity (1-127)
    duration: int = 12 # Duration in ticks

@dataclass
class StyleSection:
    bars: int = 2
    drums: List[PatternEvent] = field(default_factory=list)
    bass: List[PatternEvent] = field(default_factory=list)
    chord1: List[PatternEvent] = field(default_factory=list)
    chord2: List[PatternEvent] = field(default_factory=list)
    phrase: List[PatternEvent] = field(default_factory=list)

@dataclass
class StyleDefinition:
    name: str
    category: str
    tempo: int = 120
    time_sig_num: int = 4
    time_sig_den: int = 4
    drum_program: int = 0
    bass_program: int = 33     # Finger Bass
    chord1_program: int = 4    # E.Piano 1
    chord2_program: int = 48   # Strings
    phrase_program: int = 11   # Vibraphone
    sections: Dict[str, StyleSection] = field(default_factory=dict)

class StyleLoader:
    """Manages loading and discovery of workstation arranger styles."""

    @staticmethod
    def load_from_file(file_path: str) -> Optional[StyleDefinition]:
        """Load and parse a style JSON file."""
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            time_sig = data.get("time_signature", [4, 4])
            style = StyleDefinition(
                name=data.get("name", "Unnamed Style"),
                category=data.get("category", "General"),
                tempo=data.get("tempo", 120),
                time_sig_num=time_sig[0],
                time_sig_den=time_sig[1],
                drum_program=data.get("drum_program", 0),
                bass_program=data.get("bass_program", 33),
                chord1_program=data.get("chord1_program", 4),
                chord2_program=data.get("chord2_program", 48),
                phrase_program=data.get("phrase_program", 11)
            )

            sections_data = data.get("sections", {})
            bars_data = data.get("bars_per_section", {})

            for sec_name, sec_dict in sections_data.items():
                section = StyleSection(bars=bars_data.get(sec_name, 2))

                # Parse drum events
                for d in sec_dict.get("drums", []):
                    section.drums.append(PatternEvent(
                        tick=d.get("tick", 0),
                        note=d.get("note", 36),
                        vel=d.get("vel", 90),
                        duration=d.get("duration", 12)
                    ))

                # Parse bass events
                for b in sec_dict.get("bass", []):
                    section.bass.append(PatternEvent(
                        tick=b.get("tick", 0),
                        note=b.get("degree", 0),
                        vel=b.get("vel", 90),
                        duration=b.get("duration", 18)
                    ))

                # Parse chord1 events
                for c in sec_dict.get("chord1", []):
                    section.chord1.append(PatternEvent(
                        tick=c.get("tick", 0),
                        degrees=c.get("degrees", [0, 4, 7]),
                        vel=c.get("vel", 85),
                        duration=c.get("duration", 24)
                    ))

                # Parse chord2 events
                for c in sec_dict.get("chord2", []):
                    section.chord2.append(PatternEvent(
                        tick=c.get("tick", 0),
                        degrees=c.get("degrees", [0, 7]),
                        vel=c.get("vel", 75),
                        duration=c.get("duration", 24)
                    ))

                # Parse phrase events
                for p in sec_dict.get("phrase", []):
                    section.phrase.append(PatternEvent(
                        tick=p.get("tick", 0),
                        note=p.get("degree", 0),
                        vel=p.get("vel", 80),
                        duration=p.get("duration", 12)
                    ))

                style.sections[sec_name] = section

            return style
        except Exception as e:
            print(f"[StyleLoader] Error loading style '{file_path}': {e}")
            return None

    @classmethod
    def load_all_styles(cls, directory: str) -> List[StyleDefinition]:
        """Scan directory for .json style definitions."""
        styles = []
        dir_path = Path(directory)
        if not dir_path.exists():
            return styles

        for json_file in sorted(dir_path.glob("*.json")):
            style = cls.load_from_file(str(json_file))
            if style:
                styles.append(style)
        return styles
