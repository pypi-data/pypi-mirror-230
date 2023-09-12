"""Utilities to support converting from one format to another."""
from pathlib import Path

from ecghelper.waveform import WaveformRecord

def convert(source_record, source_format, target_record, target_format='wfdb'):
    # load the source data
    record = WaveformRecord.read_xml(source_record)

    # get fcn to write out to target format
    write_fcn = record.write_methods[target_format]

    # if target_record is a string, treat it as a file path
    if isinstance(target_record, str):
        write_fcn(Path(target_record))

    # if target_record is file-like, write out to file
    if isinstance(target_record, Path):
        write_fcn(target_record)
