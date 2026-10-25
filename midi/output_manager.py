"""
KIYA Piano Studio Pro - MIDI Output Manager
Sends outgoing MIDI events to hardware or virtual MIDI devices.
"""

from typing import Optional
from audio.midi_synth import MidiSynth
from midi.midi_events import NoteEvent, ControlChangeEvent, PitchBendEvent

class MidiOutputManager:
    """High-level MIDI output router."""

    def __init__(self, midi_synth: MidiSynth):
        self.midi_synth = midi_synth

    def send_note(self, evt: NoteEvent):
        if evt.is_on:
            self.midi_synth.note_on(evt.channel, evt.note, evt.velocity)
        else:
            self.midi_synth.note_off(evt.channel, evt.note)

    def send_cc(self, evt: ControlChangeEvent):
        self.midi_synth.control_change(evt.channel, evt.control, evt.value)

    def send_pitch(self, evt: PitchBendEvent):
        self.midi_synth.pitch_bend(evt.channel, evt.pitch)
