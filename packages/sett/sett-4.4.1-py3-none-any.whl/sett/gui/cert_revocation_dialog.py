from sett_rs.cert import CertStore, CertType, RevocationReason

from .component import (
    GridLayoutCell,
    LineEdit,
    NormalMessageBox,
    grid_layout,
    warning_callback,
)
from .model import AppData
from .pyside import QtWidgets, QtCore, open_window
from .parallel import run_thread
from ..core.crypt import create_revocation_signature, revoke_certificate


class CertCreateRevocationDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget, app_data: AppData):
        super().__init__(parent=parent)
        self.app_data = app_data
        self.setWindowTitle("Create revocation signature")
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.certs = CertStore().list_certs(CertType.Secret)
        self.cert_selector = QtWidgets.QComboBox()
        self.cert_selector.addItems([str(cert) for cert in self.certs])

        self.reason = {
            "compromised": RevocationReason.Compromised,
            "superseded": RevocationReason.Superseded,
            "retired": RevocationReason.Retired,
            "unspecified": RevocationReason.Unspecified,
        }
        self.reason_selector = QtWidgets.QComboBox()
        self.reason_selector.setStatusTip("Reason for revocation")
        self.reason_selector.addItems(list(self.reason))
        self.reason_msg = LineEdit()
        self.reason_msg.setStatusTip(
            "A short text explaining the reason for the certificate revocation"
        )
        self.reason_msg = LineEdit()
        self.password = LineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.revocation_signature = QtWidgets.QTextEdit()
        self.revocation_signature.setReadOnly(True)
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Close
        )
        btn_box.rejected.connect(self.reject)
        self.btn_run = QtWidgets.QPushButton("Create revocation signature")
        self.btn_run.clicked.connect(self.create_revocation)

        self.setLayout(
            grid_layout(
                (QtWidgets.QLabel("Certificate"), self.cert_selector),
                (QtWidgets.QLabel("Reason"), self.reason_selector),
                (
                    QtWidgets.QLabel("Message"),
                    self.reason_msg,
                ),
                (QtWidgets.QLabel("Password"), self.password),
                (
                    GridLayoutCell(
                        self.btn_run,
                        span=2,
                    ),
                ),
                (
                    GridLayoutCell(
                        self.revocation_signature,
                        span=2,
                    ),
                ),
                (None, btn_box),
            )
        )

    def create_revocation(self) -> None:
        cert = self.certs[self.cert_selector.currentIndex()]
        self.btn_run.setEnabled(False)

        def show_revocation_signature(signature: bytes) -> None:
            self.revocation_signature.clear()
            self.revocation_signature.append(signature.decode("utf8"))

        cert_serialized = CertStore().export_cert(cert.fingerprint, CertType.Secret)
        run_thread(
            create_revocation_signature,
            f_kwargs={
                "cert": cert_serialized,
                "reason": self.reason[self.reason_selector.currentText()],
                "message": self.reason_msg.text().encode("utf8"),
                "password": self.password.text().encode("utf8"),
            },
            forward_errors=warning_callback(
                "OpenPGP revocation signature generation error"
            ),
            report_config=self.app_data.config,
            signals={
                "result": show_revocation_signature,
                "finished": lambda: self.btn_run.setEnabled(True),
            },
        )


class CertRevokeDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget, app_data: AppData):
        super().__init__(parent=parent)
        self.app_data = app_data
        self.setWindowTitle("Certificate revocation")
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )
        self.revocation_signature = QtWidgets.QTextEdit(parent=self)
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Close
        )
        btn_box.rejected.connect(self.reject)
        self.btn_run = QtWidgets.QPushButton("Revoke certificate")
        self.btn_run.setDefault(True)
        self.btn_run.clicked.connect(self.revoke)

        self.setLayout(
            grid_layout(
                (QtWidgets.QLabel("Paste your revocation signature"),),
                (self.revocation_signature,),
                (self.btn_run,),
                (btn_box,),
            ),
        )

    def revoke(self) -> None:
        def post_cert_revocation() -> None:
            msg = NormalMessageBox(
                self.parentWidget(), "OpenPGP Certificate Revocation"
            )
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setText("OpenPGP certificate has been successfully revoked.")
            open_window(msg)
            self.app_data.update_public_keys()
            self.close()

        run_thread(
            revoke_certificate,
            f_kwargs={
                "rev_sig": self.revocation_signature.toPlainText().encode("utf8")
            },
            forward_errors=warning_callback("OpenPGP certificate revocation error"),
            report_config=self.app_data.config,
            signals={"result": post_cert_revocation},
        )
