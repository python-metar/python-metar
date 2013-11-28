from nose.tools import *
from metar import station
from metar import exporters
import datetime as dt
import pandas
import matplotlib
import matplotlib.pyplot as plt
from six import StringIO

class test_exporter():
    def setup(self):
        self.fivemin = pandas.read_csv('test/data_for_tests.csv', parse_dates=True, index_col=0)
        self.hourly = self.fivemin.resample('1H', how='sum')

        self.known_fivemin_swmm5_file = 'test/known_fivemin_swmm5.dat'
        self.known_hourly_swmm5_file = 'test/known_hourly_swmm5.dat'
        self.knwon_hourly_ncdc_file= 'test/known_hourly_ncdc.dat'

        with open('test/known_fivemin_swmm5.dat', 'r') as f:
            self.known_fivemin_swmm5 = f.read()

        with open('test/known_hourly_swmm5.dat', 'r') as f:
            self.known_hourly_swmm = f.read()

        with open('test/known_hourly_ncdc.dat', 'r') as f:
            self.known_hourly_ncdc = f.read()

    def teardown(self):
        plt.close('all')

    def test_dumpSWMM5Format_form(self):
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='5min',
            dropzeros=True,
            filename='test/test_dumpSWMM.dat'
        )
        assert_true(isinstance(data, pandas.DataFrame))
        assert_list_equal(
            data.columns.tolist(),
            ['station', 'year', 'month', 'day', 'hour', 'minute', 'precip']
        )

    def test_dumpSWMM5Format_DropZeros(self):
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='5min',
            dropzeros=True,
            filename='test/test_dumpSWMM_withoutZeros.dat'
        )
        assert_equal(data[data.precip == 0].shape[0], 0)

    def test_dumpSWMM5Format_KeepZeros(self):
        data = exporters.SWMM5Format(
            self.fivemin,
            'Test-Station',
            col='precip',
            freq='5min',
            dropzeros=False,
            filename='test/test_dumpSWMM_withZeros.dat'
        )
        assert_greater(data[data.precip == 0].shape[0], 0)

    def test_dumpSWMM5Format_Result5min(self):
        testfilename = 'test/test_dumpSWMM_fivemin.dat'
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

        assert_equal(known_data, test_data)

    def test_dumpSWMM5Format_ResultHourly(self):
        testfilename = 'test/test_dumpSWMM_hourly.dat'
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

        assert_equal(known_data, test_data)

    def test_dumpNCDCFormat(self):
        testfilename = 'test/test_dumpNCDCFormat.dat'
        data = exporters.NCDCFormat(
            self.hourly,
            '041685',
            'California',
            col='precip',
            filename=testfilename
        )

        with open(self.knwon_hourly_ncdc_file, 'r') as f:
            known_data = f.read()

        with open(testfilename, 'r') as f:
            test_data = f.read()

        assert_equal(known_data, test_data)