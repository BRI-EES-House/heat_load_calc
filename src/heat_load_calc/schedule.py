import os
import pandas as pd
import numpy as np
import csv
from typing import List, Dict
import logging

from heat_load_calc.initializer import residents_number
from heat_load_calc.initializer import schedule_loader


logger = logging.getLogger(name='HeatLoadCalc').getChild('Schedule')


class Schedule:

    def __init__(self, q_gen_is_ns: np.ndarray, x_gen_is_ns: np.ndarray, v_mec_vent_local_is_ns: np.ndarray, n_hum_is_ns: np.ndarray, ac_demand_is_ns: np.ndarray):
        """

        Args:
            q_gen_is_ns: ステップnの室iにおける内部発熱, W, [i, n]
            x_gen_is_ns: ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, n]
            v_mec_vent_local_is_ns: ステップnの室iにおける局所換気量, m3/s, [i, n]
            n_hum_is_ns: ステップnの室iにおける在室人数, [i, n]
            ac_demand_is_ns: ステップnの室iにおける空調需要, [i, n]
        """

        self._q_gen_is_ns = q_gen_is_ns
        self._x_gen_is_ns = x_gen_is_ns
        self._v_mec_vent_local_is_ns = v_mec_vent_local_is_ns
        self._n_hum_is_ns = n_hum_is_ns
        self._ac_demand_is_ns = ac_demand_is_ns

    @classmethod
    def get_schedule(cls, common: Dict, rooms: List[Dict], flag_run_schedule: bool, folder_path: str = ""):

        # 独自指定のCSVファイルの読み込み
        # 読み込むファイルが存在しない場合（独自指定をしない場合に該当）はNoneを返す。
        df_hg = cls._read_pandas_file(folder_path=folder_path, file_name='heat_generation.csv')
        np_hg = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_heat_generation.csv')
        df_mg = cls._read_pandas_file(folder_path=folder_path, file_name='moisture_generation.csv')
        np_mg = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_moisture_generation.csv')
        df_lv = cls._read_pandas_file(folder_path=folder_path, file_name='local_vent.csv')
        np_lv = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_local_vent.csv')
        df_op = cls._read_pandas_file(folder_path=folder_path, file_name='occupants.csv')
        np_op = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_occupants.csv')
        df_ad = cls._read_pandas_file(folder_path=folder_path, file_name='ac_demand.csv')
        np_ad = cls._read_csv_file(folder_path=folder_path, file_name='mid_data_ac_demand.csv')

        if common['schedule']['method'] == 'calculate':

            # 室iの名称, [i]
            room_name_is = [r['name'] for r in rooms]

            # 室iの床面積, m2, [i]
            a_floor_is = np.array([r['floor_area'] for r in rooms])

            # 床面積の合計, m2
            a_floor_total = a_floor_is.sum()

            # 居住人数
            n_p = residents_number.get_total_number_of_residents(a_floor_total=a_floor_total)

            # スケジュールを記述した辞書の読み込み
            d = schedule_loader._load_schedule()

            # カレンダーの読み込み（日にちの種類（'平日', '休日外', '休日在'））, [365]
            calendar = np.array(d['calendar'])

            # ステップ n の室 i における局所換気量, m3/s, [i, n]
            # jsonファイルでは、 m3/h で示されているため、単位換算(m3/h -> m3/s)を行っている。
            v_mec_vent_local_is_ns = np.concatenate([[schedule_loader._get_schedule(room_name_i=room_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='local_vent_amount')] for room_name_i in room_name_is]) / 3600.0

            # ステップ n の室 i における機器発熱, W, [i, n]
            q_gen_app_is_ns = np.concatenate([[schedule_loader._get_schedule(room_name_i=room_name, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='heat_generation_appliances')] for room_name in room_name_is])

            # ステップ n の室 i における調理発熱, W, [i, n]
            q_gen_ckg_is_ns = np.concatenate([[schedule_loader._get_schedule(room_name_i=room_name, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='vapor_generation_cooking')] for room_name in room_name_is])

            # ステップ n の室 i における調理発湿, kg/s, [i, n]
            # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
            x_gen_ckg_is_ns = np.concatenate([[schedule_loader._get_schedule(room_name_i=room_name, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='heat_generation_cooking')] for room_name in room_name_is]) / 1000.0 / 3600.0

            # ステップ n の室 i における照明発熱, W/m2, [i, n]
            # 単位面積あたりで示されていることに注意
            q_gen_lght_is_ns = np.concatenate([[schedule_loader._get_schedule(room_name_i=room_name, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='heat_generation_lighting')] for room_name in room_name_is])

            # ステップ n の室 i における在室人数, [i, n]
            # 居住人数で按分しているため、整数ではなく小数であることに注意
            n_hum_is_ns = np.concatenate([[schedule_loader._get_schedule(room_name_i=room_name, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='number_of_people')] for room_name in room_name_is])

            # ステップ n の室 i における空調割合, [i, n]
            ac_demand_is_ns = np.concatenate([[schedule_loader._get_schedule(room_name_i=room_name, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='is_temp_limit_set')] for room_name in room_name_is])

            # ステップ n の室 i における人体発熱を除く内部発熱, W, [i, n]
            q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * a_floor_is[:, np.newaxis]

            # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n]
            x_gen_is_ns = x_gen_ckg_is_ns

        elif common['schedule']['method'] == 'specify':

            q_gen_is_ns = cls._get_multi_schedule(category='heat_generation', f_df=df_hg, f_csv=np_hg, rooms=rooms)
            x_gen_is_ns = cls._get_multi_schedule(category='moisture_generation', f_df=df_mg, f_csv=np_mg, rooms=rooms)
            v_mec_vent_local_is_ns = cls._get_multi_schedule(category='local_ventilation', f_df=df_lv, f_csv=np_lv, rooms=rooms)
            n_hum_is_ns = cls._get_multi_schedule(category='occupants', f_df=df_op, f_csv=np_op, rooms=rooms)
            ac_demand_is_ns = cls._get_multi_schedule(category='ac_demand', f_df=df_ad, f_csv=np_ad, rooms=rooms)

        else:

            raise Exception()

        return Schedule(
            q_gen_is_ns=q_gen_is_ns,
            x_gen_is_ns=x_gen_is_ns,
            v_mec_vent_local_is_ns=v_mec_vent_local_is_ns,
            n_hum_is_ns=n_hum_is_ns,
            ac_demand_is_ns=ac_demand_is_ns
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
            logger.info('The file ' + file_name + ' was exist.')
            return pd.read_csv(file_path)
        else:
            logger.info('The file ' + file_name + ' was not exist.')
            return None

    @classmethod
    def _read_csv_file(cls, folder_path: str, file_name: str):

        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            logger.info('The file ' + file_name + ' was exist.')
            with open(file_path, 'r') as f:
                r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                return np.array([row for row in r]).T
        else:
            logger.info('The file ' + file_name + ' was not exist.')
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
                logger.info('Set the constant value to {} .'.format(category))
                return np.full(shape=(8760 * 4), fill_value=float(c['constant_value']))
            elif c['method'] == 'file':
                logger.info('Read {} csv data for pandas format.'.format(category))
                return f_df[str(room['id'])].values
            else:
                raise Exception()
        else:
            logger.info('Read {} csv data for numpy format.'.format(category))
            return f_csv[int(room['id'])]
