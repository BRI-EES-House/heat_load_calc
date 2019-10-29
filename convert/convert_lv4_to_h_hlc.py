from typing import Dict, List, Tuple

import pprint

import nbimporter
import copy
import math
import numpy
import json


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

    rooms = make_initial_rooms(
        a_a=a_a, a_mr=a_mr, a_or=a_or, a_nr=a_nr, a_uf=a_uf, n=n, v_nv_mr=v_nv_mr, v_nv_or=v_nv_or)

    d_calc_input['Rooms'] = rooms

    surfaces_mr, surfaces_or, surfaces_nr, surfaces_uf = get_surfaces_wall(region, gps)

    for room in rooms:

        if room['room_type'] == 'main_occupant_room':
            room['surface'].extend(surfaces_mr)
        elif room['room_type'] == 'other_occupant_room':
            room['surface'].extend(surfaces_or)
        elif room['room_type'] == 'non_occupant_room':
            room['surface'].extend(surfaces_nr)
        elif room['room_type'] == 'underfloor':
            room['surface'].extend(surfaces_uf)
        else:
            raise ValueError()


    d_calc_input['Rooms'] = integrate_windows_to_rooms(region, gws, rooms)

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
) -> Dict:
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
        rooms ディクショナリ
    """

    # 室の容積, m3
    v_mr, v_or, v_nr, v_uf = get_room_volume(a_mr, a_or, a_nr, a_uf)

    # 外気から流入する換気量, m3/h
    v_vent_ex_mr, v_vent_ex_or, v_vent_ex_nr, v_vent_ex_uf = get_v_vent_ex(a_a, a_mr, a_or, n)

    # 室間の換気量, m3/h
    v_vent_mr_nr, v_vent_or_nr = get_v_vent(v_vent_ex_mr, v_vent_ex_or)

    c_value = 5.0  # ここは住宅構造やUA値等から何らかの設定が必要

    rooms = []

    if a_mr <= 0.0:
        raise ValueError('主たる居室の面積が0m2になっています。')

    rooms.append({
            'name': 'main_occupant_room',
            'room_type': 'main_occupant_room',
            'volume': v_mr,
            'vent': v_vent_ex_mr,
            'next_vent': [],
            'c_value': c_value,
            'natural_vent_time': v_nv_mr,
            'boundaries': [],
        })

    if a_or > 0.0:

        rooms.append({
            'name': 'other_occupant_room',
            'room_type': 'other_occupant_room',
            'volume': v_or,
            'vent': v_vent_ex_or,
            'next_vent': [],
            'c_value': c_value,
            'natural_vent_time': v_nv_or,
            'boundaries': [],
        })

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

        rooms.append({
            'name': 'non_occupant_room',
            'room_type': 'non_occupant_room',
            'volume': v_nr,
            'vent': v_vent_ex_nr,
            'next_vent': next_vent,
            'c_value': c_value,
            'natural_vent_time': 0.0,
            'boundaries': [],
        })

    if a_uf > 0.0:

        rooms.append({
            'name': 'underfloor',
            'room_type': 'underfloor',
            'volume': v_uf,
            'vent': v_vent_ex_uf,
            'next_vent': [],
            'c_value': c_value,
            'natural_vent_time': 0.0,
            'boundaries': [],
        })

    return rooms


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


def get_surfaces_wall(region, general_parts):

    n = {'Roof': 1, 'Ceiling': 1, 'Wall': 1, 'Floor': 1, 'BoundaryCeiling': 1, 'BoundaryWall': 1, 'BoundaryFloor': 1}

    surfaces_mr = []
    surfaces_or = []
    surfaces_nr = []
    surfaces_uf = []

    for gp in general_parts:

        gp_type = gp['general_part_type']
        next_space = gp['next_space']
        spec = gp['spec']

        r_surf_i, r_surf_o = get_r_surf(general_part_type=gp_type, next_space=next_space)

        if spec['structure'] == 'wood':
            if spec['u_value_input_method_wood'] == 'u_value_directly':
                parts = get_parts_u_value_directly(
                    general_part_type=gp_type,
                    structure='wood',
                    u_target=spec['u_value'],
                    r_surf_i=r_surf_i,
                    r_surf_o=r_surf_o)
            elif spec['u_value_input_method_wood'] == 'detail_method':
                parts = get_parts_detail_method(spec['parts'])
            elif spec['u_value_input_method_wood'] == 'area_ratio_method':
                parts = get_parts_area_ratio_method(general_part_type=gp_type, spec=spec)
            elif spec['u_value_input_method_wood'] == 'r_corrected_method':
                raise KeyError('熱貫流率補正法は実装していません。')
            else:
                raise ValueError()
        elif gp['spec']['structure'] == 'rc':
            if spec['u_value_input_method_rc'] == 'u_value_directly':
                parts = get_parts_u_value_directly(
                    general_part_type=gp_type,
                    structure='rc',
                    u_target=spec['u_value'],
                    r_surf_i=r_surf_i,
                    r_surf_o=r_surf_o)
            elif spec['u_value_input_method_rc'] == 'detail_method':
                parts = get_parts_detail_method(spec['parts'])
            else:
                raise ValueError()
        elif spec['structure'] == 'steel':
            if spec['u_value_input_method_steel'] == 'u_value_directly':
                parts = get_parts_u_value_directly(
                    general_part_type=gp_type,
                    structure='steel',
                    u_target=spec['u_value'],
                    r_surf_i=r_surf_i,
                    r_surf_o=r_surf_o)
            elif spec['u_value_input_method_steel'] == 'detail_method':
                parts = get_parts_detail_method_steel(
                    u_r_value_steel=gp['u_r_value_steel'],
                    spec=spec,
                    r_surf_i=r_surf_i,
                    r_surf_o=r_surf_o)
            else:
                raise ValueError()
        elif spec['structure'] == 'other':
            parts = get_parts_u_value_directly(
                general_part_type=gp_type,
                structure='steel',
                u_target=spec['u_value'],
                r_surf_i=r_surf_i,
                r_surf_o=r_surf_o)
        else:
            raise ValueError()

        for part in parts:
            surface = {
                'skin': True,
                'direction': get_direction_from_direction_for_outer_skin(
                    gp['direction'] if gp['next_space'] == 'Outdoor' else gp['next_space']),
                'floor': True if gp['direction'] == 'Bottom' else False,
                'boundary': get_boundary_for_outer_skin(region, gp['next_space'], gp['direction']),
                'unsteady': True,
                'IsSoil': False,
                'name': gp['type'] + str(n[gp['type']]),
                'area': gp['area'],
                'flr': 0,
                'Wall': {
                    'OutEmissiv': 0.9,
                    'OutSolarAbs': 0.8,
                    'OutHeatTrans': 1 / r_surf_o,
                    'InHeatTrans': 1 / r_surf_i,
                    'Layers': gp['Layers']
                },
                'sunbreak': {'D': gp['Z'], 'WI1': 500, 'WI2': 500, 'hi': gp['Y1'], 'WR': 0, 'WH': gp['Y2'],
                             'name': 'ひさし'} if gp['IsSunshadeInput'] == True else {}
            }

            if gp['space_type'] == 'main_occupant_room':
                surfaces_mr.append(surface)
            elif gp['space_type'] == 'other_occupant_room':
                surfaces_or.append(surface)
            elif gp['space_type'] == 'non_occupant_room':
                surfaces_nr.append(surface)
            elif gp['space_type'] == 'under_floor':
                surfaces_uf.append(surface)
            else:
                raise ValueError()

            n[gp['type']] = n[gp['type']] + 1

    return surfaces_mr, surfaces_or, surfaces_nr, surfaces_uf


def get_r_surf(general_part_type: str, next_space: str) -> (float, float):
    """
    表面熱伝達抵抗を取得する。
    Args:
        general_part_type: 一般部位の種類（以下の値をとる）
            ceiling: 天井
            roof: 屋根
            wall: 壁
            floor: 床
            boundary_wall: 界壁
            upward_boundary_floor: 上界側界床
            downward_boundary_floor: 下界側界床
        next_space: 隣接空間の種類（以下の値をとる）
            outdoor: 外気
            open_space: 外気に通じる空間
            closed_space: 外気に通じていない空間
            open_underfloor: 外気に通じる床裏
            air_conditioned: 住戸及び住戸と同様の熱的環境の空間
            closed_underfloor: 外気に通じていない床裏
    Returns:
        表面熱伝達抵抗, m2K/W
            (1) 室内側
            (2) 室外側
    """

    if general_part_type == 'roof':

        if next_space == 'outdoor':
            return 0.09, 0.04
        else:
            return 0.09, 0.09

    elif general_part_type == 'ceiling':

        if next_space == 'outdoor':
            raise ValueError('「部位の種類」が「天井」の場合に「外気の種類」として「外気」は選択できません。')
        else:
            return 0.09, 0.09

    elif general_part_type == 'wall':

        if next_space == 'outdoor':
            return 0.11, 0.04
        else:
            return 0.11, 0.11

    elif general_part_type == 'floor':

        if next_space == 'outdoor':
            return 0.15, 0.04
        else:
            return 0.15, 0.15

    elif general_part_type == 'boundary_wall':

        if next_space == 'air_conditioned':
            return 0.11, 0.11
        else:
            raise ValueError('「部位の種類」が「界壁」の場合は「外気の種類」に「住戸及び住戸と同様の熱的環境の空間」を指定する必要があります。')

    elif general_part_type == 'upward_boundary_floor':

        if next_space == 'air_conditioned':
            return 0.09, 0.09
        else:
            raise ValueError('「部位の種類」が「上階側界床」の場合は「外気の種類」に「住戸及び住戸と同様の熱的環境の空間」を指定する必要があります。')

    elif general_part_type == 'downward_boundary_floor':

        if next_space == 'air_conditioned':
            return 0.15, 0.15
        else:
            raise ValueError('「部位の種類」が「下界側界床」の場合は「外気の種類」に「住戸及び住戸と同様の熱的環境の空間」を指定する必要があります。')
    else:

        raise ValueError()


def get_parts_u_value_directly(
        general_part_type: str, structure: str, u_target: float, r_surf_i, r_surf_o) -> List[Dict]:
    """general_part の parts を作成する

    general_part の parts を作成する。
    parts は 配列であるが、配列数は必ず1をとる。

    Args:
        general_part_type: 一般部位の種類（以下の値をとる）
            ceiling: 天井
            roof: 屋根
            wall: 壁
            floor: 床
            boundary_wall: 界壁
            upward_boundary_floor: 上界側界床
            downward_boundary_floor: 下界側界床
        structure: 一般部位の構造（以下の値をとる）
            wood: 木造
            rc: 鉄筋コンクリート造等
            steel: 鉄骨造
            other: その他／不明
        u_target: 目標とするU値, W/m2K
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W
    Returns:
        一般部位のパートの配列（辞書型）
        {
            name(str): 部分（パート）の名前
            area_ratio(int): 面積比率
            layers(dict): {
                name(str): 層の名前
                heat_resistance_input_method(str): 断熱性能の入力方法（以下の値をとる）
                    conductivity: 熱伝導率から計算する
                    resistance: 熱抵抗を直接入力する
                thermal_conductivity(float): 熱伝導率, W/mK
                volumetric_specific_heat(float): 容積比熱, J/LK
                thickness(float): 厚さ, m
            }
        }
    """

    # 層構成を取得する
    layer_names = get_layer_names(general_part_type, structure)

    # 断熱材以外の熱抵抗(リスト)
    r_others_sum = get_r_others_sum(layer_names)

    # 断熱材
    # 断熱材の熱伝導率, W/mK
    lambda_ins = 0.045
    # 断熱材の体積熱容量, J/LK
    c_ins = 13.0

    # 断熱材の厚さ(m)の推定
    t_ins = get_t_ins(
        u_target=u_target, r_surf_o=r_surf_o, r_surf_i=r_surf_i, r_others_sum=r_others_sum, lambda_res=lambda_ins)

    def make_layer(name):

        if name == 'gypsum_board' or name == 'concrete' or name == 'plywood':
            m = get_material(name)
            return {
                'name': name,
                'heat_resistance_input_method': 'conductivity',
                'thermal_conductivity': m['thermal_conductivity'],
                'thickness': m['thickness'],
                'volumetric_specific_heat': m['volumetric_specific_heat'],
            }
        elif name == 'insulation':
            return {
                'name': 'insulation',
                'heat_resistance_input_method': 'conductivity',
                'thermal_conductivity': lambda_ins,
                'thickness': t_ins,
                'volumetric_specific_heat': c_ins,
            }

    layers = [make_layer(name) for name in layer_names]

    # 配列長さ1のリストを返す。
    return [
        {
            'name': 'part_inputed_by_u_value_directly',
            'area_ratio': 1.0,
            'layers': layers,
        }
    ]


def get_layer_names(general_part_type: str, structure: str) -> List[str]:
    """
    想定する層の材料名称のリストを取得する。
    Args:
        general_part_type: 一般部位の種類（以下の値をとる）
            ceiling: 天井
            roof: 屋根
            wall: 壁
            floor: 床
            boundary_wall: 界壁
            upward_boundary_floor: 上界側界床
            downward_boundary_floor: 下界側界床
        structure: 一般部位の構造（以下の値をとる）
            wood: 木造
            rc: 鉄筋コンクリート造等
            steel: 鉄骨造
            other: その他／不明
    Returns:
        層を構成する材料名のリスト
    """

    if structure == 'wood' or structure == 'steel' or structure == 'other':

        return {
            'roof': ['gypsum_board', 'insulation'],
            'ceiling': ['gypsum_board', 'insulation'],
            'wall': ['gypsum_board', 'insulation'],
            'floor': ['plywood', 'plywood', 'insulation'],
            'boundary_wall': ['gypsum_board', 'insulation', 'gypsum_board'],
            'upward_boundary_floor': ['gypsum_board', 'insulation', 'plywood', 'plywood'],
            'downward_boundary_floor': ['plywood', 'plywood', 'insulation', 'gypsum_board'],
        }[general_part_type]

    elif structure == 'rc':

        return {
            'roof': ['gypsum_board', 'insulation', 'concrete'],
            'ceiling': ['gypsum_board', 'insulation', 'concrete'],
            'wall': ['gypsum_board', 'insulation', 'concrete'],
            'floor': ['plywood', 'plywood', 'insulation', 'concrete'],
            'boundary_wall': ['gypsum_board', 'insulation', 'concrete', 'insulation', 'gypsum_board'],
            'upward_boundary_floor': ['gypsum_board', 'concrete', 'insulation', 'plywood', 'plywood'],
            'downward_boundary_floor': ['plywood', 'plywood', 'insulation', 'concrete', 'gypsum_board'],
        }[general_part_type]

    else:

        raise ValueError


def get_material(name: str) -> Dict:
    """
    指定した材料名の物性値を取得する。
    Args:
        name: 物性名
            ここで指定できる物性名は以下の通り。
                gypsum_board: せっこうボード
                concrete: コンクリート
                plywood: 合板

    Returns:
        物性値をいれた辞書
            {
                conductivity(float): 熱伝導率, W/mK,
                specific_heat(float): 体積熱容量, J/LK,
                thickness(float): 厚さ, m,
            }
    """

    return {
        'gypsum_board': {
            'thermal_conductivity': 0.22,
            'volumetric_specific_heat': 830.0,
            'thickness': 0.0095,
        },
        'concrete': {
            'thermal_conductivity': 1.6,
            'volumetric_specific_heat': 2000.0,
            'thickness': 0.120,
        },
        'plywood': {
            'thermal_conductivity': 0.16,
            'volumetric_specific_heat': 720.0,
            'thickness': 0.012,
        }
    }[name]


def get_t_ins(
        u_target: float, r_surf_o: float, r_surf_i: float, r_others_sum: float, lambda_res: float) -> float:
    """
    Args:
        u_target: 目標とするU値, W/m2K
        r_surf_o: 室外側熱伝達抵抗, m2K/W
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_others_sum: 断熱材以外の層の熱抵抗の合計, m2K/W
        lambda_res: 断熱材の熱伝導率, W/mK
    Returns:
        断熱材の厚さ, m
    """
    return max(0.0, (1 / u_target - r_surf_o - r_others_sum - r_surf_i) * lambda_res)


def get_r_others_sum(names: List[str]) -> float:
    """
    Args:
        names: 層を構成する物質の名称
    Returns:
        断熱材を除く層の熱抵抗の合計, m2K/W
    """

    def calc_resistance(name):
        m = get_material(name)
        return m['thickness'] / m['thermal_conductivity']

    return sum([calc_resistance(name) for name in names if name != 'insulation'])


def get_parts_detail_method(parts: List[dict]) -> List[dict]:
    """
    parts リストからpartsリストを作成

    詳細計算法のため、ここでは何もせず、area_ratioを追加するのみである。
    引数としてのpartsはリスト形式であるが、面積比率法を使用する場合以外は常にリスト長は1である。
    ここでは、リスト長が1以外であった場合のエラー処理も行う。

    Args:
        parts: 一般部位の部分。リスト形式であるがリスト長は必ず1。以下の辞書型のリスト。
            {
                name(str) : 部分の名称
                part_type(str) : 部分の種類（本関数では使用しない）
                layers(List[dict]) : 層の物性値（層の名前・断熱性能の入力方法・熱伝導率・熱抵抗・容積比熱・厚さからなる辞書）のリスト
            }
    Returns:
        一般部位の部分。リスト形式であるがリスト長は必ず1。以下の辞書型のリスト。
            {
                name(str) : 部分の名称
                area_ratio(float) : 面積比率（ここでは必ず1.0）
                layers(List[dict]) : [
                    {
                        name(str): 層の名前
                        heat_resistance_input_method(str): 断熱性能の入力方法（以下の値をとる）
                        conductivity: 熱伝導率から計算する
                        resistance: 熱抵抗を直接入力する
                        thermal_conductivity(float): 熱伝導率, W/mK
                        volumetric_specific_heat(float): 容積比熱, J/LK
                        thickness(float): 厚さ, m
                    }
                ]
            }

    """

    if len(parts) != 1:
        raise ValueError('与えられたpartsのリスト数が1ではありません。')

    part = parts[0]

    return [
        {
            'name': part['name'],
            'area_ratio': 1.0,
            'layers': copy.deepcopy(part['layers']),
        }
    ]


def get_parts_area_ratio_method(general_part_type: str, spec: Dict) -> List[Dict]:
    """
    面積比率法を用いてpartsリストを作成
    Args:
        general_part_type: 一般部位の種類（以下の値をとる）
            ceiling: 天井
            roof: 屋根
            wall: 壁
            floor: 床
            boundary_wall: 界壁
            upward_boundary_floor: 上界側界床
            downward_boundary_floor: 下界側界床
        spec: 仕様。以下の辞書型
                structure(str): 構造種別（以下の値をとる）
                    wood: 木造
                    rc: 鉄筋コンクリート造等
                    steel: 鉄骨造
                    other: その他／不明
                u_value_input_method_wood(str): U値の入力方法（木造）（以下の値をとる）
                    u_value_directly: U値を入力
                    detail_method: 詳細計算法
                    area_ratio_method: 面積比率法
                    r_corrected_mothod: 熱貫流率補正法
                u_value_input_method_rc(str): U値の入力方法（鉄筋コンクリート造等）（以下の値をとる）
                    u_value_directly(str): U値を入力
                    detail_method(str): 詳細計算法
                u_value_input_method_steel(str):U値の入力方法（鉄骨造）（以下の値をとる）
                    u_value_directly(str): U値を入力
                    detail_method(str): 詳細計算法
                u_value(float): 熱貫流率
                floor_construction_method(str): 床の工法の種類（以下の値をとる）
                    frame_beam_joist_insulation: 軸組構法・床梁工法（根太間に断熱）
                    footing_joist_insulation: 軸組構法・束立大引工法（根太間に断熱）
                    footing_sleeper_insulation: 軸組構法・束立大引工法（大引間に断熱）
                    footing_joist_sleeper_insulation: 軸組構法・束立大引工法（根太間及び大引間に断熱）
                    rigid_floor: 軸組構法・剛床工法
                    same_surface_joist_insulation: 軸組構法・床梁土台同面工法（根太間に断熱）
                    frame_wall_joist_insulation: 枠組壁工法（根太間に断熱）
                wall_construction_method(str): 壁の工法の種類（以下の値をとる）
                    frame_beam: 軸組構法（柱・間柱間に断熱）
                    frame_beam_additional_insulation_horizontal: 軸組構法（柱・間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
                    frame_beam_additional_insulation_vertical: 軸組構法（柱、間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））
                    frame_wall: 枠組壁工法（たて枠間に断熱）
                    frame_wall_additional_insulation_horizontal: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
                    frame_wall_additional_insulation_vertical: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））
                ceiling_construction_method(str):天井の工法の種類（以下の値をとる）
                    beam_insulation: 桁・梁間に断熱
                roof_construction_method(str):屋根の工法の種類（以下の値をとる）
                    rafter_insulation: たるき間に断熱
                    rafter_additional_insulation: たるき間に断熱し付加断熱（横下地）
                parts: 一般部位の部分。リスト形式。面積比率法に限り要素数は1以上をとり得る。以下の辞書型のリスト。
                    name(str) : 部分の名称
                    part_type(str) : 部分の種類（以下の値をとる）
                        ins: 断熱
                        hb: 熱橋
                        ins_ins:
                        ins_ins: 断熱＋断熱
                        ins_hb: 断熱＋熱橋
                        hb_ins: 熱橋＋断熱
                        hb_hb: 熱橋＋熱橋
                        magsa_ins: まぐさ＋断熱
                        magsa_hb: まぐさ＋熱橋
                    layers(List[dict]) : 層の物性値（層の名前・断熱性能の入力方法・熱伝導率・熱抵抗・容積比熱・厚さからなる辞書）のリスト
    Returns:
    """

    # 面積比を取得
    # area_ratio は第一引数は部分の種類、第二引数は面積比率
    area_ratios = get_area_ratios(general_part_type, spec)

    def make_part(area_ratio):
        # area_ratio は第一引数は部分の種類、第二引数は面積比率
        k = area_ratio[0]
        v = area_ratio[1]
        ps = [p for p in spec['parts'] if p['part_type'] == k]
        if len(ps) != 1:
            raise ValueError()
        p = ps[0]
        return {
            'name': p['name'],
            'area_ratio': v,
            'layers': copy.deepcopy(p['layers']),
        }

    return [make_part(area_ratio) for area_ratio in area_ratios]


def get_area_ratios(general_part_type: str, spec: Dict) -> List[Tuple[str, float]]:
    """
    一般部位の部分の面積比率を取得する
    Args:
        general_part_type: 一般部位の種類
        spec: 仕様
    Returns:
        面積比率の辞書型（keyは以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分(柱・間柱間断熱材+付加断熱材)
            ins_hb: 断熱部分+熱橋部分(柱・間柱間断熱材+付加断熱層内熱橋部)
            hb_ins: 断熱部分＋熱橋部分(構造部材等+付加断熱材)
            hb_hb: 熱橋部分(構造部材等+付加断熱層内熱橋部)
            magsa_ins: 断熱部分＋熱橋部分(まぐさ+付加断熱材)
            magsa_hb: 熱橋部分(まぐさ+付加断熱層内熱橋部)
    """

    if general_part_type == 'floor'\
            or general_part_type == 'upward_boundary_floor' \
            or general_part_type == 'downward_boundary_floor':

        return get_area_ratio_wood_floor(spec['floor_construction_method'])

    elif general_part_type == 'wall' \
            or general_part_type == 'boundary_wall':

        return get_area_ratio_wood_wall(spec['wall_construction_method'])

    elif general_part_type == 'ceiling':

        return get_area_ratio_wood_ceiling(spec['ceiling_construction_method'])

    elif general_part_type == 'roof':

        return get_area_ratio_wood_roof(spec['roof_construction_method'])

    else:

        raise ValueError()


def get_area_ratio_wood_floor(floor_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造床の部分の面積比率を取得する
    Args:
        floor_construction_method: 床の工法種類（以下の値をとる）
            1 frame_beam_joist_insulation: 軸組構法・床梁工法（根太間に断熱）
            2 footing_joist_insulation: 軸組構法・束立大引工法（根太間に断熱）
            3 footing_sleeper_insulation: 軸組構法・束立大引工法（大引間に断熱）
            4 footing_joist_sleeper_insulation: 軸組構法・束立大引工法（根太間及び大引間に断熱）
            5 rigid_floor: 軸組構法・剛床工法
            6 same_surface_joist_insulation: 軸組構法・床梁土台同面工法（根太間に断熱）
            7 frame_wall_joist_insulation: 枠組壁工法（根太間に断熱）
    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分(根太間断熱材+大引間断熱材)
            ins_hb: 断熱部分+熱橋部分(根太間断熱材+大引材等)
            hb_ins: 断熱部分＋熱橋部分(根太材+大引間断熱材)
            hb_hb: 熱橋部分(根太材+大引材等)
    """

    return {
        'frame_beam_joist_insulation': [('ins', 0.80), ('hb', 0.20)],
        'footing_joist_insulation': [('ins', 0.80), ('hb', 0.20)],
        'footing_sleeper_insulation': [('ins', 0.85), ('hb', 0.15)],
        'footing_joist_sleeper_insulation': [
            ('ins_ins', 0.72), ('ins_hb', 0.12), ('hb_ins', 0.13), ('hb_hb', 0.03)],
        'rigid_floor': [('ins', 0.85), ('hb', 0.15)],
        'same_surface_joist_insulation': [('ins', 0.70), ('hb', 0.30)],
        'frame_wall_joist_insulation': [('ins', 0.87), ('hb', 0.13)]
    }[floor_construction_method]


