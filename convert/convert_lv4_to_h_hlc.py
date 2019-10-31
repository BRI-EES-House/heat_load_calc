from typing import Dict
import copy

import pprint

import a_06_common_items
from a_01_00_general_part import get_general_part_spec_hlc as a_01_00_get_general_part_spec_hlc
from f_01_factor_h import get_factor_h as f_01_get_factor_h

# region common


def make_common(region: int) -> Dict:
    """
    Args:
        region: 地域の区分
    Returns:
        common ディクショナリ
    """

    return {
        'region': region,
        'calculation_type': 'residential'
    }


# endregion


# region rooms


def make_rooms(common, d, d_calc_input, envelope, equipment_main, equipment_other, region, ventilation, natural_vent):

    # 外皮に関する辞書
    gps = envelope['general_parts']    # 一般部位
    gws = envelope['windows']    # 大部分がガラスで構成される窓等の開口部
    gds = envelope['doors']    # 大部分がガラスで構成されないドア等の開口部
    eps = envelope['earthfloor_perimeters']    # 土間床等の外周部
    ecs = envelope['earthfloor_centers']    # 土間床等の中心部

    # 床面積の合計, m2
    a_a = common['total_floor_area']

    # 主たる居室の床面積, m2
    a_mr = common['main_occupant_room_floor_area']

    # その他の居室の床面積, m2
    a_or = common['other_occupant_room_floor_area']

    # 非居室の床面積, m2
    a_nr = a_a - a_mr - a_or

    # 床下空間の床面積, m2
    a_uf = get_a_uf(ecs=ecs)

    # 換気回数
    n = ventilation['air_change_rate']

    # 自然風利用, 換気回数, 1/h
    v_nv_mr = natural_vent['main_occupant_room_natural_vent_time']
    v_nv_or = natural_vent['other_occupant_room_natural_vent_time']

    room_mr, room_or, room_nr, room_uf = make_initial_rooms(
        a_a=a_a, a_mr=a_mr, a_or=a_or, a_nr=a_nr, a_uf=a_uf, n=n, v_nv_mr=v_nv_mr, v_nv_or=v_nv_or)

    boundaries_mr, boundaries_or, boundaries_nr, boundaries_uf = get_boundaries_general_part(region, gps)

    room_mr['surface'].extend(boundaries_mr)
    room_or['surface'].extend(boundaries_or)
    room_nr['surface'].extend(boundaries_nr)
    room_uf['surface'].extend(boundaries_uf)

    d_calc_input['Rooms'] = rooms

    d_calc_input['Rooms'] = get_boundaries_windows(region, gws, rooms)

    d_calc_input['Rooms'] = integrate_doors_to_rooms(region, gds, rooms)

    d_calc_input['Rooms'] = integrate_earthfloorperimeters_to_rooms(region, eps, rooms)

    d_calc_input['Rooms'] = integrate_earthfloors_to_rooms(region, ecs, rooms)

    d_calc_input['Rooms'] = integrate_innerwalls_to_rooms(region, d['InnerWalls'], rooms)

    d_calc_input['Rooms'] = integrate_equipments_to_rooms(a_mr, a_or, equipment_main, equipment_other, rooms)


def get_a_uf(ecs: Dict) -> float:
    """
    Args:
        ecs: 土間床等の中心部のDict
    Returns:
        床下空間の床面積, m2
    """

    return sum([ec['area'] for ec in ecs if ec['space_type'] == 'underfloor'])


def make_initial_rooms(
        a_a: float, a_mr: float, a_or: float, a_nr: float, a_uf: float, n: float, v_nv_mr: float, v_nv_or: float
) -> (Dict, Dict, Dict, Dict):
    """
    Args:
        a_a: 床面積の合計, m2
        a_mr: 主たる居室の床面積, m2
        a_or: その他の居室の床面積, m2
        a_nr: 非居室の床面積, m2
        a_uf: 床下空間の床面積, m2
        n: 換気回数, 1/h
        v_nv_mr: 主たる居室における自然風利用時の換気回数, 1/h
        v_nv_or: その他の居室における自然風利用時の換気回数, 1/h
    Returns:
        以下のタプル
            (1) 主たる居室
            (2) その他の居室
            (3) 非居室
            (4) 床下空間
    """

    # 室の容積, m3
    v_mr, v_or, v_nr, v_uf = get_room_volume(a_mr, a_or, a_nr, a_uf)

    # 外気から流入する換気量, m3/h
    v_vent_ex_mr, v_vent_ex_or, v_vent_ex_nr, v_vent_ex_uf = get_v_vent_ex(a_a, a_mr, a_or, n)

    # 室間の換気量, m3/h
    v_vent_mr_nr, v_vent_or_nr = get_v_vent(v_vent_ex_mr, v_vent_ex_or)

    c_value = 5.0  # ここは住宅構造やUA値等から何らかの設定が必要

    if a_mr <= 0.0:
        raise ValueError('主たる居室の面積が0m2になっています。')

    room_mr = {
        'name': 'main_occupant_room',
        'room_type': 'main_occupant_room',
        'volume': v_mr,
        'vent': v_vent_ex_mr,
        'next_vent': [],
        'c_value': c_value,
        'natural_vent_time': v_nv_mr,
        'boundaries': [],
    }

    if a_or > 0.0:

        room_or = {
            'name': 'other_occupant_room',
            'room_type': 'other_occupant_room',
            'volume': v_or,
            'vent': v_vent_ex_or,
            'next_vent': [],
            'c_value': c_value,
            'natural_vent_time': v_nv_or,
            'boundaries': [],
        }

    else:

        room_or = None

    if a_nr > 0.0:

        next_vent = []

        if a_mr > 0.0:
            next_vent.append({
                'upstream_room_name': 'main',
                'volume': v_vent_mr_nr,
            })

        if a_or > 0.0:
            next_vent.append({
                'upstream_room_name': 'other',
                'volume': v_vent_or_nr,
            })

        room_nr = {
            'name': 'non_occupant_room',
            'room_type': 'non_occupant_room',
            'volume': v_nr,
            'vent': v_vent_ex_nr,
            'next_vent': next_vent,
            'c_value': c_value,
            'natural_vent_time': 0.0,
            'boundaries': [],
        }

    else:

        room_nr = None

    if a_uf > 0.0:

        room_uf = {
            'name': 'underfloor',
            'room_type': 'underfloor',
            'volume': v_uf,
            'vent': v_vent_ex_uf,
            'next_vent': [],
            'c_value': c_value,
            'natural_vent_time': 0.0,
            'boundaries': [],
        }

    else:

        room_uf = None

    return room_mr, room_or, room_nr, room_uf


