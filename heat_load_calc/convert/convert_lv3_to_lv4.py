from typing import Dict, Tuple, List
import copy

from heat_load_calc.convert.ees_house import UpperArealEnvelope
from heat_load_calc.convert.ees_house import GeneralPart
from heat_load_calc.convert.ees_house import Window
from heat_load_calc.convert.ees_house import Door
from heat_load_calc.convert.ees_house import Heatbridge
from heat_load_calc.convert.ees_house import EarthfloorPerimeter
from heat_load_calc.convert.ees_house import EarthfloorCenter
from heat_load_calc.convert.ees_house import InnerFloor
from heat_load_calc.convert.ees_house import InnerWall


def get_inner_floor_spec() -> Dict:
    """
    Returns:
        室内床
    """

    return {
        'layers': [
            {
                'name': 'plywood',
                'thermal_resistance_input_method': 'conductivity',
                'thermal_conductivity': 0.16,
                'volumetric_specific_heat': 720.0,
                'thickness': 0.024,
            }
        ]
    }


def get_downward_envelope_total_area(
        gps: List[UpperArealEnvelope],
        ws: List[UpperArealEnvelope],
        ds: List[UpperArealEnvelope]
) -> Tuple[float, float, float]:
    """
    Args:
        gps:
        ws:
        ds:
    Returns:
        以下の3つの変数
            (1) 主たる居室に接する方位が下面である外皮の部位の面積の合計, m2
            (2) その他の居室に接する方位が下面である外皮の部位の面積の合計, m2
            (3) 非居室に接する方位が下面である外皮の部位の面積の合計, m2
    """

    ss = gps + ws + ds

    a_evlp_down_mr = sum([
        s.area for s in ss
        if s.space_type == 'main_occupant_room' and (s.direction == 'bottom' or s.direction == 'downward')
    ])

    a_evlp_down_or = sum([
        s.area for s in ss
        if s.space_type == 'other_occupant_room' and (s.direction == 'bottom' or s.direction == 'downward')
    ])

    a_evlp_down_nr = sum([
        s.area for s in ss
        if s.space_type == 'non_occupant_room' and (s.direction == 'bottom' or s.direction == 'downward')
    ])

    return a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr


def get_earthfloor_total_area(ecs: List[EarthfloorCenter]) -> (float, float, float, float):
    """
    Args:
        ecs:
    Returns:
        以下の4つの変数
            (1) 主たる居室に接する土間床等の中心部の面積の合計, m2
            (2) その他の居室に接する土間床等の中心部の面積の合計, m2
            (3) 非居室に接する土間床等の中心部の面積の合計, m2
            (4) 床下空間に接する土間床等の中心部の面積の合計, m2
    """

    a_ef_mr = sum([s.area for s in ecs if s.space_type == 'main_occupant_room'])
    a_ef_or = sum([s.area for s in ecs if s.space_type == 'other_occupant_room'])
    a_ef_nr = sum([s.area for s in ecs if s.space_type == 'non_occupant_room'])
    a_ef_uf = sum([s.area for s in ecs if s.space_type == 'underfloor'])

    return a_ef_mr, a_ef_or, a_ef_nr, a_ef_uf


def get_inner_floor_total_area(
        a_a: float, a_mr: float, a_or: float,
        a_evlp_down_mr: float, a_evlp_down_or: float, a_evlp_down_nr: float,
        a_ef_mr: float, a_ef_or: float, a_ef_nr: float) -> Tuple[float, float, float]:
    """
    Args:
        a_a: 床面積の合計, m2
        a_mr: 主たる居室の床面積, m2
        a_or: その他の居室の床面積, m2
        a_evlp_down_mr: 主たる居室に接する方位が下面である外皮の部位の面積の合計, m2
        a_evlp_down_or: その他の居室に接する方位が下面である外皮の部位の面積の合計, m2
        a_evlp_down_nr: 非居室に接する方位が下面である外皮の部位の面積の合計, m2
        a_ef_mr: 主たる居室に接する土間床等の中心部の面積の合計, m2
        a_ef_or: その他の居室に接する土間床等の中心部の面積の合計, m2
        a_ef_nr: 非居室に接する土間床等の中心部の面積の合計, m2
    Returns:
        以下の3つの変数
            (1) 床上側が主たる居室に接する間仕切り床の面積の合計, m2
            (2) 床上側がその他の居室に接する間仕切り床の面積の合計, m2
            (3) 床上側が非居室に接する間仕切り床の面積の合計, m2
    """

    a_if_mr = max(0.0, a_mr - a_evlp_down_mr - a_ef_mr)
    a_if_or = max(0.0, a_or - a_evlp_down_or - a_ef_or)
    a_if_nr = max(0.0, a_a - a_mr - a_or - a_evlp_down_nr - a_ef_nr)

    return a_if_mr, a_if_or, a_if_nr


