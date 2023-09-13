import os
import re
import json
import time
from typing import List, Tuple, Dict, Optional, Callable

from sett_rs.cert import CertInfo, CertStore, CertType

from ..core import gpg
from ..core.crypt import get_recipient_email, retrieve_refresh_and_validate_keys
from ..core.archive import (
    check_package,
    extract_multiple,
    DATA_FILE_ENCRYPTED,
)
from ..core.metadata import load_metadata, METADATA_FILE
from ..core.error import UserError
from ..utils.config import Config
from ..utils.log import create_logger, log_runtime_info, log_timing
from ..utils.progress import ProgressInterface
from ..protocols import Protocol
from .encrypt import DATE_FMT_FILENAME


logger = create_logger(__name__)


@log_timing(logger)
@log_runtime_info(logger)
def transfer(
    files: List[str],
    *,
    protocol: Protocol,
    config: Config,
    two_factor_callback: Callable[[], str],
    dry_run: bool = False,
    pkg_name_suffix: Optional[str] = None,
    progress: Optional[ProgressInterface] = None,
) -> None:
    """Main function of the transfer workflow. Transfers the specified files to
    the selected recipient specified in protocol.

    :param files: list of files to be transferred.
    :param protocol: parameters that specify the protocol (e.g. sftp) and
        destination (e.g. server URL) to be used for the transfer.
    :param config: sett config file object.
    :param two_factor_callback: function to 2FA if the destination server requires
        it.
    :param dry_run: if True, tests on the data to be transferred are carried-out,
        but the actual transfer of files is skipped.
    :param pkg_name_suffix: by default, the <package_name_suffix> value used
        to check the file name (if the check is enabled) is taken from the
        user's config file. This optional argument allows to override this.
    :param progress: progress object to be updated about the progress of the
        transfer task.
    :raises UserError:
    """

    with logger.log_task(
        f"Input data verification{' (dry_run)' if dry_run else ''}..."
    ):
        logger.info("Files to transfer: %s", ", ".join(files))
        files_by_recipient: Dict[Tuple[str, ...], List[str]] = {}

        # Loop through all files to transfer and verify their content.
        for archive_path in files:
            logger.info("Verifying: %s", archive_path)

            # Verify input data package extension and content.
            check_package(archive_path)

            # Verify input data package metadata.
            with extract_multiple(
                archive_path, (METADATA_FILE, DATA_FILE_ENCRYPTED)
            ) as (
                metadata_io,
                encrypted_file,
            ):
                raw_metadata = json.load(metadata_io)
                metadata = load_metadata(raw_metadata)
                if not config.legacy_mode:
                    try:
                        store = CertStore()
                        certs = tuple(
                            CertInfo.from_bytes(store.export_cert(r, CertType.Public))
                            for r in metadata.recipients
                        )
                        files_by_recipient.setdefault(
                            tuple(get_recipient_email(k) for k in certs), []
                        ).append(archive_path)
                    except RuntimeError as e:
                        raise UserError(
                            f"Unable to retrieve recipient's certificate: {e}"
                        ) from e
                else:
                    keys = retrieve_refresh_and_validate_keys(
                        key_identifiers=gpg.extract_key_id(encrypted_file),
                        config=config,
                    )
                    files_by_recipient.setdefault(
                        tuple(get_recipient_email(k) for k in keys), []
                    ).append(archive_path)

            if config.verify_dtr:
                if metadata.transfer_id is None:
                    raise UserError(
                        "DTR (Data Transfer Request) ID verification was "
                        "requested but DTR ID is missing in file metadata."
                    )

                # Query the portal API for the specified DTR ID and return
                # project code. Raises an RuntimeError if the DTR is
                # not-approved or some of the metadata does not match with the
                # project the DTR ID belongs to.
                try:
                    project_code = config.portal_api.verify_dpkg_metadata(
                        metadata=metadata, file_name=archive_path
                    )
                except RuntimeError as e:
                    raise UserError(format(e)) from e

                logger.info(
                    "DTR ID '%s' is valid for project '%s'",
                    metadata.transfer_id,
                    project_code,
                )

            if config.verify_package_name:
                check_archive_name_follows_convention(
                    archive_path=archive_path,
                    project_code=project_code if config.verify_dtr else None,
                    package_name_suffix=pkg_name_suffix,
                )

    if dry_run:
        logger.info("Dry run completed successfully")
        return

    # Transfer files to their destination.
    with logger.log_task("Transferring files..."):
        # For efficiency, files for a same recipient/destination are
        # transferred together.
        for emails, r_files in files_by_recipient.items():
            for label, value in (
                # LiquidFiles: email addresses of recipient must be specified.
                ("recipients", emails),
                # SFTP: encoding of public SSH key and buffer size must be specified.
                ("pkey_password_encoding", config.ssh_password_encoding),
                ("buffer_size", config.sftp_buffer_size),
            ):
                if hasattr(protocol, label):
                    setattr(protocol, label, value)

            logger.info("Transferring files encrypted for: %s", ", ".join(emails))
            protocol.upload(
                files=r_files,
                two_factor_callback=two_factor_callback,
                progress=progress,
            )

    logger.info("Completed data transfer")


def check_archive_name_follows_convention(
    archive_path: str,
    project_code: Optional[str],
    package_name_suffix: Optional[str],
) -> None:
    """Verify that the given archive_path file name follows the naming
    convention for data packages:

        <project_code>_<date_format>_<package_name_suffix>.zip

    Raises an error if the file name does not match the convention.

    Note that if a <package_name_suffix> is given, then the check succeeds if
    either the suffix is fully matched, or if it is fully absent. Having no
    suffix at all is accepted because the aim of this check is to verify that
    no sensitive info gets leaked in the package name.
    """

    def join_strings(*args: Optional[str]) -> str:
        return "_".join(filter(None, args))

    error_msg = (
        f"File '{archive_path}' does not follow the standard data package "
        "naming convention: '"
        f"{join_strings(project_code, DATE_FMT_FILENAME, package_name_suffix)}"
        f".zip/.tar'. Please make sure that the file name does not contain "
        "any confidential information. "
        "To resolve this error, please modify the name of the file to match "
        "the naming convention. "
        "If the package name is prefixed with its project code, make sure "
        "that DTR ID verification is not disabled. "
        "To permanently disable this check, uncheck the 'Verify package name' "
        "checkbox in the Settings tab (GUI), or set 'verify_package_name' to "
        "'false' in the application's configuration file."
    )

    # Capture the date+time part of the archive file using a regexp.
    m = re.fullmatch(
        join_strings(project_code, r"(?P<ts>\S+?)")
        + (r"(?:_" + package_name_suffix + r")?" if package_name_suffix else "")
        + r"\.(zip|tar)",
        os.path.basename(archive_path),
    )

    # Testing for the length of the date+time string is needed because
    # strftime() does support incomplete strings: e.g. "20210908T140302"
    # and "202198T1432" are both converted to the same date and time.
    if m is None or len(m.group("ts")) != len(
        time.strftime(DATE_FMT_FILENAME, time.localtime())
    ):
        raise UserError(error_msg)

    # Try to do a string-to-time conversion: failure indicates that the
    # captured group does not follow the date format specifications, or
    # that some additional, unexpected, text is in the archive name.
    try:
        time.strptime(m.group("ts"), DATE_FMT_FILENAME)
    except ValueError:
        raise UserError(error_msg) from None
