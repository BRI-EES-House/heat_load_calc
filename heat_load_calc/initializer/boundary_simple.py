import numpy as np
from dataclasses import dataclass

from heat_load_calc.initializer.boundary_type import BoundaryType


@dataclass
class BoundarySimple:

    # 名称
    name: str

    # 副名称
    sub_name: str

    # 境界の種類
    boundary_type: BoundaryType

    # 面積, m2
    area: float

    # 温度差係数
    h_td: float

    # 隣室タイプ
    #   'main_occupant_room': 0,
    #   'other_occupant_room': 1,
    #   'non_occupant_room': 2,
    #   'underfloor': 3
    next_room_type: int

    # 室内侵入日射吸収の有無
    is_solar_absorbed_inside: bool

    # 室外側の日射の有無
    # True: 当たる
    # False: 当たらない
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    is_sun_striked_outside: bool

    # 面する方位
    # 's', 'sw', 'w', 'nw', 'n', 'ne', 'e', 'se', 'top', 'bottom'
    # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
    direction: str

    # 室内側表面総合熱伝達率, W/m2K
    h_i: float

    # 相当外気温度, ℃, [8760 * 4]
    theta_o_sol: np.ndarray

    # 透過日射熱取得, W, [8760*4]
    q_trs_sol: np.ndarray

    # 応答係数法（項別公比法）における根の数
    n_root: int

    n_root: int
    row: np.ndarray
    rft0: float
    rfa0: float
    rft1: np.ndarray
    rfa1: np.ndarray

