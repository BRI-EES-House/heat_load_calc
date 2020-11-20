import numpy as np
from typing import Dict, List
import json
import csv
import pandas as pd
from enum import Enum

import heat_load_calc.initializer.a12_indoor_radiative_heat_transfer as a12
import heat_load_calc.initializer.a14_furniture as a14
import heat_load_calc.initializer.a15_air_flow_rate_rac as a15
import heat_load_calc.initializer.a22_radiative_heating_spec as a22

from heat_load_calc.initializer.boundary_type import BoundaryType

from heat_load_calc.initializer import schedule_loader
from heat_load_calc.initializer import residents_number
from heat_load_calc.initializer import occupants_form_factor
from heat_load_calc.initializer import boundary_simple
from heat_load_calc.initializer import building_part_summarize


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


def make_house(d, input_data_dir, output_data_dir):

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

    # 室iのC値, [i]
    # TODO: initializer の json から c_value を削除する。
    c_value_is = np.array([r['c_value'] for r in rooms])

    # 室の数
    number_of_spaces = len(rooms)

    # 室iの名称, [i]
    room_names = [r['name'] for r in rooms]

    # 境界j
    bss = np.array([
        boundary_simple.get_boundary_simple(
            theta_o_ns=theta_o_ns,
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            r_n_ns=r_n_ns,
            a_sun_ns=a_sun_ns,
            h_sun_ns=h_sun_ns,
            b=b_dict
        ) for b_dict in d['boundaries']
    ])

    bss2 = building_part_summarize.integrate(bss=list(bss))

    q_trs_sol_is_ns = np.array([
        np.sum(np.array([bs.q_trs_sol for bs in bss2 if bs.connected_room_id == i]), axis=0)
        for i in range(number_of_spaces)
    ])

    # 室iの床面積, m2, [i]
    # TODO: is_solar_absorbed_inside_js を使用すべき。
    a_floor_is = np.array([
        np.sum(np.array([bs.area for bs in bss if bs.connected_room_id == i and bs.is_solar_absorbed_inside]))
        for i in range(number_of_spaces)
    ])

    # 床面積の合計, m2
    a_floor_total = float(np.sum(a_floor_is))

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
            room_name_is=room_names,
            a_floor_is=a_floor_is
        )
    ac_demand_is_ns = np.where(ac_demand_is_ns == 1, True, False)

    # 熱交換器種類
    heat_exchanger_type_is = [a22.read_heat_exchanger_type(room) for room in rooms]

    # json 出力 のうち、"building" に対応する辞書
    building = _make_building_dict(d=d['building'])

    # json 出力のうち、"spaces" に対応する辞書
    spaces = _make_spaces_dict(rooms=d['rooms'], a_floor_is=a_floor_is)

    bdrs = make_bdrs(bss2, rooms=d['rooms'], a_floor_is=a_floor_is)

    wd = {
        'building': building,
        'spaces': spaces,
        'boundaries': bdrs
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
    number_of_spaces = len(rooms)

    # 境界j
    bss = np.array([
        boundary_simple.get_boundary_simple(
            theta_o_ns=theta_o_ns,
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            r_n_ns=r_n_ns,
            a_sun_ns=a_sun_ns,
            h_sun_ns=h_sun_ns,
            b=b_dict
        ) for b_dict in d['boundaries']
    ])

    bss2 = building_part_summarize.integrate(bss=list(bss))

    # 室iの床面積, m2, [i]
    # TODO: is_solar_absorbed_inside_js を使用すべき。
    a_floor_is = np.array([
        np.sum(np.array([bs.area for bs in bss if bs.connected_room_id == i and bs.is_solar_absorbed_inside]))
        for i in range(number_of_spaces)
    ])

    building = _make_building_dict(d=d['building'])

    spaces = _make_spaces_dict(rooms=d['rooms'], a_floor_is=a_floor_is)

    bdrs = make_bdrs(bss2, rooms=d['rooms'], a_floor_is=a_floor_is)

    wd = {
        'building': building,
        'spaces': spaces,
        'boundaries': bdrs
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


def _make_spaces_dict(rooms: List[dict], a_floor_is: np.ndarray):
    """
    出力する辞書のうち、　"spaces" に対応する辞書を作成する。
    Args:
        rooms: 入力ファイルの "rooms" に対応する辞書（リスト形式）
    Returns:
        "spaces" に対応する辞書（リスト形式）
    """

    # region 入力ファイル(space_initializer)の"rooms"部分の読み込み

    # 室の数
    number_of_spaces = len(rooms)

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

    # 室iの気積, m3, [i]
    v_room_cap_is = np.array([r['volume'] for r in rooms])

    # 室iの外気からの機械換気量, m3/h, [i]
    v_vent_ex_is = np.array([r['vent'] for r in rooms])

    # 室iの隣室からの機会換気量, m3/h, [i, i]
    v_int_vent_is = get_v_int_vent_is(rooms)

    # 室iの自然風利用時の換気回数, 1/h, [i]
    n_ntrl_vent_is = np.array([r['natural_vent_time'] for r in rooms])

    # 室iの家具等の熱容量, J/K
    c_cap_frnt_is = a14.get_c_cap_frnt_is(v_room_cap_is)

    # 室iの家具等と空気間の熱コンダクタンス, W/K, [i]
    c_frnt_is = a14.get_Cfun(c_cap_frnt_is)

    # 室iの家具等の湿気容量, kg/m3 kg/kgDA, [i]
    g_f_is = a14.get_g_f_is(v_room_cap_is)  # i室の備品類の湿気容量

    # 室iの家具等と空気間の湿気コンダクタンス, kg/s kg/kgDA
    c_x_is = a14.get_c_x_is(g_f_is)

    # 放射暖房対流比率
    beta_is = np.full(len(rooms), 0.0)

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating_is = [a22.read_is_radiative_heating(room) for room in rooms]

    # 放射暖房最大能力[W]
    Lrcap_is = np.array([a22.read_radiative_heating_max_capacity(room) for room in rooms])

    equip_heating_radiative = []
    for i, is_radiative in enumerate(is_radiative_heating_is):
        if is_radiative:
            equip_heating_radiative.append({
                'installed': True,
                'max_capacity': Lrcap_is[i]
            })
        else:
            equip_heating_radiative.append({
                'installed': False
            })

    # 冷房設備仕様の読み込み

    # 放射冷房有無（Trueなら放射冷房あり）
    is_radiative_cooling_is = [a22.read_is_radiative_cooling(room) for room in rooms]

    # 放射冷房最大能力[W]
    radiative_cooling_max_capacity_is = np.array([a22.read_is_radiative_cooling(room) for room in rooms])

    equip_cooling_radiative = []
    for i, is_radiative in enumerate(is_radiative_cooling_is):
        if is_radiative:
            equip_cooling_radiative.append({
                'installed': True,
                'max_capacity': radiative_cooling_max_capacity_is[i]
            })
        else:
            equip_cooling_radiative.append({
                'installed': False
            })

    qrtd_c_is = np.array([a15.get_qrtd_c(a_floor_i) for a_floor_i in a_floor_is])
    qmax_c_is = np.array([a15.get_qmax_c(qrtd_c_i) for qrtd_c_i in qrtd_c_is])
    qmin_c_is = np.array([a15.get_qmin_c() for qrtd_c_i in qrtd_c_is])
    Vmax_is = np.array([a15.get_Vmax(qrtd_c_i) for qrtd_c_i in qrtd_c_is])
    Vmin_is = np.array([a15.get_Vmin(Vmax_i) for Vmax_i in Vmax_is])

    # endregion

    # 室iの自然風利用時の換気量, m3/s, [i]
    v_ntrl_vent_is = v_room_cap_is * n_ntrl_vent_is / 3600

    spaces = []

    for i in range(number_of_spaces):
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
                'heat_capacity': c_cap_frnt_is[i],
                'heat_cond': c_frnt_is[i],
                'moisture_capacity': g_f_is[i],
                'moisture_cond': c_x_is[i]
            },
            'equipment': {
                'heating': {
                    'radiative': equip_heating_radiative[i],
                    'convective': {}
                },
                'cooling': {
                    'radiative': equip_cooling_radiative[i],
                    'convective': {
                        'q_min': qmin_c_is[i],
                        'q_max': qmax_c_is[i],
                        'v_min': Vmin_is[i],
                        'v_max': Vmax_is[i]
                    }
                }
            }
        })

    return spaces


