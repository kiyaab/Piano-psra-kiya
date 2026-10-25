"""
KIYA Piano Studio Pro - Interactive Piano Roll Editor Widget
Renders pitch and time grid, notes with velocity coloration,
and provides interactive note creation, dragging, resizing, and quantization.
"""

from dataclasses import dataclass
from typing import List, Optional, Callable
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QMouseEvent, QWheelEvent
from app.constants import (
    COLOR_BG,
    COLOR_PANEL_MAIN,
    COLOR_PANEL_SECONDARY,
    COLOR_BORDER,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_BLUE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    NOTE_NAMES,
    midi_to_note_name
)

@dataclass
class PianoRollNote:
    note: int          # MIDI Note (0-127)
    start_tick: int    # Start tick
    duration: int      # Duration in ticks
    velocity: int = 100
    channel: int = 0
    selected: bool = False

class PianoRollWidget(QWidget):
    """Interactive Piano Roll Editor widget."""

    note_clicked = Signal(int, int) # note, velocity for preview
    notes_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

        # Note list
        self.notes: List[PianoRollNote] = []

        # Grid view parameters
        self.ppq = 96               # Ticks per beat
        self.min_pitch = 36         # C2
        self.max_pitch = 84         # C6
        self.total_bars = 8
        self.pixels_per_tick = 0.25 # Horizontal zoom
        self.row_height = 18.0      # Vertical pitch row height
        self.ruler_width = 54.0     # Left piano key ruler width
        self.header_height = 28.0   # Top timeline ruler height

        # Editing state
        self.selected_note: Optional[PianoRollNote] = None
        self.is_dragging = False
        self.is_resizing = False
        self.drag_start_pos = QPointF()
        self.drag_initial_tick = 0
        self.drag_initial_pitch = 0
        self.drag_initial_duration = 0

        # Quantize grid step in ticks (96 = quarter note, 48 = 8th note, 24 = 16th note)
        self.quantize_ticks = 48

        self._populate_demo_notes()

    def _populate_demo_notes(self):
        """Populate initial melody phrase."""
        demo_chords = [
            (60, 0, 96, 95), (64, 0, 96, 90), (67, 0, 96, 92), # C Major
            (62, 96, 96, 90), (65, 96, 96, 88), (69, 96, 96, 85), # D Minor
            (64, 192, 96, 92), (67, 192, 96, 90), (71, 192, 96, 90), # E Minor
            (65, 288, 96, 95), (69, 288, 96, 95), (72, 288, 96, 95), # F Major
        ]
        for note, tick, dur, vel in demo_chords:
            self.notes.append(PianoRollNote(note=note, start_tick=tick, duration=dur, velocity=vel))

    def set_notes(self, notes: List[PianoRollNote]):
        self.notes = notes
        self.update()

    def quantize_all(self):
        """Quantize all note start times and durations to current grid step."""
        for n in self.notes:
            n.start_tick = round(n.start_tick / self.quantize_ticks) * self.quantize_ticks
            n.duration = max(self.quantize_ticks, round(n.duration / self.quantize_ticks) * self.quantize_ticks)
        self.notes_changed.emit()
        self.update()

    def clear_all(self):
        self.notes.clear()
        self.selected_note = None
        self.notes_changed.emit()
        self.update()

    def pitch_to_y(self, pitch: int) -> float:
        """Convert MIDI pitch to widget Y position."""
        row_from_top = self.max_pitch - pitch
        return self.header_height + (row_from_top * self.row_height)

    def y_to_pitch(self, y: float) -> int:
        """Convert widget Y position to MIDI pitch."""
        row = (y - self.header_height) / self.row_height
        pitch = int(round(self.max_pitch - row))
        return max(0, min(127, pitch))

    def tick_to_x(self, tick: int) -> float:
        """Convert tick to widget X position."""
        return self.ruler_width + (tick * self.pixels_per_tick)

    def x_to_tick(self, x: float) -> int:
        """Convert widget X position to tick."""
        tick = (x - self.ruler_width) / self.pixels_per_tick
        return max(0, int(round(tick)))

    def note_to_rect(self, note: PianoRollNote) -> QRectF:
        x = self.tick_to_x(note.start_tick)
        y = self.pitch_to_y(note.note)
        w = max(4.0, note.duration * self.pixels_per_tick)
        h = self.row_height - 1.0
        return QRectF(x, y, w, h)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        width = self.width()
        height = self.height()

        # Background
        painter.fillRect(0, 0, width, height, QColor(COLOR_BG))

        # 1. Pitch Grid Rows
        for p in range(self.min_pitch, self.max_pitch + 1):
            y = self.pitch_to_y(p)
            is_black = (p % 12) in (1, 3, 6, 8, 10)
            row_color = QColor(COLOR_PANEL_MAIN) if not is_black else QColor(COLOR_BG)
            painter.fillRect(QRectF(self.ruler_width, y, width - self.ruler_width, self.row_height), row_color)

            # Subtle horizontal separator
            painter.setPen(QColor(COLOR_BORDER))
            painter.drawLine(int(self.ruler_width), int(y + self.row_height), int(width), int(y + self.row_height))

        # 2. Timeline Grid Vertical Columns (Beats & Bars)
        ticks_per_bar = self.ppq * 4
        total_ticks = max(1000, self.total_bars * ticks_per_bar)

        for b in range(0, total_ticks, self.ppq):
            x = self.tick_to_x(b)
            if x > width:
                break
            is_bar = (b % ticks_per_bar == 0)
            pen_color = QColor("#3D485C") if is_bar else QColor("#222833")
            painter.setPen(QPen(pen_color, 1.5 if is_bar else 1.0))
            painter.drawLine(int(x), int(self.header_height), int(x), int(height))

        # 3. Render Notes
        for n in self.notes:
            rect = self.note_to_rect(n)
            # Velocity color interpolation: 60 (blue) to 127 (orange)
            vel_factor = max(0.0, min(1.0, (n.velocity - 40) / 80.0))
            base_col = QColor(COLOR_ACCENT_ORANGE if vel_factor > 0.65 else COLOR_ACCENT_BLUE)
            if n.selected:
                base_col = base_col.lighter(130)

            # Note fill
            painter.fillRect(rect, base_col)
            # Note border
            border_pen = QColor("#FFFFFF") if n.selected else base_col.darker(140)
            painter.setPen(border_pen)
            painter.drawRect(rect)

            # Note pitch label if wide enough
            if rect.width() > 32.0:
                painter.setPen(QColor("#000000" if vel_factor > 0.65 else "#FFFFFF"))
                font = painter.font()
                font.setPointSize(8)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(rect.adjusted(4, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter, midi_to_note_name(n.note))

        # 4. Left Piano Key Ruler
        painter.fillRect(0, 0, int(self.ruler_width), height, QColor(COLOR_PANEL_SECONDARY))
        for p in range(self.min_pitch, self.max_pitch + 1):
            y = self.pitch_to_y(p)
            is_black = (p % 12) in (1, 3, 6, 8, 10)
            key_rect = QRectF(0, y, self.ruler_width - 1, self.row_height)
            painter.fillRect(key_rect, QColor("#14171E") if is_black else QColor("#2B3444"))
            painter.setPen(QColor(COLOR_BORDER))
            painter.drawRect(key_rect)

            # Label C notes
            if p % 12 == 0:
                painter.setPen(QColor(COLOR_ACCENT_ORANGE))
                font = painter.font()
                font.setPointSize(8)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(key_rect.adjusted(6, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter, midi_to_note_name(p))

        # 5. Top Timeline Header Ruler
        painter.fillRect(0, 0, width, int(self.header_height), QColor(COLOR_PANEL_MAIN))
        painter.setPen(QColor(COLOR_BORDER))
        painter.drawLine(0, int(self.header_height), width, int(self.header_height))

        for t in range(0, total_ticks, ticks_per_bar):
            x = self.tick_to_x(t)
            if x > width:
                break
            bar_num = (t // ticks_per_bar) + 1
            painter.setPen(QColor(COLOR_TEXT_PRIMARY))
            font = painter.font()
            font.setPointSize(9)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(int(x + 4), 18, f"Bar {bar_num}")

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position()
        x, y = pos.x(), pos.y()

        # Check left piano key click -> trigger preview
        if x < self.ruler_width and y >= self.header_height:
            pitch = self.y_to_pitch(y)
            self.note_clicked.emit(pitch, 100)
            return

        if y < self.header_height:
            return

        clicked_note = None
        is_edge = False

        for n in reversed(self.notes):
            rect = self.note_to_rect(n)
            if rect.contains(pos):
                clicked_note = n
                # Check right edge for resize
                if pos.x() >= (rect.right() - 8.0):
                    is_edge = True
                break

        if event.button() == Qt.MouseButton.LeftButton:
            if clicked_note:
                for n in self.notes:
                    n.selected = False
                clicked_note.selected = True
                self.selected_note = clicked_note
                self.note_clicked.emit(clicked_note.note, clicked_note.velocity)

                self.drag_start_pos = pos
                self.drag_initial_tick = clicked_note.start_tick
                self.drag_initial_pitch = clicked_note.note
                self.drag_initial_duration = clicked_note.duration

                if is_edge:
                    self.is_resizing = True
                else:
                    self.is_dragging = True
            else:
                # Clicked empty space -> deselect all
                for n in self.notes:
                    n.selected = False
                self.selected_note = None

        elif event.button() == Qt.MouseButton.RightButton:
            if clicked_note:
                self.notes.remove(clicked_note)
                self.selected_note = None
                self.notes_changed.emit()

        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double click empty cell to add note."""
        pos = event.position()
        if pos.x() > self.ruler_width and pos.y() > self.header_height:
            pitch = self.y_to_pitch(pos.y())
            tick = self.x_to_tick(pos.x())
            # Quantize to grid
            q_tick = round(tick / self.quantize_ticks) * self.quantize_ticks
            new_note = PianoRollNote(note=pitch, start_tick=q_tick, duration=self.quantize_ticks, velocity=100)
            self.notes.append(new_note)
            self.note_clicked.emit(pitch, 100)
            self.notes_changed.emit()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        delta_x = pos.x() - self.drag_start_pos.x()
        delta_y = pos.y() - self.drag_start_pos.y()
        delta_ticks = int(delta_x / self.pixels_per_tick)

        if self.is_dragging and self.selected_note:
            new_tick = max(0, self.drag_initial_tick + delta_ticks)
            q_tick = round(new_tick / self.quantize_ticks) * self.quantize_ticks
            new_pitch = self.y_to_pitch(pos.y())

            if self.selected_note.start_tick != q_tick or self.selected_note.note != new_pitch:
                self.selected_note.start_tick = q_tick
                if self.selected_note.note != new_pitch:
                    self.selected_note.note = new_pitch
                    self.note_clicked.emit(new_pitch, self.selected_note.velocity)
                self.notes_changed.emit()
                self.update()

        elif self.is_resizing and self.selected_note:
            new_dur = max(self.quantize_ticks, self.drag_initial_duration + delta_ticks)
            q_dur = round(new_dur / self.quantize_ticks) * self.quantize_ticks
            if self.selected_note.duration != q_dur:
                self.selected_note.duration = q_dur
                self.notes_changed.emit()
                self.update()

        # Update cursor on hover
        if not self.is_dragging and not self.is_resizing:
            hover_edge = False
            for n in self.notes:
                rect = self.note_to_rect(n)
                if rect.contains(pos) and pos.x() >= (rect.right() - 8.0):
                    hover_edge = True
                    break
            self.setCursor(Qt.CursorShape.SizeHorCursor if hover_edge else Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.is_dragging = False
        self.is_resizing = False
        self.update()
