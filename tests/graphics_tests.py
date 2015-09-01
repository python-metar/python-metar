import os
import sys

import nose.tools as ntools
import datetime as dt
import pandas
import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['text.usetex'] = False

from metar import station
from metar import graphics

@ntools.nottest
def getTestFile(filename):
    current_dir, _ = os.path.split(__file__)
    return os.path.join(current_dir, 'data', filename)

class test_graphics():
    def setup(self):
        self.freqlist = ['5min', 'hourly', 'daily', 'weekly']
        self.df = pandas.read_csv(getTestFile('data_for_graphics_tests.csv'),
                                  parse_dates=True, index_col=0)

    def teardown(self):
        plt.close('all')

    def test_rainClock(self):
        '''Confirm that rainClock returns an mpl figure and two axes'''
        fig = graphics.rainClock(self.df, fname=getTestFile('test_rainClock.png'))
        ntools.assert_true(isinstance(fig, matplotlib.figure.Figure))
        pass

    def test_windRose_kt(self):
        '''Confirm that windRose returns an mpl figure and one axis'''
        fig = graphics.windRose(self.df, fname=getTestFile('test_windRose_kt.png'),
                                mph=False)
        ntools.assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_windRose_mph(self):
        '''Confirm that windRose returns an mpl figure and one axis'''
        fig = graphics.windRose(self.df, fname=getTestFile('test_windRose_mph.png'),
                                mph=True)
        ntools.assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_hyetograph(self):
        '''Confirm that hyetograph returns an mpl figure and one axis'''
        for freq in self.freqlist:
            fname = getTestFile('test_hyetograph_%s.png' % freq)
            fig = graphics.hyetograph(self.df, freq=freq, fname=fname)
            ntools.assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_psychromograph(self):
        '''Confirm that psychromograph returns an mpl figure and one axis'''
        for freq in self.freqlist:
            fname = getTestFile('test_psychromograph_%s.png' % freq)
            fig = graphics.psychromograph(self.df, freq=freq, fname=fname)
            ntools.assert_true(isinstance(fig, matplotlib.figure.Figure))

    def test_temperaturePlot(self):
        '''Confirm that temperaturePlot returns an mpl figure and one axis'''
        for freq in self.freqlist:
            fname = getTestFile('test_temperaturePlot_%s.png' % freq)
            fig = graphics.temperaturePlot(self.df, freq=freq, fname=fname)
            ntools.assert_true(isinstance(fig, matplotlib.figure.Figure))
