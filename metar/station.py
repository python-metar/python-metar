#!/usr/bin/python
#
#  Python module to provide station information from the ICAO identifiers
#
#  Copyright 2004  Tom Pollard

# std lib stuff
import datetime
import urllib2
import cookielib
import os
import pdb

# math stuff
import numpy as np
import matplotlib
import matplotlib.dates as mdates
import pandas

# metar stuff
import metar
import datatypes

__all__ = ['getAllStations', 'getStationByID', 'WeatherStation',
           'getASOSData', 'getWundergroundData', 'getWunderground_NonAirportData']
matplotlib.rcParams['timezone'] = 'UTC'


class WeatherStation(object):
    """An object representing a weather station."""

    def __init__(self, sta_id, city=None, state=None, country=None, lat=None, lon=None, max_attempts=10):
        self.sta_id = sta_id
        self.city = city
        self.state = state
        self.country = country
        self.position = datatypes.position(lat, lon)
        self.max_attempts = max_attempts

        if self.state:
            self.name = "%s, %s" % (self.city, self.state)
        else:
            self.name = self.city

        self.wunderground = self._set_cookies(src='wunderground')
        self.wunder_nonairport = self._set_cookies(src='wunder_nonairport')
        self.asos = self._set_cookies(src='asos')
        self.errorfile = 'data/%s_errors.log' % (sta_id,)
        self.data = {}

    def _find_dir(self, src, step):
        '''
        returns a string representing the relative path to the requsted data

        input:
            *src* : 'asos' or 'wunderground'
            *step* : 'raw' or 'flat' or 'compile'
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

        if src.lower() in ['wunderground', 'wunder_nonairport'] or step == 'final':
            datefmtstr = '%Y%m%d'
        else:
            datefmtstr = '%Y%m'

        return '%s_%s.%s' % (self.sta_id, date.strftime(datefmtstr), ext)

    def _set_cookies(self, src):
        '''
        function that returns a urllib2 opener for retrieving data from *src*

        input:
            *src* : 'asos' or 'wunderground' or 'wunder_nonairport'
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

            elif src.lower() == 'wunder_nonairport':
                url = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=MEGKO3&day=1&year=2013&month=1&graphspan=day&format=1'
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
            endurl = 'DailyHistory.html?&&theprefset=SHOWMETAR&theprefvalue=1&format=1'
            datestring = date.strftime('%Y/%m/%d')
            url = '%s/%s/%s' % (baseurl, datestring, endurl)

        elif src.lower() == 'wunder_nonairport':
            baseurl = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=%s' % self.sta_id
            endurl = '&day=%s&year=%s&month=%s&graphspan=day&format=1' % \
                (date.strftime('%d'), date.strftime('%Y'), date.strftime('%m'))
            url = '%s%s' % (baseurl, endurl)

        elif src.lower() == 'asos':
            baseurl = 'ftp://ftp.ncdc.noaa.gov/pub/data/asos-fivemin/6401-'
            url = '%s%s/64010%s%s%02d.dat' % \
                  (baseurl, date.year, self.sta_id, date.year, date.month)
        else:
            raise ValueError("src must be 'wunderground' or 'asos'")

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
        _check_dirs(datadir.split(os.path.sep))
        return os.path.join(datadir, datafile)

    def _fetch_data(self, timestamp, src='asos', force_download=False):
        ''' method that downloads data from a *src* for a *timestamp*
        returns the status of the download
            ('ok', 'bad', 'not there')
        input:
        *timestamp* : pands timestamp object
        *src* : 'asos' or 'wunderground'
        *force_download* : bool; default False
        '''

        outname = self._make_data_file(timestamp, src, 'raw')
        status = 'not there'
        errorfile = open(self.errorfile, 'a')
        if not os.path.exists(outname) or force_download:
            outfile = open(outname, 'w')
            url = self._url_by_date(timestamp, src=src)
            if src.lower() == 'wunderground':
                start = 2
                source = self.wunderground
            elif src.lower() == 'wunder_nonairport':
                start = 1
                source = self.wunder_nonairport
            elif src.lower() == 'asos':
                start = 0
                source = self.asos

            try:
                webdata = source.open(url)
                weblines = webdata.readlines()[start:]

                if src != 'wunder_nonairport':
                    outfile.writelines(weblines)
                else:
                    for line in weblines:
                        if line != '<br>\n':
                            outfile.write(line.strip() + '\n')

            except:
                print('error on: %s\n' % (url,))
                outfile.close()
                os.remove(outname)
                errorfile.write('error on: %s\n' % (url,))

            outfile.close()
            status = _check_file(outname)
        else:
            status = _check_file(outname)

        errorfile.close()
        return status

    def _attempt_download(self, timestamp, src, attempt=0):
        '''
        recursively calls _attempt_download at most *max_attempts* times.
        returns the status of the download
            ('ok', 'bad', 'not there')
        input:
            *timestamp* : a pandas timestamp object
            *src* : 'asos' or 'wunderground'
            *attempt* : the current attempt number
        '''
        attempt += 1
        status = self._fetch_data(timestamp, src=src)
        if status == 'not there' and attempt < self.max_attempts:
            print(attempt)
            status, attempt = self._attempt_download(timestamp, src, attempt=attempt)

        return status, attempt

    def _process_file(self, timestamp, src):
        '''
        processes a raw data file (*.dat) to a flat file (*csv).
        returns the filename and status of the download
            ('ok', 'bad', 'not there')

        input:
            *timestamp* : a pandas timestamp object
        '''
        #pdb.set_trace()
        _check_src(src)
        rawfilename = self._make_data_file(timestamp, src, 'raw')
        flatfilename = self._make_data_file(timestamp, src, 'flat')
        if not os.path.exists(rawfilename):
            rawstatus, attempt = self._attempt_download(timestamp, src, attempt=0)
        else:
            rawstatus = _check_file(rawfilename)

        if not os.path.exists(flatfilename) and rawstatus == 'ok':
            datain = open(rawfilename, 'r')
            dataout = open(flatfilename, 'w')

            if src.lower() in ['asos', 'wunderground']:

                headers = 'Sta,Date,Precip,Temp,DewPnt,' \
                          'WindSpd,WindDir,AtmPress,SkyCover\n'
                dataout.write(headers)

                dates = []
                rains = []
                temps = []
                dewpt = []
                windspd = []
                winddir = []
                press = []
                cover = []

                errorfile = open(self.errorfile, 'a')
                for line in datain:
                    if src.lower() == 'asos':
                        metarstring = line
                        dates.append(_date_ASOS(metarstring))
                    elif src.lower() == 'wunderground':
                        row = line.split(',')
                        if len(row) > 2:
                            metarstring = row[-3]
                            datestring = row[-1].split('<')[0]
                            dates.append(_parse_date(datestring))
                        else:
                            metarstring = None

                    if metarstring is not None:
                        obs = metar.Metar(metarstring, errorfile=errorfile)
                        rains = _append_val(obs.precip_1hr, rains, fillNone=0.0)
                        temps = _append_val(obs.temp, temps)
                        dewpt = _append_val(obs.dewpt, dewpt)
                        windspd = _append_val(obs.wind_speed, windspd)
                        winddir = _append_val(obs.wind_dir, winddir)
                        press = _append_val(obs.press, press)
                        cover.append(_process_sky_cover(obs))

                errorfile.close()
                rains = np.array(rains)
                dates = np.array(dates)

                if src == 'asos':
                    final_precip = _process_precip(dates, rains)
                else:
                    final_precip = rains

                for row in zip([self.sta_id]*rains.shape[0], dates, final_precip,
                               temps, dewpt, windspd, winddir, press, cover):
                    dataout.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % row)

            else:
                headers = 'Time,TemperatureC,DewpointC,PressurehPa,WindDirection,' \
                           'WindDirectionDegrees,WindSpeedKMH,WindSpeedGustKMH,' \
                           'Humidity,HourlyPrecipMM,Conditions,Clouds,dailyrainMM,' \
                           'SolarRadiationWatts/m^2,SoftwareType,DateUTC\n'

                #dataout.write(headers)
                dataout.write(datain.read())

            datain.close()
            dataout.close()
        flatstatus = _check_file(flatfilename)
        return flatfilename, flatstatus

    def _read_csv(self, timestamp, src):
        '''
        tries to retrieve data from the web from *src* for a *timestamp*
        returns a pandas dataframe if the download and prcoessing are
        successful. returns None if they fail.

        input:
            *timestamp* : a pandas timestamp object
            *src* : 'asos' or 'wunderground'
        '''
        if src in ['asos', 'wunderground']:
            icol = 1
        elif src == 'wunder_nonairport':
            icol = 0
        flatfilename = self._make_data_file(timestamp, src, 'flat')
        if not os.path.exists(flatfilename):
            flatfilename, flatstatus = self._process_file(timestamp, src)

        flatstatus = _check_file(flatfilename)
        if flatstatus == 'ok':
            data = pandas.read_csv(flatfilename, index_col=False, parse_dates=[icol])
            data.set_index(data.columns[icol], inplace=True)

        else:
            data = None

        return data

    def _get_data(self, startdate, enddate, source, filename):
        '''
        This function will return data in the form of a pandas dataframe
        for the station between *startdate* and *enddate*.

        Input:
            *startdate* : string representing the earliest date for the data
            *enddate* : string representing the latest data for the data
            *source* : string indicating where the data will come from
                can in "asos" or "wunderground"

        Returns:
            *data* : a pandas data frame of the data for this station
        '''
        _check_src(source)

        freq = {
            'asos': 'MS',
            'wunderground': 'D',
            'wunder_nonairport': 'D'
        }

        try:
            timestamps = pandas.DatetimeIndex(start=startdate, end=enddate,
                                              freq=freq[source])
        except KeyError:
            raise ValueError('source must be either "ASOS" or "wunderground"')

        data = None
        for ts in timestamps:
            if data is None:
                data = self._read_csv(ts, source)
            else:
                data = data.append(self._read_csv(ts, source))

        # add a row number to each row
        data['rownum'] = range(data.shape[0])

        # corrected data are appended to the bottom of the ASOS files by NCDC
        # QA people. So for any given date/time index, we want the *last* row
        # that appeared in the data file.
        grouped_data = data.groupby(level=0, by=['rownum'])
        final_data = grouped_data.last().drop(['rownum'], axis=1)

        if filename is not None:
            compdir = self._find_dir(source, 'compile')
            _check_dirs(compdir.split(os.path.sep))
            final_data.to_csv(os.path.join(compdir, filename))

        return final_data

    def getASOSData(self, startdate, enddate, filename=None):
        '''
        This function will return ASOS data in the form of a pandas dataframe
        for the station between *startdate* and *enddate*.

        Input:
            *startdate* : string representing the earliest date for the data
            *enddate* : string representing the latest data for the data

        Returns:
            *data* : a pandas data frame of the ASOS data for this station

        Example:
        >>> import metar.Station as Station
        >>> startdate = '2012-1-1'
        >>> enddate = 'September 30, 2012'
        >>> pdx = Station.getStationByID('KPDX')
        >>> data = pdx.getASOSdata(startdate, enddate)
        '''
        self.data['asos'] = self._get_data(startdate, enddate, 'asos', filename)

    def getWundergroundData(self, startdate, enddate, filename=None):
        '''
        This function will return Wunderground data in the form of a pandas dataframe
        for the station between *startdate* and *enddate*.

        Input:
            *startdate* : string representing the earliest date for the data
            *enddate* : string representing the latest data for the data

        Returns:
            *data* : a pandas data frame of the Wunderground data for this station

        Example:
        >>> import metar.Station as Station
        >>> startdate = '2012-1-1'
        >>> enddate = 'September 30, 2012'
        >>> pdx = Station.getStationByID('KPDX')
        >>> data = pdx.getWundergroundData(startdate, enddate)
        '''
        self.data['wunder'] = self._get_data(startdate, enddate, 'wunderground', filename)

    def getWunderground_NonAirportData(self, startdate, enddate, filename=None):
        '''
        This function will return non-airport Wunderground data in the form of a pandas dataframe
        for the station between *startdate* and *enddate*.

        Input:
            *startdate* : string representing the earliest date for the data
            *enddate* : string representing the latest data for the data

        Returns:
            *data* : a pandas data frame of the Wunderground data for this station

        Example:
        >>> import metar.Station as Station
        >>> startdate = '2012-1-1'
        >>> enddate = 'September 30, 2012'
        >>> pdx = Station.getStationByID('KPDX')
        >>> data = pdx.getWunderground_NonAirportData(startdate, enddate)
        '''
        self.data['wunder_nonairport'] = self._get_data(startdate, enddate, 'wunder_nonairport', filename)

    def _get_compiled_files(self, source):
        compdir = self._find_dir(source, 'compile')
        _check_dirs(compdir.split(os.path.sep))
        compfiles = os.listdir(compdir)
        return compdir, compfiles

    def showCompiledFiles(self, source):
        compdir, compfiles = self._get_compiled_files(source)
        if len(compfiles) == 0:
            print('No compiled files')

        for n, cf in enumerate(compfiles):
            cfile = open(os.path.join(compdir, cf), 'r')
            cdata = cfile.readlines()
            start = cdata[1].split(',')[0]
            end = cdata[-1].split(',')[0]
            cfile.close()
            print('%d) %s - start: %s\tend: %s' % (n+1, cf, start, end))

    def loadCompiledFile(self, source, filename=None, filenum=None):
        if filename is None and filenum is None:
            raise ValueError("must specify either a file name or number")

        compdir, compfiles = self._get_compiled_files(source)
        N = len(compfiles)
        if N > 0:
            if filenum is not None:
                if 0 < filenum <= N:
                    filename = compfiles[filenum-1]
                else:
                    raise ValueError('file number must be between 1 and %d' % N)
            elif filename not in compfiles:
                raise ValueError('filename does not exist')

            cfilepath = os.path.join(compdir, filename)
            data = pandas.read_csv(cfilepath, index_col=0, parse_dates=True)

        else:
            print('No files to load')
            data = None

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
    if src.lower() not in ('wunderground', 'asos', 'wunder_nonairport'):
        raise ValueError('src must be one of "wunderground" or "asos"')


