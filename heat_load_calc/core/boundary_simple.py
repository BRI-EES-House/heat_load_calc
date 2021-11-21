import numpy as np
from dataclasses import dataclass
from typing import List

from heat_load_calc.core import outside_eqv_temp, solar_shading, transmission_solar_radiation
from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.core import shape_factor
from heat_load_calc.core import response_factor


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

    # 室内側表面放射熱伝達率, W/m2K
    h_r: float

    # 相当外気温度, ℃, [8760 * 4]
    theta_o_sol: np.ndarray

    # 透過日射熱取得, W, [8760*4]
    q_trs_sol: np.ndarray

    # 応答係数データクラス
    rf: response_factor.ResponseFactor


class Boundaries:

    def __init__(self, a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, n_rm, r_n_ns, theta_o_ns, bs):

        self._bss = get_boundary_simples(a_sun_ns=a_sun_ns, h_sun_ns=h_sun_ns, i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, n_rm=n_rm, r_n_ns=r_n_ns, theta_o_ns=theta_o_ns, bs=bs)

    def get_bss(self):

        return self._bss


def get_boundary_simples(a_sun_ns, h_sun_ns, i_dn_ns, i_sky_ns, n_rm, r_n_ns, theta_o_ns, bs):

    # 本来であれば BoundarySimple クラスにおいて境界に関する入力用辞書から読み込みを境界個別に行う。
    # しかし、室内側表面放射熱伝達は室内側の形態係数によって値が決まり、ある室に接する境界の面積の組み合わせで決定されるため、
    # 境界個別に値を決めることはできない。（すべての境界の情報が必要である。）
    # 一方で、境界の集約を行うためには、応答係数を BoundarySimple クラス生成時に求める必要があり、
    # さらに応答係数の計算には裏面の表面放射・対流熱伝達率の値が必要となるため、
    # BoundarySimple クラスを生成する前に、予め室内側表面放射・対流熱伝達率を計算しておき、
    # BoundarySimple クラスを生成する時に必要な情報としておく。

    # 境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]
    h_r_js = shape_factor.get_h_r_js(
        n_spaces=n_rm,
        bs=bs
    ).reshape(-1, 1)

    # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]
    h_c_js = np.array([b['h_c'] for b in bs]).reshape(-1, 1)

    # 境界j
    bss = [
        get_boundary_simple(
            theta_o_ns=theta_o_ns,
            i_dn_ns=i_dn_ns,
            i_sky_ns=i_sky_ns,
            r_n_ns=r_n_ns,
            a_sun_ns=a_sun_ns,
            h_sun_ns=h_sun_ns,
            b=b,
            h_c_js=h_c_js,
            h_r_js=h_r_js
        ) for b in bs
    ]

    return bss


def get_boundary_simple(theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, a_sun_ns, h_sun_ns, b, h_c_js, h_r_js):

    # ID
    # TODO: ID が0始まりで1ずつ増え、一意であることのチェックを行うコードを追記する。
    boundary_id = int(b['id'])

    # 名前
    name = b['name']
    sub_name = b['sub_name']

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
    if boundary_type in [
        BoundaryType.ExternalGeneralPart,
        BoundaryType.ExternalTransparentPart,
        BoundaryType.ExternalOpaquePart,
        BoundaryType.Ground
    ]:
        h_td = float(b['temp_dif_coef'])
    else:
        h_td = 0.0

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

    h_r = h_r_js[boundary_id]

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

    # 応答係数
    rf = response_factor.get_response_factor(b=b, h_c_js=h_c_js, h_r_js=h_r_js)

    return BoundarySimple(
        id=boundary_id,
        name=name,
        sub_name=sub_name,
        connected_room_id=connected_room_id,
        boundary_type=boundary_type,
        area=area,
        h_td=h_td,
        rear_surface_boundary_id=rear_surface_boundary_id,
        is_floor=is_floor,
        is_solar_absorbed_inside=is_solar_absorbed_inside,
        is_sun_striked_outside=is_sun_striked_outside,
        direction=direction,
        h_c=h_c,
        h_r=h_r,
        theta_o_sol=theta_o_sol,
        q_trs_sol=q_trs_sol,
        rf=rf
    )


def get_boundary_by_id(bss: List[BoundarySimple], boundary_id: int):

    # 指定された boundary_id に一致する Boundary を取得する。
    _bss = [bs.id == boundary_id for bs in bss]

    # 取得された Boundary は必ず1つのはずなので、「見つからない場合」「複数該当した場合」にはエラーを出す。
    if len(_bss) == 0:
        raise Exception("指定された boundary_id に一致する boundary が見つかりませんでした。")
    if len(_bss) >1:
        raise Exception("指定された boundary_id に一致する boundary が複数見つかりました。")

    return _bss[0]

