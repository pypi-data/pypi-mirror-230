import os
from pathlib import Path
import pytest

@pytest.fixture
def data_path():
    """Return the path to the data directory."""
    return Path(os.path.dirname(os.path.realpath(__file__))) / 'data'

@pytest.fixture
def cpsc_2018_path(data_path: Path) -> Path:
    """Return the path to the data directory."""
    return data_path / 'cpsc_2018'

@pytest.fixture
def muse_xml_record_name(data_path):
    """Load a sample XML file."""
    return data_path / '82000.xml'

@pytest.fixture
def wfdb_record_name(data_path):
    """Load a sample XML file."""
    return data_path / 'A0001'