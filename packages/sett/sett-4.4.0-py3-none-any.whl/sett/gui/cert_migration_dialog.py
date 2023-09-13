from sett_rs.cert import CertStore, CertType

from .component import LineEdit, grid_layout, warning_callback
from .model import AppData
from .parallel import run_thread
from .pyside import QtWidgets, QtCore
from .settings_tab import show_missing_gnupg_warning


def open_key_migration_dialog(parent: QtWidgets.QWidget, app_data: AppData) -> None:
    """Wrapper around the key migration dialog (CertMigrationDialog) that
    displays a user-friendly error message in the case where GnuPG is not
    installed on the user's machine.
    """
    try:
        CertMigrationDialog(parent=parent, app_data=app_data).show()
    except FileNotFoundError as e:
        show_missing_gnupg_warning(
            parent_widget=parent,
            msg_prefix="Migrating PGP keys from the GnuPG keyring to the "
            "sett certificate store",
            original_error=str(e),
        )


class CertMigrationDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget, app_data: AppData):
        super().__init__(parent=parent)
        self.app_data = app_data
        self.setWindowTitle("GnuPG secret key migration")
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.certs = self.app_data.config.gpg_store.list_sec_keys()
        self.cert_selector = QtWidgets.QComboBox()
        self.cert_selector.addItems(
            [f"{cert.uids[0]} {cert.key_id}" for cert in self.certs]
        )
        self.password = LineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.btn_accepted = QtWidgets.QPushButton("Migrate key")
        btn_box.addButton(
            self.btn_accepted,
            QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole,
        )
        btn_box.rejected.connect(self.reject)
        btn_box.accepted.connect(self.migrate)

        self.setLayout(
            grid_layout(
                (
                    None,
                    QtWidgets.QLabel(
                        "This dialog box allows to migrate (i.e. copy) a "
                        "secret OpenPGP key from the GnuPG keyring to the "
                        "sett OpenPGP certificate store.\n\n"
                        "Please note that:\n"
                        " - Migrating a secret key will also migrate its "
                        "associated public key.\n"
                        " - Migrating public keys that have no associated "
                        "secret key (typically, a public key that is not your "
                        "own) is not supported.\n"
                        "   To migrate such public keys, please download them "
                        "from the keyserver.\n"
                        " - This procedure will not delete the "
                        "migrated key from the GnuPG keyring.\n"
                    ),
                ),
                (QtWidgets.QLabel("GnuPG secret key"), self.cert_selector),
                (QtWidgets.QLabel("Password"), self.password),
                (None, btn_box),
            )
        )

    def migrate(self) -> None:
        self.btn_accepted.setEnabled(False)

        def _migrate(fingerprint: str) -> None:
            CertStore().import_cert(
                self.app_data.config.gpg_store.export_secret(
                    fingerprint, self.password.text()
                ),
                CertType.Secret,
            )

        def on_result() -> None:
            self.app_data.update_private_keys()
            self.app_data.update_public_keys()
            self.close()

        run_thread(
            _migrate,
            f_kwargs={
                "fingerprint": self.certs[self.cert_selector.currentIndex()].fingerprint
            },
            forward_errors=warning_callback("GnuPG key migration error"),
            report_config=self.app_data.config,
            signals={
                "result": on_result,
                "finished": lambda: self.btn_accepted.setEnabled(True),
            },
        )
