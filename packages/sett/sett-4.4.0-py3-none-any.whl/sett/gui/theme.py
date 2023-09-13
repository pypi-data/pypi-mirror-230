from enum import Enum
from typing import Callable, cast

import darkdetect

from .pyside import QtGui, get_application_global_instance, QtCore, QtWidgets, QAction


class Appearance(Enum):
    LIGHT = 1
    DARK = 2

    @classmethod
    def current(cls) -> "Appearance":
        return cls.DARK if darkdetect.isDark() else cls.LIGHT


class Icon(QtGui.QIcon):
    def __init__(self, filename: str):
        super().__init__(self.to_pixmap(filename))

    @staticmethod
    def to_pixmap(filename: str) -> QtGui.QPixmap:
        palette = get_application_global_instance().palette()  # type: ignore
        pixmap = QtGui.QPixmap(filename)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(
            QtGui.QPainter.CompositionMode.CompositionMode_SourceIn
        )
        painter.fillRect(pixmap.rect(), palette.color(palette.ColorRole.Text))
        painter.end()
        return pixmap


class IconRepainter(QtCore.QObject):
    signal = QtCore.Signal()

    def repaint_icons(self) -> None:
        self.signal.emit()

    def register(self, slot: Callable[..., None]) -> None:
        self.signal.connect(slot)


def get_icon_repainter(widget: QtWidgets.QWidget) -> IconRepainter:
    if hasattr(widget, "icon_repainter"):
        return cast(IconRepainter, widget.icon_repainter)
    parent_widget = widget.parentWidget()
    if parent_widget:
        return get_icon_repainter(parent_widget)
    raise NotImplementedError(f"'icon_repainter' NOT found in '{type(widget)}'")


class Action(QAction):
    def __init__(
        self, icon_file_name: str, text: str, parent: QtWidgets.QWidget
    ) -> None:
        self._icon_file_name = icon_file_name
        super().__init__(Icon(icon_file_name), text, parent)
        get_icon_repainter(parent).register(self.refresh_icon)

    def refresh_icon(
        self,
    ) -> None:
        self.setIcon(Icon(self._icon_file_name))


class PushButton(QtWidgets.QPushButton):
    def __init__(
        self, icon_file_name: str, text: str, parent: QtWidgets.QWidget
    ) -> None:
        self._icon_file_name = icon_file_name
        super().__init__(Icon(icon_file_name), text, parent)
        get_icon_repainter(parent).register(self.refresh_icon)

    def refresh_icon(self) -> None:
        self.setIcon(Icon(self._icon_file_name))


class EnabledOnSelectionButton(PushButton):
    """A push button extension which connects this button to a given selection
    model. The button is disabled by default. And gets enabled when the
    selection has, at least, one selected row.
    """

    def __init__(
        self,
        icon_file_name: str,
        text: str,
        parent: QtWidgets.QWidget,
        selection_model: QtCore.QItemSelectionModel,
    ):
        super().__init__(icon_file_name, text, parent)
        self.setEnabled(False)
        self._selection_model = selection_model
        selection_model.selectionChanged.connect(self.selection_changed)

    def selection_changed(self) -> None:
        # Following works better than using 'QItemSelection', especially in
        # cases where multiple selection is possible
        self.setEnabled(bool(len(self._selection_model.selectedRows())))
