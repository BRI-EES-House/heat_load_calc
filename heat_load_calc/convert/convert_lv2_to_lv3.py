from typing import Dict, List

from heat_load_calc.convert import ees_house
from heat_load_calc.convert.ees_house import GeneralPart
from heat_load_calc.convert.ees_house import Window
from heat_load_calc.convert.ees_house import Door
from heat_load_calc.convert.ees_house import Heatbridge
from heat_load_calc.convert.ees_house import EarthfloorPerimeter
from heat_load_calc.convert.ees_house import EarthfloorCenter


def get_separated_areas(a_evlp: float, a_f_mr: float, a_f_or: float, a_f_total: float) -> (float, float, float):
    """
    面積を「主たる居室」「その他の居室」「非居室」の床面積に応じて按分する。
    Args:
        a_evlp: 面積, m2
        a_f_mr: 主たる居室の床面積, m2
        a_f_or: その他の居室の床面積, m2
        a_f_total: 床面積の合計, m2
    Returns:
        按分された以下に対応する面積のタプル。
            (1) 主たる居室
            (2) その他の居室
            (3) 非居室
    """

    a_evlp_mr_i = a_f_mr / a_f_total * a_evlp
    a_evlp_or_i = a_f_or / a_f_total * a_evlp
    a_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * a_evlp

    return a_evlp_mr_i, a_evlp_or_i, a_evlp_nr_i


def get_separated_lengths(l_evlp: float, a_f_mr: float, a_f_or: float, a_f_total: float) -> (float, float, float):
    """
    長さを「主たる居室」「その他の居室」「非居室」の床面積に応じて按分する。
    Args:
        l_evlp: 長さ, m
        a_f_mr: 主たる居室の床面積, m2
        a_f_or: その他の居室の床面積, m2
        a_f_total: 床面積の合計, m2
    Returns:
        按分された以下に対応する長さのタプル。
            (1) 主たる居室
            (2) その他の居室
            (3) 非居室
    """

    l_evlp_mr_i = a_f_mr / a_f_total * l_evlp
    l_evlp_or_i = a_f_or / a_f_total * l_evlp
    l_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * l_evlp

    return l_evlp_mr_i, l_evlp_or_i, l_evlp_nr_i


def get_general_parts_lv3(a_f_mr: float, a_f_or: float, a_f_total: float, gps: List[GeneralPart]) -> List[GeneralPart]:

    gps_lv3 = []

    for gp in gps:

        a_mr, a_or, a_nr = get_separated_areas(a_evlp=gp.area, a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total)

        gps_lv3.append(get_general_part_lv3(gp=gp, space_type='main_occupant_room', area=a_mr))
        gps_lv3.append(get_general_part_lv3(gp=gp, space_type='other_occupant_room', area=a_or))
        gps_lv3.append(get_general_part_lv3(gp=gp, space_type='non_occupant_room', area=a_nr))

    return gps_lv3


def get_general_part_lv3(gp: GeneralPart, space_type, area):

    return GeneralPart(
        name=gp.name + '_' + space_type,
        general_part_type=gp.general_part_type,
        next_space=gp.next_space,
        direction=gp.direction,
        area=area,
        space_type=space_type,
        sunshade=gp.sunshade,
        general_part_spec=gp.general_part_spec
    )


def get_windows_lv3(a_f_mr: float, a_f_or: float, a_f_total: float, ws: List[Window]) -> List[Window]:

    ws_lv3 = []

    for w in ws:

        a_mr, a_or, a_nr = get_separated_areas(a_evlp=w.area, a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total)

        ws_lv3.append(get_window_lv3(w=w, space_type='main_occupant_room', area=a_mr))
        ws_lv3.append(get_window_lv3(w=w, space_type='other_occupant_room', area=a_or))
        ws_lv3.append(get_window_lv3(w=w, space_type='non_occupant_room', area=a_nr))

    return ws_lv3


def get_window_lv3(w: Window, space_type, area):

    return Window(
        name=w.name + '_' + space_type,
        area=area,
        next_space=w.next_space,
        direction=w.direction,
        space_type=space_type,
        sunshade=w.sunshade,
        window_spec=w.window_spec
    )


