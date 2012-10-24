from nose.tools import *
from metar import Station
from metar import Metar
import numpy as np
import datetime as dt
import types
import os
import pandas
import urllib2
import matplotlib
import matplotlib.dates as mdates

class testClass(object):
    def value(self):
        return 'item2'

def makeStationAndTS():
    sta = Station.station('KPDX', city='Portland', state='OR', 
                          country='Cascadia', lat=999, lon=999)
    start = dt.datetime(2001, 1, 1)
    ts = pandas.DatetimeIndex(start=start, freq='D', periods=1)[0]    
    return sta, ts

def makeFakeRainData():
    tdelta = dt.datetime(2001,1,1,1,5) - dt.datetime(2001,1,1,1,0)
    start = dt.datetime(2001, 1, 1, 12, 0)
    end = dt.datetime(2001, 1, 1, 16, 0)
    daterange_num = mdates.drange(start, end, tdelta)
    daterange = mdates.num2date(daterange_num)

    rain_raw = [ 
        0.,  1.,  2.,  3.,  4.,  4.,  4.,  4.,  4.,  4.,  4.,  4.,  
        0.,  0.,  0.,  0.,  0.,  5.,  5.,  5.,  5.,  5.,  5.,  5.,  
        0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  
        1.,  2.,  3.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]

    return daterange, rain_raw

def test_station():
    sta, ts = makeStationAndTS()
    attributes = ['sta_id', 'city', 'state', 'country', 'position',
                  'name', 'wunderground', 'asos', 'errorfile']
    for attr in attributes:
        assert_true(hasattr(sta, attr))
    pass

def test_find_dir():
    sta, ts = makeStationAndTS()
    sep = os.path.sep 
    testdir = sta._find_dir('asos', 'raw')

    if os.path.sep == '/':
        knowndir = 'data/KPDX/asos/raw'
    else:
        knowndir = 'data\\KPDX\\asos\\raw'

    assert_equal(testdir, knowndir)
    pass

def test_find_file():
    sta, ts = makeStationAndTS()
    testfile1 = sta._find_file(ts, 'asos', 'raw')
    testfile2 = sta._find_file(ts, 'wunderground', 'flat')

    knownfile1 = 'KPDX_200101.dat'
    knownfile2 = 'KPDX_20010101.csv'

    assert_equal(testfile1, knownfile1)
    assert_equal(testfile2, knownfile2)
    pass

def test_set_cookies():
    sta, ts = makeStationAndTS()
    assert_true(isinstance(sta.asos, urllib2.OpenerDirector))
    assert_true(isinstance(sta.wunderground, urllib2.OpenerDirector))
    pass

def test_url_by_date():
    sta, ts = makeStationAndTS()
    start = dt.datetime(2001, 1, 1)
    ts = pandas.DatetimeIndex(start=start, freq='M', periods=1)[0]
    testurl1 = sta._url_by_date(ts, src='wunderground')
    testurl2 = sta._url_by_date(ts, src='asos')

    knownurl1 = "http://www.wunderground.com/history/airport/KPDX/2001/01/31/DailyHistory.html?&&theprefset=SHOWMETAR&theprefvalue=1&format=1"
    knownurl2 = "ftp://ftp.ncdc.noaa.gov/pub/data/asos-fivemin/6401-2001/64010KPDX200101.dat"

    assert_equal(testurl1, knownurl1)
    assert_equal(testurl2, knownurl2)
    pass

def test_make_data_file():
    sta, ts = makeStationAndTS()
    testfile1 = sta._make_data_file(ts, 'wunderground', 'flat')
    testfile2 = sta._make_data_file(ts, 'asos', 'raw')

    if os.path.sep == '/':
        knownfile1 = 'data/KPDX/wunderground/flat/KPDX_20010101.csv'
        knownfile2 = 'data/KPDX/asos/raw/KPDX_200101.dat'
    else:
        knownfile1 = 'data\\KPDX\\wunderground\\flat\\KPDX_20010101.csv'
        knownfile2 = 'data\\KPDX\\asos\\raw\\KPDX_200101.dat'

    assert_equal(testfile1, knownfile1)
    assert_equal(testfile2, knownfile2)
    pass

def test_fetch_data():
    sta, ts = makeStationAndTS()
    status_asos = sta._fetch_data(ts, src='asos')
    status_wund = sta._fetch_data(ts, src='wunderground')
    known_statuses = ['ok', 'bad', 'not there']
    assert_in(status_asos, known_statuses)
    assert_in(status_wund, known_statuses)
    pass

def test_attempt_download():
    sta, ts = makeStationAndTS()
    status_asos, attempt1 = sta._attempt_download(ts, src='asos')
    status_wund, attempt2 = sta._attempt_download(ts, src='wunderground')
    known_statuses = ['ok', 'bad', 'not there']
    assert_in(status_asos, known_statuses)
    assert_in(status_wund, known_statuses)
    ts2 = pandas.DatetimeIndex(start='1999-1-1', freq='D', periods=1)[0]
    status_fail, attempt3 = sta._attempt_download(ts2, src='asos')
    assert_equal(status_fail, 'not there')

    assert_less_equal(attempt1, 10)
    assert_less_equal(attempt2, 10)
    assert_equal(attempt3, 10)
    pass

def test_process_file_asos():
    sta, ts = makeStationAndTS()
    filename, status = sta._process_file(ts, 'asos')

    if os.path.sep == '/':
        knownfile = 'data/KPDX/asos/flat/KPDX_200101.csv'
    else:
        knownfile = 'data\\KPDX\\asos\\flat\\KPDX_200101.csv'
    
    assert_equal(filename, knownfile)
    known_statuses = ['ok', 'bad', 'not there']
    assert_in(status, known_statuses)
    pass

