import numpy as np
from typing import Dict, List
import json
import csv
import pandas as pd
from enum import Enum

import heat_load_calc.initializer.a12_indoor_radiative_heat_transfer as a12
import heat_load_calc.initializer.a22_radiative_heating_spec as a22

from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.initializer.boundary_simple import BoundarySimple

from heat_load_calc.initializer import schedule_loader
from heat_load_calc.initializer import residents_number
from heat_load_calc.initializer import occupants_form_factor
from heat_load_calc.initializer import boundary_simple
from heat_load_calc.initializer import furniture
from heat_load_calc.initializer.shape_factor import get_h_r_js


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

    # 以下の気象データの読み込み
    # 外気温度, degree C, [n]
    # 外気絶対湿度, kg/kg(DA), [n]
    # 法線面直達日射量, W/m2, [n]
    # 水平面天空日射量, W/m2, [n]
    # 夜間放射量, W/m2, [n]
    # 太陽高度, rad, [n]
    # 太陽方位角, rad, [n]
    a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns = _read_weather_data(input_data_dir=input_data_dir)

    rooms = d['rooms']

    # 室の数
    n_spaces = len(rooms)

    # 室iの名称, [i]
    room_name_is = [r['name'] for r in rooms]

    # 境界j
    bss = [
        boundary_simple.get_boundary_simple(
            theta_o_ns=theta_o_ns,
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            r_n_ns=r_n_ns,
            a_sun_ns=a_sun_ns,
            h_sun_ns=h_sun_ns,
            b=b_dict
        ) for b_dict in d['boundaries']
    ]

    bss2 = bss
    # bss2 = building_part_summarize.integrate(bss=bss)

    q_trs_sol_is_ns = np.array([
        np.sum(np.array([bs.q_trs_sol for bs in bss2 if bs.connected_room_id == i]), axis=0)
        for i in range(n_spaces)
    ])

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

    # json 出力 のうち、"building" に対応する辞書
    building = _make_building_dict(d=d['building'])

    # json 出力のうち、"spaces" に対応する辞書
    spaces = _make_spaces_dict(rooms=d['rooms'])

    boundaries = _make_boundaries(bss2=bss2, rooms=d['rooms'], boundaries=d['boundaries'])

    equipments = _make_equipment_dict(rooms=d['rooms'])

    wd = {
        'building': building,
        'spaces': spaces,
        'boundaries': boundaries,
        'equipments': equipments
    }

    with open(output_data_dir + '/mid_data_house.json', 'w') as f:
        json.dump(wd, f, indent=4)

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

    # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
    with open(output_data_dir + '/mid_data_q_trs_sol.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(q_trs_sol_is_ns.T.tolist())

    # ステップnの境界jにおける裏面等価温度, ℃, [j, 8760*4]
    with open(output_data_dir + '/mid_data_theta_o_sol.csv', 'w') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerows(np.array([bs.theta_o_sol for bs in bss2]).T.tolist())


def make_house_for_test(d, input_data_dir, output_data_dir):

    # 以下の気象データの読み込み
    # 外気温度, degree C
    # 外気絶対湿度, kg/kg(DA)
    # 法線面直達日射量, W/m2
    # 水平面天空日射量, W/m2
    # 夜間放射量, W/m2
    # 太陽高度, rad
    # 太陽方位角, rad
    a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns = _read_weather_data(input_data_dir=input_data_dir)

    rooms = d['rooms']

    # 室の数
    n_spaces = len(rooms)

    # 境界j
    bss = [
        boundary_simple.get_boundary_simple(
            theta_o_ns=theta_o_ns,
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            r_n_ns=r_n_ns,
            a_sun_ns=a_sun_ns,
            h_sun_ns=h_sun_ns,
            b=b_dict
        ) for b_dict in d['boundaries']
    ]

    # 壁体の集約を行わない。
    # layer のC値・R値を core に引き継ぐため
    # C値・R値は集約ができないため
    bss2 = bss
#    bss2 = building_part_summarize.integrate(bss=bss)

    building = _make_building_dict(d=d['building'])

    spaces = _make_spaces_dict(rooms=d['rooms'])

    boundaries = _make_boundaries(bss2=bss2, rooms=d['rooms'], boundaries=d['boundaries'])

    equipments = _make_equipment_dict(rooms=d['rooms'])

    wd = {
        'building': building,
        'spaces': spaces,
        'boundaries': boundaries,
        'equipments': equipments
    }

    with open(output_data_dir + '/mid_data_house.json', 'w') as f:
        json.dump(wd, f, indent=4)


def _read_weather_data(input_data_dir: str):
    """
    気象データを読み込む。
    Args:
        input_data_dir: 現在計算しているデータのパス
    Returns:
        外気温度, degree C
        外気絶対湿度, kg/kg(DA)
        法線面直達日射量, W/m2
        水平面天空日射量, W/m2
        夜間放射量, W/m2
        太陽高度, rad
        太陽方位角, rad
    """

    # 気象データ
    pp = pd.read_csv(input_data_dir + '/weather.csv', index_col=0)

    # 外気温度, degree C
    theta_o_ns = pp['temperature'].values
    # 外気絶対湿度, kg/kg(DA)
    x_o_ns = pp['absolute humidity'].values
    # 法線面直達日射量, W/m2
    i_dn_ns = pp['normal direct solar radiation'].values
    # 水平面天空日射量, W/m2
    i_sky_ns = pp['horizontal sky solar radiation'].values
    # 夜間放射量, W/m2
    r_n_ns = pp['outward radiation'].values
    # 太陽高度, rad
    h_sun_ns = pp['sun altitude'].values
    # 太陽方位角, rad
    a_sun_ns = pp['sun azimuth'].values

    return a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, r_n_ns, theta_o_ns


def _make_building_dict(d: Dict):
    """
    出力する辞書のうち、　"building" に対応する辞書を作成する。
    Args:
        d: 入力ファイルの "building" に対応する辞書
    Returns:
        "building" に対応する辞書
    """

    # 建物の階数
    story = Story(d['story'])

    # 建物のC値
    c_value = d['c_value']

    # 室内圧力 = POSITIVE, NEGATIVE, BALANCED
    inside_pressure = InsidePressure(d['inside_pressure'])

    return {
        'infiltration_method': 'balance_residential',
        'story': story.value,
        'c_value': c_value,
        'inside_pressure': inside_pressure.value
    }


def _make_spaces_dict(rooms: List[dict]):
    """
    出力する辞書のうち、　"spaces" に対応する辞書を作成する。
    Args:
        rooms: 入力ファイルの "rooms" に対応する辞書（リスト形式）
    Returns:
        "spaces" に対応する辞書（リスト形式）
    """

    # region 入力ファイル(space_initializer)の"rooms"部分の読み込み

    # 室の数
    n_spaces = len(rooms)

    # 室のID, [i]
    room_id_is = [int(r['id']) for r in rooms]
    # ID が0始まりで1ずつ増え、一意であることをチェック
    for i, room_id in enumerate(room_id_is):
        if i != room_id:
            raise ValueError('指定されたroomのIDは0からインクリメントする必要があります。')

    # 室iの名称, [i]
    room_name_is = [r['name'] for r in rooms]

    # 室iのタイプ, [i]
    # 現在、室iのタイプについては使用していない。
    # boundary が接する空間の識別は ID で行っているため。
    # とはいえ、室i がどの種別の部屋なのかの情報は非常に重要であるため、当面の間、この入力項目は残しておく。
    room_type_is = [RoomType(r['room_type']) for r in rooms]
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
    v_room_cap_is = np.array([r['volume'] for r in rooms])

    # 室iの外気からの機械換気量, m3/h, [i]
    v_vent_ex_is = np.array([r['vent'] for r in rooms])

    # 隣室からの機械換気
    # 2重のリスト構造を持つ。
    # 外側のリスト：室、（流入側の室を基準とする。）
    # 内側のリスト：換気経路（数は任意であり、換気経路が無い（0: 空のリスト）場合もある。）
    # 変数はタプル （流出側の室ID: int, 換気量（m3/h): float)
    next_vents = [
        [
            ([next_vent['upstream_room_id']], next_vent['volume']) for next_vent in r['next_vent']
        ] for r in rooms
    ]

    # 室iの自然風利用時の換気回数, 1/h, [i]
    n_ntrl_vent_is = np.array([r['natural_vent_time'] for r in rooms])

    # endregion

    # region 出力ファイルに必要なパラメータの作成（必要なもののみ）

    # 放射暖房対流比率, [i]
    beta_is = np.zeros(shape=(n_spaces), dtype=float)

    # 室iの自然風利用時の換気量, m3/s, [i]
    # TODO: もしかすると換気回数わたしの方が自然か？
    v_ntrl_vent_is = v_room_cap_is * n_ntrl_vent_is / 3600

    # 室iの家具等の熱容量, J/K
    c_sh_frt_is = furniture.get_c_cap_frt_is(v_room_cap_is=v_room_cap_is)

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
    g_sh_frt_is = furniture.get_g_sh_frt_is(c_sh_frt_is=c_sh_frt_is)

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
    c_lh_frt_is = furniture.get_c_lh_frt_is(v_room_cap_is)

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA
    g_lh_frt_is = furniture.get_g_lh_frt_is(c_lh_frt_is=c_lh_frt_is)

    # endregion

    spaces = []

    for i in range(n_spaces):
        spaces.append({
            'id': room_id_is[i],
            'name': room_name_is[i],
            'volume': v_room_cap_is[i],
            'beta': beta_is[i],
            'ventilation': {
                'mechanical': v_vent_ex_is[i] / 3600,
                'next_spaces': [
                    {
                        'upstream_room_id': next_vent['upstream_room_id'],
                        'volume': next_vent['volume'] / 3600
                    } for next_vent in rooms[i]['next_vent']
                ],
                'natural': v_ntrl_vent_is[i]
            },
            'furniture': {
                'heat_capacity': c_sh_frt_is[i],
                'heat_cond': g_sh_frt_is[i],
                'moisture_capacity': c_lh_frt_is[i],
                'moisture_cond': g_lh_frt_is[i]
            }
        })

    return spaces


def _make_equipment_dict(rooms: List[dict]) -> dict:
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


def _make_boundaries(bss2: List[BoundarySimple], rooms: List[Dict], boundaries: List[Dict]):

    # 室の数
    n_spaces = len(rooms)

    k_ei_js = []

    for bs in bss2:

        if bs.boundary_type in [
            BoundaryType.ExternalOpaquePart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalGeneralPart
        ]:
            # 温度差係数が1.0でない場合はk_ei_jsに値を代入する。
            # id は自分自身の境界IDとし、自分自身の表面の影響は1.0から温度差係数を減じた値になる。
            if bs.h_td < 1.0:
                k_ei_js.append({'id': bs.id, 'coef': round(1.0 - bs.h_td, 1)})
            else:
                # 温度差係数が1.0の場合はNoneとする。
                k_ei_js.append(None)
        elif bs.boundary_type == BoundaryType.Internal:
            # 室内壁の場合にk_ei_jsを登録する。
            k_ei_js.append({'id': int(bs.rear_surface_boundary_id), 'coef': 1.0})
        else:
            # 外皮に面していない場合、室内壁ではない場合（地盤の場合が該当）は、Noneとする。
            k_ei_js.append(None)

    # 室iの在室者に対する境界jの形態係数
    f_mrt_hum_is = np.zeros_like(bss2, dtype=float)
    for i in range(n_spaces):
        is_connected = np.array([bs.connected_room_id == i for bs in bss2])

        f_mrt_hum_is[is_connected] = occupants_form_factor.get_f_mrt_hum_is(
            a_bdry_i_js=np.array([bs.area for bs in np.array(bss2)[is_connected]]),
            is_floor_bdry_i_js=np.array([bs.is_floor for bs in np.array(bss2)[is_connected]])
        )

    # 室iの微小球に対する境界jの形態係数
    h_r_is = np.zeros_like(bss2, dtype=float)
    for i in range(n_spaces):
        is_connected = np.array([bs.connected_room_id == i for bs in bss2])

        h_r_is[is_connected] = get_h_r_js(
            a_srf=np.array([bs.area for bs in np.array(bss2)[is_connected]])
        )

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating_is = np.array([a22.read_is_radiative_heating(room) for room in rooms])

    connected_room_ids = np.array([b['connected_room_id'] for b in boundaries])

    area_js = np.array([b['area'] for b in boundaries])

    is_floor_js = np.array([b['is_floor'] for b in boundaries])

    n_boundaries = len(bss2)

    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    # TODO: 発熱部位を指定して、面積按分するように変更すべき。
    flr_js = a12.get_flr_js(area_js, connected_room_ids, is_floor_js, is_radiative_heating_is, n_boundaries, n_spaces)

    specs = [_get_boundary_spec(boundary, bs) for boundary, bs in zip(boundaries, bss2)]

    bdrs = []

    for i, bs in enumerate(bss2):

        bdrs.append({
            'id': bs.id,
            'name': bs.name,
            'sub_name': bs.sub_name,
            'is_ground': True if bs.boundary_type == BoundaryType.Ground else False,
            'connected_space_id': bs.connected_room_id,
            'area': bs.area,
            'h_c': bs.h_c,
            'h_r': h_r_is[i],
            'flr': flr_js[i],
            'is_solar_absorbed': bs.is_solar_absorbed_inside,
            'f_mrt_hum': f_mrt_hum_is[i],
            'k_outside': bs.h_td,
            'k_inside': k_ei_js[i],
            'is_floor': bool(is_floor_js[i]),
            'spec': specs[i]
        })


    return bdrs





def _get_boundary_spec(boundaries, bs) -> Dict:

    if bs.boundary_type in [BoundaryType.ExternalGeneralPart]:
        return {
            'method': 'layers',
            'boundary_type': bs.boundary_type.value,
            'layers': boundaries['layers'],
            'outside_heat_transfer_resistance': boundaries['outside_heat_transfer_resistance']
        }
    elif bs.boundary_type in [BoundaryType.Internal]:
        return {
            'method': 'layers',
            'boundary_type': bs.boundary_type.value,
            'layers': boundaries['layers'],
            'outside_heat_transfer_resistance': boundaries['outside_heat_transfer_resistance'],
            'rear_surface_boundary_id': boundaries['rear_surface_boundary_id']
        }
    elif bs.boundary_type == BoundaryType.Ground:
        return {
            'method': 'layers_ground',
            'boundary_type': bs.boundary_type.value,
            'layers': boundaries['layers']
        }
    elif bs.boundary_type in [BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart]:
        return {
            'method': 'u_value',
            'boundary_type': bs.boundary_type.value,
            'u_value': boundaries['u_value'],
            'inside_heat_transfer_resistance': boundaries['inside_heat_transfer_resistance']
        }
    else:
        raise KeyError()