def _check_step(step):
    '''
    checks that a *step* value is valid
    '''
    if step.lower() not in ('raw', 'flat', 'compile'):
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
        topdir = [os.path.join(subdirs[0], subdirs[1])]
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

    date = datetime.datetime(yr, mo, da, hr, mi)

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
        for n in range(1, len(date)):
            if precip[n] < precip[n-1]:
                minuteIndex = date[n].minute/5
                minutes[minuteIndex] += 1

        resetTime, = np.where(minutes == minutes.max())
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
            p2[n] = p1[n]

        #elif tdelta.seconds/60 == 5 and dateval[n].minute != RT:
        else:
            p2[n] = (float(p1[n]) - float(p1[n-1]))

    return p2


def _process_sky_cover(obs):
    coverdict = {'CLR': 0.0000,
                 'SKC': 0.0000,
                 'NSC': 0.0000,
                 'NCD': 0.0000,
                 'FEW': 0.1785,
                 'SCT': 0.4375,
                 'BKN': 0.7500,
                 'VV': 0.9900,
                 'OVC': 1.0000}
    coverlist = []
    for sky in obs.sky:
        coverval = coverdict[sky[0]]
        coverlist.append(coverval)

    if len(coverlist) > 0:
        cover = np.max(coverlist)
    else:
        cover = 'NA'

    return cover


