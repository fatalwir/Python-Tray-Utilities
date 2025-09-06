# Python Tray Utilities
Some Python utilities for a tray panel in Linux.

Created using ChatGPT for Debian with KDE Plasma.

## shutdownTimer.py
Starts a timer (1 hr) to run *systemctl poweroff*. The time can be reset by left mouse click on the tray icon. The remaining time is indicated by the icon as a pie chart.

## nightColorToggler.py
This utility toggles the *Night Light* mode by clicking the tray icon.

### disable-nightcolor.service
Disables the *Night Light* mode for the next computer startup.

1. Put into *~/.config/systemd/user/*.
2. systemctl --user enable disable-nightcolor.service
3. systemctl --user start disable-nightcolor.service
