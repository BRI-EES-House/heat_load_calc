from typing import Optional, List
from general_functions import round_num


class ModelHouse:

    def __init__(self, a_f):

        self.a_f = a_f


def get_a_f(house_type: str, a_f_total: float, r_fa: Optional[float]) -> List[float]:
    """
    Args:
        house_type: 住戸の種類
        a_f_total: 床面積の合計, m2
        r_fa: 1階の床面積に対する2階の床面積の比
    Returns:
        各階の床面積, m2
    Notes:
        戸建住戸の場合は2つの要素からなる配列で、配列0番目が1階、配列1番目が2階の値である。
        集合住宅の場合は1つの要素からなる配列（集合住宅の場合、平屋を想定している。）
    """

    if house_type == 'detached':
        return [a_f_total / (1 + r_fa), a_f_total * r_fa / (1 + r_fa)]
    elif house_type == 'attached':
        return [a_f_total]
    else:
        raise Exception


def get_entrance(
        house_type: str, floor_ins_type: str, l_entrance_ms: float, l_entrance_os: float
) -> (float, float, (float, float, float, float), float, float, float, float, float):
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床断熱の種類
        l_entrance_ms: 主開口方位側の玄関の土間床等の周辺部の基礎長さ, m
        l_entrance_os: その他方位側の玄関の土間床等の周辺部の基礎長さ, m
    Returns:
        次の7つの変数からなるタプル
            (1) 玄関の土間床等の面積, m2
            (2) 玄関の床の面積, m2
            (3) 玄関の土間床等の外周部の長さ（室外側）（4方向）, m
            (4) 玄関の土間床等の外周部の長さ（主方位から0度）, m
            (5) 玄関の土間床等の外周部の長さ（主方位から90度）, m
            (6) 玄関の土間床等の外周部の長さ（主方位から180度）, m
            (7) 玄関の土間床等の外周部の長さ（主方位から270度）, m
            (8) 玄関の土間床等の外周部の長さ（室内側）, m
    """

    # 玄関の土間床等の外周部の長さ（主方位から0度）, m
    # 玄関の土間床等の外周部の長さ（主方位から90度）, m
    # 玄関の土間床等の外周部の長さ（主方位から180度）, m
    # 玄関の土間床等の外周部の長さ（主方位から270度）, m
    if house_type == 'detached':
        l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270 \
            = 0.0, l_entrance_os, l_entrance_ms, 0.0
    elif house_type == 'attached':
        l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270 = 0.0, 0.0, 0.0, 0.0
    else:
        raise Exception

    # 玄関の土間床等の外周部の長さ（室内側）, m
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            l_base_entrance_inside = l_entrance_ms + l_entrance_os
        elif floor_ins_type == 'base':
            l_base_entrance_inside = 0.0
        else:
            raise Exception
    elif house_type == 'attached':
        l_base_entrance_inside = 0.0
    else:
        raise Exception

    # 玄関の土間床等の面積, m2
    if house_type == 'detached':
        a_ef_entrance = l_entrance_ms * l_entrance_os
        a_entrance = 0.0
    elif house_type == 'attached':
        a_ef_entrance = 0.0
        a_entrance = l_entrance_ms * l_entrance_os

    return a_ef_entrance,a_entrance, \
        (l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270), \
        l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270,\
        l_base_entrance_inside


def get_bath(
        house_type: str, floor_ins_type: str, bath_ins_type: str, l_base_bath_ms: float, l_base_bath_os: float
) -> (float, float, float, float, float, float, float):
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床の断熱の種類
        bath_ins_type: 浴室の断熱の種類
        l_base_bath_ms: 主開口方位側の浴室の土間床等の周辺部の基礎長さ, m
        l_base_bath_os: その他方位側の浴室の土間床等の周辺部の基礎長さ, m
    Returns:
        次の7つの変数からなるタプル
            (1) 浴室の土間床等の面積, m2,
            (2) 浴室の床面積, m2
            (3) 浴室の土間床等の外周部の長さ（主方位から0度）, m
            (4) 浴室の土間床等の外周部の長さ（主方位から90度）, m
            (5) 浴室の土間床等の外周部の長さ（主方位から180度）, m
            (6) 浴室の土間床等の外周部の長さ（主方位から270度）, m
            (7) 浴室の土間床等の外周部の長さ（室内側）, m
    """

    # 浴室の土間床等の外周部の長さ（主方位から0度）, m
    # 浴室の土間床等の外周部の長さ（主方位から90度）, m
    # 浴室の土間床等の外周部の長さ（主方位から180度）, m
    # 浴室の土間床等の外周部の長さ（主方位から270度）, m
    if house_type == 'detached':
        if (floor_ins_type == 'floor' and bath_ins_type == 'base') or floor_ins_type == 'base':
            l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 \
                = 0.0, l_base_bath_os, l_base_bath_ms, 0.0
        elif floor_ins_type == 'floor' and (bath_ins_type == 'floor' or bath_ins_type == 'not_exist'):
            l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 = 0.0, 0.0, 0.0, 0.0
        else:
            raise Exception
    elif house_type == 'attached':
        l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 = 0.0, 0.0, 0.0, 0.0
    else:
        raise Exception

    # 浴室の土間床等の外周部の長さ（室内側）, m
    if house_type == 'detached':
        if floor_ins_type == 'base':
            l_base_bath_inside = 0.0
        elif floor_ins_type == 'floor':
            if bath_ins_type == 'base':
                l_base_bath_inside = l_base_bath_ms + l_base_bath_os
            elif bath_ins_type == 'floor' or bath_ins_type == 'not_exist':
                l_base_bath_inside = 0.0
            else:
                raise Exception
        else:
            raise Exception
    elif house_type == 'attached':
        l_base_bath_inside = 0.0
    else:
        raise Exception

    # 浴室の土間床等の面積, m2
    if house_type == 'detached':
        if floor_ins_type == 'base':
            a_ef_bath = l_base_bath_ms * l_base_bath_os
            a_f_bath = 0.0
        elif floor_ins_type == 'floor':
            if bath_ins_type == 'base':
                a_ef_bath = l_base_bath_ms * l_base_bath_os
                a_f_bath = 0.0
            elif bath_ins_type == 'floor' or bath_ins_type == 'not_exist':
                a_ef_bath = 0.0
                a_f_bath = l_base_bath_ms * l_base_bath_os
            else:
                raise Exception
        else:
            raise Exception
    elif house_type == 'attached':
        a_ef_bath = 0.0
        a_f_bath = l_base_bath_ms * l_base_bath_os
    else:
        raise Exception

    return a_ef_bath, a_f_bath, l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270, l_base_bath_inside


