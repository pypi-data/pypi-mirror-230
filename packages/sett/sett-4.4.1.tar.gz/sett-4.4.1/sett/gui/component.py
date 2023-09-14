from functools import partial
from pathlib import Path
from typing import (
    Callable,
    Optional,
    Tuple,
    Sequence,
    Dict,
    Union,
    Any,
    cast,
    TypeVar,
    Type,
    Iterable,
)

from .parallel import run_thread
from .pyside import QtCore, QtWidgets, open_window
from .theme import Action, PushButton
from .. import APP_NAME_SHORT
from ..core.secret import Secret
from ..utils.progress import ProgressInterface

EXTRA_HEIGHT = 1
MACOS_TOOLTIP_BG_COLOR = "#ffffca"


def is_macos() -> bool:
    return QtCore.QSysInfo.productType() in ("osx", "macos")


class SpinBox(QtWidgets.QSpinBox):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        if is_macos():
            self.setMinimumHeight(self.sizeHint().height() + EXTRA_HEIGHT)


class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        if is_macos():
            self.setMinimumHeight(self.sizeHint().height() + EXTRA_HEIGHT)


class ToolBar(QtWidgets.QToolBar):
    def __init__(self, title: str, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(title, parent)
        # Remove the ugly gradient from the macos toolbar.
        if is_macos():
            self.setStyleSheet("background: transparent;border-width: 0px;")
        self.setIconSize(QtCore.QSize(20, 20))


class NormalMessageBox(QtWidgets.QMessageBox):
    """A message box which enforces normal font."""

    def __init__(self, parent: QtWidgets.QWidget, window_title: str):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setTextFormat(QtCore.Qt.TextFormat.MarkdownText)
        self.setStyleSheet("font-weight: 500;")

    def set_text_list(self, text: Iterable[str]) -> None:
        return super().setText("\n\n".join(text))


class MandatoryLabel(QtWidgets.QLabel):
    """A label extension which appends a '*' at the end of the label to mark
    the field as required.
    """

    def __init__(self, label: str):
        super().__init__(label + " <sup><font color='red'>*</font></sup>")


class SelectionButton(QtWidgets.QPushButton):
    """A push button extension which connects this button to a given selection
    model.

    The button is disabled by default. And gets enabled when the selection has,
    at least, one selected row.
    """

    def __init__(self, label: str, selection_model: QtCore.QItemSelectionModel):
        super().__init__(label)
        self.setEnabled(False)
        self._selection_model = selection_model
        selection_model.selectionChanged.connect(self.selection_changed)

    def selection_changed(self) -> None:
        # Following works better than using 'QItemSelection', especially in
        # cases where multiple selection is possible
        self.setEnabled(bool(len(self._selection_model.selectedRows())))


class SelectionAction(Action):
    """An action extension which connects this action to a selection model.

    The action is disabled by default, and gets enabled when the selection has,
    at least, one selected row.
    """

    def __init__(self, *args: Any, selection_model: QtCore.QItemSelectionModel):
        super().__init__(*args)
        self.setEnabled(False)
        self._selection_enabled = True
        self._selection_model = selection_model
        self._selection_model.selectionChanged.connect(self.selection_changed)

    def enable_selection(self, enabled: bool) -> None:
        self._selection_enabled = enabled
        self.selection_changed()

    def selection_changed(self) -> None:
        # Following works better than using 'QItemSelection', especially in
        # cases where multiple selection is possible.
        self.setEnabled(
            self._selection_enabled and bool(len(self._selection_model.selectedRows()))
        )


class GuiProgress(QtCore.QObject, ProgressInterface):
    # NOTE: the casting below is needed but it's not clear whether this is
    #       because i) we are generating the SignalInstance object improperly,
    #       or ii) PySide has implemented this badly and the cast to path their
    #       implementation.
    updated = cast(QtCore.SignalInstance, QtCore.Signal(int))

    def __init__(self, update_callback: Callable[..., None]):
        super().__init__()
        self.n: float = 0
        self.updated.connect(update_callback)

    def update(self, completed_fraction: float) -> None:
        self.n = completed_fraction
        self.updated.emit(round(completed_fraction * 100, 0))

    def get_completed_fraction(self) -> float:
        return self.n


class ConsoleWidget(QtWidgets.QGroupBox):
    def __init__(self, title: str, parent: QtWidgets.QWidget):
        super().__init__(title, parent)
        self.textbox = QtWidgets.QTextEdit()
        self.textbox.setReadOnly(True)
        btn_clear_console = PushButton(":icon/feather/slash.png", "", self)
        btn_clear_console.setToolTip("Clear console")
        btn_clear_console.clicked.connect(self.clear)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.textbox)
        layout.addWidget(btn_clear_console, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

    def clear(self) -> None:
        self.textbox.clear()

    def append(self, text: str) -> None:
        self.textbox.append(text)

    def write(self, text: str) -> None:
        self.textbox.append(text)


class PathInput:
    """Path selection container with a select button and a 'show path' field."""

    def __init__(
        self,
        parent: QtWidgets.QWidget,
        directory: bool = True,
        path: Optional[Path] = Path.home(),
        btn_clear: bool = True,
    ):
        self.parent = parent
        self.text = LineEdit(parent)
        self.text.setReadOnly(True)
        self.btn = PushButton(
            f":icon/feather/{'folder' if directory else 'file'}.png", "", parent
        )
        self.btn.setToolTip("Change location")
        self.btn.clicked.connect(partial(self._update_location, directory))
        if btn_clear:
            # Add additional button to allow clearing the selected path.
            self.btn_clear = PushButton(":icon/feather/slash.png", "", parent)
            self.btn_clear.setToolTip("Clear location")
            self.btn_clear.clicked.connect(self._clear_location)
        self.update_path(path)

    def update_path(self, path: Optional[Path]) -> None:
        self.path = path
        self.text.setText("" if path is None else str(path))
        self.text.editingFinished.emit()

    def _update_location(self, directory: bool) -> None:
        if self.path and self.path.exists():
            location = self.path if self.path.is_dir() else self.path.parent
        else:
            location = Path.home()
        if directory:
            new_path = QtWidgets.QFileDialog.getExistingDirectory(
                parent=self.parent,
                caption="Select Directory",
                dir=str(location),
            )
        else:
            new_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                parent=self.parent, caption="Select File", dir=str(location)
            )
        if new_path:
            self.update_path(Path(new_path))

    def _clear_location(self) -> None:
        self.update_path(None)

    def setStatusTip(self, msg: str) -> None:
        self.text.setStatusTip(msg)

    def on_path_change(self, fn: Callable[[Optional[Path]], None]) -> None:
        """Run callback when path changes."""
        self.text.editingFinished.connect(lambda: fn(self.path))


