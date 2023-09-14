import html
import logging
import warnings
import functools
from pathlib import Path
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Tuple,
    Union,
    cast,
)

from sett_rs.cert import CertInfo, CertStore, CertType, KeyType
from libbiomedit.portal import KeyStatus

from sett.core.error import UserError
from .component import (
    GridLayoutCell,
    SelectionAction,
    ToolBar,
    grid_layout,
    warning_callback,
    NormalMessageBox,
)
from .key_generation_dialog import KeyGenDialog
from .keys_download_dialog import KeyDownloadDialog
from .cert_import_dialog import CertImportDialog
from .cert_revocation_dialog import CertCreateRevocationDialog, CertRevokeDialog
from .cert_migration_dialog import open_key_migration_dialog
from .model import AppData, KeyValueListModel
from .parallel import run_thread
from .pyside import QAction, QtCore, QtWidgets, open_window
from .theme import Action
from ..core import crypt, gpg
from ..workflows import upload_keys as upload_keys_workflow


def open_message_box(
    *text: str,
    title: str,
    parent: QtWidgets.QWidget,
    icon_type: QtWidgets.QMessageBox.Icon,
    with_ok_cancel_buttons: bool = False,
) -> int:
    """Open a pop-up message box of the specified type and with the specified
    text.
    """
    msgbox = NormalMessageBox(parent=parent, window_title=title)
    msgbox.setIcon(icon_type)
    msgbox.setText("\n\n".join(text))

    # If requested, add "OK" / "Cancel" buttons the user can click.
    if with_ok_cancel_buttons:
        msgbox.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Ok
            | QtWidgets.QMessageBox.StandardButton.Cancel
        )

    # Display the message box to the user.
    return open_window(msgbox)


open_warning_msgbox = functools.partial(
    open_message_box, icon_type=QtWidgets.QMessageBox.Icon.Warning
)
open_info_msgbox = functools.partial(
    open_message_box, icon_type=QtWidgets.QMessageBox.Icon.Information
)


