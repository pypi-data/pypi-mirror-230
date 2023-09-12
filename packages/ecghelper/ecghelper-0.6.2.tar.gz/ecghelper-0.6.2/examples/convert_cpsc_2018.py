"""
Example script converting the first 10 records of CPSC-2018 data
into various formats.
"""
import os
import numpy as np
from pathlib import Path

from ecghelper.waveform import WaveformRecord

def main():
    # inputs
    data_path = Path('tests/data/cpsc_2018').resolve()
    files = data_path.glob('*.hea')
    filenames = [x.stem for x in files][:10]

    for filename in filenames:
        # read in the WFDB format record
        record = WaveformRecord.from_wfdb(data_path / f"{filename}")

        fcns = [
            (".xml", record.to_xml, WaveformRecord.from_xml),
            # TODO: edf is failing!
            # (".edf", record.to_edf, WaveformRecord.from_edf),
            (".csv", record.to_csv, WaveformRecord.from_csv),
        ]
        for ext, to_fcn, load_fcn in fcns:
            # precision for these records is 5 digits
            # rounding is useful for output to EDF, CSV, etc.
            signal = np.around(record.data, 5)

            output_file = Path(data_path / f'{filename}{ext}')
            to_fcn(output_file)
            assert os.path.exists(output_file)

            # re-load, compare to original signal
            record_reloaded = load_fcn(output_file)
            signal_reloaded = record_reloaded.data
            assert signal_reloaded.shape == signal.shape

            # assert approximately equal
            assert (abs(signal_reloaded - signal) < 0.01).all()

            assert signal_reloaded.shape[0] > 0
            assert signal_reloaded.shape[1] == 12

            # reloaded signal should be very close
            np.allclose(signal_reloaded, signal, atol=0.0001)

if __name__ == '__main__':
    main()