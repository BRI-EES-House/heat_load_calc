import numpy as np
from collections import namedtuple
from typing import List, Dict

from heat_load_calc.convert.ees_house import GeneralPartType
from heat_load_calc.convert.ees_house import IArea
from heat_load_calc.convert.ees_house import GeneralPartNoSpec
from heat_load_calc.convert.ees_house import WindowNoSpec
from heat_load_calc.convert.ees_house import DoorNoSpec
from heat_load_calc.convert.ees_house import EarthfloorPerimeterNoSpec
from heat_load_calc.convert.ees_house import EarthfloorCenterNoSpec

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


def get_m_opq(
        region: int,
        u_psi_value: Dict[str, float],
        gps: List[GeneralPartNoSpec],
        ds: List[DoorNoSpec]
) -> (float, float):
    """
    Args:
        region: 地域の区分
        u_psi_value: 各部位のU値またはψ値, W/m2K or W/mK
        gps: GeneralPartNoSpec クラスのリスト
        ds: DoorNoSpec クラスのリスト
    Returns:
        不透明部位のm値の合計, W/K （暖房期・冷房期）
    """

    m_opq_h_general_part = sum(
        s.area * 0.034 * u_psi_value[s.general_part_type.value] * s.get_nu(region=region, season='heating')
        for s in gps if s.next_space == 'outdoor'
    )

    m_opq_c_general_part = sum(
        s.area * 0.034 * u_psi_value[s.general_part_type.value] * s.get_nu(region=region, season='cooling')
        for s in gps if s.next_space == 'outdoor'
    )

    m_opq_h_door = sum([s.area * 0.034 * u_psi_value['door'] * s.get_nu(region=region, season='heating') for s in ds])

    m_opq_c_door = sum([s.area * 0.034 * u_psi_value['door'] * s.get_nu(region=region, season='cooling') for s in ds])

    m_opq_h = m_opq_h_general_part + m_opq_h_door
    m_opq_c = m_opq_c_general_part + m_opq_c_door

    return m_opq_h, m_opq_c


def get_eta_d_each(
        region: int, m_h: float, m_c: float, m_h_opq: float, m_c_opq: float, ws: List[WindowNoSpec]
) -> (float, float):
    """
    Args:
        region: 地域の区分
        m_h: m_h値, W/(W/m2)
        m_c: m_c値, W/(W/m2)
        m_h_opq: 不透明部位のm_h値, W/(W/m2)
        m_c_opq: 不透明部位のm_c値, W/(W/m2)
        ws: WindowNoSpec クラスのリスト
    Returns:
        η_d,h・η_d,c 値, (W/m2)/(W/m2)
    """

    sum_a_f_nu_h = sum(
        s.area * s.get_f(region=region, season='heating') * s.get_nu(region=region, season='heating') for s in ws
    )

    sum_a_f_nu_c = sum(
        s.area * s.get_f(region=region, season='cooling') * s.get_nu(region=region, season='cooling') for s in ws
    )

    eta_d_h = np.clip((m_h - m_h_opq) / sum_a_f_nu_h, 0.0, 0.88)
    eta_d_c = np.clip((m_c - m_c_opq) / sum_a_f_nu_c, 0.0, 0.88)

    return float(eta_d_h), float(eta_d_c)


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
        region: int,
        u_a_target: float, eta_a_h_target: float, eta_a_c_target: float,
        gps: List[GeneralPartNoSpec],
        ds: List[DoorNoSpec],
        ws: List[WindowNoSpec],
        eps: List[EarthfloorPerimeterNoSpec],
        ecs: List[EarthfloorCenterNoSpec]
) -> (PartType, float, float, float):
    """
    Args:
        region: 地域の区分
        u_a_target: 目標とするUA値, W/m2k
        eta_a_h_target: 目標とするηAH値, (W/m2)/(W/m2)
        eta_a_c_target: 目標とするηAC値, (W/m2)/(W/m2)
        gps: 一般部位（仕様なし）のリスト
        ds: 大部分がガラスで構成されないドア等の開口部（仕様なし）のリスト
        ws: 大部分がガラスで構成される窓等の開口部（仕様なし）のリスト
        eps: 土間床等の外周部のリスト
        ecs: 土間床等の中心部のリスト
    Returns:
        次の2変数
            (1) 部位の種類ごとのU値, W/m2K,
            (2) 透明な開口部のηd値, (W/m2)/(W/m2)
    """

    # 外皮の面積の合計, m2
    a_evp_total = _get_a_evp_total(gps=gps, ws=ws, ds=ds, ecs=ecs)

    # q値, W/K
    q = _get_q(a_evp_total=a_evp_total, u_a=u_a_target)

    # m値, W/(W/m2)
    m_h = _get_m_h(a_evp_total=a_evp_total, eta_a_h=eta_a_h_target)
    m_c = _get_m_c(a_evp_total=a_evp_total, eta_a_c=eta_a_c_target)

    # 各部位の基準U値・ψ値に対するq値, W/K
    q_std = _get_q_std(region=region, gps=gps, ws=ws, ds=ds, eps=eps)

    # 部位の種類ごとの標準U値・ψ値に乗じる係数の最大値（ = 最大値 / 標準値 ）
    f_u_psi_max_each_part = get_f_u_psi_max_each_part(region=region)

    # q値を満たす部位の種類ごとのf_u値またはf_psi値（ = 標準U値・ψ値に乗じる係数）
    f_u_psi = get_f_u_psi(q_std=q_std, f_u_psi_max_each_part=f_u_psi_max_each_part, q=q)

    # 各部位の種類のU値またはψ値, W/m2K or W/mK
    u_psi_value = get_u_psi_value(region, f_u_psi)

    # 不透明部位のm値, W/(W/m2)
    m_h_opq, m_c_opq = get_m_opq(region, u_psi_value, gps=gps, ds=ds)

    # ηdの算出
    eta_d_h, eta_d_c = get_eta_d_each(region, m_h, m_c, m_h_opq, m_c_opq, ws=ws)

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
        door=u_psi_value['door'],
        earthfloor_perimeter=u_psi_value['earthfloor_perimeter']
    )

    return u_psi, eta_d, eta_d_h, eta_d_c


