#!/usr/bin/env python3

import sys
import os
import time
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtNetwork import QLocalServer, QLocalSocket


class ShutdownTimer(QtWidgets.QSystemTrayIcon):
    def __init__(self):
        super().__init__()

        self.duration = 60*60  # seconds (1 hour)
        self.interval = 1    # update every second
        self.elapsed = 0

        self.setToolTip("Shutdown Timer")
        self.menu = QtWidgets.QMenu()

        restart_action = self.menu.addAction("Restart Timer")
        restart_action.triggered.connect(self.restart_timer)

        cancel_action = self.menu.addAction("Cancel Shutdown")
        cancel_action.triggered.connect(self.cancel_shutdown)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_tray_icon_clicked)

        self.update_icon()
        self.show()

        self.start_timers()

    def start_timers(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(self.interval * 1000)

        self.shutdown_timer = QtCore.QTimer()
        self.shutdown_timer.setSingleShot(True)
        self.shutdown_timer.timeout.connect(self.shutdown)
        self.shutdown_timer.start(self.duration * 1000)

    def restart_timer(self):
        self.elapsed = 0
        self.setToolTip("Shutdown Timer")
        self.update_icon()
        self.timer.stop()
        self.shutdown_timer.stop()
        self.start_timers()

    def on_tray_icon_clicked(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:  # Left-click
            self.restart_timer()

    def update_timer(self):
        self.elapsed += self.interval
        remaining = max(0, self.duration - self.elapsed)
        minutes_left = remaining // 60
        if remaining < 60:
            self.setToolTip(f"Shutdown Timer - {remaining} sec remaining")
        else:
            self.setToolTip(f"Shutdown Timer - {minutes_left} min remaining")
        self.update_icon()

    def update_icon(self):
        progress = min(1.0, self.elapsed / self.duration)
        pixmap = QtGui.QPixmap(64, 64)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = QtCore.QRectF(0, 0, 64, 64)

        # Draw full green circle
        painter.setBrush(QtGui.QColor(0, 255, 0))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(rect)

        # Draw red arc covering elapsed part
        if progress > 0:
            painter.setBrush(QtGui.QColor(255, 0, 0))
            painter.setPen(QtCore.Qt.NoPen)
            path = QtGui.QPainterPath()
            path.moveTo(rect.center())
            path.arcTo(rect, 90, -360 * progress)
            path.lineTo(rect.center())
            painter.drawPath(path)

        painter.end()
        self.setIcon(QtGui.QIcon(pixmap))

    def shutdown(self):
        os.system("wmctrl -c 'Firefox'")
        time.sleep(1)
        os.system("systemctl poweroff")

    def cancel_shutdown(self):
        self.shutdown_timer.stop()
        self.timer.stop()
        exit()


class SingleInstance:
    def __init__(self, name, on_message):
        self.name = name
        self.on_message = on_message
        self.server = QLocalServer()

        if self.server.listen(self.name):
            # This is the first instance
            self.server.newConnection.connect(self.handle_connection)
            self.is_primary = True
        else:
            # Connect to the first instance and send message
            self.is_primary = False
            self.send_message("RESTART")

    def handle_connection(self):
        socket = self.server.nextPendingConnection()
        socket.readyRead.connect(lambda: self.read_message(socket))

    def read_message(self, socket):
        msg = bytes(socket.readAll()).decode()
        if msg == "RESTART":
            self.on_message()

    def send_message(self, message):
        socket = QLocalSocket()
        socket.connectToServer(self.name)
        if socket.waitForConnected(1000):
            socket.write(message.encode())
            socket.flush()
            socket.waitForBytesWritten(1000)
            socket.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray = ShutdownTimer()

    # Create unique instance handler
    instance = SingleInstance("shutdown-timer-instance", tray.restart_timer)

    if not instance.is_primary:
        # This is a second instance, exit silently
        sys.exit(0)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
