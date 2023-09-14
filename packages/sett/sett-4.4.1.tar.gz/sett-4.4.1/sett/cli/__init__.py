#!/usr/bin/env python3
# The {} placeholders in the docstring are to be replaced with URL_HELP
# and URL_GITLAB_ISSUES whenever the docstring is used.
"""Secure Encryption and Transfer Tool
For detailed documentation see: {}
To report an issue, please use: {}
"""

import os
import json
import shlex
import subprocess  # nosec B404:blacklist import_subprocess
from functools import wraps
from getpass import getpass
from typing import List, Dict, Any, Optional, Callable, Type, Union, TypeVar, cast

from sett_rs.cert import CertStore, CertType

from .progress import CliProgress
from .cli_builder import (
    rename,
    return_to_stdout,
    partial,
    lazy_partial,
    CliWithSubcommands,
    Subcommand,
    SubcommandGroup,
    decorate,
)
from ..core.secret import Secret
from .. import VERSION_WITH_DEPS
from ..utils.config import Config, load_config, config_to_dict
from ..utils.log import (
    log_to_stream,
    log_to_rotating_file,
    create_logger,
)
from ..utils.error_handling import (
    exit_on_exception,
    log_exceptions,
    error_report_hint_at_exit,
)
from ..utils.progress import ProgressInterface
from ..workflows.config import create as create_config
from ..workflows.transfer import transfer as workflows_transfer
from ..workflows.decrypt import decrypt as workflows_decrypt
from ..workflows.encrypt import encrypt as workflows_encrypt
from ..workflows.upload_keys import verify_keylengths_and_upload_keys
from ..protocols import (
    sftp,
    liquid_files,
    parse_protocol,
    __all__ as available_protocols,
)
from ..core.versioncheck import check_version
from ..core.error import UserError
from ..core.filesystem import OutOfSpaceError
from ..core.metadata import Purpose
from .. import URL_READTHEDOCS, URL_GITLAB_ISSUES

logger = create_logger(__name__)


def parse_dict(s: str) -> Dict[str, Any]:
    """Convert/deserialize a JSON formatted string to a dict object."""

    return dict(json.loads(s))


def parse_protocol_args(s: str) -> Dict[str, Any]:
    """Convert/deserialize a string containing SFTP protocol values to a
    dictionary object.

    Example of input string:
    {"host": "sftp.example.com", "username": "sftp",
    "destination_dir": "upload", "pkey": "~/.ssh/id_rsa", "pkey_password": ""}
    """
    args = parse_dict(s)

    # Convert the provided password (if any) to a `Secret` object (i.e. an
    # object that will not print its encapsulated content). If the value
    # {"pkey_password": null} was passed, the "null" is converted to an
    # empty string `""` rather than to None.
    args["pkey_password"] = Secret(
        str(args["pkey_password"] if args["pkey_password"] else "")
        if "pkey_password" in args
        else getpass("Please enter your SSH private key password:")
    )
    return args


def two_factor_cli_prompt() -> str:
    return input("Please enter 2FA verification code: ")


