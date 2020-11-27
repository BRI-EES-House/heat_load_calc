import numpy as np
from typing import Dict, List, Tuple
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
from heat_load_calc.initializer import building_part_summarize
from heat_load_calc.initializer import furniture


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

    bss2 = building_part_summarize.integrate(bss=bss)

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

    boundaries = _make_boundaries(bss2=bss2, rooms=d['rooms'])

    wd = {
        'building': building,
        'spaces': spaces,
        'boundaries': boundaries
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

    bss2 = building_part_summarize.integrate(bss=bss)

    building = _make_building_dict(d=d['building'])

    spaces = _make_spaces_dict(rooms=d['rooms'])

    boundaries = _make_boundaries(bss2=bss2, rooms=d['rooms'])

    wd = {
        'building': building,
        'spaces': spaces,
        'boundaries': boundaries
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

    # 暖房設備, [i]
    heating_equipment_is = [r['heating_equipment'] for r in rooms]

    # 暖房形式, [i]
    # 暖房設備の仕様, [i]
    heating_equipment_type_is = []
    heating_equipment_spec_is = []

    for he in heating_equipment_is:

        # 暖房形式
        he_type = HeatingEquipmentType(he['equipment_type'])

        # 暖房形式を追加する。
        heating_equipment_type_is.append(he_type)

        # 設置しない
        if he_type == HeatingEquipmentType.NOT_INSTALLED:
            heating_equipment_spec_is.append(None)

        # 対流暖房方式
        elif he_type == HeatingEquipmentType.CONVECTIVE:
            # 対流暖房方式における仕様
            spec = he['convective']
            # 以下の仕様をタプル形式で追加
            # 最小暖房能力, W
            # 最大暖房能力, W
            # 暖房時最小風量, m3/min
            # 暖房時最大風量, m3/min
            heating_equipment_spec_is.append(
                (spec['q_min'], spec['q_max'], spec['v_min'], spec['v_max'])
            )

        # 放射暖房方式
        elif he_type == HeatingEquipmentType.RADIATIVE:
            # 放射暖房方式における仕様
            spec = he['radiative']
            # 以下の仕様をタプル形式で追加
            # 最大能力, W/m2
            # (放熱)面積, m2
            heating_equipment_spec_is.append(
                (spec['max_capacity'], spec['area'])
            )

        else:
            raise Exception()

    # 冷房設備, [i]
    cooling_equipment_is = [r['cooling_equipment'] for r in rooms]

    # 冷房形式, [i]
    # 冷房設備の仕様, [i]
    cooling_equipment_type_is = []
    cooling_equipment_spec_is = []

    for ce in cooling_equipment_is:

        # 冷房形式
        ce_type = CoolingEquipmentType(ce['equipment_type'])

        # 冷房形式を追加する。
        cooling_equipment_type_is.append(ce_type)

        # 設置しない
        if ce_type == CoolingEquipmentType.NOT_INSTALLED:
            cooling_equipment_spec_is.append(None)

        # 対流冷房方式
        elif ce_type == CoolingEquipmentType.CONVECTIVE:
            # 対流暖房方式における仕様
            spec = ce['convective']
            # 以下の仕様をタプル形式で追加
            # 最小冷房能力, W
            # 最大冷房能力, W
            # 冷房時最小風量, m3/min
            # 冷房時最大風量, m3/min
            cooling_equipment_spec_is.append(
                (spec['q_min'], spec['q_max'], spec['v_min'], spec['v_max'])
            )

        # 放射冷房方式
        elif ce_type == CoolingEquipmentType.RADIATIVE:
            # 放射冷房方式における仕様
            spec = ce['radiative']
            # 以下の仕様をタプル形式で追加
            # 最大能力, W/m2
            # (放熱)面積, m2
            cooling_equipment_spec_is.append(
                (spec['max_capacity'], spec['area'])
            )

        else:
            raise Exception()

    # endregion

    # region 出力ファイルに必要なパラメータの作成（必要なもののみ）

    # 放射暖房対流比率, [i]
    beta_is = []
    for he_type, he_spec in zip(heating_equipment_type_is, heating_equipment_spec_is):
        if he_type == HeatingEquipmentType.NOT_INSTALLED:
            beta_is.append(0.0)
        elif he_type == HeatingEquipmentType.CONVECTIVE:
            beta_is.append(0.0)
        elif he_type == HeatingEquipmentType.RADIATIVE:
            beta_is.append(0.0)
        else:
            raise Exception()

    # 室iの隣室からの機械換気量, m3/h, [i, i]
    v_int_vent_is = _get_v_int_vent_is(next_vents, n_spaces)

    # 室iの自然風利用時の換気量, m3/s, [i]
    v_ntrl_vent_is = v_room_cap_is * n_ntrl_vent_is / 3600

    # 室iの家具等の熱容量, J/K
    c_sh_frt_is = furniture.get_c_cap_frt_is(v_room_cap_is=v_room_cap_is)

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
    g_sh_frt_is = furniture.get_g_sh_frt_is(c_sh_frt_is=c_sh_frt_is)

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
    c_lh_frt_is = furniture.get_c_lh_frt_is(v_room_cap_is)

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA
    g_lh_frt_is = furniture.get_g_lh_frt_is(c_lh_frt_is=c_lh_frt_is)

    equip_heating_convective = []
    equip_heating_radiative = []

    for he_type, he_spec in zip(heating_equipment_type_is, heating_equipment_spec_is):
        if he_type == HeatingEquipmentType.NOT_INSTALLED:
            equip_heating_convective.append({
                'installed': False
            })
            equip_heating_radiative.append({
                'installed': False
            })
        elif he_type == HeatingEquipmentType.CONVECTIVE:
            equip_heating_convective.append({
                'installed': True
            })
            equip_heating_radiative.append({
                'installed': False
            })
        elif he_type == HeatingEquipmentType.RADIATIVE:
            equip_heating_convective.append({
                'installed': False
            })
            # 最大能力, W/m2
            # (放熱)面積, m2
            he_max_capacity, he_area = he_spec
            # 放射暖房最大能力[W]
            he_cap = he_max_capacity * he_area
            equip_heating_radiative.append({
                'installed': True,
                'max_capacity': he_cap
            })
        else:
            raise Exception()

    equip_cooling_convective = []
    equip_cooling_radiative = []

    for ce_type, ce_spec in zip(cooling_equipment_type_is, cooling_equipment_spec_is):
        if ce_type == CoolingEquipmentType.NOT_INSTALLED:
            equip_cooling_convective.append({
                'installed': False
            })
            equip_cooling_radiative.append({
                'installed': False
            })
        elif ce_type == CoolingEquipmentType.CONVECTIVE:
            ce_q_min, ce_q_max, ce_v_min, ce_v_max = ce_spec
            equip_cooling_convective.append({
                'installed': True,
                'q_min': ce_q_min,
                'q_max': ce_q_max,
                'v_min': ce_v_min,
                'v_max': ce_v_max
            })
            equip_cooling_radiative.append({
                'installed': False
            })
        elif ce_type == CoolingEquipmentType.RADIATIVE:
            equip_cooling_convective.append({
                'installed': False
            })
            # 最大能力, W/m2
            # (放熱)面積, m2
            ce_max_capacity, ce_area = ce_spec
            # 放射暖房最大能力[W]
            ce_cap = ce_max_capacity * ce_area
            equip_cooling_radiative.append({
                'installed': True,
                'max_capacity': ce_cap
            })
        else:
            raise Exception()

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
                'next_spaces': v_int_vent_is.tolist()[i],
                'natural': v_ntrl_vent_is[i]
            },
            'furniture': {
                'heat_capacity': c_sh_frt_is[i],
                'heat_cond': g_sh_frt_is[i],
                'moisture_capacity': c_lh_frt_is[i],
                'moisture_cond': g_lh_frt_is[i]
            },
            'equipment': {
                'heating': {
                    'radiative': equip_heating_radiative[i],
                    'convective': equip_heating_convective[i]
                },
                'cooling': {
                    'radiative': equip_cooling_radiative[i],
                    'convective': equip_cooling_convective[i]
                }
            }
        })

    return spaces


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


