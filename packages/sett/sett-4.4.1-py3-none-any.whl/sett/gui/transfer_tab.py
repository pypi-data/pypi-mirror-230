import enum
import json
import time
from functools import partial
from typing import Iterator, Optional, Sequence

from .component import (
    BaseTab,
    PathInput,
    GuiProgress,
    get_text_input,
    MandatoryLabel,
    ToolBar,
    LineEdit,
    grid_layout,
    vbox_layout,
    hbox_layout,
    GridLayoutCell,
    NormalMessageBox,
)
from .file_selection_widget import ArchiveOnlyFileSelectionWidget
from .model import new_sftp_connection, AppData
from .pyside import QtCore, QtGui, QtWidgets, QAction, open_window
from .theme import Action
from .ui_model_bind import (
    bind,
    TextControl,
    OptionalTextControl,
    OptionalPasswordControl,
    OptionalPathControl,
    BoolControl,
)
from .. import protocols
from ..core.error import UserError
from ..protocols.liquid_files import Protocol as LiquidFiles
from ..protocols.s3 import Protocol as S3
from ..protocols.sftp import Protocol as Sftp
from ..utils.config import ConnectionStore
from ..workflows import transfer


class TransferProtocol(enum.Enum):
    sftp = "SFTP"
    s3 = "S3-compatible"
    liquid_files = "Liquid Files"

    @property
    def status_tip(self) -> str:
        return {
            TransferProtocol.sftp: "Secure (SSH) File Transfer Protocol.",
            TransferProtocol.s3: "Amazon S3 (Simple Storage Service) compatible object storage.",
            TransferProtocol.liquid_files: "A proprietary file-sharing service.",
        }[self]

    def create_button(self) -> QtWidgets.QRadioButton:
        btn = QtWidgets.QRadioButton(self.value)
        btn.setStatusTip(self.status_tip)
        return btn

    def create_options_panel(
        self, data: AppData, parent: QtWidgets.QWidget
    ) -> QtWidgets.QGroupBox:
        if self is TransferProtocol.sftp:
            return self._create_sftp_options_panel(data, parent)
        if self is TransferProtocol.s3:
            return self._create_s3_options_panel(data)
        if self is TransferProtocol.liquid_files:
            return self._create_lf_options_panel(data)
        raise RuntimeError("Unreachable")

    def _create_sftp_options_panel(
        self, data: AppData, parent: QtWidgets.QWidget
    ) -> QtWidgets.QGroupBox:
        args = data.transfer_protocol_args[Sftp]
        text_username = LineEdit()
        text_username.setStatusTip("Username on the SFTP server")
        bind(args, "username", text_username, TextControl)

        text_destination_dir = LineEdit()
        text_destination_dir.setStatusTip(
            "Relative or absolute path to the "
            "destination directory on the SFTP "
            "server"
        )
        bind(args, "destination_dir", text_destination_dir, TextControl)

        text_host = LineEdit()
        text_host.setStatusTip("URL of the SFTP server with an optional port number")
        bind(args, "host", text_host, TextControl)

        text_jumphost = LineEdit()
        text_jumphost.setStatusTip("(optional) URL of the jumphost server")
        bind(args, "jumphost", text_jumphost, OptionalTextControl)

        pkey_location = PathInput(directory=False, path=None, parent=parent)
        pkey_location.setStatusTip(
            "Path to the private SSH key used for authentication"
        )
        bind(args, "pkey", pkey_location, OptionalPathControl)

        pkey_password = LineEdit()
        pkey_password.setStatusTip("Passphrase for the SSH private key")
        pkey_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        bind(args, "pkey_password", pkey_password, OptionalPasswordControl)

        box = QtWidgets.QGroupBox()
        box.setFlat(True)
        grid_layout(
            (MandatoryLabel("User name"), text_username),
            (MandatoryLabel("Host URL"), text_host),
            (QtWidgets.QLabel("Jumphost URL"), text_jumphost),
            (MandatoryLabel("Destination directory"), text_destination_dir),
            (
                QtWidgets.QLabel("SSH key location"),
                pkey_location.text,
                pkey_location.btn,
                pkey_location.btn_clear,
            ),
            (QtWidgets.QLabel("SSH key password"), pkey_password),
            parent=box,
        )
        return box

    def _create_s3_options_panel(self, data: AppData) -> QtWidgets.QGroupBox:
        args = data.transfer_protocol_args[S3]

        text_host = LineEdit()
        text_host.setStatusTip("Host name of the S3-compatible server.")
        text_host.setPlaceholderText("minioserver.example.net:9000")
        bind(args, "host", text_host, TextControl)

        bool_secure = QtWidgets.QCheckBox()
        bool_secure.setStatusTip("Whether to use a secure (TLS) connection or not.")
        bool_secure.setChecked(True)
        bind(args, "secure", bool_secure, BoolControl)
        secure_layout = QtWidgets.QHBoxLayout()
        secure_layout.addWidget(QtWidgets.QLabel("Use secure TLS connection"))
        secure_layout.addWidget(bool_secure)

        text_bucket = LineEdit()
        text_bucket.setStatusTip(
            "Location (bucket) of the S3-compatible server to which the "
            "file(s) should be uploaded."
        )
        bind(args, "bucket", text_bucket, TextControl)

        text_access_key = LineEdit()
        text_access_key.setStatusTip(
            "Credentials for logging-in to the S3-compatible server: user access key."
        )
        bind(args, "access_key", text_access_key, TextControl)

        text_secret_key = LineEdit()
        text_secret_key.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        text_secret_key.setStatusTip(
            "Credentials for logging-in to the S3-compatible server: user secret key."
        )
        # To make left and right panels the same width.
        text_secret_key.setMinimumWidth(400)
        bind(args, "secret_key", text_secret_key, OptionalPasswordControl)

        text_session_token = LineEdit()
        text_session_token.setStatusTip(
            "Credentials for logging-in to the S3-compatible server: "
            "temporary STS (Security Token Service) token."
        )
        bind(args, "session_token", text_session_token, OptionalTextControl)

        # Function to copy/paste s3 access credentials from the portal.
        def read_clipboard() -> None:
            clipboard = QtGui.QGuiApplication.clipboard()
            try:
                credentials_with_opts = json.loads(clipboard.text())
                for field, key in (
                    (text_access_key, "accessKeyId"),
                    (text_secret_key, "secretAccessKey"),
                    (text_session_token, "sessionToken"),
                    (text_host, "endpoint"),
                    (text_bucket, "bucket"),
                ):
                    # Make sure that the value change is really registered (important for `bind`)
                    field.setFocus()
                    field.setText(credentials_with_opts[key])
                    field.clearFocus()
            except (json.JSONDecodeError, KeyError):
                msg = NormalMessageBox(
                    parent=box, window_title="Paste from clipboard failure"
                )
                msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                msg.setText(
                    "This credential pasting is intended to be used with "
                    "credentials copied from the portal.\n\n"
                    "For the credentials pasting to work, the content of "
                    "the clipboard must be a JSON string with the following "
                    "format:\n\n"
                    "{"
                    '"accessKeyId": "value of access key ID", '
                    '"secretAccessKey": "value of secret key", '
                    '"sessionToken": "value of STS token", '
                    '"endpoint": "S3 server endpoint", '
                    '"bucket": "bucket name"'
                    "}"
                )
                open_window(msg)

        button = QtWidgets.QPushButton("Paste credentials from clipboard")
        button.clicked.connect(read_clipboard)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(button)

        box = QtWidgets.QGroupBox()
        box.setFlat(True)
        grid_layout(
            (
                MandatoryLabel("Host"),
                text_host,
                secure_layout,
            ),
            (
                MandatoryLabel("Bucket"),
                text_bucket,
            ),
            (
                MandatoryLabel("Access Key"),
                GridLayoutCell(text_access_key, span=2),
                MandatoryLabel("Secret Key"),
                text_secret_key,
            ),
            (
                QtWidgets.QLabel("Session Token"),
                GridLayoutCell(text_session_token, span=4),
            ),
            (None, None, None, None, button_layout),
            parent=box,
        )
        return box

    def _create_lf_options_panel(self, data: AppData) -> QtWidgets.QGroupBox:
        args = data.transfer_protocol_args[LiquidFiles]

        text_host = LineEdit()
        bind(args, "host", text_host, TextControl)

        text_api_key = LineEdit()
        bind(args, "api_key", text_api_key, TextControl)

        box = QtWidgets.QGroupBox()
        box.setFlat(True)
        grid_layout(
            (MandatoryLabel("Host URL"), text_host),
            (MandatoryLabel("API Key"), text_api_key),
            parent=box,
        )
        return box


