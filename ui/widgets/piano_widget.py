"""
KIYA Piano Studio Pro - Professional 61-Key Virtual Piano Keyboard Widget
Implements realistic white and black key rendering, glissando dragging,
velocity-sensitive clicking, octave labels, split point indicator, and scale highlighting.
"""

from typing import Dict, Set, Optional, List
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QMouseEvent, QEventPoint, QTouchEvent
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
    """61-key interactive virtual piano keyboard widget."""

    note_pressed = Signal(int, int)   # note, velocity
    note_released = Signal(int)       # note

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setMinimumHeight(130)

        self.min_note = KEYBOARD_MIN_NOTE  # 36 (C2)
        self.max_note = KEYBOARD_MAX_NOTE  # 96 (C7) - 61 keys total

        self.split_point = DEFAULT_SPLIT_POINT # 54 (F#3)
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

        # Count total white keys
        white_notes = [n for n in range(self.min_note, self.max_note + 1) if not self.keys[n].is_black]
        num_white = len(white_notes)
        if num_white == 0:
            return

        white_key_width = width / num_white
        black_key_width = white_key_width * 0.62
        black_key_height = height * 0.64

        # 1. Layout white keys
        white_idx = 0
        white_x_positions: Dict[int, float] = {}
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if not k.is_black:
                x = white_idx * white_key_width
                white_x_positions[n] = x
                k.rect = QRectF(x, 0.0, white_key_width, height)
                white_idx += 1

        # 2. Layout black keys centered on the boundary between corresponding white keys
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if k.is_black:
                # White key immediately below this black key
                prev_white_n = n - 1
                if prev_white_n in white_x_positions:
                    prev_x = white_x_positions[prev_white_n]
                    # Center black key over boundary between prev white key and next white key
                    x = prev_x + white_key_width - (black_key_width * 0.5)
                    k.rect = QRectF(x, 0.0, black_key_width, black_key_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        height = self.height()

        # 1. Draw White Keys
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if not k.is_black:
                self._draw_white_key(painter, k)

        # 2. Draw Black Keys (Rendered on top)
        for n in range(self.min_note, self.max_note + 1):
            k = self.keys[n]
            if k.is_black:
                self._draw_black_key(painter, k)

        # 3. Draw Split Point Marker Line if active
        if self.show_split_marker and self.split_point in self.keys:
            sp_key = self.keys[self.split_point]
            split_x = sp_key.rect.right()
            painter.setPen(QPen(QColor(COLOR_ACCENT_BLUE), 3.0, Qt.PenStyle.DashLine))
            painter.drawLine(int(split_x), 0, int(split_x), int(height))

            # Split label badge
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(COLOR_ACCENT_BLUE))
            painter.drawRoundedRect(QRectF(split_x - 30, 4, 60, 18), 4, 4)
            painter.setPen(QColor("#101216"))
            font = painter.font()
            font.setPointSize(8)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QRectF(split_x - 30, 4, 60, 18), Qt.AlignmentFlag.AlignCenter, "SPLIT")

    PC_KEY_MAP = {
        48: 'Z', 49: 'S', 50: 'X', 51: 'D', 52: 'C', 53: 'V', 54: 'G', 55: 'B', 56: 'H', 57: 'N', 58: 'J', 59: 'M',
        60: 'Q', 61: '2', 62: 'W', 63: '3', 64: 'E', 65: 'R', 66: '5', 67: 'T', 68: '6', 69: 'Y', 70: '7', 71: 'U',
        72: 'I', 73: '9', 74: 'O', 75: '0', 76: 'P'
    }

    def _draw_white_key(self, painter: QPainter, key: PianoKey):
        rect = key.rect
        is_split_left = self.show_split_marker and (key.note <= self.split_point)

        # 1. Key Body Gradient & Geometry (depressed vertically when pressed)
        y_depress = 2.0 if key.is_pressed else 0.0
        draw_rect = rect.adjusted(0.5, y_depress, -0.5, 0.0)

        grad = QLinearGradient(0, draw_rect.top(), 0, draw_rect.bottom())
        if key.is_pressed:
            grad.setColorAt(0.0, QColor("#FFE082"))
            grad.setColorAt(0.3, QColor("#FFB300"))
            grad.setColorAt(0.8, QColor("#FF8F00"))
            grad.setColorAt(1.0, QColor("#E65100"))
            border_col = QColor("#BF360C")
        elif key.is_highlighted:
            grad.setColorAt(0.0, QColor("#FFF8E1"))
            grad.setColorAt(1.0, QColor("#FFE082"))
            border_col = QColor(COLOR_ACCENT_ORANGE)
        elif is_split_left:
            grad.setColorAt(0.0, QColor("#F0F6FF"))
            grad.setColorAt(0.85, QColor("#E0ECF8"))
            grad.setColorAt(1.0, QColor("#D0E0F0"))
            border_col = QColor("#6B9FD4")
        else:
            # Pristine warm acoustic ivory gradient
            grad.setColorAt(0.0, QColor("#FFFFFF"))
            grad.setColorAt(0.65, QColor("#FAF9F5"))
            grad.setColorAt(0.90, QColor("#F2EFE8"))
            grad.setColorAt(1.0, QColor("#E2DCD2"))
            border_col = QColor("#B0B8C4")

        painter.setPen(QPen(border_col, 1.0))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(draw_rect, 3.0, 3.0)

        # 2. 1px Left White Bevel & 1px Right Soft Shadow for physical 3D separation
        if not key.is_pressed:
            painter.setPen(QPen(QColor(255, 255, 255, 220), 1.0))
            painter.drawLine(int(draw_rect.left() + 1), int(draw_rect.top() + 4),
                             int(draw_rect.left() + 1), int(draw_rect.bottom() - 6))
            painter.setPen(QPen(QColor(150, 160, 175, 75), 1.0))
            painter.drawLine(int(draw_rect.right() - 1), int(draw_rect.top() + 4),
                             int(draw_rect.right() - 1), int(draw_rect.bottom() - 6))

        # 3. Top Fallboard Felt Shadow when pressed down
        if key.is_pressed:
            felt_shad = QLinearGradient(0, draw_rect.top(), 0, draw_rect.top() + 8)
            felt_shad.setColorAt(0.0, QColor(70, 15, 0, 180))
            felt_shad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(felt_shad))
            painter.drawRect(QRectF(draw_rect.left() + 1, draw_rect.top() + 1, draw_rect.width() - 2, 8))

        # 4. Top indicator strip for Split Left Zone
        if is_split_left and not key.is_pressed:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#2563EB"))
            painter.drawRoundedRect(QRectF(draw_rect.left() + 1, draw_rect.top() + 1, draw_rect.width() - 2, 4), 2, 2)

        # 5. Bottom lip 3D depth shadow
        painter.setPen(Qt.PenStyle.NoPen)
        lip_col = QColor("#C2BCB0") if not key.is_pressed else QColor("#B73600")
        painter.setBrush(QBrush(lip_col))
        painter.drawRoundedRect(QRectF(draw_rect.left() + 1, draw_rect.bottom() - 5, draw_rect.width() - 2, 4.5), 2, 2)

        # 6. Middle C Indicator jewel badge (C4 = 60)
        if key.note == 60:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#F59E0B"))
            mc_y = draw_rect.bottom() - 40
            painter.drawEllipse(QPointF(draw_rect.center().x(), mc_y), 3.5, 3.5)
            painter.setBrush(QColor(255, 255, 255, 220))
            painter.drawEllipse(QPointF(draw_rect.center().x() - 1, mc_y - 1), 1.2, 1.2)

        # 7. Computer Keyboard Key Shortcut Badge (Clean, subtle, integrated pill)
        pc_key = self.PC_KEY_MAP.get(key.note)
        if pc_key and self.show_note_names:
            badge_w = 16
            badge_h = 13
            bx = draw_rect.center().x() - (badge_w / 2.0)
            by = draw_rect.bottom() - 34

            painter.setPen(Qt.PenStyle.NoPen)
            if key.is_pressed:
                painter.setBrush(QColor(0, 0, 0, 160))
                text_col = QColor("#FFFFFF")
            else:
                painter.setBrush(QColor(220, 225, 235, 180))
                text_col = QColor("#334155")
            painter.drawRoundedRect(QRectF(bx, by, badge_w, badge_h), 3, 3)

            font = painter.font()
            font.setPointSize(7)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(text_col)
            painter.drawText(QRectF(bx, by, badge_w, badge_h), Qt.AlignmentFlag.AlignCenter, pc_key)

        # 8. Note Names & Octave Labels at bottom
        if self.show_note_names:
            pitch_idx = key.note % 12
            note_name = NOTE_NAMES[pitch_idx]
            octave = (key.note // 12) - 1
            is_c = (pitch_idx == 0)

            if key.is_pressed:
                painter.setPen(QColor("#FFFFFF"))
            else:
                painter.setPen(QColor("#D97706" if is_c else "#64748B"))

            font = painter.font()
            font.setPointSize(8 if is_c else 7)
            font.setBold(is_c)
            painter.setFont(font)
            label = f"C{octave}" if is_c else note_name
            painter.drawText(QRectF(draw_rect.left(), draw_rect.bottom() - 19, draw_rect.width(), 16),
                             Qt.AlignmentFlag.AlignCenter, label)

    def _draw_black_key(self, painter: QPainter, key: PianoKey):
        rect = key.rect
        is_split_left = self.show_split_marker and (key.note <= self.split_point)
        y_depress = 1.5 if key.is_pressed else 0.0
        draw_rect = rect.adjusted(0.5, y_depress, -0.5, 0.0)

        # 1. Black key gradient body
        grad = QLinearGradient(0, draw_rect.top(), 0, draw_rect.bottom())
        if key.is_pressed:
            grad.setColorAt(0.0, QColor("#FFA726"))
            grad.setColorAt(0.4, QColor("#FB8C00"))
            grad.setColorAt(1.0, QColor("#D84315"))
            border_col = QColor("#BF360C")
        elif key.is_highlighted:
            grad.setColorAt(0.0, QColor("#FFB74D"))
            grad.setColorAt(1.0, QColor("#F57C00"))
            border_col = QColor("#E65100")
        else:
            grad.setColorAt(0.0, QColor("#2A2D35"))
            grad.setColorAt(0.65, QColor("#181A20"))
            grad.setColorAt(1.0, QColor("#0D0E12"))
            border_col = QColor("#050608")

        painter.setPen(QPen(border_col, 1.0))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(draw_rect, 3.0, 3.0)

        # 2. Top and Left Highlight Sheen
        if not key.is_pressed:
            sheen_rect = QRectF(draw_rect.left() + 1.5, draw_rect.top() + 1.5, draw_rect.width() - 3.0, draw_rect.height() - 8.0)
            sheen_grad = QLinearGradient(0, sheen_rect.top(), 0, sheen_rect.bottom())
            sheen_grad.setColorAt(0.0, QColor("#444B5A"))
            sheen_grad.setColorAt(1.0, QColor("#1C1F26"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(sheen_grad))
            painter.drawRoundedRect(sheen_rect, 2.0, 2.0)

            # Left 1px subtle edge reflection
            painter.setPen(QPen(QColor(255, 255, 255, 35), 1.0))
            painter.drawLine(int(draw_rect.left() + 1), int(draw_rect.top() + 2),
                             int(draw_rect.left() + 1), int(draw_rect.bottom() - 4))

        # 3. Split Left Dot Indicator
        if is_split_left and not key.is_pressed:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#38BDF8"))
            painter.drawEllipse(QPointF(draw_rect.center().x(), draw_rect.top() + 6), 2.5, 2.5)

        # 4. Computer Keyboard Key Shortcut on Black Key
        pc_key = self.PC_KEY_MAP.get(key.note)
        if pc_key and self.show_note_names:
            badge_w = 14
            badge_h = 12
            bx = draw_rect.center().x() - (badge_w / 2.0)
            by = draw_rect.bottom() - 16
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 40) if not key.is_pressed else QColor("#0A0B0E"))
            painter.drawRoundedRect(QRectF(bx, by, badge_w, badge_h), 2, 2)

            font = painter.font()
            font.setPointSize(6)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#E2E8F0"))
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

                # Velocity based on click Y position (lower on key = louder)
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
                # Glissando / drag across keys
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
                # Dragged outside keys
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
        """Clean up when mouse leaves keyboard area to prevent stuck notes."""
        if self.current_mouse_note in self.keys:
            self.keys[self.current_mouse_note].is_pressed = False
            self.note_released.emit(self.current_mouse_note)
            self.current_mouse_note = None
        self.is_mouse_down = False
        self.update()
        super().leaveEvent(event)
