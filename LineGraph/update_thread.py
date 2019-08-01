import threading
import numbers
import time
import pandas as pd
import datetime as dt
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
        print("Updating... {0}".format(dt.datetime.now()))
        df = pd.read_csv(self.csv_path)

        retrieved_data = []

        for index, row in df.iterrows():
            value, units = get_value(row['Facility'], row['Meter'], live=True)

            value = float(value) if isinstance(value, numbers.Number) else ''
            retrieved_data.append(value)

            if self.stopped:
                return

        retrieved_data.append(dt.datetime.now())

        # Add to the end of the DF
        self.data_df.loc[len(self.data_df)] = retrieved_data
        print("Updated...")

    def continuous_update(self, repeat_interval):
        while True:
            if self.stopped:
                break
            self.get_new_values()
            if self.stopped:
                break
            time.sleep(repeat_interval)

        self.save_data()
        self.fully_stopped = True

    def begin_update_thread(self, repeat_interval):
        self.thread = threading.Thread(target=self.continuous_update, args=(repeat_interval,))
        self.thread.start()

    def save_data(self):
        print("Saving")

    def stop(self):
        self.stopped = True

    def is_fully_stopped(self):
        return self.fully_stopped
