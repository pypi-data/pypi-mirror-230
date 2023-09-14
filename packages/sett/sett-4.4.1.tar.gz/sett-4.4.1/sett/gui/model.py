from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Hashable,
    Iterable,
    List,
    Optional,
    Tuple,
    Dict,
    Union,
    Sequence,
    Type,
    cast,
    TYPE_CHECKING,
)

from sett_rs.cert import CertInfo, CertStore, CertType
from libbiomedit.portal import KeyStatus

from .listener import ClassWithListener
from .listener import ListenerWrap
from .pyside import QtCore
from ..core import gpg
from ..core.metadata import Purpose
from ..core.secret import Secret
from ..protocols import Protocol, sftp, liquid_files, s3
from ..utils.config import Config

INDEX_UNION_TYPE = Union[QtCore.QModelIndex, QtCore.QPersistentModelIndex]

# Default value Qt.DisplayRole for index is not an int (upstream issue).
default_display_role = cast(int, QtCore.Qt.ItemDataRole.DisplayRole)


class TableModel(QtCore.QAbstractTableModel):
    def __init__(
        self,
        data: Sequence[Sequence[Any]] = (),
        columns: Optional[Tuple[str, ...]] = None,
    ):
        super().__init__()
        self.set_data(data or tuple(tuple()))
        self.columns = columns or tuple(map(str, range(self.columnCount())))

    @property
    def columns(self) -> Tuple[str, ...]:
        return self._columns

    @columns.setter
    def columns(self, values: Sequence[str]) -> None:
        self._columns = tuple(values)

    def get_data(self) -> Tuple[Sequence[Any], ...]:
        return self._data

    def set_data(self, data: Sequence[Sequence[Any]]) -> None:
        self._data = tuple(sorted(tuple(x) for x in data))
        self.layoutChanged.emit()
        self.dataChanged.emit(
            self.createIndex(0, 0),
            self.createIndex(self.rowCount(), self.columnCount()),
        )

    def rowCount(self, _parent: INDEX_UNION_TYPE = QtCore.QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _parent: INDEX_UNION_TYPE = QtCore.QModelIndex()) -> int:
        return len(self._data) and len(self._data[0])

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        role: int = default_display_role,
    ) -> Optional[str]:
        if (
            orientation == QtCore.Qt.Orientation.Horizontal
            and role == default_display_role
        ):
            return self._columns[section]
        if (
            orientation == QtCore.Qt.Orientation.Vertical
            and role == default_display_role
        ):
            return str(section)
        return None

    def data(
        self, index: INDEX_UNION_TYPE, role: int = default_display_role
    ) -> Optional[Any]:
        if role == default_display_role:
            return self._data[index.row()][index.column()]
        return None

    def removeRows(
        self, row: int, count: int, _parent: INDEX_UNION_TYPE = QtCore.QModelIndex()
    ) -> bool:
        if row > -1 and row + count <= self.rowCount():
            self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
            self.set_data(self.get_data()[:row] + self.get_data()[row + count :])
            self.endRemoveRows()
            return True
        return False


