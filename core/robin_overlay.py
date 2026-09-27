from __future__ import annotations

import math
import time
from PyQt6.QtCore import QPoint, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class RobinOverlay(QWidget):
    """Small always-on-top Robin-style desktop companion.

    The character is drawn locally so the assistant has no mandatory external
    art download. The art layer is isolated from the assistant logic and can
    later be replaced by sprite/Live2D assets without touching the core.
    """

    confirmed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFixedSize(230, 285)

        self.state = "SLEEPING"
        self._phase = 0.0
        self._drag_origin: QPoint | None = None
        self._message = ""
        self._confirm_box = None
        self._last_click = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

        self._place_bottom_right()

    def _place_bottom_right(self):
        screen = self.screen()
        if screen:
            g = screen.availableGeometry()
            self.move(g.right() - self.width() - 24, g.bottom() - self.height() - 24)

    def showEvent(self, e):
        self._place_bottom_right()
        super().showEvent(e)

    def set_state(self, state: str):
        self.state = (state or "SLEEPING").upper()
        self.update()

    def set_message(self, text: str):
        self._message = " ".join(str(text).split())[:180]
        self.update()

    def show_confirmation(self, title: str, detail: str):
        self._confirm_box = (str(title)[:90], str(detail)[:220])
        self.update()

    def hide_confirmation(self):
        self._confirm_box = None
        self.update()

    def _tick(self):
        self._phase = (self._phase + 0.055) % (math.tau * 10)
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._last_click = time.monotonic()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._drag_origin is not None and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_origin)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self._drag_origin = None
        super().mouseReleaseEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Soft halo
        glow = QColor(80, 45, 160, 42 if self.state == "SLEEPING" else 72)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(QRectF(16, 8, w - 32, h - 30))

        # Character body
        cx = w / 2
        bob = math.sin(self._phase) * (1.7 if self.state != "SLEEPING" else 0.7)
        cy = 118 + bob

        # Long dark hair
        hair = QPainterPath()
        hair.moveTo(cx - 64, cy - 46)
        hair.cubicTo(cx - 84, cy - 15, cx - 82, cy + 65, cx - 48, cy + 103)
        hair.cubicTo(cx - 31, cy + 88, cx - 23, cy + 52, cx - 27, cy + 8)
        hair.cubicTo(cx - 18, cy - 38, cx - 37, cy - 59, cx - 64, cy - 46)
        hair.moveTo(cx + 64, cy - 46)
        hair.cubicTo(cx + 84, cy - 15, cx + 82, cy + 65, cx + 48, cy + 103)
        hair.cubicTo(cx + 31, cy + 88, cx + 23, cy + 52, cx + 27, cy + 8)
        hair.cubicTo(cx + 18, cy - 38, cx + 37, cy - 59, cx + 64, cy - 46)
        p.setBrush(QColor(20, 18, 30, 245))
        p.setPen(QPen(QColor(100, 70, 150, 180), 1.5))
        p.drawPath(hair)

        # Face
        p.setBrush(QColor(246, 214, 201, 255))
        p.setPen(QPen(QColor(75, 42, 65, 220), 1.0))
        p.drawEllipse(QRectF(cx - 43, cy - 55, 86, 92))

        # Hair fringe
        fringe = QPainterPath()
        fringe.moveTo(cx - 46, cy - 43)
        fringe.cubicTo(cx - 18, cy - 71, cx + 10, cy - 67, cx + 45, cy - 41)
        fringe.cubicTo(cx + 28, cy - 27, cx + 13, cy - 39, cx, cy - 27)
        fringe.cubicTo(cx - 15, cy - 13, cx - 30, cy - 20, cx - 46, cy - 43)
        p.setBrush(QColor(18, 17, 28, 255))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(fringe)

        # Eyes
        blink = math.sin(self._phase * 0.55) > 0.995
        eye_y = cy - 12
        p.setPen(QPen(QColor(36, 25, 55, 255), 2))
        if blink:
            p.drawLine(QPoint(int(cx - 27), int(eye_y)), QPoint(int(cx - 11), int(eye_y)))
            p.drawLine(QPoint(int(cx + 11), int(eye_y)), QPoint(int(cx + 27), int(eye_y)))
        else:
            p.setBrush(QColor(65, 100, 145, 255))
            p.drawEllipse(QRectF(cx - 29, eye_y - 5, 16, 11))
            p.drawEllipse(QRectF(cx + 13, eye_y - 5, 16, 11))
            p.setBrush(QColor(20, 15, 35, 255))
            p.drawEllipse(QRectF(cx - 25, eye_y - 2, 7, 7))
            p.drawEllipse(QRectF(cx + 17, eye_y - 2, 7, 7))

        # Nose + mouth animation
        p.setPen(QPen(QColor(130, 76, 95, 220), 1))
        p.drawLine(QPoint(int(cx), int(cy + 2)), QPoint(int(cx - 2), int(cy + 9)))
        mouth_open = self.state in ("SPEAKING", "THINKING") and math.sin(self._phase * 2.8) > 0.1
        p.setBrush(QColor(115, 38, 60, 220) if mouth_open else Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - 8, cy + 16, 16, 5 if mouth_open else 2))

        # Outfit / shoulders
        body = QPainterPath()
        body.moveTo(cx - 62, cy + 82)
        body.cubicTo(cx - 50, cy + 49, cx - 32, cy + 42, cx, cy + 46)
        body.cubicTo(cx + 32, cy + 42, cx + 50, cy + 49, cx + 62, cy + 82)
        body.lineTo(cx + 70, h - 20)
        body.lineTo(cx - 70, h - 20)
        body.closeSubpath()
        p.setBrush(QColor(54, 31, 74, 248))
        p.setPen(QPen(QColor(117, 75, 160, 220), 1.5))
        p.drawPath(body)

        # State ring
        ring_col = {
            "LISTENING": QColor(90, 210, 255, 220),
            "THINKING": QColor(190, 125, 255, 230),
            "SPEAKING": QColor(255, 135, 205, 230),
            "SLEEPING": QColor(120, 100, 155, 120),
        }.get(self.state, QColor(160, 120, 210, 180))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(ring_col, 2.5))
        p.drawEllipse(QRectF(8, 4, w - 16, h - 8))

        # Status label
        p.setPen(QColor(235, 220, 250, 235))
        p.setFont(p.font())
        p.drawText(QRectF(0, h - 24, w, 18), Qt.AlignmentFlag.AlignCenter, "ROBIN")

        if self._message:
            p.setPen(QColor(235, 235, 245, 235))
            p.setFont(p.font())
            p.drawText(QRectF(10, 6, w - 20, 32),
                       Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.TextWordWrap,
                       self._message)

        if self._confirm_box:
            self._paint_confirm(p)

    def _paint_confirm(self, p: QPainter):
        title, detail = self._confirm_box
        x, y, ww, hh = 8, 38, self.width() - 16, 150
        p.setBrush(QColor(20, 8, 28, 248))
        p.setPen(QPen(QColor(255, 170, 80, 240), 1.5))
        p.drawRoundedRect(QRectF(x, y, ww, hh), 12, 12)
        p.setPen(QColor(255, 230, 205, 255))
        p.drawText(QRectF(x + 12, y + 10, ww - 24, 24),
                   Qt.AlignmentFlag.AlignLeft, "CONFIRM")
        p.setPen(QColor(245, 220, 235, 235))
        p.drawText(QRectF(x + 12, y + 35, ww - 24, 34),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.TextWordWrap, title)
        p.setPen(QColor(220, 205, 225, 220))
        p.drawText(QRectF(x + 12, y + 66, ww - 24, 38),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.TextWordWrap, detail)
        p.setBrush(QColor(65, 145, 100, 230))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(x + 18, y + 112, 82, 26), 8, 8)
        p.setBrush(QColor(145, 55, 75, 230))
        p.drawRoundedRect(QRectF(x + 112, y + 112, 82, 26), 8, 8)
        p.setPen(QColor(255, 255, 255, 245))
        p.drawText(QRectF(x + 18, y + 112, 82, 26), Qt.AlignmentFlag.AlignCenter, "YES")
        p.drawText(QRectF(x + 112, y + 112, 82, 26), Qt.AlignmentFlag.AlignCenter, "NO")

    def mouseDoubleClickEvent(self, e):
        if self._confirm_box and e.button() == Qt.MouseButton.LeftButton:
            pos = e.position()
            if 45 <= pos.y() <= 205:
                if pos.x() < self.width() / 2:
                    self._confirm_box = None
                    self.confirmed.emit(True)
                else:
                    self._confirm_box = None
                    self.confirmed.emit(False)
                self.update()
                return
        super().mouseDoubleClickEvent(e)
