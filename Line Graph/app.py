import numpy as np
import pandas as pd
import os
import numbers
from BuildingEnergyAPI.building_data_requests_internal import get_value
from pylive.pylive import live_plotter_xy

# Open dataframe
df = pd.read_csv(os.path.join('csv', 'ahs_power.csv'))

main_row = df[df['Label'] == 'Main (kW)']


def get_reading():
    value, units = get_value(main_row['Facility'], main_row['Meter'], live=True)
    value = float(value) if isinstance(value, numbers.Number) else ''
    units = units if units else ''

    return value


# The most points to be shown on the screen at one time
max_points = 20

# How many seconds between updates
update_interval = 5

x_vec = np.ndarray(shape=(1,), buffer=np.array([0]))
y_vec = np.ndarray(shape=(1,), buffer=np.array([0]))

# Supply first value
y_vec = np.append(y_vec[1:], get_reading())

line1 = []
while True:
    line1 = live_plotter_xy(x_vec, y_vec, line1, pause_time=update_interval, title="AHS Main",
                            xlabel='Elapsed Time (Seconds)', ylabel='Power (kW)')

    reading = get_reading()

    if x_vec.size < max_points:
        x_vec = np.append(x_vec, [x_vec[-1] + update_interval])
    else:
        x_vec = np.append(x_vec[1:], [x_vec[-1] + update_interval])

    if y_vec.size < max_points:
        y_vec = np.append(y_vec, [reading])
    else:
        y_vec = np.append(y_vec[1:], [reading])