class KeyValueListModel(QtCore.QAbstractListModel):
    """List model extension for key-value objects."""

    def __init__(
        self,
        *args: Any,
        data: Optional[Iterable[Tuple[Hashable, Any]]] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.set_data(data or [])

    def set_data(self, data: Iterable[Tuple[Hashable, Any]]) -> None:
        self._keyvalues = dict(data)
        self._keys = list(self._keyvalues.keys())
        self.layoutChanged.emit()

    def get_data(self) -> Dict[Hashable, Any]:
        return self._keyvalues

    # Default value Qt.DisplayRole for index is not an int (upstream issue):
    def data(self, index, role) -> Optional[Hashable]:  # type: ignore
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            key: Hashable = self._keys[index.row()]
            return key
        return None

    def rowCount(self, _parent: INDEX_UNION_TYPE = QtCore.QModelIndex()) -> int:
        return len(self._keys)

    def get_value(self, index: Union[int, QtCore.QModelIndex]) -> Any:
        if isinstance(index, int):
            return self._keyvalues[self._keys[index]]
        if isinstance(index, QtCore.QModelIndex):
            return self._keyvalues[self._keys[index.row()]]
        raise TypeError("Wrong index type for index.")


def protocol_factory() -> Dict[Type[Protocol], ListenerWrap[Protocol]]:
    return {
        sftp.Protocol: ListenerWrap(new_sftp_connection()),
        s3.Protocol: ListenerWrap(new_s3_connection()),
        liquid_files.Protocol: ListenerWrap(new_liquid_files_connection()),
    }


def new_sftp_connection() -> Protocol:
    return sftp.Protocol(host="", username="", destination_dir="")


def new_s3_connection() -> Protocol:
    return s3.Protocol(  # nosec
        host="",
        secure=True,
        bucket="",
        access_key="",
        secret_key=Secret(""),
        session_token="",
    )


def new_liquid_files_connection() -> Protocol:
    return liquid_files.Protocol(host="", api_key=Secret(""))


# Trick the type-checker into thinking that ConfigProxy is a Config object, so
# that it recognizes the methods/attribute calls made to ConfigProxy as methods
# and calls made to Config. This will not impact the code at runtime.
if TYPE_CHECKING:
    base = Config
else:
    base = object


class ConfigProxy(ListenerWrap[Config], base):
    """Proxy between the Config dataclass and the UI."""

    def set_value(self, attr: str, val: Any) -> None:
        """Updates the specified sett config attribute (attr) with a new value."""
        if val != getattr(self, attr):
            super().set_value(attr, val)
            self._trigger(attr)

    def refresh(self) -> None:
        self._trigger_all()

    def set_config(self, cfg: Config) -> None:
        """Sets/Updates the in-memory config values with the new values passed
        in "cfg". Then updates the Settings Tab widgets in the UI.
        """
        self._target = cfg
        self.refresh()

    def get_config(self) -> Config:
        """Returns the current in-memory config values."""
        return self.target


@dataclass
class AppData(ClassWithListener):
    """Settings that are specific to the sett GUI."""

    config: ConfigProxy

    encrypt_sender: Optional[str] = None
    encrypt_recipients: Tuple[str, ...] = ()
    encrypt_transfer_id: Optional[int] = None
    encrypt_purpose: Optional[Purpose] = None
    encrypt_compression_level: int = 6
    encrypt_output_location: Path = field(default_factory=Path.home)
    encrypt_files: List[str] = field(default_factory=list)
    encrypt_package_name_suffix: str = ""
    encrypt_ignore_disk_space_error: bool = False

    decrypt_decrypt_only: bool = False
    decrypt_output_location: Path = field(default_factory=Path.home)
    decrypt_files: List[str] = field(default_factory=list)

    transfer_protocol_type: Type[Protocol] = sftp.Protocol
    transfer_protocol_args: Dict[Type[Protocol], ListenerWrap[Protocol]] = field(
        default_factory=protocol_factory
    )
    transfer_files: QtCore.QStringListModel = field(
        default_factory=QtCore.QStringListModel
    )

    priv_keys_model: KeyValueListModel = field(default_factory=KeyValueListModel)
    pub_keys_model: KeyValueListModel = field(default_factory=KeyValueListModel)
    pub_key_status: Dict[str, KeyStatus] = field(default_factory=dict)
    encrypt_recipients_model: TableModel = field(
        default_factory=lambda: TableModel(columns=("Name", "Email", "Fingerprint"))
    )
    default_key_index: Optional[int] = None

    def update_private_keys(self) -> None:
        """Retrieve/reload all private keys from the user's local keyring and
        store them in the application's memory.
        """
        if not self.config.legacy_mode:
            certs = CertStore().list_certs(CertType.Secret)
            try:
                self.default_key_index = next(
                    index
                    for index, entry in enumerate(certs)
                    if entry.fingerprint == self.config.default_sender
                )
                self.encrypt_sender = self.config.default_sender
            except StopIteration:
                pass
            self.priv_keys_model.set_data(data=certs_as_tuple(certs))
        else:
            keys_private = self.config.gpg_store.list_sec_keys()
            try:
                default_key = (
                    self.config.default_sender or self.config.gpg_store.default_key()
                )
                self.default_key_index = next(
                    index
                    for index, entry in enumerate(keys_private)
                    if entry.fingerprint == default_key
                )
                self.encrypt_sender = default_key
            except StopIteration:
                pass
            self.priv_keys_model.set_data(data=keys_as_tuple(keys=keys_private))
        self.priv_keys_model.endResetModel()

    def update_public_keys(self) -> None:
        """Retrieve/reload all public keys from the user's local keyring and
        store them in the application's memory.
        """

        if not self.config.legacy_mode:
            certs = CertStore().list_certs(CertType.Public)
            self.pub_keys_model.set_data(data=certs_as_tuple(certs))
        else:
            keys_public = self.config.gpg_store.list_pub_keys(sigs=True)
            self.pub_keys_model.set_data(data=keys_as_tuple(keys=keys_public))
        self.pub_keys_model.endResetModel()

        # Go through the list of currently selected data recipients (displayed
        # in the encrypt tab) to make sure all keys are still present. If a
        # selected key is no longer available, it gets removed.
        available_pub_keys = [
            k.fingerprint for k in self.pub_keys_model.get_data().values()
        ]
        for index, row in list(enumerate(self.encrypt_recipients_model.get_data()))[
            ::-1
        ]:
            fingerprint = row[2]
            if fingerprint not in available_pub_keys:
                self.encrypt_recipients_model.removeRow(index)

    def update_key_approval_status(self) -> None:
        """Check whether public keys from the user's local keyring are approved
        in the portal and store/update this information in the application's
        memory.
        If no keys are present in the user's local PGP keyring, the request to
        the Portal's API is skipped.
        """
        if self.config.verify_key_approval:
            if not self.config.legacy_mode:
                fingerprints = [
                    cert.fingerprint for cert in CertStore().list_certs(CertType.Public)
                ]
            else:
                fingerprints = [
                    k.fingerprint for k in self.config.gpg_store.list_pub_keys()
                ]
            self.pub_key_status = (
                self.config.portal_api.get_key_status(fingerprints)
                if fingerprints
                else {}
            )

    def __post_init__(self) -> None:
        super().__init__()
        if self.config.output_dir:
            self.encrypt_output_location = Path(self.config.output_dir)
            self.decrypt_output_location = Path(self.config.output_dir)
        if self.config.compression_level is not None:
            self.encrypt_compression_level = self.config.compression_level
        if self.config.package_name_suffix is not None:
            self.encrypt_package_name_suffix = self.config.package_name_suffix
        self.transfer_verify_package_name = self.config.verify_package_name
        self.update_private_keys()
        self.update_public_keys()


def keys_as_tuple(keys: Sequence[gpg.Key]) -> Iterable[Tuple[str, gpg.Key]]:
    """Returns a generator of tuples of the form ("userID keyID", key)."""
    return ((f"{key.uids[0]} {key.key_id}", key) for key in keys)


def certs_as_tuple(
    certs: Sequence[CertInfo],
) -> Iterable[Tuple[str, CertInfo]]:
    """Returns a generator of tuples of the form ("userID keyID", cert)."""
    return (
        (f"{'' if cert.uid is None else str(cert.uid)} {cert.key_id}", cert)
        for cert in certs
    )
