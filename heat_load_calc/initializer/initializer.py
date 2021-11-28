import numpy as np
from typing import Dict, List
import json
import csv
from enum import Enum

import heat_load_calc.initializer.a22_radiative_heating_spec as a22

from heat_load_calc.initializer import schedule_loader
from heat_load_calc.initializer import residents_number
from heat_load_calc.initializer.boundary_type import BoundaryType


class Story(Enum):
    """
    建物の階数（共同住宅の場合は住戸の階数）
    """
    # 1階
    ONE = 1
    # 2階（2階以上の階数の場合も2階とする。）
    TWO = 2


class InsidePressure(Enum):
    """
    室内圧力
    """
    # 正圧
    POSITIVE = 'positive'
    # 負圧
    NEGATIVE = 'negative'
    # ゼロバランス
    BALANCED = 'balanced'


class RoomType(Enum):
    """
    室のタイプ
    """
    # 主たる居室
    MAIN_OCCUPANT_ROOM = 'main_occupant_room'
    # その他の居室
    OTHER_OCCUPANT_ROOM = 'other_occupant_room'
    # 非居室
    NON_OCCUPANT_ROOM = 'non_occupant_room'
    # 床下
    UNDERFLOOR = 'underfloor'


class HeatingEquipmentType(Enum):
    # 設置なし
    NOT_INSTALLED = 'not_installed'
    # 対流暖房
    CONVECTIVE = 'convective'
    # 放射暖房
    RADIATIVE = 'radiative'


class CoolingEquipmentType(Enum):
    # 設置なし
    NOT_INSTALLED = 'not_installed'
    # 対流冷房
    CONVECTIVE = 'convective'
    # 放射冷房
    RADIATIVE = 'radiative'


