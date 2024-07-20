import os
import numpy as np
import csv
from typing import List, Dict, Tuple, Optional, Union
import logging
import json
from os import path
from enum import Enum, auto

from heat_load_calc import interval

logger = logging.getLogger(name='HeatLoadCalc').getChild('Schedule')


class NumberOfOccupants(Enum):
    """specified method of number of occupants / 居住人数の指定方法
    Specify the number of the occupants from one to four, or "auto".
    "auto" is the way that the number of the occupants is decided based on the total floor area.
    1~4人を指定するか、auto の場合は床面積から居住人数を指定する方法を選択する。

    """

    One = "1"
    Two = "2"
    Three = "3"
    Four = "4"
    Auto = "auto"


class ScheduleType(Enum):
    """Schedule type
    number = specify each schedule for one, two theree and four occupant(s)
    const = specify constant schedule not depending the number of occupants
    """

    NUMBER = "number"
    CONST = "const"


class ScheduleItem(Enum):

    LOCAL_VENTILATION_AMMOUNT = auto()
    APPLIANCE_HEAT_GENERATION = auto()
    COOKING_HEAT_GENERATION = auto()
    COOKING_VAPOUR_GENERATION = auto()
    LIGHTING_HEAT_GENERATION = auto()
    NUMBER_OF_PEOPLE = auto()
    AC_DEMMAND = auto()
    AC_MODE = auto()

    def get_item_name_in_dictionary(self) -> str:

        return {
            ScheduleItem.LOCAL_VENTILATION_AMMOUNT: 'local_vent_amount',
            ScheduleItem.APPLIANCE_HEAT_GENERATION: 'heat_generation_appliances',
            ScheduleItem.COOKING_HEAT_GENERATION: 'heat_generation_cooking',
            ScheduleItem.COOKING_VAPOUR_GENERATION: 'vapor_generation_cooking',
            ScheduleItem.LIGHTING_HEAT_GENERATION: 'heat_generation_lighting',
            ScheduleItem.NUMBER_OF_PEOPLE: 'number_of_people',
            ScheduleItem.AC_DEMMAND: 'is_temp_limit_set',
            ScheduleItem.AC_MODE: 'is_temp_limit_set'
        }[self]
    
    def is_zero_one(self) -> bool:
        """Bool value which the value are converted to zero or one value. / 数字データの意味をゼロ・イチの意味に読み替えるかどうか
        example: [0, 3, 5, 7, 0] -> [0, 1, 1, 1, 0]
        This convert is assumed to be adopted to ac_demand.
        ac_demand に適用されることを想定している
        """
            
        return {
            ScheduleItem.LOCAL_VENTILATION_AMMOUNT: False,
            ScheduleItem.APPLIANCE_HEAT_GENERATION: False,
            ScheduleItem.COOKING_HEAT_GENERATION: False,
            ScheduleItem.COOKING_VAPOUR_GENERATION: False,
            ScheduleItem.LIGHTING_HEAT_GENERATION: False,
            ScheduleItem.NUMBER_OF_PEOPLE: False,
            ScheduleItem.AC_DEMMAND: True,
            ScheduleItem.AC_MODE: False
        }[self]

    def is_proportionable(self) -> bool:
        """which the value is proportionable: 按分可能かどうか
            If proportionable, the value is proportioned by the number of occupants. / 按分可能な場合は居住人数により按分が行われる。
            If not proportionable, the maximum vale is applied. / 按分可能でない場合は2つの数字のうち大きい方の値が採用される。
            按分作業が発生しない場合（schedule_type が const の場合または schedule_type が number でかつ居住人数が auto ではない場合）、本パラメータは無視される。
            これが適用されないのは唯一、ac_setting を想定している。
        """

        return {
            ScheduleItem.LOCAL_VENTILATION_AMMOUNT: True,
            ScheduleItem.APPLIANCE_HEAT_GENERATION: True,
            ScheduleItem.COOKING_HEAT_GENERATION: True,
            ScheduleItem.COOKING_VAPOUR_GENERATION: True,
            ScheduleItem.LIGHTING_HEAT_GENERATION: True,
            ScheduleItem.NUMBER_OF_PEOPLE: True,
            ScheduleItem.AC_DEMMAND: True,
            ScheduleItem.AC_MODE: False
        }[self]



