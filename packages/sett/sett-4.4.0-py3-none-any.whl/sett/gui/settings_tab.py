import re
from dataclasses import Field, asdict, fields
from itertools import chain, repeat
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

from sett.utils.get_config_path import get_config_file
from sett.utils.validation import REGEX_FQDN, REGEX_IP
from .component import (
    NormalMessageBox,
    PathInput,
    create_slider,
    LineEdit,
    SpinBox,
    grid_layout,
    GridLayoutCell,
)
from .model import AppData, ConfigProxy
from .pyside import QtCore, QtGui, QtWidgets, open_window
from .theme import Icon, PushButton, get_icon_repainter
from .ui_model_bind import (
    bind,
    TextControl,
    PathControl,
    BoolControl,
    NumericControl,
)
from ..utils import config
from ..utils.config import Config, FileType


def align(
    items: Sequence[Sequence[Sequence[Any]]],
) -> Iterator[Tuple[Optional[Any], ...]]:
    """Align a table where items have different lengths.

    Given a 2-dimensional array of sequences of different lengths, yield
    tuples of equal length where shorter sequences are filled with `None`s
    to reach the length of the longest sequence.
    """
    longest = max((len(col) for row in items for col in row), default=0)
    for row in items:
        aligned: List[Any] = []
        for col in row:
            aligned.extend(chain(col, repeat(None, longest - len(col))))
        yield tuple(aligned)


