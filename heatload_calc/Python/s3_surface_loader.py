from collections import namedtuple

import numpy as np

import a24_wall_layer as a24

Surface = namedtuple('Surface', [
    'N_surf_i',
    'is_sun_striked_outside',
    'boundary_type',
    'a_i_k',
    'Rnext_i_k',
    'direction',
    'is_solar_absorbed_inside',
    'A_i_k',
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
def read_surface(surfaces):
    # 部位数
    N_surf_i = len(surfaces)

    def read_to_array(key):
        return np.array([d[key] if key in d else None for d in surfaces])

    # True:外表面に日射が当たる
    is_sun_striked_outside = read_to_array('is_sun_striked_outside')

    # 境界条件タイプ
    boundary_type = read_to_array('boundary_type')

    # 隣室温度差係数
    a_i_k = read_to_array('temp_dif_coef')

    # 隣接室
    Rnext_i_k = read_to_array('next_room_type')

    # 方位
    direction = read_to_array('direction')

    # 床フラグ（透過日射の吸収部位）
    is_solar_absorbed_inside = read_to_array('is_solar_absorbed_inside')

    # 面積
    A_i_k = read_to_array('area')

    # 屋外に日射が当たる場合はひさしの情報を読み込む
    sunbrk = read_to_array('solar_shading_part')

    # 読みだし元位置決定
    part_key_name = [{
                         "external_general_part": "general_part_spec",
                         "internal": "general_part_spec",
                         "ground": "ground_spec",
                         "external_transparent_part": "transparent_opening_part_spec",
                         "external_opaque_part": "opaque_opening_part_spec"
                     }[boundary_type[k]] for k in range(N_surf_i)]

    # 読み出し
    datalist = [s[k] for (s, k) in zip(surfaces, part_key_name)]

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
        if boundary_type[k] in ["external_general_part", "internal", "ground"]:
            is_ground = boundary_type[k] == "ground"

            R_i_k_p[k], C_i_k_p[k] = a24.read_layers(data, is_ground)

    return Surface(N_surf_i,
                   is_sun_striked_outside,
                   boundary_type,
                   a_i_k,
                   Rnext_i_k,
                   direction,
                   is_solar_absorbed_inside,
                   A_i_k,
                   sunbrk,
                   tau_i_k,
                   IAC_i_k,
                   as_i_k,
                   eps_i_k,
                   Ro_i_k_n,
                   Ri_i_k_n,
                   U,
                   R_i_k_p,
                   C_i_k_p
                   )