class KeysTab(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QMainWindow, app_data: AppData):
        super().__init__(parent=parent)
        self.app_data = app_data

        self.text_panel = QtWidgets.QTextEdit()
        self.text_panel.setReadOnly(True)

        self.priv_keys_view = QtWidgets.QListView()
        self.priv_keys_view.setModel(self.app_data.priv_keys_model)
        self.priv_keys_view.selectionModel().currentChanged.connect(
            self._update_display
        )

        self.pub_keys_view = QtWidgets.QListView()
        self.pub_keys_view.setModel(self.app_data.pub_keys_model)
        self.pub_keys_view.selectionModel().currentChanged.connect(self._update_display)
        self.pub_keys_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )

        # When item is selected in the public/private key list, clear
        # the selection in the other list.
        self.priv_keys_view.selectionModel().currentChanged.connect(
            lambda: self.pub_keys_view.selectionModel().clear()
        )
        self.pub_keys_view.selectionModel().currentChanged.connect(
            lambda: self.priv_keys_view.selectionModel().clear()
        )

        action_generate_key = Action(
            ":icon/feather/plus-square.png",
            "Generate new private/public key",
            self,
        )
        action_generate_key.triggered.connect(
            lambda: KeyGenDialog(parent=self, app_data=app_data).show()
        )
        action_refresh_keys = Action(
            ":icon/feather/refresh-cw.png",
            "Refresh keys from the local keyring and refresh key status from portal",
            self,
        )

        def refresh_keys() -> None:
            """Fetch PGP key approval status from portal."""
            self.app_data.update_private_keys()
            self.app_data.update_public_keys()

            run_thread(
                self.app_data.update_key_approval_status,
                f_kwargs={},
                report_config=self.app_data.config,
                forward_errors=warning_callback(
                    title="Key approval status retrieval failure",
                    msg_prefix="Approval status of PGP keys could not be "
                    f"retrieved from \n'{self.app_data.config.dcc_portal_url}'.",
                ),
                signals={"result": self.update_display_selected_pub_key},
            )

        action_refresh_keys.triggered.connect(refresh_keys)

        toolbar = ToolBar("Key management", self)
        toolbar.addAction(action_generate_key)
        toolbar.addSeparator()
        for action in self.create_public_keys_actions():
            toolbar.addAction(action)
        toolbar.addSeparator()
        toolbar.addAction(action_refresh_keys)

        self.setLayout(
            grid_layout(
                (GridLayoutCell(toolbar, span=2),),
                (QtWidgets.QLabel("Private keys"), QtWidgets.QLabel("Public keys")),
                (self.priv_keys_view, self.pub_keys_view),
                (GridLayoutCell(self.text_panel, span=2),),
            )
        )

        # Fetch PGP key approval status from portal.
        refresh_keys()

    def cert_to_html(self, cert: CertInfo) -> str:
        """Represent a PGP key as an HTML string"""

        # Add key info (user ID, key ID, fingerprint, signatures).
        content = ["<table>"]
        rows = [
            ("User ID", html.escape(str(cert.uid))),
            ("Key ID", cert.key_id),
            ("Key fingerprint", cert.fingerprint),
            (
                "Key algorithm",
                crypt.KeyAlgorithm(cert.primary_key.pub_key_algorithm).name,
            ),
            ("Key length", cert.primary_key.length),
        ]
        if cert.primary_key.key_type == KeyType.Public:
            rows.append(("Validity", str(cert.validity)))
        for k, v in rows:
            content.append(f"<tr><th>{k}</th><td>{v}</td></tr>")
        content.append("</td></tr></table>")
        if cert.primary_key.revocation_reason:
            for reason in cert.primary_key.revocation_reason:
                content.append(f'<p class="danger">&#215; {reason}</p>')
        # Add key validation info: display whether a key is approved or not.
        if cert.primary_key.key_type == KeyType.Public:
            if not self.app_data.config.verify_key_approval:
                content.append(
                    '<p class="info">Key approval cannot be verified because '
                    "approval verification is disabled in your config file.</p>"
                )
            else:
                cert_status = self.app_data.pub_key_status.get(
                    cert.fingerprint, KeyStatus.UNKNOWN_KEY
                )
                if cert_status == KeyStatus.APPROVED:
                    content.append('<p class="safe">&#x2714; This key is approved.</p>')
                else:
                    content.append(
                        '<p class="danger">&#215; This key is not approved. '
                        f"Status: {cert_status.value}"
                    )
        else:
            content.append(
                "<p>This is a private key. Private keys are not subject to "
                "approval.</p>"
            )

        return "".join(content)

    def key_to_html(self, key: gpg.Key) -> str:
        """Represent a PGP key as an HTML string"""

        # Add key info (user ID, key ID, fingerprint, signatures).
        content = ["<table>"]
        rows = [
            ("User ID", html.escape(str(key.uids[0]))),
            ("Key ID", key.key_id),
            ("Key fingerprint", key.fingerprint),
            ("Key length", key.key_length),
        ]
        for k, v in rows:
            content.append(f"<tr><th>{k}</th><td>{v}</td></tr>")

        content.append("<tr><th>Signatures</th><td>")
        content.append(
            "<br>".join(
                [
                    f"{html.escape(str(sig.issuer_uid))} {sig.issuer_key_id} "
                    f"{sig.signature_class}"
                    for sig in key.valid_signatures
                ]
            )
        )
        content.append("</td></tr>")

        # Add key validation info: display whether a key is approved or not.
        content.append("</table>")
        if key.key_type == gpg.KeyType.public:
            if not self.app_data.config.verify_key_approval:
                content.append(
                    '<p class="info">Key approval cannot be verified because '
                    "approval verification is disabled in your config file.</p>"
                )
            else:
                key_status = self.app_data.pub_key_status.get(
                    key.fingerprint, KeyStatus.UNKNOWN_KEY
                )
                if key_status == KeyStatus.APPROVED:
                    content.append('<p class="safe">&#x2714; This key is approved.</p>')
                else:
                    content.append(
                        '<p class="danger">&#215; This key is not approved. '
                        f"Status: {key_status.value}"
                    )
        else:
            content.append(
                "<p>This is a private key. Private keys are not subject to "
                "approval.</p>"
            )
        return "".join(content)

    @staticmethod
    def key_to_text(key: Union[gpg.Key, CertInfo]) -> str:
        email = key.uids[0].email if isinstance(key, gpg.Key) else key.email
        return f"{email} ({key.key_id})"

    def create_public_keys_actions(self) -> Iterator[QAction]:
        selection_model = self.pub_keys_view.selectionModel()

        # Create a dict of actions (functions) to associate to each
        # action button of the GUI.
        # The reason to create a dict object before looping over it is so
        # that mypy gets the correct typing information (for some reason
        # SelectionAction is not recognized as a subtype of QAction).
        functions_by_action: List[Tuple[QAction, Callable[..., Any]]] = [
            (
                Action(
                    ":icon/feather/download-cloud.png",
                    "Download keys from the keyserver",
                    self,
                ),
                lambda: KeyDownloadDialog(parent=self, app_data=self.app_data).show(),
            ),
            (
                SelectionAction(
                    ":icon/feather/upload-cloud.png",
                    "Upload selected keys to the keyserver",
                    self,
                    selection_model=selection_model,
                ),
                self.upload_key,
            ),
            (
                SelectionAction(
                    ":icon/feather/rotate-cw.png",
                    "Update selected keys from the keyserver",
                    self,
                    selection_model=selection_model,
                ),
                self.update_keys,
            ),
            (
                Action(
                    ":icon/feather/file-plus.png",
                    "Import key from file",
                    self,
                ),
                self.import_key,
            ),
        ]
        if not self.app_data.config.legacy_mode:
            functions_by_action.extend(
                [
                    (
                        SelectionAction(
                            ":icon/feather/share.png",
                            "Export key to file",
                            self,
                            selection_model=selection_model,
                        ),
                        self.export_certificate,
                    ),
                    (
                        Action(
                            ":icon/feather/edit-3.png",
                            "Create revocation signature",
                            self,
                        ),
                        lambda: CertCreateRevocationDialog(
                            parent=self, app_data=self.app_data
                        ).show(),
                    ),
                    (
                        Action(
                            ":icon/feather/flag.png",
                            "Revoke certificate",
                            self,
                        ),
                        lambda: CertRevokeDialog(
                            parent=self, app_data=self.app_data
                        ).show(),
                    ),
                    (
                        Action(
                            ":icon/feather/copy.png",
                            "Migrate secret key from GnuPG",
                            self,
                        ),
                        lambda: open_key_migration_dialog(
                            parent=self, app_data=self.app_data
                        ),
                    ),
                ]
            )
        else:
            functions_by_action.append(
                (
                    SelectionAction(
                        ":icon/feather/trash-2.png",
                        "Delete selected keys from your computer",
                        self,
                        selection_model=selection_model,
                    ),
                    self.delete_keys,
                )
            )

        for action, fn in functions_by_action:
            action.triggered.connect(fn)
            yield action

    def export_certificate(self) -> None:
        for cert in self.get_selected_keys():
            cert_ascii_armored = CertStore().export_cert(
                cert.fingerprint, CertType.Public
            )
            QtWidgets.QFileDialog.saveFileContent(
                cert_ascii_armored, f"{cert.fingerprint}.pub.asc"
            )

    def get_selected_keys(self) -> Tuple[Union[gpg.Key, CertInfo], ...]:
        """Returns the gpg.Key objects corresponding to the keys currently
        selected in the GUI.
        """
        # Note: it's probably possible to get rid of the cast() here.
        selected_keys = (
            cast(KeyValueListModel, index.model()).get_value(index)
            for index in self.pub_keys_view.selectedIndexes()
        )
        return tuple(selected_keys)

    def update_keys(self) -> None:
        """Update/refresh selected keys from the keyserver."""
        keys_to_update = self.get_selected_keys()
        if keys_to_update:

            def on_result() -> None:
                self.app_data.update_public_keys()
                self.update_display_selected_pub_key()
                open_info_msgbox(
                    "Keys have been successfully updated.",
                    title="Updated OpenPGP keys",
                    parent=self.parentWidget(),
                )

            if not self.app_data.config.legacy_mode:

                def update_selected_certificates() -> None:
                    for cert in keys_to_update:
                        CertStore().import_cert(
                            crypt.download_cert(
                                keyserver=self.app_data.config.keyserver_url,
                                identifier=cert.fingerprint,
                            ),
                            CertType.Public,
                        )

                run_thread(
                    update_selected_certificates,
                    f_kwargs={},
                    report_config=self.app_data.config,
                    forward_errors=warning_callback("OpenPGP key update error"),
                    signals={"result": on_result},
                )
            else:
                run_thread(
                    crypt.download_keys,
                    f_kwargs={
                        "key_identifiers": [key.fingerprint for key in keys_to_update],
                        "keyserver": self.app_data.config.keyserver_url,
                        "gpg_store": self.app_data.config.gpg_store,
                    },
                    report_config=self.app_data.config,
                    forward_errors=warning_callback("OpenPGP key update error"),
                    signals={"result": on_result},
                )

    def import_key(self) -> None:
        """Import a PGP key from a local file."""
        if not self.app_data.config.legacy_mode:
            CertImportDialog(parent=self, app_data=self.app_data).show()
        else:
            path = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select OpenPGP key file to import", str(Path.home())
            )[0]
            msgbox_title = "OpenPGP public key import"
            try:
                if path:
                    with open(path, encoding="utf-8") as f:
                        crypt.import_keys(f.read(), self.app_data.config.gpg_store)
                    self.app_data.update_private_keys()
                    self.app_data.update_public_keys()
                    self.update_display_selected_pub_key()
                    open_info_msgbox(
                        "OpenPGP key has been imported successfully.",
                        title=msgbox_title,
                        parent=self,
                    )
            except (UnicodeDecodeError, UserError) as e:
                open_warning_msgbox(
                    "Error while importing PGP key.",
                    f"Detailed reason: {format(e)}",
                    title=msgbox_title,
                    parent=self,
                )

    def delete_keys(self) -> None:
        """Delete the selected public keys from the user's local keyring. Only
        public keys with no associated secret key can be deleted.
        """
        keys_to_delete = self.get_selected_keys()
        user_answer = open_message_box(
            "Do you really want to delete the following public key(s)?",
            "<br />".join([self.key_to_text(key) for key in keys_to_delete]),
            title="Delete public key",
            parent=self.parentWidget(),
            icon_type=QtWidgets.QMessageBox.Icon.Question,
            with_ok_cancel_buttons=True,
        )
        if user_answer == QtWidgets.QMessageBox.StandardButton.Ok:
            priv_keys = self.app_data.config.gpg_store.list_sec_keys()
            for key in keys_to_delete:
                if any(k for k in priv_keys if key.fingerprint == k.fingerprint):
                    open_warning_msgbox(
                        "Unable to delete key:",
                        f"{KeysTab.key_to_text(key)}",
                        "Deleting private keys (and by extension public keys "
                        "with an associated private key) is not supported by "
                        "this application. Please use an external software  "
                        "such as GnuPG (Linux, MacOS) or Kleopatra (Windows).",
                        title="PGP key deletion error",
                        parent=self.parentWidget(),
                    )
                    continue
                try:
                    crypt.delete_pub_keys(
                        [key.fingerprint], self.app_data.config.gpg_store
                    )
                    self.pub_keys_view.selectionModel().clearSelection()
                except UserError as e:
                    open_warning_msgbox(
                        "An error occurred while trying to delete key:",
                        f"{KeysTab.key_to_text(key)}",
                        f"Detailed reason: {format(e)}",
                        title="PGP key deletion error",
                        parent=self.parentWidget(),
                    )
                self.text_panel.clear()
        self.app_data.update_public_keys()

    def upload_key(self) -> None:
        """Uploads selected keys to keyserver specified in the user's config file."""
        key_send_message_box = NormalMessageBox(self.parentWidget(), "Send public key")
        cb = QtWidgets.QCheckBox(
            "Associate the key(s) with your identity (email).", key_send_message_box
        )
        cb.setToolTip(
            "The identity association/verification is done via email "
            "and handled by the keyserver."
            "<p>It only makes sense to verify keys you actually own.</p>"
        )
        cb.setChecked(True)
        key_send_message_box.setCheckBox(cb)
        key_send_message_box.setIcon(QtWidgets.QMessageBox.Icon.Question)
        key_send_message_box.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Ok
            | QtWidgets.QMessageBox.StandardButton.Cancel
        )

        keys_to_upload = self.get_selected_keys()
        key_send_message_box.set_text_list(
            (
                "Do you want to upload selected key(s) to the key server?",
                "<br />".join([self.key_to_text(key) for key in keys_to_upload]),
            )
        )
        if open_window(key_send_message_box) == QtWidgets.QMessageBox.StandardButton.Ok:
            for key in keys_to_upload:
                if (
                    verify_key_length(self.parentWidget(), key)
                    == QtWidgets.QMessageBox.StandardButton.Ok
                ):
                    run_thread(
                        upload_keys_workflow.upload_keys,
                        f_kwargs={
                            "fingerprints": [key.fingerprint],
                            "verify_key": cb.isChecked(),
                            "config": self.app_data.config,
                        },
                        capture_loggers=(upload_keys_workflow.logger,),
                        report_config=self.app_data.config,
                        forward_errors=warning_callback(
                            "OpenPGP certificate upload error"
                        ),
                        signals={
                            "result": lambda _: open_info_msgbox(
                                "OpenPGP certificate successfully uploaded to keyserver.",
                                title="Sent OpenPGP certificate",
                                parent=self.parentWidget(),
                            )
                        },
                    )

    def _update_display(self, index: QtCore.QModelIndex) -> None:
        """Display key info summary in GUI text panel."""
        style = (
            "<style>"
            "th {text-align: left; padding: 0 20px 5px 0;}"
            ".danger { color: red;}"
            ".safe { color: green;}"
            "</style>"
        )
        if index.isValid():
            try:
                # Note: it's probably possible to get rid of the cast() here.
                self.text_panel.setHtml(
                    style
                    + self.cert_to_html(
                        cast(KeyValueListModel, index.model()).get_value(index)
                    )
                    if not self.app_data.config.legacy_mode
                    else self.key_to_html(
                        cast(KeyValueListModel, index.model()).get_value(index)
                    )
                )
            except IndexError:
                self.text_panel.setHtml("")

    def update_display_selected_pub_key(self) -> None:
        """Refresh the displayed key info of the currently selected public keys."""
        self._update_display(self.pub_keys_view.selectionModel().currentIndex())


def verify_key_length(
    parent: QtWidgets.QWidget,
    key: Union[gpg.Key, CertInfo],
) -> int:
    """Verifies length and type of the given key.

    If some warning or error is caught, an additional popup (asking for user
    interaction) is displayed. If this is NOT the case, it simply return
    `QtWidgets.QMessageBox.Ok` (meaning everything is fine).
    """
    msg = NormalMessageBox(parent, "Key length verification")
    try:
        with warnings.catch_warnings(record=True) as warns:
            crypt.verify_key_length(key)
            if len(warns) > 0:
                logging.warning(warns[-1].message)
                msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                msg.setStandardButtons(
                    QtWidgets.QMessageBox.StandardButton.Ok
                    | QtWidgets.QMessageBox.StandardButton.Cancel
                )
                msg.setText(str(warns[-1].message))
    except UserError as exc:
        logging.error(str(exc))
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setText(str(exc))
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Cancel)
    return (
        open_window(msg)
        if len(msg.text())
        else int(QtWidgets.QMessageBox.StandardButton.Ok)
    )
