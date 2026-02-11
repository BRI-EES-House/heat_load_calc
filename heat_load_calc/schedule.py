import os
import numpy as np
import csv
from typing import List, Dict, Tuple, Optional, Union
import logging
import json
from os import path
from enum import Enum, auto

from heat_load_calc import interval
from heat_load_calc.input_rooms import InputSchedule, InputScheduleDirect, InputScheduleFile, InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber, InputScheduleDataDayTypes, InputScheduleElements
from heat_load_calc.tenum import ENumberOfOccupants, EScheduleType, EDayType, EInterval


logger = logging.getLogger(name='HeatLoadCalc').getChild('Schedule')


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
    def get_schedule(cls, n_ocp: ENumberOfOccupants, a_f_is: List[float], itv: interval.Interval, scd_is: List[InputSchedule]):
        """Make Schedule class.

        Args:
            n_ocp: how to identify the occupants number. ('1', '2', '3', '4', or 'auto')
            a_floor_is: floor area of room i, m2, [i]
            itv: Interval class
            scds: list of the dictionary for schedule

        Returns:
            Schedule class
        """

        _a_f_is = np.array(a_f_is)

        # identify mode for the number of occupants (One, Two, Three, Four, Auto)
        #noo = ENumberOfOccupants(number_of_occupants)
        noo = n_ocp

        # number of occupants for calculation / 計算で用いられる居住人数
        n_p_calc = _get_n_p_calc(noo=noo, a_f_is=_a_f_is)

        # local ventilation amount in room i at step n / ステップnの室iにおける局所換気量, m3/s, [I, N]
        # The value is defined as the unit m3/h. Here, the unit is converted from m3/h to m3/s.
        # jsonファイルでは、 m3/h で示されているため、単位換算(m3/h -> m3/s)を行っている。
        v_mec_vent_local_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.LOCAL_VENTILATION_AMMOUNT, itv=itv, ipt_schedules=scd_is) / 3600.0

        # appliance heat generation in room i at step n / ステップnの室iにおける機器発熱, W, [I, N]
        q_gen_app_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.APPLIANCE_HEAT_GENERATION, itv=itv, ipt_schedules=scd_is)

        # cooking heat generation in room i in step n / ステップnの室iにおける調理発熱, W, [I, N]
        q_gen_ckg_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.COOKING_HEAT_GENERATION, itv=itv, ipt_schedules=scd_is)

        # cooking vapour generation in rom i at step n / ステップnの室iにおける調理発湿, kg/s, [I, N]
        # jsonファイルでは、g/h で示されているため、単位換算(g/h->kg/s)を行っている。
        x_gen_ckg_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.COOKING_VAPOUR_GENERATION, itv=itv, ipt_schedules=scd_is) / 1000.0 / 3600.0

        # lighting heat generation in room i at step n / ステップnの室iにおける照明発熱, W/m2, [I, N]
        # 単位面積あたりで示されていることに注意
        q_gen_lght_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.LIGHTING_HEAT_GENERATION, itv=itv, ipt_schedules=scd_is)

        # number of pople in room i at step n / ステップnの室iにおける在室人数, [I, N]
        # 居住人数で按分しているため、整数ではなく小数であることに注意
        n_hum_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.NUMBER_OF_PEOPLE, itv=itv, ipt_schedules=scd_is)

        # ratio of air conditioning in room i at step n / ステップnの室iにおける空調割合, [I, N]
        r_ac_demand_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.AC_DEMMAND, itv=itv, ipt_schedules=scd_is)

        # mode of air conditioning in room i at step n / ステップnの室iにおける空調モード, [I, N]
        t_ac_mode_is_ns = _get_schedules(noo=noo, n_p=n_p_calc, schedule_item=ScheduleItem.AC_MODE, itv=itv, ipt_schedules=scd_is)

        # internal heat generation excluding human body heat generation in room i at step n / ステップnの室iにおける人体発熱を除く内部発熱, W, [I, N]
        q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * _a_f_is[:, np.newaxis]

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

    @classmethod
    def create_constant(cls, n_rm: int, q_gen: float | list[float], x_gen: float | list[float], v_mec_vent_local: float | list[float], n_hum: float | list[float], r_ac_demanc: float | list[float], t_ac_mode: int | list[int], itv: interval.Interval = interval.Interval(eitv=interval.EInterval.M15)):

        n_step = itv.get_n_step_annual()

        return Schedule(
            q_gen_is_ns=np.array(q_gen).reshape(-1, 1).repeat(n_step, axis=1),
            x_gen_is_ns=np.array(x_gen).reshape(-1, 1).repeat(n_step, axis=1),
            v_mec_vent_local_is_ns=np.array(v_mec_vent_local).reshape(-1, 1).repeat(n_step, axis=1),
            n_hum_is_ns=np.array(n_hum).reshape(-1, 1).repeat(n_step, axis=1),
            r_ac_demand_is_ns=np.array(r_ac_demanc).reshape(-1, 1).repeat(n_step, axis=1),
            t_ac_mode_is_ns=np.array(t_ac_mode).reshape(-1, 1).repeat(n_step, axis=1)
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
        noo: ENumberOfOccupants,
        n_p: float,
        schedule_item: ScheduleItem,
        itv: interval.Interval,
        ipt_schedules: List[InputSchedule]
):
    
    # Read the list of the schedule type(ScheduleType Enum Class) and scheduled dictionary.
    # List of the dictionary describing the schedule.
    ipt_schedule_datas: list[InputScheduleData] = [_load_schedule(ipt_schedule=ipt_schedule) for ipt_schedule in ipt_schedules]

    return np.concatenate([
        [_get_schedule(noo=noo, n_p=n_p, schedule_item=schedule_item, itv=itv, ipt_schedule_data=ipt_schedule_data)]
        for ipt_schedule_data in ipt_schedule_datas
    ])