def getAllStations():
    station_file_name = "reference/nsd_cccc.txt"
    #station_file_url = "http://www.noaa.gov/nsd_cccc.txt"
    stations = {}

    fh = open(station_file_name, 'r')
    for line in fh:
        f = line.strip().split(";")
        stations[f[0]] = (f[0], f[3], f[4], f[5], f[7], f[8])

    fh.close()

    return stations


def getStationByID(sta_id):
    stations = getAllStations()
    try:
        info = stations[sta_id]
        sta = WeatherStation(sta_id, city=info[1], state=info[2],
                             country=info[3], lat=info[4], lon=info[5])
    except KeyError:
        sta = WeatherStation(sta_id)

    return sta


def getASOSData(station, startdate, enddate, filename=None):
    if not isinstance(station, WeatherStation):
        station = getStationByID(station)

    data = station.getASOSData(startdate, enddate, filename=filename)
    return data


def getWundergroundData(station, startdate, enddate, filename=None):
    if not isinstance(station, WeatherStation):
        station = getStationByID(station)

    data = station.getWundergroundData(startdate, enddate, filename=filename)
    return data


def getWunderground_NonAirportData(station, startdate, enddate, filename=None):
    if not isinstance(station, WeatherStation):
        station = getStationByID(station)

    data = station.getWunderground_NonAirportData(startdate, enddate, filename=filename)
    return data

