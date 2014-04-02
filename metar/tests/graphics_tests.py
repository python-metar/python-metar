from nose.tools import *
from metar import station
from metar import graphics
import datetime as dt
import pandas
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

class test_graphics():
    def setup(self):
        self.freqlist = ['5min', 'hourly', 'daily', 'weekly']
        self.df = pandas.read_csv('test/data_for_graphics_tests.csv',
                                  parse_dates=True, index_col=0)

    def teardown(self):
        plt.close('all')

    def test_rainClock(self):
        '''Confirm that rainClock returns an mpl figure and two axes'''
        fig = graphics.rainClock(self.df,
                                 fname='test/test_rainClock.png')
        assert_true(isinstance(fig, matplotlib.figure.Figure))
        pass

    def test_windRose_kt(self):
        '''Confirm that windRose returns an mpl figure and one axis'''
        fig = graphics.windRose(self.df,
                                     fname='test/test_windRose_kt.png',
                                     mph=False)
        assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_windRose_mph(self):
        '''Confirm that windRose returns an mpl figure and one axis'''
        fig = graphics.windRose(self.df,
                                fname='test/test_windRose_mph.png',
                                mph=False)
        assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_hyetograph(self):
        '''Confirm that hyetograph returns an mpl figure and one axis'''
        for freq in self.freqlist:
            fname = 'test/test_hyetograph_%s.png' % freq
            fig = graphics.hyetograph(self.df, freq=freq,
                                      fname=fname)
            assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_psychromograph(self):
        '''Confirm that psychromograph returns an mpl figure and one axis'''
        for freq in self.freqlist:
            fname = 'test/test_psychromograph_%s.png' % freq
            fig = graphics.psychromograph(self.df, freq=freq,
                                          fname=fname)
            assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_temperaturePlot(self):
        '''Confirm that temperaturePlot returns an mpl figure and one axis'''
        for freq in self.freqlist:
            fname = 'test/test_temperaturePlot_%s.png' % freq
            fig = graphics.temperaturePlot(self.df, freq=freq,
                                           fname=fname)
            assert_true(isinstance(fig, matplotlib.figure.Figure))
