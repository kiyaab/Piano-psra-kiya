"""
KIYA Piano Studio Pro - Application Constants and Sound Specifications
"""

APP_NAME = "KIYA Piano Studio Pro"
APP_SUBTITLE = "Professional Arranger Workstation"
APP_VERSION = "1.0.0"
ORGANIZATION_NAME = "KIYA Sound Systems"

# Visual Theme Constants (Professional Dark Graphite palette)
COLOR_BG = "#101216"
COLOR_PANEL_MAIN = "#191D24"
COLOR_PANEL_SECONDARY = "#222833"
COLOR_PANEL_ELEVATED = "#2A3240"
COLOR_BORDER = "#2E3646"
COLOR_BORDER_LIGHT = "#3D485C"

COLOR_ACCENT_ORANGE = "#FF8A24"
COLOR_ACCENT_ORANGE_HOVER = "#FFA34D"
COLOR_ACCENT_BLUE = "#54B8FF"
COLOR_ACCENT_BLUE_HOVER = "#75C6FF"

COLOR_TEXT_PRIMARY = "#F4F6FA"
COLOR_TEXT_SECONDARY = "#A6AFBE"
COLOR_TEXT_MUTED = "#6B778D"

COLOR_SUCCESS = "#57D995"
COLOR_WARNING = "#FFC83B"
COLOR_ERROR = "#FF626B"

# Keyboard Specifications
KEYBOARD_MIN_NOTE = 36  # C2
KEYBOARD_MAX_NOTE = 96  # C7 (61 keys total: 36 to 96 inclusive = 61 keys)
DEFAULT_SPLIT_POINT = 54  # F#3
DEFAULT_VELOCITY = 100

# Audio Engine Defaults
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_BUFFER_SIZE = 512
SUPPORTED_SAMPLE_RATES = [22050, 44100, 48000, 88200, 96000]
SUPPORTED_BUFFER_SIZES = [128, 256, 512, 1024, 2048]

# MIDI Channels Assignment
MIDI_CH_RIGHT1 = 0     # Channel 1: Right Hand Main Voice
MIDI_CH_RIGHT2 = 1     # Channel 2: Right Hand Layer Voice
MIDI_CH_LEFT = 2       # Channel 3: Left Hand Split Voice
MIDI_CH_STYLE_BASS = 8 # Channel 9: Style Bass
MIDI_CH_STYLE_DRUMS = 9# Channel 10: Style Drums / Percussion
MIDI_CH_STYLE_CHORD1 = 10 # Channel 11: Style Chord 1
MIDI_CH_STYLE_CHORD2 = 11 # Channel 12: Style Chord 2
MIDI_CH_STYLE_PHRASE = 12 # Channel 13: Style Pad/Phrase

# Arranger Accompaniment Sections
SECTION_INTRO = "INTRO"
SECTION_MAIN_A = "MAIN_A"
SECTION_MAIN_B = "MAIN_B"
SECTION_MAIN_C = "MAIN_C"
SECTION_MAIN_D = "MAIN_D"
SECTION_FILL_AA = "FILL_AA"
SECTION_FILL_BB = "FILL_BB"
SECTION_FILL_CC = "FILL_CC"
SECTION_FILL_DD = "FILL_DD"
SECTION_BREAK = "BREAK"
SECTION_ENDING = "ENDING"