def make_bdrs(bss2, rooms, a_floor_is):

    # 室の数
    number_of_spaces = len(rooms)

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

    # 暖房設備仕様の読み込み
    # 放射暖房有無（Trueなら放射暖房あり）
    is_radiative_heating_is = [a22.read_is_radiative_heating(room) for room in rooms]

    # 室iの在室者に対する境界j*の形態係数
    # TODO: 日射の吸収の有無ではなくて、床か否かで判定するように変更すべき。
    f_mrt_hum_is = np.concatenate([
        occupants_form_factor.get_f_mrt_hum_is(
            a_bdry_i_jstrs=np.array([bs.area for bs in bss2 if bs.connected_room_id == i]),
            is_solar_absorbed_inside_bdry_i_jstrs=np.array([bs.is_solar_absorbed_inside for bs in bss2 if bs.connected_room_id == i])
        ) for i in range(number_of_spaces)])

    # 放射暖房の発熱部位の設定（とりあえず床発熱） 表7
    # TODO: 発熱部位を指定して、面積按分するように変更すべき。
    flr_jstrs = np.concatenate([
        a12.get_flr(
            A_i_g=np.array([bs.area for bs in bss2 if bs.connected_room_id == i]),
            A_fs_i=a_floor_is[i],
            is_radiative_heating=is_radiative_heating_is[i],
            is_solar_absorbed_inside=np.array([bs.is_solar_absorbed_inside for bs in bss2 if bs.connected_room_id == i])
        ) for i in range(number_of_spaces)])


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
            'flr': flr_jstrs[i],
            'is_solar_absorbed': str(bs.is_solar_absorbed_inside),
            'f_mrt_hum': f_mrt_hum_is[i],
            'k_outside': bs.h_td,
            'k_inside': k_ei_js[i]
        })
    return bdrs


