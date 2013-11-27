import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as dates
import pandas

from .graphics import _resampler

states = {
    'Alabama': 1,
    'New Jersey': 28,
    'Arizona': 2,
    'New Mexico': 29,
    'Arkansas': 3,
    'New York': 30,
    'California': 4,
    'North Carolina': 31,
    'Colorado': 5,
    'North Dakota': 32,
    'Connecticut': 6,
    'Ohio': 33,
    'Delaware': 7,
    'Oklahoma': 34,
    'Florida': 8,
    'Oregon': 35,
    'Georgia': 9,
    'Pennsylvania': 36,
    'Idaho': 10,
    'Rhode Island': 37,
    'Illinois': 11,
    'South Carolina': 38,
    'Indiana': 12,
    'South Dakota': 39,
    'Iowa': 13,
    'Tennessee': 40,
    'Kansas': 14,
    'Texas': 41,
    'Kentucky': 15,
    'Utah': 42,
    'Louisiana': 16,
    'Vermont': 43,
    'Maine': 17,
    'Virginia': 44,
    'Maryland': 18,
    'Washington': 45,
    'Massachusetts': 19,
    'West Virginia': 46,
    'Michigan': 20,
    'Wisconsin': 47,
    'Minnesota': 21,
    'Wyoming': 48,
    'Mississippi': 22,
    'Not Used': 49,
    'Missouri': 23,
    'Alaska': 50,
    'Montana': 24,
    'Hawaii': 51,
    'Nebraska': 25,
    'Puerto Rico': 66,
    'Nevada': 26,
    'Virgin Islands': 67,
    'New Hampshire': 27,
    'Pacific Islands': 91
}

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

    # export and return the data
    data.to_csv(filename, index=False, sep=sep)
    return data

def NCDCFormat(dataframe, coopid, statename, col='Precip', filename=None):
    '''
    Always resamples to hourly
    '''
    # constants
    RECORDTYPE = 'HPD'
    ELEMENT = 'HPCP'
    UNITS = 'HI'
    STATECODE = states[statename]

    data, rule, plotkind = _resampler(dataframe, col, freq='hourly', how='sum')
    data.index.names = ['Datetime']
    data.name = col
    data = pandas.DataFrame(data)
    data = pandas.DataFrame(data[data.Precip > 0])
    data['Date'] = data.index.date
    data['Hour'] = data.index.hour
    data['Hour'] += 1
    data = data.reset_index().set_index(['Date', 'Hour'])[[col]]
    data = data.unstack(level='Hour')[col]

    def makeNCDCRow(row, flag=None):
        if flag is None:
            flag = " "
        newrow = row.dropna() * 100
        newrow = newrow.astype(int)
        newrow = newrow.append(pandas.Series(newrow.sum(), index=[25]))

        precipstrings = ' '.join([
            '{0:02d}00{1:06d}{2}'.format(hour, int(val), flag) \
            for hour, val in zip(newrow.index, newrow)
        ])

        ncdcstring = '{0}{1:02d}{2}{3}{4}{5}{6:02d}{7:04d}{8:03d}{9} \n'.format(
            RECORDTYPE, STATECODE, coopid,
            ELEMENT, UNITS, row.name.year,
            row.name.month, row.name.day, row.count(),
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