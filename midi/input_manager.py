"""
KIYA Piano Studio Pro - MIDI Input Manager
Listens for incoming MIDI events on a background thread and routes them
to the application note bus without blocking the GUI.
"""

import threading
from typing import Optional, Callable, List
import mido
from midi.midi_events import NoteEvent, ControlChangeEvent, PitchBendEvent, ProgramChangeEvent

class MidiInputManager:
    """Thread-safe background listener for connected MIDI keyboards."""

    def __init__(self, port_name: Optional[str] = None):
        self._lock = threading.Lock()
        self.port: Optional[mido.ports.BaseInput] = None
        self.port_name: str = ""
        self.is_connected = False
        self._stop_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_note_event: Optional[Callable[[NoteEvent], None]] = None
        self.on_cc_event: Optional[Callable[[ControlChangeEvent], None]] = None
        self.on_pitch_event: Optional[Callable[[PitchBendEvent], None]] = None
        self.on_program_event: Optional[Callable[[ProgramChangeEvent], None]] = None

        if port_name:
            self.open_port(port_name)

    def open_port(self, port_name: str) -> bool:
        """Connect to the specified MIDI input port."""
        with self._lock:
            self.close()
            available = mido.get_input_names()
            if port_name not in available:
                print(f"[MidiInputManager] Input port '{port_name}' not available.")
                return False

            try:
                self.port = mido.open_input(port_name)
                self.port_name = port_name
                self.is_connected = True
                self._stop_flag.clear()
                self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="MidiInputListener")
                self._thread.start()
                print(f"[MidiInputManager] Connected to MIDI input: '{port_name}'")
                return True
            except Exception as e:
                print(f"[MidiInputManager] Failed to open input port '{port_name}': {e}")
                self.port = None
                self.is_connected = False
                return False

    def close(self):
        """Disconnect and stop listener thread."""
        self._stop_flag.set()
        with self._lock:
            if self.port is not None:
                try:
                    self.port.close()
                except Exception:
                    pass
                self.port = None
            self.is_connected = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        self._thread = None

    def _listen_loop(self):
        """Background thread reading MIDI messages from port."""
        while not self._stop_flag.is_set():
            if not self.port or self.port.closed:
                break
            try:
                # iter_pending returns immediately without blocking indefinitely
                for msg in self.port.iter_pending():
                    self._dispatch_message(msg)
                self._stop_flag.wait(0.002)  # 2ms sleep to prevent high CPU in polling
            except Exception as e:
                print(f"[MidiInputManager] Error in listener loop: {e}")
                break
        self.is_connected = False

    def _dispatch_message(self, msg: mido.Message):
        """Dispatch message to registered callbacks."""
        if msg.type == 'note_on':
            if msg.velocity > 0:
                evt = NoteEvent(channel=msg.channel, note=msg.note, velocity=msg.velocity, is_on=True, timestamp=msg.time)
            else:
                evt = NoteEvent(channel=msg.channel, note=msg.note, velocity=0, is_on=False, timestamp=msg.time)
            if self.on_note_event:
                self.on_note_event(evt)
        elif msg.type == 'note_off':
            evt = NoteEvent(channel=msg.channel, note=msg.note, velocity=0, is_on=False, timestamp=msg.time)
            if self.on_note_event:
                self.on_note_event(evt)
        elif msg.type == 'control_change':
            evt = ControlChangeEvent(channel=msg.channel, control=msg.control, value=msg.value, timestamp=msg.time)
            if self.on_cc_event:
                self.on_cc_event(evt)
        elif msg.type == 'pitchwheel':
            evt = PitchBendEvent(channel=msg.channel, pitch=msg.pitch, timestamp=msg.time)
            if self.on_pitch_event:
                self.on_pitch_event(evt)
        elif msg.type == 'program_change':
            evt = ProgramChangeEvent(channel=msg.channel, program=msg.program, timestamp=msg.time)
            if self.on_program_event:
                self.on_program_event(evt)
