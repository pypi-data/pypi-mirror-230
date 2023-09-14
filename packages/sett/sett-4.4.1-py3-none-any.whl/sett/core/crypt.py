import enum
import io
import re
import warnings
from functools import partial, wraps
from typing import (
    IO,
    Any,
    Callable,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from libbiomedit import crypt
from sett_rs.cert import (
    CertInfo,
    CertStore,
    CertType,
    generate_cert,
    create_revocation_signature as _create_revocation_signature,
)

from . import gpg
from .error import UserError
from .request import urlopen
from .secret import Secret, reveal
from ..utils.config import Config

GPGStore = gpg.GPGStore
ExceptionType = Union[Type[BaseException], Tuple[Type[BaseException], ...]]

R = TypeVar("R")


def to_user_error(
    error_types: ExceptionType,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """A decorator to turn errors of type :error_types: into UserError."""

    def _to_user_error(f: Callable[..., R]) -> Callable[..., R]:
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any) -> R:
            try:
                return f(*args, **kwargs)
            except error_types as e:
                raise UserError(format(e)) from e

        return wrapped

    return _to_user_error


verify_metadata_signature = to_user_error(RuntimeError)(
    partial(crypt.verify_metadata_signature, url_opener=urlopen)
)
create_revocation_signature = to_user_error(RuntimeError)(_create_revocation_signature)


@to_user_error((RuntimeError, gpg.GPGError))
def retrieve_refresh_and_validate_keys(
    key_identifiers: Iterable[str], config: Config
) -> Tuple[gpg.Key, ...]:
    """Performs the following tasks on the keys matching the specified
    `key_identifiers`:
     * Retrieve and/or refresh the keys from the keyserver specified in the
       applications config file.
     * Verifies that the keys are approved by the key validation authority.
       This check is skipped if `config.verify_key_approval` is `False`.
    """

    # Retrieve and/or refresh keys from the keyserver.
    keys = tuple(
        crypt.retrieve_and_refresh_keys(
            key_identifiers=key_identifiers,
            gpg_store=config.gpg_store,
            keyserver_url=config.keyserver_url,
            allow_key_download=config.allow_gpg_key_autodownload,
            url_opener=urlopen,
        )
    )

    # Verify that all keys are approved by the central authority (via a call
    # to portal).
    if config.verify_key_approval:
        config.portal_api.verify_key_approval(
            fingerprints=(key.fingerprint for key in keys)
        )
    return keys


@to_user_error(gpg.GPGError)
def import_keys(key_data: str, gpg_store: GPGStore) -> None:
    """Import keys from text."""
    return gpg_store.import_file(key_data.encode())


@to_user_error(gpg.GPGError)
def delete_pub_keys(fingerprints: List[str], gpg_store: GPGStore) -> None:
    """Delete public key."""
    return gpg_store.delete_pub_keys(*fingerprints)


@to_user_error(gpg.GPGError)
def create_revocation_certificate(
    fingerprint: str, passphrase: str, gpg_store: GPGStore
) -> bytes:
    """Create a revocation certificate for the key."""
    return gpg_store.gen_revoke(fingerprint, passphrase=passphrase)


class KeyAlgorithm(enum.Enum):
    """Encryption algorithm used in public PGP keys.
    The numeric values associated to algorithms follow the GnuPG settings.
    """

    RSA = 1
    DSA = 2
    ECC = 22


def verify_key_length(
    key: Union[gpg.Key, CertInfo], min_key_length: int = 4096
) -> None:
    """Verify that the type (algorithm) of a PGP keys is strong enough."""

    allowed_key_description = (
        f"Only RSA (min. key length: {min_key_length}) and ECC keys are allowed"
    )

    try:
        algorithm = (
            KeyAlgorithm(key.pub_key_algorithm)
            if isinstance(key, gpg.Key)
            else KeyAlgorithm(key.primary_key.pub_key_algorithm)
        )
    except ValueError as e:
        raise UserError(
            f"OpenPGP key {key.key_id} is using a forbidden algorithm. "
            f"{allowed_key_description}."
        ) from e

    if algorithm == KeyAlgorithm.DSA:
        raise UserError(
            f"Non-allowed PGP key algorithm: key {key.key_id} is of type DSA. "
            f"{allowed_key_description}."
        )
    key_length = (
        key.key_length if isinstance(key, gpg.Key) else key.primary_key.length or 0
    )
    if algorithm == KeyAlgorithm.RSA and key_length < min_key_length:
        raise UserError(
            f"OpenPGP key {key.key_id} is shorter than the required minimal "
            f"length. {allowed_key_description}."
        )
    if algorithm == KeyAlgorithm.ECC:
        warnings.warn(
            f"Please note: key {key.key_id} is of type ECC, which is not "
            "supported by older versions of GnuPG."
        )


@to_user_error((gpg.KeyserverError, gpg.KeyserverOtherError))
def request_key_verification(
    token: str, address: str, keyserver: str
) -> gpg.keyserver.VksUploadResponse:
    """Triggers a verification email from the keyserver for given token."""
    return gpg.keyserver.vks_request_verify(token, [address], keyserver)


@to_user_error((gpg.KeyserverError, gpg.KeyserverOtherError))
def upload_keys(
    fingerprints: List[str], keyserver: str, gpg_store: GPGStore
) -> Tuple[gpg.keyserver.VksUploadResponse, ...]:
    """Upload public keys to keyserver."""
    return tuple(
        gpg_store.vks_send_key(fingerprint, keyserver=keyserver)
        for fingerprint in fingerprints
    )


@to_user_error((gpg.KeyserverError, gpg.KeyserverOtherError))
def upload_cert(
    ascii_armored_cert: str, keyserver: str
) -> gpg.keyserver.VksUploadResponse:
    """Upload an OpenPGP certificate to a verifying keyserver (VKS)."""
    return gpg.keyserver.vks_upload_key(ascii_armored_cert, keyserver=keyserver)


@to_user_error(
    (gpg.KeyserverError, gpg.KeyserverOtherError, gpg.KeyserverKeyNotFoundError)
)
def download_keys(
    key_identifiers: List[str], keyserver: str, gpg_store: GPGStore
) -> None:
    """Download public keys from a verifying keyserver (VKS)."""
    for key_identifier in key_identifiers:
        gpg_store.vks_recv_key(key_identifier, keyserver=keyserver)


@to_user_error(
    (gpg.KeyserverError, gpg.KeyserverOtherError, gpg.KeyserverKeyNotFoundError)
)
def download_cert(keyserver: str, identifier: str) -> bytes:
    """Download a public certificate from a verifying keyserver (VKS)."""
    with gpg.keyserver.vks_get_key_by_any_identifier(
        keyserver=keyserver, identifier=identifier
    ) as response:
        return response.read()


def detach_sign_file(
    src: Union[bytes, IO[bytes]],
    signature_fingerprint: str,
    passphrase: Secret[str],
    gpg_store: GPGStore,
) -> bytes:
    """Sign a file with a detached signature."""
    try:
        with gpg_store.detach_sig(
            src, passphrase.reveal(), signature_fingerprint
        ) as out:
            return out.read()
    except gpg.GPGError as e:
        raise UserError(f"File signing failed. {e}") from e


def enforce_passphrase(passphrase: Optional[Secret[str]]) -> Secret[str]:
    """Verify that a passphrase is not empty, and return it."""
    if passphrase is None:
        raise ValueError("No password given")
    return passphrase


def check_password(
    password: Secret[str], key_fingerprint: str, gpg_store: GPGStore
) -> None:
    """Verify that the provided password matches the specified PGP key.

    The verification is done by trying to use the key specified via its
    fingerprint to sign some mock data. If this operation fails, the password
    is incorrect and an error is raised.
    """
    try:
        with gpg_store.detach_sig(
            src=b"test", passphrase=password.reveal(), signee=key_fingerprint
        ):
            pass
    except gpg.GPGError:
        raise UserError("GPG password is incorrect") from None


def check_password_matches_any_key(
    password: Secret[str], keys: Iterable[gpg.Key], gpg_store: GPGStore
) -> None:
    """Check whether a password matches any of the provided GPG keys.

    If the password does not match with any of the keys, an error is raised.

    :param keys: list of GPG keys to check.
    :param password: password to check against the different keys.
    :param gpg_store: GnuPG database containing the keys to check.
    :raises UserError:
    """
    for key in keys:
        try:
            check_password(
                password=password,
                key_fingerprint=key.fingerprint,
                gpg_store=gpg_store,
            )
            break
        except UserError:
            pass
    else:
        raise UserError(
            "The provided password does not match any of the GPG keys with "
            "which the data was encrypted"
        )


class KeyType(enum.Enum):
    public = enum.auto()
    secret = enum.auto()


class UnpackError(UserError):
    """Error class that displays an error message for the cases when a search
    for a public/secret key on the user's local keyring does not yield exactly
    one match.
    """

    def __init__(self, keys: Sequence[gpg.Key], key_type: KeyType, search_value: str):
        if not keys:
            msg_start = f"No {key_type.name} key"
        else:
            msg_start = f"Multiple {key_type.name} keys"
        super().__init__(msg_start + f" matching: {search_value}")


def search_pub_key(search_term: str, gpg_store: GPGStore, sigs: bool = True) -> gpg.Key:
    """Search for exactly one public key in the user's local keyring.

    :param gpg_store: key database as gnupg object.
    :param search_term: search term for the key, e.g. fingerprint or key owner
        email address.
    :param sigs: if True, return key with signatures.
    :return: PGP key matching the search term.
    :raises UnpackError: if either no or more than one key is matching the
        search term.
    """
    keys = gpg_store.list_pub_keys(search_terms=(search_term,), sigs=sigs)
    try:
        (key,) = keys
    except ValueError:
        raise UnpackError(
            keys, key_type=KeyType.public, search_value=search_term
        ) from None
    return key


def search_priv_key(search_term: str, gpg_store: GPGStore) -> gpg.Key:
    """Searches the user's local keyring for a secret key matching the search
    term. Raises an error if either no or more than one key are found.
    """
    keys = gpg_store.list_sec_keys(search_terms=(search_term,))
    try:
        (key,) = keys
    except ValueError:
        raise UnpackError(
            keys, key_type=KeyType.secret, search_value=search_term
        ) from None
    return key


def encrypt_and_sign(
    source: gpg.cmd.ISource,
    output: gpg.cmd.OSource,
    gpg_store: GPGStore,
    recipients_fingerprint: List[str],
    signature_fingerprint: str,
    passphrase: Secret[str],
    always_trust: bool = True,
) -> None:
    """Encrypt input data with a PGP public key and sign it with a private key.

    In this function, the compression level of the "encrypt()" method is set
    to 0 as we are only encrypting data that has already been compressed, or
    has explicitly been requested by the user not to be compressed.

    There is no check of the validity of the sender and recipient keys, as it
    is assumed that this is already done earlier.

    :param source: callable writing data to encrypt.
    :param output: callable reading encrypted data.
    :param gpg_store: directory containing GnuPG keyrings as gnupg object.
    :param recipients_fingerprint: fingerprint of public key(s) with which
        the data should be encrypted.
    :param signature_fingerprint: fingerprint of private PGP key with which to
        sign the data.
    :param passphrase: password of private PGP key. Needed to sign the data.
    :param always_trust: if False, the encryption key must be signed by the
        local user.
    :raises UserError:
    """
    try:
        # Note: gpg.CompressAlgo.NONE evaluates to "uncompressed", which
        # tells GnuPG to not compress the input data.
        gpg_store.encrypt(
            source=source,
            recipients=recipients_fingerprint,
            output=output,
            sign=signature_fingerprint,
            passphrase=reveal(passphrase),
            trust_model=gpg.TrustModel.always if always_trust else gpg.TrustModel.pgp,
            compress_algo=gpg.CompressAlgo.NONE,
        )
    except gpg.GPGError as e:
        # Note: this function is only called from the encryption workflow after
        # checking that the password of the sender's key is correct.
        # As a result, the GPG error should never be triggered by a wrong password.
        msg = ["Encryption failed."]
        if not always_trust:
            msg.append(
                "If the recipient key is not 'Trusted', you need to either "
                "sign it with an external tool (e.g. GnuPG) or enable "
                "'Always trust recipient key' in the settings."
            )
        msg.append(f"Original error: {e}")
        raise UserError(" ".join(msg)) from e


def get_recipient_email(key: Union[gpg.Key, CertInfo]) -> str:
    """Retrieve the email address associated with a PGP key, and generate a
    an error if the email address is missing or could not be retrieved.
    """
    try:
        email = key.uids[0].email
    except (IndexError, UnpackError):
        raise UserError(
            f"Could not determine email address for PGP key {key.key_id}."
        ) from None
    if not email:
        raise UserError(
            f"PGP key [{key.key_id}] does not contain a valid email address."
        )
    return email


def decrypt(
    source: gpg.cmd.ISource,
    output: Union[str, gpg.cmd.OSource],
    gpg_store: GPGStore,
    passphrase: Optional[Secret[str]],
) -> List[str]:
    """Decrypt data.

    :param source: data to decrypt.
    :param output: file where the decrypted data should be written to.
    :param gpg_store: directory containing GnuPG keyrings as gnupg object.
    :param passphrase: password of the PGP decryption key (recipient key).
    :return: fingerprint or keyid of the signee's key.
    :raises UserError: if the data could not be decrypted.
    """
    try:
        if isinstance(output, str):
            with open(output, "wb") as output_file:
                sender_fingerprints = gpg_store.decrypt(
                    source=source,
                    output=cast(io.FileIO, output_file),
                    passphrase=reveal(passphrase),
                )
        else:
            sender_fingerprints = gpg_store.decrypt(
                source=source, output=output, passphrase=reveal(passphrase)
            )
    except gpg.GPGError as e:
        raise UserError(
            "Failed to decrypt. Error message from gpg:\n" + format(e)
        ) from e
    if not sender_fingerprints:
        warnings.warn("Encrypted package is not signed by the sender")
    elif len(sender_fingerprints) > 1:
        warnings.warn(
            "Encrypted package has multiple signatures. "
            "This is not compliant with the BiomedIT Protocol"
        )
    return sender_fingerprints


def create_key(
    name: str,
    email: str,
    pwd: Secret[str],
    gpg_store: GPGStore,
    comment: Optional[str] = None,
    key_type: str = "RSA",
    key_length: int = 4096,
) -> gpg.Key:
    """Create a new PGP public/private key."""

    min_pwd_len = 10
    if len(name) < 5:
        raise UserError("Full name must be at least 5 characters long.")
    if not re.search(r"[^@]+@[^@]+\.[^@]+", email):
        raise UserError("Invalid email address.")
    if len(pwd.reveal()) < min_pwd_len:
        raise UserError("Password is too short (min length: " f"{min_pwd_len})")
    fingerprint = gpg_store.gen_key(
        key_type=key_type,
        key_length=key_length,
        full_name=name + (f" ({comment})" if comment else ""),
        email=email,
        passphrase=pwd.reveal(),
    )
    pkey = gpg_store.list_sec_keys(search_terms=(fingerprint,))
    if not pkey:
        raise UserError(f"No private keys found for: {fingerprint}")
    if len(pkey) > 1:
        raise UserError(f"Multiple private keys found for: {fingerprint}")
    return pkey[0]


@to_user_error(RuntimeError)
def generate_and_import_certificate(
    name: str,
    email: str,
    password: Secret[str],
    comment: Optional[str] = None,
) -> Tuple[bytes, bytes]:
    min_pwd_len = 10
    if len(name) < 5:
        raise UserError("Full name must be at least 5 characters long.")
    if not re.search(r"[^@]+@[^@]+\.[^@]+", email):
        raise UserError("Invalid email address.")
    if len(password.reveal()) < min_pwd_len:
        raise UserError("Password is too short (min length: " f"{min_pwd_len})")
    (cert, rev_sig) = generate_cert(
        uid=f"{name} {f'({comment}) ' if comment else ''}<{email}>",
        password=password.reveal().encode("utf8"),
    )
    CertStore().import_cert(cert, CertType.Secret)
    return (cert, rev_sig)


@to_user_error(RuntimeError)
def revoke_certificate(rev_sig: bytes) -> None:
    CertStore().revoke(rev_sig)
