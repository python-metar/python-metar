import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as dates
import pandas
import datetime

from .graphics import _resampler

states = [
    {'name': 'Alabama', 'code': 1},
    {'name': 'New Jersey', 'code': 28},
    {'name': 'Arizona', 'code': 2},
    {'name': 'New Mexico', 'code': 29},
    {'name': 'Arkansas', 'code': 3},
    {'name': 'New York', 'code': 30},
    {'name': 'California', 'code': 4},
    {'name': 'North Carolina', 'code': 31},
    {'name': 'Colorado', 'code': 5},
    {'name': 'North Dakota', 'code': 32},
    {'name': 'Connecticut', 'code': 6},
    {'name': 'Ohio', 'code': 33},
    {'name': 'Delaware', 'code': 7},
    {'name': 'Oklahoma', 'code': 34},
    {'name': 'Florida', 'code': 8},
    {'name': 'Oregon', 'code': 35},
    {'name': 'Georgia', 'code': 9},
    {'name': 'Pennsylvania', 'code': 36},
    {'name': 'Idaho', 'code': 10},
    {'name': 'Rhode Island', 'code': 37},
    {'name': 'Illinois', 'code': 11},
    {'name': 'South Carolina', 'code': 38},
    {'name': 'Indiana', 'code': 12},
    {'name': 'South Dakota', 'code': 39},
    {'name': 'Iowa', 'code': 13},
    {'name': 'Tennessee', 'code': 40},
    {'name': 'Kansas', 'code': 14},
    {'name': 'Texas', 'code': 41},
    {'name': 'Kentucky', 'code': 15},
    {'name': 'Utah', 'code': 42},
    {'name': 'Louisiana', 'code': 16},
    {'name': 'Vermont', 'code': 43},
    {'name': 'Maine', 'code': 17},
    {'name': 'Virginia', 'code': 44},
    {'name': 'Maryland', 'code': 18},
    {'name': 'Washington', 'code': 45},
    {'name': 'Massachusetts', 'code': 19},
    {'name': 'West Virginia', 'code': 46},
    {'name': 'Michigan', 'code': 20},
    {'name': 'Wisconsin', 'code': 47},
    {'name': 'Minnesota', 'code': 21},
    {'name': 'Wyoming', 'code': 48},
    {'name': 'Mississippi', 'code': 22},
    {'name': 'Not Used', 'code': 49},
    {'name': 'Missouri', 'code': 23},
    {'name': 'Alaska', 'code': 50},
    {'name': 'Montana', 'code': 24},
    {'name': 'Hawaii', 'code': 51},
    {'name': 'Nebraska', 'code': 25},
    {'name': 'Puerto Rico', 'code': 66},
    {'name': 'Nevada', 'code': 26},
    {'name': 'Virgin Islands', 'code': 67},
    {'name': 'New Hampshire', 'code': 27},
    {'name': 'Pacific Islands', 'code': 91}
]


def SWMM5Format(dataframe, stationid, col='Precip', freq='hourly', dropzeros=True,
                filename=None, sep='\t'):
    # resample the `col` column of `dataframe`, returns a series
    data, rule, plotkind = _resampler(dataframe, col, freq=freq, how='sum')

    # set the precip column's name and make the series a dataframe
    data.name = col.lower()
    data = pandas.DataFrame(data)

    # add all of the data/time columns
    data['station'] = stationid
    data['year'] = data.index.year
    data['month'] = data.index.month
    data['day'] = data.index.day
    data['hour'] = data.index.hour
    data['minute'] = data.index.minute

    # drop the zeros if we need to
    if dropzeros:
        data = data[data['precip'] > 0]

    # make a file name if not provided
    if filename is None:
        filename = "{0}_{1}.dat".format(stationid, freq)

    # force the order of columns that we need
    data = data[['station', 'year', 'month', 'day', 'hour', 'minute', 'precip']]
    data.precip = np.round(data.precip, 2)

    # export and return the data
    data.to_csv(filename, index=False, sep=sep)
    return data