def _make_boundaries(bss2: List[BoundarySimple], rooms: List[Dict]):

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

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating_is = [a22.read_is_radiative_heating(room) for room in rooms]

    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    # TODO: 発熱部位を指定して、面積按分するように変更すべき。
    flr_js = np.zeros_like(bss2, dtype=float)
    for i in range(n_spaces):
        is_connected = np.array([bs.connected_room_id == i for bs in bss2])
        flr_js[is_connected] = a12.get_flr_i_js(
            area_i_js=np.array([bs.area for bs in np.array(bss2)[is_connected]]),
            is_radiative_heating=is_radiative_heating_is[i],
            is_floor_i_js=np.array([bs.is_floor for bs in np.array(bss2)[is_connected]])
        )

    bdrs = []

    for i, bs in enumerate(bss2):
        bdrs.append({
            'id': bs.id,
            'name': bs.name,
            'sub_name': bs.sub_name,
            'is_ground': 'true' if bs.boundary_type == BoundaryType.Ground else 'false',
            'connected_space_id': bs.connected_room_id,
            'area': bs.area,
            'phi_a0': bs.rfa0,
            'phi_a1': list(bs.rfa1),
            'phi_t0': bs.rft0,
            'phi_t1': list(bs.rft1),
            'r': list(bs.row),
            'h_i': bs.h_i,
            'flr': flr_js[i],
            'is_solar_absorbed': str(bs.is_solar_absorbed_inside),
            'f_mrt_hum': f_mrt_hum_is[i],
            'k_outside': bs.h_td,
            'k_inside': k_ei_js[i]
        })
    return bdrs


def _get_v_int_vent_is(next_vents: List[List[Tuple]], n_rooms: int) -> np.ndarray:
    """
    隣室iから室iへの機械換気量マトリクスを生成する。
    Args:
        next_vents: 隣室からの機械換気
                        2重のリスト構造を持つ。
                        外側のリスト：室、（流入側の室を基準とする。）
                        内側のリスト：換気経路（数は任意であり、換気経路が無い（0: 空のリスト）場合もある。）
                        変数はタプル （流出側の室ID: int, 換気量（m3/h): float)
        n_rooms: 室の数
    Returns:
        隣室iから室iへの機械換気量マトリクス, m3/s, [i, i]
            例えば、
                室0→室1:3.0
                室0→室2:4.0
                室1→室2:3.0
                室3→室1:1.5
                室3→室2:1.0
            の場合、
                [[0.0, 0.0, 0.0, 0.0],
                 [3.0, 0.0, 0.0, 1.5],
                 [4.0, 3.0, 0.0, 1.0],
                 [0.0, 0.0, 0.0, 0.0]]
    """

    # 隣室iから室iへの換気量マトリックス, m3/s [i, i]
    v_int_vent_is = np.zeros((n_rooms, n_rooms), dtype=float)

    # 室iのループ
    for i, next_vent_is in enumerate(next_vents):

        # 室iにおける経路jのループ
        # 取得するのは、(ID: int, 換気量(m3/h): float) のタプル
        for (idx, volume) in next_vent_is:

            # m3/hからm3/sへの単位変換を行っている
            v_int_vent_is[i, idx] = v_int_vent_is[i, idx] + volume / 3600.0

    return v_int_vent_is

