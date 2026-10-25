"""
KIYA Piano Studio Pro - Universal Arranger Style Loader & Parser
Loads, validates, and parses:
1. Structured JSON accompaniment style definitions (.json)
2. Yamaha Arranger Workstation Style files (.sty, .prs, .bcs, .sst)
3. Standard MIDI Accompaniment Files (.mid)
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import mido

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
    file_path: str = ""

class StyleLoader:
    """Manages loading, parsing, and discovery of workstation arranger styles."""

    @staticmethod
    def load_from_json(file_path: str) -> Optional[StyleDefinition]:
        """Load and parse a style JSON file."""
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            time_sig = data.get("time_signature", [4, 4])
            style = StyleDefinition(
                name=data.get("name", Path(file_path).stem.replace("_", " ").title()),
                category=data.get("category", "General"),
                tempo=data.get("tempo", 120),
                time_sig_num=time_sig[0],
                time_sig_den=time_sig[1],
                drum_program=data.get("drum_program", 0),
                bass_program=data.get("bass_program", 33),
                chord1_program=data.get("chord1_program", 4),
                chord2_program=data.get("chord2_program", 48),
                phrase_program=data.get("phrase_program", 11),
                file_path=str(file_path)
            )

            sections_data = data.get("sections", {})
            bars_data = data.get("bars_per_section", {})

            for sec_name, sec_dict in sections_data.items():
                section = StyleSection(bars=bars_data.get(sec_name, 2))

                for d in sec_dict.get("drums", []):
                    section.drums.append(PatternEvent(
                        tick=d.get("tick", 0),
                        note=d.get("note", 36),
                        vel=d.get("vel", 90),
                        duration=d.get("duration", 12)
                    ))

                for b in sec_dict.get("bass", []):
                    section.bass.append(PatternEvent(
                        tick=b.get("tick", 0),
                        note=b.get("degree", 0),
                        vel=b.get("vel", 90),
                        duration=b.get("duration", 18)
                    ))

                for c in sec_dict.get("chord1", []):
                    section.chord1.append(PatternEvent(
                        tick=c.get("tick", 0),
                        degrees=c.get("degrees", [0, 4, 7]),
                        vel=c.get("vel", 85),
                        duration=c.get("duration", 24)
                    ))

                for c in sec_dict.get("chord2", []):
                    section.chord2.append(PatternEvent(
                        tick=c.get("tick", 0),
                        degrees=c.get("degrees", [0, 7]),
                        vel=c.get("vel", 75),
                        duration=c.get("duration", 24)
                    ))

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
            print(f"[StyleLoader] Error loading JSON style '{file_path}': {e}")
            return None

    @staticmethod
    def load_from_sty(file_path: str) -> Optional[StyleDefinition]:
        """
        Parse Yamaha .STY / .PRS / .BCS / .SST or Standard MIDI (.MID) file.
        Extracts tempo, time signature, markers (Intro, Main A-D, Fill, Ending),
        and maps channels:
          Ch 9 (0-indexed) -> Drums
          Ch 10 -> Bass
          Ch 11-13 -> Chord 1 & Chord 2
          Ch 14-15 -> Phrase
        """
        if not os.path.exists(file_path):
            return None
        try:
            mid = mido.MidiFile(file_path, clip=True)
            ticks_per_beat = mid.ticks_per_beat or 480
            scale_to_24 = 24.0 / float(ticks_per_beat)

            tempo_bpm = 120
            ts_num = 4
            ts_den = 4
            name = Path(file_path).stem.replace("_", " ").title()

            # Pass 1: Extract meta events (tempo, time signature, track names, markers)
            markers: List[tuple] = [] # (abs_tick, marker_text)

            # Flatten messages with absolute ticks
            track_events = []
            for track in mid.tracks:
                abs_t = 0
                for msg in track:
                    abs_t += msg.time
                    if msg.type == 'set_tempo':
                        tempo_bpm = int(round(mido.tempo2bpm(msg.tempo)))
                    elif msg.type == 'time_signature':
                        ts_num = msg.numerator
                        ts_den = msg.denominator
                    elif msg.type in ('marker', 'text'):
                        txt = str(msg.text).strip()
                        if txt:
                            markers.append((abs_t, txt))
                    elif msg.type == 'track_name' and not name:
                        name = str(msg.name).strip()
                    track_events.append((abs_t, msg))

            # Sort markers and events by tick
            markers.sort(key=lambda x: x[0])
            track_events.sort(key=lambda x: x[0])

            # Section marker normalizer
            def normalize_marker(txt: str) -> Optional[str]:
                t = txt.lower().replace(" ", "").replace("_", "").replace("-", "")
                if "maina" in t or "var1" in t or "sectiona" in t:
                    return "MAIN_A"
                elif "mainb" in t or "var2" in t or "sectionb" in t:
                    return "MAIN_B"
                elif "mainc" in t or "var3" in t or "sectionc" in t:
                    return "MAIN_C"
                elif "maind" in t or "var4" in t or "sectiond" in t:
                    return "MAIN_D"
                elif "intro" in t:
                    return "INTRO"
                elif "ending" in t:
                    return "ENDING"
                elif "break" in t:
                    return "BREAK"
                elif "filla" in t or "fillin1" in t:
                    return "FILL_AA"
                elif "fillb" in t or "fillin2" in t:
                    return "FILL_BB"
                elif "fillc" in t:
                    return "FILL_CC"
                elif "filld" in t:
                    return "FILL_DD"
                return None

            # Map section boundaries
            sec_ranges: List[tuple] = [] # (sec_name, start_tick, end_tick)
            valid_markers = [(tick, normalize_marker(txt)) for tick, txt in markers if normalize_marker(txt)]

            if valid_markers:
                for i, (start_t, sec_name) in enumerate(valid_markers):
                    end_t = valid_markers[i + 1][0] if (i + 1) < len(valid_markers) else (start_t + ticks_per_beat * ts_num * 2)
                    sec_ranges.append((sec_name, start_t, end_t))
            else:
                # Slicing fallback: create Main A-D, Intro, Ending from bars
                bar_ticks = ticks_per_beat * ts_num
                sec_ranges = [
                    ("MAIN_A", 0, bar_ticks * 2),
                    ("MAIN_B", bar_ticks * 2, bar_ticks * 4),
                    ("MAIN_C", bar_ticks * 4, bar_ticks * 6),
                    ("MAIN_D", bar_ticks * 6, bar_ticks * 8),
                    ("INTRO", bar_ticks * 8, bar_ticks * 10),
                    ("ENDING", bar_ticks * 10, bar_ticks * 12),
                    ("BREAK", bar_ticks * 12, bar_ticks * 13)
                ]

            sections_dict: Dict[str, StyleSection] = {}

            # Build each section from events in its range
            for sec_name, start_t, end_t in sec_ranges:
                sec_length_ticks = max(ticks_per_beat * ts_num, end_t - start_t)
                bars = max(1, int(round(sec_length_ticks / (ticks_per_beat * ts_num))))
                total_engine_ticks = bars * ts_num * 24

                section = StyleSection(bars=bars)

                # Filter note events in range
                for abs_t, msg in track_events:
                    if abs_t < start_t or abs_t >= end_t:
                        continue
                    if msg.type != 'note_on' or msg.velocity == 0:
                        continue

                    # Tick relative to section start, wrapped to section length
                    rel_tick = int(round((abs_t - start_t) * scale_to_24)) % total_engine_ticks
                    vel = msg.velocity
                    ch = getattr(msg, 'channel', 0)
                    note = msg.note

                    if ch == 9:  # Drums
                        section.drums.append(PatternEvent(tick=rel_tick, note=note, vel=vel, duration=12))
                    elif ch == 10:  # Bass
                        deg = (note - 36) % 12
                        section.bass.append(PatternEvent(tick=rel_tick, note=deg, vel=vel, duration=18))
                    elif ch in (11, 12):  # Chord 1
                        deg = (note - 60) % 12
                        section.chord1.append(PatternEvent(tick=rel_tick, degrees=[deg, (deg + 4) % 12, (deg + 7) % 12], vel=vel, duration=24))
                    elif ch == 13:  # Chord 2
                        deg = (note - 60) % 12
                        section.chord2.append(PatternEvent(tick=rel_tick, degrees=[deg, (deg + 7) % 12], vel=vel, duration=24))
                    else:  # Phrases
                        deg = (note - 60) % 12
                        section.phrase.append(PatternEvent(tick=rel_tick, note=deg, vel=vel, duration=12))

                # Deduplicate and sort events by tick
                for cat in (section.drums, section.bass, section.chord1, section.chord2, section.phrase):
                    cat.sort(key=lambda e: e.tick)

                sections_dict[sec_name] = section

            # Ensure basic sections exist even if sparse
            if "MAIN_A" not in sections_dict and sections_dict:
                first_k = list(sections_dict.keys())[0]
                sections_dict["MAIN_A"] = sections_dict[first_k]

            style = StyleDefinition(
                name=name or "Imported Yamaha Style",
                category="User Styles",
                tempo=tempo_bpm,
                time_sig_num=ts_num,
                time_sig_den=ts_den,
                drum_program=0,
                bass_program=33,
                chord1_program=4,
                chord2_program=48,
                phrase_program=11,
                sections=sections_dict,
                file_path=str(file_path)
            )
            return style

        except Exception as e:
            print(f"[StyleLoader] Error loading Yamaha STY file '{file_path}': {e}")
            return None

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional[StyleDefinition]:
        """Universal loader: auto-detects .json or .sty/.prs/.bcs/.sst/.mid."""
        p = Path(file_path)
        ext = p.suffix.lower()
        if ext == ".json":
            return cls.load_from_json(file_path)
        elif ext in (".sty", ".prs", ".bcs", ".sst", ".mid", ".midi"):
            return cls.load_from_sty(file_path)
        else:
            # Try JSON first, fallback to STY
            res = cls.load_from_json(file_path)
            if res:
                return res
            return cls.load_from_sty(file_path)

    @classmethod
    def load_all_styles(cls, directory: str) -> List[StyleDefinition]:
        """Scan directory for all valid styles (.json, .sty, .prs, .bcs, .sst, .mid)."""
        styles = []
        dir_path = Path(directory)
        if not dir_path.exists():
            return styles

        valid_exts = {".json", ".sty", ".prs", ".bcs", ".sst", ".mid", ".midi"}
        for f in sorted(dir_path.iterdir()):
            if f.suffix.lower() in valid_exts:
                style = cls.load_from_file(str(f))
                if style:
                    styles.append(style)
        return styles
