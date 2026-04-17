import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
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

    def paintEvent(self, event):
        if len(self.points) < 2:
            return

        now     = time.monotonic()
        r, g, b = self.TRAIL_COLOR
        n       = len(self.points)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for i in range(1, n):
            pos_ratio = i / (n - 1)
            age       = now - self.points[i][1]
            age_ratio = max(0.0, 1.0 - age / self.FADE_SECONDS)
            alpha     = int(age_ratio * pos_ratio * 220)
            width     = pos_ratio * age_ratio * self.MAX_WIDTH

            if alpha < 4 or width < 0.3:
                continue

            pen = QPen(
                QColor(r, g, b, alpha), width,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
            painter.setPen(pen)
            painter.drawLine(self.points[i-1][0], self.points[i][0])


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    trail = YakaTrail()
    sys.exit(app.exec())