def get_inner_floor_over_underfloor_total_area(
        a_if_mr: float, a_if_or: float, a_if_nr: float, a_ef_uf: float) -> Tuple[float, float, float]:
    """
    Args:
        a_if_mr: 床上側が主たる居室に接する間仕切り床の面積の合計, m2
        a_if_or: 床上側がその他の居室に接する間仕切り床の面積の合計, m2
        a_if_nr: 床上側が非居室に接する間仕切り床の面積の合計, m2
        a_ef_uf: 床下空間に接する土間床等の中心部の面積の合計, m2
    Returns:
        以下の3つの変数
            (1) 床上側が主たる居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
            (2) 床上側がその他の居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
            (3) 床上側が非居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
    """

    if (a_if_mr + a_if_or + a_if_nr) > 0.0:
        a_if_mr_uf = a_ef_uf * a_if_mr / (a_if_mr + a_if_or + a_if_nr)
        a_if_or_uf = a_ef_uf * a_if_or / (a_if_mr + a_if_or + a_if_nr)
        a_if_nr_uf = a_ef_uf * a_if_nr / (a_if_mr + a_if_or + a_if_nr)
    else:
        a_if_mr_uf = 0.0
        a_if_or_uf = 0.0
        a_if_nr_uf = 0.0

    return a_if_mr_uf, a_if_or_uf, a_if_nr_uf


def get_inner_floor_between_rooms(
        a_mr, a_or, a_a, a_if_mr, a_if_or, a_if_nr, a_if_mr_uf, a_if_or_uf, a_if_nr_uf):
    """
    Args:
        a_mr: 主たる居室の床面積, m2
        a_or: その他の居室の床面積, m2
        a_a: 床面積の合計, m2
        a_if_mr: 床上側が主たる居室に接する間仕切り床の面積の合計, m2
        a_if_or:床上側がその他の居室に接する間仕切り床の面積の合計, m2
        a_if_nr:床上側が非居室に接する間仕切り床の面積の合計, m2
        a_if_mr_uf:床上側が主たる居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
        a_if_or_uf:床上側がその他の居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
        a_if_nr_uf:床上側が非居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2

    Returns:
        以下の6つの変数
            (1) 床上側が主たる居室に接し床下側がその他の居室に接する間仕切り床の面積の合計, m2
            (2) 床上側が主たる居室に接し床下側が非居室に接する間仕切り床の面積の合計, m2
            (3) 床上側がその他の居室に接し床下側が主たる居室に接する間仕切り床の面積の合計, m2
            (4) 床上側がその他の居室に接し床下側が非居室に接する間仕切り床の面積の合計, m2
            (5) 床上側が非居室に接し床下側が主たる居室に接する間仕切り床の面積の合計, m2
            (6) 床上側が非居室に接し床下側がその他の居室に接する間仕切り床の面積の合計, m2
    """

    a_nr = a_a - a_mr - a_or

    if a_mr <= 0.0:
        raise ValueError('主たる居室の面積に0又は負の値が指定されました。主たる居室は必ず0より大きい値を指定する必要があります。')

    a_if_mr_or_nr = max(0.0, a_if_mr - a_if_mr_uf)
    a_if_or_mr_nr = max(0.0, a_if_or - a_if_or_uf)
    a_if_nr_mr_or = max(0.0, a_if_nr - a_if_nr_uf)

    if a_or <= 0.0 and a_nr <= 0.0:
        a_if_mr_or = 0.0
        a_if_mr_nr = 0.0
        a_if_or_mr = 0.0
        a_if_or_nr = 0.0
        a_if_nr_mr = 0.0
        a_if_nr_or = 0.0
    elif a_or <= 0.0:
        a_if_mr_or = 0.0
        a_if_mr_nr = a_if_mr_or_nr
        a_if_or_mr = 0.0
        a_if_or_nr = 0.0
        a_if_nr_mr = a_if_nr_mr_or
        a_if_nr_or = 0.0
    elif a_nr <= 0.0:
        a_if_mr_or = a_if_mr_or_nr
        a_if_mr_nr = 0.0
        a_if_or_mr = a_if_or_mr_nr
        a_if_or_nr = 0.0
        a_if_nr_mr = 0.0
        a_if_nr_or = 0.0
    else:
        a_if_mr_or = a_if_mr_or_nr / 2
        a_if_mr_nr = a_if_mr_or_nr / 2
        a_if_or_mr = a_if_or_mr_nr / 2
        a_if_or_nr = a_if_or_mr_nr / 2
        a_if_nr_mr = a_if_nr_mr_or / 2
        a_if_nr_or = a_if_nr_mr_or / 2

    return a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or


