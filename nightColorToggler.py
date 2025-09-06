#!/usr/bin/env python3

import sys
import os
import math
from PyQt5 import QtWidgets, QtGui, QtCore

def is_night_color_active():
    """Check Night Color state using kreadconfig5."""
    try:
        result = os.popen('kreadconfig5 --file kwinrc --group "NightColor" --key "Active"').read().strip()
        return result.lower() == "true"
    except Exception:
        return False

def set_night_color(state: bool):
    """Enable or disable Night Color using kwriteconfig5."""
    value = "true" if state else "false"
    os.system(f'kwriteconfig5 --file ~/.config/kwinrc --group "NightColor" --key "Active" "{value}"')
    os.system("killall -HUP kwin_x11")

class NightColorTray(QtWidgets.QSystemTrayIcon):
    def __init__(self):
        super().__init__()

        self.setToolTip("Night Color Toggle")
        self.menu = QtWidgets.QMenu()
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        self.setContextMenu(self.menu)
        self.activated.connect(self.on_tray_icon_clicked)

        self.update_icon()
        self.show()

        # Optional: periodic check to sync icon with external changes
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_icon)
        self.timer.start(5000)  # every 5 seconds

    def update_icon(self):
        """Update tray icon: crescent moon when Night Color is off, sun when on."""
        active = is_night_color_active()
        size = 64
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        rect = QtCore.QRectF(0, 0, size, size)

        if active:
            # Draw sun
            center = rect.center()
            radius = size * 0.3

            # Draw sun rays
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 165, 0), 4))
            for angle in range(0, 360, 30):  # 12 rays
                line_length = radius + 7
                rad = math.radians(angle)  # convert degrees to radians
                x1 = center.x() + radius * 0.7 * math.cos(rad)
                y1 = center.y() + radius * 0.7 * math.sin(rad)
                x2 = center.x() + line_length * math.cos(rad)
                y2 = center.y() + line_length * math.sin(rad)
                painter.drawLine(QtCore.QPointF(x1, y1), QtCore.QPointF(x2, y2))

            # Draw central circle
            painter.setBrush(QtGui.QColor(255, 165, 0))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(center, radius, radius)

        else:
            # Draw crescent moon
            painter.setBrush(QtGui.QColor(200, 200, 200))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(rect)

            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            offset = size * 0.25
            painter.drawEllipse(QtCore.QRectF(-offset, -offset/2, size, size))

        painter.end()
        self.setIcon(QtGui.QIcon(pixmap))
        self.setToolTip(f"Night Color is {'ON' if active else 'OFF'}")


    def on_tray_icon_clicked(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:  # left-click
            active = is_night_color_active()
            set_night_color(not active)
            self.update_icon()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    tray = NightColorTray()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