class SettingsTab(QtWidgets.QWidget):
    """Class that builds the tab where users can modify the settings of their
    application.
    """

    persist_btn_text = "Save to config file"
    persist_btn_icon_file_name = ":icon/feather/save.png"

    def __init__(self, parent: QtWidgets.QMainWindow, app_data: AppData):
        super().__init__(parent=parent)
        self.config_proxy = app_data.config

        widget_register: Dict[str, QtWidgets.QWidget] = {}
        cfg_fields = {f.name: f for f in fields(Config)}

        def cfg_field(key: str) -> Tuple[QtWidgets.QWidget, ...]:
            return widget_row_from_field(
                self.config_proxy,
                cfg_fields[key],
                parent=parent,
                widget_register=widget_register,
            )

        def label_field(text: str) -> GridLayoutCell:
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(round(font.pointSize() * 1.3))
            label = QtWidgets.QLabel(text)
            label.setFont(font)
            return GridLayoutCell(
                label,
                span=8,
                align=QtCore.Qt.AlignmentFlag.AlignBottom,
            )

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        layout.addLayout(self._header())
        layout.addSpacing(20)
        layout.addLayout(
            grid_layout(
                *align(
                    (
                        ((label_field("Data encryption / decryption"),), ()),
                        (cfg_field("compression_level"), cfg_field("max_cpu")),
                        (cfg_field("verify_dtr"), cfg_field("default_sender")),
                        (
                            cfg_field("always_trust_recipient_key"),
                            cfg_field("output_dir"),
                        ),
                        ((), cfg_field("package_name_suffix")),
                        ((label_field("PGP keys"),), ()),
                        (cfg_field("gpg_key_autodownload"), cfg_field("keyserver_url")),
                        (cfg_field("verify_key_approval"), cfg_field("gpg_home_dir")),
                        ((label_field("Data transfer"),), ()),
                        (cfg_field("dcc_portal_url"), cfg_field("sftp_buffer_size")),
                        (
                            cfg_field("verify_package_name"),
                            cfg_field("ssh_password_encoding"),
                        ),
                        ((label_field("Miscellaneous"),), ()),
                        (cfg_field("repo_url"), cfg_field("log_dir")),
                        (cfg_field("check_version"), cfg_field("log_max_file_number")),
                        (
                            cfg_field("gui_quit_confirmation"),
                            cfg_field("error_reports"),
                        ),
                        (cfg_field("legacy_mode"),),
                    )
                )
            )
        )
        layout.addStretch()
        layout.addWidget(self._footer())
        self.setLayout(layout)

        # Enable or disable the PGP key auto-download checkbox option based on
        # whether a keyserver URL value is provided or not.
        self.checkbox_gpg_key_autodownload = cast(
            QtWidgets.QCheckBox, widget_register["gpg_key_autodownload"]
        )
        self.field_keyserver_url = cast(
            QtWidgets.QLineEdit, widget_register["keyserver_url"]
        )
        self._enable_checkbox_key_autodownload()
        self.field_keyserver_url.textChanged.connect(
            self._enable_checkbox_key_autodownload
        )
        self.config_proxy.refresh()
        get_icon_repainter(self).register(self.refresh_icon)

        # Enable or disable the GnuPG home directory field depending on the
        # whether legacy mode is enabled or not. Also checks that GnuPG is
        # available if legacy mode is being enabled.
        self.checkbox_legacy_mode = cast(
            QtWidgets.QCheckBox, widget_register["legacy_mode"]
        )
        self.field_gpg_home_dir = cast(
            QtWidgets.QLineEdit, widget_register["gpg_home_dir"]
        )
        self._check_gnupg_is_present_and_enable_gpg_home_dir()
        self.checkbox_legacy_mode.stateChanged.connect(
            self._check_gnupg_is_present_and_enable_gpg_home_dir
        )

    def _save_config_to_disk(self) -> None:
        """Write the current in-app config values to a config file on disk."""
        config.save_config(config.config_to_dict(self.config_proxy.get_config()))
        msg = NormalMessageBox(parent=self, window_title="Settings")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setText(f'Successfully saved settings to "{get_config_file()}"')
        open_window(msg)

    def _header(
        self,
    ) -> QtWidgets.QGridLayout:
        top_label = QtWidgets.QLabel(
            "Changes you make are applied instantly during the current session.\n"
            f"To persist changes across restarts, make sure to click the "
            f"'{self.persist_btn_text}' button at the bottom of the app."
        )
        top_label.setWordWrap(True)
        reset_btn = QtWidgets.QPushButton("Reset", self)
        reset_btn.setStatusTip("Resets to your last persisted settings")
        reset_btn.clicked.connect(
            lambda: self.config_proxy.set_config(config.load_config())
        )

        defaults_btn = QtWidgets.QPushButton("Restore defaults", self)
        defaults_btn.setStatusTip("Reset all settings to their default values")
        defaults_btn.clicked.connect(
            lambda: self.config_proxy.set_config(config.default_config())
        )
        layout = QtWidgets.QGridLayout()
        layout.addWidget(top_label, 0, 0, 1, 2)
        layout.addWidget(reset_btn, 0, 2)
        layout.addWidget(defaults_btn, 0, 3)
        return layout

    def _footer(self) -> PushButton:
        self.persist_btn = PushButton(
            self.persist_btn_icon_file_name,
            f'{self.persist_btn_text} "{get_config_file()}"',
            self,
        )
        self.persist_btn.setStatusTip("Saves your current settings to the config file")
        self.persist_btn.clicked.connect(self._save_config_to_disk)
        return self.persist_btn

    def _enable_checkbox_key_autodownload(self) -> None:
        self.checkbox_gpg_key_autodownload.setEnabled(
            len(self.field_keyserver_url.text().strip()) > 0
        )

    def _check_gnupg_is_present_and_enable_gpg_home_dir(self) -> None:
        """Test if GnuPG is available by attempting to initialize a GPGStore
        using gpg-lite. Display a warning if the GnuPG executable is missing
        and unset the "legacy_mode" checkbox.
        """
        if self.checkbox_legacy_mode.isChecked():
            try:
                _ = self.config_proxy.get_config().gpg_store
            except FileNotFoundError as e:
                show_missing_gnupg_warning(
                    parent_widget=self,
                    msg_prefix="Enabling the GnuPG legacy mode",
                    original_error=str(e),
                )
                self.checkbox_legacy_mode.setCheckState(QtCore.Qt.CheckState.Unchecked)

        # Enable/disabled the "gog home dir" input field depending on the
        # state of the legacy mode check box.
        self.field_gpg_home_dir.setEnabled(self.checkbox_legacy_mode.isChecked())

    def refresh_icon(self) -> None:
        self.persist_btn.setIcon(Icon(self.persist_btn_icon_file_name))


