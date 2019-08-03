import os
import sys
import time
import atexit
import numbers
import pandas as pd
import datetime as dt
from LineGraph.update_thread import DataUpdateThread
from BuildingEnergyAPI.building_data_requests_external import get_value
from pylive.pylive import live_plotter_init, live_plotter_update, has_been_closed

# Open dataframe
csv_path = os.path.join('csv', 'ahs_power.csv')
output_path = os.path.join('LineGraph', 'line_graph_out.csv')
df = pd.read_csv(csv_path)


def get_readings():
    values = []

    for row_num in range(num_lines):
        value, units = get_value(df.loc[row_num]['Facility'], df.loc[row_num]['Meter'], live=True)
        value = float(value) if isinstance(value, numbers.Number) else ''
        values.append(round(value, 2))

    return values


# Pull Labels
labels = [row['Label'] for index, row in df.iterrows()]
columns = labels + ['Time']

# How many seconds between updates
update_interval = 2

# How many lines to use (number of rows in df)
num_lines = len(df.index)

# Setup data storing dataframe
initial_values = get_readings()
initial_values.append(dt.datetime.now())
data_df = pd.DataFrame([initial_values], columns=columns)
data_df['Time'] = pd.to_datetime(data_df['Time'])  # Index by datetime

update_thread = DataUpdateThread(data_df, csv_path, output_path)
update_thread.begin_update_thread(update_interval)


def proper_shutdown():
    print("Shutting down, please wait...")
    update_thread.stop()
    while not update_thread.is_fully_stopped():
        time.sleep(0.5)
    print("Fully shut down")
    sys.exit()


try:
    # Properly shutdown when sys.exit() is called
    atexit.register(proper_shutdown)

    lines = [None for line_num in range(num_lines)]

    color_options = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    # Cycle through every color in the order shown in color_options
    formats = ['{0}-o'.format(color_options[format_num % len(color_options)]) for format_num in range(num_lines)]

    live_plotter_init(data_df, lines, formats, [item.replace('(kW)', '') for item in labels],
                      title="AHS Power Usage (Realtime)", xlabel='Elapsed Time (Hours:Minutes:Seconds)',
                      ylabel='Power (kW)')

    while True:
        live_plotter_update(data_df, lines)
        if has_been_closed():
            sys.exit()

except KeyboardInterrupt:
    proper_shutdown()
