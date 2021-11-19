import numpy as np
from typing import List

from heat_load_calc.core import boundary_simple
from heat_load_calc.core.equipments import Equipments


def get_flr_js(
        is_floor_js: np.ndarray,
        is_radiative_heating_is: np.ndarray,
        n_spaces: int,
        bss: List[boundary_simple.BoundarySimple],
        es: Equipments
) -> np.ndarray:
    """
    係数 flr を取得する。
    Args:
        is_floor_js: 境界 j が床か否か, [i]
        is_radiative_heating_is: 室 i に放射暖房が設置されているか否か, [i]
        n_spaces: 室の数
        bss: BoundarySimple クラスのリスト
    Returns:
        係数 flr, -, [j]
    """

    # 境界 j が接する室 id, [j]
    connected_room_id_js = np.array([bs.connected_room_id for bs in bss])

    # 境界 j の面積, m2, [j]
    a_srf_js = np.array([bs.area for bs in bss])

    flr_js = np.zeros(shape=(len(bss)), dtype=float)

    for i in range(n_spaces):

        is_connected = connected_room_id_js == i

        flr_js[is_connected] = _get_flr_i_js(
            area_i_js=a_srf_js[is_connected],
            is_radiative_heating=is_radiative_heating_is[i],
            is_floor_i_js=is_floor_js[is_connected]
        )
    return flr_js


def _get_flr_i_js(area_i_js: np.ndarray, is_radiative_heating: bool, is_floor_i_js: np.ndarray):
    """
    放射暖房放射成分吸収比率の計算

    Args:
        area_i_js: 室 i における境界 j の面積, m2
        is_radiative_heating: 室 i に放射暖房が設置されているか否か
        is_floor_i_js: 室 i における境界 j が床か否か
    Returns:
        放射暖房放射成分吸収比率
    """

    # 室 i の床面積の合計, m2
    a_floor_i = np.sum(area_i_js[is_floor_i_js])

    flr_i_js = area_i_js / a_floor_i * is_radiative_heating * is_floor_i_js

    return flr_i_js