def test_process_file_wunderground():
    sta, ts = makeStationAndTS()
    filename, status = sta._process_file(ts, 'wunderground')

    if os.path.sep == '/':
        knownfile = 'data/KPDX/wunderground/flat/KPDX_20010101.csv'
    else:
        knownfile = 'data\\KPDX\\wunderground\\flat\\KPDX_20010101.csv'
    
    assert_equal(filename, knownfile)
    known_statuses = ['ok', 'bad', 'not there']
    assert_in(status, known_statuses)
    pass

def test_read_csv_asos():
    sta, ts = makeStationAndTS()
    data = sta._read_csv(ts, 'asos')
    known_columns = ['Sta', 'Date', 'Precip', 'Temp', 
                     'DewPnt', 'WindSpd', 'WindDir', 
                     'AtmPress', 'SkyCover']
    for col in data.columns:
        assert_in(col, known_columns)
    pass

def test_read_csv_wunderground():
    sta, ts = makeStationAndTS()
    data = sta._read_csv(ts, 'wunderground')
    known_columns = ['Sta', 'Date', 'Precip', 'Temp', 
                     'DewPnt', 'WindSpd', 'WindDir', 
                     'AtmPress', 'SkyCover']
    for col in data.columns:
        assert_in(col, known_columns)
    pass

def test_getASOSData_columns():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-2-1'
    data = sta.getASOSData(start, end)
    known_columns = ['Sta', 'Date', 'Precip', 'Temp', 
                     'DewPnt', 'WindSpd', 'WindDir', 
                     'AtmPress', 'SkyCover']
    for col in data.columns:
        assert_in(col, known_columns)
    pass

def test_getASOSData_index():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-9-1'
    data = sta.getASOSData(start, end)
    assert_true(data.index.is_unique)
    pass

def test_getWundergroundData_columns():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-2-1'
    data = sta.getWundergroundData(start, end)
    known_columns = ['Sta', 'Date', 'Precip', 'Temp', 
                     'DewPnt', 'WindSpd', 'WindDir', 
                     'AtmPress', 'SkyCover']
    for col in data.columns:
        assert_in(col, known_columns)
    pass

def test_getWundergroundData_index():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-9-1'
    data = sta.getWundergroundData(start, end)
    assert_true(data.index.is_unique)
    pass

def test_getData():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-2-1'
    assert_raises(ValueError, sta.getData, start, end, 'fart')

def test_parse_dates():
    datestrings = ['2012-6-4', 'September 23, 1982']
    knowndates = [dt.datetime(2012, 6, 4), dt.datetime(1982, 9, 23)]
    for ds, kd in zip(datestrings, knowndates):
        dd = Station._parse_date(ds)
        assert_equal(dd.year, kd.year)
        assert_equal(dd.month, kd.month)
        assert_equal(dd.day, kd.day)
    pass

def test_check_src():
    Station._check_src('asos')
    Station._check_src('wunderground')
    assert_raises(ValueError, Station._check_src, 'fart')
    pass

def test_check_step():
    Station._check_step('flat')
    Station._check_step('raw')
    assert_raises(ValueError, Station._check_step, 'fart')
    pass

def test_check_file():
    assert_equal(Station._check_file('test/testfile1'), 'bad')
    assert_equal(Station._check_file('test/testfile2'), 'ok')
    assert_equal(Station._check_file('test/testfile3'), 'not there')
    pass
    
def test_check_dirs():
    pass

def test_date_asos():
    teststring = '24229KPDX PDX20010101000010001/01/01 00:00:31  5-MIN KPDX'
    knowndate = dt.datetime(2001, 1, 1, 0, 0)
    assert_equal(Station._date_ASOS(teststring), knowndate)
    pass

def test_append_val():
    x = testClass()
    knownlist = ['item1', 'item2', 'NA']
    testlist = ['item1']
    testlist = Station._append_val(x, testlist)
    testlist = Station._append_val(None, testlist)
    assert_list_equal(testlist, knownlist)
    pass

def test_determine_reset_time():
    dates, precip = makeFakeRainData()
    test_rt = Station._determine_reset_time(dates, precip)
    known_rt = 0
    assert_equal(known_rt, test_rt)
    pass

def test_process_precip():
    dates, precip = makeFakeRainData()
    test_rt = Station._determine_reset_time(dates, precip)
    known_rt = 0
    p2 = Station._process_precip(dates, precip)
    assert_true(np.all(p2 <= precip))
    pass


def test_process_sky_cover():
    teststring = 'METAR KPDX 010855Z 00000KT 10SM FEW010 OVC200 04/03 A3031 RMK AO2 SLP262 T00390028 53010 $'
    obs = Metar.Metar(teststring)
    testval = Station._process_sky_cover(obs)
    assert_equal(testval, 1.0000)
    pass

def test_rain_clock():
    sta, ts = makeStationAndTS()
    data = sta.getASOSData('2001-1-1', '2001-2-1')
    fig, (ax1, ax2) = Station.rainClock(data.Precip)
    assert_true(isinstance(fig, matplotlib.figure.Figure))
    assert_true(isinstance(ax2, matplotlib.axes.Axes))
    assert_true(isinstance(ax2, matplotlib.axes.Axes))    
    pass

def test_getAllStations():
    stations = Station.getAllStations()
    pass

def test_getStationByID():
    pdx = Station.getStationByID('KPDX')
    assert_true(isinstance(pdx, Station.station))
    pass