def _get_a_evp_total(gps: List[IArea], ws: List[IArea], ds: List[IArea], ecs: List[IArea]) -> float:

    return sum(s.area for s in gps + ws + ds + ecs)


def _get_q(a_evp_total: float, u_a: float) -> float:
    """
    Args:
        a_evp_total: 外皮の面積の合計, m2
        u_a: UA値, W/m2K
    Returns:
        q値, W/K
    """

    return a_evp_total * u_a


def _get_m_h(a_evp_total: float, eta_a_h: float) -> float:
    """
    Args:
        a_evp_total: 外皮の面積の合計, m2
        eta_a_h: ηAH値, %
    Returns:
        mh値, W/(W/m2)
    """

    return eta_a_h / 100 * a_evp_total


def _get_m_c(a_evp_total: float, eta_a_c: float) -> float:
    """
    Args:
        a_evp_total: 外皮の面積の合計, m2
        eta_a_c: ηAc値, %
    Returns:
        mc値, W/(W/m2)
    """

    return eta_a_c / 100 * a_evp_total


def _get_q_std(
        region: int,
        gps: List[GeneralPartNoSpec],
        ws: List[WindowNoSpec],
        ds: List[DoorNoSpec],
        eps: List[EarthfloorPerimeterNoSpec]
) -> Dict:
    """
    Args:
        region: 地域の区分
        gps: GeneralPartNoSpec クラスのリスト
        ws: WindowNoSpec クラスのリスト
        ds: DoorNoSpec クラスのリスト
        eps: EarthfloorPerimeterNoSpec クラスのリスト
    Returns:
        各部位の基準U値・ψ値に対するq値, W/K
    """

    q_uah_std = {}

    q_uah_std['roof'] = sum([
        s.area * get_u_psi_std(region=region, part_type='roof') * s.get_h(region=region)
        for s in gps if s.general_part_type == GeneralPartType.ROOF
    ])

    q_uah_std['ceiling'] = sum([
        s.area * get_u_psi_std(region=region, part_type='ceiling') * s.get_h(region=region)
        for s in gps if s.general_part_type == GeneralPartType.CEILING
    ])

    q_uah_std['wall'] = sum([
        s.area * get_u_psi_std(region=region, part_type='wall') * s.get_h(region=region)
        for s in gps if s.general_part_type == GeneralPartType.WALL
    ])

    q_uah_std['floor'] = sum([
        s.area * get_u_psi_std(region=region, part_type='floor') * s.get_h(region=region)
        for s in gps if s.general_part_type == GeneralPartType.FLOOR
    ])

    q_uah_std['boundary_ceiling'] = sum([
        s.area * get_u_psi_std(region=region, part_type='boundary_ceiling') * s.get_h(region=region)
        for s in gps if s.general_part_type == GeneralPartType.UPWARD_BOUNDARY_FLOOR
    ])

    q_uah_std['boundary_wall'] = sum([
        s.area * get_u_psi_std(region=region, part_type='boundary_wall') * s.get_h(region=region)
        for s in gps if s.general_part_type == GeneralPartType.BOUNDARY_WALL
    ])

    q_uah_std['boundary_floor'] = sum([
        s.area * get_u_psi_std(region=region, part_type='boundary_floor') * s.get_h(region=region)
        for s in gps if s.general_part_type == GeneralPartType.DOWNWARD_BOUNDARY_FLOOR
    ])

    q_uah_std['window'] = sum([
        s.area * get_u_psi_std(region=region, part_type='window') * s.get_h(region=region) for s in ws
    ])

    q_uah_std['door'] = sum([
        s.area * get_u_psi_std(region=region, part_type='door') * s.get_h(region=region) for s in ds
    ])

    q_uah_std['earthfloor_perimeter'] = sum([
        s.length * get_u_psi_std(region=region, part_type='earthfloor_perimeter') * s.get_h(region=region)
        for s in eps
    ])

    return q_uah_std




