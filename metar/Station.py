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
import datetime 
import urllib2 
import cookielib
import Datatypes
import matplotlib
import matplotlib.dates as mdates
import Metar
import numpy as np
matplotlib.rcParams['timezone'] = 'UTC'


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

        self.urlopener = self.__setCookies()

    def __setCookies(self):
        jar = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(jar)
        opener = urllib2.build_opener(handler)
        url1 = 'http://www.wunderground.com/history/airport/%s/2011/12/4/DailyHistory.html?' % self.sta_id
        url2 = 'http://www.wunderground.com/cgi-bin/findweather/getForecast?setpref=SHOWMETAR&value=1'
        url3 = 'http://www.wunderground.com/history/airport/%s/2011/12/4/DailyHistory.html?&&theprefset=SHOWMETAR&theprefvalue=1&format=1' % self.sta_id

        opener.open(url1)
        opener.open(url2)
        opener.open(url3)
        return opener

    def urlByDate(self, date):
        "http://www.wunderground.com/history/airport/KDCA/1950/12/18/DailyHistory.html?format=1"
        baseurl = 'http://www.wunderground.com/history/airport/%s' % self.sta_id
        endurl =  'DailyHistory.html?&&theprefset=SHOWMETAR&theprefvalue=1&format=1'
        datestring = date.strftime('%Y/%m/%d')
        url = '%s/%s/%s' % (baseurl, datestring, endurl)
        return url

    def getHourlyData(self, url, outfile, errorfile, keepheader=False):
        observations = []
        if keepheader:
            start = 1
        else:
            start = 2

        try:
            webdata = self.urlopener.open(url)
            rawlines = webdata.readlines()
            outfile.writelines(rawlines[start:])
        except:
            errorfile.write('error on: %s\n' % (url,))



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
            obs = Metar.Metar(metarstring, month=date.month, year=date.year,
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
