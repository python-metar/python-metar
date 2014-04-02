from nose.tools import *
from metar import station
from metar import graphics
import datetime as dt
import pandas
import matplotlib
import matplotlib.pyplot as plt

class test_graphics():
    def setup(self):
        self.sta = station.WeatherStation('KPDX', city='Portland', state='OR',
                                     country='Cascadia', lat=999, lon=999)
        self.start = dt.datetime(2001, 1, 1)
        self.ts = pandas.DatetimeIndex(start=self.start, freq='D', periods=1)[0]
        self.sta.getASOSData('2001-1-1', '2001-2-1')

    def teardown(self):
        plt.close('all')

    def test_rainClock(self):
        '''Confirm that rainClock returns an mpl figure and two axes'''
        fig = graphics.rainClock(self.sta.data['asos'],
                                 fname='test/test_rainClock.png')
        assert_true(isinstance(fig, matplotlib.figure.Figure))
        pass

    def test_windRose_kt(self):
        '''Confirm that windRose returns an mpl figure and one axis'''
        fig = graphics.windRose(self.sta.data['asos'],
                                     fname='test/test_windRose_kt.png',
                                     mph=False)
        assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_windRose_mph(self):
        '''Confirm that windRose returns an mpl figure and one axis'''
        fig = graphics.windRose(self.sta.data['asos'],
                                fname='test/test_windRose_mph.png',
                                mph=False)
        assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_hyetograph(self):
        '''Confirm that hyetograph returns an mpl figure and one axis'''
        for freq in ['5min', 'hourly', 'daily', 'weekly', 'monthly']:
            fname = 'test/test_hyetograph_%s.png' % freq
            fig = graphics.hyetograph(self.sta.data['asos'], freq=freq,
                                      fname=fname)
            assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_psychromograph(self):
        '''Confirm that psychromograph returns an mpl figure and one axis'''
        for freq in ['5min', 'hourly', 'daily', 'weekly', 'monthly']:
            fname = 'test/test_psychromograph_%s.png' % freq
            fig = graphics.psychromograph(self.sta.data['asos'], freq=freq,
                                          fname=fname)
            assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_temperaturePlot(self):
        '''Confirm that temperaturePlot returns an mpl figure and one axis'''
        for freq in ['5min', 'hourly', 'daily', 'weekly', 'monthly']:
            fname = 'test/test_temperaturePlot_%s.png' % freq
            fig = graphics.temperaturePlot(self.sta.data['asos'], freq=freq,
                                           fname=fname)
            assert_true(isinstance(fig, matplotlib.figure.Figure))
