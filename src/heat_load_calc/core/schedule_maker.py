import os
import pandas as pd
import numpy as np
import csv


class ScheduleMaker:

    def __init__(self, folder_path: str, rooms: list[dict]):

        self._folder_path = folder_path

        self._df_hg = self.read_pandas_file(folder_path=folder_path, file_name='heat_generation.csv')
        self._np_hg = self.read_csv_file(folder_path=folder_path, file_name='mid_data_heat_generation.csv')
        self._df_mg = self.read_pandas_file(folder_path=folder_path, file_name='moisture_generation.csv')
        self._np_mg = self.read_csv_file(folder_path=folder_path, file_name='mid_data_moisture_generation.csv')
        self._df_lv = self.read_pandas_file(folder_path=folder_path, file_name='local_vent.csv')
        self._np_lv = self.read_csv_file(folder_path=folder_path, file_name='mid_data_local_vent.csv')
        self._df_op = self.read_pandas_file(folder_path=folder_path, file_name='occupants.csv')
        self._np_op = self.read_csv_file(folder_path=folder_path, file_name='mid_data_occupants.csv')
        self._df_ad = self.read_pandas_file(folder_path=folder_path, file_name='ac_demand.csv')
        self._np_ad = self.read_csv_file(folder_path=folder_path, file_name='mid_data_ac_demand.csv')

        self._rooms = rooms

    @staticmethod
    def read_pandas_file(folder_path: str, file_name: str):

        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            print('The file ' + file_name + ' was exist.')
            return pd.read_csv(file_path)
        else:
            print('The file ' + file_name + ' was not exist.')
            return None

    @staticmethod
    def read_csv_file(folder_path: str, file_name: str):

        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            print('The file ' + file_name + ' was exist.')
            with open(file_path, 'r') as f:
                r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                return np.array([row for row in r]).T
        else:
            print('The file ' + file_name + ' was not exist.')
            return None

    def get_q_gen_is_ns(self):

        return self.get_multi_schedule(category='heat_generation', f_df=self._df_hg, f_csv=self._np_hg)

    def get_x_gen_is_ns(self):

        return self.get_multi_schedule(category='moisture_generation', f_df=self._df_mg, f_csv=self._np_mg)

    def get_v_mec_vent_local_is_ns(self):

        return self.get_multi_schedule(category='local_ventilation', f_df=self._df_lv, f_csv=self._np_lv)

    def get_n_hum_is_ns(self):

        return self.get_multi_schedule(category='occupants', f_df=self._df_op, f_csv=self._np_op)

    def get_ac_demand_is_ns(self):

        return self.get_multi_schedule(category='ac_demand', f_df=self._df_ad, f_csv=self._np_ad)

    def get_multi_schedule(self, category: str, f_df: pd.DataFrame, f_csv: np.ndarray):

        return np.stack([
            self.get_single_schedule(
                room=room, category=category, f_df=f_df, f_csv=f_csv
            ) for room in self._rooms
        ])

    @staticmethod
    def get_single_schedule(room: dict, category: str, f_df: pd.DataFrame, f_csv: np.ndarray):

        if 'schedule' in room:
            c = room['schedule'][category]
            if c['method'] == 'constant':
                print('Set the constant value to {} .'.format(category))
                return np.full(shape=(8760 * 4), fill_value=float(c['constant_value']))
            elif c['method'] == 'file':
                print('Read {} csv data for pandas format.'.format(category))
                return f_df[str(room['id'])].values
            else:
                raise Exception()
        else:
            print('Read {} csv data for numpy format.'.format(category))
            return f_csv[int(room['id'])]