def get_room_volume(a_mr: float, a_or: float, a_nr: float, a_uf: float) -> (float, float, float, float):
    """
    Args:
        a_mr: 主たる居室の床面積, m2
        a_or: その他の居室の床面積, m2
        a_nr: 非居室の床面積, m2
        a_uf: 床下空間の床面積, m2
    Returns:
        室の容積, m3
            (1) 主たる居室
            (2) その他の居室
            (3) 非居室
            (4) 床下空間
    """

    # 階高, m
    h_mr = 2.4  # 主たる居室
    h_or = 2.4  # その他居室
    h_nr = 2.4  # 非居室
    h_uf = 0.4  # 床下

    return a_mr * h_mr, a_or * h_or, a_nr * h_nr, a_uf * h_uf


def get_v_vent_ex(a_a: float, a_mr: float, a_or: float, n: float) -> (float, float, float, float):
    """
    Args:
        a_a: 床面積の合計, m2
        a_mr: 主たる居室の床面積, m2
        a_or: その他の居室の床面積, m2
        n: 換気回数, 1/h
    Returns:
        各居室の外気から流入する換気量, m3/h
            1) 主たる居室
            2) その他の居室
            3) その他の居室
            4) 床下空間
    """

    # 階高, m
    h_a = 2.4

    # 換気の余裕率
    a = 1.1

    # 換気量の合計, m3/h
    v_vent = a_a * h_a * n * a

    # 各居室の外気から流入する換気量, m3/h
    v_vent_ex_mr = v_vent * a_mr / (a_mr + a_or)  # 主たる居室
    v_vent_ex_or = v_vent * a_or / (a_mr + a_or)  # その他の居室
    v_vent_ex_nr = 0.0  # 非居室
    v_vent_ex_uf = 0.0  # 床下空間

    return v_vent_ex_mr, v_vent_ex_or, v_vent_ex_nr, v_vent_ex_uf


def get_v_vent(v_vent_ex_mr: float, v_vent_ex_or: float) -> (float, float):
    """
    Args:
        v_vent_ex_mr: 外気から主たる居室に流入する換気量, m3/h
        v_vent_ex_or: 外気からその他の居室に流入する換気量, m3/h
    Returns:
        室間の換気量, m3/h
            1) 主たる居室から非居室
            2) その他の居室から非居室
    """

    v_vent_mr_nr = v_vent_ex_mr
    v_vent_or_nr = v_vent_ex_or

    return v_vent_mr_nr, v_vent_or_nr


def get_boundaries_general_part(region, general_parts):

    boundary_mr = []
    boundary_or = []
    boundary_nr = []
    boundary_uf = []

    for gp in general_parts:

        parts = a_01_00_get_general_part_spec_hlc(gp)

        for part_i in parts:

            name_hlc_i, r_a_hlc_i, general_part_spec_hlc_i, u_i = part_i

            boundary = {
                'name': gp['name'] + name_hlc_i,
                'boundary_type': 'external_general_part',
                'area': gp['area'] * r_a_hlc_i,
                'is_sun_striked_outside': get_is_sun_striked_outside(gp['direction']),
                'temp_dif_coef': f_01_get_factor_h(region=region, next_space=gp['next_space']),
                'direction': get_direction(gp['direction']),
                'is_solar_absorbed_inside': get_is_solar_absorbed_inside(general_part_type=gp['general_part_type']),
                'general_part_spec': general_part_spec_hlc_i,
                'solar_shading_part': copy.deepcopy(gp['spec']['sunshade'])
            }

            space_type = gp['space_type']

            if space_type == 'main_occupant_room':
                boundary_mr.append(boundary)
            elif space_type == 'other_occupant_room':
                boundary_or.append(boundary)
            elif space_type == 'non_occupant_room':
                boundary_nr.append(boundary)
            elif space_type == 'under_floor':
                boundary_uf.append(boundary)
            else:
                raise ValueError()

    return boundary_mr, boundary_or, boundary_nr, boundary_uf