# General MIDI Instrument Categories & Programs (0-indexed)
GM_CATEGORIES = {
    "Piano": [
        (0, "Acoustic Grand Piano"),
        (1, "Bright Acoustic Piano"),
        (2, "Electric Grand Piano"),
        (3, "Honky-Tonk Piano"),
        (4, "Electric Piano 1 (Rhodes)"),
        (5, "Electric Piano 2 (DX7)"),
        (6, "Harpsichord"),
        (7, "Clavinet"),
    ],
    "Chromatic Percussion": [
        (8, "Celesta"),
        (9, "Glockenspiel"),
        (10, "Music Box"),
        (11, "Vibraphone"),
        (12, "Marimba"),
        (13, "Xylophone"),
        (14, "Tubular Bells"),
        (15, "Dulcimer"),
    ],
    "Organ": [
        (16, "Drawbar Organ (Hammond)"),
        (17, "Percussive Organ"),
        (18, "Rock Organ"),
        (19, "Church Organ"),
        (20, "Reed Organ"),
        (21, "Accordion"),
        (22, "Harmonica"),
        (23, "Tango Accordion"),
    ],
    "Guitar": [
        (24, "Acoustic Guitar (Nylon)"),
        (25, "Acoustic Guitar (Steel)"),
        (26, "Electric Guitar (Jazz)"),
        (27, "Electric Guitar (Clean)"),
        (28, "Electric Guitar (Muted)"),
        (29, "Overdriven Guitar"),
        (30, "Distortion Guitar"),
        (31, "Guitar Harmonics"),
    ],
    "Bass": [
        (32, "Acoustic Bass"),
        (33, "Electric Bass (Finger)"),
        (34, "Electric Bass (Pick)"),
        (35, "Fretless Bass"),
        (36, "Slap Bass 1"),
        (37, "Slap Bass 2"),
        (38, "Synth Bass 1"),
        (39, "Synth Bass 2"),
    ],
    "Strings": [
        (40, "Violin"),
        (41, "Viola"),
        (42, "Cello"),
        (43, "Contrabass"),
        (44, "Tremolo Strings"),
        (45, "Pizzicato Strings"),
        (46, "Orchestral Harp"),
        (47, "Timpani"),
    ],
    "Ensemble & Choir": [
        (48, "String Ensemble 1"),
        (49, "String Ensemble 2"),
        (50, "Synth Strings 1"),
        (51, "Synth Strings 2"),
        (52, "Choir Aahs"),
        (53, "Voice Oohs"),
        (54, "Synth Voice"),
        (55, "Orchestra Hit"),
    ],
    "Brass": [
        (56, "Trumpet"),
        (57, "Trombone"),
        (58, "Tuba"),
        (59, "Muted Trumpet"),
        (60, "French Horn"),
        (61, "Brass Section"),
        (62, "Synth Brass 1"),
        (63, "Synth Brass 2"),
    ],
    "Reed & Woodwinds": [
        (64, "Soprano Sax"),
        (65, "Alto Sax"),
        (66, "Tenor Sax"),
        (67, "Baritone Sax"),
        (68, "Oboe"),
        (69, "English Horn"),
        (70, "Bassoon"),
        (71, "Clarinet"),
        (72, "Piccolo"),
        (73, "Flute"),
        (74, "Recorder"),
        (75, "Pan Flute"),
        (76, "Blown Bottle"),
        (77, "Shakuhachi"),
        (78, "Whistle"),
        (79, "Ocarina"),
    ],
    "Synth Lead": [
        (80, "Lead 1 (Square)"),
        (81, "Lead 2 (Sawtooth)"),
        (82, "Lead 3 (Calliope)"),
        (83, "Lead 4 (Chiff)"),
        (84, "Lead 5 (Charang)"),
        (85, "Lead 6 (Voice)"),
        (86, "Lead 7 (Fifths)"),
        (87, "Lead 8 (Bass + Lead)"),
    ],
    "Synth Pad": [
        (88, "Pad 1 (New Age)"),
        (89, "Pad 2 (Warm)"),
        (90, "Pad 3 (Polysynth)"),
        (91, "Pad 4 (Choir)"),
        (92, "Pad 5 (Bowed)"),
        (93, "Pad 6 (Metallic)"),
        (94, "Pad 7 (Halo)"),
        (95, "Pad 8 (Sweep)"),
    ],
    "World & Ethnic": [
        (104, "Sitar"),
        (105, "Banjo"),
        (106, "Shamisen"),
        (107, "Koto"),
        (108, "Kalimba"),
        (109, "Bagpipe"),
        (110, "Fiddle"),
        (111, "Shanai"),
    ],
    "Sound Effects & Perc": [
        (112, "Tinkle Bell"),
        (113, "Agogo"),
        (114, "Steel Drums"),
        (115, "Woodblock"),
        (116, "Taiko Drum"),
        (117, "Melodic Tom"),
        (118, "Synth Drum"),
        (119, "Reverse Cymbal"),
        (120, "Guitar Fret Noise"),
        (121, "Breath Noise"),
        (122, "Seashore"),
        (123, "Bird Tweet"),
        (124, "Telephone Ring"),
        (125, "Helicopter"),
        (126, "Applause"),
        (127, "Gunshot"),
    ]
}

