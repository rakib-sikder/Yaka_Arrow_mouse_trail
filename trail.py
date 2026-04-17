# stage4_final.py
import sys
import time
import math
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer, QPointF


class YakaTrail(QWidget):
    TRAIL_COLOR  = (100, 180, 255)
    MAX_POINTS   = 40
    FADE_SECONDS = 0.35
    MAX_WIDTH    = 6.0
    TICK_MS      = 8

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)

        virtual = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(virtual)
        self.show()

        self.points: list[tuple[QPointF, float]] = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(self.TICK_MS)

    def _tick(self):
        now        = time.monotonic()
        global_pos = self.cursor().pos()
        local_pos  = self.mapFromGlobal(global_pos)
        new_pt     = QPointF(float(local_pos.x()), float(local_pos.y()))

        if not self.points or self.points[-1][0] != new_pt:
            self.points.append((new_pt, now))

        cutoff = now - self.FADE_SECONDS
        self.points = [p for p in self.points if p[1] >= cutoff]
        if len(self.points) > self.MAX_POINTS:
            self.points = self.points[-self.MAX_POINTS:]

        self.update()

    def _smooth_points(self) -> list[QPointF]:
        pts = [p[0] for p in self.points]
        if len(pts) < 2:
            return pts

        smooth = []
        for i in range(len(pts) - 1):
            p0 = pts[max(i - 1, 0)]
            p1 = pts[i]
            p2 = pts[min(i + 1, len(pts) - 1)]
            p3 = pts[min(i + 2, len(pts) - 1)]

            for t_step in range(8):
                t  = t_step / 8.0
                t2 = t * t
                t3 = t2 * t
                x  = 0.5 * ((2*p1.x()) +
                             (-p0.x() + p2.x()) * t +
                             (2*p0.x() - 5*p1.x() + 4*p2.x() - p3.x()) * t2 +
                             (-p0.x() + 3*p1.x() - 3*p2.x() + p3.x()) * t3)
                y  = 0.5 * ((2*p1.y()) +
                             (-p0.y() + p2.y()) * t +
                             (2*p0.y() - 5*p1.y() + 4*p2.y() - p3.y()) * t2 +
                             (-p0.y() + 3*p1.y() - 3*p2.y() + p3.y()) * t3)
                smooth.append(QPointF(x, y))

        smooth.append(pts[-1])
        return smooth

    def paintEvent(self, event):
        if len(self.points) < 2:
            return

        now     = time.monotonic()
        r, g, b = self.TRAIL_COLOR
        smooth  = self._smooth_points()
        n       = len(smooth)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        left_pts:  list[QPointF] = []
        right_pts: list[QPointF] = []

        for i, pt in enumerate(smooth):
            pos_ratio = i / (n - 1)
            half_w    = (pos_ratio * self.MAX_WIDTH) / 2.0

            if i == 0:
                dx = smooth[1].x() - pt.x()
                dy = smooth[1].y() - pt.y()
            elif i == n - 1:
                dx = pt.x() - smooth[-2].x()
                dy = pt.y() - smooth[-2].y()
            else:
                dx = smooth[i+1].x() - smooth[i-1].x()
                dy = smooth[i+1].y() - smooth[i-1].y()

            length = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / length, dx / length

            left_pts.append( QPointF(pt.x() + nx * half_w, pt.y() + ny * half_w))
            right_pts.append(QPointF(pt.x() - nx * half_w, pt.y() - ny * half_w))

        chunk = max(1, n // 20)
        for start in range(0, n - 1, chunk):
            end       = min(start + chunk + 1, n)
            pos_ratio = start / (n - 1)

            raw_idx   = int(pos_ratio * (len(self.points) - 1))
            age       = now - self.points[raw_idx][1]
            age_ratio = max(0.0, 1.0 - age / self.FADE_SECONDS)
            alpha     = int(age_ratio * pos_ratio * 220)

            if alpha < 4:
                continue

            poly_pts = left_pts[start:end] + list(reversed(right_pts[start:end]))

            path = QPainterPath()
            path.moveTo(poly_pts[0])
            for p in poly_pts[1:]:
                path.lineTo(p)
            path.closeSubpath()

            painter.setBrush(QBrush(QColor(r, g, b, alpha)))
            painter.drawPath(path)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    trail = YakaTrail()
    sys.exit(app.exec())