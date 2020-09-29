import numpy as np
from collections import namedtuple
from typing import List, Dict, Tuple

from heat_load_calc.convert import factor_f
from heat_load_calc.external.factor_h import get_h as get_factor_h  # 温度差係数

from heat_load_calc.external import factor_nu

PartType = namedtuple('PartType', [
    'roof',
    'ceiling',
    'wall',
    'floor',
    'boundary_ceiling',
    'boundary_wall',
    'boundary_floor',
    'window',
    'door',
    'earthfloor_perimeter',
])


def get_u_psi(u_psi: PartType, key: str) -> float:
    """
    Args:
        u_psi: 各部位のU値またはψ値
        key: 部位の名称
    Returns:
        U値又はψ値, W/m2K or W/mK
    """

    return {
        'roof': u_psi.roof,
        'ceiling': u_psi.ceiling,
        'wall': u_psi.wall,
        'floor': u_psi.floor,
        'boundary_ceiling': u_psi.boundary_ceiling,
        'boundary_wall': u_psi.boundary_wall,
        'boundary_floor': u_psi.boundary_wall,
        'window': u_psi.window,
        'door': u_psi.door,
        'earthfloor_perimeter': u_psi.earthfloor_perimeter,
    }[key]


def get_a_evp_total(general_parts: Dict, windows: Dict, doors: Dict, earthfloor_centers: Dict) -> float:
    """
    Args:
        general_parts: 一般部位
        windows: 窓
        doors: ドア
        earthfloor_centers: 地盤中央部
    Returns:
        外皮の面積の合計, m2
    """

    d_area = []

    if general_parts is not None:
        d_area.extend(general_parts)

    if windows is not None:
        d_area.extend(windows)

    if doors is not None:
        d_area.extend(doors)

    if earthfloor_centers is not None:
        d_area.extend(earthfloor_centers)

    return sum(d['area'] for d in d_area)


def get_q(a_evp_total: float, u_a: float) -> float:
    """
    Args:
        a_evp_total: 外皮の面積の合計, m2
        u_a: UA値, W/m2K
    Returns:
        q値, W/K
    """

    return a_evp_total * u_a


def get_m_h(a_evp_total: float, eta_a_h: float) -> float:
    """
    Args:
        a_evp_total: 外皮の面積の合計, m2
        eta_a_h: ηAH値, %
    Returns:
        mh値, W/(W/m2)
    """

    return eta_a_h / 100 * a_evp_total


def get_m_c(a_evp_total: float, eta_a_c: float) -> float:
    """
    Args:
        a_evp_total: 外皮の面積の合計, m2
        eta_a_c: ηAc値, %
    Returns:
        mc値, W/(W/m2)
    """

    return eta_a_c / 100 * a_evp_total


def get_general_parts_type() -> List[str]:
    """
    Returns:
        一般部位の種類
    """

    return [
        'roof',
        'ceiling',
        'wall',
        'floor',
        'boundary_ceiling',
        'boundary_wall',
        'boundary_floor'
    ]


def get_q_std(region: int, general_parts: Dict, windows: Dict, doors: Dict, earthfloor_perimeters: Dict) -> Dict:
    """
    Args:
        region: 地域の区分
        general_parts: 一般部位
        windows: 窓
        doors: ドア
        earthfloor_perimeters: 地盤周辺部
    Returns:
        各部位の基準U値・ψ値に対するq値, W/K
    """

    def get_q_uah_std_in_general_parts(part_type):

        return sum([
            p['area'] * get_u_psi_std(region, p['general_part_type']) * get_factor_h(region, p['next_space'])
            for p in general_parts if p['general_part_type'] == part_type
        ])

    general_parts_type = get_general_parts_type()

    q_uah_std = {pt: get_q_uah_std_in_general_parts(pt) for pt in general_parts_type}

    q_uah_std['window'] = sum([
        p['area'] * get_u_psi_std(region, 'window') * get_factor_h(region, p['next_space']) for p in windows
    ])

    q_uah_std['door'] = sum([
        p['area'] * get_u_psi_std(region, 'door') * get_factor_h(region, p['next_space']) for p in doors
    ])

    q_uah_std['earthfloor_perimeter'] = sum([
        p['length'] * get_u_psi_std(region, 'earthfloor_perimeter') * get_factor_h(region, p['next_space'])
        for p in earthfloor_perimeters
    ])

    return q_uah_std


