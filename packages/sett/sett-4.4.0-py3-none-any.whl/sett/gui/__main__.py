#!/usr/bin/env python3
"""Secure Encryption and Transfer Tool GUI."""

import sys
import threading
import time
from typing import Any

from . import main_window
from .pyside import QtGui, QtWidgets, open_window
from .theme import Appearance, IconRepainter

# Note: rc_icon is used implicitly by PySide. It must be imported into the
# namespace, even if never used, otherwise the icons don't display in the GUI.
from .resources import rc_icons  # pylint: disable=unused-import
from ..utils.log import log_to_rotating_file
from .. import APP_NAME_SHORT, __version__


def repaint_icons(icon_repainter: IconRepainter) -> None:
    """Check every 2 seconds whether user is running their OS in dark or
    light mode and repaints the GUI's icons accordingly (otherwise the icons
    become hard to see if they are black on a dark background).
    """
    previous_appearance = Appearance.current()
    while True:
        new_appearance = Appearance.current()
        if new_appearance != previous_appearance:
            icon_repainter.repaint_icons()
            previous_appearance = new_appearance
        time.sleep(2)


def set_window_size(window: QtWidgets.QMainWindow) -> None:
    screen_size = QtGui.QGuiApplication.primaryScreen().availableSize()
    screen_width = screen_size.width()
    screen_height = screen_size.height()
    recommended_width = 1100
    recommended_height = 1000
    window.resize(
        screen_width if screen_width < recommended_width else recommended_width,
        screen_height if screen_height < recommended_height else recommended_height,
    )


def run() -> Any:
    icon_repainter = IconRepainter()
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME_SHORT)
    app.setApplicationDisplayName(f"{APP_NAME_SHORT} ({__version__})")
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QtGui.QIcon(":icon/sett_icon.png"))
    window = main_window.MainWindow(icon_repainter)
    log_to_rotating_file(
        log_dir=window.app_data.config.log_dir,
        file_max_number=window.app_data.config.log_max_file_number,
    )
    start_repaint_icons_thread(icon_repainter)
    set_window_size(window)
    window.show()
    return open_window(app)


def start_repaint_icons_thread(icon_repainter: IconRepainter) -> None:
    thread = threading.Thread(target=repaint_icons, args=(icon_repainter,))
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    run()