class Schedule:

    def __init__(
            self, q_gen_is_ns: np.ndarray, x_gen_is_ns: np.ndarray, v_mec_vent_local_is_ns: np.ndarray, n_hum_is_ns: np.ndarray, r_ac_demand_is_ns: np.ndarray, t_ac_mode_is_ns: np.ndarray):
        """

        Args:
            q_gen_is_ns: ステップnにおける室iの内部発熱, W, [I, N]
            x_gen_is_ns: ステップnにおける室iの人体発湿を除く内部発湿, kg/s, [I, N]
            v_mec_vent_local_is_ns: ステップnにおける室iの局所換気量, m3/s, [I, N]
            n_hum_is_ns: ステップnにおける室iの在室人数, [I, N]
            r_ac_demand_is_ns: ステップnにおける室iの空調需要, [I, N]
            t_ac_mode_is_ns: ステップnの室iの空調モード, [I, N]
        """

        self._q_gen_is_ns = q_gen_is_ns
        self._x_gen_is_ns = x_gen_is_ns
        self._v_mec_vent_local_is_ns = v_mec_vent_local_is_ns
        self._n_hum_is_ns = n_hum_is_ns
        self._r_ac_demand_is_ns = r_ac_demand_is_ns
        self._t_ac_mode_is_ns = t_ac_mode_is_ns

    @classmethod
    def get_schedule(cls, number_of_occupants: str, a_f_is: List[float], itv: interval.Interval, scd_is: List[Dict]):
        """Schedule クラスを生成する。

        Args:
            number_of_occupants: 居住人数の指定方法
            a_floor_is: 室 i の床面積, m2, [i]
            itv: Interval class
            scds: list of the dictionary for schedule

        Returns:
            Schedule class
        """

        # 居住人数の指定モード
        noo = NumberOfOccupants(number_of_occupants)

        # number of occupants for calculation / 計算で用いられる居住人数
        n_p_calc = _get_n_p_calc(noo=noo, a_f_is=a_f_is)

        # local ventilation amount in room i at step n / ステップnの室iにおける局所換気量, m3/s, [I, N]
        # The value is defined as the unit m3/h. Here, the unit is converted from m3/h to m3/s.
        # jsonファイルでは、 m3/h で示されているため、単位換算(m3/h -> m3/s)を行っている。
        v_mec_vent_local_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.LOCAL_VENTILATION_AMMOUNT, itv=itv, scd_is=scd_is) / 3600.0

        # appliance heat generation in room i at step n / ステップnの室iにおける機器発熱, W, [I, N]
        q_gen_app_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.APPLIANCE_HEAT_GENERATION, itv=itv, scd_is=scd_is)

        # cooking heat generation in room i in step n / ステップnの室iにおける調理発熱, W, [I, N]
        q_gen_ckg_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.COOKING_HEAT_GENERATION, itv=itv, scd_is=scd_is)

        # cooking vapour generation in rom i at step n / ステップnの室iにおける調理発湿, kg/s, [I, N]
        # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
        x_gen_ckg_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.COOKING_VAPOUR_GENERATION, itv=itv, scd_is=scd_is) / 1000.0 / 3600.0

        # lighting heat generation in room i at step n / ステップnの室iにおける照明発熱, W/m2, [I, N]
        # 単位面積あたりで示されていることに注意
        q_gen_lght_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.LIGHTING_HEAT_GENERATION, itv=itv, scd_is=scd_is)

        # number of pople in room i at step n / ステップnの室iにおける在室人数, [I, N]
        # 居住人数で按分しているため、整数ではなく小数であることに注意
        n_hum_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.NUMBER_OF_PEOPLE, itv=itv, scd_is=scd_is)

        # ratio of air conditioning in room i at step n / ステップnの室iにおける空調割合, [I, N]
        r_ac_demand_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.AC_DEMMAND, itv=itv, scd_is=scd_is)

        # mode of air conditioning in room i at step n / ステップnの室iにおける空調モード, [I, N]
        t_ac_mode_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.AC_MODE, itv=itv, scd_is=scd_is)

        a_f_is = np.array(a_f_is)

        # internal heat generation excluding human body heat generation in room i at step n / ステップnの室iにおける人体発熱を除く内部発熱, W, [I, N]
        q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * a_f_is[:, np.newaxis]

        # internal vapor generation excluding human body vapor generation in room i at step n / ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [I, N]
        x_gen_is_ns = x_gen_ckg_is_ns

        return Schedule(
            q_gen_is_ns=q_gen_is_ns,
            x_gen_is_ns=x_gen_is_ns,
            v_mec_vent_local_is_ns=v_mec_vent_local_is_ns,
            n_hum_is_ns=n_hum_is_ns,
            r_ac_demand_is_ns=r_ac_demand_is_ns,
            t_ac_mode_is_ns=t_ac_mode_is_ns
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
            w.writerows(self.r_ac_demand_is_ns.T.tolist())

    @property
    def q_gen_is_ns(self) -> np.ndarray:
        """internal heat generation excluding human body heat generation in room i at step n / ステップnの室iにおける人体発熱を除く内部発熱, W, [I, N]"""
        return self._q_gen_is_ns

    @property
    def x_gen_is_ns(self) -> np.ndarray:
        """internal vapor generation excluding human body vapor generation in room i at step n / ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [I, N]"""
        return self._x_gen_is_ns

    @property
    def v_mec_vent_local_is_ns(self) -> np.ndarray:
        """local ventilation amount in room i at step n / ステップnの室iにおける局所換気量, m3/s, [I, N]"""
        return self._v_mec_vent_local_is_ns

    @property
    def n_hum_is_ns(self) -> np.ndarray:
        """number of pople in room i at step n / ステップnの室iにおける在室人数, [I, N]"""
        return self._n_hum_is_ns

    @property
    def r_ac_demand_is_ns(self) -> np.ndarray:
        """ratio of air conditioning in room i at step n / ステップnの室iにおける空調割合, [I, N]"""
        return self._r_ac_demand_is_ns

    @property
    def t_ac_mode_is_ns(self) -> np.ndarray:
        """mode of air conditioning in room i at step n / ステップnの室iにおける空調モード, [I, N]"""
        return self._t_ac_mode_is_ns


def _get_schedules(
        noo: NumberOfOccupants,
        n_p: float,
        schedule_item: ScheduleItem,
        itv: interval.Interval,
        scd_is: List[Dict]
):
    
    ds = [_load_schedule(scd_i=scd_i) for scd_i in scd_is]

    schedule_type_is = [d[0] for d in ds]
    schedule_is = [d[1] for d in ds]

    return np.concatenate([
        [_get_schedule(noo=noo, n_p=n_p, schedule_item=schedule_item, itv=itv, schedule_type_i=schedule_type_i, schedule_i=schedule_i)]
        for (schedule_type_i, schedule_i) in zip(schedule_type_is, schedule_is)
    ])


def _get_schedule(
        noo: NumberOfOccupants,
        n_p: float,
        schedule_item: ScheduleItem,
        itv: interval.Interval,
        schedule_type_i: ScheduleType,
        schedule_i: Dict
) -> np.ndarray:
    """Get the schedule. / スケジュールを取得する。

    Args:
        noo: specified method of number of occupants / 居住人数の指定方法
        n_p: number of occupants / 居住人数
        schedule_item: ScheduleItem enum class
        itv: Interval class
        schedule_type_i: ScheduleType enum type class
        schedule_i: dictionary for schedule of room i
            format of dictuonary descriving schedule / スケジュールを記述した辞書の形式
                {
                    "const/1/2/3/4": {
                        "Weekday": {
                            "number_of_people": [],
                            "heat_generation_appliances": [],
                            "heat_generation_lighting": [],
                            "heat_generation_cooking": [],
                            "vapor_generation_cooking": [],
                            "local_vent_amount": [],
                            "is_temp_limit_set": []
                        },
                        "Holiday_In": ...
                        "Holiday_Out": ...
                    }
                }
    Returns:
        スケジュール, [35040 (15min)] or [17520 (30min)] or [8760 (1h)] 
    """
    
    # Load the calendar. / カレンダーの読み込み, [365]
    # type of the day / 日にちの種類
    # "W" = weekday / 平日
    # "HO" = go outside in holiday / 休日外
    # "HI" = stay inside in holiday / 休日在
    calendar = _load_calendar()

    # 1日のうちのステップ数 / the number of steps in a day 
    n_step_day = itv.get_n_hour() * 24 

    d_365_n = np.full((365, n_step_day), np.nan, dtype=float)
    d_365_n[calendar == 'W'] = _get_interpolated_schedule(day_type='Weekday', schedule_item=schedule_item, schedule_type_i=schedule_type_i, schedule_i=schedule_i, n_step_day=n_step_day, noo=noo, n_p=n_p)
    d_365_n[calendar == 'HO'] = _get_interpolated_schedule(day_type='Holiday_Out', schedule_item=schedule_item, schedule_type_i=schedule_type_i, schedule_i=schedule_i, n_step_day=n_step_day, noo=noo, n_p=n_p)
    d_365_n[calendar == 'HI'] = _get_interpolated_schedule(day_type='Holiday_In', schedule_item=schedule_item, schedule_type_i=schedule_type_i, schedule_i=schedule_i, n_step_day=n_step_day, noo=noo, n_p=n_p)
    d = d_365_n.flatten()

    return d


def _get_interpolated_schedule(
        day_type,
        schedule_item: ScheduleItem,
        schedule_type_i,
        schedule_i,
        n_step_day,
        noo: NumberOfOccupants,
        n_p: Optional[float] = None
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
    Returns:
        list linerly interpolated / 線形補間したリスト, [24 or 48 or 96]
    """

    schedule_item_name = schedule_item.get_item_name_in_dictionary()

    is_zero_one = schedule_item.is_zero_one()

    is_proportionable = schedule_item.is_proportionable()

    if schedule_type_i == ScheduleType.CONST:

        scd = np.array(
            _check_and_read_value(d=schedule_i['const'][day_type], schedule_item_name=schedule_item_name, n_step_day=n_step_day)
        )

        if is_zero_one:
            return _convert_to_zero_one(v=scd)
        else:
            return scd

    elif schedule_type_i == ScheduleType.NUMBER:

        if noo in [NumberOfOccupants.One, NumberOfOccupants.Two, NumberOfOccupants.Three, NumberOfOccupants.Four]:

            scd = np.array(
                _check_and_read_value(d=schedule_i[str(noo.value)][day_type], schedule_item_name=schedule_item_name, n_step_day=n_step_day)
            )

            if is_zero_one:
                return _convert_to_zero_one(v=scd)
            else:
                return scd

        elif noo == NumberOfOccupants.Auto:

            ceil_np, floor_np = _get_ceil_floor_np(n_p)

            ceiled_scd = np.array(
                _check_and_read_value(d=schedule_i[str(ceil_np)][day_type], schedule_item_name=schedule_item_name, n_step_day=n_step_day)
            )
            floored_scd = np.array(
                _check_and_read_value(d=schedule_i[str(floor_np)][day_type], schedule_item_name=schedule_item_name, n_step_day=n_step_day)
            )

            if is_zero_one:
                ceil_schedule = _convert_to_zero_one(v=ceiled_scd)
                floor_schedule = _convert_to_zero_one(v=floored_scd)
            else:
                ceil_schedule = ceiled_scd
                floor_schedule = floored_scd

            if is_proportionable:
                interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)
            else:
                interpolate_np_schedule = np.maximum(ceil_schedule, floor_schedule)

            return interpolate_np_schedule

        else:

            raise KeyError()
    else:

        raise KeyError()


def _check_and_read_value(d: Dict, schedule_item_name: str, n_step_day: int) -> List:
    """_summary_

    Args:
        d: dictionary of the input file (see Notes)
            {
                "number_of_people": [],
                "heat_generation_appliances": [],
                "heat_generation_lighting": [],
                "heat_generation_cooking": [],
                "vapor_generation_cooking": [],
                "local_vent_amount": [],
                "is_temp_limit_set": []
            }
        schedule_item_name: schedule item name which is the name of the dictionary;
            number_of_people
            heat_generation_appliances
            heat_generation_cooking
            vapor_generation_cooking
            local_vent_amount
            is_temp_limit_set
        n_step_day: numbe of the steps in a day

    Returns:
        value of schedule pattern t_scd_d, type of occupants t_p and step n_d in day d
        居住人数タイプ t_p の日付 d のスケジュールパターン t_{scd,d} の値
    """

    # If the schedule_type key is not exist in the dictionary d, make the zero list.
    if schedule_item_name not in d:
        return [0] * n_step_day
    else:
        v = d[schedule_item_name]
        if v == 'zero':
            return [0] * n_step_day
        else:
            if len(v) != n_step_day:
                raise ValueError("Number of the list in the schedule does not match the interval.")
            return v


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


def _load_schedule(scd_i: Dict):
    """Load the schedule from the input dictionary or specified csv file.
    
    Args:
        scd_i: dictionary for schedule in room i from the input file
    Notes:
        scd_i
        In case that item "schedule_type" is defined.
        {
            "schedule_type": ...,
            "schedule": ...
        }
        In case that item "schedule_type" is not defined.
        {
            "name": ...,
        }
    """
    
    if "schedule_type" in scd_i:    # read from input file
        schedule_type = ScheduleType(scd_i["schedule_type"])
        schedule = scd_i["schedule"]
    else:   # read from json file
        js = _load_json_file(filename=scd_i["name"])
        schedule_type = ScheduleType(js["schedule_type"])
        schedule = js["schedule"]

    return schedule_type, schedule


def _load_calendar() -> np.ndarray:
    """Get the calender of 365 days. / 365日分のカレンダーを取得する。

    Returns:
        calendar
    """

    calender_dict = _load_json_file(filename='calendar')

    return np.array(calender_dict['calendar'])


def _load_json_file(filename: str) -> Dict:
    """Load the json file. / json ファイルを読み込む。
    """

    js = open(str(os.path.dirname(__file__)) + '/schedule/' + filename + '.json', 'r', encoding='utf-8')
    d_json = json.load(js)
    js.close()
    return d_json


def _get_n_p_calc(noo: NumberOfOccupants, a_f_is: List[float]) -> float:
    """Calculate the number of the occupants based on the total floor area. / 床面積の合計から居住人数を計算する。
    
    Args:
        noo: specified method of number of occupants / 居住人数の指定方法
        a_f_is: floor area of room i / 室iの床面積, m2, [i]

    Returns:
        number of occupants for calculation / 計算で用いられる居住人数
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
        a_f_total = sum(a_f_is)

        if a_f_total < 30.0:
            return 1.0
        elif a_f_total < 120.0:
            return a_f_total / 30.0
        else:
            return 4.0
    else:
        raise ValueError()
