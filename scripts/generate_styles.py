"""
Script to generate the 6 rich demonstration style definitions for KIYA Piano Studio Pro.
Creates:
1. Pop Groove
2. Slow Ballad
3. Classic Rock
4. Jazz Swing
5. Latin Bossa Nova
6. Ethiopian Tizita
"""

import json
from pathlib import Path

def generate():
    out_dir = Path("d:/PIANO GAME PY/resources/styles")
    out_dir.mkdir(parents=True, exist_ok=True)

    PPQ = 24  # 24 ticks per beat (4/4 bar = 96 ticks)

    # -------------------------------------------------------------
    # 1. POP GROOVE (120 BPM, 4/4)
    # -------------------------------------------------------------
    # 2-bar pattern = 192 ticks. Beats at 0, 24, 48, 72, 96, 120, 144, 168
    pop_drums_main_a = []
    # Kicks on beats 1 and 3 (0, 48, 96, 144) + offbeat kick at 84, 180
    for bar_start in [0, 96]:
        pop_drums_main_a.extend([
            {"tick": bar_start + 0, "note": 36, "vel": 105, "duration": 12},
            {"tick": bar_start + 48, "note": 36, "vel": 100, "duration": 12},
            {"tick": bar_start + 84, "note": 36, "vel": 85, "duration": 12},
        ])
        # Snares on beats 2 and 4 (24, 72)
        pop_drums_main_a.extend([
            {"tick": bar_start + 24, "note": 38, "vel": 100, "duration": 12},
            {"tick": bar_start + 72, "note": 38, "vel": 105, "duration": 12},
        ])
        # Closed Hi-Hats on every 8th note (0, 12, 24, 36, 48, 60, 72, 84)
        for t in range(0, 96, 12):
            vel = 95 if (t % 24 == 0) else 75
            pop_drums_main_a.append({"tick": bar_start + t, "note": 42, "vel": vel, "duration": 8})

    # Pop Bass (Root on 1, 8ve on offbeat, 5th on 3)
    pop_bass_main_a = []
    for bar_start in [0, 96]:
        pop_bass_main_a.extend([
            {"tick": bar_start + 0, "degree": 0, "vel": 95, "duration": 18},
            {"tick": bar_start + 24, "degree": 0, "vel": 80, "duration": 12},
            {"tick": bar_start + 48, "degree": 7, "vel": 90, "duration": 18},
            {"tick": bar_start + 72, "degree": 12, "vel": 85, "duration": 12},
            {"tick": bar_start + 84, "degree": 10, "vel": 80, "duration": 10},
        ])

    # Pop Chords: Synced rhythmic comping on offbeats
    pop_chord1_main_a = []
    for bar_start in [0, 96]:
        pop_chord1_main_a.extend([
            {"tick": bar_start + 12, "degrees": [0, 4, 7], "vel": 80, "duration": 12},
            {"tick": bar_start + 36, "degrees": [0, 4, 7], "vel": 85, "duration": 12},
            {"tick": bar_start + 60, "degrees": [0, 4, 7], "vel": 80, "duration": 12},
            {"tick": bar_start + 84, "degrees": [0, 4, 7], "vel": 85, "duration": 10},
        ])

    # Pop Fill AA (1 bar = 96 ticks): Tom roll + snare buildup + crash
    pop_drums_fill_aa = [
        {"tick": 0, "note": 36, "vel": 100, "duration": 12},
        {"tick": 24, "note": 38, "vel": 95, "duration": 12},
        {"tick": 48, "note": 48, "vel": 95, "duration": 12}, # Hi-Mid Tom
        {"tick": 60, "note": 47, "vel": 95, "duration": 12}, # Low-Mid Tom
        {"tick": 72, "note": 45, "vel": 100, "duration": 10}, # Low Tom
        {"tick": 84, "note": 40, "vel": 110, "duration": 10}, # Snare flam
    ]

    pop_style = {
        "name": "Pop Groove",
        "category": "Pop",
        "tempo": 120,
        "time_signature": [4, 4],
        "drum_program": 0,
        "bass_program": 33,    # Finger Bass
        "chord1_program": 4,   # Rhodes
        "chord2_program": 48,  # Strings
        "phrase_program": 81,  # Lead Saw
        "bars_per_section": {
            "INTRO": 2, "MAIN_A": 2, "MAIN_B": 2, "MAIN_C": 2, "MAIN_D": 2,
            "FILL_AA": 1, "FILL_BB": 1, "FILL_CC": 1, "FILL_DD": 1,
            "BREAK": 1, "ENDING": 2
        },
        "sections": {
            "MAIN_A": {
                "drums": pop_drums_main_a,
                "bass": pop_bass_main_a,
                "chord1": pop_chord1_main_a,
                "chord2": [{"tick": 0, "degrees": [0, 7, 12], "vel": 65, "duration": 90}],
                "phrase": []
            },
            "MAIN_B": {
                "drums": pop_drums_main_a + [{"tick": 0, "note": 49, "vel": 90, "duration": 24}], # Add crash
                "bass": pop_bass_main_a,
                "chord1": pop_chord1_main_a,
                "chord2": [{"tick": 0, "degrees": [0, 4, 7, 11], "vel": 75, "duration": 90}],
                "phrase": [{"tick": 48, "degree": 12, "vel": 75, "duration": 20}]
            },
            "MAIN_C": {
                "drums": pop_drums_main_a,
                "bass": pop_bass_main_a,
                "chord1": pop_chord1_main_a,
                "chord2": [{"tick": 0, "degrees": [0, 7, 12], "vel": 80, "duration": 90}],
                "phrase": []
            },
            "MAIN_D": {
                "drums": pop_drums_main_a,
                "bass": pop_bass_main_a,
                "chord1": pop_chord1_main_a,
                "chord2": [{"tick": 0, "degrees": [0, 4, 7], "vel": 85, "duration": 90}],
                "phrase": []
            },
            "FILL_AA": {
                "drums": pop_drums_fill_aa,
                "bass": [{"tick": 0, "degree": 0, "vel": 90, "duration": 48}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 7], "vel": 80, "duration": 48}],
                "chord2": [], "phrase": []
            },
            "FILL_BB": {
                "drums": pop_drums_fill_aa,
                "bass": [{"tick": 0, "degree": 0, "vel": 90, "duration": 48}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 7], "vel": 80, "duration": 48}],
                "chord2": [], "phrase": []
            },
            "FILL_CC": {
                "drums": pop_drums_fill_aa,
                "bass": [{"tick": 0, "degree": 0, "vel": 90, "duration": 48}],
                "chord1": [], "chord2": [], "phrase": []
            },
            "FILL_DD": {
                "drums": pop_drums_fill_aa,
                "bass": [{"tick": 0, "degree": 0, "vel": 90, "duration": 48}],
                "chord1": [], "chord2": [], "phrase": []
            },
            "BREAK": {
                "drums": [{"tick": 0, "note": 49, "vel": 110, "duration": 24}, {"tick": 0, "note": 36, "vel": 110, "duration": 24}],
                "bass": [{"tick": 0, "degree": 0, "vel": 100, "duration": 24}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 7], "vel": 90, "duration": 24}],
                "chord2": [], "phrase": []
            },
            "INTRO": {
                "drums": pop_drums_main_a,
                "bass": pop_bass_main_a,
                "chord1": pop_chord1_main_a,
                "chord2": [{"tick": 0, "degrees": [0, 4, 7], "vel": 75, "duration": 90}],
                "phrase": [{"tick": 0, "degree": 12, "vel": 85, "duration": 24}]
            },
            "ENDING": {
                "drums": [
                    {"tick": 0, "note": 36, "vel": 100, "duration": 12},
                    {"tick": 24, "note": 38, "vel": 100, "duration": 12},
                    {"tick": 48, "note": 49, "vel": 115, "duration": 48},
                    {"tick": 48, "note": 36, "vel": 115, "duration": 48}
                ],
                "bass": [
                    {"tick": 0, "degree": 7, "vel": 95, "duration": 24},
                    {"tick": 48, "degree": 0, "vel": 110, "duration": 48}
                ],
                "chord1": [
                    {"tick": 0, "degrees": [2, 5, 7], "vel": 85, "duration": 24},
                    {"tick": 48, "degrees": [0, 4, 7, 12], "vel": 100, "duration": 48}
                ],
                "chord2": [], "phrase": []
            }
        }
    }
    with open(out_dir / "pop_groove.json", "w", encoding="utf-8") as f:
        json.dump(pop_style, f, indent=2)

    # -------------------------------------------------------------
    # 2. SLOW BALLAD (68 BPM, 4/4)
    # -------------------------------------------------------------
    ballad_drums = []
    for bar_start in [0, 96]:
        # Subtle kick on 1 and offbeat of 2
        ballad_drums.extend([
            {"tick": bar_start + 0, "note": 36, "vel": 85, "duration": 18},
            {"tick": bar_start + 36, "note": 36, "vel": 70, "duration": 12},
            {"tick": bar_start + 48, "note": 37, "vel": 90, "duration": 12}, # Side stick on 3
            {"tick": bar_start + 84, "note": 36, "vel": 70, "duration": 10},
        ])
        # 16th-note warm hi-hat
        for t in range(0, 96, 6):
            vel = 80 if (t % 24 == 0) else 55
            ballad_drums.append({"tick": bar_start + t, "note": 42, "vel": vel, "duration": 4})

    ballad_bass = []
    for bar_start in [0, 96]:
        ballad_bass.extend([
            {"tick": bar_start + 0, "degree": 0, "vel": 85, "duration": 36},
            {"tick": bar_start + 48, "degree": 7, "vel": 80, "duration": 24},
            {"tick": bar_start + 72, "degree": 5, "vel": 75, "duration": 20},
        ])

    ballad_chord1 = []
    for bar_start in [0, 96]:
        # Arpeggiated grand piano chords
        ballad_chord1.extend([
            {"tick": bar_start + 0, "degrees": [0, 7], "vel": 75, "duration": 20},
            {"tick": bar_start + 12, "degrees": [4], "vel": 70, "duration": 12},
            {"tick": bar_start + 24, "degrees": [7], "vel": 72, "duration": 12},
            {"tick": bar_start + 36, "degrees": [12], "vel": 75, "duration": 12},
            {"tick": bar_start + 48, "degrees": [0, 4, 7], "vel": 78, "duration": 30},
            {"tick": bar_start + 72, "degrees": [4, 7, 11], "vel": 74, "duration": 20},
        ])

    ballad_style = {
        "name": "Slow Ballad",
        "category": "Ballad",
        "tempo": 68,
        "time_signature": [4, 4],
        "drum_program": 0,
        "bass_program": 32,    # Acoustic Bass
        "chord1_program": 0,   # Acoustic Grand Piano
        "chord2_program": 89,  # Warm Pad
        "phrase_program": 73,  # Flute
        "bars_per_section": {
            "INTRO": 2, "MAIN_A": 2, "MAIN_B": 2, "MAIN_C": 2, "MAIN_D": 2,
            "FILL_AA": 1, "FILL_BB": 1, "FILL_CC": 1, "FILL_DD": 1,
            "BREAK": 1, "ENDING": 2
        },
        "sections": {
            "MAIN_A": {
                "drums": ballad_drums,
                "bass": ballad_bass,
                "chord1": ballad_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 4, 7], "vel": 65, "duration": 180}],
                "phrase": []
            },
            "MAIN_B": {
                "drums": ballad_drums,
                "bass": ballad_bass,
                "chord1": ballad_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 7, 12], "vel": 75, "duration": 180}],
                "phrase": [{"tick": 48, "degree": 7, "vel": 70, "duration": 24}]
            },
            "MAIN_C": {
                "drums": ballad_drums, "bass": ballad_bass, "chord1": ballad_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 4, 7], "vel": 75, "duration": 180}], "phrase": []
            },
            "MAIN_D": {
                "drums": ballad_drums, "bass": ballad_bass, "chord1": ballad_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 4, 7], "vel": 80, "duration": 180}], "phrase": []
            },
            "FILL_AA": {
                "drums": [
                    {"tick": 0, "note": 36, "vel": 80, "duration": 12},
                    {"tick": 48, "note": 38, "vel": 85, "duration": 12},
                    {"tick": 72, "note": 42, "vel": 90, "duration": 12}
                ],
                "bass": [{"tick": 0, "degree": 0, "vel": 80, "duration": 48}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 7], "vel": 75, "duration": 48}],
                "chord2": [], "phrase": []
            },
            "FILL_BB": {
                "drums": [{"tick": 48, "note": 38, "vel": 85, "duration": 12}],
                "bass": [], "chord1": [], "chord2": [], "phrase": []
            },
            "FILL_CC": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_DD": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "BREAK": {
                "drums": [{"tick": 0, "note": 36, "vel": 90, "duration": 24}],
                "bass": [{"tick": 0, "degree": 0, "vel": 85, "duration": 24}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 7], "vel": 80, "duration": 48}],
                "chord2": [], "phrase": []
            },
            "INTRO": {
                "drums": ballad_drums, "bass": ballad_bass, "chord1": ballad_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 4, 7], "vel": 70, "duration": 180}], "phrase": []
            },
            "ENDING": {
                "drums": [{"tick": 0, "note": 36, "vel": 90, "duration": 24}, {"tick": 48, "note": 49, "vel": 95, "duration": 48}],
                "bass": [{"tick": 0, "degree": 0, "vel": 90, "duration": 48}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 7, 12], "vel": 85, "duration": 48}],
                "chord2": [], "phrase": []
            }
        }
    }
    with open(out_dir / "slow_ballad.json", "w", encoding="utf-8") as f:
        json.dump(ballad_style, f, indent=2)

    # -------------------------------------------------------------
    # 3. CLASSIC ROCK (132 BPM, 4/4)
    # -------------------------------------------------------------
    rock_drums = []
    for bar_start in [0, 96]:
        # Driving 4-on-the-floor + rock backbeat
        rock_drums.extend([
            {"tick": bar_start + 0, "note": 36, "vel": 115, "duration": 12},
            {"tick": bar_start + 24, "note": 38, "vel": 115, "duration": 12}, # Snare
            {"tick": bar_start + 48, "note": 36, "vel": 115, "duration": 12},
            {"tick": bar_start + 60, "note": 36, "vel": 95, "duration": 12},
            {"tick": bar_start + 72, "note": 38, "vel": 120, "duration": 12}, # Snare
        ])
        # Open / half-open hats
        for t in range(0, 96, 12):
            rock_drums.append({"tick": bar_start + t, "note": 46 if (t % 24 != 0) else 42, "vel": 95, "duration": 10})

    rock_bass = []
    for bar_start in [0, 96]:
        # Driving 8th-note pick bassline (0, 0, 7, 7, 10, 10, 12, 10)
        degrees = [0, 0, 0, 0, 7, 7, 10, 12]
        for idx, deg in enumerate(degrees):
            rock_bass.append({"tick": bar_start + idx * 12, "degree": deg, "vel": 100, "duration": 10})

    rock_chord1 = []
    for bar_start in [0, 96]:
        # Power chord strikes
        rock_chord1.extend([
            {"tick": bar_start + 0, "degrees": [0, 7, 12], "vel": 105, "duration": 18},
            {"tick": bar_start + 24, "degrees": [0, 7, 12], "vel": 95, "duration": 12},
            {"tick": bar_start + 48, "degrees": [0, 7, 12], "vel": 105, "duration": 18},
            {"tick": bar_start + 72, "degrees": [0, 7, 12], "vel": 100, "duration": 12},
        ])

    rock_style = {
        "name": "Classic Rock",
        "category": "Rock",
        "tempo": 132,
        "time_signature": [4, 4],
        "drum_program": 0,
        "bass_program": 34,    # Pick Bass
        "chord1_program": 29,  # Overdriven Guitar
        "chord2_program": 18,  # Rock Organ
        "phrase_program": 30,  # Distortion Guitar
        "bars_per_section": {
            "INTRO": 2, "MAIN_A": 2, "MAIN_B": 2, "MAIN_C": 2, "MAIN_D": 2,
            "FILL_AA": 1, "FILL_BB": 1, "FILL_CC": 1, "FILL_DD": 1,
            "BREAK": 1, "ENDING": 2
        },
        "sections": {
            "MAIN_A": {
                "drums": rock_drums, "bass": rock_bass, "chord1": rock_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 7], "vel": 85, "duration": 90}], "phrase": []
            },
            "MAIN_B": {
                "drums": rock_drums + [{"tick": 0, "note": 49, "vel": 115, "duration": 24}],
                "bass": rock_bass, "chord1": rock_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 7], "vel": 95, "duration": 90}], "phrase": []
            },
            "MAIN_C": {"drums": rock_drums, "bass": rock_bass, "chord1": rock_chord1, "chord2": [], "phrase": []},
            "MAIN_D": {"drums": rock_drums, "bass": rock_bass, "chord1": rock_chord1, "chord2": [], "phrase": []},
            "FILL_AA": {
                "drums": [
                    {"tick": 0, "note": 38, "vel": 105, "duration": 10},
                    {"tick": 24, "note": 48, "vel": 105, "duration": 10},
                    {"tick": 48, "note": 45, "vel": 110, "duration": 10},
                    {"tick": 72, "note": 41, "vel": 115, "duration": 10},
                ],
                "bass": [{"tick": 0, "degree": 0, "vel": 105, "duration": 48}],
                "chord1": [{"tick": 0, "degrees": [0, 7], "vel": 105, "duration": 48}],
                "chord2": [], "phrase": []
            },
            "FILL_BB": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_CC": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_DD": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "BREAK": {
                "drums": [{"tick": 0, "note": 49, "vel": 120, "duration": 24}],
                "bass": [{"tick": 0, "degree": 0, "vel": 110, "duration": 24}],
                "chord1": [{"tick": 0, "degrees": [0, 7], "vel": 110, "duration": 24}],
                "chord2": [], "phrase": []
            },
            "INTRO": {
                "drums": rock_drums, "bass": rock_bass, "chord1": rock_chord1, "chord2": [], "phrase": []
            },
            "ENDING": {
                "drums": [
                    {"tick": 0, "note": 36, "vel": 115, "duration": 12},
                    {"tick": 24, "note": 38, "vel": 115, "duration": 12},
                    {"tick": 48, "note": 49, "vel": 125, "duration": 48}
                ],
                "bass": [{"tick": 48, "degree": 0, "vel": 120, "duration": 48}],
                "chord1": [{"tick": 48, "degrees": [0, 7, 12], "vel": 120, "duration": 48}],
                "chord2": [], "phrase": []
            }
        }
    }
    with open(out_dir / "classic_rock.json", "w", encoding="utf-8") as f:
        json.dump(rock_style, f, indent=2)

    # -------------------------------------------------------------
    # 4. JAZZ SWING (144 BPM, 4/4)
    # -------------------------------------------------------------
    jazz_drums = []
    for bar_start in [0, 96]:
        # Feathered soft kick on 1, 2, 3, 4
        for b in range(0, 96, 24):
            jazz_drums.append({"tick": bar_start + b, "note": 35, "vel": 60, "duration": 8})
        # Pedal Hat on 2 and 4 (24, 72)
        jazz_drums.extend([
            {"tick": bar_start + 24, "note": 44, "vel": 95, "duration": 8},
            {"tick": bar_start + 72, "note": 44, "vel": 95, "duration": 8},
        ])
        # Swing Ride pattern: ding, ding-a-ding (0, 24, 40, 48, 72, 88)
        jazz_drums.extend([
            {"tick": bar_start + 0, "note": 51, "vel": 90, "duration": 12},
            {"tick": bar_start + 24, "note": 51, "vel": 95, "duration": 12},
            {"tick": bar_start + 40, "note": 51, "vel": 80, "duration": 8},
            {"tick": bar_start + 48, "note": 51, "vel": 90, "duration": 12},
            {"tick": bar_start + 72, "note": 51, "vel": 95, "duration": 12},
            {"tick": bar_start + 88, "note": 51, "vel": 80, "duration": 8},
        ])

    # Walking Jazz Bass (4 beats per bar: Root, 3rd, 5th, Chromatic approach)
    jazz_bass = []
    for bar_start in [0, 96]:
        jazz_bass.extend([
            {"tick": bar_start + 0, "degree": 0, "vel": 88, "duration": 22},
            {"tick": bar_start + 24, "degree": 4, "vel": 85, "duration": 22},
            {"tick": bar_start + 48, "degree": 7, "vel": 88, "duration": 22},
            {"tick": bar_start + 72, "degree": 6, "vel": 82, "duration": 20}, # Chromatic walk
        ])

    # Jazz Guitar Chords (Freddie Green / Charleston comping: beat 1, offbeat of 2)
    jazz_chord1 = []
    for bar_start in [0, 96]:
        jazz_chord1.extend([
            {"tick": bar_start + 0, "degrees": [0, 4, 10], "vel": 82, "duration": 16},
            {"tick": bar_start + 40, "degrees": [0, 4, 10], "vel": 85, "duration": 16},
            {"tick": bar_start + 64, "degrees": [0, 4, 10], "vel": 80, "duration": 16},
        ])

    jazz_style = {
        "name": "Jazz Swing",
        "category": "Jazz",
        "tempo": 144,
        "time_signature": [4, 4],
        "drum_program": 0,
        "bass_program": 32,    # Acoustic Upright Bass
        "chord1_program": 26,  # Jazz Electric Guitar
        "chord2_program": 0,   # Acoustic Piano
        "phrase_program": 66,  # Tenor Sax
        "bars_per_section": {
            "INTRO": 2, "MAIN_A": 2, "MAIN_B": 2, "MAIN_C": 2, "MAIN_D": 2,
            "FILL_AA": 1, "FILL_BB": 1, "FILL_CC": 1, "FILL_DD": 1,
            "BREAK": 1, "ENDING": 2
        },
        "sections": {
            "MAIN_A": {
                "drums": jazz_drums, "bass": jazz_bass, "chord1": jazz_chord1,
                "chord2": [{"tick": 0, "degrees": [4, 10, 14], "vel": 70, "duration": 40}], "phrase": []
            },
            "MAIN_B": {
                "drums": jazz_drums, "bass": jazz_bass, "chord1": jazz_chord1,
                "chord2": [{"tick": 0, "degrees": [4, 10, 14], "vel": 75, "duration": 40}],
                "phrase": [{"tick": 48, "degree": 14, "vel": 75, "duration": 20}]
            },
            "MAIN_C": {"drums": jazz_drums, "bass": jazz_bass, "chord1": jazz_chord1, "chord2": [], "phrase": []},
            "MAIN_D": {"drums": jazz_drums, "bass": jazz_bass, "chord1": jazz_chord1, "chord2": [], "phrase": []},
            "FILL_AA": {
                "drums": [
                    {"tick": 0, "note": 38, "vel": 85, "duration": 10},
                    {"tick": 48, "note": 40, "vel": 90, "duration": 10},
                    {"tick": 72, "note": 51, "vel": 95, "duration": 12}
                ],
                "bass": [{"tick": 0, "degree": 0, "vel": 85, "duration": 48}],
                "chord1": [], "chord2": [], "phrase": []
            },
            "FILL_BB": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_CC": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_DD": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "BREAK": {
                "drums": [{"tick": 0, "note": 51, "vel": 100, "duration": 24}],
                "bass": [{"tick": 0, "degree": 0, "vel": 90, "duration": 24}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 10], "vel": 85, "duration": 24}],
                "chord2": [], "phrase": []
            },
            "INTRO": {
                "drums": jazz_drums, "bass": jazz_bass, "chord1": jazz_chord1, "chord2": [], "phrase": []
            },
            "ENDING": {
                "drums": [{"tick": 48, "note": 51, "vel": 100, "duration": 48}],
                "bass": [{"tick": 48, "degree": 0, "vel": 100, "duration": 48}],
                "chord1": [{"tick": 48, "degrees": [0, 4, 7, 11, 14], "vel": 95, "duration": 48}],
                "chord2": [], "phrase": []
            }
        }
    }
    with open(out_dir / "jazz_swing.json", "w", encoding="utf-8") as f:
        json.dump(jazz_style, f, indent=2)

    # -------------------------------------------------------------
    # 5. LATIN BOSSA (128 BPM, 4/4)
    # -------------------------------------------------------------
    bossa_drums = []
    for bar_start in [0, 96]:
        # Bossa Nova Clave / Cross stick: 1, and of 2, 4, and of 4
        bossa_drums.extend([
            {"tick": bar_start + 0, "note": 37, "vel": 90, "duration": 10},
            {"tick": bar_start + 36, "note": 37, "vel": 85, "duration": 10},
            {"tick": bar_start + 72, "note": 37, "vel": 90, "duration": 10},
        ])
        # Soft bass drum on 1 and 3
        bossa_drums.extend([
            {"tick": bar_start + 0, "note": 35, "vel": 75, "duration": 12},
            {"tick": bar_start + 48, "note": 35, "vel": 75, "duration": 12},
        ])
        # Continuous shaker/closed hi-hat 8th notes
        for t in range(0, 96, 12):
            bossa_drums.append({"tick": bar_start + t, "note": 70, "vel": 75 if t % 24 == 0 else 60, "duration": 8})

    # Bossa Bass (Dotted quarter root, followed by 5th)
    bossa_bass = []
    for bar_start in [0, 96]:
        bossa_bass.extend([
            {"tick": bar_start + 0, "degree": 0, "vel": 85, "duration": 30},
            {"tick": bar_start + 36, "degree": 0, "vel": 80, "duration": 10},
            {"tick": bar_start + 48, "degree": 7, "vel": 85, "duration": 30},
            {"tick": bar_start + 84, "degree": 7, "vel": 78, "duration": 10},
        ])

    # Nylon Guitar syncopated chord comping
    bossa_chord1 = []
    for bar_start in [0, 96]:
        bossa_chord1.extend([
            {"tick": bar_start + 0, "degrees": [0, 4, 7, 11], "vel": 80, "duration": 20},
            {"tick": bar_start + 36, "degrees": [0, 4, 7, 11], "vel": 82, "duration": 16},
            {"tick": bar_start + 60, "degrees": [0, 4, 7, 11], "vel": 78, "duration": 16},
            {"tick": bar_start + 84, "degrees": [0, 4, 7, 11], "vel": 80, "duration": 10},
        ])

    bossa_style = {
        "name": "Latin Bossa",
        "category": "Latin",
        "tempo": 128,
        "time_signature": [4, 4],
        "drum_program": 0,
        "bass_program": 33,    # Finger Bass
        "chord1_program": 24,  # Acoustic Nylon Guitar
        "chord2_program": 73,  # Flute
        "phrase_program": 11,  # Vibraphone
        "bars_per_section": {
            "INTRO": 2, "MAIN_A": 2, "MAIN_B": 2, "MAIN_C": 2, "MAIN_D": 2,
            "FILL_AA": 1, "FILL_BB": 1, "FILL_CC": 1, "FILL_DD": 1,
            "BREAK": 1, "ENDING": 2
        },
        "sections": {
            "MAIN_A": {
                "drums": bossa_drums, "bass": bossa_bass, "chord1": bossa_chord1,
                "chord2": [{"tick": 0, "degrees": [4, 7, 11], "vel": 65, "duration": 90}], "phrase": []
            },
            "MAIN_B": {
                "drums": bossa_drums, "bass": bossa_bass, "chord1": bossa_chord1,
                "chord2": [{"tick": 0, "degrees": [4, 7, 11], "vel": 75, "duration": 90}],
                "phrase": [{"tick": 48, "degree": 11, "vel": 70, "duration": 20}]
            },
            "MAIN_C": {"drums": bossa_drums, "bass": bossa_bass, "chord1": bossa_chord1, "chord2": [], "phrase": []},
            "MAIN_D": {"drums": bossa_drums, "bass": bossa_bass, "chord1": bossa_chord1, "chord2": [], "phrase": []},
            "FILL_AA": {
                "drums": [
                    {"tick": 0, "note": 63, "vel": 85, "duration": 12},  # Conga
                    {"tick": 48, "note": 64, "vel": 90, "duration": 12},
                    {"tick": 72, "note": 55, "vel": 95, "duration": 12}
                ],
                "bass": [{"tick": 0, "degree": 0, "vel": 85, "duration": 48}],
                "chord1": [], "chord2": [], "phrase": []
            },
            "FILL_BB": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_CC": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_DD": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "BREAK": {
                "drums": [{"tick": 0, "note": 37, "vel": 95, "duration": 24}],
                "bass": [{"tick": 0, "degree": 0, "vel": 85, "duration": 24}],
                "chord1": [{"tick": 0, "degrees": [0, 4, 7, 11], "vel": 80, "duration": 24}],
                "chord2": [], "phrase": []
            },
            "INTRO": {
                "drums": bossa_drums, "bass": bossa_bass, "chord1": bossa_chord1, "chord2": [], "phrase": []
            },
            "ENDING": {
                "drums": [{"tick": 48, "note": 49, "vel": 95, "duration": 48}],
                "bass": [{"tick": 48, "degree": 0, "vel": 95, "duration": 48}],
                "chord1": [{"tick": 48, "degrees": [0, 4, 7, 11], "vel": 90, "duration": 48}],
                "chord2": [], "phrase": []
            }
        }
    }
    with open(out_dir / "latin_bossa.json", "w", encoding="utf-8") as f:
        json.dump(bossa_style, f, indent=2)

    # -------------------------------------------------------------
    # 6. ETHIOPIAN TIZITA (105 BPM, 6/8 meter feel in 4/4 syncopation)
    # -------------------------------------------------------------
    ethio_drums = []
    # Kebero inspired rhythm: deep resonant thumb hit on 1, sharp slap on 3 and 4 offbeat
    for bar_start in [0, 96]:
        ethio_drums.extend([
            {"tick": bar_start + 0, "note": 36, "vel": 100, "duration": 18}, # Deep bass Kebero
            {"tick": bar_start + 32, "note": 63, "vel": 90, "duration": 12}, # High rim slap
            {"tick": bar_start + 48, "note": 36, "vel": 85, "duration": 14},
            {"tick": bar_start + 64, "note": 64, "vel": 95, "duration": 12}, # Open slap
            {"tick": bar_start + 80, "note": 63, "vel": 88, "duration": 10},
        ])
        # Tambourine / Shaker triplets
        for t in range(0, 96, 16):
            ethio_drums.append({"tick": bar_start + t, "note": 54, "vel": 75 if t % 32 == 0 else 60, "duration": 8})

    # Pentatonic modal bassline (Tizita Minor / Major scale degrees: 0, 3, 5, 7, 10)
    ethio_bass = []
    for bar_start in [0, 96]:
        ethio_bass.extend([
            {"tick": bar_start + 0, "degree": 0, "vel": 95, "duration": 28},
            {"tick": bar_start + 32, "degree": 3, "vel": 85, "duration": 14},
            {"tick": bar_start + 48, "degree": 7, "vel": 90, "duration": 28},
            {"tick": bar_start + 80, "degree": 5, "vel": 85, "duration": 14},
        ])

    # Krar / Rhodes style modal comping
    ethio_chord1 = []
    for bar_start in [0, 96]:
        ethio_chord1.extend([
            {"tick": bar_start + 16, "degrees": [0, 3, 7], "vel": 85, "duration": 14},
            {"tick": bar_start + 48, "degrees": [0, 7, 10], "vel": 82, "duration": 14},
            {"tick": bar_start + 64, "degrees": [0, 3, 7], "vel": 88, "duration": 14},
            {"tick": bar_start + 80, "degrees": [3, 7, 12], "vel": 80, "duration": 14},
        ])

    ethio_style = {
        "name": "Ethiopian Tizita",
        "category": "World",
        "tempo": 105,
        "time_signature": [4, 4],
        "drum_program": 0,
        "bass_program": 33,    # Finger Bass
        "chord1_program": 108, # Kalimba / Krar
        "chord2_program": 16,  # Drawbar Organ
        "phrase_program": 71,  # Clarinet / Washint
        "bars_per_section": {
            "INTRO": 2, "MAIN_A": 2, "MAIN_B": 2, "MAIN_C": 2, "MAIN_D": 2,
            "FILL_AA": 1, "FILL_BB": 1, "FILL_CC": 1, "FILL_DD": 1,
            "BREAK": 1, "ENDING": 2
        },
        "sections": {
            "MAIN_A": {
                "drums": ethio_drums, "bass": ethio_bass, "chord1": ethio_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 7], "vel": 70, "duration": 90}], "phrase": []
            },
            "MAIN_B": {
                "drums": ethio_drums, "bass": ethio_bass, "chord1": ethio_chord1,
                "chord2": [{"tick": 0, "degrees": [0, 7], "vel": 80, "duration": 90}],
                "phrase": [{"tick": 48, "degree": 10, "vel": 80, "duration": 20}]
            },
            "MAIN_C": {"drums": ethio_drums, "bass": ethio_bass, "chord1": ethio_chord1, "chord2": [], "phrase": []},
            "MAIN_D": {"drums": ethio_drums, "bass": ethio_bass, "chord1": ethio_chord1, "chord2": [], "phrase": []},
            "FILL_AA": {
                "drums": [
                    {"tick": 0, "note": 63, "vel": 95, "duration": 12},
                    {"tick": 24, "note": 64, "vel": 95, "duration": 12},
                    {"tick": 48, "note": 36, "vel": 105, "duration": 24}
                ],
                "bass": [{"tick": 0, "degree": 0, "vel": 90, "duration": 48}],
                "chord1": [], "chord2": [], "phrase": []
            },
            "FILL_BB": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_CC": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "FILL_DD": {"drums": [], "bass": [], "chord1": [], "chord2": [], "phrase": []},
            "BREAK": {
                "drums": [{"tick": 0, "note": 36, "vel": 105, "duration": 24}],
                "bass": [{"tick": 0, "degree": 0, "vel": 95, "duration": 24}],
                "chord1": [{"tick": 0, "degrees": [0, 3, 7], "vel": 85, "duration": 24}],
                "chord2": [], "phrase": []
            },
            "INTRO": {
                "drums": ethio_drums, "bass": ethio_bass, "chord1": ethio_chord1, "chord2": [], "phrase": []
            },
            "ENDING": {
                "drums": [{"tick": 48, "note": 36, "vel": 110, "duration": 48}],
                "bass": [{"tick": 48, "degree": 0, "vel": 110, "duration": 48}],
                "chord1": [{"tick": 48, "degrees": [0, 3, 7, 10], "vel": 100, "duration": 48}],
                "chord2": [], "phrase": []
            }
        }
    }
    with open(out_dir / "ethiopian_tizita.json", "w", encoding="utf-8") as f:
        json.dump(ethio_style, f, indent=2)

    print("All 6 style definitions successfully generated!")

if __name__ == "__main__":
    generate()
