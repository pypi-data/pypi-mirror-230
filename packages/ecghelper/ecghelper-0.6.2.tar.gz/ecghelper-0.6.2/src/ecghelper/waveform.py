# Allow typing of returned class for class methods
# https://www.python.org/dev/peps/pep-0563/
from __future__ import annotations

import base64
import csv
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Union, List, Optional
from inspect import getmembers
from zlib import crc32

import lxml.etree as ET
from lxml.etree import _ElementTree, _Element
import numpy as np
import wfdb
import pyedflib

from .utils import remove_wfdb_suffix

@dataclass
class WaveformRecord:
    data: np.ndarray
    columns: List[str]
    sampling_frequency: float

    def __post_init__(self):
        # inspect methods with from_ prefix and create dict
        # of supported read functions
        # this provides a map from the format (e.g. 'wfdb') to the
        # read function (from_wfdb), which is useful for deserialization
        methods = getmembers(self)
        self.from_methods = {}
        for method in methods:
            if method[0].startswith('from_') and callable(method[1]):
                self.from_methods[method[0][5:]] = method[1]
        
        # similar approach for writing data out
        self.write_methods = {}
        for method in methods:
            if method[0].startswith('to_') and callable(method[1]):
                self.write_methods[method[0][3:]] = method[1]
        
        # convert 8-lead ECGs to 12-lead
        _LEADS = (
            'I', 'II', 'III', 'aVR', 'aVL', 'aVF',
            'V1', 'V2', 'V3', 'V4', 'V5', 'V6'
        )
        if self.data.shape[1] == 8:
            self._convert_8_to_12_lead(_LEADS)
        elif self.data.shape[1] != 12:
            raise ValueError('Input data for WaveformRecord must have 8 or 12 leads')

        # ensure that the columns are always in the standard 12-lead order
        idx = [self.columns.index(lead) for lead in _LEADS]
        self.data = self.data[:, idx]
        self.columns = list(_LEADS)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.data.shape})'

    def _convert_8_to_12_lead(self, _LEADS):
        """Converts 8-lead ECGs to 12-lead ECGs."""
        # determine the leads that are missing
        missing_leads = sorted(list(set(_LEADS) - set(self.columns)))

        # create a new array with the missing leads
        missing_data = np.zeros((self.data.shape[0], len(missing_leads)))
        # create an index from lead name to column index
        lead_idx = {lead: idx for idx, lead in enumerate(self.columns)}

        for i, lead in enumerate(missing_leads):
            if lead == 'III':
                # III = II - I
                missing_data[:, i] = self.data[:, lead_idx["II"]] - self.data[:, lead_idx["I"]]
            elif lead == 'aVR':
                # aVR = -(I + II)/2
                missing_data[:, i] = -(self.data[:, lead_idx["I"]] + self.data[:, lead_idx["II"]])/2
            elif lead == 'aVL':
                # aVL = I - II/2
                missing_data[:, i] = self.data[:, lead_idx["I"]] - self.data[:, lead_idx["II"]]/2
            elif lead == 'aVF':
                # aVF = II - I/2
                missing_data[:, i] = self.data[:, lead_idx["II"]] - self.data[:, lead_idx["I"]]/2
            else:
                raise ValueError(f'Unable to impute lead data for {lead}')
        # concatenate the missing data to the original data
        self.data = np.concatenate((self.data, missing_data), axis=1)

        # add the missing leads to the list of columns
        self.columns += missing_leads

    @classmethod
    def decode_binary(cls, data: str, sample_size: int, amplitude_units_per_bit: float, baseline: int, units: str):
        lead_data = base64.b64decode(data)

        # iterate through to convert each byte into an integer
        lead_data = [
            int.from_bytes(
                lead_data[i:i+sample_size],
                byteorder='little',
                signed=True
            )
            for i in range(0, len(lead_data), sample_size)
        ]

        # convert to numpy array
        lead_data = np.array(lead_data, dtype=np.float32)
    
        # convert to physical units
        lead_data = (lead_data - baseline) * amplitude_units_per_bit

        # check for various units of measure, converting to millivolts as needed
        if units == 'MICROVOLTS':
            lead_data /= 1000
        elif units == 'VOLTS':
            lead_data *= 1000
        elif units == 'MILLIVOLTS':
            pass
        else:
            raise ValueError(f'unknown units of measure: {units}')

        return lead_data

    @classmethod
    def from_binary(cls, data: List[str], columns: List[str], sampling_frequency: int, sample_size: int, amplitude_units_per_bit: float, baseline: int, units: str) -> WaveformRecord:
        """Decode a b64 string into a waveform signal."""
        signal = []

        for lead_data in data:
            signal.append(
                cls.decode_binary(lead_data, sample_size, amplitude_units_per_bit, baseline, units)
            )
        # stack lead data column-wise
        signal = np.stack(signal, axis=1)

        return cls(
            data=signal,
            columns=columns,
            sampling_frequency=sampling_frequency,
        )

    @classmethod
    def from_edf(cls, record_filename: Union[str, Path]) -> WaveformRecord:
        """Load an EDF/EDF+ record."""
        record_filename = str(Path(record_filename).resolve())
        f = pyedflib.EdfReader(record_filename)
        n = f.signals_in_file
        signal = np.zeros((f.getNSamples()[0], n))
        for i in np.arange(n):
            signal[:, i] = f.readSignal(i)

        # Get sampling frequency
        sampling_frequency = f.getSampleFrequency(0)

        # Get signal labels
        columns = f.getSignalLabels()

        # Close file
        f._close()

        return cls(
            data=signal,
            columns=columns,
            sampling_frequency=sampling_frequency,
        )

    @classmethod
    def from_edfz(cls, record_filename: Union[str, Path]) -> WaveformRecord:
        """Load an EDFZ record."""
        # with gzip.open(record_name, 'rb') as f:
        #     signal = f.read()
        # pyedflib expects a filename as input, not a file-like object :(
        raise NotImplementedError()

    @classmethod
    def from_wfdb(cls, record_filename: Union[str, Path]) -> WaveformRecord:
        """Load a WFDB record."""
        record_filename = remove_wfdb_suffix(record_filename)

        record = wfdb.rdrecord(record_filename)
        if record.p_signal is None:
            raise ValueError(f'No signal found in {record_filename}')

        return cls(
            data=record.p_signal,
            columns=record.sig_name,
            sampling_frequency=record.fs,
        )

    @classmethod
    def from_wfdbz(cls, record_filename: Union[str, Path]):
        """Load a WFDB record."""
        return cls.from_wfdb(record_filename)

    @classmethod
    def _parse_xml_data(cls, root: _Element) -> WaveformRecord:
        """Load waveform data from an XML record.
        
        This function assumes the following XML structure is present:
            <Waveform>
                <WaveformType>Rhythm</WaveformType>
                <LeadData>
                    <LeadByteCountTotal>1200</LeadByteCountTotal>
                    <LeadTimeOffset>0</LeadTimeOffset>
                    <LeadSampleCountTotal>600</LeadSampleCountTotal>
                    <LeadAmplitudeUnitsPerBit>4.88</LeadAmplitudeUnitsPerBit>
                    <LeadAmplitudeUnits>MICROVOLTS</LeadAmplitudeUnits>
                    <LeadHighLimit>32767</LeadHighLimit>
                    <LeadLowLimit>-32768</LeadLowLimit>
                    <LeadID>I</LeadID>
                    <LeadOffsetFirstSample>0</LeadOffsetFirstSample>
                    <FirstSampleBaseline>0</FirstSampleBaseline>
                    <LeadSampleSize>2</LeadSampleSize>
                    <LeadOff>FALSE</LeadOff>
                    <BaselineSway>FALSE</BaselineSway>
                    <LeadDataCRC32>1391929279</LeadDataCRC32>
                    <WaveFormData> ... </WaveFormData>
                </LeadData>
                ... (repeats for each lead)
            </Waveform>
        """
        # the 12-lead ECG is assumed stored in the Rhythm waveform type
        waveform = None
        for waveform in root.iter('Waveform'):
            waveform_type = waveform.find('WaveformType').text
            if waveform_type == 'Rhythm':
                break
            if waveform_type is None:
                raise ValueError('WaveformType = "Rhythm" not found')

        # the Waveform tag has multiple LeadData tags, each of which
        # contains a base64-encoded string of the waveform data
        signal = []
        columns = []
        if waveform is None:
            raise ValueError('Waveform tag not found')

        for lead in waveform.iter('LeadData'):
            # lead_name = lead.find('LeadID').text
            sample_size = int(lead.find('LeadSampleSize').text)
            if sample_size > 8:
                raise ValueError(f'byte size expected to be no higher than 8')

            # extract the string with the waveform data and decode into bytes
            lead_data = lead.find('WaveFormData').text

            # verify data matches the CRC32
            lead_crc32 = int(lead.find('LeadDataCRC32').text)
            if lead_crc32 != crc32(base64.b64decode(lead_data)):
                raise ValueError('CRC32 mismatch')

            # get info necessary for decoding
            sample_length = int(lead.find('LeadSampleCountTotal').text)
            amplitude_units_per_bit = float(lead.find('LeadAmplitudeUnitsPerBit').text)
            baseline = int(lead.find('FirstSampleBaseline').text)
            units = lead.find('LeadAmplitudeUnits').text
            lead_data = cls.decode_binary(lead_data, sample_size, amplitude_units_per_bit, baseline, units)

            signal.append(lead_data)

            lead_name = lead.find('LeadID').text
            columns.append(lead_name)
        
        # stack lead data column-wise
        signal = np.stack(signal, axis=1)

        # sample frequency
        fs = float(waveform.find('SampleBase').text)
        fs_exp = int(waveform.find('SampleExponent').text)
        fs = fs * (10**fs_exp)

        return cls(
            data=signal,
            columns=columns,
            sampling_frequency=fs,
        )

    @classmethod
    def from_xml_string(cls, xml_string: str) -> WaveformRecord:
        # parse the element tree
        root = ET.fromstring(xml_string, parser=None)
        return cls._parse_xml_data(root)

    @classmethod
    def from_xml(cls, record_filename: Union[str, Path]) -> WaveformRecord:
        # parse the element tree
        etree = ET.parse(record_filename, parser=None)
        root = etree.getroot()
        return cls._parse_xml_data(root)

    @classmethod
    def from_csv(cls, record_filename: Union[str, Path]) -> WaveformRecord:
        """Load a CSV record.
        
        CSV must have a header row. The first column must be a time
        column, in seconds, in order to calculate the sampling frequency.
        The remaining columns should be leads of the ECG.
        """
        with open(record_filename, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            data = np.array(list(reader), dtype=np.float32)

        # verify that the first column have evenly spaced samples
        # i.e. that it is a time column
        if data.shape[0] < 3:
            raise ValueError('CSV must have at least three samples.')
        s0, s1, s2 = data[:3, 0]
        if s2 - s1 != s1 - s0:
            raise ValueError('First column of CSV must be a time column.')

        # calculate inverse of time between first two samples
        # this is the sampling frequency
        fs = 1 / (s1 - s0)

        # omit time column from the data
        data = data[:, 1:]
        header = header[1:]

        return cls(
            data=data,
            columns=header,
            sampling_frequency=fs,
        )

    # === write out to file
    def to_csv(self, record_name: Union[str, Path]):
        """Write a CSV record.
        
        The CSV will have a header row. The first column will be the time of the sample,
        in seconds. The remaining columns will be the leads of the ECG.
        """
        with open(record_name, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['time (s)'] + self.columns)
            # TODO: probably a way to natively iterate over the numpy array,
            # rather than indexing it over and over with i
            for i in range(self.data.shape[0]):
                writer.writerow([i / self.sampling_frequency] + list(self.data[i, :]))

    def to_edf(self, record_filename: Union[str, Path]):
        """Write an EDF/EDF+ record."""
        n_samples, n_channels = self.data.shape
        record_filename = Path(record_filename)

        # Create an EdfWriter object
        writer = pyedflib.EdfWriter(
            str(record_filename.resolve()),
            n_channels,
            pyedflib.FILETYPE_EDFPLUS
        )

        # Set the channel headers
        for i, channel_name in enumerate(self.columns):
            channel_info = {
                'label': channel_name,
                'dimension': 'mV',
                'sample_frequency': self.sampling_frequency,
                'physical_min': self.data[:, i].min(),
                'physical_max': self.data[:, i].max(),
            }
            writer.setSignalHeader(i, channel_info)

        # writer.setStartdatetime(None)

        # Write the data
        writer.writeSamples([self.data[:, i] for i in range(self.data.shape[1])])

        # Close the file
        writer.close()

    def _serialize_to_xml(self) -> _ElementTree[_Element]:
        """Write waveform data to an XML record following the GE Muse Transactional
        XML developer's guide.

        While MUSE supports various data types, this method currently only supports
        writing out 16-bit signed integers.
        
        This function writes the waveform data to an XML file with the following structure:
            <Waveform>
                <LeadData>
                    <LeadByteCountTotal>1200</LeadByteCountTotal>
                    <LeadTimeOffset>0</LeadTimeOffset>
                    <LeadSampleCountTotal>600</LeadSampleCountTotal>
                    <LeadAmplitudeUnitsPerBit>4.88</LeadAmplitudeUnitsPerBit>
                    <LeadAmplitudeUnits>MICROVOLTS</LeadAmplitudeUnits>
                    <LeadHighLimit>32767</LeadHighLimit>
                    <LeadLowLimit>-32768</LeadLowLimit>
                    <LeadID>I</LeadID>
                    <LeadOffsetFirstSample>0</LeadOffsetFirstSample>
                    <FirstSampleBaseline>0</FirstSampleBaseline>
                    <LeadSampleSize>2</LeadSampleSize>
                    <LeadOff>FALSE</LeadOff>
                    <BaselineSway>FALSE</BaselineSway>
                    <LeadDataCRC32>1391929279</LeadDataCRC32>
                    <WaveFormData> ... </WaveFormData>
                </LeadData>
                ... (repeats for each lead)
            </Waveform>
        """
        # calculate an ideal amplitude units per bit
        leadwise_min = np.min(self.data, axis=0)
        leadwise_max = np.max(self.data, axis=0)

        digital_min, digital_max = -32768, 32767

        # calculate the amplitude units per bit for each lead
        # broadcasting digital scalars across each lead
        amplitude_units_per_bit = (leadwise_max - leadwise_min) / (digital_max - digital_min)
        baseline = digital_min - leadwise_min / amplitude_units_per_bit

        # adjust baseline to be an integer
        baseline = np.floor(baseline).astype(np.int16)

        # convert the signal from physical units (floating point) to integer
        # using the amplitude units per bit and baseline
        signal = np.floor(self.data / amplitude_units_per_bit + baseline)

        # ensure we don't underflow
        # -> can happen close to the negative range
        signal = np.clip(signal, digital_min, digital_max).astype(np.int16)

        root = ET.Element('RestingECG', attrib=None, nsmap=None)
        waveform = ET.SubElement(root, 'Waveform', attrib=None, nsmap=None)

        # waveform properties
        ET.SubElement(waveform, 'WaveformType').text = 'Rhythm'
        ET.SubElement(waveform, 'WaveformStartTime').text = '0'
        ET.SubElement(waveform, 'NumberofLeads').text = str(signal.shape[1])
        ET.SubElement(waveform, 'SampleType').text = 'CONTINUOUS_SAMPLES'
        ET.SubElement(waveform, 'SampleBase').text = str(self.sampling_frequency)
        ET.SubElement(waveform, 'SampleExponent').text = '0'
        ET.SubElement(waveform, 'HighPassFilter').text = '5'
        ET.SubElement(waveform, 'LowPassFilter').text = '100'
        ET.SubElement(waveform, 'ACFilter').text = '60'

        for i in range(signal.shape[1]):
            lead = ET.SubElement(waveform, 'LeadData')
            ET.SubElement(lead, 'LeadByteCountTotal').text = str(signal.shape[0] * 2)
            ET.SubElement(lead, 'LeadTimeOffset').text = '0'
            ET.SubElement(lead, 'LeadSampleCountTotal').text = str(signal.shape[0])
            ET.SubElement(lead, 'LeadAmplitudeUnitsPerBit').text = str(amplitude_units_per_bit[i])
            ET.SubElement(lead, 'LeadAmplitudeUnits').text = 'MILLIVOLTS'
            ET.SubElement(lead, 'LeadHighLimit').text = str(digital_max)
            ET.SubElement(lead, 'LeadLowLimit').text = str(digital_min)
            ET.SubElement(lead, 'LeadID').text = self.columns[i]
            ET.SubElement(lead, 'LeadOffsetFirstSample').text = '0'
            ET.SubElement(lead, 'FirstSampleBaseline').text = str(baseline[i])
            # encoding as 16-bit integers, so 2 bytes per sample
            ET.SubElement(lead, 'LeadSampleSize').text = '2'
            ET.SubElement(lead, 'LeadOff').text = 'FALSE'
            ET.SubElement(lead, 'BaselineSway').text = 'FALSE'

            # convert to integer and bytes
            lead_bytes = np.ascontiguousarray(signal[:, i], dtype='<i2').tobytes()

            # Cyclic Redundancy Check (CRC)
            # calculated on the bytes themselves, before encoding into a b64 string
            ET.SubElement(lead, 'LeadDataCRC32').text = str(crc32(lead_bytes))
            
            # encode to base64 and add to XML
            ET.SubElement(lead, 'WaveFormData').text = base64.b64encode(lead_bytes).decode()

        tree = ET.ElementTree(root)
        return tree

    def to_xml(self, record_filename: Union[str, Path]):
        tree = self._serialize_to_xml()
        tree.write(str(record_filename), encoding='utf-8', xml_declaration=True, pretty_print=True)

    def _to_wfdb(self, record_filename: Union[str, Path], fmt: str = '16'):
        """Load a WFDB record."""
        record_filename = remove_wfdb_suffix(record_filename)

        wfdb.wrsamp(
            record_filename.stem,
            fs=self.sampling_frequency,
            sig_name=self.columns,
            p_signal=self.data,
            fmt=[fmt] * self.data.shape[1],
            units=['mV'] * self.data.shape[1],
            write_dir = str(record_filename.parent.resolve())
        )

    def to_wfdb(self, record_filename: Union[str, Path]):
        """Load a WFDB record."""
        # As of WFDB 4.1.1, wrsamp expects there to be no extension in record name,
        # so we remove it if it exists
        self._to_wfdb(record_filename, fmt='16')

    def to_wfdbz(self, record_filename: Union[str, Path]):
        """Load a WFDB record."""
        # As of WFDB 4.1.1, wrsamp expects there to be no extension in record name,
        # so we remove it if it exists
        self._to_wfdb(record_filename, fmt='516')


@dataclass
class WaveformMetadata:
    age: Optional[int] = None
    sex: Optional[str] = None
    race: Optional[str] = None
    arrhythmia: Optional[List[int]] = field(default_factory=list)
    potassium:  Optional[float] = None
    lvef: Optional[int] = None

    @classmethod
    def from_edf(cls, record_filename: Union[str, Path]):
        """Load an EDF record."""
        # Open EDF file
        f = pyedflib.EdfReader(record_filename)

        # Get the header information
        header = f.getHeader()

        return cls(
            # TODO: convert startdate and birthdate keys into an age
            # startdate is a datetime, birthdate is free-text
            age=header.get('age', None),
            sex=header.get('gender', None),
            # TODO: get dx from annotations
        )

    @classmethod
    def from_wfdb(cls, record_filename: Union[str, Path]):
        """
        Load metadata from a WFDB (WaveForm DataBase) record file.

        Args:
            record_filename (Path): Path to the WFDB record file.

        Returns:
            dict: A dictionary containing metadata about the record file with the following keys:
                - 'sampling_frequency': Sampling frequency of the record
                - 'units' (str): Units of the record
                - 'age' (int): Age of the patient in years (if available)
                - 'sex' (str): Sex of the patient (e.g., Male, Female)
                - 'race' (str): Race of the patient (e.g., White, Black Or African American)
                - 'dx' (list of int): Diagnosis codes for the record (if available, otherwise None)
        """
        record_filename = remove_wfdb_suffix(record_filename)

        # only load the header for a record
        record = wfdb.rdheader(record_filename, rd_segments=False)

        if record.comments is None:
            return cls()
        data = {}

        # iterate through comments for demographics, load in
        # the data if present
        demographic_vars = ['age', 'sex', 'race', 'dx']
        for var in demographic_vars:
            data[var] = None
        for line in record.comments:
            for var in demographic_vars:
                if line.lower().strip().startswith(f'{var}:'):
                    data[var] = line.split(':')[1].strip()
        
        # parse vars
        if data['age'] is not None:
            try:
                data['age'] = int(data['age'])
            except ValueError:
                data['age'] = None
        if data['sex'] is not None:
            data['sex'] = data['sex'].title()
        if data['race'] is not None:
            data['race'] = data['race'].title()
        if data['dx'] is not None:
            data['dx'] = [int(x) for x in data['dx'].split(',')]

        data['arrhythmia'] = data.pop('dx')

        return cls(**data)

    @classmethod
    def _parse_xml_data(cls, root: _Element) -> WaveformMetadata:
        """Load waveform metadata from an XML record. The XML record is
        assumed to be in a GE MUSE XML format."""
        data = {}
        
        demographics = root.find('PatientDemographics')
        if demographics is not None:
            data['age'] = demographics.find('PatientAge')
            data['sex'] = demographics.find('Gender')
            data['race'] = demographics.find('Race')

        for key in ['age', 'sex', 'race']:
            if data[key] is not None:
                data[key] = data[key].text

        # TODO: some thought here once the data actually comes in
        dx = root.find('Diagnosis')
        # iterate through the DiagnosisStatement elements under diagnosis
        # and get the StmtText attribute under it
        if dx is None:
            data['arrhythmia'] = None
            return cls(**data)

        dx_output = []
        for stmt in dx.iter('DiagnosisStatement'):
            stmt_text = stmt.find('StmtText')
            if stmt_text is not None:
                dx_output.append(stmt_text.text)
        dx_output = ', '.join(dx_output)
        # TODO: above dx is free text
        # need to convert to a list of codes
        # for now, just return the free text
        data['arrhythmia'] = dx_output

        return cls(**data)

    @classmethod
    def from_xml_string(cls, xml_string: str) -> WaveformMetadata:
        # parse the element tree
        root = ET.fromstring(xml_string, parser=None)
        return cls._parse_xml_data(root)

    @classmethod
    def from_xml(cls, record_filename: Union[str, Path]) -> WaveformMetadata:
        # parse the element tree
        etree = ET.parse(record_filename, parser=None)
        root = etree.getroot()
        return cls._parse_xml_data(root)

    @classmethod
    def from_csv(cls, record_name: Union[str, Path]):
        """Load metadata for a CSV record. Not implemented."""
        raise NotImplementedError('Cannot load metadata from CSV.')

    @classmethod
    def from_json(cls, record_name: Union[str, Path]):
        """Load metadata for a JSON record."""
        with open(record_name, 'r') as fp:
            data = json.load(fp)
        
        # TODO: parse and remove irrelevant attributes
        return cls(**data)

    def to_json(self, record_name: Union[str, Path]):
        """Load metadata for a CSV record. Not implemented."""
        
        # TODO: get attributes dynamically
        data = {
            'age': self.age,
            'sex': self.sex,
            'race': self.race,
            'arrhythmia': self.arrhythmia,
            'potassium': self.potassium,
            'lvef': self.lvef,
        }

        with open(record_name, 'w') as fp:
            json.dump(data, fp)
