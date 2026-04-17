# stage1_window.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt


class YakaTrail(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowTransparentForInput,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)

        # Span all monitors
        virtual = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(virtual)
        self.show()


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    trail = YakaTrail()
    sys.exit(app.exec())