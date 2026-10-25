"""
KIYA Piano Studio Pro - Windows Native & Hardware MIDI Synthesizer
Directly drives Windows 'Microsoft GS Wavetable Synth' or external MIDI interfaces
using pygame.midi (instant zero-latency Windows MM) with mido fallback.
"""

import threading
from typing import List, Optional

try:
    import pygame.midi
    _HAS_PYGAME_MIDI = True
except ImportError:
    _HAS_PYGAME_MIDI = False

try:
    import mido
    _HAS_MIDO = True
except ImportError:
    _HAS_MIDO = False

class MidiSynth:
    """Hardware and native Windows MIDI synthesizer engine."""

    def __init__(self, port_name: Optional[str] = None):
        self._lock = threading.RLock()
        self.port_name: str = ""
        self.is_connected = False

        # Backends
        self._pg_output = None
        self._mido_port = None

        self.open_port(port_name)

    @staticmethod
    def get_available_ports() -> List[str]:
        """Return list of available system MIDI output ports."""
        ports = []
        if _HAS_PYGAME_MIDI:
            try:
                if not pygame.midi.get_init():
                    pygame.midi.init()
                count = pygame.midi.get_count()
                for i in range(count):
                    info = pygame.midi.get_device_info(i)
                    if info and info[3] == 1:  # is_output
                        dev_name = info[1].decode("utf-8", errors="ignore") if isinstance(info[1], bytes) else str(info[1])
                        ports.append(f"{dev_name} [{i}]")
                if ports:
                    return ports
            except Exception as e:
                print(f"[MidiSynth] pygame.midi get ports warning: {e}")

        if _HAS_MIDO:
            try:
                return mido.get_output_names()
            except Exception as e:
                print(f"[MidiSynth] mido get ports warning: {e}")
        return ports

    def open_port(self, port_name: Optional[str] = None) -> bool:
        """Open a MIDI output port safely."""
        with self._lock:
            self.close()

            # Priority 1: pygame.midi (instantaneous, lowest latency on Windows)
            if _HAS_PYGAME_MIDI:
                try:
                    if not pygame.midi.get_init():
                        pygame.midi.init()
                    count = pygame.midi.get_count()
                    chosen_id = None
                    chosen_name = ""

                    # Search for desired or Microsoft GS Wavetable
                    for i in range(count):
                        info = pygame.midi.get_device_info(i)
                        if info and info[3] == 1:  # is_output
                            dev_name = info[1].decode("utf-8", errors="ignore") if isinstance(info[1], bytes) else str(info[1])
                            if port_name and (port_name in dev_name or str(i) in port_name):
                                chosen_id = i
                                chosen_name = dev_name
                                break
                            elif not chosen_id and ("GS Wavetable" in dev_name or "Wavetable" in dev_name):
                                chosen_id = i
                                chosen_name = dev_name

                    if chosen_id is None:
                        chosen_id = pygame.midi.get_default_output_id()
                        if chosen_id != -1 and chosen_id is not None:
                            info = pygame.midi.get_device_info(chosen_id)
                            chosen_name = info[1].decode("utf-8", errors="ignore") if (info and isinstance(info[1], bytes)) else "Default MIDI"

                    if chosen_id is not None and chosen_id != -1:
                        self._pg_output = pygame.midi.Output(chosen_id)
                        self.port_name = f"{chosen_name} (pygame.midi)"
                        self.is_connected = True
                        print(f"[MidiSynth] Connected via pygame.midi: '{self.port_name}'")
                        return True
                except Exception as e:
                    print(f"[MidiSynth] Failed to open pygame.midi port: {e}")
                    self._pg_output = None

            # Priority 2: mido fallback
            if _HAS_MIDO:
                try:
                    available = mido.get_output_names()
                    if available:
                        chosen = None
                        if port_name and port_name in available:
                            chosen = port_name
                        else:
                            for p in available:
                                if "GS Wavetable" in p or "Wavetable" in p:
                                    chosen = p
                                    break
                            if not chosen:
                                chosen = available[0]

                        self._mido_port = mido.open_output(chosen)
                        self.port_name = f"{chosen} (mido)"
                        self.is_connected = True
                        print(f"[MidiSynth] Connected via mido: '{chosen}'")
                        return True
                except Exception as e:
                    print(f"[MidiSynth] Failed to open mido port: {e}")
                    self._mido_port = None

            self.is_connected = False
            return False

    def close(self):
        """Close current MIDI output port."""
        if self._pg_output is not None:
            try:
                self.panic()
                del self._pg_output
            except Exception:
                pass
            self._pg_output = None

        if self._mido_port is not None:
            try:
                self.panic()
                self._mido_port.close()
            except Exception:
                pass
            self._mido_port = None

        self.is_connected = False

    def program_change(self, channel: int, program: int):
        """Change instrument patch on specified channel (0-15, program 0-127)."""
        if not self.is_connected:
            return
        channel = max(0, min(15, channel))
        program = max(0, min(127, program))

        with self._lock:
            if self._pg_output:
                try:
                    self._pg_output.set_instrument(program, channel=channel)
                except Exception:
                    pass
            elif self._mido_port:
                try:
                    self._mido_port.send(mido.Message('program_change', channel=channel, program=program))
                except Exception:
                    pass

    def note_on(self, channel: int, note: int, velocity: int):
        """Trigger note on."""
        if not self.is_connected:
            return
        channel = max(0, min(15, channel))
        note = max(0, min(127, note))
        velocity = max(0, min(127, velocity))

        with self._lock:
            if self._pg_output:
                try:
                    self._pg_output.note_on(note, velocity, channel=channel)
                except Exception:
                    pass
            elif self._mido_port:
                try:
                    self._mido_port.send(mido.Message('note_on', channel=channel, note=note, velocity=velocity))
                except Exception:
                    pass

    def note_off(self, channel: int, note: int):
        """Trigger note off."""
        if not self.is_connected:
            return
        channel = max(0, min(15, channel))
        note = max(0, min(127, note))

        with self._lock:
            if self._pg_output:
                try:
                    self._pg_output.note_off(note, 0, channel=channel)
                except Exception:
                    pass
            elif self._mido_port:
                try:
                    self._mido_port.send(mido.Message('note_off', channel=channel, note=note, velocity=0))
                except Exception:
                    pass

    def control_change(self, channel: int, control: int, value: int):
        """Send CC message (e.g. Volume 7, Pan 10, Sustain 64, Reverb 91, Chorus 93)."""
        if not self.is_connected:
            return
        channel = max(0, min(15, channel))
        control = max(0, min(127, control))
        value = max(0, min(127, value))

        with self._lock:
            if self._pg_output:
                try:
                    status = 0xB0 | (channel & 0x0F)
                    self._pg_output.write_short(status, control, value)
                except Exception:
                    pass
            elif self._mido_port:
                try:
                    self._mido_port.send(mido.Message('control_change', channel=channel, control=control, value=value))
                except Exception:
                    pass

    def pitch_bend(self, channel: int, pitch: int):
        """Send pitch bend (-8192 to +8191, center 0)."""
        if not self.is_connected:
            return
        channel = max(0, min(15, channel))
        pitch = max(-8192, min(8191, pitch))

        with self._lock:
            if self._pg_output:
                try:
                    norm = pitch + 8192
                    lsb = norm & 0x7F
                    msb = (norm >> 7) & 0x7F
                    status = 0xE0 | (channel & 0x0F)
                    self._pg_output.write_short(status, lsb, msb)
                except Exception:
                    pass
            elif self._mido_port:
                try:
                    self._mido_port.send(mido.Message('pitchwheel', channel=channel, pitch=pitch))
                except Exception:
                    pass

    def reset_all_controllers(self):
        """Reset controllers cleanly."""
        if not self.is_connected:
            return
        with self._lock:
            for ch in range(16):
                self.control_change(ch, 121, 0)
                self.control_change(ch, 64, 0)

    def panic(self):
        """All Notes Off (CC 123) and All Sound Off (CC 120) across all channels."""
        if not self.is_connected:
            return
        with self._lock:
            for ch in range(16):
                self.control_change(ch, 120, 0)
                self.control_change(ch, 123, 0)
                self.control_change(ch, 64, 0)
