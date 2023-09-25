﻿import os
import numpy as np
import csv
from typing import List, Dict, Tuple, Optional, Union
import logging
import json
from os import path
from enum import Enum

from heat_load_calc import interval

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

    def __init__(
            self, q_gen_is_ns: np.ndarray, x_gen_is_ns: np.ndarray, v_mec_vent_local_is_ns: np.ndarray, n_hum_is_ns: np.ndarray, ac_demand_is_ns: np.ndarray, ac_setting_is_ns: np.ndarray):
        """

        Args:
            q_gen_is_ns: ステップ　n　の室　i　における内部発熱, W, [i, n]
            x_gen_is_ns: ステップ　n　の室　i　における人体発湿を除く内部発湿, kg/s, [i, n]
            v_mec_vent_local_is_ns: ステップ　n　の室　i　における局所換気量, m3/s, [i, n]
            n_hum_is_ns: ステップ　n　の室　i　における在室人数, [i, n]
            ac_demand_is_ns: ステップ　n　の室　i　における空調需要, [i, n]
            ac_setting_is_ns: ステップ n の室 i における空調モード, [i, n]
        """

        self._q_gen_is_ns = q_gen_is_ns
        self._x_gen_is_ns = x_gen_is_ns
        self._v_mec_vent_local_is_ns = v_mec_vent_local_is_ns
        self._n_hum_is_ns = n_hum_is_ns
        self._ac_demand_is_ns = ac_demand_is_ns
        self._ac_setting_is_ns = ac_setting_is_ns

    @classmethod
    def get_schedule(cls, number_of_occupants: str, s_name_is: List[str], a_floor_is: List[float], itv: interval.Interval = interval.Interval.M15):
        """Schedule クラスを生成する。

        Args:
            number_of_occupants: 居住人数の指定方法
            s_name_is: 室 i のスケジュールの名称, [i]
            a_floor_is: 室 i の床面積, m2, [i]
            itv: Interval class

        Returns:
            Schedule class
        """

        # 居住人数の指定モード
        noo = NumberOfOccupants(number_of_occupants)

        # 居住人数
        n_p = _get_n_p(noo=noo, a_floor_is=a_floor_is)

        # ステップ n の室 i における局所換気量, m3/s, [i, n]
        # jsonファイルでは、 m3/h で示されているため、単位換算(m3/h -> m3/s)を行っている。
        v_mec_vent_local_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='local_vent_amount', itv=itv) / 3600.0

        # ステップ n の室 i における機器発熱, W, [i, n]
        q_gen_app_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='heat_generation_appliances', itv=itv)

        # ステップ n の室 i における調理発熱, W, [i, n]
        q_gen_ckg_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='heat_generation_cooking', itv=itv)

        # ステップ n の室 i における調理発湿, kg/s, [i, n]
        # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
        x_gen_ckg_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='vapor_generation_cooking', itv=itv) / 1000.0 / 3600.0

        # ステップ n の室 i における照明発熱, W/m2, [i, n]
        # 単位面積あたりで示されていることに注意
        q_gen_lght_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='heat_generation_lighting', itv=itv)

        # ステップ n の室 i における在室人数, [i, n]
        # 居住人数で按分しているため、整数ではなく小数であることに注意
        n_hum_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='number_of_people', itv=itv)

        # ステップ n の室 i における空調割合, [i, n]
        ac_demand_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='is_temp_limit_set', itv=itv, is_zero_one=True)

        # ステップ n の室 i における空調モード, [i, n]
        ac_setting_is_ns = cls._get_schedules(s_name_is=s_name_is, noo=noo, n_p=n_p, schedule_type='is_temp_limit_set', itv=itv, is_proportionable=False)

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
            ac_demand_is_ns=ac_demand_is_ns,
            ac_setting_is_ns=ac_setting_is_ns
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
    def q_gen_is_ns(self) -> np.ndarray:
        """ステップnの室iにおける人体発熱を除く内部発熱, W, [i, N]"""
        return self._q_gen_is_ns

    @property
    def x_gen_is_ns(self) -> np.ndarray:
        """ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, N]"""
        return self._x_gen_is_ns

    @property
    def v_mec_vent_local_is_ns(self) -> np.ndarray:
        """ステップnの室iにおける局所換気量, m3/s, [i, N]"""
        return self._v_mec_vent_local_is_ns

    @property
    def n_hum_is_ns(self) -> np.ndarray:
        """ステップnの室iにおける在室人数, [i, N]"""
        return self._n_hum_is_ns

    @property
    def ac_demand_is_ns(self) -> np.ndarray:
        """ステップnの室iにおける空調需要, [i, N]"""
        return self._ac_demand_is_ns

    @property
    def ac_setting_is_ns(self) -> np.ndarray:
        """ステップnの室iにおける空調モード, [i, N]"""
        return self._ac_setting_is_ns

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
    def _get_schedules(
            cls,
            s_name_is: List[str],
            noo: NumberOfOccupants,
            n_p: float,
            schedule_type: str,
            itv: interval.Interval,
            is_proportionable: Optional[bool] = True,
            is_zero_one: Optional[bool] = False
    ):

        return np.concatenate([
            [cls._get_schedule(schedule_name_i=schedule_name_i, noo=noo, n_p=n_p, schedule_type=schedule_type, itv=itv, is_proportionable=is_proportionable, is_zero_one=is_zero_one)]
            for schedule_name_i in s_name_is
        ])

    @classmethod
    def _get_schedule(
            cls,
            schedule_name_i: str,
            noo: NumberOfOccupants,
            n_p: float,
            schedule_type: str,
            itv: interval.Interval,
            is_proportionable: Optional[bool] = True,
            is_zero_one: Optional[bool] = False
    ) -> np.ndarray:
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
            itv: Interval class
            is_proportionable: 按分可能かどうか
                按分可能な場合は居住人数により按分が行われる
                按分可能でない場合は2つの数字のうち大きい方の値が採用される
                按分作業が発生しない場合（schedule_type が const の場合または schedule_type が number でかつ居住人数が auto ではない場合）、本パラメータは無視される。
                これが適用されないのは唯一、ac_setting を想定している。
            is_zero_one: 数字データの意味をゼロ・イチの意味に読み替えるかどうか
                例：　[0, 3, 5, 7, 0] -> [0, 1, 1, 1, 0]
                ac_demand に適用されることを想定している
        Returns:
            スケジュール, [35040 (15min)] or [17520 (30min)] or [8760 (1h)] 
        """
        
        # カレンダーの読み込み（日にちの種類（'平日', '休日外', '休日在'））, [365]
        calendar = cls._load_calendar()

        # スケジュールを記述した辞書の読み込み
        # d = cls._load_schedule(filename='schedules')
        # {
        #  "schedule_type": "const/number",
        #  "schedule": {
        #    "const/1/2/3/4": {
        #      "Weekday": {
        #        "number_of_people": [],
        #        "heat_generation_appliances": [],
        #        "heat_generation_lighting": [],
        #        "heat_generation_cooking": [],
        #        "vapor_generation_cooking": [],
        #        "local_vent_amount": [],
        #        "is_temp_limit_set": []
        #      },
        #      "Holiday_In": ...
        #      "Holiday_Out": ...
        #    }
        #  }
        #}
        d = cls._load_schedule(filename=schedule_name_i)

        # 1日のうちのステップ数 / the number of steps in a day 
        n_step_day = itv.get_n_hour() * 24 

        def convert_schedule(day_type: str):
            if d['schedule_type'] == 'number':
                return {
                    'schedule_type': 'number',
                    '1': _check_and_read_value(d=d['schedule']['1'][day_type], schedule_type=schedule_type, n_step_day=n_step_day),
                    '2': _check_and_read_value(d=d['schedule']['2'][day_type], schedule_type=schedule_type, n_step_day=n_step_day),
                    '3': _check_and_read_value(d=d['schedule']['3'][day_type], schedule_type=schedule_type, n_step_day=n_step_day),
                    '4': _check_and_read_value(d=d['schedule']['4'][day_type], schedule_type=schedule_type, n_step_day=n_step_day),
                }
            elif d['schedule_type'] == 'const':
                return {
                    'schedule_type': 'const',
                    'const': _check_and_read_value(d=d['schedule']['const'][day_type], schedule_type=schedule_type, n_step_day=n_step_day)
                }
            else:
                raise KeyError()

        d_weekday = convert_schedule(day_type='Weekday')
        d_holiday_out = convert_schedule(day_type='Holiday_Out')
        d_holiday_in = convert_schedule(day_type='Holiday_In')

        d_365_96 = np.full((365, n_step_day), np.nan, dtype=float)
        d_365_96[calendar == 'W'] = _get_interpolated_schedule(daily_schedule=d_weekday, noo=noo, n_p=n_p, is_proportionable=is_proportionable, is_zero_one=is_zero_one)
        d_365_96[calendar == 'HO'] = _get_interpolated_schedule(daily_schedule=d_holiday_out, noo=noo, n_p=n_p, is_proportionable=is_proportionable, is_zero_one=is_zero_one)
        d_365_96[calendar == 'HI'] = _get_interpolated_schedule(daily_schedule=d_holiday_in, noo=noo, n_p=n_p, is_proportionable=is_proportionable, is_zero_one=is_zero_one)
        d = d_365_96.flatten()

        return d


def _check_and_read_value(d: Dict, schedule_type: str, n_step_day: int):

    # If the schedule_type key is not exist in the dictionary d, make the zero list.
    if schedule_type not in d:
        return [0] * n_step_day
    else:
        v = d[schedule_type]
        if v == 'zero':
            return [0] * n_step_day
        else:
            if len(v) != n_step_day:
                raise ValueError("Number of the list in the schedule does not match the interval.")
            return v


def _get_interpolated_schedule(
        daily_schedule: Dict,
        noo: NumberOfOccupants,
        n_p: Optional[float] = None,
        is_proportionable: Optional[bool] = True,
        is_zero_one: Optional[bool] = False
) -> np.ndarray:
    """Returns a list linearly interpolated by the number of occupants. / 世帯人数で線形補間したリストを返す
    Args:
        daily_schedule: schedule value
            Key: "const", "1", "2", "3", or "4"
            Value: values
                Number of values is
                    24 (itv = H1)
                    48 (itv = M30)
                    96 (itv = M15)
            {
                'schedule_type': 'number',
                '1': d['schedule']['1'][day_type][schedule_type],
                '2': d['schedule']['2'][day_type][schedule_type],
                '3': d['schedule']['3'][day_type][schedule_type],
                '4': d['schedule']['4'][day_type][schedule_type],
            }
            or
            {
                'schedule_type': 'const',
                'const': d['schedule']['const'][day_type][schedule_type]
            }
        noo: specified method of number of occupants / 居住人数の指定方法
        n_p: number of occupants / 居住人数
        is_proportionable: 按分可能かどうか
            If proportionable, the value is proportioned by the number of occupants. / 按分可能な場合は居住人数により按分が行われる。
            If not proportionable, the maximum vale is applied. / 按分可能でない場合は2つの数字のうち大きい方の値が採用される。
            按分作業が発生しない場合（schedule_type が const の場合または schedule_type が number でかつ居住人数が auto ではない場合）、本パラメータは無視される。
            これが適用されないのは唯一、ac_setting を想定している。
        is_zero_one: 数字データの意味をゼロ・イチの意味に読み替えるかどうか
            example: [0, 3, 5, 7, 0] -> [0, 1, 1, 1, 0]
            ac_demand に適用されることを想定している
    Returns:
        list linerly interpolated / 線形補間したリスト, [24 or 48 or 96]
    """

    if daily_schedule['schedule_type'] == 'const':

        scd = np.array(daily_schedule['const'])

        if is_zero_one:
            return _convert_to_zero_one(v=scd)
        else:
            return scd

    elif daily_schedule['schedule_type'] == 'number':

        if noo in [NumberOfOccupants.One, NumberOfOccupants.Two, NumberOfOccupants.Three, NumberOfOccupants.Four]:

            scd = np.array(daily_schedule[str(noo.value)])

            if is_zero_one:
                return _convert_to_zero_one(v=scd)
            else:
                return scd

        elif noo == NumberOfOccupants.Auto:

            ceil_np, floor_np = _get_ceil_floor_np(n_p)

            if is_zero_one:
                ceil_schedule = _convert_to_zero_one(v=np.array(daily_schedule[str(ceil_np)]))
                floor_schedule = _convert_to_zero_one(v=np.array(daily_schedule[str(floor_np)]))
            else:
                ceil_schedule = np.array(daily_schedule[str(ceil_np)])
                floor_schedule = np.array(daily_schedule[str(floor_np)])

            if is_proportionable:
                interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)
            else:
                interpolate_np_schedule = np.maximum(ceil_schedule, floor_schedule)

            return interpolate_np_schedule

        else:

            raise KeyError()
    else:

        raise KeyError()


def _convert_to_zero_one(v: np.ndarray) -> np.ndarray:
    """Return zero if the argument is zero and return one if the argument is more than zero. / 引数が0の場合は0を返し0より大の場合は1を返す。

    Args:
        v: argument / 引数

    Returns:
        0 or 1
    """

    return np.where(v > 0.0, np.ones_like(v, dtype=float), np.zeros_like(v, dtype=float))


def _get_ceil_floor_np(n_p: float) -> Tuple[int, int]:
    """Calculate the floor and ceiled number of the number of occupants. / 世帯人数から切り上げ・切り下げた人数を整数値で返す

    Args:
        n_p: number of occupants / 世帯人数

    Returns:
        1) ceiled number of the number of occupants / 切り上げた世帯人数
        2) floor number of the number of occupants / 切り下げた世帯人数

    Notes:
        ERROR in case that the number is less than one or more than four.
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
        raise logger.error(msg='The number of the occupants is out of range.')

    return ceil_np, floor_np


def _get_n_p(noo: NumberOfOccupants, a_floor_is: List[float]) -> float:
    """Calculate the number of the occupants based on the total floor area. / 床面積の合計から居住人数を計算する。
    
    Args:
        noo: specified method of number of occupants / 居住人数の指定方法
        a_floor_is: floor area of room i / 室iの床面積, m2, [i]

    Returns:
        number of occupants / 居住人数
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

        # total floor area / 床面積の合計, m2
        a_floor_total = sum(a_floor_is)

        if a_floor_total < 30.0:
            return 1.0
        elif a_floor_total < 120.0:
            return a_floor_total / 30.0
        else:
            return 4.0
    else:
        raise ValueError()
