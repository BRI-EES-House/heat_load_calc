from collections import namedtuple
from typing import Dict

import numpy as np

import a24_wall_layer as a24

DSurface = namedtuple('DSurface', [
    'name_i_ks',
    'boundary_type_i_ks',
    'a_i_ks',
    'is_sun_striked_outside_i_ks',
    'h_i_ks',
    'direction_i_ks',
    'next_room_type_i_ks',
    'N_surf_i',
    'is_solar_absorbed_inside',
    'sunbrk',
    'tau_i_k',
    'IAC_i_k',
    'as_i_k',
    'eps_i_k',
    'Ro_i_k_n',
    'Ri_i_k_n',
    'U',
    'R_i_k_p',
    'C_i_k_p'
])


# ========== JSONからの読み出し ==========
def read_d_boundary_i_ks(boundary: Dict):

    # 室=space はクラス構造を持っているため、
    # _i_ks の変数は本来であれば、[i ✕ k] の2次元配列であるところ、[k]の1次元配列となっている点に注意!!

    # 室iの境界kの名前 * k
    name_i_ks = np.array([b['name'] for b in boundary])

    # 境界条件タイプ * k
    # 'internal': 間仕切り
    # 'external_general_part': 外皮_一般部位
    # 'external_transparent_part': 外皮_透明な開口部
    # 'external_opaque_part': 外皮_不透明な開口部
    # 'ground': 地盤
    boundary_type_i_ks = np.array([b['boundary_type'] for b in boundary])

    # 室iの境界kの面積, m2 * k
    a_i_ks = np.array([b['area'] for b in boundary])

    # 室iの境界kの日射の有無 * k
    # True: 当たる
    # False: 当たらない
    # 室iの境界kの種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    def get_is_sun_striked_outside(b):
        if b['boundary_type'] == 'external_general_part'\
                or b['boundary_type'] == 'external_transparent_part'\
                or b['boundary_type'] == 'external_opaque_part':
            return b['is_sun_striked_outside']
        else:
            return None
    is_sun_striked_outside_i_ks = np.array([get_is_sun_striked_outside(b) for b in boundary])

    # 室iの境界kの温度差係数 * k
    # 室iの境界kの種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    def get_h(b):
        if b['boundary_type'] == 'external_general_part'\
                or b['boundary_type'] == 'external_transparent_part'\
                or b['boundary_type'] == 'external_opaque_part':
            return b['temp_dif_coef']
        else:
            return None
    h_i_ks = np.array([get_h(b) for b in boundary])

    # 室iの境界kの方位 * k
    # 's', 'sw', 'w', 'nw', 'n', 'ne', 'e', 'se', 'top', 'bottom'
    # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
    def get_direction(b):
        if 'is_sun_striked_outside' in b:
            if b['is_sun_striked_outside']:
                return b['direction']
            else:
                return None
        else:
            return None
    direction_i_ks = np.array([get_direction(b) for b in boundary])

    # 室iの境界kの隣室タイプ * k
    # 'main_occupant_room': 主たる居室
    # 'other_occupant_room': その他の居室
    # 'non_occupant_room' : 非居室
    # 'underfloor': 床下空間
    # 室iの境界kの種類が'internal'の場合に定義される。
    def get_next_room_type(b):
        if b['boundary_type'] == 'internal':
            return b['next_room_type']
        else:
            return None
    next_room_type_i_ks = np.array([get_next_room_type(b) for b in boundary])

    def read_to_array(key):
        return np.array([d[key] if key in d else None for d in boundary])

    # 部位数
    N_surf_i = len(boundary)





    # 床フラグ（透過日射の吸収部位）
    is_solar_absorbed_inside = read_to_array('is_solar_absorbed_inside')

    # 屋外に日射が当たる場合はひさしの情報を読み込む
    sunbrk = read_to_array('solar_shading_part')

    # 読みだし元位置決定
    part_key_name = [{
                         "external_general_part": "general_part_spec",
                         "internal": "general_part_spec",
                         "ground": "ground_spec",
                         "external_transparent_part": "transparent_opening_part_spec",
                         "external_opaque_part": "opaque_opening_part_spec"
                     }[boundary_type_i_ks[k]] for k in range(N_surf_i)]

    # 読み出し
    datalist = [s[k] for (s, k) in zip(boundary, part_key_name)]

    def read_from_datalist(key: str, default: str = None):
        return np.array([data[key] if key in data else default for data in datalist])

    def read_from_datalist_float(key: str, default=0.0):
        return np.array([float(data[key]) if key in data else default for data in datalist])

    # 透過率・拡散日射の入射角特性
    tau_i_k = read_from_datalist_float('eta_value', 0.0)
    IAC_i_k = read_from_datalist('incident_angle_characteristics', None)

    # 室外側日射吸収率
    as_i_k = read_from_datalist_float('outside_solar_absorption', 0.0)

    # 室外側放射率[-]
    eps_i_k = read_from_datalist_float('outside_emissivity', 0.0)

    # 室外側熱伝達率
    Ro_i_k_n = read_from_datalist_float('outside_heat_transfer_resistance', 0.0)

    # 室内側熱伝達抵抗・室内側表面総合熱伝達率
    Ri_i_k_n = read_from_datalist('inside_heat_transfer_resistance')  # 室内側熱伝達抵抗

    # 開口部熱貫流率[W/m2K]
    U = read_from_datalist_float('u_value', 0.0)

    # 応答係数の準備
    R_i_k_p = [None] * len(datalist)  # 熱抵抗
    C_i_k_p = [None] * len(datalist)  # 熱容量
    for k, data in enumerate(datalist):
        if boundary_type_i_ks[k] in ["external_general_part", "internal", "ground"]:
            is_ground = boundary_type_i_ks[k] == "ground"

            R_i_k_p[k], C_i_k_p[k] = a24.read_layers(data, is_ground)

    return DSurface(
        name_i_ks=name_i_ks,
        boundary_type_i_ks=boundary_type_i_ks,
        a_i_ks=a_i_ks,
        is_sun_striked_outside_i_ks=is_sun_striked_outside_i_ks,
        h_i_ks=h_i_ks,
        direction_i_ks=direction_i_ks,
        next_room_type_i_ks=next_room_type_i_ks,
        N_surf_i=N_surf_i,
        is_solar_absorbed_inside=is_solar_absorbed_inside,
        sunbrk=sunbrk,
        tau_i_k=tau_i_k,
        IAC_i_k=IAC_i_k,
        as_i_k=as_i_k,
        eps_i_k=eps_i_k,
        Ro_i_k_n=Ro_i_k_n,
        Ri_i_k_n=Ri_i_k_n,
        U=U,
        R_i_k_p=R_i_k_p,
        C_i_k_p=C_i_k_p
    )
