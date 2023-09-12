import os
import pytest
import numpy as np
from pathlib import Path
import csv

from ecghelper.waveform import WaveformRecord


def test_waveform_binary_read(data_path):
    """Load 82000 data converted into a CSV"""
    with open(data_path / 'binary.csv', 'r') as fp:
        csvreader = csv.DictReader(fp)
        lead_data = []
        columns = []
        for row in csvreader:
            lead_data.append(row['WaveFormData'])
            columns.append(row['LeadID'])

            # assume various parameters don't change from lead to lead
            sampling_frequency = int(row['SamplingFrequency'])
            sample_size = int(row['LeadSampleSize'])
            amplitude_units_per_bit = float(row['LeadAmplitudeUnitsPerBit'])
            baseline = int(row['FirstSampleBaseline'])
            units = str(row['LeadAmplitudeUnits'])

    # expect 8 leads of data in the source binary data
    assert len(lead_data) == 8

    binary = WaveformRecord.from_binary(
        lead_data, columns, sampling_frequency,
        sample_size, amplitude_units_per_bit, baseline, units
    )
    assert binary.data.shape[0] > 0

    # expect 12 leads of data after being loaded into a WaveformRecord
    assert binary.data.shape[1] == 12

@pytest.mark.parametrize(
        "ext,load_fcn",
        [
            (".xml", WaveformRecord.from_xml),
            (".hea", WaveformRecord.from_wfdb),
            (".edf", WaveformRecord.from_edf)
        ])
def test_waveform_read(cpsc_2018_path, ext, load_fcn):
    """Tests that we can read signals without changing the data."""
    files = cpsc_2018_path.glob(f'*{ext}')
    filenames = [x.stem for x in files]
    for filename in filenames:
        if ext == '.hea':
            record = load_fcn(cpsc_2018_path / f"{filename}")
        else:
            record = load_fcn(cpsc_2018_path / f"{filename}{ext}")

        assert record.data.shape[0] > 0
        assert record.data.shape[1] == 12

        # units should be between -2.5 and 5 millivolts
        assert record.data.min() > -2.5
        assert record.data.max() < 5

@pytest.mark.parametrize(
        "format,ext",
        [
            ("xml"),
            ("wfdb"),
            # ("edf"),
            ("csv"),
        ])
def test_write(cpsc_2018_path, tmp_path, format):
    # load in a waveform record from the CPSC-2018 dataset
    files = cpsc_2018_path.glob('*.hea')
    filename = [x.stem for x in files][0]

    # read in the record
    record = WaveformRecord.from_wfdb(cpsc_2018_path / f"{filename}")

    to_fcn = record.write_methods[format]
    load_fcn = record.from_methods[format]

    # EDF precision is 8 chars
    signal = np.around(record.data, 5)
    output_file = tmp_path /  f'{filename}'
    if format != 'wfdb':
        output_file.with_suffix(f'.{format}')
    to_fcn(output_file)

    if format == 'wfdb':
        output_file = output_file.with_suffix('.hea')
    assert output_file.exists()

    # re-load, compare to original signal
    record_reloaded = load_fcn(output_file)
    signal_reloaded = record_reloaded.data
    assert signal_reloaded.shape == signal.shape

    # assert approximately equal
    assert (abs(signal_reloaded - signal) < 0.01).all()

    assert signal_reloaded.shape[0] > 0
    assert signal_reloaded.shape[1] == 12

    # units should be between -2 and 5 millivolts
    assert signal_reloaded.min() > -2
    assert signal_reloaded.max() < 5
