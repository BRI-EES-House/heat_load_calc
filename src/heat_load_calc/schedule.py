import os
import numpy as np
import csv
from typing import List, Dict, Tuple, Optional
import logging
import json
from os import path
from enum import Enum

logger = logging.getLogger(name='HeatLoadCalc').getChild('Schedule')


class NumberOfOccupants(Enum):
    """居住人数の指定方法

    1～4人を指定するか、auto の場合は床面積から居住人数を指定する方法を選択する。
    """

    One = "1"
    Two = "2"
    Three = "3"
    Four = "4"
    Auto = "auto"


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
    def get_schedule(cls, number_of_occupants: str, s_name_is: List[str], a_floor_is: List[float]):
        """Schedule クラスを生成する。

        Args:
            number_of_occupants: 居住人数の指定方法
            s_name_is: 室 i のスケジュールの名称, [i]
            a_floor_is: 室 i の床面積, m2, [i]

        Returns:
            Schedule クラス
        """

        # 居住人数の指定モード
        noo = NumberOfOccupants(number_of_occupants)

        # 居住人数
        n_p = cls._get_n_p(noo=noo, a_floor_is=a_floor_is)

        # ステップ n の室 i における局所換気量, m3/s, [i, n]
        # jsonファイルでは、 m3/h で示されているため、単位換算(m3/h -> m3/s)を行っている。
        v_mec_vent_local_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='local_vent_amount') / 3600.0

        # ステップ n の室 i における機器発熱, W, [i, n]
        q_gen_app_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='heat_generation_appliances')

        # ステップ n の室 i における調理発熱, W, [i, n]
        q_gen_ckg_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='heat_generation_cooking')

        # ステップ n の室 i における調理発湿, kg/s, [i, n]
        # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
        x_gen_ckg_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='vapor_generation_cooking') / 1000.0 / 3600.0

        # ステップ n の室 i における照明発熱, W/m2, [i, n]
        # 単位面積あたりで示されていることに注意
        q_gen_lght_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='heat_generation_lighting')

        # ステップ n の室 i における在室人数, [i, n]
        # 居住人数で按分しているため、整数ではなく小数であることに注意
        n_hum_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='number_of_people')

        # ステップ n の室 i における空調割合, [i, n]
        ac_demand_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='is_temp_limit_set')

        a_floor_is = np.array(a_floor_is)

        # ステップ n の室 i における人体発熱を除く内部発熱, W, [i, n]
        q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * a_floor_is[:, np.newaxis]

        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n]
        x_gen_is_ns = x_gen_ckg_is_ns

        return Schedule(
            q_gen_is_ns=q_gen_is_ns,
            x_gen_is_ns=x_gen_is_ns,
            v_mec_vent_local_is_ns=v_mec_vent_local_is_ns,
            n_hum_is_ns=n_hum_is_ns,
            ac_demand_is_ns=ac_demand_is_ns
        )

    def save_schedule(self, output_data_dir):
        """スケジュールをCSV形式で保存する

        Args:
            output_data_dir: CSV形式で保存するファイルのディレクトリ

        """

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
        """

        Returns:
            ステップ n の室 i における内部発熱, W, [i, n]
        """

        return self._q_gen_is_ns

    @property
    def x_gen_is_ns(self):
        """

        Returns:
            ステップ n の室 i における人体発湿を除く内部発湿, kg / s, [i, n]
        """

        return self._x_gen_is_ns

    @property
    def v_mec_vent_local_is_ns(self):
        """

        Returns:
            ステップ n の室 i における局所換気量, m3 / s, [i, n]
        """

        return self._v_mec_vent_local_is_ns

    @property
    def n_hum_is_ns(self):
        """

        Returns:
            ステップ n の室 i における在室人数, [i, n]
        """

        return self._n_hum_is_ns

    @property
    def ac_demand_is_ns(self):
        """

        Returns:
            ステップ n の室 i における空調需要, [i, n]
        """

        return self._ac_demand_is_ns

    @classmethod
    def _load_calendar(cls) -> np.ndarray:
        """365日分のカレンダーを取得する。

        Returns:
            365日分のカレンダー
        """

        calender_dict = cls._load_schedule(filename='calendar')

        return np.array(calender_dict['calendar'])

    @classmethod
    def _load_schedule(cls, filename: str) -> Dict:
        """スケジュールを読み込む
        """

        js = open(str(os.path.dirname(__file__)) + '/schedule/' + filename + '.json', 'r', encoding='utf-8')
        d_json = json.load(js)
        js.close()
        return d_json

    @classmethod
    def _get_schedules(cls, s_name_is: List[str], noo: NumberOfOccupants, n_p: float, schedule_type: str):

        return np.concatenate([
            [cls._get_schedule(schedule_name_i=schedule_name_i, noo=noo, n_p=n_p, schedule_type=schedule_type)]
            for schedule_name_i in s_name_is
        ])

    @classmethod
    def _get_schedule(cls, schedule_name_i: str, noo: NumberOfOccupants, n_p: float, schedule_type: str) -> np.ndarray:
        """
        スケジュールを取得する。
        Args:
            schedule_name_i: 室 i のスケジュールの名称
            noo: 居住人数の指定方法（NumberOfOccupants 列挙体）
            n_p: 居住人数
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

        # カレンダーの読み込み（日にちの種類（'平日', '休日外', '休日在'））, [365]
        calendar = cls._load_calendar()

        # スケジュールを記述した辞書の読み込み
        # d = cls._load_schedule(filename='schedules')
        d = cls._load_schedule(filename=schedule_name_i)

        def convert_schedule(day_type: str):
            if d['schedule_type'] == 'number':
                return {
                    'schedule_type': 'number',
                    '1': d['schedule']['1'][day_type][schedule_type],
                    '2': d['schedule']['2'][day_type][schedule_type],
                    '3': d['schedule']['3'][day_type][schedule_type],
                    '4': d['schedule']['4'][day_type][schedule_type],
                }
            elif d['schedule_type'] == 'const':
                return {
                    'schedule_type': 'const',
                    'const': d['schedule']['const'][day_type][schedule_type]
                }
            else:
                raise KeyError()

        d_weekday = convert_schedule(day_type='Weekday')
        d_holiday_out = convert_schedule(day_type='Holiday_Out')
        d_holiday_in = convert_schedule(day_type='Holiday_In')

        d_365_96 = np.full((365, 96), -1.0, dtype=float)
        d_365_96[calendar == 'W'] = cls._get_interpolated_schedule(daily_schedule=d_weekday, noo=noo, n_p=n_p)
        d_365_96[calendar == 'HO'] = cls._get_interpolated_schedule(daily_schedule=d_holiday_out, noo=noo, n_p=n_p)
        d_365_96[calendar == 'HI'] = cls._get_interpolated_schedule(daily_schedule=d_holiday_in, noo=noo, n_p=n_p)
        d = d_365_96.flatten()

        return d

    @classmethod
    def _get_interpolated_schedule(cls, daily_schedule: Dict, noo: NumberOfOccupants, n_p: Optional[float] = None) -> np.ndarray:
        """
        世帯人数で線形補間してリストを返す
        Args:
            daily_schedule: スケジュール
                Keyは必ず'1', '2', '3', '4'
                Valueは96個のリスト形式の値（15分インターバル）
            noo: 居住人数の指定方法
            n_p: 居住人数
        Returns:
            線形補間したリスト, [96]
        """

        if daily_schedule['schedule_type'] == 'const':

            return daily_schedule['const']

        elif daily_schedule['schedule_type'] == 'number':

            if noo in [NumberOfOccupants.One, NumberOfOccupants.Two, NumberOfOccupants.Three, NumberOfOccupants.Four]:

                return np.array(daily_schedule[str(noo.value)])

            elif noo == NumberOfOccupants.Auto:

                ceil_np, floor_np = cls._get_ceil_floor_np(n_p)

                ceil_schedule = np.array(daily_schedule[str(ceil_np)])
                floor_schedule = np.array(daily_schedule[str(floor_np)])

                interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)

                return interpolate_np_schedule

            else:

                raise KeyError()
        else:

            raise KeyError()

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

    @classmethod
    def _get_n_p(cls, noo: NumberOfOccupants, a_floor_is: List[float]) -> float:
        """
        床面積の合計から居住人数を計算する。
        Args:
            noo: 居住人数の指定方法
            a_floor_is: 室 i の床面積, m2, [i]

        Returns:
            居住人数
        """

        if noo == NumberOfOccupants.One:
            return 1.0

        elif noo == NumberOfOccupants.Two:
            return 2.0

        elif noo == NumberOfOccupants.Three:
            return 3.0

        elif noo == NumberOfOccupants.Four:
            return 4.0

        elif noo == NumberOfOccupants.Auto:

            # 床面積の合計, m2
            a_floor_total = sum(a_floor_is)

            if a_floor_total < 30.0:
                return 1.0
            elif a_floor_total < 120.0:
                return a_floor_total / 30.0
            else:
                return 4.0
        else:
            raise ValueError()
