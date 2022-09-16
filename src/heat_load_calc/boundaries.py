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

    # 裏面温度に他の境界 j の等価室温が与える影響, [j, j]
    k_ei_js_j: List

    # 裏面温度に室 i の室温が与える影響, [i]
    k_s_r_j_is: List

    # 計算で使用する熱貫流率, W/m2K
    simulation_u_value: float


class Boundaries:

    def __init__(self, id_rm_is: np.ndarray, bs_list: List[Dict], w: Weather):
        """

        Args:
            id_rm_is: 室のID, [i, 1]
            bs_list: 境界に関する辞書
            w: Weather クラス
        Notes:
            本来であれば Boundaries クラスにおいて境界に関する入力用辞書から読み込みを境界個別に行う。
            しかし、室内側表面放射熱伝達は室内側の形態係数によって値が決まり、ある室に接する境界の面積の組み合わせで決定されるため、
            境界個別に値を決めることはできない。（すべての境界の情報が必要である。）
            一方で、境界の集約を行うためには、応答係数を Boundary クラス生成時に求める必要があり、
            さらに応答係数の計算には裏面の表面放射・対流熱伝達率の値が必要となるため、
            Boundary クラスを生成する前に、予め室内側表面放射・対流熱伝達率を計算しておき、
            Boundary クラスを生成する時に必要な情報としておく。
        """

        # 境界jの室内側表面放射熱伝達率, W/m2K, [J, 1]
        h_s_r_js = shape_factor.get_h_s_r_js(
            id_rm_is=id_rm_is,
            a_s_js=np.array([b['area'] for b in bs_list]).reshape(-1, 1),
            connected_room_id_js=np.array([b['connected_room_id'] for b in bs_list]).reshape(-1, 1)
        )

        # 境界jの室内側表面対流熱伝達率, W/m2K, [J, 1]
        h_c_js = np.array([b['h_c'] for b in bs_list]).reshape(-1, 1)

        # 室の数
        n_rm = id_rm_is.size

        # 境界 j, [J]
        bss = [self._get_boundary(b=b, h_c_js=h_c_js, h_s_r_js=h_s_r_js, w=w, n_rm=n_rm) for b in bs_list]

        # 室iと境界jの関係を表す係数（境界jから室iへの変換）, [i, j]
        p_is_js = self._get_p_is_js(n_rm=n_rm, bss=bss)

        # ステップ n の室 i における窓の透過日射熱取得, W, [n]
        q_trs_sol_is_ns = self.get_q_trs_sol_is_ns(n_rm=n_rm, bss=bss)

        self._bss = bss
        self._p_is_js = p_is_js
        self._q_trs_sol_is_ns = q_trs_sol_is_ns

    @staticmethod
    def _get_boundary(b: Dict, h_c_js: np.ndarray, h_s_r_js: np.ndarray, w: Weather, n_rm: int) -> Boundary:
        """

        Args:
            b: Boundary　の辞書
            h_c_js: 境界 j の室内側表面対流熱伝達率, W/m2K, [J, 1]
            h_s_r_js: 境界 j の室内側表面放射熱伝達率, W/m2K, [J, 1]
            w: Weather クラス
            n_rm: 室の数

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

        # 熱貫流率の計算
        # シミュレーションで使用する室内熱伝達抵抗の計算
        inner_h_c = h_c_js[b['id'], 0]
        inner_h_r = h_s_r_js[b['id'], 0]
        simulation_r_i = 1.0 / (inner_h_c + inner_h_r)
        simulation_u_value = 0.0

        if boundary_type in [BoundaryType.ExternalTransparentPart, BoundaryType.ExternalOpaquePart]:

            input_r_i = b['inside_heat_transfer_resistance']
            input_u_value = float(b['u_value'])
            simulation_u_value = 1.0 / (1.0 / input_u_value - input_r_i + simulation_r_i)

        else:

            sum_rs = np.sum(np.array([float(layer['thermal_resistance']) for layer in b['layers']]))

            if boundary_type == BoundaryType.ExternalGeneralPart:

                r_o = float(b['outside_heat_transfer_resistance'])

                simulation_u_value = 1.0 / (simulation_r_i + sum_rs + r_o)

            elif boundary_type == BoundaryType.Internal:

                rear_h_c = h_c_js[b['rear_surface_boundary_id'], 0]
                rear_h_r = h_s_r_js[b['rear_surface_boundary_id'], 0]

                r_o = 1.0 / (rear_h_c + rear_h_r)

                simulation_u_value = 1.0 / (simulation_r_i + sum_rs + r_o)

            elif boundary_type == BoundaryType.Ground:

                simulation_u_value = 1.0 / (simulation_r_i + sum_rs)

            else:
                KeyError()

        # Boundary の数
        n_b = h_c_js.size

        k_ei_js_j = [0.0] * n_b

        if boundary_type in [
            BoundaryType.ExternalOpaquePart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalGeneralPart
        ]:
            pass

#            h = h_td

            # 温度差係数が1.0でない場合はk_ei_jsに値を代入する。
            # id は自分自身の境界IDとし、自分自身の表面の影響は1.0から温度差係数を減じた値になる。
#            if h < 1.0:
#                k_ei_js_j[boundary_id] = round(1.0 - h, 2)
#            else:
                # 温度差係数が1.0の場合は裏面の影響は何もないため k_ei_js に操作は行わない。
#                pass

        elif boundary_type == BoundaryType.Internal:

            # 室内壁の場合にk_ei_jsを登録する。
            k_ei_js_j[int(rear_surface_boundary_id)] = 1.0

        else:

            # 外皮に面していない場合、室内壁ではない場合（地盤の場合が該当）は、k_ei_js に操作は行わない。
            pass

        k_s_r_j_is = [0.0] * n_rm

        if boundary_type in [
            BoundaryType.ExternalOpaquePart,
            BoundaryType.ExternalTransparentPart,
            BoundaryType.ExternalGeneralPart
        ]:

            h = h_td

            # 温度差係数が1.0でない場合はk_ei_jsに値を代入する。
            # id は自分自身の境界IDとし、自分自身の表面の影響は1.0から温度差係数を減じた値になる。
            if h < 1.0:
                k_s_r_j_is[connected_room_id] = round(1.0 - h, 2)
            else:
                # 温度差係数が1.0の場合は裏面の影響は何もないため k_ei_js に操作は行わない。
                pass

        else:

            pass

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
            simulation_u_value=simulation_u_value,
            theta_o_sol=theta_o_sol,
            q_trs_sol=q_trs_sol,
            rf=rf,
            k_ei_js_j=k_ei_js_j,
            k_s_r_j_is=k_s_r_j_is
        )

    @staticmethod
    def _get_p_is_js(n_rm, bss):
        # 室iと境界jの関係を表す係数（境界jから室iへの変換）
        # [[p_0_0 ... ... p_0_j]
        #  [ ...  ... ...  ... ]
        #  [p_i_0 ... ... p_i_j]]

        p_is_js = np.zeros((n_rm, len(bss)), dtype=int)

        for i, bs in enumerate(bss):
            p_is_js[bs.connected_room_id, i] = 1

        return p_is_js

    @staticmethod
    def get_q_trs_sol_is_ns(n_rm, bss):

        return np.array([
            np.sum(np.array([bs.q_trs_sol for bs in bss if bs.connected_room_id == i]), axis=0)
            for i in range(n_rm)
        ])

    @property
    def n_b(self):
        """

        Returns:
            境界の数
        """

        return len(self._bss)

    @property
    def n_ground(self):
        """

        Returns:
            地盤の数
        """

        return sum(bs.boundary_type == BoundaryType.Ground for bs in self._bss)

    @property
    def id_js(self):
        """

        Returns:
            ID
        """

        return np.array([bs.id for bs in self._bss]).reshape(-1, 1)

    @property
    def name_b_js(self):
        """

        Returns:
            名前, [j, 1]
        """

        return np.array([bs.name for bs in self._bss]).reshape(-1, 1)

    @property
    def sub_name_b_js(self):
        """

        Returns:
            名前2, [j, 1]
        """

        return np.array([bs.sub_name for bs in self._bss]).reshape(-1, 1)

    @property
    def p_is_js(self):
        """

        Returns:
            室iと境界jの関係を表す係数（境界jから室iへの変換）
        Notes:
            室iと境界jの関係を表す係数（境界jから室iへの変換）
            [[p_0_0 ... ... p_0_j]
             [ ...  ... ...  ... ]
             [p_i_0 ... ... p_i_j]]

        """

        return self._p_is_js

    @property
    def p_js_is(self):
        """

        Returns:
            室iと境界jの関係を表す係数（室iから境界jへの変換）
        Notes:
            [[p_0_0 ... p_0_i]
             [ ...  ...  ... ]
             [ ...  ...  ... ]
             [p_j_0 ... p_j_i]]
        """

        return self._p_is_js.T

    @property
    def is_floor_js(self):
        """

        Returns:
            床かどうか, [j, 1]
        """

        return np.array([bs.is_floor for bs in self._bss]).reshape(-1, 1)

    @property
    def is_ground_js(self):
        """

        Returns:
            地盤かどうか, [j, 1]
        """

        return np.array([bs.boundary_type == BoundaryType.Ground for bs in self._bss]).reshape(-1, 1)

    @property
    def k_ei_js_js(self):
        """

        Returns:
            境界jの裏面温度に他の境界の等価室温が与える影響, [j, j]
        """

        return np.array([bs.k_ei_js_j for bs in self._bss])
        
    @property
    def k_eo_js(self):
        """

        Returns:
            温度差係数
        """

        return np.array([bs.h_td for bs in self._bss]).reshape(-1, 1)

    @property
    def k_s_r_js_is(self):
        """

        Returns:
            境界 j の裏面温度に室温が与える影響, [j, i]
        """

        return np.array([bs.k_s_r_j_is for bs in self._bss])

    @property
    def p_s_sol_abs_js(self):
        """

        Returns:
            境界jの日射吸収の有無, [j, 1]
        """

        return np.array([bs.is_solar_absorbed_inside for bs in self._bss]).reshape(-1, 1)

    @property
    def h_s_r_js(self):
        """

        Returns:
            境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]
        """

        return np.array([bs.h_s_r for bs in self._bss]).reshape(-1, 1)

    @property
    def h_s_c_js(self):
        # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]

        return np.array([bs.h_s_c for bs in self._bss]).reshape(-1, 1)

    @property
    def simulation_u_value(self):
        # 境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]

        return np.array([bs.simulation_u_value for bs in self._bss]).reshape(-1, 1)

    @property
    def a_s_js(self):
        """

        Returns:
            境界jの面積, m2, [j, 1]
        """

        return np.array([bs.area for bs in self._bss]).reshape(-1, 1)

    @property
    def phi_a0_js(self):
        """

        Returns:
            境界jの吸熱応答係数の初項, m2K/W, [j, 1]
        """

        return np.array([bs.rf.rfa0 for bs in self._bss]).reshape(-1, 1)

    @property
    def phi_a1_js_ms(self):
        """

        Returns:
            境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]
        """

        return np.array([bs.rf.rfa1 for bs in self._bss])

    @property
    def phi_t0_js(self):
        """

        Returns:
            境界jの貫流応答係数の初項, [j, 1]
        """

        return np.array([bs.rf.rft0 for bs in self._bss]).reshape(-1, 1)

    @property
    def phi_t1_js_ms(self):
        """

        Returns:
            境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]
        """

        return np.array([bs.rf.rft1 for bs in self._bss])

    @property
    def r_js_ms(self):
        """

        Returns:
            境界jの項別公比法における項mの公比, [j, 12]
        """

        return np.array([bs.rf.row for bs in self._bss])

    @property
    def theta_o_eqv_js_ns(self):
        """

        Returns:
            ステップ n の境界 j における相当外気温度, ℃, [j, n+1]
        """

        return np.array([bs.theta_o_sol for bs in self._bss])

    @property
    def q_trs_sol_is_ns(self):
        """

        Returns:
            ステップ n の室 i における窓の透過日射熱取得, W, [n]
        """

        return self._q_trs_sol_is_ns

    def get_room_id_by_boundary_id(self, boundary_id: int):

        bs = self._get_boundary_by_id(boundary_id=boundary_id)

        return bs.connected_room_id

    def _get_boundary_by_id(self, boundary_id: int) -> Boundary:

        # 指定された boundary_id に一致する Boundary を取得する。
        bss = [bs for bs in self._bss if bs.id == boundary_id]

        # 取得された Boundary は必ず1つのはずなので、「見つからない場合」「複数該当した場合」にはエラーを出す。
        if len(bss) == 0:
            raise Exception("指定された boundary_id に一致する boundary が見つかりませんでした。")
        if len(bss) >1:
            raise Exception("指定された boundary_id に一致する boundary が複数見つかりました。")

        return bss[0]

