"""
KIYA Piano Studio Pro - Arranger & Accompaniment Tests
Tests:
- Built-in style definitions loading
- MusicalClock precision and tempo changes
- Chord detection from active keys (Major, Minor, 7th)
- Accompaniment sections (Intro, Main A-D, Fills, Ending)
"""

import pytest
from audio.engine import AudioEngine
from arranger.accompaniment import AccompanimentCoordinator
from arranger.chord_detector import ChordDetector


def test_styles_loaded():
    """Verify built-in Yamaha-style accompaniment patterns are discovered."""
    engine = AudioEngine(sample_rate=44100, auto_start=False)
    arranger = AccompanimentCoordinator(synth=engine.synth)
    assert len(arranger.available_styles) >= 1
    style_names = [s.name for s in arranger.available_styles]
    print("Discovered styles:", style_names)


def test_chord_detector():
    """Verify real-time chord detection logic."""
    detector = ChordDetector()

    # C Major: C4 (60), E4 (64), G4 (67)
    c_maj = detector.detect_from_notes([60, 64, 67])
    assert c_maj is not None
    assert c_maj.root_name == "C"
    assert "Maj" in c_maj.quality or c_maj.quality == ""

    # A Minor: A3 (57), C4 (60), E4 (64)
    a_min = detector.detect_from_notes([57, 60, 64])
    assert a_min is not None
    assert a_min.root_name == "A"
    assert "m" in a_min.quality


def test_arranger_sections_and_tempo():
    """Verify tempo setting and section triggers."""
    engine = AudioEngine(sample_rate=44100, auto_start=False)
    arranger = AccompanimentCoordinator(synth=engine.synth)

    arranger.set_tempo(135)
    assert arranger.tempo == 135

    arranger.set_variation("C")
    assert arranger.style_engine.current_section_name == "MAIN_C"

    arranger.trigger_intro()
    assert "INTRO" in arranger.style_engine.current_section_name

    # Test accompaniment toggle (acmp on/off)
    arranger.set_accompaniment_enabled(False)
    assert not arranger.acmp_enabled
    arranger.set_accompaniment_enabled(True)
    assert arranger.acmp_enabled

    # Test selecting styles by name
    assert arranger.select_style_by_name("Pop Groove")
    assert arranger.current_style_name == "Pop Groove"
    assert arranger.select_style_by_name("Slow Ballad")
    assert arranger.current_style_name == "Slow Ballad"

    arranger.stop_playback()
    assert not arranger.is_playing