def get_area_ratio_wood_wall(wall_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造壁の部分の面積比率を取得する
    Args:
        wall_construction_method: 壁の工法種類（以下の値をとる）
            1 frame_beam:軸組構法（柱・間柱間に断熱）
            2 frame_beam_additional_insulation_horizontal: 軸組構法（柱・間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
            3 frame_beam_additional_insulation_vertical: 軸組構法（柱、間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））
            4 frame_wall: 枠組壁工法（たて枠間に断熱）
            5 frame_wall_additional_insulation_horizontal: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
            6 frame_wall_additional_insulation_vertical: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））
    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分(柱・間柱間断熱材+付加断熱材)
            ins_hb: 断熱部分+熱橋部分(柱・間柱間断熱材+付加断熱層内熱橋部)
            hb_ins: 断熱部分＋熱橋部分(構造部材等+付加断熱材)
            hb_hb: 熱橋部分(構造部材等+付加断熱層内熱橋部)
            magsa_ins: 断熱部分＋熱橋部分(まぐさ+付加断熱材)
            magsa_hb: 熱橋部分(まぐさ+付加断熱層内熱橋部)
    """

    return {
        'frame_beam': [('ins', 0.83), ('hb', 0.17)],
        'frame_beam_additional_insulation_horizontal': [
            ('ins_ins', 0.75), ('ins_hb', 0.08), ('hb_ins', 0.12), ('hb_hb', 0.05)],
        'frame_beam_additional_insulation_vertical': [
            ('ins_ins', 0.79), ('ins_hb', 0.04), ('hb_ins', 0.04), ('hb_hb', 0.13)],
        'frame_wall': [
            ('ins', 0.77), ('hb', 0.23)],
        'frame_wall_additional_insulation_horizontal': [
            ('ins_ins', 0.69), ('ins_hb', 0.08), ('hb_ins', 0.14),
            ('magsa_ins', 0.02), ('hb_hb', 0.06), ('magsa_hb', 0.01)],
        'frame_wall_additional_insulation_vertical': [
            ('ins_ins', 0.76), ('ins_hb', 0.01), ('magsa_ins', 0.02), ('hb_hb', 0.20), ('magsa_hb', 0.01)]
    }[wall_construction_method]


def get_area_ratio_wood_ceiling(ceiling_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造天井の部分の面積比率を取得する
    Args:
        ceiling_construction_method: 天井の工法種類（以下の値をとる）
            1 beam_insulation: 桁・梁間に断熱
    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
    """

    return {
        'beam_insulation': [('ins', 0.83), ('hb', 0.17)]
    }[ceiling_construction_method]


def get_area_ratio_wood_roof(roof_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造屋根の部分の面積比率を取得する
    Args:
        roof_construction_method: 屋根の工法種類（以下の値をとる）
            rafter_insulation: たるき間に断熱
            rafter_additional_insulation: たるき間に断熱し付加断熱（横下地）
    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分（たる木間断熱材＋付加断熱材）
            ins_hb: 断熱部分＋熱橋部分（たる木間断熱材＋付加断熱層内熱橋部（下地たる木））
            hb_ins: 断熱部分＋熱橋部分（構造部材＋付加断熱材）
            hb_hb: 熱橋部分（構造部材＋付加断熱層内熱橋部（下地たる木））
    """

    return {
        'rafter_insulation': [('ins', 0.86), ('hb', 0.14)],
        'rafter_additional_insulation': [
            ('ins_ins', 0.79), ('ins_hb', 0.08), ('hb_ins', 0.12), ('hb_hb', 0.019)],
    }[roof_construction_method]


def get_parts_detail_method_steel(
        u_r_value_steel: float, spec: dict, r_surf_i: float, r_surf_o: float) -> List[dict]:
    """
    parts リストからpartsリストを作成
    Args:
        u_r_value_steel: 補正熱貫流率（Ur値）（鉄骨造）, W/m2K
        spec: 仕様。以下の辞書型
            structure(str): 構造種別 本メソッドでは steel が指定されている。
            u_value_input_method_steel(str):U値の入力方法（鉄骨造） 本メソッドでは detail_method が指定されている。
            u_value(float): 熱貫流率
            parts: 一般部位の部分。リスト形式。本メソッドではリスト長さは必ず１が指定されているはずである。
                name(str) : 部分の名称
                layers(List[dict]): 層を表す辞書型のリスト。辞書型は以下のkeyをもつ。
                    name(str): 層の名前
                    heat_resistance_input_method(str): 断熱性能の入力方法（以下の値をとる）
                    conductivity: 熱伝導率から計算する
                    resistance: 熱抵抗を直接入力する
                    thermal_conductivity(float): 熱伝導率, W/mK
                    volumetric_specific_heat(float): 容積比熱, J/LK
                    thickness(float): 厚さ, m
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W
    Returns:
        一般部位の部分。リスト形式であるがリスト長は必ず1。以下の辞書型のリスト。
                name(str) : 部分の名称
                area_ratio(float) : 面積比率（ここでは必ず1.0）
                layers(List[dict]) : 層の物性値（層の名前・断熱性能の入力方法・熱伝導率・熱抵抗・容積比熱・厚さからなる辞書）のリスト
    Notes:
        詳細計算法のため、ここでは何もせず、area_ratioを追加するのみである。
        引数としてのpartsはリスト形式であるが、面積比率法を使用する場合以外は常にリスト長は1である。
        ここでは、リスト長が1以外であった場合のエラー処理も行う。
        鉄骨造の場合に限り、補正熱貫流率を入力する
    """

    parts = spec['parts']

    if len(parts) != 1:
        raise ValueError('与えられたpartsのリスト数が1ではありません。')

    part = parts[0]

    layers = part['layers']

    r_layers = get_r_layers(layers=layers)

    u = get_u_steel(r_layers=r_layers, r_i=r_surf_i, r_o=r_surf_o)

    u_cor = get_u_steel_cor(u, u_r_value_steel)

    c_res = get_r_red(r_layers, u_cor, r_surf_i, r_surf_o)

    if c_res > 0.0:
        alt_layers = [make_alt_layer(layer, c_res) for layer in layers]
    else:
        alt_layers = []

    return [
        {
            'name': part['name'],
            'area_ratio': 1.0,
            'layers': alt_layers,
        }
    ]


def get_r_layers(layers: List[Dict]) -> float:
    """
    部位の部分の熱伝達抵抗の合計（表面熱伝達抵抗を除く）を計算する
    Args:
        layers : layer を表す辞書型のリスト（辞書型は以下の値をとる）
            name(str): 層の名前
            heat_resistance_input_method(str): 断熱性能の入力方法（以下の値をとる）
                conductivity: 熱伝導率から計算する
                resistance: 熱抵抗を直接入力する
            thermal_conductivity(float): 熱伝導率, W/mK
            thermal_resistance(float): 熱抵抗, m2K/W
            volumetric_specific_heat(float): 容積比熱, J/LK
            thickness(float): 厚さ, m
    Returns:
        部位の部分の熱伝達抵抗の合計（表面熱伝達抵抗を除く）, m2K/W
    """

    def get_r(layer: Dict) -> float:
        """
        Args:
            layer : 層を表す辞書型（以下の値をとる）
                name(str): 層の名前
                heat_resistance_input_method(str): 断熱性能の入力方法（以下の値をとる）
                    conductivity: 熱伝導率から計算する
                    resistance: 熱抵抗を直接入力する
                thermal_conductivity(float): 熱伝導率, W/mK
                thermal_resistance(float): 熱抵抗, m2K/W
                volumetric_specific_heat(float): 容積比熱, J/LK
                thickness(float): 厚さ, m
        Returns:
            熱抵抗, m2K/W
        """

        if layer['heat_resistance_input_method'] == 'conductivity':
            return layer['thickness'] / layer['thermal_conductivity']
        elif layer['heat_resistance_input_method'] == 'resistance':
            return layer['thermal_resistance']
        else:
            raise KeyError()

    return sum([get_r(layer) for layer in layers])


def get_u_steel(r_layers: float, r_i: float, r_o: float) -> float:
    """部位の部分のU値を計算する
    Args:
        r_layers : 熱伝達抵抗の合計（表面熱伝達抵抗を除く）, m2K/W
        r_i : 室内側熱伝達抵抗, m2K/W
        r_o : 室外側熱伝達抵抗, m2K/W

    Returns:
        熱貫流率, W/m2K
    """

    return 1 / (r_i + r_layers + r_o)


def make_alt_layer(layer: Dict, r_red: float) -> Dict:
    """
    Args:
        layer: 層
        r_red: 厚さ・熱抵抗に乗じる補正係数
    Returns:
        層
    """

    if layer['heat_resistance_input_method'] == 'conductivity':
        return {
            'name': layer['name'],
            'heat_resistance_input_method': layer['heat_resistance_input_method'],
            'thermal_conductivity': layer['thermal_conductivity'],
            'thickness': layer['thickness'] * r_red,
            'volumetric_specific_heat': layer['volumetric_specific_heat'],
        }
    elif layer['heat_resistance_input_method'] == 'resistance':
        return {
            'name': layer['name'],
            'heat_resistance_input_method': layer['heat_resistance_input_method'],
            'thermal_resistance': layer['thermal_resistance'] * r_red,
            'thickness': layer['thickness'] * r_red,
            'volumetric_specific_heat': layer['volumetric_specific_heat'],
        }
    else:
        raise KeyError()


def get_u_steel_cor(u_g: float, u_r: float) -> float:
    """
    Args:
        u_g: もともとのU値, W/m2K
        u_r: 補正熱貫流率（熱橋）, W/m2K
    Returns:
        結果として補正されたU値, W/m2K
    """

    return u_g + u_r


def get_r_red(r_material: float, u_target: float, r_i: float, r_o: float) -> float:
    """
    Args:
        r_material: 熱橋を考慮していない場合の各層の熱抵抗の合計, m2K/W
        u_target: 目標とするU値, W/m2K
        r_i: 室内側熱伝達抵抗, m2K/W
        r_o: 室外側熱伝達抵抗, m2K/W
    Returns:
        熱抵抗に乗じる補正値
    """

    r_target = max(0.0, 1 / u_target - r_i - r_o)

    return r_target / r_material


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

        r_i, r_o = get_r_surf(general_part_type=x['general_part'], next_space=x['next_space'])

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


def integrate_windows_to_rooms(region, d_windows, d_rooms):
    n = 1
    for x in d_windows:
        for y in d_rooms:
            if x['space'] == y['room_type']:
                eta = get_eta(x)
                y['Surface'].append({
                    'skin': True,
                    'direction': get_direction_from_direction_for_outer_skin(x['direction']),
                    'floor': True if x['direction'] == 'Bottom' else False,
                    'boundary': get_boundary_for_outer_skin(region, x['nextspace'], x['direction']),
                    'unsteady': False,
                    'name': 'Window' + str(n),
                    'area': x['area'],
                    'flr': 0,
                    'Window': {
                        'Eta': eta,
                        'SolarTrans': eta,
                        'SolarAbsorp': 0,
                        'UW': x['UW'],
                        'OutEmissiv': 0.9,
                        'OutHeatTrans': 1 / 0.04,
                        'InHeatTrans': 1 / 0.11,
                    },
                    'sunbreak': {'D': x['Z'], 'WI1': 500, 'WI2': 500, 'hi': x['Y1'], 'WR': 0, 'WH': x['Y2'],
                                 'name': 'ひさし'} if x['IsSunshadeInput'] == True else {}
                })
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