def get_is_solar_absorbed_inside(general_part_type):

    return general_part_type == 'floor' or general_part_type == 'downward_boundary_floor'


def get_is_sun_striked_outside(direction: str) -> bool:
    """
    日射の有無を判定する。

    Args:
        direction: 方位

    Returns:
        日射の有無
    """

    return {
        'top': True,
        'n': True,
        'ne': True,
        'e': True,
        'se': True,
        's': True,
        'sw': True,
        'w': True,
        'nw': True,
        'bottom': False,
        'upward': False,
        'horizontal': False,
        'downward': False
    }[direction]


def get_direction(direction: str) -> str:
    """
    負荷計算用の方位を取得する。

    Args:
        direction: 方位

    Returns:
        方位
    """

    return {
        'top': 'top',
        'n': True,
        'ne': True,
        'e': True,
        'se': True,
        's': True,
        'sw': True,
        'w': True,
        'nw': True,
        'bottom': False,
        'upward': False,
        'horizontal': False,
        'downward': False
    }[direction]






def get_directionangle_from_direction(direction):
    Direction_to_DirectionAngle = {
        'Top': None,
        'N': 180,
        'NE': -135,
        'E': -90,
        'SE': -45,
        'S': 0,
        'SW': 45,
        'W': 90,
        'NW': 135,
        'Bottom': None,
        'ClosedSpace': None,
        'OpenBackFloor': None,
        'ResidenceSpace': None,
        'ClosedBackFloor': None
    }

    return Direction_to_DirectionAngle[direction]


def get_inclinationangle_from_direction(direction):
    Direction_to_InclinationAngle = {
        'Top': 0,
        'N': 90,
        'NE': 90,
        'E': 90,
        'SE': 90,
        'S': 90,
        'SW': 90,
        'W': 90,
        'NW': 90,
        'Bottom': 180,
        'ClosedSpace': None,
        'OpenBackFloor': None,
        'ResidenceSpace': None,
        'ClosedBackFloor': None
    }

    return Direction_to_InclinationAngle[direction]


def get_tempdifferentfactor_from_direction(region, direction):
    Direction_to_NextSpace = {
        'Top': 'outside',
        'N': 'outside',
        'NE': 'outside',
        'E': 'outside',
        'SE': 'outside',
        'S': 'outside',
        'SW': 'outside',
        'W': 'outside',
        'NW': 'outside',
        'Bottom': 'outside',
        'ClosedSpace': 'underfloor',
        'OpenBackFloor': 'underfloor',
        'ResidenceSpace': 'next_room',
        'ClosedBackFloor': 'next_room'
    }

    NextSpace_to_TempDifferentFactor = {
        # 外気又は外気に通じる空間(小屋裏・天井裏・共用部・屋内駐車場・メーターボックス・エレベーターシャフト等)
        'outside': {1: 1.00, 2: 1.00, 3: 1.00, 4: 1.00, 5: 1.00, 6: 1.00, 7: 1.00, 8: 1.00},
        # 外気に通じていない空間(昇降機室、共用機械室、倉庫等)又は外気に通じる床裏
        'underfloor': {1: 0.70, 2: 0.70, 3: 0.70, 4: 0.70, 5: 0.70, 6: 0.70, 7: 0.70, 8: 0.70},
        # 住戸、住戸と同様の熱的環境の空問(空調された共用部等)又は外気に通じていない床裏(ピット等）
        'next_room': {1: 0.05, 2: 0.05, 3: 0.05, 4: 0.15, 5: 0.15, 6: 0.15, 7: 0.15, 8: 0.15}
    }

    return NextSpace_to_TempDifferentFactor[Direction_to_NextSpace[direction]][region]


def get_boundary_for_outer_skin(region, nextspace, direction):
    Type = {
        'Top': 'Outdoor',
        'N': 'Outdoor',
        'NE': 'Outdoor',
        'E': 'Outdoor',
        'SE': 'Outdoor',
        'S': 'Outdoor',
        'SW': 'Outdoor',
        'W': 'Outdoor',
        'NW': 'Outdoor',
        'Bottom': 'Outdoor',
        'ClosedSpace': 'DeltaTCoeff',
        'OpenBackFloor': 'DeltaTCoeff',
        'ResidenceSpace': 'DeltaTCoeff',
        'ClosedBackFloor': 'DeltaTCoeff'
    }

    boundary = {
        'Outdoor': {
            'name': direction,
            'Type': 'Outdoor',
            'DirectionAngle': get_directionangle_from_direction(direction if nextspace == 'Outdoor' else nextspace),
            'InclinationAngle': get_inclinationangle_from_direction(direction if nextspace == 'Outdoor' else nextspace),
            'GroundReflectRate': 0.1
        },
        'DeltaTCoeff': {
            'name': direction,
            'Type': 'DeltaTCoeff',
            'TempDifferFactor': get_tempdifferentfactor_from_direction(region,
                                                                       direction if nextspace == 'Outdoor' else nextspace)
        }
    }[Type[direction if nextspace == 'Outdoor' else nextspace]]

    return boundary


def get_boundary_for_inner_skin(type, nextspace):
    boundary = {
        'name': 'NextRoom' + '_' + nextspace,
        'Type': 'NextRoom',
        'room_type': nextspace
    }

    return boundary


