"""
与えられた外皮仕様からUA値・ηA値を計算するモジュール。
"""

from typing import List

from heat_load_calc.convert.ees_house import *
from heat_load_calc.convert.ees_house import GeneralPart, Window, Door, EarthfloorPerimeter, EarthfloorCenter


def check_u_a_and_eta_a(region, model_house_envelope):

    gps: List[GeneralPart] = GeneralPart.make_general_parts(ds=model_house_envelope['general_parts'])
    ws: List[Window] = Window.make_windows(ds=model_house_envelope['windows'])
    ds: List[Door] = Door.make_doors(ds=model_house_envelope['doors'])
    eps: List[EarthfloorPerimeter] = EarthfloorPerimeter.make_earthfloor_perimeters(ds=model_house_envelope['earthfloor_perimeters'])
    ecs: List[EarthfloorCenter] = EarthfloorCenter.make_earthfloor_centers(ds=model_house_envelope['earthfloor_centers'])

    # 外皮の面積の合計, m2
    a_evp_total = get_envelope_total_area(gps=gps, ws=ws, ds=ds, ecs=ecs)

    # q値, W/K
    q_total = get_q(gps=gps, ws=ws, ds=ds, eps=eps, region=region)

    # UA値, W/m2K
    u_a = q_total / a_evp_total

    if region != 8:

        m_h = get_m(gps=gps, ws=ws, ds=ds, region=region, season='heating')
        eta_a_h = m_h / a_evp_total * 100.0

    else:

        eta_a_h = None

    m_c = get_m(gps=gps, ws=ws, ds=ds, region=region, season='cooling')

    eta_a_c = m_c / a_evp_total * 100

    return u_a, eta_a_h, eta_a_c


def get_envelope_total_area(gps: List[IArea], ws: List[IArea], ds: List[IArea], ecs: List[IArea]) -> float:
    """
    各部位の面積を合計する。
    Args:
        gps: 一般部位
        ws: 透明な開口部
        ds: 不透明な開口部
        ecs: 土間床中央部

    Returns:
        外皮の面積の合計, m2
    """

    return sum(structure.area for structure in gps + ws + ds + ecs)


def get_q(gps: List[IGetQ], ws: List[IGetQ], ds: List[IGetQ], eps: List[IGetQ], region: int) -> float:
    """
    各部位のq値（W/K)の合計を求める。
    Args:
        gps: 一般部位
        ws: 透明な開口部
        ds: 不透明な開口部
        eps: 土間床周辺部
        region: 地域の区分
    Returns:
        q値, W/K
    """

    return sum(s.get_q(region=region) for s in gps + ws + ds + eps)


def get_m(gps: List[IGetM], ws: List[IGetM], ds: List[IGetM], region: int, season: str) -> float:
    """
    各部位のm値(W/(W/m2))の合計を求める。
    Args:
        gps: 一般部位
        ws: 透明な開口部
        ds: 不透明な開口部
        region: 地域の区分
        season: 期間
    Returns:
        m値, W/(W/m2)
    """

    return sum(s.get_m(region=region, season=season) for s in gps + ws + ds)