def _get_schedule(
        noo: ENumberOfOccupants,
        n_p: float,
        schedule_item: ScheduleItem,
        itv: interval.Interval,
        ipt_schedule_data: InputScheduleData
) -> np.ndarray:
    """Get the schedule. / スケジュールを取得する。

    Args:
        noo: specified method of number of occupants / 居住人数の指定方法
        n_p: number of occupants / 居住人数
        schedule_item: ScheduleItem enum class
        itv: Interval class
        ipt_schedule_data: InputScheduleData class

    Returns:
        schedule value, [35040 (15min)] or [17520 (30min)] or [8760 (1h)] 
    """

    # Load the calendar. / カレンダーの読み込み, [365]
    # type of the day / 日にちの種類
    # "W" = weekday / 平日
    # "HO" = go outside in holiday / 休日外
    # "HI" = stay inside in holiday / 休日在
    # example
    # ["HI", "W", "W", "W", "W", "W", "HI",...]
    calendar = _load_calendar()

    # 1日のうちのステップ数 / the number of steps in a day 
    n_step_day = itv.get_n_day()

    d_365_n = np.full((365, n_step_day), np.nan, dtype=float)
    d_365_n[calendar == 'W'] = _get_interpolated_schedule(day_type=EDayType.Weekday, schedule_item=schedule_item, ipt_schedule_data=ipt_schedule_data, noo=noo, n_p=n_p, itv=itv)
    d_365_n[calendar == 'HO'] = _get_interpolated_schedule(day_type=EDayType.HolidayOut, schedule_item=schedule_item, ipt_schedule_data=ipt_schedule_data, noo=noo, n_p=n_p, itv=itv)
    d_365_n[calendar == 'HI'] = _get_interpolated_schedule(day_type=EDayType.HolidayIn, schedule_item=schedule_item, ipt_schedule_data=ipt_schedule_data, noo=noo, n_p=n_p, itv=itv)
    d = d_365_n.flatten()

    return d