def NCDCFormat(dataframe, coopid, statename, col='Precip', filename=None):
    '''
    Always resamples to hourly
    '''
    # constants
    RECORDTYPE = 'HPD'
    ELEMENT = '00HPCP'
    UNITS = 'HI'
    _statecode = filter(lambda x: x['name'] == statename, states)
    STATECODE = [sc for sc in _statecode][0]['code']

    data, rule, plotkind = _resampler(dataframe, col, freq='hourly', how='sum')
    data.index.names = ['Datetime']
    data.name = col
    data = pandas.DataFrame(data)
    data = pandas.DataFrame(data[data[col] > 0])
    data['Date'] = data.index.date
    data['Hour'] = data.index.hour
    data['Hour'] += 1
    data = data.reset_index().set_index(['Date', 'Hour'])[[col]]
    data = data.unstack(level='Hour')[col]

    def makeNCDCRow(row, flags=None):
        newrow = row.dropna() * 100
        newrow = newrow.astype(int)
        newrow = newrow.append(pandas.Series(newrow.sum(), index=[25]))

        if flags is None:
            flags = [" "] * len(newrow)

        precipstrings = ' '.join([
            '{0:02d}00 {1:05d}{2}'.format(hour, int(val), flag) \
            for hour, val, flag in zip(newrow.index, newrow, flags)
        ])

        ncdcstring = '{0}{1:02d}{2}{3}{4}{5}{6:02d}{7:04d}{8:03d}{9} \n'.format(
            RECORDTYPE, STATECODE, coopid,
            ELEMENT, UNITS, row.name.year,
            row.name.month, row.name.day, row.count() + 1,
            precipstrings
        )
        return ncdcstring

    data['ncdcstring'] = data.apply(makeNCDCRow, axis=1)

    if filename is not None:
        with open(filename, 'w') as output:
            output.writelines(data['ncdcstring'].values)

    return data


def hourXtab(dataframe, col, filename=None, flag=None):
    '''
    Always resamples to hourly
    '''
    # constants
    data, rule, plotkind = _resampler(dataframe, col, freq='hourly', how='sum')
    data.index.names = ['Datetime']
    data.name = col
    data = pandas.DataFrame(data)
    #data = pandas.DataFrame(data[data.Precip > 0])
    data['Year'] = data.index.year
    data['Month'] = data.index.month
    data['Day'] = data.index.day
    data['Hour'] = data.index.hour
    data['Hour'] += 1
    data = data.reset_index().set_index(['Year', 'Month', 'Day', 'Hour'])[[col]]
    data = data.unstack(level='Hour')[col]
    data[25] = data.sum(axis=1)
    if filename is not None:
        data.to_csv(filename)
    return data


def NCDCtoCSV(ncdc, csv):
    """Convert NCDC format files to csv

    Parameters
    ----------
    ncdc : filepath to raw NCDC format
    csv : filepath to output CSV file

    """

    csvrows = []
    with open("input/45114_LAX.NCD", 'r') as fin:
        for row in fin:
            csvrows.extend(_obs_from_row(row))

    with open("output/045114_LAX.csv", 'w') as fout:
        fout.writelines(csvrows)


def _pop_many(mylist, N, side='left'):
    index_map = {
        'left': 0,
        'right': -1
    }
    index = index_map[side.lower()]
    popped = ''.join([mylist.pop(index) for _ in range(N)])
    if index == -1:
        popped = popped[::-1]
    return popped


def _parse_obs(obs, units='HI'):
    conversions = {
        'HI': 0.01,
    }
    hour = int(_pop_many(obs, 2)) - 1
    minute = int(_pop_many(obs, 2))
    precip = int(_pop_many(obs, 6))
    if precip == 99999:
        precip = None
    else:
        precip *= conversions[units]
    flag = ''.join(obs)
    return hour, minute, precip, flag


def _write_obs(rowheader, year, month, day, obs):
    hour, minute, precip, flag = obs
    if hour < 24 and precip is not None:
        date = datetime.datetime(year, month, day, hour, minute)
        rowstring = ','.join([
            rowheader,
            date.strftime('%Y-%m-%d %H:%M'),
            '{:.2f}'.format(precip),
            flag
        ])
        return rowstring + '\n'

def _obs_from_row(row):
    values = row.strip().split()
    header = list(values.pop(0))
    recordtype = _pop_many(header, 3)
    state_coopid = _pop_many(header, 6)
    element = _pop_many(header, 6)
    units = _pop_many(header, 2)
    year = int(_pop_many(header, 4))
    month = int(_pop_many(header, 2))
    day = int(_pop_many(header, 4))

    _count = int(_pop_many(header, 3))

    observations = [''.join(header)]
    observations.extend(values)
    parsedObs = [_parse_obs(list(obs), units=units) for obs in observations]

    rowheader = ','.join([
        state_coopid, recordtype, element, units
    ])

    rows = [_write_obs(rowheader, year, month, day, obs) for obs in parsedObs]

    return [r for r in filter(lambda r: r is not None, rows)]



