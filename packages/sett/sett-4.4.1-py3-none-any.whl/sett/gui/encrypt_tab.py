from functools import partial, wraps
from typing import Any, Optional, cast

from .component import (
    BaseTab,
    PathInput,
    GuiProgress,
    create_slider,
    get_pass_input,
    MandatoryLabel,
    LineEdit,
    grid_layout,
    GridLayoutCell,
    vbox_layout,
    hbox_layout,
)
from .file_selection_widget import DirectoryAndFileSelectionWidget
from .theme import PushButton, EnabledOnSelectionButton
from .model import TableModel, AppData, KeyValueListModel
from .pyside import QtCore, QtGui, QtWidgets
from ..core.filesystem import OutOfSpaceError
from ..core.metadata import Purpose
from ..utils.config import LABEL_COMPRESSION_LEVEL, DESCRIPTION_COMPRESSION_LEVEL
from ..utils.validation import PACKAGE_SUFFIX
from ..workflows import encrypt

ignore_disk_space_error_label = "Ignore disk space error"


@wraps(encrypt.encrypt)
def encrypt_workflow(*args: str, **kwargs: Any) -> Optional[str]:
    try:
        return encrypt.encrypt(*args, **kwargs)
    except OutOfSpaceError as e:
        raise OutOfSpaceError(
            f"{e} Use the checkbox '{ignore_disk_space_error_label}' in the "
            "output box to ignore this error.",
        ) from e


