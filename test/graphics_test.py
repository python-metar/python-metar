from nose.tools import *
from metar import station
from metar import metar
from metar import graphics
import numpy as np
import datetime as dt
import types
import os
import pandas
import urllib2
import matplotlib
import matplotlib.dates as mdates

def makeStationAndTS():
    sta = station.WeatherStation('KPDX', city='Portland', state='OR',
                          country='Cascadia', lat=999, lon=999)
    start = dt.datetime(2001, 1, 1)
    ts = pandas.DatetimeIndex(start=start, freq='D', periods=1)[0]
    return sta, ts

def test_rainClock():
    '''Confirm that rainClock returns an mpl figure and two axes'''
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    fig, (ax1, ax2) = graphics.rainClock(data, fname='test/test_rainClock.png')
    assert_true(isinstance(fig, matplotlib.figure.Figure))
    assert_true(isinstance(ax1, matplotlib.axes.Axes))
    assert_true(isinstance(ax2, matplotlib.axes.Axes))
    pass

def test_windRose():
    '''Confirm that windRose returns an mpl figure and one axis'''
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    fig, ax1 = graphics.windRose(data, fname='test/test_windRose.png')
    assert_true(isinstance(fig, matplotlib.figure.Figure))
    assert_true(isinstance(ax1, matplotlib.axes.Axes))

def test_hyetograph():
    '''Confirm that hyetograph returns an mpl figure and one axis'''
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    for freq in ['5min', 'hourly', 'daily', 'weekly', 'monthly']: #, 'yearly']:
        fig, ax1 = graphics.hyetograph(data, freq=freq, 
                     fname='test/test_hyetograph_%s.png' % freq)
        assert_true(isinstance(fig, matplotlib.figure.Figure))
        assert_true(isinstance(ax1, matplotlib.axes.Axes))

def test_psychromograph():
    '''Confirm that psychromograph returns an mpl figure and one axis'''
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    for freq in ['5min', 'hourly', 'daily', 'weekly', 'monthly']: #, 'yearly']:
        fig, ax1 = graphics.psychromograph(data, freq=freq,
                     fname='test/test_psychromograph_%s.png' % freq)
        assert_true(isinstance(fig, matplotlib.figure.Figure))
        assert_true(isinstance(ax1, matplotlib.axes.Axes))

def test_temperaturePlot():
    '''Confirm that temperaturePlot returns an mpl figure and one axis'''
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    for freq in ['5min', 'hourly', 'daily', 'weekly', 'monthly']: #, 'yearly']:
        fig, ax1 = graphics.temperaturePlot(data, freq=freq,
                      fname='test/test_temperaturePlot_%s.png' % freq)
        assert_true(isinstance(fig, matplotlib.figure.Figure))
        assert_true(isinstance(ax1, matplotlib.axes.Axes))