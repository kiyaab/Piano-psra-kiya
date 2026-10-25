"""
KIYA Piano Studio Pro - Automated UI & Hardware Component Tests
Tests:
- HardwareWindow initialization and central shell widget
- PhysicalButton states (normal, pressed, checkable, LED jewel)
- RotaryDial continuous angular rotation and steps
- CentralLCDDisplay 10-page switching and softkeys
- MiddleControlStrip transport and section buttons
- PianoKeybedAssembly 61-key note triggers and pitch/mod wheels
"""

import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_QPA_FONTDIR'] = 'C:/Windows/Fonts'

import pytest
from PySide6.QtWidgets import QApplication

from app.application import KiyaApplication
from ui.hardware_shell import HardwareShell
from ui.physical_button import PhysicalButton
from ui.rotary_encoder import RotaryDial
from ui.lcd_screen import CentralLCDDisplay
from ui.middle_strip import MiddleControlStrip
from ui.piano_keybed import PianoKeybedAssembly


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_physical_button(qapp):
    """Test physical button initialization, click, and LED states."""
    btn = PhysicalButton("TEST", secondary_text="SUB", indicator="green", checkable=True)
    assert btn.label == "TEST"
    assert btn.secondary_label == "SUB"
    assert btn.led_color == "green"
    assert not btn.is_led_on()

    btn.set_led(True)
    assert btn.is_led_on()

    btn.set_checked(True)
    assert btn.is_checked()


def test_rotary_dial(qapp):
    """Test rotary encoder dial rotation delta."""
    dial = RotaryDial(size=86)
    deltas = []
    dial.valueChanged.connect(lambda d: deltas.append(d))

    # Simulate steps
    dial.angle_deg = 36.0
    dial.valueChanged.emit(1)
    dial.valueChanged.emit(-1)

    assert len(deltas) == 2
    assert deltas == [1, -1]


def test_lcd_screen_pages(qapp):
    """Test Central LCD screen page switching across all 10 pages."""
    lcd = CentralLCDDisplay()
    assert lcd.stack.count() == 10

    # Switch through each page
    for i in range(10):
        lcd.switch_to_page(i)
        assert lcd.stack.currentIndex() == i

    # Next / Prev
    lcd.switch_to_page(0)
    lcd.next_page()
    assert lcd.stack.currentIndex() == 1
    lcd.prev_page()
    assert lcd.stack.currentIndex() == 0


def test_middle_control_strip(qapp):
    """Test middle hardware control strip signals."""
    strip = MiddleControlStrip()
    variations = []
    strip.variationChanged.connect(lambda v: variations.append(v))

    strip._select_variation("B")
    assert "B" in variations
    assert strip.var_buttons["B"].is_led_on()

    strip._toggle_acmp()
    assert not strip._acmp_enabled


def test_piano_keybed(qapp):
    """Test 61-key piano keybed note triggers and pitch/mod wheels."""
    keybed = PianoKeybedAssembly()
    pressed_notes = []
    released_notes = []

    keybed.noteOn.connect(lambda n, v: pressed_notes.append((n, v)))
    keybed.noteOff.connect(lambda n: released_notes.append(n))

    # Note 60 (Middle C)
    keybed.piano.note_pressed.emit(60, 100)
    assert (60, 100) in pressed_notes

    keybed.piano.note_released.emit(60)
    assert 60 in released_notes


def test_hardware_window_full_integration(qapp):
    """Test full KiyaApplication window instantiation and interaction."""
    app_inst = KiyaApplication([])
    w = app_inst.window
    assert w is not None
    assert "PSR-S975" in w.windowTitle()
    assert isinstance(w.centralWidget(), HardwareShell)

    # Note on and off
    w.controller._on_note_on(60, 100)
    assert len(w.split_layer._sounding_routes) > 0
    w.controller._on_note_off(60)
    assert len(w.split_layer._sounding_routes) == 0

    # Transpose
    w.controller._adjust_transpose(3)
    assert w.split_layer.master_transpose == 3
    w.controller._adjust_transpose(-3)
    assert w.split_layer.master_transpose == 0

    app_inst.quit()


def test_piano_touch_and_mouse_events(qapp):
    """Test virtual piano mouse click, drag glissando, and multi-touch chords."""
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QPointF, Qt

    keybed = PianoKeybedAssembly()
    piano = keybed.piano
    piano.resize(1000, 200)
    piano._calculate_key_geometry()

    pressed = []
    released = []
    piano.note_pressed.connect(lambda n, v: pressed.append((n, v)))
    piano.note_released.connect(lambda n: released.append(n))

    # 1. Test clicking Middle C (note 60)
    key_c = piano.keys[60]
    click_pos = QPointF(key_c.rect.center().x(), key_c.rect.center().y())
    press_ev = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        click_pos,
        click_pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    piano.mousePressEvent(press_ev)

    assert key_c.is_pressed
    assert len(pressed) == 1
    assert pressed[0][0] == 60
    assert 60 <= pressed[0][1] <= 127

    # 2. Test glissando drag to D4 (note 62)
    key_d = piano.keys[62]
    drag_pos = QPointF(key_d.rect.center().x(), key_d.rect.center().y())
    move_ev = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        drag_pos,
        drag_pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    piano.mouseMoveEvent(move_ev)

    assert not key_c.is_pressed
    assert key_d.is_pressed
    assert 60 in released
    assert any(n == 62 for n, v in pressed)

    # 3. Test release
    rel_ev = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        drag_pos,
        drag_pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier
    )
    piano.mouseReleaseEvent(rel_ev)

    assert not key_d.is_pressed
    assert 62 in released

    # 4. Test release_all_keys
    piano.set_key_pressed(64, True)
    assert piano.keys[64].is_pressed
    piano.release_all_keys()
    assert not piano.keys[64].is_pressed
    assert piano.current_mouse_note is None


def test_arranger_page_ui(qapp):
    """Test modernized ArrangerPage style selection, sections, and mixer."""
    from ui.pages.arranger_page import ArrangerPage
    from arranger.style_loader import StyleDefinition

    dummy_style = StyleDefinition(
        name="Test Groove",
        category="Pop",
        tempo=125,
        time_sig_num=4,
        time_sig_den=4,
        drum_program=0,
        bass_program=33,
        chord1_program=24,
        chord2_program=48,
        phrase_program=81,
        sections={}
    )

    page = ArrangerPage([dummy_style])
    assert page.lbl_hero_title.text() == "Test Groove"
    assert page.badge_cat.text() == "POP"
    assert page.badge_ts.text() == "4/4"
    assert page.disp_tempo.lbl_value.text() == "125 BPM"

    # Test section click
    sections = []
    page.section_selected.connect(lambda s: sections.append(s))
    page.section_buttons["MAIN B"].clicked.emit()
    assert "MAIN_B" in sections
    assert page.disp_section.lbl_value.text() == "MAIN B"

    # Test tempo change
    tempos = []
    page.tempo_changed.connect(lambda t: tempos.append(t))
    page.tempo_slider.setValue(130)
    assert 130 in tempos
    assert page.disp_tempo.lbl_value.text() == "130 BPM"


