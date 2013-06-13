from nose.tools import *
from metar import station
from metar import metar
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
    sta = station.WeatherStation('KSFO', city='Portland', state='OR',
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
        knowndir = 'data/%s/asos/raw' % sta.sta_id
    else:
        knowndir = 'data\\%s\\asos\\raw' % sta.sta_id

    assert_equal(testdir, knowndir)
    pass

def test_find_file():
    sta, ts = makeStationAndTS()
    testfile1 = sta._find_file(ts, 'asos', 'raw')
    testfile2 = sta._find_file(ts, 'wunderground', 'flat')

    knownfile1 = '%s_200101.dat' % sta.sta_id
    knownfile2 = '%s_20010101.csv' % sta.sta_id

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

    knownurl1 = "http://www.wunderground.com/history/airport/%s/2001/01/31/DailyHistory.html?&&theprefset=SHOWMETAR&theprefvalue=1&format=1" % sta.sta_id
    knownurl2 = "ftp://ftp.ncdc.noaa.gov/pub/data/asos-fivemin/6401-2001/64010%s200101.dat" % sta.sta_id

    assert_equal(testurl1, knownurl1)
    assert_equal(testurl2, knownurl2)
    pass

def test_make_data_file():
    sta, ts = makeStationAndTS()
    testfile1 = sta._make_data_file(ts, 'wunderground', 'flat')
    testfile2 = sta._make_data_file(ts, 'asos', 'raw')

    if os.path.sep == '/':
        knownfile1 = 'data/%s/wunderground/flat/%s_20010101.csv' % (sta.sta_id, sta.sta_id)
        knownfile2 = 'data/%s/asos/raw/%s_200101.dat' % (sta.sta_id, sta.sta_id)
    else:
        knownfile1 = 'data\\%s\\wunderground\\flat\\%s_20010101.csv' % (sta.sta_id, sta.sta_id)
        knownfile2 = 'data\\%s\\asos\\raw\\%s_200101.dat' % (sta.sta_id, sta.sta_id)

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
        knownfile = 'data/%s/asos/flat/%s_200101.csv' % (sta.sta_id, sta.sta_id)
    else:
        knownfile = 'data\\%s\\asos\\flat\\%s_200101.csv' % (sta.sta_id, sta.sta_id)

    assert_equal(filename, knownfile)
    known_statuses = ['ok', 'bad', 'not there']
    assert_in(status, known_statuses)
    pass

def test_process_file_wunderground():
    sta, ts = makeStationAndTS()
    filename, status = sta._process_file(ts, 'wunderground')

    if os.path.sep == '/':
        knownfile = 'data/%s/wunderground/flat/%s_20010101.csv' % (sta.sta_id, sta.sta_id)
    else:
        knownfile = 'data\\%s\\wunderground\\flat\\%s_20010101.csv' % (sta.sta_id, sta.sta_id)

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
    sta.getASOSData(start, end)
    known_columns = ['Sta', 'Date', 'Precip', 'Temp',
                     'DewPnt', 'WindSpd', 'WindDir',
                     'AtmPress', 'SkyCover']
    for col in sta.data['asos'].columns:
        assert_in(col, known_columns)
    pass

def test_getASOSData_index():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-9-1'
    sta.getASOSData(start, end)
    assert_true(sta.data['asos'].index.is_unique)
    pass

def test_getWundergroundData_columns():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-2-1'
    sta.getWundergroundData(start, end)
    known_columns = ['Sta', 'Date', 'Precip', 'Temp',
                     'DewPnt', 'WindSpd', 'WindDir',
                     'AtmPress', 'SkyCover']
    for col in sta.data['wunder'].columns:
        assert_in(col, known_columns)
    pass

def test_getWundergroundData_index():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-9-1'
    sta.getWundergroundData(start, end)
    assert_true(sta.data['wunder'].index.is_unique)
    pass

def test_getDataBadSource():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-2-1'
    assert_raises(ValueError, sta._get_data, start, end, 'fart', None)

def test_getDataGoodSource():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-2-1'
    sta._get_data(start, end, 'asos', None)

def test_getDataSaveFile():
    sta, ts = makeStationAndTS()
    start = '2012-1-1'
    end = '2012-2-1'
    sta._get_data(start, end, 'asos', 'testfile.csv')

def test_parse_dates():
    datestrings = ['2012-6-4', 'September 23, 1982']
    knowndates = [dt.datetime(2012, 6, 4), dt.datetime(1982, 9, 23)]
    for ds, kd in zip(datestrings, knowndates):
        dd = station._parse_date(ds)
        assert_equal(dd.year, kd.year)
        assert_equal(dd.month, kd.month)
        assert_equal(dd.day, kd.day)
    pass

def test_check_src():
    station._check_src('asos')
    station._check_src('wunderground')
    assert_raises(ValueError, station._check_src, 'fart')
    pass

def test_check_step():
    station._check_step('flat')
    station._check_step('raw')
    assert_raises(ValueError, station._check_step, 'fart')
    pass

def test_check_file():
    assert_equal(station._check_file('test/testfile1'), 'bad')
    assert_equal(station._check_file('test/testfile2'), 'ok')
    assert_equal(station._check_file('test/testfile3'), 'not there')
    pass

def test_check_dirs():
    pass

def test_date_asos():
    teststring = '24229KPDX PDX20010101000010001/01/01 00:00:31  5-MIN KPDX'
    knowndate = dt.datetime(2001, 1, 1, 0, 0)
    assert_equal(station._date_ASOS(teststring), knowndate)
    pass

def test_append_val():
    x = testClass()
    knownlist = ['item1', 'item2', 'NA']
    testlist = ['item1']
    testlist = station._append_val(x, testlist)
    testlist = station._append_val(None, testlist)
    assert_list_equal(testlist, knownlist)
    pass

def test_determine_reset_time():
    dates, precip = makeFakeRainData()
    test_rt = station._determine_reset_time(dates, precip)
    known_rt = 0
    assert_equal(known_rt, test_rt)
    pass

def test_process_precip():
    dates, precip = makeFakeRainData()
    test_rt = station._determine_reset_time(dates, precip)
    known_rt = 0
    p2 = station._process_precip(dates, precip)
    assert_true(np.all(p2 <= precip))
    pass

def test_process_sky_cover():
    teststring = 'METAR KPDX 010855Z 00000KT 10SM FEW010 OVC200 04/03 A3031 RMK AO2 SLP262 T00390028 53010 $'
    obs = metar.Metar(teststring)
    testval = station._process_sky_cover(obs)
    assert_equal(testval, 1.0000)
    pass

def test_getAllStations():
    stations = station.getAllStations()
    pass

def test_getStationByID():
    pdx = station.getStationByID('KPDX')
    assert_true(isinstance(pdx, station.WeatherStation))
    pass

def test_getASOSData_station():
    sta, ts = makeStationAndTS()
    station.getASOSData(sta, '2012-1-1', '2012-2-1')
    station.getASOSData(sta, '2012-1-1', '2012-2-1', filename='testfile.csv')

def test_getASOSData_string():
    station.getASOSData('KPDX', '2012-1-1', '2012-2-1')
    station.getASOSData('KPDX', '2012-1-1', '2012-2-1', filename='testfile.csv')

def test_getWundergroundData_station():
    sta, ts = makeStationAndTS()
    station.getWundergroundData(sta, '2012-1-1', '2012-2-1')
    station.getWundergroundData(sta, '2012-1-1', '2012-2-1', filename='testfile.csv')

def test_getWundergroundData_string():
    station.getWundergroundData('KPDX', '2012-1-1', '2012-2-1')
    station.getWundergroundData('KPDX', '2012-1-1', '2012-2-1', filename='testfile.csv')

def test_loadCompData_asos():
    sta, ts = makeStationAndTS()
    data = sta.loadCompiledFile('asos', filename='testfile.csv')
    data = sta.loadCompiledFile('asos', filenum=1)

def test_loadCompData_wunderground():
    sta, ts = makeStationAndTS()
    data = sta.loadCompiledFile('wunderground', filename='testfile.csv')
    data = sta.loadCompiledFile('wunderground', filenum=1)