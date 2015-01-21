import shutil
import datetime as dt
import os

import nose.tools as ntools
import numpy as np
import pandas
from six.moves.urllib import request
import matplotlib.dates as mdates

from metar import station
from metar import metar

class fakeClass(object):
    def value(self):
        return 'item2'

def makeFakeRainData():
    tdelta = dt.datetime(2001, 1, 1, 1, 5) - dt.datetime(2001, 1, 1, 1, 0)
    start = dt.datetime(2001, 1, 1, 12, 0)
    end = dt.datetime(2001, 1, 1, 16, 0)
    daterange_num = mdates.drange(start, end, tdelta)
    daterange = mdates.num2date(daterange_num)

    rain_raw = [
        0.,  1.,  2.,  3.,  4.,  4.,  4.,  4.,  4.,  4.,  4.,  4.,
        0.,  0.,  0.,  0.,  0.,  5.,  5.,  5.,  5.,  5.,  5.,  5.,
        0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
        1.,  2.,  3.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.
    ]

    return daterange, rain_raw


class test_station():
    def setup(self):
        self.max_attempts = 3
        self.sta = station.WeatherStation('KPDX', city='Portland', state='OR',
                                          country='Cascadia', lat=999, lon=999,
                                          max_attempts=self.max_attempts)
        self.sta2 = station.WeatherStation('MWPKO3', max_attempts=self.max_attempts)
        self.start = dt.datetime(2012, 1, 1)
        self.end = dt.datetime(2012, 2, 28)
        self.ts = pandas.DatetimeIndex(start=self.start, freq='D', periods=1)[0]

        self.dates, self.fakeprecip = makeFakeRainData()

    def teardown(self):
        datapath = os.path.join(os.getcwd(), 'data')
        if os.path.exists(datapath):
            shutil.rmtree(datapath)

    def test_attributes(self):
        attributes = ['sta_id', 'city', 'state', 'country', 'position',
                      'name', 'wunderground', 'asos', 'errorfile', 'data']
        for attr in attributes:
            ntools.assert_true(hasattr(self.sta, attr))

    def test_find_dir(self):
        testdir = self.sta._find_dir('asos', 'raw')

        if os.path.sep == '/':
            knowndir = 'data/%s/asos/raw' % self.sta.sta_id
        else:
            knowndir = 'data\\%s\\asos\\raw' % self.sta.sta_id

        ntools.assert_equal(testdir, knowndir)

    def test_find_file(self):
        testfile1 = self.sta._find_file(self.ts, 'asos', 'raw')
        testfile2 = self.sta._find_file(self.ts, 'wunderground', 'flat')

        knownfile1 = '%s_201201.dat' % self.sta.sta_id
        knownfile2 = '%s_20120101.csv' % self.sta.sta_id

        ntools.assert_equal(testfile1, knownfile1)
        ntools.assert_equal(testfile2, knownfile2)

    def test_set_cookies(self):
        ntools.assert_true(isinstance(self.sta.asos, request.OpenerDirector))
        ntools.assert_true(isinstance(self.sta.wunderground, request.OpenerDirector))

    def test_url_by_date(self):
        testurl1 = self.sta._url_by_date(self.ts, src='wunderground')
        testurl2 = self.sta._url_by_date(self.ts, src='asos')
        print((self.ts))
        knownurl1 = "http://www.wunderground.com/history/airport/%s" \
                    "/2012/01/01/DailyHistory.html?&&theprefset=SHOWMETAR" \
                    "&theprefvalue=1&format=1" % self.sta.sta_id
        knownurl2 = "ftp://ftp.ncdc.noaa.gov/pub/data/asos-fivemin" \
                    "/6401-2012/64010%s201201.dat" % self.sta.sta_id

        ntools.assert_equal(testurl1, knownurl1)
        ntools.assert_equal(testurl2, knownurl2)

    def test_make_data_file(self):
        testfile1 = self.sta._make_data_file(self.ts, 'wunderground', 'flat')
        testfile2 = self.sta._make_data_file(self.ts, 'asos', 'raw')

        if os.path.sep == '/':
            knownfile1 = 'data/%s/wunderground/flat/%s_20120101.csv' % \
                (self.sta.sta_id, self.sta.sta_id)
            knownfile2 = 'data/%s/asos/raw/%s_201201.dat' % \
                (self.sta.sta_id, self.sta.sta_id)
        else:
            knownfile1 = 'data\\%s\\wunderground\\flat\\%s_20120101.csv' % \
                (self.sta.sta_id, self.sta.sta_id)
            knownfile2 = 'data\\%s\\asos\\raw\\%s_201201.dat' % \
                (self.sta.sta_id, self.sta.sta_id)

        ntools.assert_equal(testfile1, knownfile1)
        ntools.assert_equal(testfile2, knownfile2)

    def test_fetch_data(self):
        status_asos = self.sta._fetch_data(self.ts, 1, src='asos')
        status_wund = self.sta._fetch_data(self.ts, 1, src='wunderground')
        known_statuses = ['ok', 'bad', 'not there']
        ntools.assert_in(status_asos, known_statuses)
        ntools.assert_in(status_wund, known_statuses)

    def test_attempt_download(self):
        status_asos, attempt1 = self.sta._attempt_download(self.ts, src='asos')
        status_wund, attempt2 = self.sta._attempt_download(self.ts, src='wunderground')
        known_statuses = ['ok', 'bad', 'not there']
        ntools.assert_in(status_asos, known_statuses)
        ntools.assert_in(status_wund, known_statuses)
        self.ts2 = pandas.DatetimeIndex(start='1999-1-1', freq='D', periods=1)[0]
        status_fail, attempt3 = self.sta._attempt_download(self.ts2, src='asos')
        ntools.assert_equal(status_fail, 'not there')

        ntools.assert_less_equal(attempt1, self.max_attempts)
        ntools.assert_less_equal(attempt2, self.max_attempts)
        ntools.assert_equal(attempt3, self.max_attempts)

    def test_process_file_asos(self):
        filename, status = self.sta._process_file(self.ts, 'asos')

        if os.path.sep == '/':
            knownfile = 'data/%s/asos/flat/%s_201201.csv' % (self.sta.sta_id, self.sta.sta_id)
        else:
            knownfile = 'data\\%s\\asos\\flat\\%s_201201.csv' % (self.sta.sta_id, self.sta.sta_id)

        ntools.assert_equal(filename, knownfile)
        known_statuses = ['ok', 'bad', 'not there']
        ntools.assert_in(status, known_statuses)

    def test_process_file_wunderground(self):
        filename, status = self.sta._process_file(self.ts, 'wunderground')

        if os.path.sep == '/':
            knownfile = 'data/%s/wunderground/flat/%s_20120101.csv' % (self.sta.sta_id, self.sta.sta_id)
        else:
            knownfile = 'data\\%s\\wunderground\\flat\\%s_20120101.csv' % (self.sta.sta_id, self.sta.sta_id)

        ntools.assert_equal(filename, knownfile)
        known_statuses = ['ok', 'bad', 'not there']
        ntools.assert_in(status, known_statuses)

    def test_read_csv_asos(self):
        data, status = self.sta._read_csv(self.ts, 'asos')
        known_columns = ['Sta', 'Date', 'Precip', 'Temp',
                         'DewPnt', 'WindSpd', 'WindDir',
                         'AtmPress', 'SkyCover']
        for col in data.columns:
            ntools.assert_in(col, known_columns)

    def test_read_csv_wunderground(self):
        data, status = self.sta._read_csv(self.ts, 'wunderground')
        known_columns = ['Sta', 'Date', 'Precip', 'Temp',
                         'DewPnt', 'WindSpd', 'WindDir',
                         'AtmPress', 'SkyCover']
        for col in data.columns:
            ntools.assert_in(col, known_columns)

    def test_getASOSData_columns(self):
        known_columns = ['Sta', 'Date', 'Precip', 'Temp',
                         'DewPnt', 'WindSpd', 'WindDir',
                         'AtmPress', 'SkyCover']
        self.sta.getASOSData(self.start, self.end)
        for col in self.sta.data['asos'].columns:
            ntools.assert_in(col, known_columns)

    def test_getASOSData_index(self):
        self.sta.getASOSData(self.start, self.end)
        ntools.assert_true(self.sta.data['asos'].index.is_unique)

    def test_getWundergroundData_columns(self):
        known_columns = ['Sta', 'Date', 'Precip', 'Temp',
                         'DewPnt', 'WindSpd', 'WindDir',
                         'AtmPress', 'SkyCover']
        self.sta.getWundergroundData(self.start, self.end)
        for col in self.sta.data['wunder'].columns:
            ntools.assert_in(col, known_columns)

    def test_getWundergroundData_index(self):
        self.sta.getWundergroundData(self.start, self.end)
        ntools.assert_true(self.sta.data['wunder'].index.is_unique)

    def test_getDataBadSource(self):
        ntools.assert_raises(ValueError, self.sta._get_data, self.start, self.end, 'fart', None)

    def test_getDataGoodSource(self):
        self.sta._get_data(self.start, self.end, 'asos', None)

    def test_getDataSaveFile(self):
        self.sta._get_data(self.start, self.end, 'asos', 'testfile.csv')

    def test_parse_dates(self):
        datestrings = ['2012-6-4', 'September 23, 1982']
        knowndates = [dt.datetime(2012, 6, 4), dt.datetime(1982, 9, 23)]
        for ds, kd in zip(datestrings, knowndates):
            dd = station._parse_date(ds)
            ntools.assert_equal(dd.year, kd.year)
            ntools.assert_equal(dd.month, kd.month)
            ntools.assert_equal(dd.day, kd.day)

    def test_check_src(self):
        station._check_src('asos')
        station._check_src('wunderground')
        ntools.assert_raises(ValueError, station._check_src, 'fart')

    def test_check_step(self):
        station._check_step('flat')
        station._check_step('raw')
        ntools.assert_raises(ValueError, station._check_step, 'fart')

    def test_check_file(self):
        ntools.assert_equal(station._check_file('test/testfile1'), 'bad')
        ntools.assert_equal(station._check_file('test/testfile2'), 'ok')
        ntools.assert_equal(station._check_file('test/testfile3'), 'not there')

    def test_check_dirs(self):
        pass

    def test_date_asos(self):
        teststring = '24229KPDX PDX20010101000010001/01/01 00:00:31  5-MIN KPDX'
        knowndate = dt.datetime(2001, 1, 1, 0, 0)
        ntools.assert_equal(station._date_ASOS(teststring), knowndate)

    def test_append_val(self):
        x = fakeClass()
        knownlist = ['item1', 'item2', 'NA']
        testlist = ['item1']
        testlist = station._append_val(x, testlist)
        testlist = station._append_val(None, testlist)
        ntools.assert_list_equal(testlist, knownlist)

    def test_determine_reset_time(self):
        test_rt = station._determine_reset_time(self.dates, self.fakeprecip)
        known_rt = 0
        ntools.assert_equal(known_rt, test_rt)

    def test_process_precip(self):
        p2 = station._process_precip(self.dates, self.fakeprecip)
        ntools.assert_true(np.all(p2 <= self.fakeprecip))

    def test_process_sky_cover(self):
        teststring = 'METAR KPDX 010855Z 00000KT 10SM FEW010 OVC200 04/03 A3031 RMK AO2 SLP262 T00390028 53010 $'
        obs = metar.Metar(teststring)
        testval = station._process_sky_cover(obs)
        ntools.assert_equal(testval, 1.0000)

    def test_getAllStations(self):
        station.getAllStations()

    def test_getStationByID(self):
        pdx = station.getStationByID('KPDX')
        ntools.assert_true(isinstance(pdx, station.WeatherStation))

    def test_getASOSData_station(self):
        station.getASOSData(self.sta, '2012-1-1', '2012-2-1')
        station.getASOSData(self.sta, '2012-1-1', '2012-2-1', filename='testfile.csv')

    def test_getASOSData_string(self):
        station.getASOSData('KPDX', '2012-1-1', '2012-2-1')
        station.getASOSData('KPDX', '2012-1-1', '2012-2-1', filename='testfile.csv')

    def test_getWundergroundData_station(self):
        station.getWundergroundData(self.sta, '2012-1-1', '2012-2-1')
        station.getWundergroundData(self.sta, '2012-1-1', '2012-2-1', filename='testfile.csv')

    def test_getWundergroundData_string(self):
        station.getWundergroundData('KPDX', '2012-1-1', '2012-2-1')
        station.getWundergroundData('KPDX', '2012-1-1', '2012-2-1', filename='testfile.csv')

    def test_getWunderground_NonAirport_station(self):
        station.getWunderground_NonAirportData(self.sta2, '2012-1-1', '2012-2-1')
        station.getWunderground_NonAirportData(self.sta2, '2012-1-1', '2012-2-1', filename='testfile.csv')

    def test_getWunderground_NonAirport_string(self):
        station.getWunderground_NonAirportData('MWPKO3', '2012-1-1', '2012-2-1')
        station.getWunderground_NonAirportData('MWPKO3', '2012-1-1', '2012-2-1', filename='testfile.csv')

    def test_loadCompData_asos(self):
        self.sta.loadCompiledFile('asos', filename='testfile.csv')
        self.sta.loadCompiledFile('asos', filenum=1)

    def test_loadCompData_wunderground(self):
        self.sta.loadCompiledFile('wunderground', filename='testfile.csv')
        self.sta.loadCompiledFile('wunderground', filenum=1)

    def test_loadCompData_wunderground_nonairport(self):
        self.sta2.loadCompiledFile('wunder_nonairport', filename='testfile.csv')
        self.sta2.loadCompiledFile('wunder_nonairport', filenum=1)