def get_boundary_for_earthfloorperimeter(region, direction):
    Type = {
        'Top': 'Outdoor',
        'N': 'Outdoor',
        'NE': 'Outdoor',
        'E': 'Outdoor',
        'SE': 'Outdoor',
        'S': 'Outdoor',
        'SW': 'Outdoor',
        'W': 'Outdoor',
        'NW': 'Outdoor',
        'Bottom': 'Outdoor',
        'ClosedSpace': 'DeltaTCoeff',
        'OpenBackFloor': 'DeltaTCoeff',
        'ResidenceSpace': 'DeltaTCoeff',
        'ClosedBackFloor': 'DeltaTCoeff'
    }

    boundary = {
        'Outdoor': {
            'name': direction,
            'Type': 'Outdoor'
        },
        'DeltaTCoeff': {
            'name': direction,
            'Type': 'DeltaTCoeff',
            'TempDifferFactor': get_tempdifferentfactor_from_direction(region, direction)
        }
    }[Type[direction]]

    return boundary


def get_direction_from_direction_for_outer_skin(direction):
    return {
        'Top': 'Downward',
        'N': 'Vertical',
        'NE': 'Vertical',
        'E': 'Vertical',
        'SE': 'Vertical',
        'S': 'Vertical',
        'SW': 'Vertical',
        'W': 'Vertical',
        'NW': 'Vertical',
        'Bottom': 'Upward',
        'ClosedSpace': 'Vertical',  # 暫定的な処理。方位と温度差係数を別の変数として扱うべき。
        'OpenBackFloor': 'Upward',  # 暫定値な処理。方位と温度差係数を別の変数として扱うべき。
        'ResidenceSpace': 'Vertical',  # 暫定値な処理。方位と温度差係数を別の変数として扱うべき。
        'ClosedBackFloor': 'Upward'  # 暫定値な処理。方位と温度差係数を別の変数として扱うべき。
    }[direction]


def get_direction_from_direction_for_inner_skin(space, type):
    return {
        'main_occupant_room': {'InnerCeiling': 'Downward', 'InnerWall': 'Vertical', 'InnerFloor': 'Upward',
                               'GroundFloor': 'Upward'},
        'other_occupant_room': {'InnerCeiling': 'Downward', 'InnerWall': 'Vertical', 'InnerFloor': 'Upward',
                                'GroundFloor': 'Upward'},
        'non_occupant_room': {'InnerCeiling': 'Downward', 'InnerWall': 'Vertical', 'InnerFloor': 'Upward',
                              'GroundFloor': 'Upward'},
        'underfloor': {'InnerCeiling': None, 'InnerWall': None, 'InnerFloor': None, 'GroundFloor': 'Downward'}
    }[space][type]


def make_layer(name, thick, cond, specH, **kwargs):
    return {
        'name': name,
        'thick': thick,
        'cond': cond,
        'specH': 0 if specH == None else specH
    }


def integrate_innerwalls_to_rooms(region, d_innerwalls, d_rooms):
    n = {'InnerCeiling': 1, 'InnerWall': 1, 'InnerFloor': 1, 'GroundFloor': 1}
    for x in d_innerwalls:

        r_i, r_o = a_06_common_items.get_r_surf(general_part_type=x['general_part'], next_space=x['next_space'])

        for y in d_rooms:
            if x['space'] == y['room_type']:
                y['Surface'].append({
                    'skin': False,
                    'direction': get_direction_from_direction_for_inner_skin(x['space'], x['type']),
                    'floor': True if (x['type'] == 'GroundFloor' or x['type'] == 'InnerFloor') else False,
                    'boundary': get_boundary_for_inner_skin(x['type'], x['nextspace']),
                    'unsteady': True,
                    'IsSoil': False,
                    'name': x['type'] + str(n[x['type']]),
                    'area': x['area'],
                    'flr': 0,
                    'Wall': {
                        'OutHeatTrans': 1 / r_o,
                        'InHeatTrans': 1 / r_i,
                        'Layers': x['Layers']
                    },
                })
                n[x['type']] = n[x['type']] + 1

    return d_rooms


def integrate_doors_to_rooms(region, d_doors, d_rooms):
    n = 1
    for x in d_doors:
        for y in d_rooms:
            if x['space'] == y['room_type']:
                eta = 0.034 * x['U']
                y['Surface'].append({
                    'skin': True,
                    'direction': get_direction_from_direction_for_outer_skin(x['direction']),
                    'floor': True if x['direction'] == 'Bottom' else False,
                    'boundary': get_boundary_for_outer_skin(region, x['nextspace'], x['direction']),
                    'unsteady': False,
                    'name': 'Door' + str(n),
                    'area': x['area'],
                    'flr': 0,
                    'Window': {
                        'Eta': eta,
                        'SolarTrans': eta,
                        'SolarAbsorp': 0,
                        'Uw': x['U'],
                        'OutEmissiv': 0.9,
                        'OutHeatTrans': 1 / 0.04,
                        'InHeatTrans': 1 / 0.11,
                    },
                    'sunbreak': {'D': x['Z'], 'WI1': 500, 'WI2': 500, 'hi': x['Y1'], 'WR': 0, 'WH': x['Y2'],
                                 'name': 'ひさし'} if x['IsSunshadeInput'] == True else {}
                })
                n = n + 1

    return d_rooms


