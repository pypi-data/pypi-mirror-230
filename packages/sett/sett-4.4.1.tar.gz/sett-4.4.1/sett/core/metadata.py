from typing import Dict, Any

from libbiomedit import metadata as _metadata
from libbiomedit.metadata import METADATA_FILE as _METADATA_FILE
from libbiomedit.metadata import METADATA_FILE_SIG as _METADATA_FILE_SIG

from .error import UserError

# Reexports
alnum_str = _metadata.alnum_str
METADATA_FILE = _METADATA_FILE
METADATA_FILE_SIG = _METADATA_FILE_SIG
Purpose = _metadata.Purpose
HexStr1024 = _metadata.HexStr1024
HexStr256 = _metadata.HexStr256
MetaData = _metadata.MetaData


def load_metadata(d: Dict[str, Any]) -> MetaData:
    try:
        return MetaData.from_dict(d)
    except ValueError as e:
        raise UserError(format(e)) from e
