import os
import json
from functools import partial
from typing import List, Optional

import sett_rs
from sett_rs.cert import CertInfo, CertStore, CertType

from ..core import gpg
from ..core.archive import (
    check_package,
    extract,
    unpack_from_stream,
    DATA_ARCHIVE,
    DATA_FILE_ENCRYPTED,
    CHECKSUM_FILE,
    extract_with_progress,
)
from ..core.crypt import (
    check_password_matches_any_key,
    decrypt as core_decrypt,
    enforce_passphrase,
    retrieve_refresh_and_validate_keys,
    verify_metadata_signature,
)
from ..core.filesystem import (
    DeleteDirOnError,
    get_compression_stats,
    get_total_size,
    to_human_readable_size,
    unique_filename,
    check_space,
)
from ..core.checksum import verify_checksums, read_checksum_file
from ..core.metadata import METADATA_FILE, load_metadata
from ..core.secret import Secret
from ..core.error import UserError
from ..utils.log import create_logger, log_runtime_info, log_timing
from ..utils.progress import ProgressInterface, subprogress
from ..utils.config import Config

logger = create_logger(__name__)
logger_rs = create_logger("sett.decrypt")


@log_timing(logger)
@log_runtime_info(logger)
def decrypt(
    files: List[str],
    *,
    passphrase: Optional[Secret[str]] = None,
    output_dir: str,
    config: Config,
    decrypt_only: bool = False,
    dry_run: bool = False,
    progress: Optional[ProgressInterface] = None,
) -> None:
    """Main function of the decrypt workflow. Decrypts and decompresses the
    input archive files.
    """

    with logger.log_task(
        f"Input data verification{' (dry_run)' if dry_run else ''}..."
    ):
        # Verify input data packages extension and content.
        logger.info("Files to decrypt: %s", ", ".join(files))
        logger.info("Output directory: %s", output_dir)
        for archive_path in files:
            logger.info("Verifying: %s", archive_path)
            check_package(archive_path)

        # Verify sufficient disk space is available.
        check_space(get_total_size(files), output_dir, force=False)

    if dry_run:
        logger.info("Dry run completed successfully.")
        return

    for archive_file in files:
        with logger.log_task(f"Processing file: {archive_file}..."):
            # Reset progress bar for each archive file.
            if progress is not None:
                progress.update(0.0)

            if not config.legacy_mode:
                decrypt_archive(
                    archive_file,
                    passphrase=passphrase,
                    output_dir=output_dir,
                    config=config,
                    decrypt_only=decrypt_only,
                    progress=progress,
                )
            else:
                decrypt_archive_gnupg(
                    archive_file,
                    passphrase=passphrase,
                    output_dir=output_dir,
                    config=config,
                    decrypt_only=decrypt_only,
                    progress=progress,
                )


def decrypt_archive(
    archive_file: str,
    passphrase: Optional[Secret[str]],
    output_dir: str,
    config: Config,
    decrypt_only: bool = False,
    progress: Optional[ProgressInterface] = None,
) -> None:
    """Decrypts and decompresses a data package using sett-rs."""

    # Retrieve data recipients from metadata.
    with extract(archive_file, METADATA_FILE) as f_data:
        passphrase = enforce_passphrase(passphrase)
        metadata = load_metadata(json.load(f_data))
        logger.debug("Recipients: %s", ", ".join(metadata.recipients))
        store = CertStore()
        recipients_certs = []
        for recipient_fp in metadata.recipients:
            try:
                recipients_certs.append(
                    store.export_cert(recipient_fp, CertType.Secret)
                )
            except RuntimeError as e:
                logger.debug("Unable to retrieve recipient's certificate: %s", e)
        if not recipients_certs:
            raise UserError(
                "No secret key was found that is able to decrypt the data. "
                "Please make sure your secret key is present on the local "
                "machine and that the data was encrypted for you."
            )
        logger.info(
            "Data encrypted for: %s",
            ", ".join(
                f"{cert_info.uid} ({cert_info.fingerprint})"
                for cert_info in (
                    CertInfo.from_bytes(cert) for cert in recipients_certs
                )
            ),
        )
        try:
            sender_cert = store.export_cert(metadata.sender, CertType.Public)
        except RuntimeError as e:
            raise UserError(f"Unable to retrieve sender's key: {e}") from e

    # Decrypt data.
    try:
        sett_rs.workflow.decrypt(
            opts=sett_rs.workflow.DecryptOpts(
                file=archive_file,
                recipients=recipients_certs,
                signer=sender_cert,
                password=passphrase.reveal(),
                dry_run=False,
                decrypt_only=decrypt_only,
                output=output_dir,
                max_cpu=config.max_cpu,
            ),
            progress=progress.update if progress is not None else None,
        )
    except RuntimeError as e:
        # Note: sett-rs also outputs a warning regarding the wrong password,
        # but as it is emitted as a warning rather than an error, it is not
        # being captured by sett GUI (for the CLI it works), hence we need
        # an somewhat verbose error message here.
        raise UserError(
            f"Unable to decrypt data: {e}. Make sure that you entered the "
            "correct password and that the data was encrypted with the "
            "correct PGP key"
        ) from e


