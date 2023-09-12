import numpy as np
import pytest

from ecghelper.io import load_xml, load_wfdb, write_xml, write_wfdb, load_edf, write_edf

# load_wfdb(), write_wfdb() tests
@pytest.mark.parametrize("filename", ["A0001"])
def test_speed_load_wfdb(filename, data_path, benchmark):
    signal = benchmark(load_wfdb, data_path / filename)
    assert signal is not None

@pytest.mark.parametrize("filename", ["A0001"])
def test_speed_write_wfdb(filename, data_path, benchmark, tmp_path):
    signal = load_wfdb(data_path / filename)
    benchmark(write_wfdb, tmp_path / filename, signal)
    assert signal is not None

@pytest.mark.parametrize("filename", ["A0001.edf"])
def test_speed_load_edf(filename, data_path, benchmark):
    signal = benchmark(load_edf, data_path / filename)
    assert signal is not None

@pytest.mark.parametrize("filename", ["A0001.edf"])
def test_speed_write_edf(filename, data_path, benchmark, tmp_path):
    signal = load_edf(data_path / filename)
    signal = np.around(signal, 8)
    benchmark(write_edf, tmp_path / filename, signal)
    assert signal is not None

@pytest.mark.parametrize("filename", ["A0001.xml"])
def test_speed_load_xml(filename, data_path, benchmark):
    signal = benchmark(load_xml, data_path / filename)
    assert signal is not None

@pytest.mark.parametrize("filename", ["A0001.xml"])
def test_speed_write_xml(filename, data_path, benchmark, tmp_path):
    signal = load_xml(data_path / filename)
    benchmark(write_xml, tmp_path / filename, signal)
    assert signal is not None

"""
# load_csv(), write_csv() tests
def test_load_and_write_csv(tmp_path, benchmark):
    csv_string = "name,age\nJohn,32\nJane,28\n"
    csv_data = csv.DictReader(csv_string.splitlines())

    temp_file = tmp_path / 'temp.csv'
    headers = ["name", "age"]
    benchmark(csv.DictWriter(open(temp_file, 'w'), fieldnames=headers).writeheader)
    benchmark(csv.DictWriter(open(temp_file, 'a'), fieldnames=headers).writerows, csv_data)

    assert temp_file.exists()
    with open(temp_file, 'r') as f:
        assert f.read() == csv_string

    temp_file.unlink()
"""