def check_hostname(regex: str, widget: LineEdit, status_tip: str) -> None:
    """Verify that the URL entered in the specified widget is valid.
    * If the URL is not valid, the cell is colored in red and an error is
      displayed as tooltip (StatusTip).
    * Minor errors (e.g. using :/ instead of :// after the scheme) are
      auto-corrected.
    """

    # Retrieve the name of the config setting associated with the widget.
    config_key = widget.objectName()

    def display_error_in_widget(error_msg: str) -> None:
        """Change the background color and status tip of the LineEdit widget
        to display an error to the user.
        """
        widget.setStyleSheet(f"#{config_key} {{background-color:red;}}")
        widget.setStatusTip(error_msg)

    # Get the URL value from the widget. Empty values are allowed (nothing to
    # check in that case)
    url = widget.text().strip()
    if not url:
        return

    # Verify that a valid scheme is given by the user.
    # If no scheme is given, https:// is added by default.
    scheme, *_ = re.split(r"://|:/", url)
    if not _:
        hostname = scheme
        scheme = "https"
    else:
        hostname = _[0]
        if scheme not in ("http", "https"):
            display_error_in_widget(f"Non-allowed scheme: {scheme}://")
            return

    hostname_only, *_ = re.split(r":\d+|/", hostname)

    # Verify that a the hostname has a valid syntax.
    if not re.search(regex, hostname_only) and not re.search(REGEX_IP, hostname_only):
        display_error_in_widget("Invalid hostname or IP address")
        return

    # Update widget text to the (possibly) corrected URL value.
    # Note: the StatusTip is here set again for the case when the field
    # earlier contained an error and still has the error message as StatusTip.
    widget.setText(scheme + "://" + hostname)
    widget.setStyleSheet(f"#{config_key} {{}}")
    widget.setStatusTip(status_tip)


def reset_to_default_if_empty(widget: LineEdit) -> None:
    """Check whether the given free text `widget` (of type LineEdit) is empty,
    and if so, fill the widget with the default value of the setting that it
    holds.
    Additionally, warn the user that the setting has been reset via a pop-up.

    :param widget: text widget whose text is to be reset.
    """
    if not widget.text().strip():
        # Reset the in-memory value (AppData) and widget text to the default
        # value of the setting.
        config_key = widget.objectName()
        widget.setText(Config.get_default_value(config_key))
        widget.editingFinished.emit()

        # Generate a pop-up that warns the user that the field has been
        # reset to its default value.
        msg = NormalMessageBox(
            parent=widget.parent(), window_title="Mandatory field warning"  # type: ignore
        )
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setText(
            f"The field '{Config.get_label(config_key)}' ('{config_key}' "
            "in the config file) is mandatory and cannot be left empty.\n\n"
            "The field was reset to its default value."
        )
        open_window(msg)


def widget_str(
    config_proxy: ConfigProxy,
    config_key: str,
    status_tip: str,
    regex: Optional[str] = None,
) -> Tuple[QtWidgets.QWidget, ...]:
    """Return a text widget (LineEdit) associated with the specified setting
    `config_key`. The widget has the following behavior:
     * The status tip of the widget is set to status_tip.
     * When edited by the user, the content of the text field is checked to
       make sure the input complies with the (optionally) specified regexp
       `regex`.
     * For settings that are mandatory, if the user clears the content of the
       widget without providing any value, the widget is reset to its default
       value.
    """

    widget = LineEdit()
    widget.setStatusTip(status_tip)
    bind(config_proxy, config_key, widget, TextControl)
    widget.setObjectName(config_key)

    # If the setting is mandatory (i.e. `None` is not allowed as a value), a
    # check for resetting empty values to their default value is added to the
    # actions to perform after a field was edited by the user.
    if Config.is_mandatory_argument(config_key):
        widget.editingFinished.connect(lambda: reset_to_default_if_empty(widget))

    # Add regexp-based validation rules to the field. These rules are either
    # added via a post-edit check (i.e. when the user leaves the field, see
    # Case 1 below), or via a "Validator" (checks the value at every keystroke
    # from the user, see Case 2 below).
    # Case 1: the field uses REGEX_FQDN as validator regexp, meaning that
    #         it contains a URL (FQDN = fully qualified domain name).
    if regex == REGEX_FQDN:
        # A check for the validity of the specified domain name is added.
        widget.editingFinished.connect(
            lambda: check_hostname(regex, widget, status_tip)
        )
    # Case 2: the field is not a URL, but it has some specific validation
    #         rules given as a regexp.
    elif regex is not None:
        widget.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(regex))
        )

    return (widget,)


def widget_path(
    config_proxy: ConfigProxy,
    config_key: str,
    status_tip: str,
    file_type: FileType,
    parent: QtWidgets.QWidget,
) -> Tuple[QtWidgets.QWidget, ...]:
    """Return a path widget associated with the setting `config_key`."""
    widget = PathInput(
        directory=file_type is FileType.directory, path=None, parent=parent
    )
    widget.setStatusTip(status_tip)
    bind(config_proxy, config_key, widget, PathControl)
    return (widget.text, widget.btn, widget.btn_clear)


