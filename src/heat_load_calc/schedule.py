import os
import pandas as pd
import numpy as np
import csv
from typing import List, Dict, Tuple
import logging
import json
from os import path

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
    def get_schedule(cls, rooms: List[Dict], folder_path: str = ""):

        schedule_specify_method = 'calculate'
        # スケジュールの与え方は常にjsonファイルから読み込む形式に統一する。
        # 今後、numpy で1年間のデータを直接与える方法は採用しない。
        # しばらくの間、'specify' メソッドを残しておくが、十分確認した後、削除する予定。

        if schedule_specify_method == 'calculate':

            # 室iの名称, [i]
            s_name_is = [r['schedule']['name'] for r in rooms]

            # 室iの床面積, m2, [i]
            a_floor_is = np.array([r['floor_area'] for r in rooms])

            # 床面積の合計, m2
            a_floor_total = a_floor_is.sum()

            # 居住人数
            n_p = get_total_number_of_residents(a_floor_total=a_floor_total)

            calender_dict = cls._load_schedule(filename='calendar')

            # カレンダーの読み込み（日にちの種類（'平日', '休日外', '休日在'））, [365]
            calendar = np.array(calender_dict['calendar'])

            # スケジュールを記述した辞書の読み込み
            d = cls._load_schedule(filename='schedules')

            # ステップ n の室 i における局所換気量, m3/s, [i, n]
            # jsonファイルでは、 m3/h で示されているため、単位換算(m3/h -> m3/s)を行っている。
            v_mec_vent_local_is_ns = np.concatenate([[cls._get_schedule(schedule_name_i=s_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='local_vent_amount')] for s_name_i in s_name_is]) / 3600.0

            # ステップ n の室 i における機器発熱, W, [i, n]
            q_gen_app_is_ns = np.concatenate([[cls._get_schedule(schedule_name_i=s_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='heat_generation_appliances')] for s_name_i in s_name_is])

            # ステップ n の室 i における調理発熱, W, [i, n]
            q_gen_ckg_is_ns = np.concatenate([[cls._get_schedule(schedule_name_i=s_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='vapor_generation_cooking')] for s_name_i in s_name_is])

            # ステップ n の室 i における調理発湿, kg/s, [i, n]
            # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
            x_gen_ckg_is_ns = np.concatenate([[cls._get_schedule(schedule_name_i=s_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='heat_generation_cooking')] for s_name_i in s_name_is]) / 1000.0 / 3600.0

            # ステップ n の室 i における照明発熱, W/m2, [i, n]
            # 単位面積あたりで示されていることに注意
            q_gen_lght_is_ns = np.concatenate([[cls._get_schedule(schedule_name_i=s_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='heat_generation_lighting')] for s_name_i in s_name_is])

            # ステップ n の室 i における在室人数, [i, n]
            # 居住人数で按分しているため、整数ではなく小数であることに注意
            n_hum_is_ns = np.concatenate([[cls._get_schedule(schedule_name_i=s_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='number_of_people')] for s_name_i in s_name_is])

            # ステップ n の室 i における空調割合, [i, n]
            ac_demand_is_ns = np.concatenate([[cls._get_schedule(schedule_name_i=s_name_i, n_p=n_p, calendar=calendar, daily_schedule=d['daily_schedule'], schedule_type='is_temp_limit_set')] for s_name_i in s_name_is])

            # ステップ n の室 i における人体発熱を除く内部発熱, W, [i, n]
            q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * a_floor_is[:, np.newaxis]

            # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n]
            x_gen_is_ns = x_gen_ckg_is_ns

        elif schedule_specify_method == 'specify':

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

    def save_schedule(self, output_data_dir):

        # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
        mid_data_local_vent_path = path.join(output_data_dir, 'mid_data_local_vent.csv')
        logger.info('Save v_mec_vent_local_is_ns to `{}`'.format(mid_data_local_vent_path))
        with open(mid_data_local_vent_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(self.v_mec_vent_local_is_ns.T.tolist())

        # ステップnの室iにおける内部発熱, W, [8760*4]
        mid_data_heat_generation_path = path.join(output_data_dir, 'mid_data_heat_generation.csv')
        logger.info('Save q_gen_is_ns to `{}`'.format(mid_data_heat_generation_path))
        with open(mid_data_heat_generation_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(self.q_gen_is_ns.T.tolist())

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
        mid_data_moisture_generation_path = path.join(output_data_dir, 'mid_data_moisture_generation.csv')
        logger.info('Save x_gen_is_ns to `{}`'.format(mid_data_moisture_generation_path))
        with open(mid_data_moisture_generation_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(self.x_gen_is_ns.T.tolist())

        # ステップnの室iにおける在室人数, [8760*4]
        mid_data_occupants_path = path.join(output_data_dir, 'mid_data_occupants.csv')
        logger.info('Save n_hum_is_ns to `{}`'.format(mid_data_occupants_path))
        with open(mid_data_occupants_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(self.n_hum_is_ns.T.tolist())

        # ステップnの室iにおける空調需要, [8760*4]
        mid_data_ac_demand_path = path.join(output_data_dir, 'mid_data_ac_demand.csv')
        logger.info('Save ac_demand_is_ns to `{}`'.format(mid_data_ac_demand_path))
        with open(mid_data_ac_demand_path, 'w') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerows(self.ac_demand_is_ns.T.tolist())

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

    @classmethod
    def _load_schedule(cls, filename: str) -> Dict:
        """スケジュールを読み込む
        """

        js = open(str(os.path.dirname(__file__)) + '/schedule/' + filename + '.json', 'r', encoding='utf-8')
        d_json = json.load(js)
        js.close()
        return d_json

    @classmethod
    def _get_schedule(
            cls, schedule_name_i: str, n_p: float, calendar: np.ndarray, daily_schedule: Dict, schedule_type: str
    ) -> np.ndarray:
        """
        スケジュールを取得する。
        Args:
            schedule_name_i: 室 i のスケジュールの名称
            n_p: 居住人数
            calendar: 日にちの種類（'平日', '休日外', '休日在'), [365]
            daily_schedule: スケジュール（辞書型）
            schedule_type: どのようなスケジュールを扱うのか？　以下から指定する。
                'local_vent_amount'
                'heat_generation_appliances'
                'vapor_generation_cooking'
                'heat_generation_cooking'
                'heat_generation_lighting'
                'number_of_people'
                'is_temp_limit_set'
        Returns:
            スケジュール, [365*96]
        """

        def convert_schedule(day_type: str):
            return {
                '1': daily_schedule[schedule_name_i]['1'][day_type][schedule_type],
                '2': daily_schedule[schedule_name_i]['2'][day_type][schedule_type],
                '3': daily_schedule[schedule_name_i]['3'][day_type][schedule_type],
                '4': daily_schedule[schedule_name_i]['4'][day_type][schedule_type],
            }

        d_weekday = convert_schedule(day_type='平日')
        d_holiday_out = convert_schedule(day_type='休日外')
        d_holiday_in = convert_schedule(day_type='休日在')

        d_365_96 = np.full((365, 96), -1.0, dtype=float)
        d_365_96[calendar == '平日'] = cls._get_interpolated_schedule(n_p, d_weekday)
        d_365_96[calendar == '休日外'] = cls._get_interpolated_schedule(n_p, d_holiday_out)
        d_365_96[calendar == '休日在'] = cls._get_interpolated_schedule(n_p, d_holiday_in)
        d = d_365_96.flatten()

        return d

    @classmethod
    def _get_interpolated_schedule(cls, n_p: float, daily_schedule: Dict) -> np.ndarray:
        """
        世帯人数で線形補間してリストを返す
        Args:
            n_p: 居住人数
            daily_schedule: スケジュール
                Keyは必ず'1', '2', '3', '4'
                Valueは96個のリスト形式の値（15分インターバル）
        Returns:
            線形補間したリスト, [96]
        """

        ceil_np, floor_np = cls._get_ceil_floor_np(n_p)

        ceil_schedule = np.array(daily_schedule[str(ceil_np)])
        floor_schedule = np.array(daily_schedule[str(floor_np)])

        interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)

        return interpolate_np_schedule

    @classmethod
    def _get_ceil_floor_np(cls, n_p: float) -> Tuple[int, int]:
        """世帯人数から切り上げ・切り下げた人数を整数値で返す

        Args:
            n_p: 世帯人数

        Returns:
            タプル：
                切り上げた世帯人数
                切り下げた世帯人数

        Notes:
            1人未満、4人より大の人数を指定した場合はエラーを返す。
        """

        if 1.0 <= n_p < 2.0:
            ceil_np = 2
            floor_np = 1
        elif 2.0 <= n_p < 3.0:
            ceil_np = 3
            floor_np = 2
        elif 3.0 <= n_p <= 4.0:
            ceil_np = 4
            floor_np = 3
        else:
            raise logger.error(msg='The number of people is out of range.')

        return ceil_np, floor_np


def get_total_number_of_residents(a_floor_total: float) -> float:
    """
    床面積の合計から居住人数を計算する。
    Args:
        a_floor_total: 床面積の合計, m2

    Returns:
        居住人数
    """

    if a_floor_total < 30.0:
        return 1.0
    elif a_floor_total < 120.0:
        return a_floor_total / 30.0
    else:
        return 4.0
