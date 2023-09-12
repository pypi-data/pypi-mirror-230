import logging
from pathlib import Path
from typing import Union

def remove_wfdb_suffix(record_filename: Union[str, Path]) -> Path:
    """Remove the WFDB suffix from a record filename.
    
    As of WFDB 4.1.2, rdrecord/wrsamp expects there to be no extension,
    so we remove it if it exists. For example, '100' is valid, but '100.dat',
    '100.hea', '100.mat' are not. We still allow for the case where a user
    is using a custom suffix, e.g. '100.custom'. In this case, wfdb would
    write out '100.custom.dat', '100.custom.hea', '100.custom.mat', etc.
    """
    record_filename = Path(record_filename)
    if record_filename.suffix in ('.dat', '.hea', '.mat', ''):
        record_filename = record_filename.with_suffix('')
    return record_filename

def create_logger(name: str, level=logging.INFO):
    """Create a logger local to the file."""
    _LOGGER = logging.getLogger(name)
    _HANDLER = logging.StreamHandler()
    _FORMATTER = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _HANDLER.setFormatter(_FORMATTER)
    _LOGGER.addHandler(_HANDLER)
    _LOGGER.setLevel(level)
    return _LOGGER