# Standard General MIDI Drum Key Numbers (Channel 10)
DRUM_BASS_DRUM_2 = 35
DRUM_BASS_DRUM_1 = 36
DRUM_SIDE_STICK = 37
DRUM_ACOUSTIC_SNARE = 38
DRUM_HAND_CLAP = 39
DRUM_ELECTRIC_SNARE = 40
DRUM_LOW_FLOOR_TOM = 41
DRUM_CLOSED_HI_HAT = 42
DRUM_HIGH_FLOOR_TOM = 43
DRUM_PEDAL_HI_HAT = 44
DRUM_LOW_TOM = 45
DRUM_OPEN_HI_HAT = 46
DRUM_LOW_MID_TOM = 47
DRUM_HI_MID_TOM = 48
DRUM_CRASH_CYMBAL_1 = 49
DRUM_HIGH_TOM = 50
DRUM_RIDE_CYMBAL_1 = 51
DRUM_CHINESE_CYMBAL = 52
DRUM_RIDE_BELL = 53
DRUM_TAMBOURINE = 54
DRUM_SPLASH_CYMBAL = 55
DRUM_COWBELL = 56
DRUM_CRASH_CYMBAL_2 = 57
DRUM_VIBRA_SLAP = 58
DRUM_RIDE_CYMBAL_2 = 59
DRUM_HI_BONGO = 60
DRUM_LOW_BONGO = 61
DRUM_MUTE_HI_CONGA = 62
DRUM_OPEN_HI_CONGA = 63
DRUM_LOW_CONGA = 64
DRUM_HIGH_TIMBALE = 65
DRUM_LOW_TIMBALE = 66
DRUM_HIGH_AGOGO = 67
DRUM_LOW_AGOGO = 68
DRUM_CABASA = 69
DRUM_MARACAS = 70
DRUM_SHORT_WHISTLE = 71
DRUM_LONG_WHISTLE = 72
DRUM_SHORT_GUIRO = 73
DRUM_LONG_GUIRO = 74
DRUM_CLAVES = 75
DRUM_HI_WOOD_BLOCK = 76
DRUM_LOW_WOOD_BLOCK = 77
DRUM_MUTE_CUICA = 78
DRUM_OPEN_CUICA = 79
DRUM_MUTE_TRIANGLE = 80
DRUM_OPEN_TRIANGLE = 81
DRUM_SHAKER = 82

# Pitch mapping helper
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

def midi_to_note_name(note_number: int, use_flats: bool = False) -> str:
    """Convert MIDI note number (0-127) to note name with octave e.g. 60 -> 'C4'."""
    octave = (note_number // 12) - 1
    pitch = note_number % 12
    name = NOTE_FLAT_NAMES[pitch] if use_flats else NOTE_NAMES[pitch]
    return f"{name}{octave}"

def note_name_to_midi(name_str: str) -> int:
    """Convert note string like 'C4' or 'F#3' or 'Bb5' to MIDI note number."""
    name_str = name_str.strip()
    if not name_str:
        return 60
    if len(name_str) >= 2 and name_str[1] in ("#", "b"):
        key = name_str[:2]
        octave_str = name_str[2:]
    else:
        key = name_str[:1]
        octave_str = name_str[1:]
    
    pitch = -1
    for i, n in enumerate(NOTE_NAMES):
        if n.upper() == key.upper():
            pitch = i
            break
    if pitch == -1:
        for i, n in enumerate(NOTE_FLAT_NAMES):
            if n.upper() == key.upper():
                pitch = i
                break
    if pitch == -1:
        return 60
    try:
        octave = int(octave_str)
    except ValueError:
        octave = 4
    return (octave + 1) * 12 + pitch
