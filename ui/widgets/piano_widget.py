"""
KIYA Piano Studio Pro - World-Class 61-Key Virtual Piano Keyboard Widget
Implements stunning white and black key rendering:
- Pristine warm ivory gradients with depth and texture
- Highly polished ebony black keys with glass-like sheen
- Vivid amber press feedback with felt-shadow effect
- Glowing split zone indicators
- Beautiful computer key shortcut badges
- Smooth velocity-sensitive mouse/touch interaction
"""

from typing import Dict, Set, Optional, List
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient,
    QFont, QMouseEvent, QEventPoint, QTouchEvent
)
from app.constants import (
    KEYBOARD_MIN_NOTE,
    KEYBOARD_MAX_NOTE,
    DEFAULT_SPLIT_POINT,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    NOTE_NAMES,
    midi_to_note_name
)


class PianoKey:
    """Calculated geometry and state for a single piano key."""
    __slots__ = ('note', 'is_black', 'rect', 'is_pressed', 'is_highlighted', 'highlight_color')

    def __init__(self, note: int, is_black: bool):
        self.note = note
        self.is_black = is_black
        self.rect = QRectF()
        self.is_pressed = False
        self.is_highlighted = False
        self.highlight_color = QColor(COLOR_ACCENT_ORANGE)


