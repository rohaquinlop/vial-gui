#!/usr/bin/env python3
"""Floating always-on-top HUD showing the key assignments of a .vil layout file.

Usage:
    uv run python layout_overlay.py [path/to/config.vil]

Defaults to corne-v4-config-dvorak.vil in this repo. Click a layer tab (or the
number keys 1-4 while it has focus) to switch layers, drag anywhere on the
background to reposition, click the x to close.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src" / "main" / "python"))

from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QColor, QFont, QPainter
from PyQt5.QtWidgets import QApplication, QWidget

from keycodes.keycodes import Keycode

CUSTOM_LABELS = {
    "FN_MO13": "Fn1+3",
    "FN_MO23": "Fn2+3",
    "ALL_T(KC_SPACE)": "Space*",
}
MASK_PREFIX = {"LSFT": "⇧", "LCTL": "⌃", "LALT": "⌥", "LGUI": "⌘"}
MASK_PATTERN = re.compile(r"^([A-Z_]+)\((.+)\)$")

LAYER_NAMES = ["Dvorak", "Numbers", "Symbols", "Function"]

KEY_SIZE = 40
KEY_GAP = 5
ROW_GAP = 5
HALF_GAP = 24
TAB_HEIGHT = 24
PADDING = 12
COLS_PER_HALF = 7
ROWS_PER_HALF = 4


def label_for(code):
    if code == -1 or code is None:
        return None
    if code in CUSTOM_LABELS:
        return CUSTOM_LABELS[code]
    m = MASK_PATTERN.match(code)
    if m and m.group(1) in MASK_PREFIX:
        inner = label_for(m.group(2))
        return MASK_PREFIX[m.group(1)] + (inner or "")
    return Keycode.label(code)


class LayoutOverlay(QWidget):

    def __init__(self, vil_path):
        super().__init__()
        self.layers = json.loads(Path(vil_path).read_text())["layout"]
        self.layer = 0
        self.drag_offset = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowOpacity(0.88)

        half_w = COLS_PER_HALF * (KEY_SIZE + KEY_GAP) - KEY_GAP
        width = PADDING * 2 + half_w * 2 + HALF_GAP
        height = PADDING * 2 + TAB_HEIGHT + 6 + ROWS_PER_HALF * (KEY_SIZE + ROW_GAP) - ROW_GAP
        self.resize(width, height)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - width - 20, screen.top() + 40)

        self.close_rect = QRect(width - PADDING - 18, 6, 18, 18)

    def rows_for_layer(self):
        layer = self.layers[self.layer]
        return layer[0:4], layer[4:8]

    def tab_rect(self, idx):
        tab_w = (self.width() - 2 * PADDING) / len(LAYER_NAMES)
        return QRect(int(PADDING + idx * tab_w), PADDING, int(tab_w) - 4, TAB_HEIGHT - 4)

    def mousePressEvent(self, ev):
        if self.close_rect.contains(ev.pos()):
            self.close()
            return
        for idx in range(len(LAYER_NAMES)):
            if self.tab_rect(idx).contains(ev.pos()):
                self.layer = idx
                self.update()
                return
        self.drag_offset = ev.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, ev):
        if self.drag_offset is not None and ev.buttons() & Qt.LeftButton:
            self.move(ev.globalPos() - self.drag_offset)

    def mouseReleaseEvent(self, ev):
        self.drag_offset = None

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Escape:
            self.close()
        elif Qt.Key_1 <= ev.key() <= Qt.Key_1 + len(LAYER_NAMES) - 1:
            self.layer = ev.key() - Qt.Key_1
            self.update()

    def draw_key(self, qp, x, y, code):
        text = label_for(code)
        if text is None:
            return
        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(250, 250, 252, 235))
        qp.drawRoundedRect(int(x), int(y), KEY_SIZE, KEY_SIZE, 7, 7)
        qp.setPen(QColor(20, 20, 24, 240))
        qp.drawText(QRect(int(x), int(y), KEY_SIZE, KEY_SIZE), Qt.AlignCenter, text)

    def draw_row(self, qp, cells, x0, row_idx, reverse):
        y = PADDING + TAB_HEIGHT + 6 + row_idx * (KEY_SIZE + ROW_GAP)
        ordered = list(reversed(cells)) if reverse else cells
        x = x0
        for code in ordered:
            if code != -1:
                self.draw_key(qp, x, y, code)
            x += KEY_SIZE + KEY_GAP

    def paintEvent(self, ev):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)

        qp.setPen(Qt.NoPen)
        qp.setBrush(QColor(18, 18, 22, 215))
        qp.drawRoundedRect(self.rect(), 14, 14)

        qp.setFont(QFont("Menlo", 10))
        for idx, name in enumerate(LAYER_NAMES):
            rect = self.tab_rect(idx)
            active = idx == self.layer
            qp.setPen(Qt.NoPen)
            qp.setBrush(QColor(90, 140, 255, 200) if active else QColor(255, 255, 255, 18))
            qp.drawRoundedRect(rect, 5, 5)
            qp.setPen(QColor(255, 255, 255, 235 if active else 120))
            qp.drawText(rect, Qt.AlignCenter, name)

        qp.setPen(QColor(255, 255, 255, 150))
        qp.drawText(self.close_rect, Qt.AlignCenter, "✕")

        left_rows, right_rows = self.rows_for_layer()
        half_w = COLS_PER_HALF * (KEY_SIZE + KEY_GAP) - KEY_GAP
        right_x0 = PADDING + half_w + HALF_GAP

        qp.setFont(QFont("Menlo", 9))
        for r in range(ROWS_PER_HALF):
            self.draw_row(qp, left_rows[r], PADDING, r, reverse=False)
            self.draw_row(qp, right_rows[r], right_x0, r, reverse=True)


def main():
    vil_path = sys.argv[1] if len(sys.argv) > 1 else str(REPO_ROOT / "corne-v4-config-dvorak.vil")
    app = QApplication(sys.argv)
    overlay = LayoutOverlay(vil_path)
    overlay.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
