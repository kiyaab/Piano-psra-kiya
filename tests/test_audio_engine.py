"""
KIYA Piano Studio Pro - Audio Engine & Synthesizer Tests
Tests:
- AudioEngine initialization without blocking
- SynthesizerFacade note routing and panic silence
- SplitLayerManager single, dual/layer, and split zone note dispatch
- Multi-channel volume and program change commands
"""

import pytest
from audio.engine import AudioEngine
from keyboard.split_layer import SplitLayerManager


def test_audio_engine_init():
    """Verify AudioEngine starts stream safely and exposes synthesizer."""
    engine = AudioEngine(sample_rate=44100, buffer_size=512, auto_start=False)
    assert engine.synth is not None
    assert engine.sample_rate == 44100
    assert engine.synth.is_connected


def test_synthesizer_note_flow():
    """Verify note_on, note_off, and panic across channels."""
    engine = AudioEngine(sample_rate=44100, auto_start=False)
    synth = engine.synth

    synth.set_program(0, 0)   # Grand piano
    synth.set_program(1, 48)  # Strings
    synth.set_program(2, 32)  # Bass

    # Note on
    synth.note_on(0, 60, 100)
    synth.note_on(1, 64, 90)

    # Note off
    synth.note_off(0, 60)
    synth.note_off(1, 64)

    # Panic kill
    synth.panic()


def test_split_layer_routing():
    """Verify keyboard split and layer routing logic."""
    engine = AudioEngine(sample_rate=44100, auto_start=False)
    split_mgr = SplitLayerManager(synth=engine.synth)

    # Mode 1: Single Right Voice
    split_mgr.route_note_on(60, 100)
    assert 60 in split_mgr._sounding_routes
    assert len(split_mgr._sounding_routes[60]) == 1 # Only R1
    split_mgr.route_note_off(60)
    assert 60 not in split_mgr._sounding_routes

    # Mode 2: Layer Enabled (R1 + R2)
    split_mgr.set_layer_enabled(True)
    split_mgr.route_note_on(60, 100)
    assert len(split_mgr._sounding_routes[60]) == 2 # R1 + R2
    split_mgr.route_note_off(60)

    # Mode 3: Split Enabled (split point 54 F#3)
    split_mgr.set_split_enabled(True)
    split_mgr.set_split_point(54)

    # Left hand key (Note 48 C3 <= 54)
    split_mgr.route_note_on(48, 100)
    routes = split_mgr._sounding_routes[48]
    assert len(routes) == 1
    assert routes[0][0] == 2 # Channel 2 (MIDI_CH_LEFT)
    split_mgr.route_note_off(48)

    # Right hand key (Note 60 C4 > 54)
    split_mgr.route_note_on(60, 100)
    routes_r = split_mgr._sounding_routes[60]
    assert len(routes_r) == 2 # R1 + R2
    split_mgr.route_note_off(60)
