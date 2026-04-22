import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

from heat_load_calc.matrix_method import v_diag
from heat_load_calc import response_factor, transmission_solar_radiation, shape_factor
from heat_load_calc.weather import Weather
from heat_load_calc.response_factor import ResponseFactor
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc import outside_eqv_temp
from heat_load_calc import transmission_solar_radiation
from heat_load_calc.window import Window
from heat_load_calc.tenum import EShapeFactorMethod, EGlassType
from heat_load_calc.input_models.input_boundary import (
    InputBoundary,
    InputBoundaryExternalGeneralPart,
    InputBoundaryExternalTransparentPart,
    InputBoundaryExternalOpaquePart,
    InputBoundaryGround,
    InputBoundaryInternal
)
from heat_load_calc.input_models.input_solar_shading_part import (
    InputSolarShadingPart,
    InputSolarShadingPartSimple,
    InputSolarShadingPartDetail,
    InputSolarShadingPartNot
)
from heat_load_calc.boundary_component import (
    BoundaryComponentResponseFactor,
    BoundaryComponents,
    BoundaryComponentsStatus
)

from heat_load_calc.tenum import EBoundaryType


from typing import Protocol, runtime_checkable

@runtime_checkable
class TempDifCoefHolder(Protocol):
    temp_dif_coef: float

@runtime_checkable
class RearSurfaceBoundaryIdHolder(Protocol):
    rear_surface_boundary_id: int

@runtime_checkable
class IsSunStrikedOutsideHolder(Protocol):
    is_sun_striked_outside: bool

@runtime_checkable
class DirectionHolder(Protocol):
    direction: Direction

@runtime_checkable
class SolarShadingPartHolder(Protocol):
    solar_shading_part: InputSolarShadingPart

@runtime_checkable
class OutsideSolarAbsorptionHolder(Protocol):
    outside_solar_absorption: float

@runtime_checkable
class OutsideHeatTransferResistanceHolder(Protocol):
    outside_heat_transfer_resistance: float

@runtime_checkable
class OutsideEmissivityHolder(Protocol):
    outside_emissivity: float

@runtime_checkable
class UValueHolder(Protocol):
    u_value: float

@runtime_checkable
class EtaValueHolder(Protocol):
    eta_value: float

@runtime_checkable
class GlassAreaRatioHolder(Protocol):
    glass_area_ratio: float

@runtime_checkable
class IncidentAngleCharacteristics(Protocol):
    incident_angle_characteristics: EGlassType