class PianoKeyboardWidget(QWidget):
    """World-class 61-key interactive virtual piano keyboard widget."""

    note_pressed = Signal(int, int)   # note, velocity
    note_released = Signal(int)       # note

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setMinimumHeight(140)

        self.min_note = KEYBOARD_MIN_NOTE   # 36 (C2)
        self.max_note = KEYBOARD_MAX_NOTE   # 96 (C7) - 61 keys total

        self.split_point = DEFAULT_SPLIT_POINT  # 54 (F#3)
        self.show_split_marker = False
        self.show_note_names = True

        # Keys storage: note -> PianoKey
        self.keys: Dict[int, PianoKey] = {}
        for n in range(self.min_note, self.max_note + 1):
            is_black = (n % 12) in (1, 3, 6, 8, 10)
            self.keys[n] = PianoKey(n, is_black)

        # Mouse interaction state
        self.current_mouse_note: Optional[int] = None
        self.is_mouse_down = False

        # Multi-touch state: point_id -> midi_note
        self._touch_notes: Dict[int, int] = {}

        # Scale / Learning highlights
        self.highlighted_notes: Set[int] = set()

    def set_split_point(self, split_note: int, show_marker: bool = True):
        self.split_point = split_note
        self.show_split_marker = show_marker
        self.update()

    def set_show_note_names(self, show: bool):
        self.show_note_names = show
        self.update()

    def set_highlighted_notes(self, notes: List[int], color: Optional[QColor] = None):
        self.highlighted_notes = set(notes)
        for n, k in self.keys.items():
            k.is_highlighted = (n in self.highlighted_notes)
            if color:
                k.highlight_color = color
        self.update()

    def clear_highlights(self):
        self.highlighted_notes.clear()
        for k in self.keys.values():
            k.is_highlighted = False
        self.update()

    def set_key_sounding(self, note: int, sounding: bool, color: Optional[QColor] = None):
        """Highlight key visually when played by any input source (MIDI, keyboard, song)."""
        if note in self.keys:
            self.keys[note].is_pressed = sounding
            if color:
                self.keys[note].highlight_color = color
            self.update()

    def set_key_pressed(self, note: int, is_pressed: bool):
        self.set_key_sounding(note, is_pressed)

    def release_all_visual_keys(self):
        for k in self.keys.values():
            k.is_pressed = False
        self.current_mouse_note = None
        self._touch_notes.clear()
        self.update()

    def release_all_keys(self):
        self.release_all_visual_keys()

    def resizeEvent(self, event):
        self._calculate_key_geometry()
        super().resizeEvent(event)

    def _calculate_key_geometry(self):
        """Calculate layout geometry for white and black keys."""
        width = float(self.width())
        height = float(self.height())

        white_notes = [n for n in range(self.min_note, self.max_note + 1) if not self.keys[n].is_black]
        num_white = len(white_notes)
        if num_white == 0:
            return

        white_key_width = width / num_white
        black_key_width = white_key_width * 0.60
        black_key_height = height * 0.63

        white_idx = 0
        white_x_positions: Dict[int, float] = {}
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if not k.is_black:
                x = white_idx * white_key_width
                white_x_positions[n] = x
                k.rect = QRectF(x, 0.0, white_key_width, height)
                white_idx += 1

        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if k.is_black:
                prev_white_n = n - 1
                if prev_white_n in white_x_positions:
                    prev_x = white_x_positions[prev_white_n]
                    x = prev_x + white_key_width - (black_key_width * 0.5)
                    k.rect = QRectF(x, 0.0, black_key_width, black_key_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        height = self.height()

        # Background shadow strip at top of keybed
        bg_grad = QLinearGradient(0, 0, 0, 8)
        bg_grad.setColorAt(0.0, QColor(0, 0, 0, 120))
        bg_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_grad)
        painter.drawRect(QRectF(0, 0, self.width(), 8))

        # 1. Draw White Keys
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if not k.is_black:
                self._draw_white_key(painter, k)

        # 2. Draw Black Keys (on top)
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if k.is_black:
                self._draw_black_key(painter, k)

        # 3. Draw Split Point Marker Line if active
        if self.show_split_marker and self.split_point in self.keys:
            sp_key = self.keys[self.split_point]
            split_x = sp_key.rect.right()
            painter.setPen(QPen(QColor(COLOR_ACCENT_BLUE), 2.5, Qt.PenStyle.DashLine))
            painter.drawLine(int(split_x), 0, int(split_x), int(height))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLOR_ACCENT_BLUE))
            painter.drawRoundedRect(QRectF(split_x - 28, 4, 56, 18), 5, 5)
            painter.setPen(QColor("#0A1020"))
            font = painter.font()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(split_x - 28, 4, 56, 18), Qt.AlignmentFlag.AlignCenter, "SPLIT")

    PC_KEY_MAP = {
        48: 'Z', 49: 'S', 50: 'X', 51: 'D', 52: 'C', 53: 'V', 54: 'G', 55: 'B', 56: 'H', 57: 'N', 58: 'J', 59: 'M',
        60: 'Q', 61: '2', 62: 'W', 63: '3', 64: 'E', 65: 'R', 66: '5', 67: 'T', 68: '6', 69: 'Y', 70: '7', 71: 'U',
        72: 'I', 73: '9', 74: 'O', 75: '0', 76: 'P'
    }

    def _draw_white_key(self, painter: QPainter, key: PianoKey):
        rect = key.rect
        is_split_left = self.show_split_marker and (key.note <= self.split_point)

        y_depress = 2.5 if key.is_pressed else 0.0
        draw_rect = rect.adjusted(0.6, y_depress, -0.6, 0.0)

        # ── 1. Key Body: Premium ivory gradient ─────────────────────────────
        grad = QLinearGradient(0, draw_rect.top(), 0, draw_rect.bottom())
        if key.is_pressed:
            # Vivid warm amber press
            grad.setColorAt(0.0, QColor("#FFE566"))
            grad.setColorAt(0.2, QColor("#FFCC00"))
            grad.setColorAt(0.6, QColor("#FF9500"))
            grad.setColorAt(0.9, QColor("#E06000"))
            grad.setColorAt(1.0, QColor("#C04400"))
            border_col = QColor("#A03000")
        elif key.is_highlighted:
            grad.setColorAt(0.0, QColor("#FFFBEC"))
            grad.setColorAt(0.6, QColor("#FFE080"))
            grad.setColorAt(1.0, QColor("#FFB020"))
            border_col = QColor(COLOR_ACCENT_ORANGE)
        elif is_split_left:
            grad.setColorAt(0.0, QColor("#EEF6FF"))
            grad.setColorAt(0.7, QColor("#DCEEFF"))
            grad.setColorAt(1.0, QColor("#C8E4FF"))
            border_col = QColor("#5090D0")
        else:
            # Pristine warm acoustic ivory – 5 stop gradient
            grad.setColorAt(0.00, QColor("#FFFFFF"))
            grad.setColorAt(0.20, QColor("#FEFCF8"))
            grad.setColorAt(0.55, QColor("#FAF7F0"))
            grad.setColorAt(0.85, QColor("#F2EDE3"))
            grad.setColorAt(1.00, QColor("#E4DDD0"))
            border_col = QColor("#A8B4C0")

        painter.setPen(QPen(border_col, 0.8))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(draw_rect, 3.5, 3.5)

        # ── 2. Left bevel highlight & right shadow ───────────────────────────
        if not key.is_pressed:
            left_grad = QLinearGradient(draw_rect.left(), draw_rect.top(),
                                         draw_rect.left(), draw_rect.bottom())
            left_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
            left_grad.setColorAt(0.2, QColor(255, 255, 255, 200))
            left_grad.setColorAt(0.8, QColor(255, 255, 255, 120))
            left_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(left_grad), 1.2))
            painter.drawLine(int(draw_rect.left() + 1), int(draw_rect.top() + 5),
                             int(draw_rect.left() + 1), int(draw_rect.bottom() - 8))

            right_grad = QLinearGradient(draw_rect.right(), draw_rect.top(),
                                          draw_rect.right(), draw_rect.bottom())
            right_grad.setColorAt(0.0, QColor(100, 110, 130, 0))
            right_grad.setColorAt(0.3, QColor(100, 110, 130, 60))
            right_grad.setColorAt(0.7, QColor(100, 110, 130, 50))
            right_grad.setColorAt(1.0, QColor(100, 110, 130, 0))
            painter.setPen(QPen(QBrush(right_grad), 1.0))
            painter.drawLine(int(draw_rect.right() - 1), int(draw_rect.top() + 5),
                             int(draw_rect.right() - 1), int(draw_rect.bottom() - 8))

        # ── 3. Press fallboard shadow ────────────────────────────────────────
        if key.is_pressed:
            felt_shad = QLinearGradient(0, draw_rect.top(), 0, draw_rect.top() + 12)
            felt_shad.setColorAt(0.0, QColor(80, 20, 0, 200))
            felt_shad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(felt_shad))
            painter.drawRect(QRectF(draw_rect.left() + 1, draw_rect.top() + 1,
                                    draw_rect.width() - 2, 12))

        # ── 4. Top stripe for Split Left Zone ────────────────────────────────
        if is_split_left and not key.is_pressed:
            painter.setPen(Qt.PenStyle.NoPen)
            stripe_grad = QLinearGradient(draw_rect.left(), draw_rect.top(),
                                           draw_rect.right(), draw_rect.top())
            stripe_grad.setColorAt(0.0, QColor("#1A70FF"))
            stripe_grad.setColorAt(1.0, QColor("#0A50C8"))
            painter.setBrush(QBrush(stripe_grad))
            painter.drawRoundedRect(QRectF(draw_rect.left() + 1, draw_rect.top() + 1,
                                           draw_rect.width() - 2, 5), 2, 2)

        # ── 5. Bottom key lip 3D shadow ──────────────────────────────────────
        painter.setPen(Qt.PenStyle.NoPen)
        lip_col = QColor("#C0BAB0") if not key.is_pressed else QColor("#A03000")
        painter.setBrush(QBrush(lip_col))
        painter.drawRoundedRect(
            QRectF(draw_rect.left() + 1, draw_rect.bottom() - 6,
                   draw_rect.width() - 2, 5.5), 2, 2
        )

        # ── 6. Middle C Jewel Badge (C4 = 60) ───────────────────────────────
        if key.note == 60:
            cx = draw_rect.center().x()
            cy = draw_rect.bottom() - 42
            # Glow halo
            glow = QRadialGradient(cx, cy, 6)
            glow.setColorAt(0.0, QColor(255, 170, 0, 160))
            glow.setColorAt(1.0, QColor(255, 170, 0, 0))
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(cx, cy), 6, 6)
            # Gold jewel
            painter.setBrush(QColor("#F59E0B"))
            painter.setPen(QPen(QColor("#D4880A"), 0.5))
            painter.drawEllipse(QPointF(cx, cy), 3.8, 3.8)
            # Specular highlight
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, 240))
            painter.drawEllipse(QPointF(cx - 1.2, cy - 1.2), 1.4, 1.4)

        # ── 7. Computer Keyboard Shortcut Badge ──────────────────────────────
        pc_key = self.PC_KEY_MAP.get(key.note)
        if pc_key and self.show_note_names:
            badge_w = 17
            badge_h = 14
            bx = draw_rect.center().x() - (badge_w / 2.0)
            by = draw_rect.bottom() - 37

            if key.is_pressed:
                # Dark badge on pressed key
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(20, 10, 0, 200))
                painter.drawRoundedRect(QRectF(bx, by, badge_w, badge_h), 3.5, 3.5)
                painter.setPen(QColor("#FFE566"))
            else:
                # Frosted glass badge on normal key
                painter.setPen(Qt.NoPen)
                badge_bg = QLinearGradient(bx, by, bx, by + badge_h)
                badge_bg.setColorAt(0.0, QColor(220, 228, 245, 210))
                badge_bg.setColorAt(1.0, QColor(190, 200, 225, 180))
                painter.setBrush(badge_bg)
                painter.drawRoundedRect(QRectF(bx, by, badge_w, badge_h), 3.5, 3.5)
                # Subtle top highlight
                painter.setPen(QPen(QColor(255, 255, 255, 160), 0.8))
                painter.drawLine(int(bx + 2), int(by + 1), int(bx + badge_w - 2), int(by + 1))
                painter.setPen(QColor("#2A3A5A"))

            font = painter.font()
            font.setPointSize(7)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(bx, by, badge_w, badge_h), Qt.AlignmentFlag.AlignCenter, pc_key)

        # ── 8. Note names at bottom ───────────────────────────────────────────
        if self.show_note_names:
            pitch_idx = key.note % 12
            note_name = NOTE_NAMES[pitch_idx]
            octave = (key.note // 12) - 1
            is_c = (pitch_idx == 0)

            if key.is_pressed:
                painter.setPen(QColor("#FFFFFF"))
            else:
                painter.setPen(QColor("#CC8800" if is_c else "#5A6880"))

            font = painter.font()
            font.setPointSize(8 if is_c else 7)
            font.setBold(is_c)
            painter.setFont(font)
            label = f"C{octave}" if is_c else note_name
            painter.drawText(
                QRectF(draw_rect.left(), draw_rect.bottom() - 20, draw_rect.width(), 17),
                Qt.AlignmentFlag.AlignCenter, label
            )

    def _draw_black_key(self, painter: QPainter, key: PianoKey):
        rect = key.rect
        is_split_left = self.show_split_marker and (key.note <= self.split_point)
        y_depress = 1.8 if key.is_pressed else 0.0
        draw_rect = rect.adjusted(0.6, y_depress, -0.6, 0.0)

        # ── 1. Outer dark body ────────────────────────────────────────────────
        outer_grad = QLinearGradient(0, draw_rect.top(), 0, draw_rect.bottom())
        if key.is_pressed:
            outer_grad.setColorAt(0.0, QColor("#FF9520"))
            outer_grad.setColorAt(0.35, QColor("#E07000"))
            outer_grad.setColorAt(0.8, QColor("#B04400"))
            outer_grad.setColorAt(1.0, QColor("#803000"))
            border_col = QColor("#602000")
        elif key.is_highlighted:
            outer_grad.setColorAt(0.0, QColor("#FFB040"))
            outer_grad.setColorAt(1.0, QColor("#E06000"))
            border_col = QColor("#C04000")
        else:
            outer_grad.setColorAt(0.00, QColor("#22272E"))
            outer_grad.setColorAt(0.60, QColor("#14181E"))
            outer_grad.setColorAt(0.88, QColor("#0C0F14"))
            outer_grad.setColorAt(1.00, QColor("#08090D"))
            border_col = QColor("#040507")

        painter.setPen(QPen(border_col, 1.0))
        painter.setBrush(QBrush(outer_grad))
        painter.drawRoundedRect(draw_rect, 4.0, 4.0)

        # ── 2. Inner glossy sheen face ────────────────────────────────────────
        if not key.is_pressed:
            inner_rect = QRectF(draw_rect.left() + 2, draw_rect.top() + 2,
                                draw_rect.width() - 4, draw_rect.height() * 0.76)
            sheen_grad = QLinearGradient(0, inner_rect.top(), 0, inner_rect.bottom())
            sheen_grad.setColorAt(0.0, QColor("#424C5E"))
            sheen_grad.setColorAt(0.25, QColor("#303848"))
            sheen_grad.setColorAt(0.6, QColor("#222830"))
            sheen_grad.setColorAt(1.0, QColor("#181C24"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(sheen_grad))
            painter.drawRoundedRect(inner_rect, 2.5, 2.5)

            # Left edge reflection line
            left_refl = QLinearGradient(draw_rect.left(), draw_rect.top(),
                                         draw_rect.left(), draw_rect.bottom())
            left_refl.setColorAt(0.0, QColor(255, 255, 255, 0))
            left_refl.setColorAt(0.15, QColor(255, 255, 255, 60))
            left_refl.setColorAt(0.5, QColor(255, 255, 255, 40))
            left_refl.setColorAt(0.85, QColor(255, 255, 255, 20))
            left_refl.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(left_refl), 1.2))
            painter.drawLine(int(draw_rect.left() + 1.5), int(draw_rect.top() + 3),
                             int(draw_rect.left() + 1.5), int(draw_rect.bottom() - 6))

            # Top surface glass highlight
            top_spec = QLinearGradient(draw_rect.left(), draw_rect.top(),
                                        draw_rect.right(), draw_rect.top())
            top_spec.setColorAt(0.0, QColor(255, 255, 255, 0))
            top_spec.setColorAt(0.3, QColor(255, 255, 255, 50))
            top_spec.setColorAt(0.7, QColor(255, 255, 255, 40))
            top_spec.setColorAt(1.0, QColor(255, 255, 255, 0))
            painter.setPen(QPen(QBrush(top_spec), 1.0))
            painter.drawLine(int(draw_rect.left() + 2), int(draw_rect.top() + 2),
                             int(draw_rect.right() - 2), int(draw_rect.top() + 2))

        # ── 3. Press glow halo ────────────────────────────────────────────────
        if key.is_pressed:
            glow_r = QRadialGradient(draw_rect.center().x(), draw_rect.bottom() * 0.6,
                                      draw_rect.width() * 1.2)
            glow_r.setColorAt(0.0, QColor(255, 150, 0, 120))
            glow_r.setColorAt(0.5, QColor(255, 100, 0, 50))
            glow_r.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow_r)
            painter.drawRoundedRect(draw_rect, 4.0, 4.0)

        # ── 4. Split indicator dot ────────────────────────────────────────────
        if is_split_left and not key.is_pressed:
            cx = draw_rect.center().x()
            cy = draw_rect.top() + 7
            glow = QRadialGradient(cx, cy, 5)
            glow.setColorAt(0.0, QColor(100, 200, 255, 180))
            glow.setColorAt(1.0, QColor(0, 150, 255, 0))
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)
            painter.setBrush(QColor("#38B4FF"))
            painter.drawEllipse(QPointF(cx, cy), 2.8, 2.8)

        # ── 5. Computer shortcut badge on black key ───────────────────────────
        pc_key = self.PC_KEY_MAP.get(key.note)
        if pc_key and self.show_note_names:
            badge_w = 14
            badge_h = 12
            bx = draw_rect.center().x() - (badge_w / 2.0)
            by = draw_rect.bottom() - 18
            painter.setPen(Qt.PenStyle.NoPen)
            if key.is_pressed:
                painter.setBrush(QColor(10, 5, 0, 180))
            else:
                painter.setBrush(QColor(255, 255, 255, 50))
            painter.drawRoundedRect(QRectF(bx, by, badge_w, badge_h), 2.5, 2.5)

            font = painter.font()
            font.setPointSize(6)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#FFE566") if key.is_pressed else QColor("#CCD8E8"))
            painter.drawText(QRectF(bx, by, badge_w, badge_h), Qt.AlignmentFlag.AlignCenter, pc_key)

    def _key_at_point(self, point: QPointF) -> Optional[PianoKey]:
        # Check black keys first (since they overlap white keys)
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if k.is_black and k.rect.contains(point):
                return k
        # Check white keys
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if not k.is_black and k.rect.contains(point):
                return k
        return None

    def event(self, ev: QEvent):
        if ev.type() in (
            QEvent.Type.TouchBegin,
            QEvent.Type.TouchUpdate,
            QEvent.Type.TouchEnd,
            QEvent.Type.TouchCancel
        ):
            self._handle_touch_event(ev)
            return True
        return super().event(ev)

    def _handle_touch_event(self, event):
        if event.type() == QEvent.Type.TouchCancel:
            for note in list(self._touch_notes.values()):
                if note in self.keys:
                    self.keys[note].is_pressed = False
                self.note_released.emit(note)
            self._touch_notes.clear()
            self.update()
            return

        for point in event.points():
            pid = point.id()
            state = point.state()
            pos = point.position()

            if state in (QEventPoint.State.Pressed, QEventPoint.State.Updated, QEventPoint.State.Stationary):
                key = self._key_at_point(pos)
                old_note = self._touch_notes.get(pid)
                if key:
                    new_note = key.note
                    if old_note != new_note:
                        if old_note is not None and old_note in self.keys:
                            self.keys[old_note].is_pressed = False
                            self.note_released.emit(old_note)
                        self._touch_notes[pid] = new_note
                        key.is_pressed = True
                        key.highlight_color = QColor(COLOR_ACCENT_ORANGE)
                        norm_y = (pos.y() - key.rect.top()) / max(1.0, key.rect.height())
                        velocity = int(70 + (norm_y * 57))
                        velocity = max(60, min(127, velocity))
                        self.note_pressed.emit(new_note, velocity)
                else:
                    if old_note is not None and old_note in self.keys:
                        self.keys[old_note].is_pressed = False
                        self.note_released.emit(old_note)
                        self._touch_notes.pop(pid, None)
            elif state == QEventPoint.State.Released:
                old_note = self._touch_notes.pop(pid, None)
                if old_note is not None and old_note in self.keys:
                    self.keys[old_note].is_pressed = False
                    self.note_released.emit(old_note)

        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            self.is_mouse_down = True
            pos = event.position()
            key = self._key_at_point(pos)
            if key:
                self.current_mouse_note = key.note
                key.is_pressed = True
                key.highlight_color = QColor(COLOR_ACCENT_ORANGE)

                norm_y = (pos.y() - key.rect.top()) / max(1.0, key.rect.height())
                velocity = int(70 + (norm_y * 57))
                velocity = max(60, min(127, velocity))
                self.note_pressed.emit(key.note, velocity)
                self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_mouse_down:
            pos = event.position()
            key = self._key_at_point(pos)
            if key and key.note != self.current_mouse_note:
                if self.current_mouse_note in self.keys:
                    self.keys[self.current_mouse_note].is_pressed = False
                    self.note_released.emit(self.current_mouse_note)
                self.current_mouse_note = key.note
                key.is_pressed = True
                key.highlight_color = QColor(COLOR_ACCENT_ORANGE)
                norm_y = (pos.y() - key.rect.top()) / max(1.0, key.rect.height())
                velocity = int(70 + (norm_y * 57))
                velocity = max(60, min(127, velocity))
                self.note_pressed.emit(key.note, velocity)
                self.update()
            elif not key and self.current_mouse_note is not None:
                if self.current_mouse_note in self.keys:
                    self.keys[self.current_mouse_note].is_pressed = False
                    self.note_released.emit(self.current_mouse_note)
                self.current_mouse_note = None
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_mouse_down = False
            if self.current_mouse_note in self.keys:
                self.keys[self.current_mouse_note].is_pressed = False
                self.note_released.emit(self.current_mouse_note)
                self.current_mouse_note = None
                self.update()

    def leaveEvent(self, event):
        if self.current_mouse_note in self.keys:
            self.keys[self.current_mouse_note].is_pressed = False
            self.note_released.emit(self.current_mouse_note)
            self.current_mouse_note = None
        self.is_mouse_down = False
        self.update()
        super().leaveEvent(event)
