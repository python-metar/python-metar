#!/usr/bin/python
#
#  Python module to provide station information from the ICAO identifiers
#
#  Copyright 2004  Tom Pollard
# 
#!/usr/bin/python
#
#  Python module to provide station information from the ICAO identifiers
#
#  Copyright 2004  Tom Pollard
# 
import datetime, urllib, urllib2, cookielib, os, pdb
from Metar import Metar
from Datatypes import position, distance, direction
import numpy as np
import matplotlib
import matplotlib.dates as mdates
matplotlib.rcParams['timezone'] = 'UTC'


class station:
    """An object representing a weather station."""

    def __init__(self, sta_id, city=None, state=None,
                country=None, latitude=None, longitude=None):
        self.sta_id = sta_id
        self.city = city
        self.state = state
        self.country = country
        self.position = position(latitude,longitude)
        if self.state:
            self.name = "%s, %s" % (self.city, self.state)
        else:
            self.name = self.city

        self.wundergound = self._set_cookies(src='wunderground')
        self.asos = self._set_cookies(src='asos')

    def _find_dir(self, src, step):
        _check_src(src)
        _check_step(step)
        return os.path.join('data', self.sta_id, src.lower(), step.lower())

    def _find_file(self, date, src, step):
        _check_src(src)
        _check_step(step)

        if step == 'raw':
            ext = 'dat'
        else:
            ext = 'csv'

        if src.lower() == 'wunderground':
            datefmtstr = '%Y%m%d'
        else:
            datefmtstr = '%Y%m'

        return '%s_%s.%s' % (self.sta_id, date.strftime('%Y%m%d'), ext)

    def _set_cookies(self, src):
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

    def _url_by_date(self, date, src='wunderground'):
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

    def _make_data_file(self, date, src, step):
        _check_src(src)
        _check_step(step)
        datadir = self._find_dir(src, step)
        datafile = self._find_file(date, src, step)
        subdirs = datadir.split(os.path.sep)
        _check_dirs(subdirs)
        return os.path.join(datadir, datafile)

    def getData(self, date, errorfile=None, keepheader=False, src='wunderground'):
        observations = []
        if keepheader:
            start = 0
        else:
            start = 1

        outname = self._make_data_file(date, src, 'raw')
        if not os.path.exists(outname):
            outfile = open(outname, 'w')
            url = self._url_by_date(date, src=src)
            if src.lower() == 'wunderground':
                try:
                    webdata = self.wunderground.open(url)
                    rawlines = webdata.readlines()
                    outfile.writelines(rawlines[start:])
                except:
                    print('error on: %s\n' % (url,))
                    if errorfile is not None:
                        errorfile.write('error on: %s\n' % (url,))
            elif src.lower() == 'asos':
                try:
                    webdata = self.asos.open(url)
                    rawlines = webdata.readlines()
                    outfile.writelines(rawlines[start:])
                except:
                    print('error on: %s\n' % (url,))
                    if errorfile is not None:
                        errorfile.write('error on: %s\n' % (url,))
            outfile.close()

    def processASOSFile(self, date, errorfile):
        datain = open(self._make_data_file(date, 'asos', 'raw'), 'r')
        dataout = open(self._make_data_file(date, 'asos', 'flat'), 'w')

        headers = 'Sta,Date,Precip1hr_cum(in),Precip5min(in),Temp(degF),' + \
                    'DewPnt(defF),WindSpd(mph),WindDir(deg),AtmPress(hPa)\n'
        dataout.write(headers)

        dates = []
        rains = []
        temps = []
        dewpt = []
        windspd = []
        winddir = []
        press = []
        for metarstring in datain:
            obs = Metar(metarstring, errorfile=errorfile)
            dates.append(dateASOS(metarstring))
            rains = appendVal(obs.precip_1hr, rains, fillNone=0.0)
            temps = appendVal(obs.temp, temps)
            dewpt = appendVal(obs.dewpt, dewpt)
            windspd = appendVal(obs.wind_speed, windspd)
            winddir = appendVal(obs.wind_dir, winddir)
            press = appendVal(obs.press, press)

        rains = np.array(rains)
        dates = np.array(dates)

        rt = determineResetTime(dates, rains)
        final_precip = processPrecip(dates, rains)

        for row in zip([self.sta_id]*rains.shape[0], dates, rains, final_precip, \
                        temps, dewpt, windspd, winddir, press):
            dataout.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % row)

        datain.close()
        dataout.close()

def _check_src(src):
    if src.lower() not in ('wunderground','asos'):
        raise ValueError('src must be one of "wunderground", or "asos"')

def _check_step(step):
    if step.lower() not in ('raw','flat','final'):
        raise ValueError('step must be one of "raw", "flat", or "final"')

def _check_dirs(subdirs):
    if not os.path.exists(subdirs[0]):
        print('making '+subdirs[0])
        os.mkdir(subdirs[0])

    if len(subdirs) > 1:
        topdir = [os.path.join(subdirs[0],subdirs[1])]
        for sd in subdirs[2:]:
            topdir.append(sd)
        _check_dirs(topdir)

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

def rainASOS(x):
    '''get 5-min precip value (cumulative w/i the hour)'''
    p = 0
    m = re.search('[ +]P\d\d\d\d\s', x)
    if m:
        p = int(m.group(0)[2:-1])

    return p

def dateASOS(x):
    '''get date/time of asos reading'''
    yr = int(x[13:17])   # year
    mo = int(x[17:19])   # month
    da = int(x[19:21])   # day
    hr = int(x[37:39])   # hour
    mi = int(x[40:42])   # minute

    date = datetime.datetime(yr,mo,da,hr,mi)

    return date

def getStationByID(sta_id):
    stations = getAllStations()
    return stations[sta_id]

def appendVal(obsval, listobj, fillNone='NA'):
    if obsval is not None and hasattr(obsval, 'value'):
        listobj.append(obsval.value())
    else:
        listobj.append(fillNone)
    return listobj

def determineResetTime(date, precip):
    minutes = np.zeros(12)
    if len(date) <> len(precip):
        raise ValueError("date and precip must be same length")
    else:
        for n in range(1,len(date)):
            if precip[n] < precip[n-1]:
                minuteIndex = date[n].minute/5
                minutes[minuteIndex] += 1

        resetTime, = np.where(minutes==minutes.max())
        return resetTime[0]*5

def processPrecip(dateval, p1):
    '''convert 5-min rainfall data from cumuative w/i an hour to 5-min totals
    p = precip data (list)
    dt = list of datetime objects
    RT = point in the hour when the tip counter resets
    #if (p1[n-1] <= p1[n]) and (dt[n].minute != RT):'''
    RT = determineResetTime(dateval, p1)
    p2 = np.zeros(len(p1))
    p2[0] = p1[0]
    for n in range(1, len(p1)):

        tdelta = dateval[n] - dateval[n-1]
        if p1[n] < p1[n-1] or dateval[n].minute == RT or tdelta.seconds/60 != 5:
            p2[n] = p1[n]/100.

        #elif tdelta.seconds/60 == 5 and dateval[n].minute != RT:
        else:
            p2[n] = (float(p1[n]) - float(p1[n-1]))/100.

    return p2

def processWundergroundFile(csvin, csvout, errorfile):
    coverdict = {'CLR' : 0,
                 'SKC' : 0,
                 'OVC' : 1,
                 'BKN' : 0.75,
                 'SCT' : 0.4375,
                 'FEW' : 0.1875,
                 'VV'  : 0.99}

    headers =['TimeEST',
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
            obs = Metar(metarstring, month=date.month, year=date.year,
                        errorfile=errorfile)

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

