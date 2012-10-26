from nose.tools import *
from metar import Station
from metar import Metar
from metar import Graphics
import numpy as np
import datetime as dt
import types
import os
import pandas
import urllib2
import matplotlib
import matplotlib.dates as mdates

def makeStationAndTS():
    sta = Station.station('KPDX', city='Portland', state='OR', 
                          country='Cascadia', lat=999, lon=999)
    start = dt.datetime(2001, 1, 1)
    ts = pandas.DatetimeIndex(start=start, freq='D', periods=1)[0]    
    return sta, ts

def test_rainClock():
    '''Confirm that rainClock returns an mpl figure and two axes'''
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    fig, (ax1, ax2) = Graphics.rainClock(data.Precip)
    assert_true(isinstance(fig, matplotlib.figure.Figure))
    assert_true(isinstance(ax1, matplotlib.axes.Axes))
    assert_true(isinstance(ax2, matplotlib.axes.Axes))    
    pass

def test_windRose():
    '''Confirm that windRose returns an mpl figure and one axis'''
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    fig, ax1 = Graphics.windRose(data)
    assert_true(isinstance(fig, matplotlib.figure.Figure))
    assert_true(isinstance(ax1, matplotlib.axes.Axes))