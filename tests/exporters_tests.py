import os
import sys

import nose.tools as ntools
import datetime as dt
import pandas
import matplotlib
import matplotlib.pyplot as plt
from six import StringIO

from metar import station
from metar import exporters


@ntools.nottest
def getTestFile(filename):
    current_dir, _ = os.path.split(__file__)
    return os.path.join(current_dir, 'data', filename)

class test_exporter(object):
    def setup(self):
        self.fivemin = pandas.read_csv(getTestFile('data_for_tests.csv'),
                                       parse_dates=True, index_col=0)
        self.hourly = self.fivemin.resample('1H', how='sum')

        self.known_fivemin_swmm5_file = getTestFile('known_fivemin_swmm5.dat')
        self.known_hourly_swmm5_file = getTestFile('known_hourly_swmm5.dat')
        self.known_hourly_ncdc_file = getTestFile('known_hourly_NCDC.dat')

        with open(self.known_fivemin_swmm5_file, 'r') as f:
            self.known_fivemin_swmm5 = f.read()

        with open(self.known_hourly_swmm5_file, 'r') as f:
            self.known_hourly_swmm = f.read()

        with open(self.known_hourly_ncdc_file, 'r') as f:
            self.known_hourly_ncdc = f.read()

        self.known_columns = ['station', 'year', 'month', 'day',
                              'hour', 'minute', 'precip']

    def test_dumpSWMM5Format_form(self):
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='5min',
            dropzeros=True,
            filename=getTestFile('test_dumpSWMM.dat')
        )
        ntools.assert_true(isinstance(data, pandas.DataFrame))
        ntools.assert_list_equal(
            data.columns.tolist(),
            self.known_columns
        )

    def test_dumpSWMM5Format_DropZeros(self):
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='5min',
            dropzeros=True,
            filename=getTestFile('test_dumpSWMM_withoutZeros.dat')
        )
        ntools.assert_equal(data[data.precip == 0].shape[0], 0)

    def test_dumpSWMM5Format_KeepZeros(self):
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='5min',
            dropzeros=False,
            filename=getTestFile('test_dumpSWMM_withZeros.dat')
        )
        ntools.assert_greater(data[data.precip == 0].shape[0], 0)

    def test_dumpSWMM5Format_Result5min(self):
        testfilename = getTestFile('test_dumpSWMM_fivemin.dat')
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='5min',
            dropzeros=True,
            filename=testfilename
        )
        with open(self.known_fivemin_swmm5_file, 'r') as f:
            known_data = f.read()

        with open(testfilename, 'r') as f:
            test_data = f.read()

        ntools.assert_equal(known_data, test_data)

    def test_dumpSWMM5Format_ResultHourly(self):
        testfilename = getTestFile('test_dumpSWMM_hourly.dat')
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='hourly',
            dropzeros=False,
            filename=testfilename
        )
        with open(self.known_hourly_swmm5_file, 'r') as f:
            known_data = f.read()

        with open(testfilename, 'r') as f:
            test_data = f.read()

        ntools.assert_equal(known_data, test_data)

    def test_dumpNCDCFormat(self):
        testfilename = getTestFile('test_dumpNCDCFormat.dat')
        data = exporters.NCDCFormat(
            self.hourly,
            '041685',
            'California',
            col='precip',
            filename=testfilename
        )

        with open(self.known_hourly_ncdc_file, 'r') as f:
            known_data = f.read()

        with open(testfilename, 'r') as f:
            test_data = f.read()

        ntools.assert_equal(known_data, test_data)


class test__pop_many(object):
    def setup(self):
        self.x = list('12345678')
        self.known_L1 = '1'
        self.known_L3 = '123'
        self.known_R1 = '8'
        self.known_R4 = '5678'

    def test_left1(self):
        popped = exporters._pop_many(self.x, 1)
        ntools.assert_equal(popped, self.known_L1)

    def test_left3(self):
        popped = exporters._pop_many(self.x, 3)
        ntools.assert_equal(popped, self.known_L3)

    def test_right1(self):
        popped = exporters._pop_many(self.x, 1, side='riGHt')
        ntools.assert_equal(popped, self.known_R1)

    def test_right4(self):
        popped = exporters._pop_many(self.x, 4, side='riGHt')
        ntools.assert_equal(popped, self.known_R4)


class _baseParseWriteObsMixin(object):
    def test_parse(self):
        parsed_obs = exporters._parse_obs(list(self.obs))
        ntools.assert_tuple_equal(parsed_obs, self.known_parsed)

    def test__write(self):
        row = exporters._write_obs('testheader', 2012, 5, 16, self.known_parsed)
        ntools.assert_equal(row, self.known_row)


class testParseWrite_ZeroWithFlag(_baseParseWriteObsMixin):
    def setup(self):
        self.obs = '1300000000M'
        self.known_parsed = (12, 00, 0.00, 'M')
        self.known_row = 'testheader,2012-05-16 12:00,0.00,M\n'


class testParseWrite_ZeroWithoutFlag(_baseParseWriteObsMixin):
    def setup(self):
        self.obs = '1300000000'
        self.known_parsed = (12, 00, 0.00, '')
        self.known_row = 'testheader,2012-05-16 12:00,0.00,\n'


class testParseWrite_Invalid(_baseParseWriteObsMixin):
    def setup(self):
        self.obs = '2200099999M'
        self.known_parsed = (21, 00, None, 'M')
        self.known_row = None


class testParseWrite_NonZeroWithFlag(_baseParseWriteObsMixin):
    def setup(self):
        self.obs = '0300000012A'
        self.known_parsed = (2, 00, 0.12, 'A')
        self.known_row = 'testheader,2012-05-16 02:00,0.12,A\n'


class testParseWrite_NonZeroWithoutFlag(_baseParseWriteObsMixin):
    def setup(self):
        self.obs = '0300000145'
        self.known_parsed = (2, 00, 1.45, '')
        self.known_row = 'testheader,2012-05-16 02:00,1.45,\n'


class testParseWrite_EndOfDay(_baseParseWriteObsMixin):
    def setup(self):
        self.obs = '2500000005I'
        self.known_parsed = (24, 00, 0.05, 'I')
        self.known_row = None


class _baseObsFromRow(object):
    def test_basic(self):
        obs = exporters._obs_from_row(self.row)
        ntools.assert_list_equal(obs, self.known_obs)


class testObsFromRow_Baseline(_baseObsFromRow):
    def setup(self):
        self.row = (
            'HPD04511406HPCPHI19480700010040100000000  '
            '1300000000M 2400000000M 2500000000I '
        )
        self.known_obs = [
            '045114,HPD,06HPCP,HI,1948-07-01 00:00,0.00,\n',
            '045114,HPD,06HPCP,HI,1948-07-01 12:00,0.00,M\n',
            '045114,HPD,06HPCP,HI,1948-07-01 23:00,0.00,M\n'
        ]


class testObsFromRow_WithInvalids(_baseObsFromRow):
    def setup(self):
        self.row = (
            'HPD04511406HPCPHI19480700010040100000000  '
            '0800000185A 0900099999M 1300000000M 2400000000M '
            '2500000000I '
        )
        self.known_obs = [
            '045114,HPD,06HPCP,HI,1948-07-01 00:00,0.00,\n',
            '045114,HPD,06HPCP,HI,1948-07-01 07:00,1.85,A\n',
            '045114,HPD,06HPCP,HI,1948-07-01 12:00,0.00,M\n',
            '045114,HPD,06HPCP,HI,1948-07-01 23:00,0.00,M\n'
        ]