def get_inner_wall_spec() -> Dict:
    """
    Returns:
        室内壁
    """

    return {
        'layers': [
            {
                'name': 'gpb',
                'thermal_resistance_input_method': 'conductivity',
                'thermal_conductivity': 0.22,
                'thickness': 0.0125,
                'volumetric_specific_heat': 830.0,
            },
            {
                'name': 'air_layer',
                'thermal_resistance_input_method': 'resistance',
                'thermal_resistance': 0.09,
                'volumetric_specific_heat': 0.0,
            },
            {
                'name': 'gpb',
                'thermal_resistance_input_method': 'conductivity',
                'thermal_conductivity': 0.22,
                'thickness': 0.0125,
                'volumetric_specific_heat': 830.0,
            },
        ]
    }


def get_horizontal_envelope_total_area(
        gps: List[UpperArealEnvelope],
        ws: List[UpperArealEnvelope],
        ds: List[UpperArealEnvelope]
) -> (float, float, float):
    """
    Args:
        gps:
        ws:
        ds:
    Returns:
        以下の3つの変数
            (1) 主たる居室に接する方位が水平である外皮の部位の面積の合計, m2
            (2) その他の居室に接する方位が水平である外皮の部位の面積の合計, m2
            (3) 非居室に接する方位が水平である外皮の部位の面積の合計, m2
    """

    ss = gps + ws + ds

    def is_horizontal(d):
        return d in ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'horizontal']

    a_ow_mr = sum([s.area for s in ss if s.space_type == 'main_occupant_room' and is_horizontal(s.direction)])
    a_ow_or = sum([s.area for s in ss if s.space_type == 'other_occupant_room' and is_horizontal(s.direction)])
    a_ow_nr = sum([s.area for s in ss if s.space_type == 'non_occupant_room' and is_horizontal(s.direction)])

    return a_ow_mr, a_ow_or, a_ow_nr