def get_eta_from_specification(typeFrame, typeGlass, typeShade):
    f_frame = {'WoodOrResin': 0.72, 'Steel': 0.8}[typeFrame]

    eta = {
        '3WgG': {'None': 0.54, 'Shoji': 0.34, 'ExtarnalBlind': 0.12},  # 三層複層 Low-E三層複層ガラス（Low-Eガラス2枚）日射取得型
        '3WsG': {'None': 0.33, 'Shoji': 0.22, 'ExtarnalBlind': 0.08},  # 三層複層 Low-E三層複層ガラス（Low-Eガラス2枚）日射遮蔽型
        '3LgG': {'None': 0.59, 'Shoji': 0.37, 'ExtarnalBlind': 0.14},  # 三層複層 Low-E三層複層ガラス（Low-Eガラス1枚）日射取得型
        '3LsG': {'None': 0.37, 'Shoji': 0.25, 'ExtarnalBlind': 0.10},  # 三層複層 Low-E三層複層ガラス（Low-Eガラス1枚）日射遮蔽型
        '2LgG': {'None': 0.64, 'Shoji': 0.38, 'ExtarnalBlind': 0.15},  # 二層複層 Low-E複層ガラス日射取得型
        '2LsG': {'None': 0.40, 'Shoji': 0.26, 'ExtarnalBlind': 0.11},  # 二層複層 Low-E複層ガラス日射遮蔽型
        '2FAheatreflect1': {'None': 0.79, 'Shoji': 0.38, 'ExtarnalBlind': 0.17},  # 二層複層 遮熱複層ガラス熱線反射ガラス1種
        '2FAheatreflect2': {'None': 0.79, 'Shoji': 0.38, 'ExtarnalBlind': 0.17},  # 二層複層 遮熱複層ガラス熱線反射ガラス2種
        '2FAheatreflect3': {'None': 0.79, 'Shoji': 0.38, 'ExtarnalBlind': 0.17},  # 二層複層 遮熱複層ガラス熱線反射ガラス3種
        '2FAheatabsorb2': {'None': 0.79, 'Shoji': 0.38, 'ExtarnalBlind': 0.17},  # 二層複層 遮熱複層ガラス熱線吸収板ガラス2種
        '2FAmulti': {'None': 0.79, 'Shoji': 0.38, 'ExtarnalBlind': 0.17},  # 二層複層 複層ガラス
        '2FAsingle': {'None': 0.79, 'Shoji': 0.38, 'ExtarnalBlind': 0.17},  # 二層複層 単板ガラス2枚
        'Theatreflect1': {'None': 0.88, 'Shoji': 0.38, 'ExtarnalBlind': 0.19},  # 単層 単板ガラス熱線反射ガラス1種
        'Theatreflect2': {'None': 0.88, 'Shoji': 0.38, 'ExtarnalBlind': 0.19},  # 単層 単板ガラス熱線反射ガラス2種
        'Theatreflect3': {'None': 0.88, 'Shoji': 0.38, 'ExtarnalBlind': 0.19},  # 単層 単板ガラス熱線反射ガラス3種
        'Theatabsorb2': {'None': 0.88, 'Shoji': 0.38, 'ExtarnalBlind': 0.19},  # 単層 単板ガラス熱線吸収板ガラス2種
        'Tsingle': {'None': 0.88, 'Shoji': 0.38, 'ExtarnalBlind': 0.19}  # 単層 単板ガラスその他
    }[typeGlass][typeShade]

    return eta * f_frame


def get_eta(d_window):
    if d_window['EtaInputMethod'] == 'InputValue':
        if d_window['TypeWindow'] == 'Single':
            eta = d_window['Eta']
        if d_window['TypeWindow'] == 'Double':
            eta = d_window['EtaInside'] * d_window['EtaOutside'] * 1.06 / \
                  (0.72 if d_window['TypeFrameInside'] == 'WoodOrResin' and d_window[
                      'TypeFrameOutside'] == 'WoodOrResin' else 0.8)
    elif d_window['EtaInputMethod'] == 'InputSpecification':
        if d_window['TypeWindow'] == 'Single':
            eta = get_eta_from_specification(d_window['TypeFrame'], d_window['TypeGlass'], d_window['TypeShade'])
        if d_window['TypeWindow'] == 'Double':
            eta = get_eta_from_specification(d_window['TypeFrameInside'], d_window['TypeGlassInside'],
                                             d_window['TypeShadeInside']) * \
                  get_eta_from_specification(d_window['TypeFrameOutside'], d_window['TypeGlassOutside'],
                                             d_window['TypeShadeOutside']) * \
                  1.06 / (0.72 if d_window['TypeFrameInside'] == 'WoodOrResin' and d_window[
                'TypeFrameOutside'] == 'WoodOrResin' else 0.8)
    else:
        raise ValueError

    return eta