def get_u_psi_std(region: int, part_type: str) -> float:
    """
    Args:
        region: 地域の区分
        part_type: 部位の種類
    Returns:
        基準U値又はψ値, W/m2K or W/mK
    """

    return {
        'roof': {1: 0.17, 2: 0.17, 3: 0.24, 4: 0.24, 5: 0.24, 6: 0.24, 7: 0.24, 8: 0.24},
        'ceiling': {1: 0.17, 2: 0.17, 3: 0.24, 4: 0.24, 5: 0.24, 6: 0.24, 7: 0.24, 8: 0.24},
        'wall': {1: 0.35, 2: 0.35, 3: 0.53, 4: 0.53, 5: 0.53, 6: 0.53, 7: 0.53, 8: 4.10},
        'floor': {1: 0.34, 2: 0.34, 3: 0.34, 4: 0.48, 5: 0.48, 6: 0.48, 7: 0.48, 8: 3.52},
        'boundary_ceiling': {1: 0.17, 2: 0.17, 3: 0.24, 4: 0.24, 5: 0.24, 6: 0.24, 7: 0.24, 8: 0.24},
        'boundary_wall': {1: 0.35, 2: 0.35, 3: 0.53, 4: 0.53, 5: 0.53, 6: 0.53, 7: 0.53, 8: 4.10},
        'boundary_floor': {1: 0.34, 2: 0.34, 3: 0.34, 4: 0.48, 5: 0.48, 6: 0.48, 7: 0.48, 8: 3.52},
        'window': {1: 2.33, 2: 2.33, 3: 3.49, 4: 4.65, 5: 4.65, 6: 4.65, 7: 4.65, 8: 6.51},
        'door': {1: 2.33, 2: 2.33, 3: 3.49, 4: 4.65, 5: 4.65, 6: 4.65, 7: 4.65, 8: 6.51},
        'earthfloor_perimeter': {1: 0.53, 2: 0.53, 3: 0.53, 4: 0.76, 5: 0.76, 6: 0.76, 7: 0.76, 8: 1.80}
    }[part_type][region]


def get_u_psi_max(part_type):    # 部位別の熱貫流率の上限値, W/m2 K
    """
    Args:
        part_type: 部位の種類
    Returns:
        各部位のU値又はψ値の最高値, W/m2K or W/mK
    """

    return {
        'roof': 1/(0.09+0.0095/0.22+0.04),
        'ceiling': 1/(0.09+0.0095/0.22+0.09),
        'wall': 1/(0.11+0.0095/0.22+0.04),
        'floor': 1/(0.15+0.012/0.16+0.04),
        'boundary_ceiling': 1/(0.09+0.0095/0.22+0.09),
        'boundary_wall': 1/(0.11+0.0095/0.22+0.11),
        'boundary_floor': 1/(0.15+0.012/0.16+0.15),
        'window': 6.51,
        'door': 6.51,
        'earthfloor_perimeter': 100.0
    }[part_type]


def get_f_u_psi_max_each_part(region: int) -> Dict[str, float]:
    """
    Args:
        region: 地域の区分
    Returns:
        部位の種類ごとの標準U値に乗じる係数の最大値（ = 最大U値 / 標準U値 ）
    """

    part_type_all = PartType._fields

    return {p: get_u_psi_max(p) / get_u_psi_std(region, p) for p in part_type_all}