def get_v_int_vent_is(rooms: List[Dict]) -> np.ndarray:
    """

    Args:
        rooms: 部屋（入力）（辞書型）

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

    # 室の数
    number_of_rooms = len(rooms)

    # 隣室iから室iへの機械換気量, m3/s, [i, i]
    v_int_vent_is = np.concatenate([[
        get_v_int_vent_i(
            next_vents=r['next_vent'],
            number_of_rooms=number_of_rooms
        )
    ] for r in rooms])

    return v_int_vent_is


def get_v_int_vent_i(next_vents: List[Dict], number_of_rooms: int) -> np.ndarray:
    """隣室から室への機械換気量の配列を取得する。

    Args:
        next_vents: 隣室からの機械換気量
            辞書型：
                上流側の室の名称
                換気量, m3/h
        number_of_rooms: 部屋の数

    Returns:
        隣室から室への機械換気量の配列, m3/s, [i]
            例えば、
                室インデックス0からの換気量が 10.0
                室インデックス1からの換気量が  0.0
                室インデックス2からの換気量が  8.0
                室インデックス3からの換気量が  6.0
            の場合は、
            [10.0, 0.0, 8.0, 6.0]

    Notes:
        室インデックスが重なって指定された場合はそこで指定された換気量は加算される。
            例えば、
                室インデックス0からの換気量が 10.0
                室インデックス1からの換気量が  0.0
                室インデックス2からの換気量が  8.0
                室インデックス3からの換気量が  6.0
                室インデックス0からの換気量が  2.0
            の場合は、
            [12.0, 0.0, 8.0, 6.0]

    """

    # 室iの隣室からの機械換気量, m3/s, [i]
    v_int_vent_i = np.zeros(number_of_rooms)

    for next_vent in next_vents:

        idx = {
            'main_occupant_room': 0,
            'other_occupant_room': 1,
            'non_occupant_room': 2,
            'underfloor': 3
        }[next_vent['upstream_room_type']]

        # m3/hからm3/sへの単位変換を行っている
        v_int_vent_i[idx] = v_int_vent_i[idx] + next_vent['volume'] / 3600.0

    return v_int_vent_i