def get_inner_wall_total_area(a_mr, a_or, a_a, a_evlp_hzt_mr, a_evlp_hzt_or, a_evlp_hzt_nr):
    """
    Args:
        a_mr: 主たる居室の床面積, m2
        a_or: その他の居室の床面積, m2
        a_a: 床面積の合計, m2
        a_evlp_hzt_mr: 主たる居室に接する方位が水平である外皮の部位の面積の合計, m2
        a_evlp_hzt_or: その他の居室に接する方位が水平である外皮の部位の面積の合計, m2
        a_evlp_hzt_nr: 非居室に接する方位が水平である外皮の部位の面積の合計, m2
    Returns:
        以下の3つの変数
            (1) 主たる居室に接する間仕切り壁の面積の合計, m2
            (2) その他の居室に接する間仕切り壁の面積の合計, m2
            (3) 非居室に接する間仕切り壁の面積の合計, m2
    """
    r_iw_mr, r_iw_or, r_iw_nr = 1.2, 1.4, 1.4

    h_iw = 2.8

    a_iw_mr = max(0.0, 4 * r_iw_mr * h_iw * a_mr ** 0.5 - a_evlp_hzt_mr)
    a_iw_or = max(0.0, 4 * r_iw_or * h_iw * a_or ** 0.5 - a_evlp_hzt_or)
    a_iw_nr = max(0.0, 4 * r_iw_nr * h_iw * (a_a - a_mr - a_or) ** 0.5 - a_evlp_hzt_nr)

    return a_iw_mr, a_iw_or, a_iw_nr


def get_inner_wall_total_area_between_rooms(
        a_mr: float, a_or: float, a_a: float, a_iw_mr: float, a_iw_or: float, a_iw_nr: float
) -> Tuple[float, float, float]:
    """
    Args:
        a_mr: 主たる居室の床面積, m2
        a_or: その他の居室の床面積, m2
        a_a: 床面積の合計, m2
        a_iw_mr: 主たる居室に接する間仕切り壁の面積の合計, m2
        a_iw_or: その他の居室に接する間仕切り壁の面積の合計, m2
        a_iw_nr: 非居室に接する間仕切り壁の面積の合計, m2
    Returns:
        以下の3つの変数
            (1) 主たる居室とその他の居室に接する間仕切り壁の面積の合計, m2
            (2) 主たる居室と非居室に接する間仕切り壁の面積の合計, m2
            (3) その他の居室と非居室に接する間仕切り壁の面積の合計, m2
    """

    a_nr = a_a - a_mr - a_or

    if a_mr <= 0.0:
        raise ValueError('主たる居室の面積に0又は負の値が指定されました。主たる居室は必ず0より大きい値を指定する必要があります。')

    if a_or <= 0.0 and a_nr <= 0.0:
        a_iw_mr_or = 0.0
        a_iw_mr_nr = 0.0
        a_iw_or_nr = 0.0
    elif a_or <= 0.0:
        a_iw_mr_or = 0.0
        a_iw_mr_nr = (a_iw_mr + a_iw_nr) / 2
        a_iw_or_nr = 0.0
    elif a_nr <= 0.0:
        a_iw_mr_or = (a_iw_mr + a_iw_or) / 2
        a_iw_mr_nr = 0.0
        a_iw_or_nr = 0.0
    else:
        a_iw_mr_or = max(0.0, (a_iw_mr + a_iw_or - a_iw_nr) / 2)
        a_iw_mr_nr = max(0.0, (a_iw_mr + a_iw_nr - a_iw_or) / 2)
        a_iw_or_nr = max(0.0, (a_iw_or + a_iw_nr - a_iw_mr) / 2)

    return a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr


def make_inner_floors(
        common: Dict,
        gps: List[GeneralPart],
        ws: List[Window],
        ds: List[Door],
        ecs: List[EarthfloorCenter]
) -> List[InnerFloor]:
    """
    Args:
        common: 共通項目
        gps:
        ws:
        ds:
        ecs:
    Returns:
        室内床
    """

    a_mr = common['main_occupant_room_floor_area']
    a_or = common['other_occupant_room_floor_area']
    a_a = common['total_floor_area']

    # 主たる居室に接する方位が下面である外皮の部位の面積の合計, m2
    # その他の居室に接する方位が下面である外皮の部位の面積の合計, m2
    # 非居室に接する方位が下面である外皮の部位の面積の合計, m2
    a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr = get_downward_envelope_total_area(gps=gps, ws=ws, ds=ds)

    # 主たる居室に接する土間床等の中心部の面積の合計, m2
    # その他の居室に接する土間床等の中心部の面積の合計, m2
    # 非居室に接する土間床等の中心部の面積の合計, m2
    # 床下空間に接する土間床等の中心部の面積の合計, m2
    a_ef_mr, a_ef_or, a_ef_nr, a_ef_uf = get_earthfloor_total_area(ecs=ecs)

    # 床上側が主たる居室に接する間仕切り床の面積の合計, m2
    # 床上側がその他の居室に接する間仕切り床の面積の合計, m2
    # 床上側が非居室に接する間仕切り床の面積の合計, m2
    a_if_mr, a_if_or, a_if_nr = get_inner_floor_total_area(
        a_a, a_mr, a_or, a_evlp_down_mr, a_evlp_down_or, a_evlp_down_nr, a_ef_mr, a_ef_or, a_ef_nr)

    # 床上側が主たる居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
    # 床上側がその他の居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
    # 床上側が非居室に接し床下側が床下空間に接する間仕切り床の面積の合計, m2
    a_if_mr_uf, a_if_or_uf, a_if_nr_uf = get_inner_floor_over_underfloor_total_area(a_if_mr, a_if_or, a_if_nr, a_ef_uf)

    # 床上側が主たる居室に接し床下側がその他の居室に接する間仕切り床の面積の合計, m2
    # 床上側が主たる居室に接し床下側が非居室に接する間仕切り床の面積の合計, m2
    # 床上側がその他の居室に接し床下側が主たる居室に接する間仕切り床の面積の合計, m2
    # 床上側がその他の居室に接し床下側が非居室に接する間仕切り床の面積の合計, m2
    # 床上側が非居室に接し床下側が主たる居室に接する間仕切り床の面積の合計, m2
    # 床上側が非居室に接し床下側がその他の居室に接する間仕切り床の面積の合計, m2
    a_if_mr_or, a_if_mr_nr, a_if_or_mr, a_if_or_nr, a_if_nr_mr, a_if_nr_or = get_inner_floor_between_rooms(
        a_mr, a_or, a_a, a_if_mr, a_if_or, a_if_nr, a_if_mr_uf, a_if_or_uf, a_if_nr_uf)

    ifs = []

    def append_inner_floor(
            ifs: List[InnerFloor],
            name: str,
            area: float,
            upper_space_type: str,
            lower_space_type: str
    ) -> List[InnerFloor]:
        if area > 0.0:
            ifs.append(
                InnerFloor(
                    name=name,
                    area=area,
                    upper_space_type=upper_space_type,
                    lower_space_type=lower_space_type,
                    inner_floor_spec=get_inner_floor_spec()
                )
            )

    append_inner_floor(ifs, 'inner_floor_main_to_underfloor', a_if_mr_uf, 'main_occupant_room', 'underfloor')
    append_inner_floor(ifs, 'inner_floor_other_to_underfloor', a_if_or_uf, 'other_occupant_room', 'underfloor')
    append_inner_floor(ifs, 'inner_floor_non_to_underfloor', a_if_nr_uf, 'non_occupant_room', 'underfloor')
    append_inner_floor(ifs, 'inner_floor_main_to_other', a_if_mr_or, 'main_occupant_room', 'other_occupant_room')
    append_inner_floor(ifs, 'inner_floor_main_to_non', a_if_mr_nr, 'main_occupant_room', 'non_occupant_room')
    append_inner_floor(ifs, 'inner_floor_other_to_main', a_if_or_mr, 'other_occupant_room', 'main_occupant_room')
    append_inner_floor(ifs, 'inner_floor_other_to_non', a_if_or_nr, 'other_occupant_room', 'non_occupant_room')
    append_inner_floor(ifs, 'inner_floor_non_to_main', a_if_nr_mr, 'non_occupant_room', 'main_occupant_room')
    append_inner_floor(ifs, 'inner_floor_non_to_other', a_if_nr_or, 'non_occupant_room', 'other_occupant_room')

    return ifs