def get_boundaries_windows(region, d_windows, d_rooms):

    n = 1

    boundary_mr = []
    boundary_or = []
    boundary_nr = []
    boundary_uf = []

    for window in d_windows:

        eta = get_eta(window)
                surface = {
                    'skin': True,
                    'direction': get_direction_from_direction_for_outer_skin(window['direction']),
                    'floor': True if window['direction'] == 'Bottom' else False,
                    'boundary': get_boundary_for_outer_skin(region, window['nextspace'], window['direction']),
                    'unsteady': False,
                    'name': 'Window' + str(n),
                    'area': window['area'],
                    'flr': 0,
                    'Window': {
                        'Eta': eta,
                        'SolarTrans': eta,
                        'SolarAbsorp': 0,
                        'UW': window['UW'],
                        'OutEmissiv': 0.9,
                        'OutHeatTrans': 1 / 0.04,
                        'InHeatTrans': 1 / 0.11,
                    },
                    'sunbreak': {'D': window['Z'], 'WI1': 500, 'WI2': 500, 'hi': window['Y1'], 'WR': 0, 'WH': window['Y2'],
                                 'name': 'ひさし'} if window['IsSunshadeInput'] == True else {}
                }
                y['Surface'].append(surface)

                space_type = gp['space_type']

                if space_type == 'main_occupant_room':
                    boundary_mr.append(boundary)
                elif space_type == 'other_occupant_room':
                    boundary_or.append(boundary)
                elif space_type == 'non_occupant_room':
                    boundary_nr.append(boundary)
                elif space_type == 'under_floor':
                    boundary_uf.append(boundary)
                else:
                    raise ValueError()

                n = n + 1

    return d_rooms


def integrate_earthfloorperimeters_to_rooms(region, d_earthfloorperimeters, d_rooms):
    n = 1
    for x in d_earthfloorperimeters:
        for y in d_rooms:
            if x['space'] == y['room_type']:
                y['EarthfloorPerimeter'].append({
                    'name': 'EarthfloorPerimeter' + str(n),
                    'LinearHeatTrans': x['psi'],
                    'LinearHeatTransLength': x['length'],
                    'boundary': get_boundary_for_earthfloorperimeter(region,
                                                                     x['direction'] if x['nextspace'] == 'Outdoor' else
                                                                     x['nextspace'])
                })
                n = n + 1

    return d_rooms


def integrate_earthfloors_to_rooms(region, d_earthfloors, d_rooms):
    n = 1
    for x in d_earthfloors:
        for y in d_rooms:
            if x['space'] == y['room_type']:
                y['Surface'].append({
                    'skin': True,
                    'direction': 'Upward',
                    'floor': True,
                    'boundary': 'AnnualAverage',
                    'unsteady': True,
                    'IsSoil': True,
                    'name': 'Earthfloor' + str(n),
                    'area': x['area'],
                    'flr': 0,
                    'Wall': {
                        'InHeatTrans': 1 / 0.15,
                        'Layers': [
                            {'name': 'RC', 'thick': 0.150, 'cond': 1.6, 'specH': 2000.0},
                            {'name': 'Soil', 'thick': 3.000, 'cond': 1.0, 'specH': 3300.0}
                        ]
                    },
                })
                n = n + 1

    return d_rooms


def integrate_equipments_to_rooms(area_main, area_other, equipment_main, equipment_other, d_rooms):
    if area_main > 0:
        for x in d_rooms:
            if x['room_type'] == 'main_occupant_room':
                x['equipment'] = equipment_main

    if area_other > 0:
        for x in d_rooms:
            if x['room_type'] == 'other_occupant_room':
                x['equipment'] = equipment_other

    return d_rooms


# endregion


def convert(common, envelope, d, equipment_main, equipment_other, natural_vent):

    region = common['region']

    ventilation = d['ventilation']
    envelope = d['envelope']

    d_calc_input = {
        'common': make_common(region=region)
    }

    make_rooms(common, d, d_calc_input, envelope, equipment_main, equipment_other, region, ventilation, natural_vent)

    return d_calc_input


