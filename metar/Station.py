#!/usr/bin/python
#
#  Python module to provide station information from the ICAO identifiers
#
#  Copyright 2004  Tom Pollard

# metar stuff
import Metar
import Datatypes

# std lib stuff
import datetime
import urllib2
import cookielib
import pdb
import os

# math stuff
import numpy as np
import matplotlib
#matplotlib.rcParams['timezone'] = 'UTC'
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas

class station:
    """An object representing a weather station."""

    def __init__(self, sta_id, city=None, state=None,
                country=None, latitude=None, longitude=None):
        self.sta_id = sta_id
        self.city = city
        self.state = state
        self.country = country
        self.position = Datatypes.position(latitude,longitude)
        if self.state:
            self.name = "%s, %s" % (self.city, self.state)
        else:
            self.name = self.city

        self.wundergound = self._set_cookies(src='wunderground')
        self.asos = self._set_cookies(src='asos')

    def _find_dir(self, src, step):
        '''
        returns a string representing the relative path to the requsted data

        input:
            *src* : 'asos' or 'wunderground'
            *step* : 'raw' or 'flat'
        '''
        _check_src(src)
        _check_step(step)
        return os.path.join('data', self.sta_id, src.lower(), step.lower())

    def _find_file(self, timestamp, src, step):
        '''
        returns a file name for a data file from the *src* based on the *timestamp*

        input:
            *timestamp* : pands timestamp object
            *src* : 'asos' or 'wunderground'
            *step* : 'raw' or 'flat'
        '''
        date = timestamp.to_datetime()
        _check_src(src)
        _check_step(step)

        if step == 'raw':
            ext = 'dat'
        else:
            ext = 'csv'

        if src.lower() == 'wunderground' or step == 'final':
            datefmtstr = '%Y%m%d'
        else:
            datefmtstr = '%Y%m'

        return '%s_%s.%s' % (self.sta_id, date.strftime(datefmtstr), ext)

    def _set_cookies(self, src):
        '''
        function that returns a urllib2 opener for retrieving data from *src*

        input:
            *src* : 'asos' or 'wunderground'
        '''
        jar = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(jar)
        opener = urllib2.build_opener(handler)
        try:
            if src.lower() == 'wunderground':
                url1 = 'http://www.wunderground.com/history/airport/%s/2011/12/4/DailyHistory.html?' % self.sta_id
                url2 = 'http://www.wunderground.com/cgi-bin/findweather/getForecast?setpref=SHOWMETAR&value=1'
                url3 = 'http://www.wunderground.com/history/airport/%s/2011/12/4/DailyHistory.html?&&theprefset=SHOWMETAR&theprefvalue=1&format=1' % self.sta_id

                opener.open(url1)
                opener.open(url2)
                opener.open(url3)
            elif src.lower() == 'asos':
                url = 'ftp://ftp.ncdc.noaa.gov/pub/data/asos-fivemin/'
                opener.open(url)
        except urllib2.URLError:
            print('connection to %s not available. working locally' % src)

        return opener

    def _url_by_date(self, timestamp, src='wunderground'):
        '''
        function that returns a url to retrieve data for a *timestamp*
        from the *src*

        input:
            *src* : 'asos' or 'wunderground'
            *timestamp* : pands timestamp object
        '''
        date = timestamp.to_datetime()
        "http://www.wunderground.com/history/airport/KDCA/1950/12/18/DailyHistory.html?format=1"
        _check_src(src)
        if src.lower() == 'wunderground':
            baseurl = 'http://www.wunderground.com/history/airport/%s' % self.sta_id
            endurl =  'DailyHistory.html?&&theprefset=SHOWMETAR&theprefvalue=1&format=1'
            datestring = date.strftime('%Y/%m/%d')
            url = '%s/%s/%s' % (baseurl, datestring, endurl)
        elif src.lower() == 'asos':
            baseurl = 'ftp://ftp.ncdc.noaa.gov/pub/data/asos-fivemin/6401-'
            url = '%s%s/64010%s%s%02d.dat' % \
                        (baseurl, date.year, self.sta_id, date.year, date.month)
        else:
            raise ValueError, "src must be 'wunderground' or 'asos'"
        return url

    def _make_data_file(self, timestamp, src, step):
        '''
        creates a data file for a *timestamp* from a *src* at a *step*

        input:
            *timestamp* : pands timestamp object
            *src* : 'asos' or 'wunderground'
            *step* : 'raw' or 'flat'
        '''
        _check_src(src)
        _check_step(step)
        datadir = self._find_dir(src, step)
        datafile = self._find_file(timestamp, src, step)
        subdirs = datadir.split(os.path.sep)
        _check_dirs(subdirs)
        return os.path.join(datadir, datafile)

    def _get_data(self, timestamp, errorfile=None, src='asos', force_download=False):
        ''' method that downloads data from a *src* for a *timestamp*
        returns the status of the download
            ('ok', 'bad', 'not there')
        input:
        *timestamp* : pands timestamp object
        *src* : 'asos' or 'wunderground'
        *errorfile* : writable buffer to log errors in retrieving data
        *force_download* : bool; default False
        '''
        date = timestamp.to_datetime()
        observations = []
        outname = self._make_data_file(timestamp, src, 'raw')
        status = 'not there'
        if not os.path.exists(outname) or force_download:
            outfile = open(outname, 'w')
            url = self._url_by_date(timestamp, src=src)
            if src.lower() == 'wunderground':
                try:
                    webdata = self.wunderground.open(url)
                    weblines = webdata.readlines()
                    outfile.writelines(weblines)
                except:
                    print('error on: %s\n' % (url,))
                    outfile.close()
                    os.remove(outname)
                    if errorfile is not None:
                        errorfile.write('error on: %s\n' % (url,))
            elif src.lower() == 'asos':
                try:
                    webdata = self.asos.open(url)
                    weblines = webdata.readlines()
                    outfile.writelines(weblines)
                except:
                    outfile.close()
                    os.remove(outname)
                    print('error on: %s\n' % (url,))
                    if errorfile is not None:
                        errorfile.write('error on: %s\n' % (url,))
            outfile.close()
            status = _check_file(outname)
        else:
            status = _check_file(outname)

        #print('%s - %s' % (date.strftime('%Y-%m'), status))
        return status

    def _attempt_download(self, timestamp, errorfile, src, attempt=0, max_attempts=10):
        '''
        recursively calls _attempt_download at most *max_attempts* times.
        returns the status of the download
            ('ok', 'bad', 'not there')
        input:
            *timestamp* : a pandas timestamp object
            *errorfile* : writable buffer to log errors
            *src* : 'asos' or 'wunderground'
            *attempt* : the current attempt number
            *max_attempts* : the max number of tries to download a file (default=10)
        '''
        attempt += 1
        status = self._get_data(timestamp, errorfile=errorfile, src=src)
        if status == 'not there' and attempt < max_attempts:
            attempt += 1
            self._attempt_download(timestamp, errorfile,
                                   src, attempt=attempt)

        return status

    def _process_ASOS_file(self, timestamp, errorfile):
        '''
        processes as raw ASOS data file (*.dat) to a flat file (*csv).
        returns the filename and status of the download
            ('ok', 'bad', 'not there')

        input:
            *timestamp* : a pandas timestamp object
            *errorfile* : writable buffer to log errors
        '''
        date = timestamp.to_datetime()
        rawfilename = self._make_data_file(timestamp, 'asos', 'raw')
        flatfilename = self._make_data_file(timestamp, 'asos', 'flat')
        if not os.path.exists(rawfilename):
            rawstatus = self._attempt_download(timestamp, errorfile,
                                               'asos', attempt=0)
        else:
            rawstatus = _check_file(rawfilename)

        if not os.path.exists(flatfilename) and rawstatus == 'ok':
            datain = open(rawfilename, 'r')
            dataout = open(flatfilename, 'w')

            headers = 'Sta,Date,Precip1hr,Precip5min,Temp,' + \
                        'DewPnt,WindSpd,WindDir,AtmPress\n'
            dataout.write(headers)

            dates = []
            rains = []
            temps = []
            dewpt = []
            windspd = []
            winddir = []
            press = []
            for metarstring in datain:
                obs = Metar.Metar(metarstring, errorfile=errorfile)
                dates.append(_date_ASOS(metarstring))
                rains = _append_val(obs.precip_1hr, rains, fillNone=0.0)
                temps = _append_val(obs.temp, temps)
                dewpt = _append_val(obs.dewpt, dewpt)
                windspd = _append_val(obs.wind_speed, windspd)
                winddir = _append_val(obs.wind_dir, winddir)
                press = _append_val(obs.press, press)

            rains = np.array(rains)
            dates = np.array(dates)

            final_precip = _process_precip(dates, rains)

            for row in zip([self.sta_id]*rains.shape[0], dates, rains, final_precip, \
                            temps, dewpt, windspd, winddir, press):
                dataout.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % row)

            datain.close()
            dataout.close()
        flatstatus = _check_file(flatfilename)
        return flatfilename, flatstatus

    def _read_csv(self, timestamp, errorfile, src):
        '''
        tries to retrieve data from the web from *src* for a *timestamp*
        returns a pandas dataframe if the download and prcoessing are
        successful. returns None if they fail.

        input:
            *timestamp* : a pandas timestamp object
            *errorfile* : writable buffer to log errors
            *src* : 'asos' or 'wunderground'
        '''
        flatfilename = self._make_data_file(timestamp, src, 'flat')
        if not os.path.exists(flatfilename):
            if src.lower() == 'asos':
                flatfilename, flatstatus = self._process_ASOS_file(timestamp, errorfile)

        flatstatus = _check_file(flatfilename)
        if flatstatus == 'ok':
            data = pandas.read_csv(flatfilename, index_col=[1], parse_dates=True)
        else:
            data = None

        return data

    def getASOSdata(self, startdate, enddate, errorfile):
        '''
        This function will return ASOS data in the form of a pandas dataframe
        for the station between *startdate* and *enddate*.

        Input:
            *startdate* : string representing the earliest date for the data
            *enddate* : string representing the latest data for the data
            *errorfile* : a writable buffer to log errors

        Returns:
            *data* : a pandas data frame of the ASOS data for this station

        Example:
        >>> import metar.Station as Station
        >>> startdate = '2012-1-1'
        >>> enddate = 'September 30, 2012'
        >>> errors = open('errors.log', 'a')
        >>> pdx = Station.station('KPDX')
        >>> data = pdx.getASOSdata(startdate, enddate, errors)
        >>> errors.close()
        '''
        start = _parse_date(startdate)
        end = _parse_date(enddate)
        timestamps = pandas.DatetimeIndex(start=start, end=enddate, freq='MS')
        data = None
        for ts in timestamps:
            if data is None:
                data = self._read_csv(ts, errorfile, 'asos')
            else:
                data = data.append(self._read_csv(ts, errorfile, 'asos'))

        return data

