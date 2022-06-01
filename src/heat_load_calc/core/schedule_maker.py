import os
import pandas as pd
import numpy as np
import csv


class ScheduleMaker:

    def __init__(self, q_gen_is_ns: np.ndarray, x_gen_is_ns: np.ndarray, v_mec_vent_local_is_ns: np.ndarray, n_hum_is_ns: np.ndarray, ac_demand_is_ns: np.ndarray):

        self._q_gen_is_ns = q_gen_is_ns
        self._x_gen_is_ns = x_gen_is_ns
        self._v_mec_vent_local_is_ns = v_mec_vent_local_is_ns
        self._n_hum_is_ns = n_hum_is_ns
        self._ac_demand_is_ns = ac_demand_is_ns

    @classmethod
    def read_schedule(cls, folder_path: str, rooms: list[dict]):

        _df_hg = cls._read_pandas_file(folder_path=folder_path, file_name='heat_generation.csv')
        _np_hg = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_heat_generation.csv')
        _df_mg = cls._read_pandas_file(folder_path=folder_path, file_name='moisture_generation.csv')
        _np_mg = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_moisture_generation.csv')
        _df_lv = cls._read_pandas_file(folder_path=folder_path, file_name='local_vent.csv')
        _np_lv = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_local_vent.csv')
        _df_op = cls._read_pandas_file(folder_path=folder_path, file_name='occupants.csv')
        _np_op = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_occupants.csv')
        _df_ad = cls._read_pandas_file(folder_path=folder_path, file_name='ac_demand.csv')
        _np_ad = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_ac_demand.csv')

        _q_gen_is_ns = cls._get_multi_schedule(category='heat_generation', f_df=_df_hg, f_csv=_np_hg, rooms=rooms)
        _x_gen_is_ns = cls._get_multi_schedule(category='moisture_generation', f_df=_df_mg, f_csv=_np_mg, rooms=rooms)
        _v_mec_vent_local_is_ns = cls._get_multi_schedule(category='local_ventilation', f_df=_df_lv, f_csv=_np_lv, rooms=rooms)
        _n_hum_is_ns = cls._get_multi_schedule(category='occupants', f_df=_df_op, f_csv=_np_op, rooms=rooms)
        _ac_demand_is_ns = cls._get_multi_schedule(category='ac_demand', f_df=_df_ad, f_csv=_np_ad, rooms=rooms)

        return ScheduleMaker(
            q_gen_is_ns=_q_gen_is_ns,
            x_gen_is_ns=_x_gen_is_ns,
            v_mec_vent_local_is_ns=_v_mec_vent_local_is_ns,
            n_hum_is_ns=_n_hum_is_ns,
            ac_demand_is_ns=_ac_demand_is_ns
        )

    @property
    def q_gen_is_ns(self):

        return self._q_gen_is_ns

    @property
    def x_gen_is_ns(self):

        return self._x_gen_is_ns

    @property
    def v_mec_vent_local_is_ns(self):

        return self._v_mec_vent_local_is_ns

    @property
    def n_hum_is_ns(self):

        return self._n_hum_is_ns

    @property
    def ac_demand_is_ns(self):

        return self._ac_demand_is_ns

    @classmethod
    def _read_pandas_file(cls, folder_path: str, file_name: str):

        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            print('The file ' + file_name + ' was exist.')
            return pd.read_csv(file_path)
        else:
            print('The file ' + file_name + ' was not exist.')
            return None

    @classmethod
    def _read_csv_file(cls, folder_path: str, file_name: str):

        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            print('The file ' + file_name + ' was exist.')
            with open(file_path, 'r') as f:
                r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                return np.array([row for row in r]).T
        else:
            print('The file ' + file_name + ' was not exist.')
            return None

    @classmethod
    def _get_multi_schedule(cls, category: str, f_df: pd.DataFrame, f_csv: np.ndarray, rooms: list[dict]):

        return np.stack([
            cls._get_single_schedule(
                room=room, category=category, f_df=f_df, f_csv=f_csv
            ) for room in rooms
        ])

    @classmethod
    def _get_single_schedule(cls, room: dict, category: str, f_df: pd.DataFrame, f_csv: np.ndarray):

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