if __name__ == '__main__':

    common = {
        'region': 6,
        'main_occupant_room_floor_area': 30.0,
        'other_occupant_room_floor_area': 30.0,
        'total_floor_area': 120.0
    }

    d = {
        'ventilation': {
            'air_change_rate': 0.5,
        },
        'envelope': {
            'general_parts': [
                {'name': 'Roof_other', 'next_space': 'OpenBackFloor', 'direction': 'Top', 'area': 16.95,
                 'space': 'other_occupant_room', 'general_part_type': 'Roof',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 7.7},
                {'name': 'Roof_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'Top', 'area': 33.9,
                 'space': 'non_occupant_room', 'general_part_type': 'Roof',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 7.7},
                {'name': 'Wall_SW_main', 'next_space': 'OpenBackFloor', 'direction': 'SW', 'area': 10.1575,
                 'space': 'main_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_SW_other', 'next_space': 'OpenBackFloor', 'direction': 'SW', 'area': 10.1575,
                 'space': 'other_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_SW_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'SW', 'area': 20.315,
                 'space': 'non_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_NW_main', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 7.4575,
                 'space': 'main_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_NW_other', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 7.4575,
                 'space': 'other_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_NW_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 14.915,
                 'space': 'non_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_NE_main', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 15.9725,
                 'space': 'main_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_NE_other', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 15.9725,
                 'space': 'other_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_NE_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 31.945,
                 'space': 'non_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_SE_main', 'next_space': 'OpenBackFloor', 'direction': 'SE', 'area': 7.4275,
                 'space': 'main_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_SE_other', 'next_space': 'OpenBackFloor', 'direction': 'SE', 'area': 7.4275,
                 'space': 'other_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Wall_SE_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'SE', 'area': 14.855,
                 'space': 'non_occupant_room', 'general_part_type': 'Wall',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 6.67},
                {'name': 'Floor_main', 'next_space': 'OpenBackFloor', 'direction': 'Bottom', 'area': 15.0175,
                 'space': 'main_occupant_room', 'general_part_type': 'Floor',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 5.27},
                {'name': 'Floor_other', 'next_space': 'OpenBackFloor', 'direction': 'Bottom', 'area': 15.0175,
                 'space': 'other_occupant_room', 'general_part_type': 'Floor',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 5.27},
                {'name': 'Floor_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'Bottom', 'area': 30.035,
                 'space': 'non_occupant_room', 'general_part_type': 'Floor',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 5.27},
                {'name': 'Floor_bath_main', 'next_space': 'OpenBackFloor', 'direction': 'Bottom', 'area': 1.1025,
                 'space': 'main_occupant_room', 'general_part_type': 'Floor',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 5.27},
                {'name': 'Floor_bath_other', 'next_space': 'OpenBackFloor', 'direction': 'Bottom', 'area': 1.1025,
                 'space': 'other_occupant_room', 'general_part_type': 'Floor',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 5.27},
                {'name': 'Floor_bath_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'Bottom', 'area': 2.205,
                 'space': 'non_occupant_room', 'general_part_type': 'Floor',
                 'structure': 'wood', 'InputMethod': 'InputUA', 'IsSunshadeInput': False, 'UA': 5.27},
                {
                    'name': 'Roof_main',
                    'next_space': 'OpenBackFloor',
                    'direction': 'Top',
                    'IsInContactWithOutsideAir': True,
                    'area': 16.95, 'space': 'main_occupant_room',
                    'general_part_type': 'Roof',
                    'structure': 'wood',
                    'InputMethod': 'InputAllDetails',
                    'Parts': [
                        {'AreaRatio': 1.0, 'Layers': [{'name': 'wood', 'thick': 0.012, 'cond': 0.16, 'specH': None},
                                                      {'name': 'wood', 'thick': 0.012, 'cond': 0.16, 'specH': 720}]}],
                    'IsSunshadeInput': False, 'UA': 7.7
                },
            ],
            'Windows': [
                {'name': 'WindowSW_main', 'next_space': 'OpenBackFloor', 'direction': 'SW', 'area': 7.5625,
                 'space': 'main_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.348},
                {'name': 'WindowSW_other', 'next_space': 'OpenBackFloor', 'direction': 'SW', 'area': 7.5625,
                 'space': 'other_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.348},
                {'name': 'WindowSW_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'SW', 'area': 15.125,
                 'space': 'non_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.348},
                {'name': 'WindowNW_main', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 0.7925,
                 'space': 'main_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.316},
                {'name': 'WindowNW_other', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 0.7925,
                 'space': 'other_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.316},
                {'name': 'WindowNW_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 1.585,
                 'space': 'non_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.316},
                {'name': 'WindowNE_main', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 1.21,
                 'space': 'main_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.316},
                {'name': 'WindowNE_other', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 1.21,
                 'space': 'other_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.316},
                {'name': 'WindowNE_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 2.42,
                 'space': 'non_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.316},
                {'name': 'WindowSE_main', 'next_space': 'OpenBackFloor', 'direction': 'SE', 'area': 1.4575,
                 'space': 'main_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.348},
                {'name': 'WindowSE_other', 'next_space': 'OpenBackFloor', 'direction': 'SE', 'area': 1.4575,
                 'space': 'other_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.348},
                {'name': 'WindowSE_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'SE', 'area': 2.915,
                 'space': 'non_occupant_room', 'UW': 3.49,
                 'IsSunshadeInput': True, 'TypeWindow': 'Single', 'EtaInputMethod': 'InputValue', 'Eta': 0.51,
                 'TypeGlass': None,
                 'Y1': 0, 'Y2': 1.1, 'Z': 0.348}
            ],
            'Doors': [
                {'name': 'DoorNW_main', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 0.63,
                 'space': 'main_occupant_room', 'U': 4.65, 'IsSunshadeInput': False},
                {'name': 'DoorNW_other', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 0.63,
                 'space': 'other_occupant_room', 'U': 4.65, 'IsSunshadeInput': False},
                {'name': 'DoorNW_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'NW', 'area': 1.26,
                 'space': 'non_occupant_room', 'U': 4.65, 'IsSunshadeInput': False},
                {'name': 'DoorNE_main', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 0.54,
                 'space': 'main_occupant_room', 'U': 4.65, 'IsSunshadeInput': False},
                {'name': 'DoorNE_other', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 0.54,
                 'space': 'other_occupant_room', 'U': 4.65, 'IsSunshadeInput': False},
                {'name': 'DoorNE_nonliving', 'next_space': 'OpenBackFloor', 'direction': 'NE', 'area': 1.08,
                 'space': 'non_occupant_room', 'U': 4.65, 'IsSunshadeInput': False}
            ],
            'EarthfloorPerimeters': [
                {'next_space': 'OpenBackFloor', 'direction': 'NW', 'length': 2.43, 'name': 'Entrance_NW', 'psi': 1.8,
                 'space': 'underfloor'},
                {'next_space': 'OpenBackFloor', 'direction': 'NE', 'length': 1.83, 'name': 'Entrance_NE', 'psi': 1.8,
                 'space': 'underfloor'},
                {'next_space': 'OpenBackFloor', 'direction': 'OpenBackFloor', 'length': 4.25, 'name': 'Entrance_floor',
                 'psi': 1.8, 'space': 'underfloor'}
            ],
            'earthfloor_centers': [
                {'name': 'earthfloor', 'area': 3.24, 'space_type': 'underfloor'}
            ],
            'InnerWalls': [
                {'name': 'GroundFloor_main', 'type': 'GroundFloor', 'direction': 'Horizontal', 'area': 0.81,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'main_occupant_room', 'next_space': 'underfloor'},
                {'name': 'GroundFloor_main', 'type': 'GroundFloor', 'direction': 'Horizontal', 'area': 0.81,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'underfloor', 'next_space': 'main_occupant_room'},
                {'name': 'GroundFloor_other', 'type': 'GroundFloor', 'direction': 'Horizontal', 'area': 0.81,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'other_occupant_room', 'next_space': 'underfloor'},
                {'name': 'GroundFloor_other', 'type': 'GroundFloor', 'direction': 'Horizontal', 'area': 0.81,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'underfloor', 'next_space': 'other_occupant_room'},
                {'name': 'GroundFloor_nonliving', 'type': 'GroundFloor', 'direction': 'Horizontal', 'area': 1.62,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'non_occupant_room', 'next_space': 'underfloor'},
                {'name': 'GroundFloor_nonliving', 'type': 'GroundFloor', 'direction': 'Horizontal', 'area': 1.62,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'underfloor', 'next_space': 'non_occupant_room'},
                {'name': 'InnerFloor_main', 'type': 'InnerFloor', 'direction': 'Horizontal', 'area': 10.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'main_occupant_room', 'next_space': 'other_occupant_room'},
                {'name': 'InnerFloor_main', 'type': 'InnerFloor', 'direction': 'Horizontal', 'area': 20.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'main_occupant_room', 'next_space': 'non_occupant_room'},
                {'name': 'InnerFloor_other', 'type': 'InnerFloor', 'direction': 'Horizontal', 'area': 10.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'other_occupant_room', 'next_space': 'main_occupant_room'},
                {'name': 'InnerFloor_other', 'type': 'InnerFloor', 'direction': 'Horizontal', 'area': 20.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'other_occupant_room', 'next_space': 'non_occupant_room'},
                {'name': 'InnerFloor_nonliving', 'type': 'InnerFloor', 'direction': 'Horizontal', 'area': 30.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'non_occupant_room', 'next_space': 'main_occupant_room'},
                {'name': 'InnerFloor_nonliving', 'type': 'InnerFloor', 'direction': 'Horizontal', 'area': 30.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'non_occupant_room', 'next_space': 'other_occupant_room'},
                {'name': 'InnerCeiling_main', 'type': 'InnerCeiling', 'direction': 'Horizontal', 'area': 10.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'main_occupant_room', 'next_space': 'other_occupant_room'},
                {'name': 'InnerCeiling_main', 'type': 'InnerCeiling', 'direction': 'Horizontal', 'area': 20.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'main_occupant_room', 'next_space': 'non_occupant_room'},
                {'name': 'InnerCeiling_other', 'type': 'InnerCeiling', 'direction': 'Horizontal', 'area': 10.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH':
                     720.0}],
                 'space': 'other_occupant_room', 'next_space': 'main_occupant_room'},
                {'name': 'InnerCeiling_other', 'type': 'InnerCeiling', 'direction': 'Horizontal', 'area': 20.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'other_occupant_room', 'next_space': 'non_occupant_room'},
                {'name': 'InnerCeiling_nonliving', 'type': 'InnerCeiling', 'direction': 'Horizontal', 'area': 30.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'non_occupant_room', 'next_space': 'main_occupant_room'},
                {'name': 'InnerCeiling_nonliving', 'type': 'InnerCeiling', 'direction': 'Horizontal', 'area': 30.0,
                 'Layers': [{'name': 'PED', 'cond': 0.16, 'thick': 0.012, 'specH': 720.0}],
                 'space': 'non_occupant_room', 'next_space': 'other_occupant_room'}
            ]
        }
    }

    equipment_main = {
        'cooling': {
            'main': {'q_rtd_c': 5600, 'q_max_c': 5944.619999999999, 'e_rtd_c': 3.2432},
            'sub': {}
        },
        'heating': {
            'main': {'q_rtd_h': 6685.3, 'q_max_h': 10047.047813999998, 'e_rtd_h': 4.157264},
            'sub': {}}
    }

    equipment_other = {
        'cooling': {
            'main': {'q_rtd_c': 5600, 'q_max_c': 5944.619999999999, 'e_rtd_c': 3.0576},
            'sub': {}
        },
        'heating': {
            'main': {'construct_area': 21.0},
            'sub': {'q_rtd_h': 6685.3, 'q_max_h': 10047.047813999998, 'e_rtd_h': 3.855424}
        }
    }

    natural_vent = {
        'main_occupant_room_natural_vent_time': '5ACH',
        'other_occupant_room_natural_vent_time': '5ACH'
    }

    result1 = convert(
        common=common,
        envelope=d['envelope'],
        d=d,
        equipment_main=equipment_main,
        equipment_other=equipment_other,
        natural_vent=natural_vent)

    pprint.pprint(result1)