def _parse_date(datestring):
    '''
    takes a date string and returns a datetime.datetime object
    '''
    datenum = mdates.datestr2num(datestring)
    dateval = mdates.num2date(datenum)
    return dateval

def _check_src(src):
    '''
    checks that a *src* value is valid
    '''
    if src.lower() not in ('wunderground','asos'):
        raise ValueError('src must be one of "wunderground" or "asos"')

def _check_step(step):
    '''
    checks that a *step* value is valid
    '''
    if step.lower() not in ('raw','flat'):
        raise ValueError('step must be one of "raw" or "flat"')

def _check_file(filename):
    '''
    confirms that a raw file isn't empty
    '''
    try:
        testfile = open(filename, 'r')
        lines = testfile.readlines()
        testfile.close()
        if len(lines) > 1:
            status = 'ok'
        else:
            status = 'bad'

    except IOError:
        status = 'not there'

    return status

def _check_dirs(subdirs):
    '''
    checks to see that a directory exists. if not, it makes it.
    '''
    if not os.path.exists(subdirs[0]):
        #print('making '+subdirs[0])
        os.mkdir(subdirs[0])

    if len(subdirs) > 1:
        topdir = [os.path.join(subdirs[0],subdirs[1])]
        for sd in subdirs[2:]:
            topdir.append(sd)
        _check_dirs(topdir)