def decrypt_archive_gnupg(
    archive_file: str,
    passphrase: Optional[Secret[str]],
    output_dir: str,
    config: Config,
    decrypt_only: bool = False,
    progress: Optional[ProgressInterface] = None,
) -> None:
    """Decrypts and decompresses the input archive_file."""

    # To avoid overwriting files, each archive is unpacked in a directory
    # that has the same name as the archive file minus its extension.
    out_dir = unique_filename(
        os.path.splitext(os.path.join(output_dir, os.path.basename(archive_file)))[0]
    )
    with DeleteDirOnError(out_dir):
        # Verify that the detached signature on the metadata.json file is
        # valid, and that the fingerprint matches the sender fingerprint
        # from the metadata file.
        # Note: this does **not** verify that the data sender's key is
        # approved by the key approval authority, but that doesn't matter
        # because it gets checked later in the function.
        logger.info("Verifying signatures")
        verify_metadata_signature(
            tar_file=archive_file,
            gpg_store=config.gpg_store,
            keyserver_url=config.keyserver_url,
            allow_key_download=config.allow_gpg_key_autodownload,
        )

        # Find the secret key(s) for which the data was encrypted in the
        # user's local keyring.
        logger.info("Verifying decryption keys")
        with extract(archive_file, DATA_FILE_ENCRYPTED) as f_data:
            secret_keys = config.gpg_store.list_sec_keys(gpg.extract_key_id(f_data))
            if not secret_keys:
                raise UserError(
                    "No secret key able to decrypt the data was found. "
                    "Please make sure your secret key is present on the local "
                    "machine and that the data was encrypted for you."
                )
            logger.info(
                "Data encrypted for: %s",
                ", ".join(f"{key.uids[0]} ({key.fingerprint})" for key in secret_keys),
            )
            check_password_matches_any_key(
                password=enforce_passphrase(passphrase),
                keys=secret_keys,
                gpg_store=config.gpg_store,
            )

        # Decrypt and decompress input files.
        logger.info("Decrypting data")
        unpacked_files: List[str] = []
        with subprogress(
            progress, step_completion_increase=0.95
        ) as scaled_progress, extract_with_progress(
            archive_file, scaled_progress, DATA_FILE_ENCRYPTED
        ) as f_data:
            os.makedirs(out_dir, exist_ok=True)
            sender_fingerprint = core_decrypt(
                source=f_data,
                output=os.path.join(out_dir, DATA_ARCHIVE)
                if decrypt_only
                else partial(unpack_from_stream, dest=out_dir, content=unpacked_files),
                gpg_store=config.gpg_store,
                passphrase=passphrase,
            )
            sender_key = retrieve_refresh_and_validate_keys(
                key_identifiers=sender_fingerprint,
                config=config,
            )
            logger.info(
                "Data signed by: %s",
                ", ".join(f"{key.uids[0]} ({key.fingerprint})" for key in sender_key),
            )

        # Compute decrypted data size and checksum verification (if data was
        # decompressed).
        with subprogress(progress, step_completion_increase=0.05) as scaled_progress:
            if decrypt_only:
                decryption_stats = "size: " + to_human_readable_size(
                    os.path.getsize(archive_file)
                )
            else:
                logger.info("Checksum verification of uncompressed data")
                with open(os.path.join(out_dir, CHECKSUM_FILE), "rb") as f:
                    # Path separator replacement is a fail-safe if paths are
                    # not POSIX.
                    verify_checksums(
                        [
                            (c, os.path.join(out_dir, p.replace("\\", os.path.sep)))
                            for c, p in read_checksum_file(f)
                        ],
                        # `max_workers` accepts only None and positive integers.
                        max_workers=config.max_cpu if config.max_cpu > 0 else None,
                    )
                log_files(unpacked_files)
                decryption_stats = get_compression_stats(
                    os.path.getsize(archive_file),
                    get_total_size(os.path.join(out_dir, f) for f in unpacked_files),
                    compression=False,
                )
            if scaled_progress is not None:
                scaled_progress.update(1.0)
            logger.info(
                "Completed data decryption: %s [%s]", archive_file, decryption_stats
            )


def log_files(files: List[str]) -> None:
    max_files_to_list = 5
    d_n = len(files) - max_files_to_list
    logger.info(
        "Extracted files: [%s] %s",
        ", ".join(files[:max_files_to_list]),
        ((f"and {d_n} more files - not listing them all.") if d_n > 0 else ""),
    )
