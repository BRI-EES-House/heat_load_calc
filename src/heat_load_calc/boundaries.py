import numpy as np
from dataclasses import dataclass
from typing import List, Dict

from heat_load_calc import response_factor, transmission_solar_radiation, shape_factor
from heat_load_calc.boundary_type import BoundaryType
from heat_load_calc.weather import Weather
from heat_load_calc.response_factor import ResponseFactor
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc.outside_eqv_temp import OutsideEqvTemp
from heat_load_calc.window import Window, GlazingType


@dataclass
class Boundary:

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

    # 室内側表面対流熱伝達率, W/m2K
    h_s_c: float

    # 室内側表面放射熱伝達率, W/m2K
    h_s_r: float

    # 相当外気温度, ℃, [8760 * 4]
    theta_o_sol: np.ndarray

    # 透過日射熱取得, W, [8760*4]
    q_trs_sol: np.ndarray

    # 応答係数データクラス
    rf: response_factor.ResponseFactor


class Boundaries:

    def __init__(self, id_rm_is: np.ndarray, bs_list: List[Dict], w: Weather):
        """

        Args:
            id_rm_is: 室のID, [i, 1]
            bs_list: 境界に関する辞書
            w: Weather クラス
        """

        self._bss = self._get_boundary_list(id_rm_is=id_rm_is, bs_list=bs_list, w=w)

    def _get_boundary_list(self, id_rm_is: np.ndarray, bs_list: List[Dict], w: Weather) -> List[Boundary]:
        """

        Args:
            id_rm_is: 室のID, [i, 1]
            bs_list: 境界に関する辞書
            w: Weather クラス

        Returns:

        """

        # 本来であれば Boundaries クラスにおいて境界に関する入力用辞書から読み込みを境界個別に行う。
        # しかし、室内側表面放射熱伝達は室内側の形態係数によって値が決まり、ある室に接する境界の面積の組み合わせで決定されるため、
        # 境界個別に値を決めることはできない。（すべての境界の情報が必要である。）
        # 一方で、境界の集約を行うためには、応答係数を Boundary クラス生成時に求める必要があり、
        # さらに応答係数の計算には裏面の表面放射・対流熱伝達率の値が必要となるため、
        # Boundary クラスを生成する前に、予め室内側表面放射・対流熱伝達率を計算しておき、
        # Boundary クラスを生成する時に必要な情報としておく。

        # 境界jの室内側表面放射熱伝達率, W/m2K, [J, 1]
        h_s_r_js = shape_factor.get_h_s_r_js(
            id_rm_is=id_rm_is,
            a_s_js=np.array([b['area'] for b in bs_list]).reshape(-1, 1),
            connected_room_id_js=np.array([b['connected_room_id'] for b in bs_list]).reshape(-1, 1)
        )

        # 境界jの室内側表面対流熱伝達率, W/m2K, [J, 1]
        h_c_js = np.array([b['h_c'] for b in bs_list]).reshape(-1, 1)

        # 境界 j, [J]
        bss = [self._get_boundary(b=b, h_c_js=h_c_js, h_s_r_js=h_s_r_js, w=w) for b in bs_list]

        return bss

    @staticmethod
    def _get_boundary(b: Dict, h_c_js: np.ndarray, h_s_r_js: np.ndarray, w: Weather) -> Boundary:
        """

        Args:
            b: Boundary　の辞書
            h_c_js: 境界 j の室内側表面対流熱伝達率, W/m2K, [J, 1]
            h_s_r_js: 境界 j の室内側表面放射熱伝達率, W/m2K, [J, 1]
            w: Weather クラス

        Returns:
            Boundary クラス
        """

        # ID
        # TODO: ID が0始まりで1ずつ増え、一意であることのチェックを行うコードを追記する。
        boundary_id = int(b['id'])

        # 名前
        name = b['name']

        # 副名称
        sub_name = b['sub_name']

        # 接する室のID
        # TODO: 指定された room_id が存在するかどうかをチェックするコードを追記する。
        connected_room_id = int(b['connected_room_id'])

        # 境界の種類
        boundary_type = BoundaryType(b['boundary_type'])

        # 面積, m2
        area = float(b['area'])
        if area <= 0.0:
            raise ValueError("境界(ID=" + boundary_id + ")の面積で0以下の値が指定されました。")

        # 日射の有無 (True:当たる/False: 当たらない)
        # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
        if boundary_type in [
            BoundaryType.ExternalGeneralPart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalOpaquePart
        ]:
            is_sun_striked_outside = bool(b['is_sun_striked_outside'])
        else:
            is_sun_striked_outside = None

        # 温度差係数
        # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
        # TODO: 下記、BoundaryType.Ground が指定されているのは間違い？　要チェック。
        if boundary_type in [
            BoundaryType.ExternalGeneralPart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalOpaquePart
        ]:
            h_td = float(b['temp_dif_coef'])
        elif boundary_type == BoundaryType.Ground:
            h_td = 1.0
        else:
            h_td = 0.0
        if h_td > 1.0:
            raise ValueError("境界(ID=" + str(boundary_id) + ")の温度差係数で1.0を超える値が指定されました。")
        if h_td < 0.0:
            raise ValueError("境界(ID=" + str(boundary_id) + ")の温度差係数で0.0を下回る値が指定されました。")

        # TODO: 指定された rear_surface_boundary_id の rear_surface_boundary_id が自分自信のIDかどうかのチェックが必要かもしれない。
        if boundary_type == BoundaryType.Internal:
            rear_surface_boundary_id = int(b['rear_surface_boundary_id'])
        else:
            rear_surface_boundary_id = None

        # 室内侵入日射吸収の有無 (True:吸収する/False:吸収しない)
        is_solar_absorbed_inside = bool(b['is_solar_absorbed_inside'])

        # 床か否か(True:床/False:床以外)
        is_floor = bool(b['is_floor'])

        # 方位
        # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
        if is_sun_striked_outside is not None:
            if is_sun_striked_outside:
                direction = Direction(b['direction'])
            else:
                direction = None
        else:
            direction = None

        # 室内側表面対流熱伝達率, W/m2K
        h_s_c = b['h_c']

        # 室内側表面放射熱伝達率, W/m2K
        h_s_r = h_s_r_js[boundary_id]

        # 日除け
        if is_sun_striked_outside is not None:
            if is_sun_striked_outside:
                ssp = SolarShading.create(ssp_dict=b['solar_shading_part'], direction=direction)
            else:
                ssp = None
        else:
            ssp = None

        # 室外側長波長放射率, -
        if boundary_type in [
            BoundaryType.ExternalGeneralPart, BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart
        ]:
            eps_r = float(b['outside_emissivity'])
            if eps_r > 1.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の室外側長波長放射率で1.0を超える値が指定されました。")
            if eps_r < 0.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の室外側長波長放射率で0.0を下回る値が指定されました。")
        else:
            eps_r = None

        # 室外側熱伝達抵抗, m2K/W
        if boundary_type in [
            BoundaryType.ExternalGeneralPart, BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart
        ]:
            r_surf = float(b['outside_heat_transfer_resistance'])
            if r_surf <= 0.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の室外側熱伝達抵抗で0.0以下の値が指定されました。")
        else:
            r_surf = None

        # 熱貫流率
        if boundary_type in [BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart]:
            u_value = float(b['u_value'])
            if u_value <= 0.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の熱貫流率で0.0以下の値が指定されました。")
        else:
            u_value = None

        # 室内側熱伝達抵抗, m2K/W
        if boundary_type in [BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart]:
            r_i = float(b['inside_heat_transfer_resistance'])
            if r_i <= 0.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の室内側熱伝達抵抗で0.0以下の値が指定されました。")
        else:
            r_i = None

        if boundary_type == BoundaryType.ExternalTransparentPart:

            # 日射熱取得率
            eta_value = float(b['eta_value'])
            if eta_value <= 0.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の日射熱取得率で0.0以下の値が指定されました。")

            # 開口部の面積に対するグレージングの面積の比率
            glass_area_ratio = b['glass_area_ratio']
            if glass_area_ratio < 0.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の開口部の面積に対するグレージング面積の比率で0.0未満の値が指定されました。")
            if glass_area_ratio > 1.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の開口部の面積に対するグレージング面積の比率で1.0より大の値が指定されました。")

            # グレージングの種類
            glazing_type = GlazingType(b['incident_angle_characteristics'])

            window = Window(r_a_glass_j=glass_area_ratio, eta_w_j=eta_value, glazing_type_j=glazing_type)

        else:

            window = None

        if boundary_type in [BoundaryType.ExternalGeneralPart, BoundaryType.ExternalOpaquePart]:
            a_s = float(b['outside_solar_absorption'])
            if a_s < 0.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の日射吸収率で0.0未満の値が指定されました。")
            if a_s > 1.0:
                raise ValueError("境界(ID=" + str(boundary_id) + ")の日射吸収率で1.0より大の値が指定されました。")
        else:
            a_s = None

        # 相当外気温度, degree C, [N+1]
        oet = OutsideEqvTemp.create(
            ss=ssp,
            boundary_type=boundary_type,
            is_sun_striked_outside=is_sun_striked_outside,
            direction=direction,
            eps_r=eps_r,
            r_surf=r_surf,
            u_value=u_value,
            window=window,
            a_s=a_s
        )

        theta_o_sol = oet.get_theta_o_sol_i_j_ns(w=w)

        # 透過日射量, W, [N+1]
        tsr = transmission_solar_radiation.TransmissionSolarRadiation.create(
            ss=ssp,
            boundary_type=boundary_type,
            direction=direction,
            area=area,
            window=window,
            is_sun_striked_outside=is_sun_striked_outside
        )

        q_trs_sol = tsr.get_qgt(w=w)

        # 応答係数
        if boundary_type in [BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart]:

            rf = ResponseFactor.create_for_steady(u_w=b['u_value'], r_i=r_i)

        else:

            cs = np.array([float(layer['thermal_capacity']) for layer in b['layers']])
            rs = np.array([float(layer['thermal_resistance']) for layer in b['layers']])

            if boundary_type == BoundaryType.ExternalGeneralPart:

                r_o = float(b['outside_heat_transfer_resistance'])
                rf = ResponseFactor.create_for_unsteady_not_ground(cs=cs, rs=rs, r_o=r_o)

            elif boundary_type == BoundaryType.Internal:

                rear_h_c = h_c_js[b['rear_surface_boundary_id'], 0]
                rear_h_r = h_s_r_js[b['rear_surface_boundary_id'], 0]

                r_o = 1.0 / (rear_h_c + rear_h_r)

                rf = ResponseFactor.create_for_unsteady_not_ground(cs=cs, rs=rs, r_o=r_o)

            elif boundary_type == BoundaryType.Ground:

                rf = ResponseFactor.create_for_unsteady_ground(cs=cs, rs=rs)

            else:

                KeyError()

        return Boundary(
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
            h_s_c=h_s_c,
            h_s_r=h_s_r,
            theta_o_sol=theta_o_sol,
            q_trs_sol=q_trs_sol,
            rf=rf
        )

    def get_n_b(self):

        return len(self._bss)

    def get_n_ground(self):
        # 地盤の数

        return sum(bs.boundary_type == BoundaryType.Ground for bs in self._bss)

    def get_id_js(self):
        # ID

        return np.array([bs.id for bs in self._bss]).reshape(-1, 1)

    def get_name_bdry_js(self):
        # 名前, [j, 1]

        return np.array([bs.name for bs in self._bss]).reshape(-1, 1)

    def get_sub_name_bdry_js(self):
        # 名前2, [j, 1]

        return np.array([bs.sub_name for bs in self._bss]).reshape(-1, 1)

    def get_p_is_js(self, n_rm):
        # 室iと境界jの関係を表す係数（境界jから室iへの変換）
        # [[p_0_0 ... ... p_0_j]
        #  [ ...  ... ...  ... ]
        #  [p_i_0 ... ... p_i_j]]

        p_is_js = np.zeros((n_rm, len(self._bss)), dtype=int)

        for i, bs in enumerate(self._bss):
            p_is_js[bs.connected_room_id, i] = 1

        return p_is_js

    def get_p_js_is(self, n_rm):
        # 室iと境界jの関係を表す係数（室iから境界jへの変換）
        # [[p_0_0 ... p_0_i]
        #  [ ...  ...  ... ]
        #  [ ...  ...  ... ]
        #  [p_j_0 ... p_j_i]]

        p_is_js = self.get_p_is_js(n_rm=n_rm)

        p_js_is = p_is_js.T

        return p_js_is

    def get_is_floor_js(self):

        return np.array([bs.is_floor for bs in self._bss]).reshape(-1, 1)

    def get_is_ground_js(self):
        # 地盤かどうか, [j, 1]

        return np.array([bs.boundary_type == BoundaryType.Ground for bs in self._bss]).reshape(-1, 1)

    def get_k_ei_js_js(self):
        # 境界jの裏面温度に他の境界の等価温度が与える影響, [j, j]

        return np.array([self._get_k_ei_js_j(bs=bs, n_boundaries=len(self._bss)) for bs in self._bss])

    def get_k_eo_js(self):
        # 温度差係数

        return np.array([bs.h_td for bs in self._bss]).reshape(-1, 1)

    def get_p_s_sol_abs_js(self):
        # 境界jの日射吸収の有無, [j, 1]

        return np.array([bs.is_solar_absorbed_inside for bs in self._bss]).reshape(-1, 1)

    def get_h_s_r_js(self):
        # 境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]

        return np.array([bs.h_s_r for bs in self._bss]).reshape(-1, 1)

    def get_h_s_c_js(self):
        # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]

        return np.array([bs.h_s_c for bs in self._bss]).reshape(-1, 1)

    def get_room_id_by_boundary_id(self, boundary_id: int):

        bs = self._get_boundary_by_id(boundary_id=boundary_id)

        return bs.connected_room_id

    def get_a_s_js(self):
        # 境界jの面積, m2, [j, 1]

        return np.array([bs.area for bs in self._bss]).reshape(-1, 1)

    def get_phi_a0_js(self):
        # 境界jの吸熱応答係数の初項, m2K/W, [j, 1]

        return np.array([bs.rf.rfa0 for bs in self._bss]).reshape(-1, 1)

    def get_phi_a1_js_ms(self):
        # 境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]

        return np.array([bs.rf.rfa1 for bs in self._bss])

    def get_phi_t0_js(self):
        # 境界jの貫流応答係数の初項, [j, 1]

        return np.array([bs.rf.rft0 for bs in self._bss]).reshape(-1, 1)

    def get_phi_t1_js_ms(self):
        # 境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]

        return np.array([bs.rf.rft1 for bs in self._bss])

    def get_r_js_ms(self):
        # 境界jの項別公比法における項mの公比, [j, 12]

        return np.array([bs.rf.row for bs in self._bss])

    def get_theta_o_eqv_js_ns(self):

        return np.array([bs.theta_o_sol for bs in self._bss])

    def get_q_trs_sol_is_ns(self, n_rm):

        return np.array([
            np.sum(np.array([bs.q_trs_sol for bs in self._bss if bs.connected_room_id == i]), axis=0)
            for i in range(n_rm)
        ])

    def _get_boundary_by_id(self, boundary_id: int) -> Boundary:

        # 指定された boundary_id に一致する Boundary を取得する。
        bss = [bs for bs in self._bss if bs.id == boundary_id]

        # 取得された Boundary は必ず1つのはずなので、「見つからない場合」「複数該当した場合」にはエラーを出す。
        if len(bss) == 0:
            raise Exception("指定された boundary_id に一致する boundary が見つかりませんでした。")
        if len(bss) >1:
            raise Exception("指定された boundary_id に一致する boundary が複数見つかりました。")

        return bss[0]

    @staticmethod
    def _get_k_ei_js_j(bs: Boundary, n_boundaries: int):

        k_ei_js_j = [0.0] * n_boundaries

        if bs.boundary_type in [
            BoundaryType.ExternalOpaquePart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalGeneralPart
        ]:

            h = bs.h_td

            # 温度差係数が1.0でない場合はk_ei_jsに値を代入する。
            # id は自分自身の境界IDとし、自分自身の表面の影響は1.0から温度差係数を減じた値になる。
            if h < 1.0:
                k_ei_js_j[bs.id] = round(1.0 - h, 2)
            else:
                # 温度差係数が1.0の場合は裏面の影響は何もないため k_ei_js に操作は行わない。
                pass

        elif bs.boundary_type == BoundaryType.Internal:

            # 室内壁の場合にk_ei_jsを登録する。
            k_ei_js_j[int(bs.rear_surface_boundary_id)] = 1.0

        else:

            # 外皮に面していない場合、室内壁ではない場合（地盤の場合が該当）は、k_ei_js に操作は行わない。
            pass

        return k_ei_js_j