def get_passphrase_from_cmd(passphrase_cmd: str) -> Secret[str]:
    try:
        # B603:subprocess_without_shell_equals_true
        # Suppress the warning, user can easily execute the same command
        # directly in the shell.
        proc = subprocess.run(  # nosec
            shlex.split(passphrase_cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return Secret(proc.stdout.decode().strip())
    except subprocess.CalledProcessError as e:
        raise UserError(
            f"Failed to read passphrase from '{passphrase_cmd}'. "
            f"{e.stderr.decode().strip()}"
        ) from e


def get_passphrase_from_cmd_or_prompt(
    msg: str, passphrase_cmd: Optional[str]
) -> Secret[str]:
    if passphrase_cmd:
        return get_passphrase_from_cmd(passphrase_cmd)
    return Secret(getpass(msg))


def get_certificate_fingerprint(
    search_term: str, store: CertStore, cert_type: CertType
) -> str:
    """Check that the specified search term matches exactly one certificate
    in the local CertStore, and return the fingerprint of the matching
    certificate.

    The search term can be one of the following: email, fingerprint or
    keyID (the last 16 chars of the fingerprint)
    """

    certs = [
        cert
        for cert in store.list_certs(cert_type)
        if search_term in (cert.email, cert.fingerprint, cert.key_id)
    ]
    try:
        (cert,) = certs
        return cert.fingerprint
    except ValueError:
        raise UserError(
            f"{'No' if len(certs) == 0 else 'More than one'} certificate "
            f"matching '{search_term}' was found in the local CertStore."
        ) from None


def encrypt(
    files: List[str],
    config: Config,
    recipient: List[str],
    sender: Optional[str] = None,
    compression_level: Optional[int] = None,
    dry_run: bool = False,
    passphrase_cmd: Optional[str] = None,
    dtr_id: Optional[int] = None,
    output: Optional[str] = None,
    output_suffix: Optional[str] = None,
    force: bool = False,
    purpose: Optional[Purpose] = None,
    progress: Optional[ProgressInterface] = None,
) -> Optional[str]:
    """Wrapper for the main function of the encrypt workflow."""

    def get_value_from_config(arg_name: str, arg_name_in_config: str) -> Any:
        value_from_config = getattr(config, arg_name_in_config)
        if value_from_config is None:
            raise UserError(f"{arg_name} not specified with no default in config.")
        return value_from_config

    # If no sender or compression level is specified, attempt to retrieve their
    # default values from config.
    if sender is None:
        sender = get_value_from_config("sender", "default_sender")
    if compression_level is None:
        compression_level = get_value_from_config(
            "compression_level", "compression_level"
        )

    # Make sure that sender and recipient certificates are present in the local
    # CertStore. If needed, this also converts the certificate identifier from
    # an email to a fingerprint.
    # Note: only applies when using Sequoia as crypto backend.
    if not config.legacy_mode:
        store = CertStore()
        sender = get_certificate_fingerprint(sender, store, CertType.Secret)
        recipients = [
            get_certificate_fingerprint(r, store, CertType.Public) for r in recipient
        ]
    else:
        # Note: we use "recipient" instead of "recipients" in the signature of
        # this function because it's used to build the CLI options.
        recipients = recipient

    # Run the encrypt workflow.
    try:
        return workflows_encrypt(
            files=files,
            dtr_id=dtr_id,
            config=config,
            sender=sender,
            recipients=recipients,
            output=output,
            output_suffix=output_suffix,
            force=force,
            purpose=purpose,
            dry_run=dry_run,
            compression_level=compression_level,
            passphrase=None
            if dry_run
            else get_passphrase_from_cmd_or_prompt(
                "Please enter your PGP private key password:", passphrase_cmd
            ),
            progress=progress,
        )
    except OutOfSpaceError as e:
        raise OutOfSpaceError(f"{e} Use --force or -f to ignore this error.") from e


@wraps(workflows_decrypt)
def decrypt(
    *files: str, dry_run: bool, passphrase_cmd: Optional[str], **kwargs: Any
) -> None:
    if dry_run:
        kwargs["passphrase"] = None
    else:
        kwargs["passphrase"] = get_passphrase_from_cmd_or_prompt(
            "Please enter your PGP private key password:", passphrase_cmd
        )
    workflows_decrypt(*files, dry_run=dry_run, **kwargs)


def transfer(
    files: List[str],
    *,
    connection: Optional[str] = None,
    two_factor_callback: Callable[[], str],
    passphrase_cmd: Optional[str] = None,
    config: Config,
    protocol: Optional[Type[Union[sftp.Protocol, liquid_files.Protocol]]] = None,
    protocol_args: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
    progress: Optional[ProgressInterface] = None,
) -> None:
    if connection is not None:
        if protocol is not None:
            raise UserError(
                "Arguments 'protocol' and 'connection' cannot be given together"
            )
        protocol_instance = config.connections[connection]
    else:
        if protocol is None or protocol_args is None:
            raise UserError(
                "Missing argument: either 'protocol' and 'protocol_args', "
                "or 'connection' must be given."
            )
        try:
            protocol_instance = protocol(**protocol_args)
        except TypeError as e:
            raise UserError(
                format(e).replace("__init__", protocol.__module__)
            ) from None
    for pw_arg in protocol_instance.required_password_args():
        if getattr(protocol_instance, pw_arg, None) is None:
            setattr(
                protocol_instance,
                pw_arg,
                get_passphrase_from_cmd_or_prompt(
                    f"Please enter the secret for the argument `{pw_arg}`:",
                    passphrase_cmd,
                ),
            )
    workflows_transfer(
        files,
        protocol=protocol_instance,
        config=config,
        dry_run=dry_run,
        pkg_name_suffix=config.package_name_suffix,
        progress=progress,
        two_factor_callback=two_factor_callback,
    )


def load_config_and_check_app_is_up_to_date() -> Config:
    """Load the config file and perform a check to see whether the user's
    local instance of the application is up-to-date.
    """
    cfg = load_config()
    if cfg.check_version:
        check_version(cfg.repo_url)
    return cfg


class Cli(CliWithSubcommands):
    description = __doc__.format(URL_READTHEDOCS, URL_GITLAB_ISSUES)
    version = VERSION_WITH_DEPS
    config = load_config_and_check_app_is_up_to_date()
    passphrase_override = {
        "help": "Instead of asking for passphrase, get it from an external command "
        "(passphrase must be returned to the standard output).",
        "name": "passphrase-cmd",
        "dest": "passphrase_cmd",
        "type": str,
    }
    dry_run_override = {
        "help": "Perform checks on the input data, without running the actual command."
    }
    subcommands = (
        Subcommand(
            decorate(
                encrypt,
                partial(config=config),
                lazy_partial(progress=CliProgress),
            ),
            overrides={
                "files": {"help": "Input file(s) or directories."},
                "sender": {
                    "help": "Fingerprint, key ID or email associated "
                    "with OpenPGP key of data sender.",
                    "alias": "-s",
                },
                "recipient": {
                    "help": "Fingerprint, key ID or email associated with "
                    "OpenPGP key of data recipient. Multiple recipients can "
                    "be specified by passing this option multiple times.",
                    "alias": "-r",
                },
                "dtr_id": {
                    "help": "Data Transfer Request (DTR) ID (optional if "
                    "`verify_dtr` is disabled in settings).",
                    "alias": "-t",
                },
                "purpose": {
                    "help": "Purpose of the DTR (PRODUCTION, TEST). "
                    "Mandatory only if `transfer_id` is specified."
                },
                "force": {
                    "help": "Ignore errors about missing disk space",
                    "alias": "-f",
                },
                "output": {
                    "help": "Output path (directory path and/or file name) of "
                    "the encrypted package. If no directory path is specified, "
                    "the output package is saved in the current working "
                    "directory. If this argument is missing or the path is a "
                    "directory, the file name is generated based on the "
                    "current date and an optional suffix.",
                    "default": None,
                    "alias": "-o",
                },
                "output_suffix": {"help": "Output file name suffix (optional)"},
                "dry_run": dry_run_override,
                "compression_level": {
                    "help": "Compression level for inner tarball in the range "
                    "0 (no compression) to 9 (highest compression). "
                    "Higher compression levels require more computing "
                    "time."
                },
                "passphrase_cmd": passphrase_override,
            },
        ),
        Subcommand(
            decorate(
                transfer,
                partial(config=config, two_factor_callback=two_factor_cli_prompt),
                lazy_partial(progress=CliProgress),
            ),
            overrides={
                "files": {"help": "Path(s) to encrypted package(s)"},
                "protocol": {
                    "help": f"The protocol for the file transfer."
                    f"Currently available: {', '.join(available_protocols)}",
                    "type": parse_protocol,
                    "alias": "-p",
                },
                "protocol_args": {
                    "help": "Protocol specific arguments. "
                    "Must be passed as a json string",
                    "type": parse_protocol_args,
                },
                "connection": {
                    "help": "Instead of the option 'protocol', load a connection "
                    "named by the argument of this option to use the "
                    "protocol and protocol args from the config. The "
                    "protocol args can be overwritten by the "
                    "protocol_args option"
                },
                "passphrase_cmd": {"help": passphrase_override["help"]},
                "dry_run": dry_run_override,
            },
        ),
        Subcommand(
            decorate(
                decrypt, partial(config=config), lazy_partial(progress=CliProgress)
            ),
            overrides={
                "files": {"help": "Path(s) to encrypted package(s)"},
                "output_dir": {
                    "help": "Path to the directory where package content is "
                    "saved after decryption. If no path is specified, current "
                    "working directory is taken.",
                    "default": os.getcwd(),
                    "alias": "-o",
                },
                "decrypt_only": {"help": "Skip extraction."},
                "dry_run": dry_run_override,
                "passphrase": passphrase_override,
            },
        ),
        SubcommandGroup(
            "config",
            decorate(
                config_to_dict, rename("show"), return_to_stdout, partial(config=config)
            ),
            create_config,
            help="Commands related to config file",
        ),
        Subcommand(
            decorate(verify_keylengths_and_upload_keys, partial(config=config)),
            overrides={"fingerprints": {"help": "Fingerprints to upload"}},
        ),
    )


# F is used as generic type for functions (Callable).
F = TypeVar("F", bound=Callable[..., Any])


def when(condition: bool, decorator: F) -> F:
    if condition:
        return decorator
    return cast(F, lambda x: x)


log_to_rotating_file(
    log_dir=Cli.config.log_dir, file_max_number=Cli.config.log_max_file_number
)
log_to_stream()


@exit_on_exception
@when(Cli.config.error_reports, error_report_hint_at_exit(Cli.config))
@log_exceptions(logger)
def run() -> int:
    if Cli():
        return 0
    return 1


if __name__ == "__main__":
    run()