def _get_interpolated_schedule(
        day_type: EDayType,
        schedule_item: ScheduleItem,
        ipt_schedule_data: InputScheduleData,
        noo: ENumberOfOccupants,
        n_p: float,
        itv: interval.Interval
) -> np.ndarray:
    """Returns a list linearly interpolated by the number of occupants. / 世帯人数で線形補間したリストを返す
    Args:
        day_type: day type for schedule interpolation
        schedule_item: ScheduleItem class
        ipt_schedule_data: InputScheduleData class
        n_step_day: number of steps in a day
        noo: specified method of number of occupants / 居住人数の指定方法
        n_p: number of occupants / 居住人数

    Returns:
        list linerly interpolated / 線形補間したリスト, [24 or 48 or 96]
    """

    # TRUE is the list consisting of 0 or 1 value.
    # Only AC_DEMMAND is the 0 or 1 list.
    is_zero_one = schedule_item.is_zero_one()

    # Is the list proportionable ?
    # Only AC_MODE is NOT proportionable. 
    is_proportionable = schedule_item.is_proportionable()

    match ipt_schedule_data.schedule_type:

        case EScheduleType.CONST:

            if not isinstance(ipt_schedule_data, InputScheduleDataConst):
                raise Exception()

            ipt_schedule_data_const: InputScheduleDataConst = ipt_schedule_data

            input_const_schedule_elements: InputScheduleElements = ipt_schedule_data_const.ipt_schedule_data_day_types_const.day_type(day_type=day_type)

            return _make_list(input_schedule_elements=input_const_schedule_elements, schedule_item=schedule_item, itv=itv)

        case EScheduleType.NUMBER:

            if not isinstance(ipt_schedule_data, InputScheduleDataNumber):
                raise Exception()

            ipt_schedule_data_number: InputScheduleDataNumber = ipt_schedule_data

            if noo in [ENumberOfOccupants.One, ENumberOfOccupants.Two, ENumberOfOccupants.Three, ENumberOfOccupants.Four]:

                input_number_schedule_elements: InputScheduleElements = ipt_schedule_data_number.num(noo=noo).day_type(day_type=day_type)

                return _make_list(input_schedule_elements=input_number_schedule_elements, schedule_item=schedule_item, itv=itv)

            elif noo == ENumberOfOccupants.Auto:

                ceil_np, floor_np = _get_ceil_floor_np(n_p)

                ceiled_input_schedule_elements: InputScheduleElements = ipt_schedule_data_number.num(noo=ENumberOfOccupants(str(ceil_np))).day_type(day_type=day_type)
                ceil_schedule = _make_list(input_schedule_elements=ceiled_input_schedule_elements, schedule_item=schedule_item, itv=itv)

                floored_input_schedule_elements: InputScheduleElements = ipt_schedule_data_number.num(noo=ENumberOfOccupants(str(floor_np))).day_type(day_type=day_type)
                floor_schedule = _make_list(input_schedule_elements=floored_input_schedule_elements, schedule_item=schedule_item, itv=itv)
                
                if is_proportionable:
                    interpolate_np_schedule = ceil_schedule * (n_p - float(floor_np)) + floor_schedule * (float(ceil_np) - n_p)
                else:
                    interpolate_np_schedule = np.maximum(ceil_schedule, floor_schedule)

                return interpolate_np_schedule

            else:

                raise KeyError()

        case _:
            raise KeyError()


def _make_list(input_schedule_elements: InputScheduleElements, schedule_item: ScheduleItem, itv: interval.Interval) -> np.ndarray:
    """make ndarray list from the input dictionary.

    Args:
        input_schedule_elements: InputScheduleElements class
        schedule_item: ScheduleItem enum class
        itv: Interval class

    Returns:
        ndarray list of the schedule
    
    Notes:
        schedule_item_name: schedule item name which is the name of the dictionary;
            number_of_people
            heat_generation_appliances
            heat_generation_cooking
            vapor_generation_cooking
            local_vent_amount
            is_temp_limit_set

    """

    vs: np.ndarray = _make_schedule_list(input_schedule_elements, schedule_item)

    # The ratio for scaling the list length
    # 1 -> 24 : 24
    # 1 -> 48 : 48
    # 1 -> 96 : 96
    # 24 -> 24 : 1
    # 24 -> 48 : 2
    # 24 -> 96 : 4
    # 48 -> 24 : 0.5
    # 48 -> 48 : 1
    # 48 -> 96 : 2
    # 96 -> 24 : 0.25
    # 96 -> 48 : 0.5
    # 96 -> 96 : 1 
    ratio = itv.get_n_day() / len(vs)

    if ratio >= 1:

        expanding_ratio = int(ratio)

        if expanding_ratio not in [1, 2, 4, 24, 48, 96]:
            raise Exception()

        return vs.repeat(expanding_ratio)

    else:

        shrinking_ratio = int(1/ratio)

        if shrinking_ratio not in [2, 4]:
            raise Exception()

        if schedule_item.is_proportionable():
            return vs.reshape(-1, shrinking_ratio).mean(axis=1) 
        else:
            return vs.reshape(-1, shrinking_ratio).max(axis=1)