def widget_bool(
    config_proxy: ConfigProxy,
    config_key: str,
    status_tip: str,
) -> Tuple[QtWidgets.QWidget, ...]:
    """Return a check-box widget associated with the specified boolean setting
    `config_key`.
    """
    widget = QtWidgets.QCheckBox()
    widget.setStatusTip(status_tip)

    bind(config_proxy, config_key, widget, BoolControl)
    return (widget,)


def widget_int(
    config_proxy: ConfigProxy,
    config_key: str,
    status_tip: str,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
) -> Tuple[QtWidgets.QWidget, ...]:
    """Return a spin-box widget (a field for integer values with arrows to
    increase/decrease the value) associated with the specified setting
    `config_key`.
    """
    widget = SpinBox()
    widget.setStatusTip(status_tip)
    if minimum is not None:
        widget.setMinimum(minimum)
    if maximum is not None:
        widget.setMaximum(maximum)
    bind(config_proxy, config_key, widget, NumericControl)
    return (widget,)


def widget_int_range(
    config_proxy: ConfigProxy,
    config_key: str,
    status_tip: str,
    minimum: int,
    maximum: int,
) -> Tuple[QtWidgets.QWidget, ...]:
    """Return a slider widget that allows to select integer values associated
    with the specified setting `config_key`.

    The slider has a specified range [minimum - maximum]. This widget only
    makes sense when the range of values is not too large, typically <= 25.
    """
    slider, slider_value = create_slider(
        minimum=minimum,
        maximum=maximum,
        initial_value=getattr(config_proxy, config_key),
        status_tip=status_tip,
        on_change=None,
        show_ticks=True,
    )
    bind(config_proxy, config_key, slider, NumericControl)
    return (slider, slider_value)


widget_by_type: Dict[type, Callable[..., Tuple[QtWidgets.QWidget, ...]]] = {
    int: widget_int,
    bool: widget_bool,
    str: widget_str,
}


# TODO: when dropping support for python 3.8, remove quotes around "Field".
def widget_row_from_field(
    config_proxy: ConfigProxy,
    field: "Field[Any]",
    widget_register: Optional[Dict[str, QtWidgets.QWidget]] = None,
    parent: Optional[QtWidgets.QWidget] = None,
) -> Tuple[QtWidgets.QWidget, ...]:
    """Create a widget row consisting of a label, a main widget and possible
    auxiliary widgets based on field metadata of the Config dataclass.

    If widget_register is passed, register the main widget under the
    corresponding field name.
    """
    field_type = field.type
    if getattr(field_type, "__origin__", None) is Union:
        field_type = next(t for t in field_type.__args__ if not isinstance(None, t))
    try:
        metadata = field.metadata["metadata"]
    except KeyError:
        raise RuntimeError(
            "Field metadata is required in order to create a widget from a field."
        ) from None
    widget_factory = widget_by_type[field_type]
    widget_args = {
        key: val
        for key, val in asdict(metadata).items()
        if key not in ("label", "description") and val is not None
    }

    # Special cases:
    #  * The setting is a small numerical range:
    if (
        metadata.minimum is not None
        and metadata.maximum is not None
        and abs(metadata.minimum - metadata.maximum) < 25
    ):
        widget_factory = widget_int_range
    #  * The setting is a path to a directory/file:
    if metadata.file_type is not None:
        widget_factory = widget_path
        widget_args = {**widget_args, **{"parent": parent}}

    widget_row = widget_factory(
        config_proxy,
        config_key=field.name,
        status_tip=metadata.description,
        **widget_args,
    )
    if widget_register is not None:
        widget_register[field.name] = widget_row[0]
    return (
        QtWidgets.QLabel(metadata.label),
        *widget_row,
    )


def show_missing_gnupg_warning(
    parent_widget: QtWidgets.QWidget,
    msg_prefix: str,
    original_error: str,
) -> None:
    """Show a pop-up explaining that GnuPG is missing."""
    msg = NormalMessageBox(
        parent=parent_widget, window_title="GnuPG executable not found"
    )
    msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
    msg.setText(
        f"{msg_prefix} requires the `gpg` application to be installed "
        "on your machine. This seems not to be the case.\n\n"
        "Please install the GnuPG executable, and/or make sure it is part "
        "of your PATH and try again.\n\n"
        f"Original error: {original_error}"
    )
    open_window(msg)