def get_doors_lv3(a_f_mr: float, a_f_or: float, a_f_total: float, ds: List[Door]) -> List[Door]:

    ds_lv3 = []

    for d in ds:

        a_mr, a_or, a_nr = get_separated_areas(a_evlp=d.area, a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total)

        ds_lv3.append(get_door_lv3(d=d, space_type='main_occupant_room', area=a_mr))
        ds_lv3.append(get_door_lv3(d=d, space_type='other_occupant_room', area=a_or))
        ds_lv3.append(get_door_lv3(d=d, space_type='non_occupant_room', area=a_nr))

    return ds_lv3


def get_door_lv3(d: Door, space_type, area):

    return Door(
        name=d.name + '_' + space_type,
        next_space=d.next_space,
        direction=d.direction,
        area=area,
        space_type=space_type,
        sunshade=d.sunshade,
        door_spec=d.door_spec
    )


def get_heatbridges_lv3(a_f_mr: float, a_f_or: float, a_f_total: float, hbs: List[Heatbridge]) -> List[Heatbridge]:

    hbs_lv3 = []

    for hb in hbs:

        l_mr, l_or, l_nr = get_separated_lengths(l_evlp=hb.length, a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total)

        hbs_lv3.append(get_heatbridge_lv3(hb=hb, space_type='main_occupant_room', length=l_mr))
        hbs_lv3.append(get_heatbridge_lv3(hb=hb, space_type='other_occupant_room', length=l_or))
        hbs_lv3.append(get_heatbridge_lv3(hb=hb, space_type='non_occupant_room', length=l_nr))

    return hbs_lv3


def get_heatbridge_lv3(hb: Heatbridge, space_type, length):

    return Heatbridge(
        name=hb.name + '_' + space_type,
        next_spaces=hb.next_spaces,
        directions=hb.directions,
        length=length,
        space_type=space_type,
        heatbridge_spec=hb.heatbridge_spec
    )


def get_earthfloor_perimeters_lv3(eps: List[EarthfloorPerimeter]) -> List[EarthfloorPerimeter]:

    eps_lv3 = [
        EarthfloorPerimeter(
            name=s.name,
            next_space=s.next_space,
            length=s.length,
            space_type='underfloor',
            earthfloor_perimeter_spec=s.earthfloor_perimeter_spec
        ) for s in eps
    ]

    return eps_lv3


def get_earthfloor_centers_lv3(ecs: List[EarthfloorCenter]) -> List[EarthfloorCenter]:

    ecs_lv3 = [
        EarthfloorCenter(
            name=s.name,
            area=s.area,
            space_type='underfloor',
            earthfloor_center_spec=s.earthfloor_center_spec
        ) for s in ecs
    ]

    return ecs_lv3


def convert_spec(common, envelope):

    a_f_mr = common['main_occupant_room_floor_area']
    a_f_or = common['other_occupant_room_floor_area']
    a_f_total = common['total_floor_area']

    gps_lv3 = get_general_parts_lv3(
        a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total,
        gps=GeneralPart.make_general_parts(ds=envelope['general_parts'])
    )

    ws_lv3 = get_windows_lv3(
        a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total,
        ws=Window.make_windows(ds=envelope['windows'])
    )

    ds_lv3 = get_doors_lv3(
        a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total,
        ds=Door.make_doors(ds=envelope['doors'])
    )

    hbs_lv3 = get_heatbridges_lv3(
        a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total,
        hbs=Heatbridge.make_heatbridges(ds=envelope['heatbridges'])
    )

    eps_lv3 = get_earthfloor_perimeters_lv3(
        eps=EarthfloorPerimeter.make_earthfloor_perimeters(ds=envelope['earthfloor_perimeters'])
    )

    ecs_lv3 = get_earthfloor_centers_lv3(
        ecs=EarthfloorCenter.make_earthfloor_centers(ds=envelope['earthfloor_centers'])
    )

    result = {
        'input_method': 'detail_with_room_usage',
        'general_parts': [r.get_as_dict() for r in gps_lv3],
        'windows': [w_lv3.get_as_dict() for w_lv3 in ws_lv3],
        'doors': [d_lv3.get_as_dict() for d_lv3 in ds_lv3],
        'heatbridges': [hb_lv3.get_as_dict() for hb_lv3 in hbs_lv3],
        'earthfloor_perimeters': [ep_lv3.get_as_dict() for ep_lv3 in eps_lv3],
        'earthfloor_centers': [ec_lv3.get_as_dict() for ec_lv3 in ecs_lv3]
    }

    return result

