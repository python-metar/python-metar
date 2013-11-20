from nose.tools import *
from metar import station
from metar import exporters
import datetime as dt
import pandas
import matplotlib
import matplotlib.pyplot as plt

class test_exporter():
    def setup(self):
        self.sta = station.WeatherStation('KCEZ', city='Portland', state='OR',
                                     country='Cascadia', lat=999, lon=999)
        self.start = dt.datetime(2001, 1, 1)
        self.ts = pandas.DatetimeIndex(start=self.start, freq='D', periods=1)[0]
        self.sta.getASOSData('2009-1-1', '2009-2-1')

    def teardown(self):
        plt.close('all')

    def test_dumpSWMM5Format_form(self):
        data = exporters.SWMM5Format(
            self.sta.data['asos'],
            'Test-Station',
            col='Precip',
            freq='hourly',
            dropzeros=True,
            filename='test/test_dumpSWMM.dat'
        )
        assert_true(isinstance(data, pandas.DataFrame))
        assert_list_equal(
            data.columns.tolist(),
            ['station', 'year', 'month', 'day', 'hour', 'minute', 'precip']
        )
        assert_equal(data[data.precip == 0].shape[0], 0)

    def test_dumpSWMM5Format_DropZeros(self):
        data = exporters.SWMM5Format(
            self.sta.data['asos'],
            'Test-Station',
            col='Precip',
            freq='hourly',
            dropzeros=True,
            filename='test/test_dumpSWMM_withoutZeros.dat'
        )
        assert_equal(data[data.precip == 0].shape[0], 0)

    def test_dumpSWMM5Format_KeepZeros(self):
        data = exporters.SWMM5Format(
            self.sta.data['asos'],
            'Test-Station',
            col='Precip',
            freq='hourly',
            dropzeros=False,
            filename='test/test_dumpSWMM_withZeros.dat'
        )
        assert_greater(data[data.precip == 0].shape[0], 0)

    def test_dumpNCDCFormat(self):
        data = exporters.NCDCFormat(
            self.sta.data['asos'],
            '056318',
            'Oregon',
            filename='test/test_dumpNCDCFormat.dat'
        )