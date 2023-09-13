from typing import Sequence, Iterable

from gpg_lite.keyserver import VksEmailStatus, VksUploadResponse
from sett_rs.cert import CertInfo, CertStore, CertType

from ..core.crypt import (
    request_key_verification as crypt_request_key_verification,
    search_pub_key,
    upload_cert,
    upload_keys as crypt_upload_keys,
    verify_key_length,
)
from ..core.error import UserError
from ..utils.config import Config
from ..utils.log import create_logger, log_runtime_info

logger = create_logger(__name__)


@log_runtime_info(logger)
def verify_keylengths_and_upload_keys(
    fingerprints: Sequence[str], *, config: Config
) -> None:
    """Verify key lengths and upload keys"""
    keys = frozenset(
        search_pub_key(k, config.gpg_store, sigs=False) for k in fingerprints
    )
    for key in keys:
        verify_key_length(key)
    upload_keys(fingerprints=fingerprints, config=config)


@log_runtime_info(logger)
def upload_keys(
    fingerprints: Iterable[str],
    *,
    verify_key: bool = True,
    config: Config,
) -> None:
    """Uploads one or more public PGP keys to the keyserver specified in the
    config. Triggers a verification if the status returned by the keyserver is
    appropriate.

    Note that we assume that each key contains one single UID (email address).
    """
    if config.keyserver_url is None:
        raise UserError("Keyserver URL is undefined.")

    def handle_response(response: VksUploadResponse, email: str, key_id: str) -> None:
        if email in response.status:
            if (
                response.status[email]
                in (
                    VksEmailStatus.UNPUBLISHED,
                    VksEmailStatus.PENDING,
                )
                and verify_key
            ):
                logger.info("Requesting verification for '%s'", email)
                crypt_request_key_verification(
                    response.token, email, config.keyserver_url
                )
            if response.status[email] == VksEmailStatus.REVOKED:
                raise UserError(f"'{key_id}' is revoked and can NOT be used.")

    if not config.legacy_mode:
        for cert_armored in [
            CertStore().export_cert(f, CertType.Public) for f in fingerprints
        ]:
            cert = CertInfo.from_bytes(cert_armored)
            if not cert.uids or not cert.email:
                raise UserError(
                    f"The selected certificate '{cert}' does NOT contain UID or email."
                )
            logger.info("Uploading certificate '%s'", cert.key_id)
            response = upload_cert(
                cert_armored.decode("utf-8"), keyserver=config.keyserver_url
            )
            handle_response(response, cert.email, cert.key_id)
    else:
        for key in frozenset(
            search_pub_key(k, config.gpg_store, sigs=False) for k in fingerprints
        ):
            logger.info("Uploading key '%s'", key.key_id)
            if not key.uids or not key.uids[0].email:
                raise UserError(
                    f"The selected key '{key}' does NOT contain UID or email."
                )
            (response,) = crypt_upload_keys(
                [key.fingerprint],
                keyserver=config.keyserver_url,
                gpg_store=config.gpg_store,
            )
            handle_response(response, key.uids[0].email, key.key_id)
