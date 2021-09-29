import numpy as np
from dataclasses import dataclass

from heat_load_calc.initializer import outside_eqv_temp
from heat_load_calc.initializer import solar_shading
from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.initializer import transmission_solar_radiation


@dataclass
class BoundarySimple:

    # ID
    id: int

    # 名称
    name: str

    # 副名称
    sub_name: str

    # 接する室のID
    connected_room_id: int

    # 境界の種類
    boundary_type: BoundaryType

    # 面積, m2
    area: float

    # 温度差係数
    h_td: float

    # 隣室タイプ
    #   'main_occupant_room': 0,
    #   'other_occupant_room': 1,
    #   'non_occupant_room': 2,
    #   'underfloor': 3
    next_room_type: int

    # 裏側表面の境界ID
    # internal_wall の場合のみ定義される。
    rear_surface_boundary_id: int

    # 床か否か
    is_floor: bool

    # 室内侵入日射吸収の有無
    is_solar_absorbed_inside: bool

    # 室外側の日射の有無
    # True: 当たる
    # False: 当たらない
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    is_sun_striked_outside: bool

    # 面する方位
    # 's', 'sw', 'w', 'nw', 'n', 'ne', 'e', 'se', 'top', 'bottom'
    # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
    direction: str

    # 室内側表面対流熱伝達率, W/m2K
    h_c: float

    # 相当外気温度, ℃, [8760 * 4]
    theta_o_sol: np.ndarray

    # 透過日射熱取得, W, [8760*4]
    q_trs_sol: np.ndarray


def get_boundary_simple(theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, a_sun_ns, h_sun_ns, b):

    # ID
    # TODO: ID が0始まりで1ずつ増え、一意であることのチェックを行うコードを追記する。
    boundary_id = int(b['id'])

    # 名前
    name = b['name']
    sub_name = ''

    # 接する室のID
    connected_room_id = int(b['connected_room_id'])

    # 境界の種類
    # 'internal': 間仕切り
    # 'external_general_part': 外皮_一般部位
    # 'external_transparent_part': 外皮_透明な開口部
    # 'external_opaque_part': 外皮_不透明な開口部
    # 'ground': 地盤
    boundary_type = BoundaryType(b['boundary_type'])

    # 面積, m2
    area = float(b['area'])

    # 日射の有無
    # True: 当たる
    # False: 当たらない
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    if b['boundary_type'] in ['external_general_part', 'external_transparent_part', 'external_opaque_part']:
        is_sun_striked_outside = bool(b['is_sun_striked_outside'])
    else:
        is_sun_striked_outside = None

    # 温度差係数
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    if b['boundary_type'] in ['external_general_part', 'external_transparent_part', 'external_opaque_part', 'ground']:
        h_td = float(b['temp_dif_coef'])
    else:
        h_td = 0.0

    # 隣室タイプ
    # 境界の種類が'internal'の場合に定義される。
    # 隣室タイプにひもづけて隣室のIDを取得している。
    # 本来であれば、IDで直接指定する方が望ましい。
    # TODO: ID指定に変更する。
    next_room_type = {
        'main_occupant_room': 0,
        'other_occupant_room': 1,
        'non_occupant_room': 2,
        'underfloor': 3
    }[b['next_room_type']] if b['boundary_type'] == 'internal' else -1

    if b['boundary_type'] == 'internal':
        rear_surface_boundary_id = int(b['rear_surface_boundary_id'])
    else:
        rear_surface_boundary_id = None

    # 室内侵入日射吸収の有無
    # True: 吸収する
    # False: 吸収しない
    is_solar_absorbed_inside = bool(b['is_solar_absorbed_inside'])

    # 床か否か
    # True: 床, False: 床以外
    is_floor = bool(b['is_floor'])

    # 方位
    # 's', 'sw', 'w', 'nw', 'n', 'ne', 'e', 'se', 'top', 'bottom'
    # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
    if 'is_sun_striked_outside' in b:
        if b['is_sun_striked_outside']:
            direction = b['direction']
        else:
            direction = None
    else:
        direction = None

    # 室内側表面対流熱伝達率, W/m2K
    h_c = b['h_c']

    solar_shading_part = solar_shading.SolarShading.create(b=b)

    # 相当外気温度, degree C, [8760 * 4]
    oet = outside_eqv_temp.OutsideEqvTemp.create(b)
    theta_o_sol = oet.get_theta_o_sol_i_j_ns(
        theta_o_ns=theta_o_ns,
        i_dn_ns=i_dn_ns,
        i_sky_ns=i_sky_ns,
        r_n_ns=r_n_ns,
        a_sun_ns=a_sun_ns,
        h_sun_ns=h_sun_ns
    )

    # 透過日射量, W, [8760*4]
    tsr = transmission_solar_radiation.TransmissionSolarRadiation.create(d=b, solar_shading_part=solar_shading_part)
    q_trs_sol = tsr.get_qgt(a_sun_ns=a_sun_ns, h_sun_ns=h_sun_ns, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns)

    return BoundarySimple(
        id=boundary_id,
        name=name,
        sub_name=sub_name,
        connected_room_id=connected_room_id,
        boundary_type=boundary_type,
        area=area,
        h_td=h_td,
        next_room_type=next_room_type,
        rear_surface_boundary_id=rear_surface_boundary_id,
        is_floor=is_floor,
        is_solar_absorbed_inside=is_solar_absorbed_inside,
        is_sun_striked_outside=is_sun_striked_outside,
        direction=direction,
        h_c=h_c,
        theta_o_sol=theta_o_sol,
        q_trs_sol=q_trs_sol
    )