@dataclass
class Boundary:

    # ID
    id: int

    # 名称
    name: str

    # 副名称
    sub_name: str

    # 境界の種類
    t_b: EBoundaryType

    # 面積, m2
    a_s: float

    # 温度差係数
    k_eo: float

    # 床か否か
    b_floor: bool

    # 室内侵入日射吸収の有無
    b_sol_abs: bool

    # 相当外気温度, ℃, [8760 * 4]
    theta_o_eqv_nspls: np.ndarray

    # 透過日射熱取得, W, [8760*4]
    q_trs_sol_nplus: np.ndarray

    # 応答係数データクラス
    rf: response_factor.ResponseFactor

    # 裏面温度に他の境界 j の等価室温が与える影響, [j, j]
    k_ei_js: np.ndarray

    # 裏面温度に室の空気温度が与える影響
    k_s_r: float

    # boundary component
    bcomp: BoundaryComponentResponseFactor

    @staticmethod
    def _get_k_eo_j(ipt_boundary: InputBoundary):

        if (
            isinstance(ipt_boundary, InputBoundaryExternalGeneralPart)
            or isinstance(ipt_boundary, InputBoundaryExternalTransparentPart)
            or isinstance(ipt_boundary, InputBoundaryExternalOpaquePart)
        ):
            if not isinstance(ipt_boundary, TempDifCoefHolder):
                raise Exception()
            return ipt_boundary.temp_dif_coef

        elif isinstance(ipt_boundary, InputBoundaryGround):
            return 1.0

        elif isinstance(ipt_boundary, InputBoundaryInternal):
            return 0.0

        else:
            raise Exception()

    @staticmethod
    def _get_boundary_index(id_js: np.ndarray, rear_surface_boundary_id: int, id: int) -> int:
        """Get the boundary index matched to the specify id.

        Args:
            id_js: list of the indices of boundaries
            rear_surface_boundary_id: specified boundary id as rear surface
            id: id of this boundary

        Raises:
            ValueError: There is no boundary index corresponding to the specified index.
            ValueError: Multiple indices were found corresponding to the specified index.

        Returns:
            the boundary index
        """

        matched_indices = [index for (index, id_j) in enumerate(id_js) if id_j == rear_surface_boundary_id]

        if len(matched_indices) == 0:
            raise ValueError("境界(ID=" + str(id) + ")(間仕切りの場合)の裏面のIDとして指定する boundary ID 存在しませんでした。")
        if len(matched_indices) > 1:
            raise ValueError("境界(ID=" + str(id) + ")(間仕切りの場合)の裏面のIDとして指定する boundary ID が複数存在しました。")
        
        return matched_indices[0]

    @classmethod
    def _get_j_rear_j(cls, ipt_boundary: InputBoundary, id_js: np.ndarray):

        if isinstance(ipt_boundary, RearSurfaceBoundaryIdHolder):
            rear_surface_boundary_id = ipt_boundary.rear_surface_boundary_id
            return cls._get_boundary_index(
                id_js=id_js,
                rear_surface_boundary_id=rear_surface_boundary_id,
                id=ipt_boundary.id
            )

        else:
            return None

    @staticmethod
    def get_window_j(ipt_boundary: InputBoundaryExternalTransparentPart) -> Window:

        # standard heat transmittance coefficient (u value) of boundary j, W / ( m2 K )
        u_w_std_j = ipt_boundary.u_value

        # standard solar gain coefficient (eta value) of boundary j, -
        eta_w_std_j = ipt_boundary.eta_value

        # grazing type of boundary j
        t_glz_j = ipt_boundary.incident_angle_characteristics

        # grazing area ratio of boundary j, -
        r_a_w_g_j = ipt_boundary.glass_area_ratio

        return Window(u_w_std_j=u_w_std_j, eta_w_std_j=eta_w_std_j, t_glz_j=t_glz_j, r_a_w_g_j=r_a_w_g_j)

    @staticmethod
    def _get_theta_o_eqv_j_ns(w: Weather, ipt_boundary: InputBoundary) -> np.ndarray:
        """Calculate the equivalent outside temperature of boundary j at step n.

        Args:
            w: weather class
            ipt_boundary: InputBoundary class

        Returns:
            equivalent outside temperature of boundary j at step n, degree C, [N+1]
        """
        
        if isinstance(ipt_boundary, InputBoundaryInternal):
        
            return outside_eqv_temp.get_theta_o_eqv_j_ns_for_internal(w=w)

        elif (
            isinstance(ipt_boundary, InputBoundaryExternalGeneralPart)
            or isinstance(ipt_boundary, InputBoundaryExternalOpaquePart)
        ):
            
            if ipt_boundary.is_sun_striked_outside:

                t_drct_j = ipt_boundary.direction

                a_sol_j = ipt_boundary.outside_solar_absorption

                eps_r_o_j = ipt_boundary.outside_emissivity

                r_s_o_j = ipt_boundary.outside_heat_transfer_resistance

                ssp_j = SolarShading.create(direction=t_drct_j, input_solar_shading_part=ipt_boundary.solar_shading_part)

                return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_general_part_and_external_opaque_part(
                    t_drct_j=t_drct_j, a_sol_j=a_sol_j, eps_r_o_j=eps_r_o_j, r_s_o_j=r_s_o_j, ssp_j=ssp_j, w=w
                )

            else:

                return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_not_sun_striked(w=w)  

        elif isinstance(ipt_boundary, InputBoundaryExternalTransparentPart):

            if ipt_boundary.is_sun_striked_outside:

                t_drct_j = ipt_boundary.direction

                eps_r_o_j = ipt_boundary.outside_emissivity

                r_s_o_j = ipt_boundary.outside_heat_transfer_resistance

                # standard heat transmittance coefficient (u value) of boundary j, W / ( m2 K )
                u_w_std_j = ipt_boundary.u_value

                window_j = Boundary.get_window_j(ipt_boundary=ipt_boundary)

                ssp_j = SolarShading.create(direction=t_drct_j, input_solar_shading_part=ipt_boundary.solar_shading_part)

                return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_transparent_part(
                    t_drct_j=t_drct_j, eps_r_o_j=eps_r_o_j, r_s_o_j=r_s_o_j, u_w_std_j=u_w_std_j, ssp_j=ssp_j, window_j=window_j, w=w
                )

            else:

                return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_not_sun_striked(w=w)

        elif isinstance(ipt_boundary, InputBoundaryGround):

            return outside_eqv_temp.get_theta_o_eqv_j_ns_for_ground(w=w)

        else:

            raise Exception()

    @staticmethod
    def _get_q_trs_sol_j_ns(w: Weather, ipt_boundary: InputBoundary) -> np.ndarray:
        """Calculate the transmitted solar radiation of boundary j at step n

        Args:
            w: weather class
            ipt_boundary: InputBoundary class

        Returns:
            transmitted solar radiation of boundary j at step n, W, [N+1]
        """

        if (
            isinstance(ipt_boundary, InputBoundaryInternal)
            or isinstance(ipt_boundary, InputBoundaryExternalGeneralPart)
            or isinstance(ipt_boundary, InputBoundaryExternalOpaquePart)
            or isinstance(ipt_boundary, InputBoundaryGround)
        ):

            return transmission_solar_radiation.get_q_trs_sol_j_ns_for_not(w=w)

        elif isinstance(ipt_boundary, InputBoundaryExternalTransparentPart):

            if ipt_boundary.is_sun_striked_outside:

                t_drct_j = ipt_boundary.direction

                # surface area of boundary j/ 面積, m2
                a_s_j = ipt_boundary.area

                # solar shading of boundary j / 日よけ        
                #ssp_j = _read_ssp(ipt_boundary=ipt_boundary)
                ssp_j = SolarShading.create(direction=t_drct_j, input_solar_shading_part=ipt_boundary.solar_shading_part)

                window_j = Boundary.get_window_j(ipt_boundary=ipt_boundary)

                return transmission_solar_radiation.get_q_trs_sol_j_ns_for_transparent_sun_striked(
                    t_drct_j=t_drct_j, a_s_j=a_s_j, ssp_j=ssp_j, window_j=window_j, w=w
                )
        
            else:

                return transmission_solar_radiation.get_q_trs_sol_j_ns_for_not(w=w)
        
        else:

            raise Exception()

    @staticmethod
    def _get_boundary_component(
            ipt_boundary: InputBoundary,
            h_s_c_js: np.ndarray,
            h_s_r_js: np.ndarray,
            id_js: np.ndarray
        ) -> BoundaryComponentResponseFactor:
        """Get response factor of boundary j.

        Args:
            ipt_boundary:
            h_s_c_js: convective heat transfer coefficient of inside surface of boundary j, W/m2K, [J, 1]
            h_s_r_js: radiative heat transfer coefficient of inside surface of boundary j, W/m2K, [J, 1]
            id_js:

        Returns:
            response factor class
        """

        if isinstance(ipt_boundary, InputBoundaryInternal):

            c_j_ls = np.array([ipt_layer.thermal_capacity for ipt_layer in ipt_boundary.ipt_layers])
            r_j_ls = np.array([ipt_layer.thermal_resistance for ipt_layer in ipt_boundary.ipt_layers])

            j_rear_j = Boundary._get_j_rear_j(ipt_boundary=ipt_boundary, id_js=id_js)
            h_s_c_rear_j = h_s_c_js[j_rear_j, 0]
            h_s_r_rear_j = h_s_r_js[j_rear_j, 0]

            r_rear_j = 1.0 / (h_s_c_rear_j + h_s_r_rear_j)

            bcomp = BoundaryComponentResponseFactor.create_for_unsteady_not_ground(cs=c_j_ls, rs=r_j_ls, r_o=r_rear_j)

            return bcomp

        elif isinstance(ipt_boundary, InputBoundaryExternalGeneralPart):

            c_j_ls = np.array([ipt_layer.thermal_capacity for ipt_layer in ipt_boundary.ipt_layers])
            r_j_ls = np.array([ipt_layer.thermal_resistance for ipt_layer in ipt_boundary.ipt_layers])

            r_s_o_j = ipt_boundary.outside_heat_transfer_resistance

            bcomp = BoundaryComponentResponseFactor.create_for_unsteady_not_ground(cs=c_j_ls, rs=r_j_ls, r_o=r_s_o_j)

            return bcomp

        elif (
            isinstance(ipt_boundary, InputBoundaryExternalTransparentPart)
            or isinstance(ipt_boundary, InputBoundaryExternalOpaquePart)
        ):

            r_i_std_j = ipt_boundary.inside_heat_transfer_resistance

            u_w_std_j = ipt_boundary.u_value

            bcomp = BoundaryComponentResponseFactor.create_for_steady(u_w=u_w_std_j, r_i=r_i_std_j)

            return bcomp

        elif isinstance(ipt_boundary, InputBoundaryGround):

            c_j_ls = np.array([ipt_layer.thermal_capacity for ipt_layer in ipt_boundary.ipt_layers])
            r_j_ls = np.array([ipt_layer.thermal_resistance for ipt_layer in ipt_boundary.ipt_layers])

            bcomp = BoundaryComponentResponseFactor.create_for_unsteady_ground(cs=c_j_ls, rs=r_j_ls)

            return bcomp

        else:

            raise KeyError()

    @classmethod
    def _get_k_ei_js_j(cls, id_js: np.ndarray, ipt_boundary: InputBoundary) -> np.ndarray:

        k_ei_js_j = np.zeros_like(id_js, dtype=float).flatten()

        if (
            isinstance(ipt_boundary, InputBoundaryExternalGeneralPart)
            or isinstance(ipt_boundary, InputBoundaryExternalTransparentPart)
            or isinstance(ipt_boundary, InputBoundaryExternalOpaquePart)
            or isinstance(ipt_boundary, InputBoundaryGround)
        ):

            pass

        elif isinstance(ipt_boundary, InputBoundaryInternal):

            j_rear_j = cls._get_j_rear_j(ipt_boundary=ipt_boundary, id_js=id_js)

            # 室内壁の場合にk_ei_jsを登録する。
            k_ei_js_j[j_rear_j] = 1.0

        else:
            raise Exception()
        
        return k_ei_js_j

    @staticmethod
    def _get_k_s_r_j(ipt_boundary: InputBoundary) -> float:
        """Get the coefficient representing the effect of the room air temperature to the rear temperature of boundary j.

        Args:
            ipt_boundary: InputBoundary class

        Returns:
            coefficient representing the effect of room air temperature to rear temperature of boundary j
        """

        if (
            isinstance(ipt_boundary, InputBoundaryExternalGeneralPart)
            or isinstance(ipt_boundary, InputBoundaryExternalTransparentPart)
            or isinstance(ipt_boundary, InputBoundaryExternalOpaquePart)
        ):
            
            #if k_eo_j is None:
            #    raise Exception("k_eo_j should be defined when boundary type is external opaque part, external transparent part, or external general part.")
            
            if not isinstance(ipt_boundary, TempDifCoefHolder):
                raise Exception()
            
            # TODO: なぜここはRound?
            return round(1.0 - ipt_boundary.temp_dif_coef, 2)

            #return round(1.0 - k_eo_j, 2)

        elif (
            isinstance(ipt_boundary, InputBoundaryInternal)
            or isinstance(ipt_boundary, InputBoundaryGround)
        ):
            return 0.0

        else:
            raise Exception()

    @classmethod
    def get_boundary(cls, h_s_c_js: np.ndarray, h_s_r_js: np.ndarray, w: Weather, id_js: np.ndarray, ipt_boundary: InputBoundary):
        """

        Args:
            h_s_c_js: 境界jの室内側表面対流熱伝達率, W/m2K, [J, 1]
            h_s_r_js: 境界jの室内側表面放射熱伝達率, W/m2K, [J, 1]
            w: Weather クラス
            id_js: id of boundaries, [J]
            ipt_boundary: InputBoundary class

        Returns:
            Boundary クラス
        """

        # ID of boundary j
        id_j = ipt_boundary.id

        # name of boundary j / 名前
        name_j = ipt_boundary.name

        # sub name of boundary j / 副名称
        sub_name_j = ipt_boundary.sub_name

        # type of boundary j / 境界の種類
        t_b_j = ipt_boundary.boundary_type

        # surface area of boundary j/ 面積, m2
        a_s_j = ipt_boundary.area

        # temperature difference coefficient of boundary j / 温度差係数
        k_eo_j = cls._get_k_eo_j(ipt_boundary=ipt_boundary)

        # is inside solar radiation absorbed of boundary j / 室内侵入日射吸収の有無 (True:吸収する/False:吸収しない)
        b_sol_abs_j = ipt_boundary.is_solar_absorbed_inside

        # is boundary j floor / 床か否か(True:床/False:床以外)
        b_floor_j = ipt_boundary.is_floor

        # equivalent outside temperature of boundary i at step n, degree C, [N+1]
        theta_o_eqv_j_nspls = cls._get_theta_o_eqv_j_ns(w=w, ipt_boundary=ipt_boundary)

        # transmitted solar radiation of boundary j at step n, W, [N+1]
        q_trs_sol_j_nspls = cls._get_q_trs_sol_j_ns(w=w, ipt_boundary=ipt_boundary)

        # boundary component
        bcomp = cls._get_boundary_component(ipt_boundary=ipt_boundary, h_s_c_js=h_s_c_js, h_s_r_js=h_s_r_js, id_js=id_js)

        # response factor of boundary j
        rf = bcomp.rf
        
        # coefficient representing the effect of equivalent room temperature of other boundary j to the rear temperature of boundary j
        # 裏面温度に他の境界 j の等価室温が与える影響, [J]
        k_ei_js_j = cls._get_k_ei_js_j(id_js=id_js, ipt_boundary=ipt_boundary)

        # coefficient representing the effect of room air temperature to the rear temperature of boundary j / 裏面温度に室の空気温度が与える影響
        k_s_r_j = cls._get_k_s_r_j(ipt_boundary=ipt_boundary)

        return Boundary(
            id=id_j,
            name=name_j,
            sub_name=sub_name_j,
            t_b=t_b_j,
            a_s=a_s_j,
            k_eo=k_eo_j,
            b_floor=b_floor_j,
            b_sol_abs=b_sol_abs_j,
            theta_o_eqv_nspls=theta_o_eqv_j_nspls,
            q_trs_sol_nplus=q_trs_sol_j_nspls,
            rf=rf,
            k_ei_js=k_ei_js_j,
            k_s_r=k_s_r_j,
            bcomp=bcomp
        )


