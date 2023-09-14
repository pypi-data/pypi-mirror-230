from sett_rs.cert import CertStore, CertType

from .component import (
    grid_layout,
    warning_callback,
    PathInput,
    GridLayoutCell,
)
from .model import AppData
from .parallel import run_thread
from .pyside import QtWidgets, QtCore
from ..core.error import UserError


class CertImportDialog(QtWidgets.QDialog):
    """Dialog box to import a PGP certificate from file."""

    def __init__(self, parent: QtWidgets.QWidget, app_data: AppData):
        super().__init__(parent=parent)
        self.app_data = app_data
        self.setWindowTitle("Import PGP certificate from file")
        self.setModal(True)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )

        # Create the file selection components.
        self.cert_file_path = PathInput(
            parent=self, directory=False, path=None, btn_clear=False
        )

        # Create the checkbox to enable the import of secret material.
        self.secret_checkbox = QtWidgets.QCheckBox()
        self.secret_checkbox.setToolTip(
            "Import the secret material (secret key) present in the "
            "certificate file. Results in error if no secret material is "
            "present."
        )

        # Create the "Cancel" / "Import" buttons.
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel, parent=self
        )
        self.btn_accepted = QtWidgets.QPushButton("Import key")
        btn_box.addButton(
            self.btn_accepted,
            QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole,
        )
        btn_box.rejected.connect(self.reject)
        btn_box.accepted.connect(self.import_cert)

        # Create a label with instructions for the user.
        checkbox_label = "Import secret material"
        info_label = QtWidgets.QLabel()
        info_label.setText(
            f"""
Import a PGP certificate from a local file. Please note:

 - To import a certificate with secret material (secret key), enable the '{checkbox_label}' checkbox.
 - To import a public certificate (or only the public part of a secret certificate), leave '{checkbox_label}' unchecked.
 - Enabling '{checkbox_label}' for files that contain only public material will result in error.
 - SECURITY WARNING: only import secret certificates that you trust, such as your own certificate.
"""
        )

        # Add all components to the dialog box.
        self.setLayout(
            grid_layout(
                (
                    GridLayoutCell(
                        info_label,
                        span=3,
                    ),
                ),
                (
                    QtWidgets.QLabel("File to import:"),
                    self.cert_file_path.text,
                    self.cert_file_path.btn,
                ),
                (
                    QtWidgets.QLabel(checkbox_label),
                    self.secret_checkbox,
                    None,
                ),
                (None, GridLayoutCell(btn_box, span=2)),
            )
        )

    def import_cert(self) -> None:
        # Disable the "Import" button so that the user cannot click it again
        # while the operation is running in its own thread. The button is
        # enabled again when the thread completed.
        self.btn_accepted.setEnabled(False)

        def _import_cert(path: str, with_secret: bool) -> None:
            with open(path, "rb") as f:
                try:
                    CertStore().import_cert(
                        f.read(), CertType.Secret if with_secret else CertType.Public
                    )
                except RuntimeError as e:
                    raise UserError(str(e)) from e

        def on_result() -> None:
            self.app_data.update_private_keys()
            self.app_data.update_public_keys()
            self.close()

        run_thread(
            _import_cert,
            f_kwargs={
                "path": self.cert_file_path.path,
                "with_secret": self.secret_checkbox.isChecked(),
            },
            forward_errors=warning_callback("Certificate import error"),
            report_config=self.app_data.config,
            signals={
                "result": on_result,
                "finished": lambda: self.btn_accepted.setEnabled(True),
            },
        )