def get_f_s(house_type: str, floor_ins_type: str, bath_ins_type: str,
            a_env: float, a_f: List[float], h: List[float], h_base_other: float,
            h_base_bath: float, h_base_entrance: float, l_base_bath_000: float, l_base_bath_090: float,
            l_base_bath_180: float, l_base_bath_270: float, l_base_bath_inside: float, l_base_entrance_000: float,
            l_base_entrance_090: float, l_base_entrance_180: float, l_base_entrance_270: float,
            l_base_entrance_inside: float, f_s_default: List[float]):
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床の断熱の種類
        bath_ins_type: 浴室の床の断熱の種類
        a_env: 外皮面積の合計, m2
        a_f: 各階の床面積, m2
        h: 各階の高さ, m
        h_base_other: 基礎の高さ, m
        h_base_bath: 浴室の基礎の高さ, m
        h_base_entrance: 玄関の基礎の高さ, m
        l_base_bath_000: 浴室の土間床等の外周部の長さ（主方位から0度）, m
        l_base_bath_090: 浴室の土間床等の外周部の長さ（主方位から90度）, m
        l_base_bath_180: 浴室の土間床等の外周部の長さ（主方位から180度）, m
        l_base_bath_270: 浴室の土間床等の外周部の長さ（主方位から270度）, m
        l_base_bath_inside: 浴室の土間床等の外周部の長さ（室内側）, m
        l_base_entrance_000: 玄関の土間床等の外周部の長さ（主方位から0度）, m
        l_base_entrance_090: 玄関の土間床等の外周部の長さ（主方位から90度）, m
        l_base_entrance_180: 玄関の土間床等の外周部の長さ（主方位から180度）, m
        l_base_entrance_270: 玄関の土間床等の外周部の長さ（主方位から270度）, m
        l_base_entrance_inside: 玄関の土間床等の外周部の長さ（室内側）, m
        f_s_default: 形状係数のデフォルト値
    Returns:
        形状係数（リスト）
    Notes:
        戸建住戸の場合は2つの要素からなる配列で、配列0番目が1階、配列1番目が2階の値である。
        集合住宅の場合は1つの要素からなる配列（集合住宅の場合、平屋を想定している。）
    """

    l_base_entrance_total = l_base_entrance_000 + l_base_entrance_090 + l_base_entrance_180 \
        + l_base_entrance_270 + l_base_entrance_inside
    l_base_bath_total = l_base_bath_000 + l_base_bath_090 + l_base_bath_180 + l_base_bath_270 + l_base_bath_inside

    x = a_env - 2 * a_f[0] \
        - l_base_entrance_total * h_base_entrance \
        - l_base_bath_total * h_base_bath \
        + (l_base_entrance_total + l_base_bath_total) * h_base_other

    if house_type == 'detached':
        y = 4 * a_f[0] ** 0.5 * (h[0] + h_base_other) + 4 * a_f[1] ** 0.5 * f_s_default[1] / f_s_default[0] * h[1]
        f_s_2 = max(x / y * f_s_default[1] / f_s_default[0], 1.0)
        f_s_1 = f_s_2 * f_s_default[0] / f_s_default[1]
        return [f_s_1, f_s_2]
    elif house_type == 'attached':
        y = 4 * a_f[0] ** 0.5 * h[0]
        f_s_1 = max(x / y, 1.0)
        return [f_s_1]
    else:
        raise Exception


def get_l_prm(a_f: List[float], f_s: List[float]) -> List[float]:
    """
    Args:
        a_f: 各階の床面積, m2
        f_s: 形状係数（リスト）
    Returns:
        周長（リスト）, m
    Notes:
        戸建住戸の場合は2つの要素からなる配列で、配列0番目が1階、配列1番目が2階の値である。
        集合住宅の場合は1つの要素からなる配列（集合住宅の場合、平屋を想定している。）
    """

    return [4 * a_f_i ** 0.5 * f_s_i for a_f_i, f_s_i in zip(a_f, f_s)]


def get_l(house_type: str, a_f: List[float], l_prm: List[float]) -> (List[float], List[float]):
    """
    Args:
        house_type: 住戸の種類
        a_f: 各階の床面積（リスト）, m2
        l_prm: 周長（リスト）, m
    Returns:
        次の2つの変数からなるタプル
            (1) 各階の主方位の辺の長さ（リスト）, m
            (2) 各階のその他方位の辺の長さ（リスト）, m
    """

    dif = [max((l_prm_i / 2) ** 2 - 4 * a_f_i, 0.0) ** 0.5 / 2 for l_prm_i, a_f_i in zip(l_prm, a_f)]

    # 長手方向の辺の長さ, m
    l_ls = [l_prm_i / 4 + dif_i for l_prm_i, dif_i in zip(l_prm, dif)]
    # 短手方向の辺の長さ, m
    l_ss = [l_prm_i / 4 - dif_i for l_prm_i, dif_i in zip(l_prm, dif)]

    # 主方位とその他方位の辺の長さ, m
    l_ms, l_os = {
        'detached': (l_ls, l_ss),
        'attached': (l_ss, l_ls),
    }[house_type]

    return l_ms, l_os


def get_a_d_wall(a_door_000, a_door_090, a_door_180, a_door_270, a_srf_000, a_srf_090, a_srf_180, a_srf_270, a_window_000,
                 a_window_090, a_window_180, a_window_270):
    a_wall_000 = sum(a_srf_000) - a_window_000 - a_door_000
    a_wall_090 = sum(a_srf_090) - a_window_090 - a_door_090
    a_wall_180 = sum(a_srf_180) - a_window_180 - a_door_180
    a_wall_270 = sum(a_srf_270) - a_window_270 - a_door_270
    return a_wall_000, a_wall_090, a_wall_180, a_wall_270


def get_a_d_door(a_door_back_entrance, a_door_entrance, house_type):
    a_door_000 = 0.0
    a_door_090 = a_door_entrance if house_type == 'detached' else 0.0
    a_door_180 = a_door_back_entrance if house_type == 'detached' else a_door_entrance
    a_door_270 = 0.0
    return a_door_000, a_door_090, a_door_180, a_door_270


def get_a_d_window(a_window_total, r_window_000, r_window_090, r_window_180, r_window_270):
    a_window_000 = a_window_total * r_window_000
    a_window_090 = a_window_total * r_window_090
    a_window_180 = a_window_total * r_window_180
    a_window_270 = a_window_total * r_window_270
    return a_window_000, a_window_090, a_window_180, a_window_270


def get_a_d_window_total(a_door_back_entrance, a_door_entrance, a_open):
    a_window_total = a_open - a_door_entrance - a_door_back_entrance
    return a_window_total


def get_a_d_open(a_d_env, r_open):
    a_open = a_d_env * r_open
    return a_open


def get_a_d_env(a_base_total_000, a_base_total_090, a_base_total_180, a_base_total_270, a_base_total_inside, a_d_env):
    a_env = a_d_env + a_base_total_000 + a_base_total_090 + a_base_total_180 + a_base_total_270 + a_base_total_inside
    return a_env


def get_a_d_env_not_base(a_ef_total, a_f_total, a_roof, a_srf_000, a_srf_090, a_srf_180, a_srf_270):
    a_d_env = a_f_total + a_ef_total + a_roof + sum(a_srf_000) + sum(a_srf_090) + sum(a_srf_180) + sum(a_srf_270)
    return a_d_env


def get_a_d_srf(l_ms, l_os, h):
    a_srf_000 = [l_ls_i * h_i for l_ls_i, h_i in zip(l_ms, h)]
    a_srf_090 = [l_ss_i * h_i for l_ss_i, h_i in zip(l_os, h)]
    a_srf_180 = [l_ls_i * h_i for l_ls_i, h_i in zip(l_ms, h)]
    a_srf_270 = [l_ss_i * h_i for l_ss_i, h_i in zip(l_os, h)]
    return a_srf_000, a_srf_090, a_srf_180, a_srf_270


def get_a_d_base_total(a_base_entrance_000, a_base_entrance_090, a_base_entrance_180, a_base_entrance_270,
                       a_base_entrance_inside, a_base_bath_000, a_base_bath_090, a_base_bath_180, a_base_bath_270,
                       a_base_bath_inside, a_base_other_000, a_base_other_090, a_base_other_180, a_base_other_270,
                       a_base_other_inside):
    a_base_total_000 = a_base_other_000 + a_base_entrance_000 + a_base_bath_000
    a_base_total_090 = a_base_other_090 + a_base_entrance_090 + a_base_bath_090
    a_base_total_180 = a_base_other_180 + a_base_entrance_180 + a_base_bath_180
    a_base_total_270 = a_base_other_270 + a_base_entrance_270 + a_base_bath_270
    a_base_total_inside = a_base_other_inside + a_base_entrance_inside + a_base_bath_inside
    return a_base_total_000, a_base_total_090, a_base_total_180, a_base_total_270, a_base_total_inside


def get_a_d_base_other(l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270, h_base_other):
    a_base_other_000 = l_base_other_000 * h_base_other
    a_base_other_090 = l_base_other_090 * h_base_other
    a_base_other_180 = l_base_other_180 * h_base_other
    a_base_other_270 = l_base_other_270 * h_base_other
    a_base_other_inside = 0.0
    return a_base_other_000, a_base_other_090, a_base_other_180, a_base_other_270, a_base_other_inside


def get_a_d_base_bath(l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270, l_base_bath_inside,
                      h_base_bath):
    a_base_bath_000 = l_base_bath_000 * h_base_bath
    a_base_bath_090 = l_base_bath_090 * h_base_bath
    a_base_bath_180 = l_base_bath_180 * h_base_bath
    a_base_bath_270 = l_base_bath_270 * h_base_bath
    a_base_bath_inside = l_base_bath_inside * h_base_bath
    return a_base_bath_000, a_base_bath_090, a_base_bath_180, a_base_bath_270, a_base_bath_inside


def get_a_d_base_entrance(l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270,
                          l_base_entrance_inside, h_base_entrance):
    a_base_entrance_000 = l_base_entrance_000 * h_base_entrance
    a_base_entrance_090 = l_base_entrance_090 * h_base_entrance
    a_base_entrance_180 = l_base_entrance_180 * h_base_entrance
    a_base_entrance_270 = l_base_entrance_270 * h_base_entrance
    a_base_entrance_inside = l_base_entrance_inside * h_base_entrance
    return a_base_entrance_000, a_base_entrance_090, a_base_entrance_180, a_base_entrance_270, a_base_entrance_inside


def get_a_d_roof(a_f):
    a_roof = a_f[0]
    return a_roof


def get_l_base_total(l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270,
                     l_base_entrance_inside, l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270,
                     l_base_bath_inside, l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270,
                     l_base_other_inside):
    l_base_total_000 = l_base_other_000 + l_base_entrance_000 + l_base_bath_000
    l_base_total_090 = l_base_other_090 + l_base_entrance_090 + l_base_bath_090
    l_base_total_180 = l_base_other_180 + l_base_entrance_180 + l_base_bath_180
    l_base_total_270 = l_base_other_270 + l_base_entrance_270 + l_base_bath_270
    l_base_total_inside = l_base_other_inside + l_base_entrance_inside + l_base_bath_inside
    return l_base_total_000, l_base_total_090, l_base_total_180, l_base_total_270, l_base_total_inside


def get_l_base_other(house_type, floor_ins_type, l_ms, l_os, l_base_entrance_000, l_base_entrance_090,
                     l_base_entrance_180, l_base_entrance_270, l_base_bath_000, l_base_bath_090, l_base_bath_180,
                     l_base_bath_270):
    if house_type == 'detached' and floor_ins_type == 'base':
        l_base_other_000 = l_ms[0] - l_base_entrance_000 - l_base_bath_000
        l_base_other_090 = l_os[0] - l_base_entrance_090 - l_base_bath_090
        l_base_other_180 = l_ms[0] - l_base_entrance_180 - l_base_bath_180
        l_base_other_270 = l_os[0] - l_base_entrance_270 - l_base_bath_270
    else:
        l_base_other_000 = 0.0
        l_base_other_090 = 0.0
        l_base_other_180 = 0.0
        l_base_other_270 = 0.0
    l_base_other_inside = 0.0
    return l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270, l_base_other_inside


def get_a_d_f_total(a_f_entrance, a_f_bath, a_f_other):
    return a_f_entrance + a_f_bath + a_f_other


def get_a_d_f_other(house_type, floor_ins_type, bath_ins_type, a_ef_entrance, a_ef_bath, a_f, a_f_entrance, a_f_bath):
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            if bath_ins_type == 'base':
                a_f_other = a_f[0] - a_ef_entrance - a_ef_bath
            elif bath_ins_type == 'floor' or bath_ins_type == 'not_exist':
                a_f_other = a_f[0] - a_ef_entrance - a_f_bath
            else:
                raise Exception
        elif floor_ins_type == 'base':
            a_f_other = 0.0
        else:
            raise Exception
    elif house_type == 'attached':
        a_f_other = a_f[0] - a_f_entrance - a_f_bath
    else:
        raise Exception
    return a_f_other


def get_a_d_ef_total(a_ef_bath, a_ef_entrance, a_ef_other):
    a_ef_total = a_ef_entrance + a_ef_bath + a_ef_other
    return a_ef_total


def get_a_d_ef_other(house_type, floor_ins_type, a_f, a_ef_bath, a_ef_entrance):
    if house_type == 'detached' and floor_ins_type == 'base':
        a_ef_other = a_f[0] - a_ef_entrance - a_ef_bath
    else:
        a_ef_other = 0.0
    return a_ef_other


def calc_area(house_type: str, a_f_total: float, r_open: float,
              floor_ins_type: str = None, bath_ins_type: str = None, a_d_env: float = None):
    """
    Args:
        house_type: 住戸の種類 (= 'detached', 'attached')
        a_f_total: 床面積の合計, m2
        r_open: 開口部の面積比率
        floor_ins_type: 床の断熱の種類 (= 'floor', 'base')
        bath_ins_type: 浴室の床の断熱の種類 (= 'floor', 'base', 'not_exist')
        a_d_env: 外皮面積の合計, m2
    Returns:
    """

    # region model house を作成するにあたってのデフォルト設定

    # 形状係数のデフォルト値
    # 集合住宅の場合
    #   デフォルト住宅の床面積は70.00m2であり、周長は、主方位側長さ6.14m、その他方位側長さ11.4mである。
    #   f_s = l_prm / (a_f ** 0.5 * 4) だから、
    #   f_s = (11.4 + 11.4 + 6.14 + 6.14) / (70 ** 0.5 * 4) = 1.048215... = 1.05
    f_s_default = {'detached': [1.08, 1.04], 'attached': [1.05]}[house_type]

    # 1階の床面積に対する2階の床面積の比
    # 集合住宅の場合、平屋であるので、この値は定義できないため、Noneを返す。
    r_fa = {'detached': 0.77, 'attached': None}[house_type]

    # 玄関の基礎の高さ, m
    h_base_entrance = {'detached': 0.18, 'attached': 0.0}[house_type]

    # 浴室の基礎の高さ, m
    h_base_bath = {
        'detached': {
            'floor': {
                'floor': 0.0,
                'base': 0.5,
                'not_exist': 0.0,
                None: 0.0,
            }[bath_ins_type],
            'base': 0.5,
            None: 0.0,
        }[floor_ins_type],
        'attached': 0.0,
    }[house_type]

    # （玄関・浴室を除く）その他の部分の基礎の高さ
    h_base_other = {
        'detached': {'floor': 0.0, 'base': 0.5, None: 0.0}[floor_ins_type],
        'attached': 0.0,
    }[house_type]

    # 各階の高さ, m
    h = {'detached': [2.9, 2.7], 'attached': [2.8]}[house_type]

    # 玄関ドアの面積, m2
    #   集合住宅の玄関ドアは、0.9*1.95
    a_door_entrance = {'detached': 1.89, 'attached': 1.755}[house_type]

    # 勝手口ドアの面積, m2
    a_door_back_entrance = {'detached': 1.62, 'attached': 0.0}[house_type]

    # 主開口方位側の玄関の長さ, m
    # その他方位側の玄関の長さ, m
    l_entrance_ms, l_entrance_os = {'detached': (1.365, 1.82), 'attached': (1.0, 1.0)}[house_type]

    # 主開口方位側の浴室の長さ, m
    # その他方位側の浴室の長さ, m
    l_bath_ms, l_bath_os = {'detached': (1.82, 1.82), 'attached': (2.1, 1.365)}[house_type]

    # 窓の面積の合計に対する方位別の窓の面積
    # 集合住宅
    #   南側：2.26*2.0, 1.8*1.8
    #   西側：1.2*1.1, 0.6*0.9
    #   北側：1.2*1.1, 1.2*1.1
    #   南側の比率：0.632953..., 0.151713..., 0.215334... = 0.633, 0.1517, 0.2153, 0.0
    #   窓の面積の合計：12.26
    #   外皮の面積の合計：237.03
    #   面積比率：0.051723... = 0.052
    r_window_000, r_window_090, r_window_180, r_window_270 = {
        'detached': (0.6862, 0.0721, 0.1097, 0.1320),
        'attached': (0.6330, 0.1517, 0.2153, 0.0000),
    }[house_type]

    # endregion

    # 各階の床面積, m2
    a_f = get_a_f(house_type, a_f_total, r_fa)

    # 玄関の土間床等の面積, m2
    # 玄関の床面積, m2
    # 玄関の土間床等の外周部の長さ, m
    a_evp_ef_etrc, a_evp_f_entrance, l_base_entrance_outside, l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270, \
        l_base_entrance_inside = get_entrance(house_type, floor_ins_type, l_entrance_ms, l_entrance_os)
    l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270 = l_base_entrance_outside

    mh = ModelHouse(a_f)

    # 浴室の土間床等の面積, m2
    # 浴室の床面積, m2
    # 浴室の土間床等の外周部の長さ, m
    a_d_ef_bath, a_d_f_bath, l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270, l_base_bath_inside \
        = get_bath(house_type, floor_ins_type, bath_ins_type, l_bath_ms, l_bath_os)

    # 各階の形状係数
    # 外皮の面積の合計が定義されていない場合はデフォルト値を使用する。
    # 外皮の面積の合計が定義されている場合は、そこから逆算して形状係数を求める。
    if a_d_env is None:
        f_s = f_s_default
    else:
        f_s = get_f_s(
            house_type, floor_ins_type, bath_ins_type,
            a_d_env, a_f, h, h_base_other, h_base_bath, h_base_entrance, l_base_bath_000,
            l_base_bath_090, l_base_bath_180, l_base_bath_270, l_base_bath_inside, l_base_entrance_000,
            l_base_entrance_090, l_base_entrance_180, l_base_entrance_270, l_base_entrance_inside, f_s_default)

    # 各階の周長, m
    l_prm = get_l_prm(a_f, f_s)

    # 主方位の辺の長さ, m
    # その他方位の辺の長さ, m
    # 集合住宅の場合は修正する必要あり
    l_ms, l_os = get_l(house_type, a_f, l_prm)

    a_d_ef_other = get_a_d_ef_other(house_type, floor_ins_type, a_f, a_d_ef_bath, a_evp_ef_etrc)

    a_d_ef_total = get_a_d_ef_total(a_d_ef_bath, a_evp_ef_etrc, a_d_ef_other)

    a_d_f_other = get_a_d_f_other(
        house_type, floor_ins_type, bath_ins_type, a_evp_ef_etrc, a_d_ef_bath, a_f, a_evp_f_entrance, a_d_f_bath)

    a_d_f_total = get_a_d_f_total(a_evp_f_entrance, a_d_f_bath, a_d_f_other)

    l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270, l_base_other_inside = get_l_base_other(
        house_type, floor_ins_type, l_ms, l_os, l_base_entrance_000, l_base_entrance_090, l_base_entrance_180,
        l_base_entrance_270, l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270)

    l_base_total_000, l_base_total_090, l_base_total_180, l_base_total_270, l_base_total_inside = get_l_base_total(
        l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270,
        l_base_entrance_inside, l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270,
        l_base_bath_inside, l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270,
        l_base_other_inside)

    a_d_roof = get_a_d_roof(a_f)

    a_d_base_entrance_000, a_d_base_entrance_090, a_d_base_entrance_180, a_d_base_entrance_270,\
        a_d_base_entrance_inside = get_a_d_base_entrance(
            l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270, l_base_entrance_inside,
            h_base_entrance)

    a_d_base_bath_000, a_d_base_bath_090, a_d_base_bath_180, a_d_base_bath_270,\
        a_d_base_bath_inside = get_a_d_base_bath(
            l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270, l_base_bath_inside, h_base_bath)

    a_d_base_other_000, a_d_base_other_090, a_d_base_other_180, a_d_base_other_270,\
        a_d_base_other_inside = get_a_d_base_other(
            l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270, h_base_other)

    a_d_base_total_000, a_d_base_total_090, a_d_base_total_180, a_d_base_total_270,\
        a_d_base_total_inside = get_a_d_base_total(
            a_d_base_entrance_000, a_d_base_entrance_090, a_d_base_entrance_180, a_d_base_entrance_270,
            a_d_base_entrance_inside, a_d_base_bath_000, a_d_base_bath_090, a_d_base_bath_180, a_d_base_bath_270,
            a_d_base_bath_inside, a_d_base_other_000, a_d_base_other_090, a_d_base_other_180, a_d_base_other_270,
            a_d_base_other_inside)

    a_d_srf_000, a_d_srf_090, a_d_srf_180, a_d_srf_270 = get_a_d_srf(l_ms, l_os, h)

    a_d_env_not_base = get_a_d_env_not_base(a_d_ef_total, a_d_f_total, a_d_roof, a_d_srf_000, a_d_srf_090, a_d_srf_180, a_d_srf_270)

    a_d_env = get_a_d_env(
        a_d_base_total_000, a_d_base_total_090, a_d_base_total_180, a_d_base_total_270, a_d_base_total_inside,
        a_d_env_not_base)

    a_d_open = get_a_d_open(a_d_env_not_base, r_open)

    a_d_window_total = get_a_d_window_total(a_door_back_entrance, a_door_entrance, a_d_open)

    a_d_window_000, a_d_window_090, a_d_window_180, a_d_window_270 = get_a_d_window(
        a_d_window_total, r_window_000, r_window_090, r_window_180, r_window_270)

    a_d_door_000, a_d_door_090, a_d_door_180, a_d_door_270 = get_a_d_door(
        a_door_back_entrance, a_door_entrance, house_type)

    a_d_wall_000, a_d_wall_090, a_d_wall_180, a_d_wall_270 = get_a_d_wall(
        a_d_door_000, a_d_door_090, a_d_door_180, a_d_door_270, a_d_srf_000, a_d_srf_090, a_d_srf_180, a_d_srf_270,
        a_d_window_000, a_d_window_090, a_d_window_180, a_d_window_270)

    return mh
    """
           dict(
        a_f=a_f,  # 各階の床面積, m2
        a_env=round_num(a_d_env, 2),  # 外皮の部位の面積の合計, m2
        a_f_total=round_num(a_f_total, 2),  # 床面積の合計, m2
        a_roof=round_num(a_d_roof, 2),  # 屋根又は天井の面積, m2
        a_wall_000=round_num(a_d_wall_000, 2),  # 主開口方位から時計回りに0度の方向に面した壁の面積, m2
        a_wall_090=round_num(a_d_wall_090, 2),  # 主開口方位から時計回りに90度の方向に面した壁の面積, m2
        a_wall_180=round_num(a_d_wall_180, 2),  # 主開口方位から時計回りに180度の方向に面した壁の面積, m2
        a_wall_270=round_num(a_d_wall_270, 2),  # 主開口方位から時計回りに270度の方向に面した壁の面積, m2
        a_door_000=round_num(a_d_door_000, 2),
        a_door_090=round_num(a_d_door_090, 2),
        a_door_180=round_num(a_d_door_180, 2),
        a_door_270=round_num(a_d_door_270, 2),
        a_window_000=round_num(a_d_window_000, 2),
        a_window_090=round_num(a_d_window_090, 2),
        a_window_180=round_num(a_d_window_180, 2),
        a_window_270=round_num(a_d_window_270, 2),
        a_evp_f_entrance=round_num(a_evp_f_entrance, 2),
        a_d_f_bath=round_num(a_d_f_bath, 2),
        a_d_f_other=round_num(a_d_f_other, 2),
        a_d_f_total=round_num(a_d_f_total, 2),
    )
"""


if __name__ == '__main__':

    result1 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='base', a_d_env=266.10)
    result2 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='floor', a_d_env=266.10)
    result3 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='not_exist', a_d_env=266.10)
    result4 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='base', a_d_env=237.03)
    result5 = calc_area(house_type='attached', a_f_total=70.00, r_open=0.052, a_d_env=264.36)
    result6 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='base')
    result7 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='floor')
    result8 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='not_exist')
    result9 = calc_area(house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='base')
    result10 = calc_area(house_type='attached', a_f_total=70.00, r_open=0.052)

    print(result1)
    print(result2)
    print(result3)
    print(result4)
    print(result5)
    print(result6)
    print(result7)
    print(result8)
    print(result9)
    print(result10)