def make_house(d, input_data_dir, output_data_dir):

    make_mid_data_house(d, output_data_dir)

    rooms = d['rooms']

    # 室iの名称, [i]
    room_name_is = [r['name'] for r in rooms]

    # 室iの床面積, m2, [i]
    a_floor_is = np.array([r['floor_area'] for r in rooms])

    # 床面積の合計, m2
    a_floor_total = a_floor_is.sum()

    # 居住人数
    n_p = residents_number.get_total_number_of_residents(a_floor_total=a_floor_total)

    # 以下のスケジュールの取得, [i, 365*96]
    #   ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
    # 　　ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, 8760*4]
    #   ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    #   ステップnの室iにおける在室人数, [i, 8760*4]
    #   ステップnの室iにおける空調割合, [i, 8760*4]
    q_gen_is_ns, x_gen_is_ns, v_mec_vent_local_is_ns, n_hum_is_ns, ac_demand_is_ns\
        = schedule_loader.get_compiled_schedules(
            n_p=n_p,
            room_name_is=room_name_is,
            a_floor_is=a_floor_is
        )

    # ステップnの室iにおける局所換気量, m3/s, [i, 8760*4]
    with open(output_data_dir + '/mid_data_local_vent.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(v_mec_vent_local_is_ns.T.tolist())

    # ステップnの室iにおける内部発熱, W, [8760*4]
    with open(output_data_dir + '/mid_data_heat_generation.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(q_gen_is_ns.T.tolist())

    # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [8760*4]
    with open(output_data_dir + '/mid_data_moisture_generation.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(x_gen_is_ns.T.tolist())

    # ステップnの室iにおける在室人数, [8760*4]
    with open(output_data_dir + '/mid_data_occupants.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(n_hum_is_ns.T.tolist())

    # ステップnの室iにおける空調需要, [8760*4]
    with open(output_data_dir + '/mid_data_ac_demand.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(ac_demand_is_ns.T.tolist())


def make_mid_data_house(d, output_data_dir):

    building = _make_building(d=d['building'])

    rooms = _make_rooms(rms=d['rooms'])

    boundaries = _make_boundaries(boundaries=d['boundaries'])

    equipments = _make_equipment(rooms=d['rooms'])

    wd = {
        'building': building,
        'rooms': rooms,
        'boundaries': boundaries,
        "mechanical_ventilations": d['mechanical_ventilations'],
        'equipments': equipments
    }

    with open(output_data_dir + '/mid_data_house.json', 'w') as f:
        json.dump(wd, f, indent=4)


def _make_building(d: Dict):
    """
    出力する辞書のうち、　"building" に対応する辞書を作成する。
    Args:
        d: "building" に対応する入力用辞書
    Returns:
        "building" に対応する出力用辞書
    """

    # 建物の階数
    story = Story(d['story'])

    # 建物のC値
    c_value = d['c_value']

    # 室内圧力 = POSITIVE, NEGATIVE, BALANCED
    inside_pressure = InsidePressure(d['inside_pressure'])

    return {
        'infiltration': {
            'method': 'balance_residential',
            'story': story.value,
            'c_value': c_value,
            'inside_pressure': inside_pressure.value
        }
    }


def _make_rooms(rms: List[dict]) -> List[dict]:
    """
    出力する辞書のうち、　"spaces" に対応する辞書を作成する。
    Args:
        rms: "rooms" に対応する入力用辞書
    Returns:
        "rooms" に対応する出力用辞書
    """

    # region 入力ファイル(space_initializer)の"rooms"部分の読み込み

    # 室の数
    n_rms = len(rms)

    # 室のID, [i]
    id_is = [int(r['id']) for r in rms]

    # ID が0始まりで1ずつ増え、一意であることをチェック
    for i, room_id in enumerate(id_is):
        if i != room_id:
            raise ValueError('指定されたroomのIDは0からインクリメントする必要があります。')

    # 室iの名称, [i]
    name_is = [r['name'] for r in rms]

    # 室iのタイプ, [i]
    # 現在、室iのタイプについては使用していない。
    # boundary が接する空間の識別は ID で行っているため。
    # とはいえ、室i がどの種別の部屋なのかの情報は非常に重要であるため、当面の間、この入力項目は残しておく。
    room_type_is = [RoomType(r['room_type']) for r in rms]
    # 主たる居室が必ず指定されていることを確認する。
    check_specifying_room_type(room_type_is=room_type_is, specified_type=RoomType.MAIN_OCCUPANT_ROOM)
    # 主たる居室が複数回指定されていないかどうかを確認する。
    check_not_specifying_multi_room_type(room_type_is=room_type_is, specified_type=RoomType.MAIN_OCCUPANT_ROOM)
    # その他の居室が複数回指定されていないかどうかを確認する。
    check_not_specifying_multi_room_type(room_type_is=room_type_is, specified_type=RoomType.OTHER_OCCUPANT_ROOM)
    # 非居室が複数回指定されていないかどうかを確認する。
    check_not_specifying_multi_room_type(room_type_is=room_type_is, specified_type=RoomType.NON_OCCUPANT_ROOM)
    # 床下が複数回指定されていないかどうかを確認する。
    check_not_specifying_multi_room_type(room_type_is=room_type_is, specified_type=RoomType.UNDERFLOOR)

    # 室iの気積, m3, [i]
    v_rm_is = np.array([r['volume'] for r in rms])

    # 室iの外気からの機械換気量, m3/h, [i]
    v_vent_ex_is = np.array([r['vent'] for r in rms])

    # 室iの自然風利用時の換気回数, 1/h, [i]
    n_ntrl_vent_is = np.array([r['natural_vent_time'] for r in rms])

    # endregion

    # region 出力ファイルに必要なパラメータの作成（必要なもののみ）

    # 室iの自然風利用時の換気量, m3/h, [i]
    # TODO: もしかすると換気回数わたしの方が自然か？
    v_ntrl_vent_is = v_rm_is * n_ntrl_vent_is

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating_is = np.array([a22.read_is_radiative_heating(room) for room in rms])

    # endregion

    spaces = []

    for i in range(n_rms):
        spaces.append({
            'id': id_is[i],
            'name': name_is[i],
            'sub_name': '',
            'volume': v_rm_is[i],
            'ventilation': {
                'mechanical': v_vent_ex_is[i],
                'next_spaces': [
                    {
                        'upstream_room_id': next_vent['upstream_room_id'],
                        'volume': next_vent['volume']
                    } for next_vent in rms[i]['next_vent']
                ],
                'natural': v_ntrl_vent_is[i]
            },
            'furniture': {
                'input_method': 'default'
            }
        })

    return spaces


def _make_equipment(rooms: List[dict]) -> dict:
    """
    出力する辞書のうち、　"equipments" に対応する辞書を作成する。
    Args:
        rooms: 入力ファイルの "rooms" に対応する辞書（リスト形式）
    Returns:
        "equipments" に対応する辞書（リスト形式）
    """

    return {
        'heating_equipments': _make_heating_equipment_dict(rooms),
        'cooling_equipments': _make_cooling_equipment_dict(rooms)
    }


def _make_heating_equipment_dict(rooms):

    heating_equipments = []

    he_id = 0

    for r in rooms:

        # 暖房設備
        he = r['heating_equipment']

        # 暖房形式
        he_type = HeatingEquipmentType(he['equipment_type'])

        # 設置しない
        if he_type == HeatingEquipmentType.NOT_INSTALLED:
            pass

        # 対流暖房方式
        elif he_type == HeatingEquipmentType.CONVECTIVE:

            heating_equipments.append(
                {
                    'id': he_id,
                    'name': 'heating_equipment no.' + str(he_id),
                    'equipment_type': 'rac',
                    'property': {
                        'space_id': r['id'],
                        'q_min': he['convective']['q_min'],
                        'q_max': he['convective']['q_max'],
                        'v_min': he['convective']['v_min'],
                        'v_max': he['convective']['v_max'],
                        'bf': 0.2
                    }
                }
            )

            he_id = he_id + 1

        # 放射暖房方式
        elif he_type == HeatingEquipmentType.RADIATIVE:

            heating_equipments.append(
                {
                    'id': he_id,
                    'name': 'heating_equipment no.' + str(he_id),
                    'equipment_type': 'floor_heating',
                    'property': {
                        'space_id': r['id'],
                        'max_capacity': he['radiative']['max_capacity'],
                        'area': he['radiative']['area']
                    }
                }
            )

            he_id = he_id + 1

        else:
            raise Exception()

    return heating_equipments


def _make_cooling_equipment_dict(rooms):

    cooling_equipments = []

    ce_id = 0

    for r in rooms:

        # 冷房設備
        ce = r['cooling_equipment']

        # 冷房房形式
        ce_type = CoolingEquipmentType(ce['equipment_type'])

        # 設置しない
        if ce_type == CoolingEquipmentType.NOT_INSTALLED:
            pass

        # 対流冷房方式
        elif ce_type == CoolingEquipmentType.CONVECTIVE:

            cooling_equipments.append(
                {
                    'id': ce_id,
                    'name': 'cooling_equipment no.' + str(ce_id),
                    'equipment_type': 'rac',
                    'property': {
                        'space_id': r['id'],
                        'q_min': ce['convective']['q_min'],
                        'q_max': ce['convective']['q_max'],
                        'v_min': ce['convective']['v_min'],
                        'v_max': ce['convective']['v_max'],
                        'bf': 0.2
                    }
                }
            )

            ce_id = ce_id + 1

        # 放射冷房方式
        elif ce_type == CoolingEquipmentType.RADIATIVE:

            cooling_equipments.append(
                {
                    'id': ce_id,
                    'name': 'heating_equipment no.' + str(ce_id),
                    'equipment_type': 'floor_cooling',
                    'property': {
                        'space_id': r['id'],
                        'max_capacity': ce['radiative']['max_capacity'],
                        'area': ce['radiative']['area']
                    }
                }
            )

            ce_id = ce_id + 1

        else:
            raise Exception()

    return cooling_equipments


def check_specifying_room_type(room_type_is: List[RoomType], specified_type: RoomType):
    """
    specified_type で指定された RoomType が必ず1回指定されていることを確認する。
    Args:
        room_type_is: RoomType を格納したリスト
        specified_type: 確認する RoomType
    """
    if room_type_is.count(specified_type) != 1:
        raise ValueError("室タイプ " + specified_type.value + " は必ず指定されなければなりません。")


def check_not_specifying_multi_room_type(room_type_is: List[RoomType], specified_type: RoomType):
    """
    specified_type で指定された RoomType が複数回指定されていないかどうかを確認する。
    Args:
        room_type_is: RoomType を格納したリスト
        specified_type: 確認する RoomType
    """
    if room_type_is.count(specified_type) > 1:
        raise ValueError("室タイプ " + specified_type.value + " が複数回指定されました。")


def _make_boundaries(boundaries: List[Dict]):

    specs = [_get_boundary_spec(b=b) for b in boundaries]

    bdrs = []

    for i, b in enumerate(boundaries):

        bt = BoundaryType(b['boundary_type'])

        bdr = {
            'id': b['id'],
            'name': b['name'],
            'sub_name': '',
            'connected_room_id': b['connected_room_id'],
            'boundary_type': b['boundary_type'],
            'is_ground': True if BoundaryType(b['boundary_type']) == BoundaryType.Ground else False,
            'area': b['area'],
            'h_c': b['h_c'],
            'is_solar_absorbed_inside': b['is_solar_absorbed_inside'],
            'is_floor': bool(b['is_floor']),
            'spec': specs[i],
            'solar_shading_part': b['solar_shading_part']
        }

        if bt in [
            BoundaryType.ExternalGeneralPart, BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart
        ]:
            bdr['is_sun_striked_outside'] = b['is_sun_striked_outside']

            if b['is_sun_striked_outside'] == True:
                bdr['direction'] = b['direction']

        if bt in [
            BoundaryType.ExternalGeneralPart, BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart
        ]:
            bdr['outside_emissivity'] = b['outside_emissivity']

        if bt in [
            BoundaryType.ExternalGeneralPart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalOpaquePart,
            BoundaryType.Internal
        ]:
            bdr['outside_heat_transfer_resistance'] = b['outside_heat_transfer_resistance']

        if bt in [
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalOpaquePart
        ]:
            bdr['u_value'] = b['u_value']

        if bt in [BoundaryType.ExternalTransparentPart]:
            bdr['eta_value'] = b['eta_value']
            bdr['incident_angle_characteristics'] = b['incident_angle_characteristics']
            bdr['glass_area_ratio'] = b['glass_area_ratio']

        if bt in [BoundaryType.ExternalGeneralPart, BoundaryType.ExternalOpaquePart]:
            bdr['outside_solar_absorption'] = b['outside_solar_absorption']

        if bt in [
            BoundaryType.ExternalOpaquePart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalGeneralPart,
            BoundaryType.Ground
        ]:
            bdr['temp_dif_coef'] = b['temp_dif_coef']

        if bt == BoundaryType.Internal:
            bdr['rear_surface_boundary_id'] = int(b['rear_surface_boundary_id'])

        bdrs.append(bdr)

    return bdrs


def _get_boundary_spec(b) -> Dict:

    boundary_type = BoundaryType(b['boundary_type'])

    if boundary_type in [BoundaryType.ExternalGeneralPart]:
        return {
            'method': 'layers',
            'boundary_type': boundary_type.value,
            'layers': b['layers'],
            'outside_heat_transfer_resistance': b['outside_heat_transfer_resistance']
        }
    elif boundary_type in [BoundaryType.Internal]:
        return {
            'method': 'layers',
            'boundary_type': boundary_type.value,
            'layers': b['layers'],
            'outside_heat_transfer_resistance': b['outside_heat_transfer_resistance'],
            'rear_surface_boundary_id': b['rear_surface_boundary_id']
        }
    elif boundary_type == BoundaryType.Ground:
        return {
            'method': 'layers_ground',
            'boundary_type': boundary_type.value,
            'layers': b['layers']
        }
    elif boundary_type in [BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart]:
        return {
            'method': 'u_value',
            'boundary_type': boundary_type.value,
            'u_value': b['u_value'],
            'inside_heat_transfer_resistance': b['inside_heat_transfer_resistance']
        }
    else:
        raise KeyError()

