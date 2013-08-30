import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as dates

__all__ = ['hyetograph', 'rainClock', 'windRose', 'psychromograph',
           'temperaturePlot']


def _plotter(dataframe, col, ylabel, freq='hourly', how='sum',
             ax=None, downward=False, fname=None, fillna=None):

    if not hasattr(dataframe, col):
        raise ValueError('input `dataframe` must have a `%s` column' % col)

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    rules = {
        '5min': ('5Min', 'line'),
        '5 min': ('5Min', 'line'),
        '5-min': ('5Min', 'line'),
        '5 minute': ('5Min', 'line'),
        '5-minute': ('5Min', 'line'),
        '15min': ('15Min', 'line'),
        '15 min': ('15Min', 'line'),
        '15-min': ('15Min', 'line'),
        '15 minute': ('15Min', 'line'),
        '15-minute': ('15Min', 'line'),
        'hour': ('H', 'line'),
        'hourly': ('H', 'line'),
        'day': ('D', 'line'),
        'daily': ('D', 'line'),
        'week': ('W', 'line'),
        'weekly': ('W', 'line'),
        'month': ('M', 'line'),
        'monthly': ('M', 'line')
    }

    if freq.lower() in rules.keys():
        rule = rules[freq.lower()][0]
        kind = rules[freq.lower()][1]
        data = dataframe[col].resample(how=how, rule=rule)
        if fillna is not None:
            data.fillna(value=fillna, inplace=True)

        data.plot(ax=ax, kind=kind)
        if rule == 'A':
            xformat = dates.DateFormatter('%Y')
            ax.xaxis.set_major_formatter(xformat)
        elif rule == 'M':
            xformat = dates.DateFormatter('%Y-%m')
            ax.xaxis.set_major_formatter(xformat)

    else:
        m = "freq should be in ['5-min', 'hourly', 'daily', 'weekly, 'monthly']"
        raise ValueError(m)

    ax.tick_params(axis='x', labelsize=8)
    ax.set_xlabel('Date')
    ax.set_ylabel(ylabel)
    if downward:
        ax.invert_yaxis()

    if fname is not None:
        fig.tight_layout()
        fig.savefig(fname, dpi=300, bbox_inches='tight')

    return fig, ax


def hyetograph(dataframe, freq='hourly', ax=None, downward=True, col='Precip', fname=None):
    ylabel = '%s Rainfall Depth (in)' % freq.title()
    fig, ax = _plotter(dataframe, col, ylabel, freq=freq, fillna=0,
                       how='sum', ax=ax, downward=downward, fname=fname)
    return fig, ax


def psychromograph(dataframe, freq='hourly', ax=None, col='AtmPress', fname=None):
    ylabel = '%s Barometric Pressure (in Hg)' % freq.title()
    fig, ax = _plotter(dataframe, col, ylabel, freq=freq,
                       how='mean', ax=ax, fname=fname)
    return fig, ax


def temperaturePlot(dataframe, freq='hourly', ax=None, col='Temp', fname=None):
    ylabel = u'%s Temperature (\xB0C)' % freq.title()
    fig, ax = _plotter(dataframe, col, ylabel, freq=freq,
                       how='mean', ax=ax, fname=fname)
    return fig, ax


def rainClock(dataframe, raincol='Precip', fname=None):
    '''
    Mathematically dubious representation of the likelihood of rain at
    at any hour given that will rain.
    '''
    if not hasattr(dataframe, raincol):
        raise ValueError('input `dataframe` must have a `%s` column' % raincol)

    rainfall = dataframe[raincol]
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
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(7, 3),
                                   subplot_kw=dict(polar=True))
    theta = np.arange(0.0, 2*np.pi, 2*np.pi/12)
    ax1.bar(theta + 2*np.pi/12 * 0.1, rain_by_hour[:12],
            bar_width, color='DodgerBlue', linewidth=0.5)
    ax2.bar(theta + 2*np.pi/12 * 0.1, rain_by_hour[12:],
            bar_width, color='Crimson', linewidth=0.5)
    ax1.set_title('AM Hours')
    ax2.set_title('PM Hours')
    for ax in [ax1, ax2]:
        ax.set_theta_zero_location("N")
        ax.set_theta_direction('clockwise')
        ax.set_xticks(theta)
        ax.set_xticklabels(am_hours)
        ax.set_yticklabels([])

    if fname is not None:
        fig.tight_layout()
        fig.savefig(fname, dpi=300, bbox_inches='tight')

    return fig, (ax1, ax2)


def windRose(dataframe, speedcol='WindSpd', dircol='WindDir', mph=False,
             fname=None):
    '''
    Plots a Wind Rose. Feed it a dataframe with 'WindSpd' (knots) and
    'WindDir' degrees clockwise from north (columns)
    '''

    if not hasattr(dataframe, speedcol):
        raise ValueError('input `dataframe` must have a `%s` column' % speedcol)

    if not hasattr(dataframe, dircol):
        raise ValueError('input `dataframe` must have a `%s` column' % dircol)

    # set up the figure
    fig, ax1 = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax1.xaxis.grid(True, which='major', linestyle='-', alpha='0.125', zorder=0)
    ax1.yaxis.grid(True, which='major', linestyle='-', alpha='0.125', zorder=0)
    ax1.set_theta_zero_location("N")
    ax1.set_theta_direction('clockwise')

    # speed bins and colors
    speedBins = [40, 30, 20, 10, 5]
    colors = ['#990000', '#FF4719', '#FFCC00', '#579443', '#0066FF']

    # number of total and zero-wind observations
    total = np.float(dataframe.shape[0])
    if mph:
        factor =  1.15
        units = 'mph'
    else:
        factor = 1
        units = 'kt'

    calm = np.float(dataframe[dataframe[speedcol] == 0].shape[0])/total * 100

    # loop through the speed bins
    for spd, clr in zip(speedBins, colors):
        barLen = _get_wind_counts(dataframe, spd, speedcol, dircol, factor=factor)
        barLen = barLen/total
        barDir, barWidth = _convert_dir_to_left_radian(np.array(barLen.index))
        ax1.bar(barDir, barLen, width=barWidth, linewidth=0.50,
                edgecolor=(0.25, 0.25, 0.25), color=clr, alpha=0.8,
                label=r"<%d %s" % (spd, units))

    # format the plot's axes
    ax1.legend(loc='lower right', bbox_to_anchor=(1.10, -0.13), fontsize=8)
    ax1.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    ax1.xaxis.grid(True, which='major', color='k', alpha=0.5)
    ax1.yaxis.grid(True, which='major', color='k', alpha=0.5)
    ax1.yaxis.set_major_formatter(FuncFormatter(_pct_fmt))
    fig.text(0.05, 0.95, 'Calm Winds: %0.1f%%' % calm)
    #if calm >= 0.1:
    #    ax1.set_ylim(ymin=np.floor(calm*10)/10.)

    if fname is not None:
        fig.tight_layout()
        fig.savefig(fname, dpi=300, bbox_inches='tight')

    return fig, ax1


def _get_wind_counts(dataframe, maxSpeed, speedcol, dircol, factor=1):
    group = dataframe[dataframe[speedcol]*factor < maxSpeed].groupby(by=dircol)
    counts = group.size()
    return counts[counts.index != 0]


def _pct_fmt(x, pos=0):
    return '%0.1f%%' % (100*x)


def _convert_dir_to_left_radian(directions):
    N = directions.shape[0]
    barDir = directions * np.pi/180. - np.pi/N
    barWidth = [2 * np.pi / N]*N
    return barDir, barWidth
