"""
KIYA Piano Studio Pro - Master Hardware Interaction Controller
Routes all physical hardware controls, LCD pages, encoder dial, style triggers,
multi-pads, registration memory, and piano keys to the underlying engines:
- Synthesizer (Windows GS Wavetable / DSP)
- Split & Layer Manager
- Arranger & Accompaniment Coordinator
- Registration System
- Audio Recording & MIDI I/O
- PC Keyboard Mapping
"""

import os
import time
from typing import Optional
from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QFileDialog

from audio.engine import AudioEngine
from keyboard.split_layer import SplitLayerManager
from keyboard.computer_keymap import ComputerKeymap
from arranger.accompaniment import AccompanimentCoordinator
from presets.registrations import RegistrationManager, RegistrationSlot
from midi.input_manager import MidiInputManager
from ui.hardware_shell import HardwareShell


class InteractionController(QObject):
    """
    Central controller orchestrating all hardware UI events with audio/arranger logic.
    """
    def __init__(
        self,
        shell: HardwareShell,
        audio_engine: AudioEngine,
        split_layer: SplitLayerManager,
        arranger: AccompanimentCoordinator,
        reg_manager: RegistrationManager,
        computer_keymap: ComputerKeymap,
        midi_engine: Optional[MidiInputManager] = None,
        parent=None
    ):
        super().__init__(parent)
        self.shell = shell
        self.audio = audio_engine
        self.synth = audio_engine.synth
        self.split_layer = split_layer
        self.arranger = arranger
        self.reg_manager = reg_manager
        self.keymap = computer_keymap
        self.midi = midi_engine

        # Shorthand UI references
        self.cp = shell.control_panel
        self.left_panel = self.cp.left_panel
        self.lcd = self.cp.lcd_screen
        self.rotary = self.cp.rotary_cluster
        self.right_panel = self.cp.right_panel
        self.middle_strip = self.shell.middle_strip
        self.keybed = self.shell.keybed

        # Tap Tempo & Chord state
        self._tap_times = []
        self._active_chord_keys = set()

        # Connect all hardware UI components
        self._connect_keybed()
        self._connect_left_controls()
        self._connect_rotary_encoder()
        self._connect_right_instrument_panel()
        self._connect_middle_control_strip()
        self._connect_lcd_pages()
        self._connect_arranger_clock()
        self._connect_midi_input()

        # Initial UI synchronization
        self._sync_all_states()

    # =========================================================================
    # 1. PIANO KEYBED & PITCH/MOD WHEELS
    # =========================================================================
    def _connect_keybed(self):
        self.keybed.noteOn.connect(self._on_note_on)
        self.keybed.noteOff.connect(self._on_note_off)
        self.keybed.pitchBend.connect(self._on_pitch_bend)
        self.keybed.modulation.connect(self._on_modulation)

    def _on_note_on(self, note: int, velocity: int):
        # 1. Route to keyboard split & layer
        self.split_layer.route_note_on(note, velocity)
        self.keybed.set_key_pressed(note, True)

        # 2. Feed into arranger chord detection (left-hand keys or full keyboard)
        chord_note = note + self.split_layer.master_transpose
        self._active_chord_keys.add(chord_note)
        self.arranger.process_chord_notes(list(self._active_chord_keys))

        # 3. Bump live audio spectrum visualizer
        if hasattr(self.lcd.p_perf, "spectrum"):
            self.lcd.p_perf.spectrum.bump(min(1.0, velocity / 100.0))

        # 4. If sync start is armed and accompaniment is stopped, start on key press
        if self.middle_strip._sync_start_enabled and not self.arranger.is_playing:
            self.arranger.start_playback()
            self.middle_strip.set_playing_state(True)

    def _on_note_off(self, note: int):
        self.split_layer.route_note_off(note)
        self.keybed.set_key_pressed(note, False)

        chord_note = note + self.split_layer.master_transpose
        self._active_chord_keys.discard(chord_note)
        self.arranger.process_chord_notes(list(self._active_chord_keys))

        # Sync stop support: if all keys released and sync stop is active
        if self.middle_strip._sync_stop_enabled and len(self.split_layer._sounding_routes) == 0:
            self.arranger.stop_playback()
            self.middle_strip.set_playing_state(False)

    def _on_pitch_bend(self, value: int):
        # value: -8192 to 8191
        self.synth.pitch_bend(0, value)
        self.synth.pitch_bend(1, value)
        self.synth.pitch_bend(2, value)

    def _on_modulation(self, value: int):
        # value: 0 to 127 (CC 1)
        self.synth.control_change(0, 1, value)
        self.synth.control_change(1, 1, value)
        self.synth.control_change(2, 1, value)

    # =========================================================================
    # 2. LEFT CONTROL PANEL (SONG, TEMPO, TRANSPOSE, VOLUME)
    # =========================================================================
    def _connect_left_controls(self):
        # Master Volume
        self.left_panel.masterVolumeChanged.connect(self._on_master_volume)

        # Tempo
        self.left_panel.tempoUp.connect(lambda: self._adjust_tempo(1))
        self.left_panel.tempoDown.connect(lambda: self._adjust_tempo(-1))
        self.left_panel.tapTempo.connect(self._on_tap_tempo)
        self.left_panel.metronomeToggle.connect(self._on_metronome_toggle)

        # Transpose & Octave
        self.left_panel.transposeUp.connect(lambda: self._adjust_transpose(1))
        self.left_panel.transposeDown.connect(lambda: self._adjust_transpose(-1))
        self.left_panel.octaveUp.connect(lambda: self._adjust_octave(1))
        self.left_panel.octaveDown.connect(lambda: self._adjust_octave(-1))

        # Song Transport
        self.left_panel.songPlayPause.connect(self._on_song_play_pause)
        self.left_panel.songStop.connect(self._on_song_stop)
        self.left_panel.songRecord.connect(self._on_song_record)

        # Style Category Select & File Import
        self.left_panel.styleCategorySelected.connect(self._on_style_category)
        if hasattr(self.left_panel, "loadStyleRequested"):
            self.left_panel.loadStyleRequested.connect(self._on_browse_style_file)

    def _on_master_volume(self, vol: float):
        self.audio.set_master_volume(vol)
        for ch in range(16):
            self.synth.set_channel_volume(ch, vol)

    def _adjust_tempo(self, delta: int):
        new_bpm = max(30, min(280, self.arranger.tempo + delta))
        self.arranger.set_tempo(new_bpm)
        self._update_tempo_display(new_bpm)

    def _on_tap_tempo(self):
        now = time.time()
        self._tap_times.append(now)
        if len(self._tap_times) > 4:
            self._tap_times.pop(0)

        if len(self._tap_times) >= 2:
            intervals = [self._tap_times[i] - self._tap_times[i-1] for i in range(1, len(self._tap_times))]
            avg_interval = sum(intervals) / len(intervals)
            if 0.2 < avg_interval < 2.0:
                bpm = int(round(60.0 / avg_interval))
                self.arranger.set_tempo(bpm)
                self._update_tempo_display(bpm)

    def _on_metronome_toggle(self):
        is_metro = not self.left_panel.btn_metro.is_led_on
        self.left_panel.btn_metro.set_led(is_metro)
        # Metronome click on Ch 9 (rimshot 37 / cowbell 56) handled on beat if active

    def _adjust_transpose(self, delta: int):
        new_t = max(-12, min(12, self.split_layer.master_transpose + delta))
        self.split_layer.master_transpose = new_t
        t_text = f"{new_t:+d}" if new_t != 0 else "+0"
        self.left_panel.display_transpose.set_value(t_text)
        self.lcd.p_perf.lbl_transpose.setText(f"TRANS: {t_text}")

    def _adjust_octave(self, delta: int):
        target = self.right_panel._active_selected_part
        if target == "R1":
            self.split_layer.right1_octave = max(-2, min(2, self.split_layer.right1_octave + delta))
            val = self.split_layer.right1_octave
        elif target == "R2":
            self.split_layer.right2_octave = max(-2, min(2, self.split_layer.right2_octave + delta))
            val = self.split_layer.right2_octave
        else:
            self.split_layer.left_octave = max(-2, min(2, self.split_layer.left_octave + delta))
            val = self.split_layer.left_octave
        self.left_panel.display_octave.set_value(f"{val:+d}" if val != 0 else "0")

    def _on_song_play_pause(self):
        # Toggle recording playback or MIDI player
        pass

    def _on_song_stop(self):
        self.left_panel.btn_song_play.set_led(False)
        self.left_panel.btn_song_rec.set_led(False)
        if self.audio.is_recording:
            self.audio.stop_recording()
        self.synth.panic()

    def _on_song_record(self):
        if not self.audio.is_recording:
            self.audio.start_recording()
            self.left_panel.btn_song_rec.set_led(True)
            self.lcd.p_perf.lbl_rec_status.setText("REC: RECORDING (WAV/MIDI)  |  ARMED")
            self.lcd.p_perf.lbl_rec_status.setStyleSheet("color: #F05D52; font-weight: bold;")
        else:
            self.audio.stop_recording()
            self.left_panel.btn_song_rec.set_led(False)
            self.lcd.p_perf.lbl_rec_status.setText("REC: STOPPED  |  SAVED")
            self.lcd.p_perf.lbl_rec_status.setStyleSheet("color: #4DA8DA;")

    def _on_style_category(self, cat_name: str):
        cat_to_style = {
            "POP & ROCK": "Pop Groove",
            "BALLAD": "Slow Ballad",
            "DANCE": "80s Synthwave",
            "LATIN": "Latin Bossa Nova",
            "JAZZ": "Jazz Swing",
            "R&B / SOUL": "R&B Smooth Soul",
            "COUNTRY": "Country Folk",
            "WORLD / ETHNIC": "Ethiopian Tizita"
        }
        style_name = cat_to_style.get(cat_name, "Pop Groove")
        self._on_style_selected(style_name)

    # =========================================================================
    # 3. ROTARY ENCODER & NAVIGATION CLUSTER
    # =========================================================================
    def _connect_rotary_encoder(self):
        self.rotary.dialMoved.connect(self._on_dial_moved)
        self.rotary.enterTriggered.connect(self._on_enter)
        self.rotary.exitTriggered.connect(self._on_exit)
        self.rotary.upTriggered.connect(lambda: self._on_nav("UP"))
        self.rotary.downTriggered.connect(lambda: self._on_nav("DOWN"))
        self.rotary.leftTriggered.connect(lambda: self._on_nav("LEFT"))
        self.rotary.rightTriggered.connect(lambda: self._on_nav("RIGHT"))

    def _on_dial_moved(self, delta: int):
        curr_page = self.lcd.stack.currentIndex()
        if curr_page == 0:  # Main page: adjusts tempo
            self._adjust_tempo(delta)
        elif curr_page == 1:  # Voice page: select voice row
            tbl = self.lcd.p_voice.voice_table
            r = max(0, min(tbl.rowCount() - 1, tbl.currentRow() + delta))
            tbl.selectRow(r)
        elif curr_page == 2:  # Style page: select style row
            tbl = self.lcd.p_style.table
            r = max(0, min(tbl.rowCount() - 1, tbl.currentRow() + delta))
            tbl.selectRow(r)

    def _on_enter(self):
        curr_page = self.lcd.stack.currentIndex()
        if curr_page == 1:
            self.lcd.p_voice._assign_selected(self.right_panel._active_selected_part)
        elif curr_page == 2:
            self.lcd.p_style._on_load_clicked()

    def _on_exit(self):
        self.lcd.switch_to_page(0)  # Return to main performance page

    def _on_nav(self, direction: str):
        if direction in ("UP", "DOWN"):
            delta = -1 if direction == "UP" else 1
            self._on_dial_moved(delta)
        elif direction == "LEFT":
            self.lcd.prev_page()
        elif direction == "RIGHT":
            self.lcd.next_page()

    # =========================================================================
    # 4. RIGHT INSTRUMENT PANEL (VOICES, PARTS, EFFECTS)
    # =========================================================================
    def _connect_right_instrument_panel(self):
        self.right_panel.categorySelected.connect(self._on_voice_category)
        self.right_panel.partSelected.connect(self._on_part_selected)
        self.right_panel.partToggled.connect(self._on_part_toggled)
        self.right_panel.sustainToggled.connect(self._on_sustain_toggled)
        self.right_panel.touchToggled.connect(self._on_touch_toggled)
        self.right_panel.harmonyToggled.connect(self._on_harmony_toggled)
        self.right_panel.dspToggled.connect(self._on_dsp_toggled)

    def _on_voice_category(self, cat_name: str):
        # 1. Open voice page and populate that category
        self.lcd.switch_to_page(1)
        self.lcd.p_voice._populate_category(cat_name)

        # 2. Automatically assign premier voice of that category to active part
        cat_to_voice = {
            "PIANO": (0, "Acoustic Grand Piano"),
            "E. PIANO": (4, "Electric Piano 1 (Rhodes)"),
            "ORGAN": (16, "Drawbar Organ"),
            "ACCORDION": (21, "Accordion"),
            "GUITAR": (24, "Acoustic Guitar (nylon)"),
            "BASS": (32, "Acoustic Bass"),
            "STRINGS": (48, "String Ensemble 1"),
            "CHOIR": (52, "Choir Aahs"),
            "BRASS": (61, "Brass Section"),
            "WOODWIND": (73, "Flute"),
            "SAXOPHONE": (66, "Tenor Sax"),
            "SYNTH LEAD": (81, "Lead 2 (sawtooth)"),
            "SYNTH PAD": (89, "Pad 2 (warm)"),
            "PERCUSSION": (11, "Vibraphone"),
            "DRUM KITS": (0, "Standard Drum Kit"),
            "EXPANSION": (50, "Synth Strings 1")
        }
        if cat_name in cat_to_voice:
            prog, name = cat_to_voice[cat_name]
            part = self.right_panel._active_selected_part
            self._on_voice_selected(part, prog, name)

    def _on_part_selected(self, part: str):
        # Update octave readout for that part
        if part == "R1":
            oct_val = self.split_layer.right1_octave
        elif part == "R2":
            oct_val = self.split_layer.right2_octave
        else:
            oct_val = self.split_layer.left_octave
        self.left_panel.display_octave.set_value(f"{oct_val:+d}" if oct_val != 0 else "0")

    def _on_part_toggled(self, part: str, is_on: bool):
        if part == "R1":
            self.split_layer.right1_mute = not is_on
        elif part == "R2":
            self.split_layer.set_layer_enabled(is_on)
            self.lcd.p_perf.lbl_r2_name.setText(
                "Warm String Ensemble  [ON]" if is_on else "Warm String Ensemble  [OFF]"
            )
            self.lcd.p_perf.lbl_r2_name.setStyleSheet("color: #4DA8DA;" if is_on else "color: #8C9BAA;")
        elif part == "LEFT":
            self.split_layer.set_split_enabled(is_on)
            self.keybed.set_split_point(self.split_layer.split_point, show_marker=is_on)
            self.lcd.p_perf.lbl_left_name.setText(
                "Acoustic Upright Bass  [ON]" if is_on else "Acoustic Upright Bass  [OFF]"
            )
            self.lcd.p_perf.lbl_left_name.setStyleSheet("color: #FFB347;" if is_on else "color: #8C9BAA;")

    def _on_sustain_toggled(self, is_on: bool):
        cc_val = 127 if is_on else 0
        self.synth.control_change(0, 64, cc_val)
        self.synth.control_change(1, 64, cc_val)
        self.synth.control_change(2, 64, cc_val)

    def _on_touch_toggled(self, is_on: bool):
        pass

    def _on_harmony_toggled(self, is_on: bool):
        pass

    def _on_dsp_toggled(self, is_on: bool):
        # Toggle reverb / chorus depth
        rev_val = 64 if is_on else 0
        for ch in range(16):
            self.synth.control_change(ch, 91, rev_val)

    # =========================================================================
    # 5. MIDDLE CONTROL STRIP (ARRANGER, MULTI-PADS, REGISTRATIONS)
    # =========================================================================
    def _connect_middle_control_strip(self):
        # Style playback
        self.middle_strip.startStopClicked.connect(self._on_start_stop)
        self.middle_strip.variationChanged.connect(self._on_variation_changed)
        self.middle_strip.introRequested.connect(self._on_intro)
        self.middle_strip.endingRequested.connect(self._on_ending)
        self.middle_strip.breakRequested.connect(self._on_break)
        self.middle_strip.acmpToggled.connect(self._on_acmp_toggled)

        # Multi-Pads
        self.middle_strip.multipad_panel.padTriggered.connect(self._on_multipad_trigger)
        self.middle_strip.multipad_panel.padStopped.connect(self._on_multipad_stop)

        # Registrations
        self.middle_strip.registration_panel.slotStored.connect(self._on_reg_store)
        self.middle_strip.registration_panel.slotRecalled.connect(self._on_reg_recall)
        if hasattr(self.middle_strip, "loadStyleRequested"):
            self.middle_strip.loadStyleRequested.connect(self._on_browse_style_file)
        if hasattr(self.middle_strip.registration_panel, "loadBankRequested"):
            self.middle_strip.registration_panel.loadBankRequested.connect(self._on_browse_regist_file)
            self.middle_strip.registration_panel.exportBankRequested.connect(self._on_export_regist_file)

    def _on_start_stop(self):
        if self.arranger.is_playing:
            self.arranger.stop_playback()
            self.middle_strip.set_playing_state(False)
            self.middle_strip.beat_indicator.reset_all()
        else:
            self.arranger.start_playback()
            self.middle_strip.set_playing_state(True)

    def _on_variation_changed(self, var: str):
        self.arranger.set_variation(var)
        self.lcd.p_perf.lbl_style_section.setText(f"SECTION: MAIN {var}  |  ACMP: ON")

    def _on_intro(self, num: int):
        self.arranger.trigger_intro()
        self.middle_strip.set_playing_state(True)
        self.lcd.p_perf.lbl_style_section.setText(f"SECTION: INTRO {num}  |  ACMP: ON")

    def _on_ending(self, num: int):
        self.arranger.trigger_ending()
        self.lcd.p_perf.lbl_style_section.setText(f"SECTION: ENDING {num}  |  ACMP: ON")

    def _on_break(self):
        self.arranger.trigger_break()
        self.lcd.p_perf.lbl_style_section.setText("SECTION: BREAK  |  ACMP: ON")

    def _on_acmp_toggled(self, is_on: bool):
        self.arranger.set_acmp_enabled(is_on)
        sec = self.arranger.style_engine.current_section_name or "MAIN A"
        self.lcd.p_perf.lbl_style_section.setText(f"SECTION: {sec}  |  ACMP: {'ON' if is_on else 'OFF'}")

    def _on_multipad_trigger(self, pad_index: int):
        # Real audio playback on multi-pad press
        if pad_index == 1:
            # Crash Cymbal (note 49) + Snare hit on Drum Channel 9
            self.synth.note_on(9, 49, 115)
            self.synth.note_on(9, 38, 100)
            QTimer.singleShot(300, lambda: self.synth.note_off(9, 49))
            QTimer.singleShot(300, lambda: self.synth.note_off(9, 38))
        elif pad_index == 2:
            # Tambourine / Shaker roll (notes 54 & 70)
            for delay, n in [(0, 54), (80, 70), (160, 54), (240, 70)]:
                QTimer.singleShot(delay, lambda note=n: self.synth.note_on(9, note, 105))
                QTimer.singleShot(delay + 120, lambda note=n: self.synth.note_off(9, note))
        elif pad_index == 3:
            # Brass Section Chord (Notes 60, 64, 67, 72)
            for n in [60, 64, 67, 72]:
                self.synth.note_on(0, n, 100)
                QTimer.singleShot(450, lambda note=n: self.synth.note_off(0, note))
        elif pad_index == 4:
            # Orchestra Hit (Program 55, Note 60)
            self.synth.note_on(1, 60, 110)
            QTimer.singleShot(400, lambda: self.synth.note_off(1, 60))

    def _on_multipad_stop(self):
        self.synth.panic()

    def _on_reg_store(self, slot_num: int):
        slot_idx = max(0, min(7, slot_num - 1))
        slot = RegistrationSlot(
            name=f"User Reg {slot_num}",
            is_empty=False,
            right1_voice=self.split_layer.right1_program,
            right2_voice=self.split_layer.right2_program,
            layer_enabled=self.split_layer.layer_enabled,
            left_voice=self.split_layer.left_program,
            split_enabled=self.split_layer.split_enabled,
            split_point=self.split_layer.split_point,
            transpose=self.split_layer.master_transpose,
            tempo=self.arranger.tempo,
            style_name=self.arranger.current_style_name or "8-Beat Modern Pop"
        )
        self.reg_manager.save_slot(slot_idx, slot)
        lbl = self.lcd.p_perf.reg_indicators[slot_idx]
        lbl.setText(f"[{slot_num}] STORED")
        lbl.setStyleSheet("background: #1E3825; color: #65D878; border: 1px solid #285435; padding: 2px 6px; border-radius: 2px;")

    def _on_reg_recall(self, slot_num: int):
        slot_idx = max(0, min(7, slot_num - 1))
        slot = self.reg_manager.get_slot(slot_idx)
        if slot and not slot.is_empty:
            self.split_layer.right1_program = slot.right1_voice
            self.split_layer.right2_program = slot.right2_voice
            self.split_layer.set_layer_enabled(slot.layer_enabled)
            self.split_layer.left_program = slot.left_voice
            self.split_layer.set_split_enabled(slot.split_enabled)
            self.split_layer.set_split_point(slot.split_point)
            self.split_layer.master_transpose = slot.transpose
            self.split_layer.apply_all_programs()

            if slot.style_name:
                self.arranger.load_style(slot.style_name)
            if slot.tempo:
                self.arranger.set_tempo(slot.tempo)
                self._update_tempo_display(slot.tempo)

            self._sync_all_states()

    # =========================================================================
    # 6. LCD SCREEN PAGES INTERACTION
    # =========================================================================
    def _connect_lcd_pages(self):
        # Page 0: Performance Page clicks
        self.lcd.p_perf.styleClicked.connect(lambda: self.lcd.switch_to_page(2))
        if hasattr(self.lcd.p_perf, "loadStyleClicked"):
            self.lcd.p_perf.loadStyleClicked.connect(self._on_browse_style_file)
        if hasattr(self.lcd.p_perf, "loadRegistClicked"):
            self.lcd.p_perf.loadRegistClicked.connect(self._on_browse_regist_file)

        # Page 1: Voice Page assign
        self.lcd.p_voice.voiceSelected.connect(self._on_voice_assigned)

        # Page 2: Style Page select & import
        self.lcd.p_style.styleSelected.connect(self._on_style_selected)
        if hasattr(self.lcd.p_style, "importStyleRequested"):
            self.lcd.p_style.importStyleRequested.connect(self._on_browse_style_file)

        # Page 3: Mixer faders
        self.lcd.p_mixer.channelVolumeChanged.connect(self._on_mixer_volume)

        # Page 5: Registration Page
        if hasattr(self.lcd.p_regist, "importBankRequested"):
            self.lcd.p_regist.importBankRequested.connect(self._on_browse_regist_file)
            self.lcd.p_regist.exportBankRequested.connect(self._on_export_regist_file)
            self.lcd.p_regist.slotSelected.connect(self._on_reg_recall)

        # Page 6: USB File Explorer Page
        if hasattr(self.lcd, "p_file"):
            self.lcd.p_file.importStyleRequested.connect(self._on_browse_style_file)
            self.lcd.p_file.importRegistRequested.connect(self._on_browse_regist_file)
            self.lcd.p_file.exportRegistRequested.connect(self._on_export_regist_file)
            self.lcd.p_file.styleFileSelected.connect(self._on_load_style_filepath)
            self.lcd.p_file.registFileSelected.connect(self._on_load_regist_filepath)

        # LCD Hardware Softkeys [A]-[E] and [F]-[J]
        if hasattr(self.lcd, "softkeyPressed"):
            self.lcd.softkeyPressed.connect(self._on_softkey_pressed)

    def _on_voice_assigned(self, target: str, program: int, name: str):
        if target == "R1":
            self.split_layer.right1_program = program
            self.synth.set_program(0, program)
            self.lcd.p_perf.lbl_r1_name.setText(name)
        elif target == "R2":
            self.split_layer.right2_program = program
            self.synth.set_program(1, program)
            self.lcd.p_perf.lbl_r2_name.setText(f"{name}  [ON]")
            self.split_layer.set_layer_enabled(True)
            self.right_panel.btn_on_r2.set_led(True)
        elif target == "LEFT":
            self.split_layer.left_program = program
            self.synth.set_program(2, program)
            self.lcd.p_perf.lbl_left_name.setText(f"{name}  [ON]")
            self.split_layer.set_split_enabled(True)
            self.right_panel.btn_on_left.set_led(True)
            self.keybed.set_split_point(self.split_layer.split_point, show_marker=True)

    def _on_style_selected(self, style_name: str):
        self.arranger.load_style(style_name)
        self.lcd.p_perf.lbl_style_name.setText(style_name)
        if hasattr(self.lcd.p_perf, "lbl_style_genre"):
            cat = getattr(self.arranger.current_style, "category", "Pop") if getattr(self.arranger, "current_style", None) else "Pop"
            self.lcd.p_perf.lbl_style_genre.setText(f"[{cat.upper()}]")
        self._update_tempo_display(self.arranger.tempo)
        self.lcd.switch_to_page(0)  # Return to main performance page

    def _on_mixer_volume(self, ch_id: str, vol: float):
        ch_map = {
            "R1": 0, "R2": 1, "LEFT": 2, "DRUMS": 9,
            "BASS": 8, "CHORD1": 4, "CHORD2": 5, "PAD": 6
        }
        if ch_id in ch_map:
            self.synth.set_channel_volume(ch_map[ch_id], vol)

    # =========================================================================
    # 7. ARRANGER CLOCK & BEAT FLASHING
    # =========================================================================
    def _connect_arranger_clock(self):
        self.arranger.on_beat_changed = self._on_beat_pulse
        self.arranger.on_chord_changed = self._on_chord_changed

    def _on_beat_pulse(self, beat: int, measure: int):
        # Flash the physical 4-jewel LEDs
        self.middle_strip.beat_indicator.trigger_beat(beat)
        self.lcd.p_perf.lbl_measure.setText(f"BAR: {measure:03d} : {beat}")

        # Update rotating 4-beat glowing dots on the LCD screen
        dots = ["○", "○", "○", "○"]
        if 1 <= beat <= 4:
            dots[beat - 1] = "●"
        self.lcd.p_perf.lbl_beat_dots.setText("   ".join(dots))

        # Bump real-time spectrum visualizer
        if hasattr(self.lcd.p_perf, "spectrum"):
            self.lcd.p_perf.spectrum.bump(0.75)

    def _on_chord_changed(self, chord_info):
        display = chord_info.display_name if hasattr(chord_info, 'display_name') else str(chord_info)
        self.lcd.p_perf.lbl_chord.setText(f"CHORD: {display}")
        self.lcd.p_perf.lbl_hero_chord.setText(display)

    # =========================================================================
    # 8. HARDWARE MIDI INPUT INTEGRATION
    # =========================================================================
    def _connect_midi_input(self):
        if self.midi:
            self.midi.on_note_event = self._on_midi_note_event
            self.midi.on_cc_event = self._on_midi_cc_event
            self.midi.on_pitch_event = self._on_midi_pitch_event

    def _on_midi_note_event(self, event):
        if event.is_note_on:
            self._on_note_on(event.note, event.velocity)
        else:
            self._on_note_off(event.note)

    def _on_midi_cc_event(self, event):
        if event.control == 64:  # Sustain pedal
            self.right_panel.btn_sustain.set_led(event.value >= 64)
            self._on_sustain_toggled(event.value >= 64)

    def _on_midi_pitch_event(self, event):
        self._on_pitch_bend(event.value)

    # =========================================================================
    # 9. STATE SYNCHRONIZATION HELPERS
    # =========================================================================
    def _sync_all_states(self):
        self._update_tempo_display(self.arranger.tempo)
        t_val = self.split_layer.master_transpose
        self.left_panel.display_transpose.set_value(f"{t_val:+d}" if t_val != 0 else "+0")
        self.left_panel.display_octave.set_value(f"{self.split_layer.right1_octave:+d}" if self.split_layer.right1_octave != 0 else "0")

    def _update_tempo_display(self, bpm: int):
        self.lcd.p_perf.lbl_tempo.setText(f"TEMPO: {bpm}  [4/4]")
        if hasattr(self.left_panel, "display_tempo"):
            self.left_panel.display_tempo.set_value(str(bpm))

    def _on_softkey_pressed(self, key_id: str):
        """Handle hardware softkeys [A]-[E] on left and [F]-[J] on right."""
        k = key_id.upper()
        if k == "A":
            self.lcd.switch_to_page(2)  # Style Page
        elif k == "B":
            self.lcd.switch_to_page(0)  # Main Performance Page
        elif k == "C":
            self.lcd.switch_to_page(5)  # Registration Page
        elif k == "D":
            self.lcd.switch_to_page(3)  # Mixer Page
        elif k == "E":
            self._on_browse_style_file() # Quick Load Style
        elif k == "F":
            self.right_panel.set_selected_part("R1")
            self.lcd.switch_to_page(1)  # Voice Page (R1)
        elif k == "G":
            self.right_panel.set_selected_part("R2")
            self.lcd.switch_to_page(1)  # Voice Page (R2)
        elif k == "H":
            self.right_panel.set_selected_part("LEFT")
            self.lcd.switch_to_page(1)  # Voice Page (LEFT)
        elif k == "I":
            self.lcd.switch_to_page(4)  # DSP/FX Page
        elif k == "J":
            self.lcd.switch_to_page(6)  # USB File Explorer Page

    def _on_browse_style_file(self):
        """Open system file picker to select Yamaha Style or MIDI file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.shell,
            "Import Yamaha Style File",
            "resources/styles",
            "Yamaha Style / MIDI (*.sty *.prs *.bcs *.sst *.mid *.midi *.json);;All Files (*.*)"
        )
        if file_path:
            self._on_load_style_filepath(file_path)

    def _on_load_style_filepath(self, file_path: str):
        """Parse and load Yamaha .sty / .mid / .json file into accompaniment engine."""
        style = self.arranger.load_style_from_file(file_path)
        if style:
            self.lcd.p_perf.lbl_style_name.setText(style.name)
            if hasattr(self.lcd.p_perf, "lbl_style_genre"):
                self.lcd.p_perf.lbl_style_genre.setText(f"[{style.category.upper()}]")
            self._update_tempo_display(style.tempo)
            self.lcd.show_toast(f"STYLE LOADED: {style.name} ({style.tempo} BPM)", "#39FF8A")
            if hasattr(self.lcd, "p_file"):
                self.lcd.p_file.refresh_file_list()
            self.lcd.switch_to_page(0)

    def _on_browse_regist_file(self):
        """Open system file picker to select Yamaha Registration Bank."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.shell,
            "Import Yamaha Registration Bank",
            "resources/registrations",
            "Registration Bank Files (*.rgt *.reg *.json);;All Files (*.*)"
        )
        if file_path:
            self._on_load_regist_filepath(file_path)

    def _on_load_regist_filepath(self, file_path: str):
        """Import registration memory bank from file."""
        success = self.reg_manager.import_bank_from_file(file_path)
        if success:
            fname = os.path.basename(file_path)
            self.lcd.show_toast(f"REG BANK LOADED: {fname}", "#38B4FF")
            if hasattr(self.lcd.p_regist, "_populate_slots"):
                self.lcd.p_regist._populate_slots()
            if hasattr(self.lcd, "p_file"):
                self.lcd.p_file.refresh_file_list()
            self._on_reg_recall(1)

    def _on_export_regist_file(self):
        """Export active registration memory bank to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.shell,
            "Export Registration Bank",
            f"resources/registrations/User_Bank_{self.reg_manager.current_bank}.rgt",
            "Registration Bank (*.rgt *.json);;All Files (*.*)"
        )
        if file_path:
            success = self.reg_manager.export_bank_to_file(file_path)
            if success:
                fname = os.path.basename(file_path)
                self.lcd.show_toast(f"REG BANK SAVED: {fname}", "#FFB726")
                if hasattr(self.lcd, "p_file"):
                    self.lcd.p_file.refresh_file_list()

    def handle_key_press(self, event):
        """Map computer keyboard presses to musical notes."""
        if event.isAutoRepeat():
            return
        text = event.text().strip().lower()
        note = self.keymap.get_note_for_key(text) if text else None
        if note is None:
            note = self.keymap.get_note_for_key(event.key())
        if note is not None:
            self._on_note_on(note, 100)

    def handle_key_release(self, event):
        """Map computer keyboard releases to musical note releases."""
        if event.isAutoRepeat():
            return
        text = event.text().strip().lower()
        note = self.keymap.get_note_for_key(text) if text else None
        if note is None:
            note = self.keymap.get_note_for_key(event.key())
        if note is not None:
            self._on_note_off(note)