class TransferTab(BaseTab):
    """Class that creates the "Transfer" Tab of the GUI application."""

    def __init__(self, parent: QtWidgets.QMainWindow, app_data: AppData):
        super().__init__(parent=parent)
        self.app_data = app_data
        self.connections_model = QtCore.QStringListModel()
        files_panel = self.create_files_panel()
        options_panel = self.create_options_panel()
        self.create_run_panel("Transfer data", self.transfer, "Transfer selected files")
        self.create_console()
        self.create_progress_bar()
        vbox_layout(
            files_panel,
            options_panel,
            self.run_panel,
            self.console,
            self.progress_bar,
            parent=self,
        )

    def create_files_panel(self) -> QtWidgets.QGroupBox:
        box = ArchiveOnlyFileSelectionWidget(
            title="Encrypted files to transfer",
            parent=self,
            model=self.app_data.transfer_files,
        )
        self.app_data.transfer_files.layoutChanged.connect(
            lambda: self.set_buttons_enabled(
                self.app_data.transfer_files.rowCount() > 0
            )
        )
        return box

    def create_conn_actions(
        self, connections_selection: QtWidgets.QComboBox
    ) -> Iterator[QAction]:
        connection_store = ConnectionStore()

        def confirm(text: str) -> bool:
            dialog = QtWidgets.QMessageBox(parent=self)
            dialog.setWindowTitle("Connection profile")
            dialog.setText(text)
            dialog.setStandardButtons(
                QtWidgets.QMessageBox.StandardButton.Ok
                | QtWidgets.QMessageBox.StandardButton.Cancel
            )
            dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Cancel)
            return bool(open_window(dialog) == QtWidgets.QMessageBox.StandardButton.Ok)

        def rename() -> None:
            label_old = connections_selection.currentText()
            dialog = ConnectionDialog(
                parent=self,
                label=f"Rename connection profile '{label_old}' to:",
                forbidden=self.connections_model.stringList(),
                default_input=label_old,
            )
            if open_window(dialog):
                label_new = dialog.text_field.text()
                self.app_data.config.connections[
                    label_new
                ] = self.app_data.config.connections.pop(label_old)
                try:
                    connection_store.rename(old=label_old, new=label_new)
                except UserError:
                    # Connection profile is not saved in the config file.
                    pass
                self.connections_model.setStringList(
                    sorted(
                        label_new if x == label_old else x
                        for x in self.connections_model.stringList()
                    )
                )
                connections_selection.setCurrentText(label_new)

        def add() -> None:
            dialog = ConnectionDialog(
                parent=self,
                label="New connection profile label:",
                forbidden=self.connections_model.stringList(),
            )
            if open_window(dialog):
                label = dialog.text_field.text()
                self.app_data.config.connections[label] = new_sftp_connection()
                self.connections_model.setStringList(
                    sorted(self.connections_model.stringList() + [label])
                )
                connections_selection.setCurrentText(label)

        def delete() -> None:
            label = connections_selection.currentText()
            if confirm(f"Do you want to delete '{label}' profile?"):
                self.app_data.config.connections.pop(label)
                self.connections_model.removeRow(connections_selection.currentIndex())
                try:
                    connection_store.delete(label)
                except UserError:
                    # Connection profile is not saved in the config file.
                    pass

        def save() -> None:
            label = connections_selection.currentText()
            if confirm(f"Do you want to save '{label}' profile to your config file?"):
                connection = self.app_data.transfer_protocol_args[
                    self.app_data.transfer_protocol_type
                ].target
                self.app_data.config.connections[label] = connection
                connection_store.save(label, connection)

        def set_btn_enabled(btn: QtWidgets.QAbstractButton, text: str) -> None:
            btn.setEnabled(bool(text))

        for tip, fn, needs_selection, icon in (
            ("Create a new connection profile", add, False, "plus-square"),
            ("Rename the current connection profile", rename, True, "edit"),
            ("Delete the current connection profile", delete, True, "trash-2"),
            ("Save the current connection profile", save, True, "save"),
        ):
            action = Action(f":icon/feather/{icon}.png", tip, self)
            action.triggered.connect(fn)
            if needs_selection:
                connections_selection.currentTextChanged.connect(
                    partial(set_btn_enabled, action)
                )
                if not connections_selection.currentText():
                    action.setEnabled(False)
            yield action

    def create_options_panel(self) -> QtWidgets.QGroupBox:
        box = QtWidgets.QGroupBox("Connection")

        connections_selection = QtWidgets.QComboBox(box)
        connections_selection.setStatusTip(
            "Select a predefined connection profile. Check documentation for details."
        )
        connections_selection.setModel(self.connections_model)
        self.connections_model.setStringList(list(self.app_data.config.connections))

        protocol_sftp = TransferProtocol.sftp
        protocol_s3 = TransferProtocol.s3
        protocol_lf = TransferProtocol.liquid_files

        protocol_btn_grp = QtWidgets.QButtonGroup(box)
        for p in (protocol_sftp, protocol_s3, protocol_lf):
            protocol_btn_grp.addButton(p.create_button())

        get_btn_from_group(protocol_btn_grp, protocol_sftp.value).setChecked(True)

        protocol_boxes = {
            p.name: p.create_options_panel(self.app_data, self)
            for p in (protocol_sftp, protocol_s3, protocol_lf)
        }
        for p in (protocol_s3, protocol_lf):
            protocol_boxes[p.name].hide()

        def load_connection() -> None:
            connection = self.app_data.config.connections.get(
                connections_selection.currentText()
            )
            if not connection:
                return
            protocol = protocols.protocol_name[type(connection)]
            get_btn_from_group(
                protocol_btn_grp, TransferProtocol[protocol].value
            ).click()
            self.app_data.transfer_protocol_args[
                self.app_data.transfer_protocol_type
            ].target = connection

        connections_selection.currentTextChanged.connect(load_connection)

        def toggle_protocol(btn: QtWidgets.QRadioButton, state: bool) -> None:
            protocol_name = TransferProtocol(btn.text()).name
            if state:
                self.app_data.transfer_protocol_type = protocols.parse_protocol(
                    protocol_name
                )
            protocol_boxes[protocol_name].setVisible(state)

        protocol_btn_grp.buttonToggled.connect(toggle_protocol)

        toolbar = ToolBar("Options", self)
        for action in self.create_conn_actions(connections_selection):
            toolbar.addAction(action)
        layout_connection = hbox_layout(connections_selection, toolbar)
        layout_protocol_buttons = hbox_layout(*protocol_btn_grp.buttons())

        layout_protocol = vbox_layout(layout_protocol_buttons, *protocol_boxes.values())
        vbox_layout(layout_connection, layout_protocol, parent=box)
        load_connection()
        return box

    def transfer(self, dry_run: bool = False) -> None:
        second_factor = None

        class Msg(enum.Enum):
            code = enum.auto()

        class MsgSignal(QtCore.QObject):
            msg = QtCore.Signal(object)

        msg_signal = MsgSignal()

        def second_factor_callback() -> None:
            msg_signal.msg.emit(Msg.code)
            time_start = time.time()
            timeout = 120
            while time.time() - time_start < timeout:
                time.sleep(1)
                if second_factor is not None:
                    break
            return second_factor

        def show_second_factor_dialog(msg: str) -> None:
            """Show a pop-up where the user can enter the verification code
            for their second factor authentication.
            """
            nonlocal second_factor
            second_factor = None
            if msg == str(Msg.code):
                output = get_text_input(self, "Verification code")
                second_factor = "" if output is None else output

        protocol = self.app_data.transfer_protocol_args[
            self.app_data.transfer_protocol_type
        ].target

        msg_signal.msg.connect(show_second_factor_dialog)
        self.run_workflow_thread(
            transfer.transfer,
            f_kwargs={
                "files": self.app_data.transfer_files.stringList(),
                "protocol": protocol,
                "config": self.app_data.config,
                "dry_run": dry_run,
                "pkg_name_suffix": self.app_data.encrypt_package_name_suffix,
                "progress": GuiProgress(self.progress_bar.setValue),
                "two_factor_callback": second_factor_callback,
            },
            capture_loggers=(
                transfer.logger,
                protocols.sftp.logger,
                protocols.sftp.logger_rs,
                protocols.s3.logger,
            ),
            ignore_exceptions=True,
            report_config=self.app_data.config,
        )


class ConnectionDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget],
        label: str,
        forbidden: Sequence[str] = (),
        default_input: str = "",
    ):
        super().__init__(parent=parent)
        self.setWindowTitle("Connection profile")
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )

        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        self.text_field = LineEdit()
        self.text_field.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"[\w\-@]+"))
        )
        self.text_field.setText(default_input)

        def set_ok_enabled(text: str) -> None:
            btn_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setEnabled(
                len(text) > 0 and text not in forbidden
            )

        set_ok_enabled(self.text_field.text())
        self.text_field.textChanged.connect(set_ok_enabled)

        self.setLayout(vbox_layout(QtWidgets.QLabel(label), self.text_field, btn_box))


def get_btn_from_group(
    btn_grp: QtWidgets.QButtonGroup, text: str
) -> QtWidgets.QAbstractButton:
    btn = next(x for x in btn_grp.buttons() if x.text() == text)
    if not btn:
        raise KeyError(f"No button matching '{text}' found in the group.")
    return btn