def _make_schedule_list(input_schedule_elements: InputScheduleElements, schedule_item: ScheduleItem) -> list[float] | list[int]:

    match schedule_item:
        case ScheduleItem.LOCAL_VENTILATION_AMMOUNT:
            vs = input_schedule_elements.local_vent_amount
        case ScheduleItem.APPLIANCE_HEAT_GENERATION:
            vs = input_schedule_elements.heat_generation_appliances
        case ScheduleItem.COOKING_HEAT_GENERATION:
            vs = input_schedule_elements.heat_generation_cooking
        case ScheduleItem.COOKING_VAPOUR_GENERATION:
            vs = input_schedule_elements.vapor_generation_cooking
        case ScheduleItem.LIGHTING_HEAT_GENERATION:
            vs = input_schedule_elements.heat_generation_lighting
        case ScheduleItem.NUMBER_OF_PEOPLE:
            vs = input_schedule_elements.number_of_people
        case ScheduleItem.AC_DEMMAND:
            vs = input_schedule_elements.is_temp_limit_set
        case ScheduleItem.AC_MODE:
            vs = input_schedule_elements.is_temp_limit_set
        case _:
            raise KeyError()
        
    if schedule_item.is_zero_one():
        return _convert_to_zero_one(v=np.array(vs))
    else:
        return np.array(vs)



def _convert_to_zero_one(v: np.ndarray) -> np.ndarray:
    """Return zero if the argument is zero and return one if the argument is more than zero. / 引数が0の場合は0を返し0より大の場合は1を返す。

    Args:
        v: argument / 引数

    Returns:
        0 or 1
    """

    return np.where(v > 0.0, np.ones_like(v, dtype=float), np.zeros_like(v, dtype=float))


def _get_ceil_floor_np(n_p: float) -> tuple[int, int]:
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
        raise ValueError('The number of the occupants is out of range.')

    return ceil_np, floor_np


def _load_schedule(ipt_schedule: InputSchedule) -> InputScheduleData:
    """Load the schedule from the input dictionary or specified csv file.
    
    Args:
        ipt_schedule: InputSchedule Class

    Returns:
        InputScheduleData class
    """
    
    ipt_schedule_direct: InputScheduleDirect
    
    if ipt_schedule.is_schedule_type_defined:

        if not isinstance(ipt_schedule, InputScheduleDirect):
            raise ValueError('Input schedule is not InputScheduleDirect class.')

        ipt_schedule_direct = ipt_schedule

    else:   # read from json file

        if not isinstance(ipt_schedule, InputScheduleFile):
            raise ValueError('Input schedule is not InputScheduleFile class.')

        ipt_schedule_file: InputScheduleFile = ipt_schedule

        js = _load_json_file(filename=ipt_schedule_file.name)

        ipt_schedule_from_file = InputSchedule.read(id=ipt_schedule_file.id, d_schedule=js)

        if not ipt_schedule_from_file.is_schedule_type_defined:
            raise ValueError('Schedule type is not defined in the json file.')
        
        ipt_schedule_direct = ipt_schedule_from_file

    ipt_schedule_data: InputScheduleData = ipt_schedule_direct.ipt_schedule_data

    return ipt_schedule_data


def _load_calendar() -> np.ndarray:
    """Get the calender of 365 days. / 365日分のカレンダーを取得する。

    Returns:
        list of calendar
    
    Note:
        ["HI", "W", "W", "W", "W", "W", "HI",...]
        The length of list is 365.
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


def _get_n_p_calc(noo: ENumberOfOccupants, a_f_is: np.ndarray) -> float:
    """Calculate the number of the occupants based on the total floor area. / 床面積の合計から居住人数を計算する。
    
    Args:
        noo: specified method of number of occupants / 居住人数の指定方法
        a_f_is: floor area of room i / 室iの床面積, m2, [I]

    Returns:
        number of occupants for calculation / 計算で用いられる居住人数
    """

    match noo:

        case ENumberOfOccupants.One:

            return 1.0

        case ENumberOfOccupants.Two:

            return 2.0

        case ENumberOfOccupants.Three:

            return 3.0
        
        case ENumberOfOccupants.Four:

            return 4.0
        
        case ENumberOfOccupants.Auto:

            # total floor area / 床面積の合計, m2
            a_f_total = a_f_is.sum()

            return np.clip(a_f_total / 30.0, 1.0, 4.0)
        
        case _:
    
            raise ValueError()
