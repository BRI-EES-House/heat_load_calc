import numpy as np
import logging
from typing import Union
from enum import Enum

from heat_load_calc.global_number import get_sgm, get_eps
from scipy import optimize


class ShapeFactorMethod(Enum):

    AREA_AVERAGE = 'area_average'
    NAGATA = 'Nagata'


def get_f_mrt_is_js(a_s_js: np.ndarray, h_s_r_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """Calculate the weight coefficient of boundary for the infinitesimal sphere in the room.

    Args:
        a_s_js: surface area of boundary j, [J, 1]
        h_s_r_js: indoor surface radiant heat transfer coefficient of boundary j, W/m2K, [J, 1]
        p_is_js: matrix representing the relationship between rooms and boundaries, (0 or 1), [I, J]

    Returns:
        weight coefficient of boundary j for the infinitesimal sphere in room i, -, [i, j]

    Notes:
        eq.(1)
    """

    ah = a_s_js * h_s_r_js

    return p_is_js * ah.T / np.dot(p_is_js, ah)


def get_h_s_r_js(a_s_js: np.ndarray, p_is_js: np.ndarray, eps_r_i_js: np.ndarray, method: ShapeFactorMethod) -> np.ndarray:
    """Calculate indoor surface radiant heat transfer coefficient of boundary j.

    Args:
        a_s_js: surface area of boundary j, [J, 1]
        p_is_js: matrix representing the relationship between rooms and boundaries, (0 or 1), [I, J]
        eps_r_i_js: inside long wave radiative emissivity of boundary j, -, [J, 1]
        method: method for calculation of mutual shape factor of each boundaries, AREA_AVERAGE or NAGATA

    Returns:
        indoor surface radiant heat transfer coefficient of boundary j, W/m2K, [J, 1]
    """

    match method:

        case ShapeFactorMethod.AREA_AVERAGE:
            return _get_h_s_r_js_AreaAverage(a_s_js=a_s_js, p_is_js=p_is_js, eps_r_i_js=eps_r_i_js)
        case ShapeFactorMethod.NAGATA:
            return _get_h_s_r_js_Nagata(a_s_js=a_s_js, p_is_js=p_is_js, eps_r_js=eps_r_i_js)
        case _:
            raise ValueError()


def _get_h_s_r_js_AreaAverage(a_s_js: np.ndarray, eps_r_i_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """Calculate inside surface radiant heat transfer coefficient of boundary j (Area Ratio Method)
    
    Args:
        a_s_js: surface area of boundary j, m2, [J, 1]
        eps_r_i_js: inside long wave emissivity of boundary j, -, [J, 1]
        p_is_js: matrix representing the relationship between rooms and boundaries, (0 or 1), [I, J]

    Returns:
        inside surface radiant heat transfer coefficient of boundary j, W/m2K, [J, 1]
    """

    # ratio of the area of the boundary j to the sum of the arera of the boundary connecting to room i, -, [J, 1]
    r_a_js = _get_r_a_js(a_s_js=a_s_js, p_is_js=p_is_js)

    # The shape factor is considered equal to the area ratio.
    f_js = r_a_js

    _check_sum_f_value(p_is_js=p_is_js, f_js=f_js)

    h_s_r_js = _get_h_s_r_i_js(eps_r_i_js=eps_r_i_js, f_js=f_js)

    return h_s_r_js


def _get_h_s_r_js_Nagata(a_s_js: np.ndarray, eps_r_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """Calculate inside surface radiant heat transfer coefficient of boundary j (Nagata Method)

    Args:
        a_s_js: surface area of boundary j, m2, [J, 1]
        eps_r_i_js: inside long wave emissivity of boundary j, -, [J, 1]
        p_is_js: matrix representing the relationship between rooms and boundaries, (0 or 1), [I, J]

    Returns:
        inside surface radiant heat transfer coefficient of boundary j, W/m2K, [J, 1]
    """

    # ratio of the area of the boundary j to the sum of the arera of the boundary connecting to room i, -, [J, 1]
    r_a_js = _get_r_a_js(a_s_js=a_s_js, p_is_js=p_is_js)

    # area ratio of the boundary j in room i, [I, J]
    r_a_is_js = p_is_js * r_a_js.flatten()[np.newaxis, :]

    # 非線形方程式L(f̅)=0の解, [I, 1]
    f_ver_is = _get_f_ver_is(r_a_is_js=r_a_is_js)

    # 放射伝熱計算で使用する微小球に対する部位の形態係数, -, [j]
    f_is_js = _get_f_is_js(f_ver_is=f_ver_is, r_a_is_js=r_a_is_js)

    f_js = f_is_js.sum(axis=0).reshape(-1,1)

    _check_sum_f_value(p_is_js=p_is_js, f_js=f_js)

    h_s_r_js = _get_h_s_r_i_js(eps_r_i_js=eps_r_js, f_js=f_js)

    return h_s_r_js


def _get_h_s_r_i_js(eps_r_i_js: np.ndarray, f_js: np.ndarray) -> np.ndarray:
    """Clculate the radiative heat transfer coefficient.

    Args:
        eps_r_i_js: inside long wave radiative emissivity of boundary j, -, [J, 1]
        f_is_js: shape factor from micro-spheres in room of boundary j, -, [J, 1]

    Returns:
        radiative heat transfer coefficient of boundary j connected to room i, W/m2K, [J, 1]
    """

    # When determining the radiant heat transfer coefficient between boundaries,
    # the average radiant temperature is calculated as a fixed value of 20°C.
    theta_mrt = 20.0

    # radiative heat transfer efficient of boundary i, W/ m2K
    h_s_r_js = (eps_r_i_js / (1.0 - eps_r_i_js * f_js) * 4.0 * get_sgm() * (273.15 + theta_mrt) ** 3.0)

    return h_s_r_js


def _get_f_ver_is(r_a_is_js: np.ndarray) -> np.ndarray:
    """get the solution to the non liner equation L(f_ver_i)

    Args:
        r_a_is_js: the area ratio of the boundary j to the sum of the area of boundary connecting to rooms, [I, J]
    Returns:
        solution to the non liner equation L(f_ver_i), [I, 1]
    """

    return  np.array([_get_f_ver(r_a_i_js=r_a_i_js) for r_a_i_js in r_a_is_js]).reshape(-1, 1)


def _get_f_ver(r_a_i_js: np.ndarray) -> float:
    """get the solution to the non liner equation L(f_ver_i)

    Args:
        r_a_i_js: ratio of area of boundary i to the sum of area of the boundaries connected the room, -, [J]

    Returns:
        solution to the non liner equation L(f_ver_i)
    """

    def function_L(f_ver_i):
        """
        Args:
            f_ver_i: solution to the non liner equation L(f_ver_i)
        Notes:
            eq.(4)
        """
        return np.sum(_get_f_is_js(f_ver_is=f_ver_i, r_a_is_js=r_a_i_js)) - 1.0

    return float(optimize.fsolve(function_L, np.array(1.0))[0])


def _get_f_is_js(f_ver_is: np.ndarray, r_a_is_js: np.ndarray) -> np.ndarray:
    """Calculate the shape factor from the sphere in the room to boundaries.
    
    Args:
        f_ver_i: Solution to the non liner equation L(f_ver_i), -, [I, 1]
        r_a_is_js: ratio of area of boundary i to the sum of area of the boundaries connected room i, -, [I, J]
    Returns:
        shape factor from the sphere in the room i to the boundary j, [I, J]
    Notes:
        eq.(3)
    """

    return 0.5 * (1.0 - np.sign(1.0 - 4.0 * r_a_is_js / f_ver_is) * np.sqrt(np.abs(1.0 - 4.0 * r_a_is_js / f_ver_is)))


def _get_r_a_js(a_s_js: np.ndarray, p_is_js: np.ndarray) -> np.ndarray:
    """Get the ratio of the area of boundary i to the sum of the area in each room.

    Args:
        a_s_js: area of boundary j, [J, 1]
        p_is_js: matrix of the relationship between rooms and boundaries, [I, J]

    Returns:
        ratio of area of boundary i, [J, 1]
    
    Notes:
        eq. (5)
    """

    # sum of the area of the boundary connecting to room i, m2, [I, 1]
    a_s_sum_is = np.dot(p_is_js, a_s_js)

    # ratio of the area of the boundary j to the sum of the arera of the boundary connecting to room i, -, [J, 1]
    r_a_js = a_s_js / np.dot(p_is_js.T, a_s_sum_is)

    return r_a_js


def _check_sum_f_value(p_is_js: np.ndarray, f_js: np.ndarray):
    """Check the sum of shape factors. It should be equal to 1.0.

    Args:
        p_is_js: matrix of the relationship beween rooms and boundaries
        f_js: shape factor of boundary j
    """

    # the sum of the shape factors of boundaries which are connected to room i
    f_sum_is = np.dot(p_is_js, f_js)

    # Check whether the sum of f value in each room are equal to 1.0.
    for f_sum_i in f_sum_is.flatten():
        if abs(f_sum_i - 1.0) > 1.0e-3:
            logging.warning('形態係数の合計値が不正 TotalFF=', f_sum_i)

