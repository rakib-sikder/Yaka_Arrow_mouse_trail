# stage2_tracking.py
import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF


class YakaTrail(QWidget):
    MAX_POINTS   = 40
    FADE_SECONDS = 0.35
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
        now = time.monotonic()

        # Global → local coordinates (fixes multi-monitor offset)
        global_pos = self.cursor().pos()
        local_pos  = self.mapFromGlobal(global_pos)
        new_pt     = QPointF(float(local_pos.x()), float(local_pos.y()))

        # Only store if cursor moved
        if not self.points or self.points[-1][0] != new_pt:
            self.points.append((new_pt, now))

        # Evict old points
        cutoff = now - self.FADE_SECONDS
        self.points = [p for p in self.points if p[1] >= cutoff]
        if len(self.points) > self.MAX_POINTS:
            self.points = self.points[-self.MAX_POINTS:]

        # Verify in console
        print(f"tracking {len(self.points)} points | tip → {new_pt.x():.0f}, {new_pt.y():.0f}")


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    trail = YakaTrail()
    sys.exit(app.exec())