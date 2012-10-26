import numpy as np
import matplotlib.pyplot as plt

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