@dataclass
class Boundaries:

    # number of boundaries
    n_b: int

    # number_of_boundaries of ground
    n_ground: int

    # IDs, [J, 1]
    id_js: np.ndarray

    # name, [J, 1]
    name_js: np.ndarray

    # subname, [J, 1]
    sub_name_js: np.ndarray

    # connected room IDs, [J, 1]
    connected_room_id_js: np.ndarray

    # coefficient of relation between room i and boundary j
    # example　(vertical axis = room, horizontal axis = boundary)
    #  [[p_0_0 ... ... p_0_j]
    #   [ ...  ... ...  ... ]
    #   [p_i_0 ... ... p_i_j]]
    p_is_js: np.ndarray

    # p_is_js.T
    p_js_is: np.ndarray

    # is the boundary floor ?, [J, 1]
    b_floor_js: np.ndarray

    # is the boundary ground ?, [J, 1]
    b_ground_js: np.ndarray

    # coefficient of effects
    # of equivallent temperature of other boundary
    # to rear surface temperature of the given boundary
    # [J, J]
    k_ei_js_js: np.ndarray

    # coefficient of effects
    # of outdoor air temperature
    # to rear surface temperature of the given boundary
    # (temperature different coefficient)
    # [J, 1] 
    k_eo_js: np.ndarray

    # coefficient of effects
    # of room temperature
    # to rear surface temperature of the given boundary
    # [J, I]
    k_s_r_js_is: np.ndarray

    # Wheter does the surface of boundary absorb solar radiation ?
    b_s_sol_abs_js: np.ndarray

    # radiative heat transfer coefficient of inside surface, W/m2K, [J, 1]
    h_s_r_js: np.ndarray

    # convective heat transfer coefficient of inside surface, W/m2K, [J, 1]
    h_s_c_js: np.ndarray

    # thermal transfer coefficient, W/m2K, [J, 1]
    # the value calculated in this simulation is used as thermal resistance of surface
    u_js: np.ndarray

    # area, m2, [J, 1]
    a_s_js: np.ndarray

    # long wave emissivity, -, [J, 1]
    eps_r_i_js: np.ndarray

    # initial term of heat absorption response factor, m2K/W, [J, 1]
    phi_a0_js: np.ndarray

    # initial term of heat transmission response factor, -, [J, 1]
    phi_t0_js: np.ndarray

    # equivalent outdoor temperature at step n+1, deg.C, [J, N+1]
    theta_o_eqv_js_nspls: np.ndarray

    # transmitted solar heat gain at step n+1, W, [J, N+1]
    q_trs_sol_js_nspls: np.ndarray

    # shape factor for microsphier in the room, [I, J]
    f_mrt_is_js: np.ndarray

    # coeeficient f_ax, -, [J, J]
    f_ax_js_js: np.ndarray

    # coefficient f_wsr, -, [J, I]
    f_wsr_js_is: np.ndarray

    # boundary components class
    bcomps: BoundaryComponents

    # boundary components class for ground
    bcomps_ground: BoundaryComponents

    @classmethod
    def create(cls, id_r_is: np.ndarray, w: Weather, rad_method: EShapeFactorMethod, ipt_boundaries: list[InputBoundary]):
        """

        Args:
            id_r_is: room id, [I, 1]
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

        # number of boundaries
        n_b = len(ipt_boundaries)

        # boundary id, [J]
        id_js = np.array([ipt_boundary.id for ipt_boundary in ipt_boundaries]).reshape(-1, 1)

        # connected foom id, [J, 1]
        connected_room_id_js = np.array([ipt_boundary.connected_room_id for ipt_boundary in ipt_boundaries]).reshape(-1, 1)

        # coefficient of relation between room i and boundary j / 室iと境界jの関係を表す係数（境界jから室iへの変換）, [I, J]
        p_is_js = _get_p_is_js(id_r_is=id_r_is, connected_room_id_js=connected_room_id_js)

        p_js_is = p_is_js.T

        # surface area of boundary j / 境界jの面積, m2, [J, 1]
        a_s_js = np.array([ipt_boundary.area for ipt_boundary in ipt_boundaries]).reshape(-1, 1)

        # indoor surface emissivity of boundary j / 境界jの室内側長波長放射率
        eps_r_i_js = np.array([ipt_boundary.inside_emissivity for ipt_boundary in ipt_boundaries]).reshape(-1, 1)

        # indoor surface radiant heat transfer coefficient of boundary j / 境界jの室内側表面放射熱伝達率, W/m2K, [J, 1]
        h_s_r_js = shape_factor.get_h_s_r_js(a_s_js=a_s_js, p_is_js=p_is_js, eps_r_i_js=eps_r_i_js, method=rad_method)

        # indoor surface convection heat transfer coefficient of boundary j / 境界jの室内側表面対流熱伝達率, W/m2K, [J, 1]
        h_s_c_js = np.array([ipt_boundary.h_c for ipt_boundary in ipt_boundaries]).reshape(-1, 1)

        # boundary j / 境界 j, [J]
        bss = [Boundary.get_boundary(h_s_c_js=h_s_c_js, h_s_r_js=h_s_r_js, w=w, id_js=id_js, ipt_boundary=ipt_boundary) for ipt_boundary in ipt_boundaries]

        # GOUND の数
        n_ground = sum(bs.t_b == EBoundaryType.GROUND for bs in bss)

        # id of boundary j, [J, 1]
        id_js = np.array([bs.id for bs in bss]).reshape(-1, 1)

        # name of boundary j, [J, 1]
        name_js = np.array([bs.name for bs in bss]).reshape(-1, 1)

        # sub name of boundary j, [J, 1]
        sub_name_js = np.array([bs.sub_name for bs in bss]).reshape(-1, 1)

        # is the boundary j floor ?, [J, 1]
        b_floor_js = np.array([bs.b_floor for bs in bss]).reshape(-1, 1)

        # is the boundary j ground ?, [J, 1]
        b_ground_js = np.array([bs.t_b == EBoundaryType.GROUND for bs in bss]).reshape(-1, 1)

        # coefficient representing the effect of equivalent room temperature of other boundary j to the rear temperature of boundary j
        # 裏面温度に他の境界 j の等価室温が与える影響, [J, J]
        k_ei_js_js = np.array([bs.k_ei_js for bs in bss])

        # temperature difference coefficient of boundary j / 温度差係数, [J]
        k_eo_js = np.array([bs.k_eo for bs in bss]).reshape(-1, 1)

        # coefficient representing the effect of room air temperature i to the rear temperature of boundary j / 裏面温度に室の空気温度が与える影響, [J, I]
        k_s_r_js = np.array([bs.k_s_r for bs in bss])
        k_s_r_js_is = p_is_js.T * k_s_r_js[:, np.newaxis]

        # is inside solar radiation absorbed of boundary j / 室内侵入日射吸収の有無 (True:吸収する/False:吸収しない) 
        b_sol_abs_js = np.array([bs.b_sol_abs for bs in bss]).reshape(-1, 1)

        # the resistance from the inside surface of boundary j to the outside air, m2K/W, [J, 1]
        # r_total_js = np.array([bs.rf.r_total for bs in bss]).reshape(-1, 1)
        r_total_js = np.array([bs.bcomp.r_total for bs in bss]).reshape(-1, 1)

        # thermal transmittance coefficient of boundary j, W/m2K, [J, 1]
        u_js = 1.0 / (1.0 / (h_s_c_js + h_s_r_js) + r_total_js)

        # response factor of boundary j, [J, 1] or [J, M]
        bcomps = BoundaryComponents.create(bcomplist=[bs.bcomp for bs in bss])
        phi_a0_js = bcomps.phi_a0_js
        phi_t0_js = bcomps.phi_t0_js

        bcomps_ground = BoundaryComponents.create(bcomplist=[bs.bcomp for bs in bss if bs.t_b == EBoundaryType.GROUND])

        # outside equivalent temperature of boundary j, degree C, [J, N+1]
        theta_o_eqv_js_nspls = np.array([bs.theta_o_eqv_nspls for bs in bss])

        # transmitted solar radiation of boundary j, W, [J, N+1]
        q_trs_sol_js_nspls = np.array([bs.q_trs_sol_nplus for bs in bss])

        # shape factor for microsphier in the room, [I, J]
        f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_s_js=a_s_js, h_s_r_js=h_s_r_js, p_is_js=p_is_js)

        f_ax_js_js = _get_f_ax_js_is(
            f_mrt_is_js=f_mrt_is_js,
            h_s_c_js=h_s_c_js,
            h_s_r_js=h_s_r_js,
            k_ei_js_js=k_ei_js_js,
            p_js_is=p_js_is,
            phi_a0_js=phi_a0_js,
            phi_t0_js=phi_t0_js
        )

        f_fia_js_is = _get_f_fia_js_is(
            h_s_c_js=h_s_c_js,
            h_s_r_js=h_s_r_js,
            k_ei_js_js=k_ei_js_js,
            p_js_is=p_js_is,
            phi_a0_js=phi_a0_js,
            phi_t0_js=phi_t0_js,
            k_s_r_js_is=k_s_r_js_is
        )

        f_wsr_js_is = _get_f_wsr_js_is(f_ax_js_js=f_ax_js_js, f_fia_js_is=f_fia_js_is)


        return Boundaries(
            n_b=n_b,
            connected_room_id_js=connected_room_id_js,
            p_is_js=p_is_js,
            p_js_is=p_js_is,
            a_s_js=a_s_js,
            eps_r_i_js=eps_r_i_js,
            h_s_r_js=h_s_r_js,
            h_s_c_js=h_s_c_js,
            n_ground=n_ground,
            id_js=id_js,
            name_js=name_js,
            sub_name_js=sub_name_js,
            b_floor_js=b_floor_js,
            b_ground_js=b_ground_js,
            k_ei_js_js=k_ei_js_js,
            k_eo_js=k_eo_js,
            k_s_r_js_is=k_s_r_js_is,
            b_s_sol_abs_js=b_sol_abs_js,
            u_js=u_js,
            phi_a0_js=phi_a0_js,
            phi_t0_js=phi_t0_js,
            theta_o_eqv_js_nspls=theta_o_eqv_js_nspls,
            q_trs_sol_js_nspls=q_trs_sol_js_nspls,
            f_mrt_is_js=f_mrt_is_js,
            f_ax_js_js=f_ax_js_js,
            f_wsr_js_is=f_wsr_js_is,
            bcomps=bcomps,
            bcomps_ground=bcomps_ground
        )

    def get_f_crx_js_ns(self, q_s_sol_js_ns: np.ndarray) -> np.ndarray:
        """

        Args:
            q_s_sol_js_ns: ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]

        Returns:
            係数 f_CRX, degree C, [j, n]

        Notes:
            式(4.3)
        """

        return _get_f_crx_js_ns(
            h_s_c_js=self.h_s_c_js,
            h_s_r_js=self.h_s_r_js,
            k_ei_js_js=self.k_ei_js_js,
            phi_a0_js=self.phi_a0_js,
            phi_t0_js=self.phi_t0_js,
            q_s_sol_js_ns=q_s_sol_js_ns,
            k_eo_js=self.k_eo_js,
            theta_o_eqv_js_ns=self.theta_o_eqv_js_nspls
        )

    def get_f_flb_js_is(self, beta_is: np.ndarray, f_flr_js_is: np.ndarray) -> np.ndarray:
        """

        Args:
            beta_is: 室 i の放射暖冷房設備の対流成分比率, -, [I, 1]
            f_flr_js_is: 室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [J, i]

        Returns:
            係数 f_FLB, K/W, [J, I]

        Notes:
            式(2.12)

        """

        return _get_f_flb_js_is(
            a_s_js=self.a_s_js,
            beta_is=beta_is,
            f_flr_js_is=f_flr_js_is,
            h_s_c_js=self.h_s_c_js,
            h_s_r_js=self.h_s_r_js,
            k_ei_js_js=self.k_ei_js_js,
            phi_a0_js=self.phi_a0_js,
            phi_t0_js=self.phi_t0_js
        )

    def get_f_cvl_js_n_pls(
            self,
            bcs_js_n: BoundaryComponentsStatus,
            theta_rear_js_n: np.ndarray,
            q_s_js_n: np.ndarray
        ) -> tuple[np.ndarray, BoundaryComponentsStatus]:
        """

        Args:
            bcs_js_n: boundary components status at step n
            theta_rear_js_n: ステップ n における境界 j の裏面温度, degree C, [j, 1]
            q_s_js_n: ステップ n における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]

        Returns:
            ステップ n+1 における係数 f_CVL, degree C, [j, 1]
        Notes:
            式(2.28)
        """

        bcs_js_n_pls = self.bcomps._get_next_boundary_components_status(
            bcs_js_n=bcs_js_n,
            theta_rear_js_n=theta_rear_js_n,
            q_s_js_n=q_s_js_n
        )

        f_cvl_js_n_pls = self.bcomps._get_f_cvl_js_n_pls(bcs_js_n_pls=bcs_js_n_pls)
        
        return f_cvl_js_n_pls, bcs_js_n_pls

    def get_f_wsc_js_ns(self, f_ax_js_js, q_s_sol_js_ns):
        """

        Args:
            f_ax_js_js: 係数 f_{AX}, -, [j, j]
            q_s_sol_js_ns: the transparent solar radiation absorbed by the boundary j at step n, W/m2, [J, N]

        Returns:
            係数 f_{WSC,n}, degree C, [j, n]

        Notes:
            式(4.1)
        """

        f_crx_js_ns = self.get_f_crx_js_ns(q_s_sol_js_ns=q_s_sol_js_ns)

        return np.linalg.solve(f_ax_js_js, f_crx_js_ns)

    def get_f_wsb_js_is(self, beta_is, f_flr_js_is):
        """

        Args:
            beta_is: 室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
            f_flr_js_is: 室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]

        Returns:
            係数 f_WSB, K/W, [j, i]

        Notes:
            式(2.11)

        """

        f_flb_js_is = self.get_f_flb_js_is(beta_is= beta_is, f_flr_js_is=f_flr_js_is)

        return np.linalg.solve(self.f_ax_js_js, f_flb_js_is)


def _get_p_is_js(id_r_is:np.ndarray, connected_room_id_js: np.ndarray):
    """

    Args:
        id_r_is: room id, [I, 1]
        connected_room_id_js: connected room id, [J, 1]

    Returns:
        matrix of relationship between rooms and boundaries, [I, J]

    Notes:
        Matrix is:
            [[p_0_0 ... ... p_0_j]
             [ ...  ... ...  ... ]
             [p_i_0 ... ... p_i_j]]
    """

    connected_room_id_js = connected_room_id_js.flatten()

    p_js_is = [
        _get_p_is_j(id_r_is=id_r_is, connected_room_id_j=connected_room_id_j)
        for connected_room_id_j in connected_room_id_js
    ]

    p_is_js = np.array(p_js_is).T
    
    return p_is_js


def _get_p_is_j(id_r_is: np.ndarray, connected_room_id_j: int):

    try:
        p_is_j = np.zeros(id_r_is.size, dtype=int)
        p_is_j[_get_room_index(id_r_is=id_r_is, id=connected_room_id_j)] = 1
        return p_is_j
    except Exception as e:
        raise ValueError("id_r_is = " + str(id_r_is) + ", connected_room_id_j = " + str(connected_room_id_j))


def _get_room_index(id_r_is: np.ndarray, id: int):
    """Get the index of rooms matched to the specify id.

    Args:
        id_r_is: list of the indices of rooms
        id: specified room id

    Raises:
        ValueError: There is no room index corresponding to the specified index.
        ValueError: Multiple indices were found corresponding to the specified index.

    Returns:
        the index of the room
    """

    matched_indices = [index for (index, id_r_i) in enumerate(id_r_is) if id_r_i == id]

    if len(matched_indices) == 0:
        raise ValueError("Boundary が接続する room のIDが存在しませんでした。(id=" + str(id) + ")")
    if len(matched_indices) > 1:
        raise ValueError("Boundary が接続する room のIDが複数存在しました。(id=" + str(id) + ")")
    
    return matched_indices[0]


def _get_f_ax_js_is(f_mrt_is_js, h_s_c_js, h_s_r_js, k_ei_js_js, p_js_is, phi_a0_js, phi_t0_js):
    """

    Args:
        f_mrt_is_js: 室 i の微小球に対する境界 j の形態係数, -, [i, j]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j∗ の等価温度が与える影響, -, [j, j]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j, 1]
        phi_t0_js: 境界 j の貫流応答係数の初項, -, [j, 1]

    Returns:
        係数 f_AX, -, [J, J]

    Notes:
        式(4.5)
    """

    return v_diag(1.0 + phi_a0_js * (h_s_c_js + h_s_r_js)) \
        - np.dot(p_js_is, f_mrt_is_js) * h_s_r_js * phi_a0_js \
        - np.dot(k_ei_js_js, np.dot(p_js_is, f_mrt_is_js) * h_s_r_js / (h_s_c_js + h_s_r_js)) * phi_t0_js


def _get_f_fia_js_is(h_s_c_js, h_s_r_js, k_ei_js_js, p_js_is, phi_a0_js, phi_t0_js, k_s_r_js_is):
    """

    Args:
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j∗ の等価温度が与える影響, -, [j, j]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j, 1]
        phi_t0_js: 境界 j の貫流応答係数の初項, -, [j, 1]

    Returns:
        係数 f_FIA, -, [j, i]

    Notes:
        式(4.4)
    """

    return phi_a0_js * h_s_c_js * p_js_is + np.dot(k_ei_js_js, p_js_is * h_s_c_js / (h_s_c_js + h_s_r_js)) * phi_t0_js + phi_t0_js * k_s_r_js_is


def _get_f_crx_js_ns(h_s_c_js, h_s_r_js, k_ei_js_js, phi_a0_js, phi_t0_js, q_s_sol_js_ns, k_eo_js, theta_o_eqv_js_ns):
    """

    Args:
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j∗ の等価温度が与える影響, -, [j, j]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j, 1]
        phi_t0_js: 境界 j の貫流応答係数の初項, -, [j, 1]
        q_s_sol_js_ns: ステップ n における境界 j の透過日射吸収熱量, W/m2, [j, n]
        k_eo_js: 境界 j の裏面温度に境界 j の相当外気温度が与える影響, -, [j, 1]
        theta_o_eqv_js_ns: ステップ n における境界 j の相当外気温度, degree C, [j, 1]

    Returns:
        係数 f_CRX, degree C, [j, n]

    Notes:
        式(4.3)
    """

    return phi_a0_js * q_s_sol_js_ns\
        + phi_t0_js * np.dot(k_ei_js_js, q_s_sol_js_ns / (h_s_c_js + h_s_r_js))\
        + phi_t0_js * theta_o_eqv_js_ns * k_eo_js


def _get_f_flb_js_is(a_s_js, beta_is, f_flr_js_is, h_s_c_js, h_s_r_js, k_ei_js_js, phi_a0_js, phi_t0_js):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        beta_is: 室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
        f_flr_js_is: 室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        k_ei_js_js: 境界 j の裏面温度に境界　j* の等価温度が与える影響, -, [j*, j]
        phi_a0_js: 境界 j の吸熱応答係数の初項, m2 K/W, [j]
        phi_t0_js: 境界 |j| の貫流応答係数の初項, -, [j]

    Returns:
        係数 f_FLB, K/W, [j, i]

    Notes:
        式(2.12)

    """

    return f_flr_js_is * (1.0 - beta_is.T) * phi_a0_js / a_s_js \
        + np.dot(k_ei_js_js, f_flr_js_is * (1.0 - beta_is.T)) * phi_t0_js / (h_s_c_js + h_s_r_js) / a_s_js


def _get_f_wsr_js_is(f_ax_js_js, f_fia_js_is):
    """

    Args:
        f_ax_js_js: 係数 f_AX, -, [j, j]
        f_fia_js_is: 係数 f_FIA, -, [j, i]

    Returns:
        係数 f_WSR, -, [j, i]

    Notes:
        式(4.2)
    """

    return np.linalg.solve(f_ax_js_js, f_fia_js_is)

