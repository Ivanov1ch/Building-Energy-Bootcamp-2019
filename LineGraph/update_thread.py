import threading
import numbers
import time
import os
import sys
import pandas as pd
import datetime as dt
from pylive.pylive import has_been_closed
from BuildingEnergyAPI.building_data_requests_internal import get_value


class DataUpdateThread:
    def __init__(self, df, csv_path, output_path):
        self.data_df = df
        self.csv_path = csv_path
        self.output_path = output_path
        self.thread = None
        self.stopped = False
        self.fully_stopped = False

    def get_new_values(self):
        df = pd.read_csv(self.csv_path)

        retrieved_data = []

        for index, row in df.iterrows():
            value, units = get_value(row['Facility'], row['Meter'], live=True)

            value = float(value) if isinstance(value, numbers.Number) else ''
            retrieved_data.append(value)

            if self.stopped or has_been_closed():
                return

        retrieved_data.append(dt.datetime.now())

        # Add to the end of the DF
        self.data_df.loc[len(self.data_df)] = retrieved_data

    def continuous_update(self, repeat_interval):
        while True:
            if self.stopped or has_been_closed():
                break
            self.get_new_values()
            if self.stopped or has_been_closed():
                break
            time.sleep(repeat_interval)

        self.save_data()
        self.fully_stopped = True
        sys.exit()

    def begin_update_thread(self, repeat_interval):
        self.thread = threading.Thread(target=self.continuous_update, args=(repeat_interval,))
        self.thread.start()

    def save_data(self):
        # if file does not exist write to file with header
        if not os.path.isfile(self.output_path):
            self.data_df.to_csv(self.output_path, header=True)
        else:  # else it exists so append without writing the header
            self.data_df.to_csv(self.output_path, mode='a', header=False)

    def stop(self):
        self.stopped = True

    def is_fully_stopped(self):
        return self.fully_stopped