class BaseTab(QtWidgets.QWidget):
    """Adds two boxes to the layout of a QWidget (a Tab from the application):
    - Box with buttons to run and test run a workflow.
    - Box with a console.
    """

    def create_console(self) -> None:
        # pylint:disable=attribute-defined-outside-init
        self.console = ConsoleWidget(title="Console", parent=self)

    def create_progress_bar(self) -> None:
        # pylint:disable=attribute-defined-outside-init
        self.progress_bar = QtWidgets.QProgressBar(self)

    @staticmethod
    def _create_disabled_button(action_name: str) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(action_name)
        button.setEnabled(False)
        return button

    def set_buttons_enabled(self, enabled: bool) -> None:
        self.btn_run.setEnabled(enabled)
        self.btn_test.setEnabled(enabled)

    def create_run_panel(
        self, panel_name: str, action: Callable[..., Any], action_name: str
    ) -> None:
        # pylint:disable=attribute-defined-outside-init
        self.run_panel = QtWidgets.QGroupBox(panel_name)
        # pylint:disable=attribute-defined-outside-init
        self.btn_test = BaseTab._create_disabled_button("Test")

        # On pressed button, make sure that the focus switches to that
        # button (Mac specific issue)
        self.btn_test.pressed.connect(self.btn_test.setFocus)
        self.btn_test.clicked.connect(partial(action, dry_run=True))
        # pylint:disable=attribute-defined-outside-init
        self.btn_run = BaseTab._create_disabled_button(action_name)

        # On pressed button, make sure that the focus switches to that
        # button (Mac specific issue)
        self.btn_run.pressed.connect(self.btn_run.setFocus)
        self.btn_run.clicked.connect(action)
        hbox_layout(self.btn_test, self.btn_run, parent=self.run_panel)

    def run_workflow_thread(
        self,
        f: Callable[..., Any],
        signals: Optional[Dict[str, Callable[..., Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """Run a thread with predefined signals."""
        self.run_panel.setEnabled(False)
        default_signals: Dict[str, Callable[..., Any]] = {
            "logging": self.console.write,
            "error": lambda e: self.console.append(str(e[1])),
            "finished": lambda: self.run_panel.setEnabled(True),
        }
        run_thread(f, signals={**default_signals, **(signals or {})}, **kwargs)


def get_text_input(
    parent: QtWidgets.QWidget, msg: str, password: bool = False
) -> Optional[str]:
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(APP_NAME_SHORT)
    buttons = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.StandardButton.Cancel
    )
    ok_btn = buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ok)
    ok_btn.setEnabled(False)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    user_input = LineEdit()
    user_input.textChanged.connect(lambda t: ok_btn.setEnabled(bool(t)))
    if password:
        user_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
    vbox_layout(QtWidgets.QLabel(msg), user_input, buttons, parent=dialog)
    if open_window(dialog) != QtWidgets.QDialog.DialogCode.Accepted:
        return None
    return user_input.text()


def get_pass_input(parent: QtWidgets.QWidget, msg: str) -> Optional[Secret[str]]:
    raw_pw = get_text_input(parent, msg, password=True)
    return None if raw_pw is None else Secret(raw_pw)


def warning_callback(
    title: str,
    parent: Optional[QtWidgets.QWidget] = None,
    msg_prefix: Optional[str] = None,
) -> Callable[[str], None]:
    msg_warn = warning_dialog(title, parent=parent)
    prefix = f"{msg_prefix}\n\n" if msg_prefix else ""

    def _show_warning(msg: str) -> None:
        # Add an extra line break so that text is easier to read in GUI.
        error_msg_from_process = format(msg).replace("\n", "\n\n")
        msg_warn.setText(prefix + error_msg_from_process)
        open_window(msg_warn)

    return _show_warning


def warning_dialog(
    title: str, text: Optional[str] = None, parent: Optional[QtWidgets.QWidget] = None
) -> QtWidgets.QMessageBox:
    msg = QtWidgets.QMessageBox(parent=parent)
    msg.setWindowTitle(title)
    msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
    if text is not None:
        msg.setText(text)
    return msg


def show_warning(
    title: str, text: str, parent: Optional[QtWidgets.QWidget] = None
) -> None:
    warning_dialog(title, text, parent).show()


def create_slider(
    minimum: int,
    maximum: int,
    initial_value: int,
    status_tip: Optional[str],
    on_change: Optional[Callable[[int], None]] = None,
    show_ticks: bool = False,
    interval: int = 1,
) -> Tuple[QtWidgets.QSlider, QtWidgets.QLabel]:
    widget_value = QtWidgets.QLabel(str(initial_value))

    slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
    slider.setMinimum(minimum)
    slider.setMaximum(maximum)
    slider.setValue(initial_value)
    slider.setTickInterval(interval)
    if status_tip is not None:
        slider.setStatusTip(status_tip)
    if show_ticks:
        slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)

    def update_text(value: int) -> None:
        widget_value.setText(str(value))

    slider.valueChanged.connect(update_text)
    if on_change is not None:
        slider.valueChanged.connect(on_change)

    return slider, widget_value


WIDGET_OR_LAYOUT = Union[QtWidgets.QWidget, QtWidgets.QBoxLayout]


class GridLayoutCell:
    def __init__(
        self,
        widget: WIDGET_OR_LAYOUT,
        span: int = 1,
        align: Optional[QtCore.Qt.AlignmentFlag] = None,
    ):
        self.widget = widget
        self.span = span
        self.align = align


def layout_add(
    layout: Union[QtWidgets.QGridLayout, QtWidgets.QBoxLayout],
    child: WIDGET_OR_LAYOUT,
) -> Callable[..., None]:
    """Returns either layout.addLayout or layout.addWidget depending on the
    type of child.
    """
    return (
        layout.addLayout
        if isinstance(child, (QtWidgets.QVBoxLayout, QtWidgets.QHBoxLayout))
        else layout.addWidget
    )


def grid_layout(
    *widgets: Sequence[Union[WIDGET_OR_LAYOUT, GridLayoutCell, None]],
    parent: Optional[QtWidgets.QWidget] = None,
    min_col_width: Optional[Sequence[int]] = None,
) -> QtWidgets.QGridLayout:
    parent_args = () if parent is None else (parent,)
    layout = QtWidgets.QGridLayout(*parent_args)
    if min_col_width is not None:
        layout.setColumnMinimumWidth(*min_col_width)
    for i, row in enumerate(widgets):
        row_index = 0
        for widget in row:
            if widget is None:
                row_index += 1
                continue
            if not isinstance(widget, GridLayoutCell):
                cell = GridLayoutCell(widget)
            else:
                cell = widget
            align_args = {} if cell.align is None else {"alignment": cell.align}
            add_method = layout_add(layout, cell.widget)
            add_method(cell.widget, i, row_index, 1, cell.span, **align_args)
            row_index += cell.span
    return layout


T = TypeVar("T", QtWidgets.QVBoxLayout, QtWidgets.QHBoxLayout)


def box_layout(
    *widgets: WIDGET_OR_LAYOUT,
    parent: Optional[QtWidgets.QWidget] = None,
    LayoutClass: Type[T],
) -> T:
    parent_args = () if parent is None else (parent,)
    layout = LayoutClass(*parent_args)
    for widget in widgets:
        add_method = layout_add(layout=layout, child=widget)
        add_method(widget)
    return layout


def vbox_layout(
    *widgets: WIDGET_OR_LAYOUT,
    parent: Optional[QtWidgets.QWidget] = None,
) -> QtWidgets.QVBoxLayout:
    return box_layout(*widgets, parent=parent, LayoutClass=QtWidgets.QVBoxLayout)


def hbox_layout(
    *widgets: WIDGET_OR_LAYOUT,
    parent: Optional[QtWidgets.QWidget] = None,
) -> QtWidgets.QHBoxLayout:
    return box_layout(*widgets, parent=parent, LayoutClass=QtWidgets.QHBoxLayout)
