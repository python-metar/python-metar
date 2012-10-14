import metar
import matplotlib.dates as mdates
import datetime as dt

stations = [('KPDX', 'Portland', 'OR'),
            ('KDLS', 'The Dalles', 'OR'),
            ('KHRI', 'Hermiston', 'OR'),
            ('KPSC', 'Pasco', 'WA')
            ]

startdate = dt.datetime(2007,10,1)
enddate = dt.datetime(2012,10,1)
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
            sta.getData(url, outfile, errorfile, keepheader=True)
        else:
            sta.getData(url, outfile, errorfile, keepheader=False)

    outfile.close()

    metar.Station.processWundergroundFile(outfilename, procfilename, errorfile)
    errorfile.close()