def make_inner_walls(common: Dict, gps, ws, ds) -> List[InnerWall]:
    """
    Args:
        common: 共通項目
        gps:
        ws:
        ds:
    Returns:
        内壁
    """

    a_mr = common['main_occupant_room_floor_area']
    a_or = common['other_occupant_room_floor_area']
    a_a = common['total_floor_area']

    # 主たる居室に接する方位が水平である外皮の部位の面積の合計, m2
    # その他の居室に接する方位が水平である外皮の部位の面積の合計, m2
    # 非居室に接する方位が水平である外皮の部位の面積の合計, m2
    a_ow_mr, a_ow_or, a_ow_nr = get_horizontal_envelope_total_area(gps=gps, ws=ws, ds=ds)

    # 主たる居室に接する間仕切り壁の面積の合計, m2
    # その他の居室に接する間仕切り壁の面積の合計, m2
    # 非居室に接する間仕切り壁の面積の合計, m2
    a_iw_mr, a_iw_or, a_iw_nr = get_inner_wall_total_area(a_mr, a_or, a_a, a_ow_mr, a_ow_or, a_ow_nr)

    # 主たる居室とその他の居室に接する間仕切り壁の面積の合計, m2
    # 主たる居室と非居室に接する間仕切り壁の面積の合計, m2
    # その他の居室と非居室に接する間仕切り壁の面積の合計, m2
    a_iw_mr_or, a_iw_mr_nr, a_iw_or_nr = get_inner_wall_total_area_between_rooms(
        a_mr, a_or, a_a, a_iw_mr, a_iw_or, a_iw_nr)

    iws = []

    # def append_inner_wall(iws, name, area, space_type_1, space_type_2):
    #     if area > 0.0:
    #         iws.append(
    #             {
    #                 'name': name,
    #                 'area': area,
    #                 'space_type_1': space_type_1,
    #                 'space_type_2': space_type_2,
    #                 'spec': get_inner_wall_spec()
    #             }
    #         )
    #
    def append_inner_wall(iws, name, area, space_type_1, space_type_2):
        if area > 0.0:
            iws.append(
                InnerWall(
                    name=name,
                    area=area,
                    space_type_1=space_type_1,
                    space_type_2=space_type_2,
                    inner_wall_spec=get_inner_wall_spec()
                )
            )

    append_inner_wall(iws, 'inner_wall_main_to_other', a_iw_mr_or, 'main_occupant_room', 'other_occupant_room')
    append_inner_wall(iws, 'inner_wall_main_to_non', a_iw_mr_nr, 'main_occupant_room', 'non_occupant_room')
    append_inner_wall(iws, 'inner_wall_other_to_non', a_iw_or_nr, 'other_occupant_room', 'non_occupant_room')

    return iws


def convert_spec(common, envelope):

    # 入力辞書データから外皮の部位のクラスに変換する。
    gps = GeneralPart.make_general_parts(ds=envelope['general_parts'])
    ws = Window.make_windows(ds=envelope['windows'])
    ds = Door.make_doors(ds=envelope['doors'])
    eps = EarthfloorPerimeter.make_earthfloor_perimeters(ds=envelope['earthfloor_perimeters'])
    ecs = EarthfloorCenter.make_earthfloor_centers(ds=envelope['earthfloor_centers'])
    hbs = Heatbridge.make_heatbridges(ds=envelope['heat_bridges'])

    # 内壁床の作成
    ifs = make_inner_floors(common=common, gps=gps, ws=ws, ds=ds, ecs=ecs)

    # 内壁壁の作成
    iws = make_inner_walls(common=common, gps=gps, ws=ws, ds=ds)

    envelope_out = {
        'general_parts': [s.get_as_dict() for s in gps],
        'windows': [s.get_as_dict() for s in ws],
        'doors': [s.get_as_dict() for s in ds],
        'earthfloor_perimeters': [s.get_as_dict() for s in eps],
        'earthfloor_centers': [s.get_as_dict() for s in ecs],
        'heat_bridges': [s.get_as_dict() for s in hbs],
        'inner_floors': [s.get_as_dict() for s in ifs],
        'inner_walls': [s.get_as_dict() for s in iws]
    }

    return envelope_out