def _date_ASOS(metarstring):
    '''get date/time of asos reading'''
    yr = int(metarstring[13:17])   # year
    mo = int(metarstring[17:19])   # month
    da = int(metarstring[19:21])   # day
    hr = int(metarstring[37:39])   # hour
    mi = int(metarstring[40:42])   # minute

    date = datetime.datetime(yr,mo,da,hr,mi)

    return date

def _append_val(obsval, listobj, fillNone='NA'):
    '''
    appends attribute of an object to a list. if attribute does
    not exist or is none, appends the *fillNone* value instead.
    '''
    if obsval is not None and hasattr(obsval, 'value'):
        listobj.append(obsval.value())
    else:
        listobj.append(fillNone)
    return listobj

def _determine_reset_time(date, precip):
    '''
    determines the precip gauge reset time for a month's
    worth of ASOS data.
    '''
    minutes = np.zeros(12)
    if len(date) != len(precip):
        raise ValueError("date and precip must be same length")
    else:
        for n in range(1,len(date)):
            if precip[n] < precip[n-1]:
                minuteIndex = date[n].minute/5
                minutes[minuteIndex] += 1

        resetTime, = np.where(minutes==minutes.max())
        return resetTime[0]*5

def _process_precip(dateval, p1):
    '''convert 5-min rainfall data from cumuative w/i an hour to 5-min totals
    p = precip data (list)
    dt = list of datetime objects
    RT = point in the hour when the tip counter resets
    #if (p1[n-1] <= p1[n]) and (dt[n].minute != RT):'''
    RT = _determine_reset_time(dateval, p1)
    p2 = np.zeros(len(p1))
    p2[0] = p1[0]
    for n in range(1, len(p1)):

        tdelta = dateval[n] - dateval[n-1]
        if p1[n] < p1[n-1] or dateval[n].minute == RT or tdelta.seconds/60 != 5:
            p2[n] = p1[n]/100.

        #elif tdelta.seconds/60 == 5 and dateval[n].minute != RT:
        else:
            p2[n] = (float(p1[n]) - float(p1[n-1]))

    return p2