def get_f_u_psi(q_std: Dict[str, float], f_u_psi_max_each_part: Dict[str, float], q: float) -> Dict[str, float]:
    """
    Args:
        q_std: 各部位の標準U値・ψ値に対するq値, W/K
        f_u_psi_max_each_part: 各部位の標準U値・ψ値に対するU値・ψ値の最大値の比
        q: q値, W/K
    Returns:
        各部位の各部位の標準U値に対するU値の比
    """

    def get_remaining_f(remaining_q: float, f_u_base: float, remaining_part: List[str]) -> Dict[str, float]:

        # 部位の種類が残っていなかったら空の辞書を返す。
        # すべての部位において最大値をとってもなおq値を満たさなかった場合、これが該当する。
        if not remaining_part:
            return {}

        # 残っている部位の種類のうちで、最も小さい（上限に引っかかる）f_u_max 値を取得する。
        f_u_max_subtractable = min(f_u_psi_max_each_part[p] for p in remaining_part)

        # 上記の f_u_max 値に該当する部位の種類の名前を取得する。
        f_u_max_subtractable_names = [p for p in remaining_part if f_u_psi_max_each_part[p] == f_u_max_subtractable]

        # 上記の f_u_max 値の場合の q 値を計算する。
        q_max_subtractable = sum(q_std[p] for p in remaining_part) * (f_u_max_subtractable - f_u_base)

        # 残っている q 値よりも、 最も小さい（上限に引っかかる）f_u_max 値をとった時のq値の方が大きい場合。
        # この場合は、最も小さい f_u_max 値よりも小さい値で、q値を満たすことができる。
        # 残りのq値から、残っている部位の種類の q_uah の合計で除して、f_u 値を算出する。
        # その際、これまで削除してきた q 値分に該当する f_u 値の分は足してやらないといけない。
        # 計算された f_u 値を現在残っている部位の種類全てに適用させて、この計算を終了する。
        if q_max_subtractable > remaining_q:
            v = f_u_base + remaining_q / sum(q_std[p] for p in remaining_part)
            return {p: v for p in remaining_part}

        # 残っている q 値の方が、 最も小さい（上限に引っかかる）f_u_max 値をとった時のq値よりも大きい場合。
        # f_u 値の上限に達した部位の種類はリストから除外する。
        # f_u_base を今回計算した f_u_max 値に引き上げる。
        else:
            remaining_q = remaining_q - q_max_subtractable
            [remaining_part.remove(n) for n in f_u_max_subtractable_names]
            f_u_base = f_u_max_subtractable

            # 今回上限に引っかかってしまった部位の種類
            dict1 = {name: f_u_max_subtractable for name in f_u_max_subtractable_names}

            # 今回上限に引っかからなかった部位の種類
            # 再帰計算を行い、さらに残りの部位の種類の f_u 値を決定する。
            dict2 = get_remaining_f(remaining_q, f_u_base, remaining_part)

            return dict(**dict1, **dict2)

    part_type_all = list(PartType._fields)

    return get_remaining_f(remaining_q=q, f_u_base=0.0, remaining_part=part_type_all.copy())


def get_u_psi_value(region: int, f_u: Dict[str, float]) -> Dict[str, float]:
    """
    Args:
        region: 地域の区分
        part_type_all: 各部位の名称（リスト）
        f_u: 各部位の標準U値に対するU値の比
    Returns:
        各部位のU値, W/m2K
    """

    return {pt: get_u_psi_std(region, pt) * f_u[pt] for pt in list(PartType._fields)}


def get_m_opq(region: int, u_psi_value: Dict[str, float], general_parts: Dict, doors: Dict) -> (float, float):
    """
    Args:
        region: 地域の区分
        u_psi_value: 各部位のU値またはψ値, W/m2K or W/mK
        general_parts: 一般部位
        doors: ドア
    Returns:
        不透明部位のm値の合計, W/K （暖房期・冷房期）
    """

    general_parts_type = get_general_parts_type()

    def get_m_opq_h_in_general_parts(pt):
        return sum([
            p['area'] * 0.034 * u_psi_value[pt] * factor_nu.get_nu(region, 'heating', p['direction'])
            for p in general_parts if (p['general_part_type'] == pt and p['next_space'] == 'outdoor')
        ])

    def get_m_opq_c_in_general_parts(pt):
        return sum([
            p['area'] * 0.034 * u_psi_value[pt] * factor_nu.get_nu(region, 'cooling', p['direction'])
            for p in general_parts if (p['general_part_type'] == pt and p['next_space'] == 'outdoor')
        ])

    m_opq_h_general_part = sum(get_m_opq_h_in_general_parts(pt) for pt in general_parts_type)
    m_opq_c_general_part = sum(get_m_opq_c_in_general_parts(pt) for pt in general_parts_type)

    m_opq_h_door = sum([
        p['area'] * 0.034 * u_psi_value['door'] * factor_nu.get_nu(region, 'heating', p['direction']) for p in doors
    ])
    m_opq_c_door = sum([
        p['area'] * 0.034 * u_psi_value['door'] * factor_nu.get_nu(region, 'cooling', p['direction']) for p in doors
    ])

    m_opq_h = m_opq_h_general_part + m_opq_h_door
    m_opq_c = m_opq_c_general_part + m_opq_c_door

    return m_opq_h, m_opq_c