class EncryptTab(BaseTab):
    """Class that creates the "Encrypt" Tab of the GUI application."""

    def __init__(self, parent: QtWidgets.QMainWindow, app_data: AppData):
        super().__init__(parent=parent)
        self.app_data = app_data
        files_panel = self.create_files_panel()
        self.create_run_panel(
            "Package and encrypt data", self.encrypt, "Package && Encrypt"
        )
        for field in (
            "encrypt_files",
            "encrypt_recipients",
            "encrypt_transfer_id",
            "encrypt_purpose",
        ):
            self.app_data.add_listener(field, self._enable_buttons)
            self.app_data.config.add_listener("verify_dtr", self._enable_buttons)
        self.create_console()
        self.create_progress_bar()

        vbox_layout(
            files_panel,
            self._create_sender_transferinfo_and_output_layout(),
            self.run_panel,
            self.console,
            self.progress_bar,
            parent=self,
        )

    def _enable_buttons(self) -> None:
        self.set_buttons_enabled(
            len(self.app_data.encrypt_recipients) > 0
            and len(self.app_data.encrypt_files) > 0
            and (
                not self.app_data.config.verify_dtr
                or (
                    self.app_data.config.verify_dtr
                    and self.app_data.encrypt_transfer_id is not None
                )
            )
            and (
                self.app_data.encrypt_transfer_id is None
                or self.app_data.encrypt_purpose is not None
            )
        )

    def create_files_panel(self) -> QtWidgets.QGroupBox:
        box = DirectoryAndFileSelectionWidget(title="Data to encrypt", parent=self)
        box.file_list_model.layoutChanged.connect(
            lambda: setattr(self.app_data, "encrypt_files", box.get_list())
        )
        return box

    def create_user_panel(self) -> QtWidgets.QGroupBox:
        group_box = QtWidgets.QGroupBox("Data sender and recipients")
        sender_widget = QtWidgets.QComboBox()
        sender_widget.setModel(self.app_data.priv_keys_model)
        if self.app_data.default_key_index:
            sender_widget.setCurrentIndex(self.app_data.default_key_index)

        recipients_input_view = QtWidgets.QComboBox()
        recipients_input_view.setModel(self.app_data.pub_keys_model)

        recipients_output_view = QtWidgets.QTableView()
        recipients_output_view.setModel(self.app_data.encrypt_recipients_model)
        recipients_output_view.verticalHeader().hide()
        recipients_output_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents
        )
        recipients_output_view.horizontalHeader().setStretchLastSection(True)
        recipients_output_view.setSelectionBehavior(
            QtWidgets.QTableView.SelectionBehavior.SelectRows
        )
        recipients_output_view.setSelectionMode(
            QtWidgets.QTableView.SelectionMode.SingleSelection
        )

        recipients_btn_add = PushButton(":icon/feather/user-plus.png", "", self)
        recipients_btn_add.setToolTip("Add recipient to the list")

        recipients_btn_remove = EnabledOnSelectionButton(
            ":icon/feather/user-minus.png",
            "",
            self,
            recipients_output_view.selectionModel(),
        )
        recipients_btn_remove.setToolTip("Remove recipient from the list")

        def update_sender(index: int) -> None:
            self.app_data.encrypt_sender = (
                ""
                if index == -1
                else self.app_data.priv_keys_model.get_value(index).fingerprint
            )

        def update_recipients(index: QtCore.QModelIndex) -> None:
            # Note: it's probably possible to get rid of the cast() here.
            recipients = cast(TableModel, index.model())
            self.app_data.encrypt_recipients = tuple(
                str(x[2]) for x in recipients.get_data()
            )

        def add_recipient() -> None:
            # Note: it's probably possible to get rid of the cast() here.
            key = cast(KeyValueListModel, recipients_input_view.model()).get_value(
                recipients_input_view.currentIndex()
            )
            row = (
                key.uids[0].full_name
                if hasattr(key.uids[0], "full_name")
                else key.uids[0].name,
                key.uids[0].email,
                key.fingerprint,
            )
            self.app_data.encrypt_recipients_model.set_data(
                tuple(
                    set(self.app_data.encrypt_recipients_model.get_data()) | set([row])
                )
            )

        def remove_recipient() -> None:
            recipients_output_view.model().removeRows(
                recipients_output_view.currentIndex().row(), 1
            )
            recipients_output_view.clearSelection()

        # Connect actions.
        recipients_btn_add.clicked.connect(add_recipient)
        recipients_btn_remove.clicked.connect(remove_recipient)
        self.app_data.encrypt_recipients_model.dataChanged.connect(update_recipients)
        sender_widget.currentIndexChanged.connect(update_sender)

        # Set the default value for the sender.
        update_sender(sender_widget.currentIndex())
        grid_layout(
            (
                GridLayoutCell(
                    QtWidgets.QLabel(
                        "Select data sender and add at least one recipient:"
                    ),
                    span=3,
                ),
            ),
            (MandatoryLabel("Sender"), sender_widget),
            (None, recipients_input_view, recipients_btn_add),
            (
                GridLayoutCell(
                    MandatoryLabel("Recipients"), align=QtCore.Qt.AlignmentFlag.AlignTop
                ),
                recipients_output_view,
                GridLayoutCell(
                    recipients_btn_remove, align=QtCore.Qt.AlignmentFlag.AlignTop
                ),
            ),
            parent=group_box,
        )
        return group_box

    def _create_sender_transferinfo_and_output_layout(self) -> QtWidgets.QHBoxLayout:
        """Create a layout with 3 group boxes: 'Data sender and recipients',
        'Data transfer info' and 'Output'.
        """
        layout_right = vbox_layout(
            self._create_transferinfo_group_box(), self._create_output_group_box()
        )
        return hbox_layout(self.create_user_panel(), layout_right)

    def _create_output_group_box(self) -> QtWidgets.QGroupBox:
        """Create a group box with the output-related fields."""

        group_box = QtWidgets.QGroupBox("Output")

        # Create fields
        output_suffix = LineEdit()
        output_suffix.setText(self.app_data.encrypt_package_name_suffix)
        output_suffix.setStatusTip(
            "(optional) File name suffix in the format (project_)datetime(_suffix).tar"
        )
        output_suffix.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(PACKAGE_SUFFIX))
        )
        output_location = PathInput(
            path=self.app_data.encrypt_output_location, parent=self, btn_clear=False
        )
        output_location.setStatusTip("Destination folder for the encrypted package")

        # Add actions
        output_suffix.editingFinished.connect(
            lambda: setattr(
                self.app_data, "encrypt_package_name_suffix", output_suffix.text()
            )
        )
        output_location.on_path_change(
            partial(setattr, self.app_data, "encrypt_output_location")
        )

        slider_widgets = create_slider(
            minimum=0,
            maximum=9,
            initial_value=self.app_data.encrypt_compression_level,
            status_tip=DESCRIPTION_COMPRESSION_LEVEL,
            on_change=lambda n: setattr(self.app_data, "encrypt_compression_level", n),
        )
        compression_layout = hbox_layout(
            *(QtWidgets.QLabel(LABEL_COMPRESSION_LEVEL),) + slider_widgets
        )

        ignore_disk_space_error = QtWidgets.QCheckBox(
            ignore_disk_space_error_label, group_box
        )
        ignore_disk_space_error.setStatusTip(
            "Write to disk, even if there is less space available than the "
            "input data occupies."
        )
        ignore_disk_space_error.setChecked(
            self.app_data.encrypt_ignore_disk_space_error
        )
        ignore_disk_space_error.stateChanged.connect(
            lambda state: setattr(
                self.app_data,
                "encrypt_ignore_disk_space_error",
                QtCore.Qt.CheckState(state) == QtCore.Qt.CheckState.Checked,
            )
        )
        grid_layout(
            (QtWidgets.QLabel("Suffix"), output_suffix),
            (
                QtWidgets.QLabel("Location"),
                output_location.text,
                output_location.btn,
            ),
            (GridLayoutCell(compression_layout, span=2),),
            (GridLayoutCell(ignore_disk_space_error, span=2),),
            parent=group_box,
        )
        return group_box

    def _create_transferinfo_group_box(self) -> QtWidgets.QGroupBox:
        """Create a group box with data transfer request (DTR) related fields."""

        group_box = QtWidgets.QGroupBox("Data transfer info")
        required_suffix = "<sup><font color='red'>*</font></sup>"

        transfer_id_label = QtWidgets.QLabel("DTR ID")
        transfer_id = LineEdit()
        transfer_id.setStatusTip(
            "Data Transfer Request ID (optional if Verify DTR is disabled in settings)"
        )
        transfer_id.setValidator(QtGui.QIntValidator(1, 10**9))
        purpose_label = QtWidgets.QLabel("Purpose")
        purpose = QtWidgets.QComboBox(group_box)
        purpose.setStatusTip("Purpose of the package (required if DTR ID is specified)")
        purpose.addItems(("",) + tuple(x.name for x in Purpose))
        purpose.setCurrentText("")

        def on_verify_dtr_changed() -> None:
            transfer_id_label.setText(
                "DTR ID" + (required_suffix if self.app_data.config.verify_dtr else "")
            )

        self.app_data.config.add_listener("verify_dtr", on_verify_dtr_changed)

        def on_transfer_id_changed(text: str) -> None:
            if text:
                self.app_data.encrypt_transfer_id = int(text)
                purpose_label.setText(f"Purpose{required_suffix}")
            else:
                self.app_data.encrypt_transfer_id = None
                purpose_label.setText("Purpose")

        transfer_id.textChanged.connect(on_transfer_id_changed)
        purpose.currentTextChanged.connect(
            lambda text: setattr(
                self.app_data, "encrypt_purpose", None if text == "" else Purpose(text)
            )
        )
        grid_layout(
            (transfer_id_label, transfer_id),
            (purpose_label, purpose),
            parent=group_box,
        )
        return group_box

    def encrypt(self, dry_run: bool = False) -> None:
        """Run the encrypt workflow in a separate thread."""

        def update_files_to_transfer_in_transfer_tab(path: Optional[str]) -> None:
            if path is not None:
                self.app_data.transfer_files.setStringList([path])
                self.app_data.transfer_files.layoutChanged.emit()
                self.console.append(
                    "<strong>Added the newly created package to the 'Transfer' tab.</strong>"
                )

        # Retrieve the user's PGP key password (needed to sign the data).
        if not dry_run:
            passphrase = get_pass_input(self, "Please enter your PGP key password")
            if passphrase is None:
                return
        else:
            passphrase = None

        # Run the encrypt workflow in a separate thread.
        self.run_workflow_thread(
            encrypt_workflow,
            f_kwargs={
                "files": self.app_data.encrypt_files,
                "capture_loggers": (encrypt.logger, encrypt.logger_rs),
                "sender": self.app_data.encrypt_sender,
                "recipients": self.app_data.encrypt_recipients,
                "dtr_id": self.app_data.encrypt_transfer_id,
                "config": self.app_data.config,
                "passphrase": passphrase,
                "output": self.app_data.encrypt_output_location,
                "output_suffix": self.app_data.encrypt_package_name_suffix,
                "dry_run": dry_run,
                "compression_level": self.app_data.encrypt_compression_level,
                "purpose": self.app_data.encrypt_purpose,
                "progress": GuiProgress(self.progress_bar.setValue),
            },
            signals={"result": update_files_to_transfer_in_transfer_tab},
            ignore_exceptions=True,
            report_config=self.app_data.config,
            force=self.app_data.encrypt_ignore_disk_space_error,
        )
