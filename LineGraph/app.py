import numpy as np
import pandas as pd
import os
import time
import numbers
import datetime as dt
import math
from BuildingEnergyAPI.building_data_requests_external import get_value
from pylive.pylive import live_plotter_init, live_plotter_xy
from LineGraph.update_thread import DataUpdateThread

# Open dataframe
csv_path = os.path.join('csv', 'ahs_power.csv')
df = pd.read_csv(csv_path)


def get_readings():
    values = []

    for row_num in range(num_lines):
        value, units = get_value(df.loc[row_num]['Facility'], df.loc[row_num]['Meter'], live=True)
        value = float(value) if isinstance(value, numbers.Number) else ''
        values.append(value)

    return values


# Pull Labels
labels = [row['Label'] for index, row in df.iterrows()]
columns = labels + ['Time']

# The most points to be shown on the screen at one time
max_points = 20

# How many seconds between updates
update_interval = 5

# How many lines to use (number of rows in df)
num_lines = len(df.index)

# Setup data storing dataframe
initial_values = get_readings()
initial_values.append(dt.datetime.now())
data_df = pd.DataFrame([initial_values], columns=columns)
data_df['Time'] = pd.to_datetime(data_df['Time'])  # Index by datetime

update_thread = DataUpdateThread(data_df, csv_path, None)
update_thread.begin_update_thread(10)

try:
    lines = [None for line_num in range(num_lines)]

    color_options = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    # Cycle through every color in the order shown in color_options
    formats = ['{0}-o'.format(color_options[format_num % len(color_options)]) for format_num in range(num_lines)]

    live_plotter_init(data_df, lines, formats, [item.replace('(kW)', '') for item in labels],
                      title="AHS Power Usage (Realtime)", xlabel='Elapsed Time (Seconds)',
                      ylabel='Power (kW)')

    # while True:
    #     live_plotter_xy(x_vec, y_vec, lines, coordinate_index, pause_time=update_interval)
    #
    #     values = get_readings()
    #
    #     for x_arr in x_vec:
    #         x_arr[coordinate_index] = x_arr[coordinate_index - 1] + update_interval
    #
    #     for index in range(num_lines):
    #         y_vec[index][coordinate_index] = values[index]
    #
    #     coordinate_index = coordinate_index + 1
    #
    #     if coordinate_index == num_lines:
    #         coordinate_index = 0

except KeyboardInterrupt:
    print("Shutting down, please wait...")
    update_thread.stop()
    while not update_thread.is_fully_stopped():
        time.sleep(0.5)
    print("Fully shut down")