def rainClock(rainfall):
    am_hours = np.arange(0, 12)
    am_hours[0] = 12
    rainhours = rainfall.index.hour
    rain_by_hour = []
    for hr in np.arange(24):
        selector = (rainhours == hr)
        total_depth = rainfall[selector].sum()
        num_obervations = rainfall[selector].count()
        rain_by_hour.append(total_depth/num_obervations)

    bar_width = 2*np.pi/12 * 0.8
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(7,3), subplot_kw=dict(polar=True))
    theta = np.arange(0.0, 2*np.pi, 2*np.pi/12)
    am_bars = ax1.bar(theta + 2*np.pi/12 * 0.1, rain_by_hour[:12], bar_width, color='DodgerBlue', linewidth=0.5)
    pm_bars = ax2.bar(theta + 2*np.pi/12 * 0.1, rain_by_hour[12:], bar_width, color='Crimson', linewidth=0.5)
    ax1.set_title('AM Hours')
    ax2.set_title('PM Hours')
    for ax in [ax1, ax2]:
        ax.set_theta_zero_location("N")
        ax.set_theta_direction('clockwise')
        ax.set_xticks(theta)
        ax.set_xticklabels(am_hours)
        ax.set_yticklabels([])

    return fig, (ax1, ax2)

def getAllStations():
    station_file_name = "nsd_cccc.txt"
    station_file_url = "http://www.noaa.gov/nsd_cccc.txt"
    stations = {}

    fh = open(station_file_name,'r')
    for line in fh:
        f = line.strip().split(";")
        stations[f[0]] = station(f[0],f[3],f[4],f[5],f[7],f[8])
    fh.close()

    return stations

def getStationByID(sta_id):
    stations = getAllStations()
    return stations[sta_id]

def processWundergroundFile(csvin, csvout, errorfile):
    coverdict = {'CLR' : 0,
                 'SKC' : 0,
                 'OVC' : 1,
                 'BKN' : 0.75,
                 'SCT' : 0.4375,
                 'FEW' : 0.1875,
                 'VV'  : 0.99}

    headers =['LocalTime',
              'Temperature C',
              'Dew Point C',
              'Humidity',
              'Sea Level Pressure hPa',
              'VisibilityKm',
              'Wind Direction',
              'Wind Speed Km/h',
              'Gust Speed Km/h',
              'Precipitationmm',
              'Events',
              'Conditions',
              'FullMetar',
              'WindDirDegrees',
              'DateUTC',
              'maxskycover',
              'allskycover->']
    datain = open(csvin, 'r')
    dataout = open(csvout, 'w')

    for h in headers[:-1]:
        dataout.write('%s,' % (h,))
    dataout.write('%s\n' % (headers[-1]),)

    junk = datain.readline()
    for line in datain:
        dataline = line.split('<')[0]
        row = dataline.split(',')
        dataout.write(dataline)
        datestr = row[-1]

        try:
            datenum = mdates.datestr2num(datestr)
            date = mdates.num2date(datenum)
            good = True
        except ValueError:
            good = False
            errorfile.write('%s: %s\n' % (date.strftime('%Y-%m-%d'), datestr))

        if good:
            metarstring = row[-3]
            obs = Metar.Metar(metarstring, errorfile=errorfile,
                              month=date.month, year=date.year)

            cover = []
            for sky in obs.sky:
                coverval = coverdict[sky[0]]
                cover.append(coverval)

            if len(cover) > 0:
                dataout.write(',%0.2f' % (np.max(cover),))
                for c in cover:
                    dataout.write(',%0.2f' % (c,))
            dataout.write('\n')

    datain.close()
    dataout.close()