def get_eta_d_each(
        region: int, m_h: float, m_c: float, m_h_opq: float, m_c_opq: float, windows: Dict, sunshade: factor_f.Sunshade) -> Tuple[float, float]:
    """
    Args:
        region: 地域の区分
        m_h: m_h値, W/(W/m2)
        m_c: m_c値, W/(W/m2)
        m_h_opq: 不透明部位のm_h値, W/(W/m2)
        m_c_opq: 不透明部位のm_c値, W/(W/m2)
        windows: 窓
        sunshade: 窓まわりの日除けの形状
    Returns:
        η_d,h・η_d,c 値, (W/m2)/(W/m2)
    """

    sum_a_f_nu_h = sum(
        p['area'] * factor_f.get_f(season='heating', region=region, direction=p['direction'], sunshade=sunshade)
        * factor_nu.get_nu(region=region, season='heating', direction=p['direction']) for p in windows
    )

    sum_a_f_nu_c = sum(
        p['area'] * factor_f.get_f(season='cooling', region=region, direction=p['direction'], sunshade=sunshade)
        * factor_nu.get_nu(region=region, season='cooling', direction=p['direction']) for p in windows
    )

    eta_d_h = np.clip((m_h - m_h_opq) / sum_a_f_nu_h, 0.0, 0.88)
    eta_d_c = np.clip((m_c - m_c_opq) / sum_a_f_nu_c, 0.0, 0.88)

    return eta_d_h, eta_d_c


def get_eta_d(region: int, eta_d_h: float, eta_d_c: float) -> float:
    """
    Args:
        region: 地域の区分
        eta_d_h: 暖房期のηd値, (W/m2)/(W/m2)
        eta_d_c: 冷房期のηd値, (W/m2)/(W/m2)
    Returns:
        ηd 値, (W/m2)/(W/m2)
    """

    if region == 8:
        return  eta_d_c
    else:
        # ここは将来的に変更しないといけない。
        # 暖房と冷房におけるデグリーデーで重み付け平均するなど
        return (eta_d_h + eta_d_c) / 2


def calc_parts_spec(
        region: int, house_no_spec: Dict,
        u_a_target: float, eta_a_h_target: float, eta_a_c_target: float, sunshade: factor_f.Sunshade
) -> Tuple[PartType, float, float, float]:
    """
    Args:
        region: 地域の区分
        house_no_spec: 住宅辞書
        u_a_target: 目標とするUA値, W/k
        eta_a_h_target: 目標とするηAH値, W/(W/m2)
        eta_a_c_target: 目標とするηAC値, W/(W/m2)
    Returns:
        次の2変数
            (1) 部位の種類ごとのU値, W/m2K,
            (2) 透明な開口部のηd値, (W/m2)/(W/m2)
    """

    general_parts = house_no_spec['general_parts']
    windows = house_no_spec['windows']
    doors = house_no_spec['doors']
    earthfloor_perimeters = house_no_spec['earthfloor_perimeters']
    earthfloor_centers = house_no_spec['earthfloor_centers']

    # 外皮の面積の合計, m2
    a_evp_total = get_a_evp_total(general_parts, windows, doors, earthfloor_centers)

    # q値, W/K
    q = get_q(a_evp_total, u_a_target)

    # m値, W/(W/m2)
    m_h = get_m_h(a_evp_total, eta_a_h_target)
    m_c = get_m_c(a_evp_total, eta_a_c_target)

    # 各部位の基準U値・ψ値に対するq値, W/K
    q_std = get_q_std(region, general_parts, windows, doors, earthfloor_perimeters)

    # 部位の種類ごとの標準U値・ψ値に乗じる係数の最大値（ = 最大値 / 標準値 ）
    f_u_psi_max_each_part = get_f_u_psi_max_each_part(region)

    # q値を満たす部位の種類ごとのf_u値またはf_psi値（ = 標準U値・ψ値に乗じる係数）
    f_u_psi = get_f_u_psi(q_std=q_std, f_u_psi_max_each_part=f_u_psi_max_each_part, q=q)

    # 各部位の種類のU値またはψ値, W/m2K or W/mK
    u_psi_value = get_u_psi_value(region, f_u_psi)

    # 不透明部位のm値, W/(W/m2)
    m_h_opq, m_c_opq = get_m_opq(region, u_psi_value, general_parts, doors)

    # ηdの算出
    eta_d_h, eta_d_c = get_eta_d_each(region, m_h, m_c, m_h_opq, m_c_opq, windows, sunshade)

    # ηd値（平均化）
    eta_d = get_eta_d(region=region, eta_d_h=eta_d_h, eta_d_c=eta_d_c)

    u_psi = PartType(
        roof=u_psi_value['roof'],
        ceiling=u_psi_value['ceiling'],
        wall=u_psi_value['wall'],
        floor=u_psi_value['floor'],
        boundary_ceiling=u_psi_value['boundary_ceiling'],
        boundary_wall=u_psi_value['boundary_wall'],
        boundary_floor=u_psi_value['boundary_floor'],
        window=u_psi_value['window'],
        door= u_psi_value['door'],
        earthfloor_perimeter=u_psi_value['earthfloor_perimeter']
    )

    return u_psi, eta_d, eta_d_h, eta_d_c





