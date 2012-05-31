import metar
import matplotlib.dates as mdates
import datetime as dt

stations = [('KDLS', 'The Dalles', 'OR'),
            ('KHRI', 'Hermiston', 'OR'),
            ('KPSC', 'Pasco', 'WA')]

startdate = dt.datetime(1980,1,1)
enddate = dt.datetime(2012,5,27)
timestep = dt.timedelta(days=1)
for station in stations:
    outfilename = '%s_raw.csv' % (station[0],)
    procfilename = '%s_processed.csv' % (station[0],)
    errfillename = '%s_errors.log' % (station[0],)
    outfile = open(outfilename, 'w')
    errorfile = open(errfillename, 'a')
    sta = metar.Station.station(station[0], city=station[1], state=station[2])

    for n, date in enumerate(mdates.drange(startdate, enddate, timestep)):
        dateobj = mdates.num2date(date)
        url = sta.urlByDate(dateobj)
        if n%100 == 0:
            print('%s - %s' % (station[0], dateobj))

        if n == 0:
            sta.getHourlyData(url, outfile, errorfile, keepheader=True)
        else:
            sta.getHourlyData(url, outfile, errorfile, keepheader=False)

    outfile.close()

    metar.Station.processWundergroundFile(outfilename, procfilename, errorfile)
    errorfile.close()

