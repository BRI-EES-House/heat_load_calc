import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Tuple
import logging

from heat_load_calc.matrix_method import v_diag
from heat_load_calc import next_condition, schedule, rooms, boundaries
from heat_load_calc import occupants_form_factor, shape_factor, solar_absorption
from heat_load_calc import operation_mode, interval
from heat_load_calc import occupants, psychrometrics as psy
from heat_load_calc.global_number import get_c_a, get_rho_a, get_l_wtr
from heat_load_calc.weather import Weather
from heat_load_calc.schedule import Schedule
from heat_load_calc.building import Building
from heat_load_calc.rooms import Rooms
from heat_load_calc.boundaries import Boundaries
from heat_load_calc.mechanical_ventilations import MechanicalVentilations
from heat_load_calc.equipments import Equipments
from heat_load_calc.conditions import Conditions
from heat_load_calc.recorder import Recorder
from heat_load_calc.conditions import GroundConditions
from heat_load_calc.operation_mode import Operation, OperationMode
from heat_load_calc.shape_factor import ShapeFactorMethod
from heat_load_calc import season


# ロガー
logger = logging.getLogger('HeatLoadCalc').getChild('core').getChild('pre_calc_parameters')


class Sequence:

    def __init__(self, itv: interval.Interval, d: Dict, weather: Weather, scd: schedule.Schedule):
        """
        Args:
            itv: interval class
            d: directory of input file
            weather: weather class
            scd: schedule class
        """

        # 時間間隔, s
        delta_t = itv.get_delta_t()

        # Building Class
        building = Building.create_building(d=d['building'])

        # Rooms Class
        rms = rooms.Rooms(ds=d['rooms'])

        # Boundaries Class
        if 'mutual_radiation_method' in d['common']:
            rad_method = ShapeFactorMethod(str(d['common']['mutual_radiation_method']))
        else:
            rad_method = ShapeFactorMethod.NAGATA
        
        bs = boundaries.Boundaries(id_r_is=rms.id_r_is, ds=d['boundaries'], w=weather, rad_method=rad_method)

        # MechanicalVentilation Class
        mvs = MechanicalVentilations(ds=d['mechanical_ventilations'], n_rm=rms.n_r)

        # Equipments Class
        es = Equipments(d=d['equipments'], id_r_is=rms.id_r_is, id_b_js=bs.id_js, connected_room_id_js=bs.connected_room_id_js, p_is_js=bs.p_is_js)

        # Operation Class
        op = operation_mode.Operation(
            d_common=d['common'],
            t_ac_mode_is_ns=scd.t_ac_mode_is_ns,
            r_ac_demand_is_ns=scd.r_ac_demand_is_ns,
            n_rm=rms.n_r
        )

        # ステップ n の室 i における窓の透過日射熱取得, W, [n]
        q_trs_sol_is_ns = np.dot(bs.p_is_js, bs.q_trs_sol_js_nspls)

        # the shape factor of boundaries j for the occupant in room i, [i, j]
        f_mrt_hum_is_js = occupants_form_factor.get_f_mrt_hum_js(
            p_is_js=bs.p_is_js,
            a_s_js=bs.a_s_js,
            eps_r_i_js=bs.eps_r_i_js,
            is_floor_js=bs.b_floor_js
        )

        # the shape factor of boundaries j for the microsphier in the room i, [i, j]
        f_mrt_is_js = shape_factor.get_f_mrt_is_js(a_s_js=bs.a_s_js, h_s_r_js=bs.h_s_r_js, p_is_js=bs.p_is_js)

        # the mechanical ventilation amount(the sum of the general ventilation amount and local ventilation amount) of room i from step n to step n+1, m3/s, [i, 1]
        v_vent_mec_is_ns = get_v_vent_mec_is_ns(
            v_vent_mec_general_is=mvs.v_vent_mec_general_is,
            v_vent_mec_local_is_ns=scd.v_mec_vent_local_is_ns
        )

        # the average value of the transparented solar radiation absorbed by the furniture in room i at step n
        q_sol_frt_is_ns = solar_absorption.get_q_sol_frt_is_ns(q_trs_sor_is_ns=q_trs_sol_is_ns, r_sol_frt_is=rms.r_sol_frt_is)

        # the transparent solar radiation absorbed by the boundary j at step n, W/m2, [J, N]
        q_s_sol_js_ns = solar_absorption.get_q_s_sol_js_ns(
            p_is_js=bs.p_is_js,
            a_s_js=bs.a_s_js,
            p_s_sol_abs_js=bs.b_s_sol_abs_js,
            p_js_is=bs.p_js_is,
            q_trs_sol_is_ns=q_trs_sol_is_ns,
            r_sol_frt_is=rms.r_sol_frt_is
        )

        # f_AX, -, [j, j]
        f_ax_js_js = bs.get_f_ax_js_is(f_mrt_is_js=f_mrt_is_js)

        # f_FIA, -, [J, I]
        f_fia_js_is = bs.get_f_fia_js_is()

        # f_CRX, degree C, [J, N]
        f_crx_js_ns = bs.get_f_crx_js_ns(q_s_sol_js_ns=q_s_sol_js_ns)

        # f_WSR, -, [J, I]
        f_wsr_js_is = get_f_wsr_js_is(f_ax_js_js=f_ax_js_js, f_fia_js_is=f_fia_js_is)

        # f_{WSC, n}, degree C, [J, N]
        f_wsc_js_ns = get_f_wsc_js_ns(f_ax_js_js=f_ax_js_js, f_crx_js_ns=f_crx_js_ns)

        # ステップnにおける室iの在室者表面における対流熱伝達率の総合熱伝達率に対する比, -, [i, 1]
        # ステップ n における室 i の在室者表面における放射熱伝達率の総合熱伝達率に対する比, -, [i, 1]
        k_c_is_n, k_r_is_n = op.get_k_is()

        # ステップn+1における室iの係数 XOT, [i, i]
        f_xot_is_is_n_pls = get_f_xot_is_is_n_pls(
            f_mrt_hum_is_js=f_mrt_hum_is_js,
            f_wsr_js_is= f_wsr_js_is,
            k_c_is_n=k_c_is_n,
            k_r_is_n=k_r_is_n
        )

        # 時間間隔クラス
        self._itv = itv

        # 時間間隔, s
        self._delta_t = delta_t

        # ロガー
        self._logger = logger

        # Weather Class
        self._weather: Weather = weather

        # Schedule Class
        self._scd: Schedule = scd

        # Building Class
        self._building: Building = building

        # Rooms Class
        self._rms: Rooms = rms

        # Boundaries Class
        self._bs: Boundaries = bs

        # MechanicalVentilation Class
        self._mvs: MechanicalVentilations = mvs

        # Equipments Class
        self._es: Equipments = es

        # Operation Class
        self._op: Operation = op

        # 次の係数を求める関数
        #   ステップ n　からステップ n+1 における係数 f_l_cl_wgt, kg/s(kg/kg(DA)), [i, i]
        #   ステップ n　からステップ n+1 における係数 f_l_cl_cst, kg/s, [i, 1]
        self._get_f_l_cl = es.get_f_l_cl

        # the solar heat gain transmitted through the windows of room i at step n, W, [I, N]
        self._q_trs_sol_is_ns = q_trs_sol_is_ns

        # mechanical ventilation amount(general ventiration amount + local ventiration amount) of room i at step n, m3/s, [I,N]
        self._v_vent_mec_is_ns = v_vent_mec_is_ns

        # the average value of the transparented solar radiation absorbed by the furniture in room i at step n
        self._q_sol_frt_is_ns = q_sol_frt_is_ns

        # the transparent solar radiation absorbed by the boundary j at step n, W/m2, [J, N]
        self._q_s_sol_js_ns = q_s_sol_js_ns

        # f_AX, -, [j, j]
        self._f_ax_js_js = f_ax_js_js

        # the shape factor of boundaries j for the occupant in room i, [i, j]
        self._f_mrt_hum_is_js = f_mrt_hum_is_js

        # the shape factor of boundaries j for the microsphier in the room i, [i, j]
        self._f_mrt_is_js = f_mrt_is_js

        # f_WSR, -, [J, I]
        self._f_wsr_js_is = f_wsr_js_is

        # f_{WSC, n}, degree C, [J, N]
        self._f_wsc_js_ns = f_wsc_js_ns

        # the ratio of the radiative heat transfer coefficient to the integrated heat transfer coefficient on the surface of the occuapnts in room i at step n, -, [I, 1]
        self._k_r_is_n = k_r_is_n

        # the ratio of the convective heat transfer coefficient to the integrated heat transfer coefficient on the surface of the occuapnts in room i at step n, -, [I, 1]
        self._k_c_is_n = k_c_is_n

        # f_{XOT, i, i}, [I, I]
        self._f_xot_is_is_n_pls = f_xot_is_is_n_pls

    @property
    def weather(self) -> Weather:
        """Weather Class"""
        return self._weather

    @property
    def scd(self) -> Schedule:
        """Schedule Class"""
        return self._scd

    @property
    def building(self) -> Building:
        """Building Class"""
        return self._building

    @property
    def rms(self) -> Rooms:
        """Rooms Class"""
        return self._rms

    @property
    def bs(self) -> Boundaries:
        """Boundaries Class"""
        return self._bs

    @property
    def mvs(self) -> MechanicalVentilations:
        """MechanicalVentilations Class"""
        return self._mvs

    @property
    def es(self) -> Equipments:
        return self._es

    @property
    def get_f_l_cl(self) -> Callable[[np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
        """次の係数を求める関数

        ステップ n　からステップ n+1 における係数 f_l_cl_wgt, kg/s(kg/kg(DA)), [i, i]
        ステップ n　からステップ n+1 における係数 f_l_cl_cst, kg/s, [i, 1]

        Returns:

        """
        return self._get_f_l_cl
    
    @property
    def q_trs_sol_is_ns(self):
        """the solar heat gain transmitted through the windows of room i at step n
        Notes:
            this property is only used for pre-recording
        """
        return self._q_trs_sol_is_ns

    @property
    def v_vent_mec_is_ns(self):
        """mechanical ventiration amount, m3/s, [I,N]"""
        return self._v_vent_mec_is_ns

    @property
    def q_sol_frt_is_ns(self):
        """the average value of the transparented solar radiation absorbed by the furniture in room i at step n"""
        return self._q_sol_frt_is_ns
    
    @property
    def q_s_sol_js_ns(self):
        """the transparent solar radiation absorbed by the boundary j at step n, W/m2, [J, N]"""
        return self._q_s_sol_js_ns
    
    @property
    def f_ax_js_js(self):
        """f_AX, -, [j, j]"""
        return self._f_ax_js_js
    
    @property
    def f_mrt_hum_is_js(self):
        """the shape factor of boundaries j for the occupant in room i, [i, j]"""
        return self._f_mrt_hum_is_js

    @property
    def f_mrt_is_js(self):
        """the shape factor of boundaries j for the microsphier in the room i, [i, j]"""
        return self._f_mrt_is_js
    
    @property
    def f_wsr_js_is(self):
        """f_WSR, -, [J, I]"""
        return self._f_wsr_js_is
    
    @property
    def f_wsc_js_ns(self):
        """f_{WSC, n}, degree C, [J, N]"""
        return self._f_wsc_js_ns

    @property
    def k_r_is_n(self):
        """the ratio of the radiative heat transfer coefficient to the integrated heat transfer coefficient on the surface of the occuapnts in room i at step n, -, [I, 1]"""
        return self._k_r_is_n
    
    @property
    def k_c_is_n(self):
        """the ratio of the convective heat transfer coefficient to the integrated heat transfer coefficient on the surface of the occuapnts in room i at step n, -, [I, 1]"""
        return self._k_c_is_n
    
    @property
    def f_xot_is_is_n_pls(self):
        """f_{XOT, i, i}, [I, I]"""
        return self._f_xot_is_is_n_pls
    

    def run_tick(self, n: int, c_n: Conditions, recorder: Recorder, exe_verify: bool = False) -> Conditions:

        delta_t = self._delta_t

        # region 人体発熱・人体発湿

        # ステップnからステップn+1における室iの1人あたりの人体発熱, W, [i, 1]
        q_hum_psn_is_n = occupants.get_q_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

        # ステップ n からステップ n+1 における室 i の人体発熱, W, [i, 1]
        q_hum_is_n = get_q_hum_is_n(n_hum_is_n=self.scd.n_hum_is_ns[:, n].reshape(-1, 1), q_hum_psn_is_n=q_hum_psn_is_n)

        # ステップnの室iにおける1人あたりの人体発湿, kg/s, [i, 1]
        x_hum_psn_is_n = occupants.get_x_hum_psn_is_n(theta_r_is_n=c_n.theta_r_is_n)

        # ステップnの室iにおける人体発湿, kg/s, [i, 1]
        x_hum_is_n = get_x_hum_is_n(n_hum_is_n=self.scd.n_hum_is_ns[:, n].reshape(-1, 1), x_hum_psn_is_n=x_hum_psn_is_n)

        # endregion

        # ステップ n の境界 j における裏面温度, degree C, [j, 1]
        theta_rear_js_n = get_theta_s_rear_js_n(
            k_s_er_js_js=self.bs.k_ei_js_js,
            theta_er_js_n=c_n.theta_ei_js_n,
            k_s_eo_js=self.bs.k_eo_js,
            theta_eo_js_n=self.bs.theta_o_eqv_js_nspls[:, n].reshape(-1, 1),
            k_s_r_js_is=self.bs.k_s_r_js_is,
            theta_r_is_n=c_n.theta_r_is_n
        )

        # ステップnの室iにおけるすきま風量, m3/s, [i, 1]
        v_leak_is_n = self.building.get_v_leak_is_n(
            theta_r_is_n=c_n.theta_r_is_n,
            theta_o_n=self.weather.theta_o_ns_plus[n],
            v_r_is=self.rms.v_r_is
        )

        # ステップ n+1 の境界 j における項別公比法の指数項 m の貫流応答の項別成分, degree C, [j, m] (m=12), eq.(29)
        # ステップ n+1 の境界 j における項別公比法の指数項 m の吸熱応答の項別成分, degree C, [j, m]
        # ステップ n+1 の境界 j における係数f_CVL, degree C, [j, 1]
        theta_dsh_s_t_js_ms_n_pls, theta_dsh_s_a_js_ms_n_pls, f_cvl_js_n_pls = self.bs.get_f_cvl_js_n_pls(
            theta_dsh_srf_t_js_ms_n=c_n.theta_dsh_srf_t_js_ms_n,
            theta_dsh_srf_a_js_ms_n=c_n.theta_dsh_srf_a_js_ms_n,
            theta_rear_js_n=theta_rear_js_n,
            q_s_js_n=c_n.q_s_js_n
        )

        # ステップ n+1 の境界 j における係数 f_WSV, degree C, [j, 1]
        f_wsv_js_n_pls = get_f_wsv_js_n_pls(
            f_cvl_js_n_pls=f_cvl_js_n_pls,
            f_ax_js_js=self.f_ax_js_js
        )

        # ステップnからステップn+1における室iの換気・隙間風による外気の流入量, m3/s, [i, 1]
        v_vent_out_non_nv_is_n = get_v_vent_out_non_ntr_is_n(
            v_leak_is_n=v_leak_is_n,
            v_vent_mec_is_n=self.v_vent_mec_is_ns[:, n].reshape(-1, 1)
        )

        # ステップ n+1 の室 i における係数 f_BRC, W, [i, 1]
        # TODO: q_sol_frt_is_ns の値は n+1 の値を使用するべき？
        f_brc_non_nv_is_n_pls, f_brc_nv_is_n_pls = get_f_brc_is_n_pls(
            a_s_js=self.bs.a_s_js,
            c_a=get_c_a(),
            v_rm_is=self.rms.v_r_is,
            c_sh_frt_is=self.rms.c_sh_frt_is,
            delta_t=delta_t,
            f_wsc_js_n_pls=self.f_wsc_js_ns[:, n + 1].reshape(-1, 1),
            f_wsv_js_n_pls=f_wsv_js_n_pls,
            g_sh_frt_is=self.rms.g_sh_frt_is,
            h_s_c_js=self.bs.h_s_c_js,
            p_is_js=self.bs.p_is_js,
            q_gen_is_n=self.scd.q_gen_is_ns[:, n].reshape(-1, 1),
            q_hum_is_n=q_hum_is_n,
            q_sol_frt_is_n=self.q_sol_frt_is_ns[:, n].reshape(-1, 1),
            rho_a=get_rho_a(),
            theta_frt_is_n=c_n.theta_frt_is_n,
            theta_o_n_pls=self.weather.theta_o_ns_plus[n + 1],
            theta_r_is_n=c_n.theta_r_is_n,
            v_vent_out_non_nv_is_n=v_vent_out_non_nv_is_n,
            v_vent_ntr_is_n=self.rms.v_vent_ntr_set_is
        )

        # ステップ n+1 における係数 f_BRM, W/K, [i, i]
        f_brm_non_nv_is_is_n_pls, f_brm_nv_is_is_n_pls = get_f_brm_is_is_n_pls(
            a_s_js=self.bs.a_s_js,
            c_a=get_c_a(),
            v_rm_is=self.rms.v_r_is,
            c_sh_frt_is=self.rms.c_sh_frt_is,
            delta_t=delta_t,
            f_wsr_js_is=self.f_wsr_js_is,
            g_sh_frt_is=self.rms.g_sh_frt_is,
            h_s_c_js=self.bs.h_s_c_js,
            p_is_js=self.bs.p_is_js,
            p_js_is=self.bs.p_js_is,
            rho_a=get_rho_a(),
            v_vent_int_is_is_n=self.mvs.v_vent_int_is_is,
            v_vent_out_non_nv_is_n=v_vent_out_non_nv_is_n,
            v_vent_ntr_set_is=self.rms.v_vent_ntr_set_is
        )

        # ステップn+1における室iの係数 XC, [i, 1]
        f_xc_is_n_pls = get_f_xc_is_n_pls(
            f_mrt_hum_is_js=self.f_mrt_hum_is_js,
            f_wsc_js_n_pls=self.f_wsc_js_ns[:, n + 1].reshape(-1, 1),
            f_wsv_js_n_pls=f_wsv_js_n_pls,
            f_xot_is_is_n_pls=self.f_xot_is_is_n_pls,
            k_r_is_n=self.k_r_is_n
        )

        # ステップ n における係数 f_BRM,OT, W/K, [i, i]
        f_brm_ot_non_nv_is_is_n_pls, f_brm_ot_nv_is_is_n_pls = get_f_brm_ot_is_is_n_pls(
            f_xot_is_is_n_pls=self.f_xot_is_is_n_pls,
            f_brm_non_nv_is_is_n_pls=f_brm_non_nv_is_is_n_pls,
            f_brm_nv_is_is_n_pls=f_brm_nv_is_is_n_pls
        )

        # ステップ n における係数 f_BRC,OT, W, [i, 1]
        f_brc_ot_non_nv_is_n_pls, f_brc_ot_nv_is_n_pls = get_f_brc_ot_is_n_pls(
            f_xc_is_n_pls=f_xc_is_n_pls,
            f_brc_non_nv_is_n_pls=f_brc_non_nv_is_n_pls,
            f_brc_nv_is_n_pls=f_brc_nv_is_n_pls,
            f_brm_non_nv_is_is_n_pls=f_brm_non_nv_is_is_n_pls,
            f_brm_nv_is_is_n_pls=f_brm_nv_is_is_n_pls
        )

        # ステップnにおける室iの自然風の非利用時の潜熱バランスに関する係数f_h_cst, kg / s, [i, 1]
        # ステップnにおける室iの自然風の利用時の潜熱バランスに関する係数f_h_cst, kg / s, [i, 1]
        f_h_cst_non_nv_is_n, f_h_cst_nv_is_n = get_f_h_cst_is_n(
            c_lh_frt_is=self.rms.c_lh_frt_is,
            delta_t=delta_t,
            g_lh_frt_is=self.rms.g_lh_frt_is,
            rho_a=get_rho_a(),
            v_rm_is=self.rms.v_r_is,
            x_frt_is_n=c_n.x_frt_is_n,
            x_gen_is_n=self.scd.x_gen_is_ns[:, n].reshape(-1, 1),
            x_hum_is_n=x_hum_is_n,
            x_o_n_pls=self.weather.x_o_ns_plus[n + 1],
            x_r_is_n=c_n.x_r_is_n,
            v_vent_out_non_nv_is_n=v_vent_out_non_nv_is_n,
            v_vent_ntr_is= self.rms.v_vent_ntr_set_is
        )

        # ステップnにおける自然風非利用時の室i*の絶対湿度が室iの潜熱バランスに与える影響を表す係数,　kg/(s kg/kg(DA)), [i, i]
        # ステップnにおける自然風利用時の室i*の絶対湿度が室iの潜熱バランスに与える影響を表す係数,　kg/(s kg/kg(DA)), [i, i]
        f_h_wgt_non_nv_is_is_n, f_h_wgt_nv_is_is_n = get_f_h_wgt_is_is_n(
            c_lh_frt_is=self.rms.c_lh_frt_is,
            delta_t=delta_t,
            g_lh_frt_is=self.rms.g_lh_frt_is,
            rho_a=get_rho_a(),
            v_rm_is=self.rms.v_r_is,
            v_vent_int_is_is_n=self.mvs.v_vent_int_is_is,
            v_vent_out_non_nv_is_n=v_vent_out_non_nv_is_n,
            v_vent_ntr_is=self.rms.v_vent_ntr_set_is
        )

        # ステップn+1における自然風非利用時の自然作用温度, degree C, [i, 1]
        # ステップn+1における自然風利用時の自然作用温度, degree C, [i, 1]
        theta_r_ot_ntr_non_nv_is_n_pls, theta_r_ot_ntr_nv_is_n_pls = get_theta_r_ot_ntr_is_n_pls(
            f_brc_ot_non_nv_is_n_pls=f_brc_ot_non_nv_is_n_pls,
            f_brc_ot_nv_is_n_pls=f_brc_ot_nv_is_n_pls,
            f_brm_ot_non_nv_is_is_n_pls=f_brm_ot_non_nv_is_is_n_pls,
            f_brm_ot_nv_is_is_n_pls=f_brm_ot_nv_is_is_n_pls
        )

        theta_r_ntr_non_nv_is_n_pls = np.dot(self.f_xot_is_is_n_pls, theta_r_ot_ntr_non_nv_is_n_pls) - f_xc_is_n_pls
        theta_r_ntr_nv_is_n_pls = np.dot(self.f_xot_is_is_n_pls, theta_r_ot_ntr_nv_is_n_pls) - f_xc_is_n_pls

        theta_s_ntr_non_nv_js_n_pls = np.dot(self.f_wsr_js_is, theta_r_ntr_non_nv_is_n_pls) + self.f_wsc_js_ns[:, n + 1].reshape(-1, 1) + f_wsv_js_n_pls
        theta_s_ntr_nv_js_n_pls = np.dot(self.f_wsr_js_is, theta_r_ntr_nv_is_n_pls) + self.f_wsc_js_ns[:, n + 1].reshape(-1, 1) + f_wsv_js_n_pls

        theta_mrt_hum_ntr_non_nv_is_n_pls = np.dot(self.f_mrt_is_js, theta_s_ntr_non_nv_js_n_pls)
        theta_mrt_hum_ntr_nv_is_n_pls = np.dot(self.f_mrt_is_js, theta_s_ntr_nv_js_n_pls)

        # ステップn+1における室iの自然風非利用時の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA) [i, 1]
        # ステップn+1における室iの自然風利用時の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA) [i, 1]
        x_r_ntr_non_nv_is_n_pls, x_r_ntr_nv_is_n_pls = get_x_r_ntr_is_n_pls(
            f_h_cst_non_nv_is_n=f_h_cst_non_nv_is_n,
            f_h_wgt_non_nv_is_is_n=f_h_wgt_non_nv_is_is_n,
            f_h_cst_nv_is_n=f_h_cst_nv_is_n,
            f_h_wgt_nv_is_is_n=f_h_wgt_nv_is_is_n
        )

        # ステップ n における室 i の運転モード, [i, 1]
        operation_mode_is_n = self._op.get_t_operation_mode_is_n(
            n=n,
            is_radiative_heating_is=self.es.is_radiative_heating_is,
            is_radiative_cooling_is=self.es.is_radiative_cooling_is,
            met_is=self.rms.met_is,
            theta_r_ot_ntr_non_nv_is_n_pls=theta_r_ot_ntr_non_nv_is_n_pls,
            theta_r_ot_ntr_nv_is_n_pls=theta_r_ot_ntr_nv_is_n_pls,
            theta_r_ntr_non_nv_is_n_pls=theta_r_ntr_non_nv_is_n_pls,
            theta_r_ntr_nv_is_n_pls=theta_r_ntr_nv_is_n_pls,
            theta_mrt_hum_ntr_non_nv_is_n_pls=theta_mrt_hum_ntr_non_nv_is_n_pls,
            theta_mrt_hum_ntr_nv_is_n_pls=theta_mrt_hum_ntr_nv_is_n_pls,
            x_r_ntr_non_nv_is_n_pls=x_r_ntr_non_nv_is_n_pls,
            x_r_ntr_nv_is_n_pls=x_r_ntr_nv_is_n_pls
        )

        f_brm_is_is_n_pls = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            f_brm_nv_is_is_n_pls,
            f_brm_non_nv_is_is_n_pls
        )

        v_vent_ntr_is_n = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            self.rms.v_vent_ntr_set_is,
            0.0
        )

        f_brm_ot_is_is_n_pls = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            f_brm_ot_nv_is_is_n_pls,
            f_brm_ot_non_nv_is_is_n_pls
        )

        f_brc_ot_is_n_pls = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            f_brc_ot_nv_is_n_pls,
            f_brc_ot_non_nv_is_n_pls
        )

        f_h_cst_is_n = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            f_h_cst_nv_is_n,
            f_h_cst_non_nv_is_n
        )

        f_h_wgt_is_is_n = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            f_h_wgt_nv_is_is_n,
            f_h_wgt_non_nv_is_is_n
        )

        theta_r_ot_ntr_is_n_pls = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            theta_r_ot_ntr_nv_is_n_pls,
            theta_r_ot_ntr_non_nv_is_n_pls
        )

        theta_r_ntr_is_n_pls = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            theta_r_ntr_nv_is_n_pls,
            theta_r_ntr_non_nv_is_n_pls
        )

        theta_mrt_hum_ntr_is_n_pls = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            theta_mrt_hum_ntr_nv_is_n_pls,
            theta_mrt_hum_ntr_non_nv_is_n_pls
        )

        x_r_ntr_is_n_pls = np.where(
            operation_mode_is_n == OperationMode.STOP_OPEN,
            x_r_ntr_nv_is_n_pls,
            x_r_ntr_non_nv_is_n_pls
        )

        theta_lower_target_is_n_pls, theta_upper_target_is_n_pls, h_hum_c_is_n, h_hum_r_is_n \
            = self._op.get_theta_target_is_n(
                operation_mode_is_n=operation_mode_is_n,
                theta_r_ntr_is_n_pls=theta_r_ntr_is_n_pls,
                theta_mrt_hum_ntr_is_n_pls=theta_mrt_hum_ntr_is_n_pls,
                x_r_ntr_is_n_pls=x_r_ntr_is_n_pls,
                n=n,
                is_radiative_heating_is=self.es.is_radiative_heating_is,
                is_radiative_cooling_is=self.es.is_radiative_cooling_is,
                met_is=self.rms.met_is
            )

        # ステップ n+1 における係数 f_flr, -, [j, i]
        f_flr_js_is_n = get_f_flr_js_is_n(
            f_flr_c_js_is=self.es.f_flr_c_js_is,
            f_flr_h_js_is=self.es.f_flr_h_js_is,
            operation_mode_is_n=operation_mode_is_n
        )

        # ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
        beta_is_n = get_beta_is_n(
            beta_c_is=self.es.beta_c_is,
            beta_h_is=self.es.beta_h_is,
            operation_mode_is_n=operation_mode_is_n
        )

        # ステップ n における係数 f_FLB, K/W, [j, i]
        #f_flb_js_is_n_pls = get_f_flb_js_is_n_pls(
            #a_s_js=self.bs.a_s_js,
            #beta_is_n=beta_is_n,
            #f_flr_js_is_n=f_flr_js_is_n,
            #h_s_c_js=self.bs.h_s_c_js,
            #h_s_r_js=self.bs.h_s_r_js,
            #k_ei_js_js=self.bs.k_ei_js_js,
            #phi_a0_js=self.bs.phi_a0_js,
            #phi_t0_js=self.bs.phi_t0_js
        #)
        f_flb_js_is_n_pls = self.bs.get_f_flb_js_is_n_pls(beta_is_n=beta_is_n, f_flr_js_is_n=f_flr_js_is_n)

        # ステップ n における係数 f_WSB, K/W, [j, i]
        f_wsb_js_is_n_pls = get_f_wsb_js_is_n_pls(
            f_flb_js_is_n_pls=f_flb_js_is_n_pls,
            f_ax_js_js=self.f_ax_js_js
        )

        # ステップ n における係数 f_BRL, -, [i, i]
        f_brl_is_is_n = get_f_brl_is_is_n(
            a_s_js=self.bs.a_s_js,
            beta_is_n=beta_is_n,
            f_wsb_js_is_n_pls=f_wsb_js_is_n_pls,
            h_s_c_js=self.bs.h_s_c_js,
            p_is_js=self.bs.p_is_js
        )

        # ステップn+1における室iの係数 f_XLR, K/W, [i, i]
        f_xlr_is_is_n_pls = get_f_xlr_is_is_n_pls(
            f_mrt_hum_is_js=self.f_mrt_hum_is_js,
            f_wsb_js_is_n_pls=f_wsb_js_is_n_pls,
            f_xot_is_is_n_pls=self.f_xot_is_is_n_pls,
            k_r_is_n=self.k_r_is_n
        )

        # ステップ n における係数 f_BRL_OT, -, [i, i]
        f_brl_ot_is_is_n = get_f_brl_ot_is_is_n(
            f_brl_is_is_n=f_brl_is_is_n,
            f_brm_is_is_n_pls=f_brm_is_is_n_pls,
            f_xlr_is_is_n_pls=f_xlr_is_is_n_pls
        )

        # ステップ n+1 における室 i の作用温度, degree C, [i, 1] (ステップn+1における瞬時値）
        # ステップ n における室 i に設置された対流暖房の放熱量, W, [i, 1] (ステップn～ステップn+1までの平均値）
        # ステップ n における室 i に設置された放射暖房の放熱量, W, [i, 1]　(ステップn～ステップn+1までの平均値）
        theta_ot_is_n_pls, l_cs_is_n, l_rs_is_n = next_condition.get_next_temp_and_load(
            ac_demand_is_ns=self.scd.r_ac_demand_is_ns,
            brc_ot_is_n=f_brc_ot_is_n_pls,
            brm_ot_is_is_n=f_brm_ot_is_is_n_pls,
            brl_ot_is_is_n=f_brl_ot_is_is_n,
            theta_lower_target_is_n=theta_lower_target_is_n_pls,
            theta_upper_target_is_n=theta_upper_target_is_n_pls,
            operation_mode_is_n=operation_mode_is_n,
            is_radiative_heating_is=self.es.is_radiative_heating_is,
            is_radiative_cooling_is=self.es.is_radiative_cooling_is,
            lr_h_max_cap_is=self.es.q_rs_h_max_is,
            lr_cs_max_cap_is=self.es.q_rs_c_max_is,
            theta_natural_is_n=theta_r_ot_ntr_is_n_pls,
            n=n
        )

        # ステップ n+1 における室 i の室温, degree C, [i, 1]
        theta_r_is_n_pls = get_theta_r_is_n_pls(
            f_xc_is_n_pls=f_xc_is_n_pls,
            f_xlr_is_is_n_pls=f_xlr_is_is_n_pls,
            f_xot_is_is_n_pls=self.f_xot_is_is_n_pls,
            l_rs_is_n=l_rs_is_n,
            theta_ot_is_n_pls=theta_ot_is_n_pls
        )

        # ステップ n+1 における境界 j の表面温度, degree C, [j, 1]
        theta_s_js_n_pls = get_theta_s_js_n_pls(
            f_wsb_js_is_n_pls=f_wsb_js_is_n_pls,
            f_wsc_js_n_pls=self.f_wsc_js_ns[:, n + 1].reshape(-1, 1),
            f_wsr_js_is=self.f_wsr_js_is,
            f_wsv_js_n_pls=f_wsv_js_n_pls,
            l_rs_is_n=l_rs_is_n,
            theta_r_is_n_pls=theta_r_is_n_pls
        )

        # ステップ n+1 における室 i　の備品等の温度, degree C, [i, 1]
        # TODO: q_sol_frt_is_ns の値は n+1 の値を使用するべき？
        theta_frt_is_n_pls = get_theta_frt_is_n_pls(
            c_sh_frt_is=self.rms.c_sh_frt_is,
            delta_t=delta_t,
            g_sh_frt_is=self.rms.g_sh_frt_is,
            q_sol_frt_is_n=self.q_sol_frt_is_ns[:, n].reshape(-1, 1),
            theta_frt_is_n=c_n.theta_frt_is_n,
            theta_r_is_n_pls=theta_r_is_n_pls
        )

        # ステップ n+1 における室 i の人体に対する平均放射温度, degree C, [i, 1]
        theta_mrt_hum_is_n_pls = get_theta_mrt_hum_is_n_pls(
            f_mrt_hum_is_js=self.f_mrt_hum_is_js,
            theta_s_js_n_pls=theta_s_js_n_pls
        )

        # ステップ n+1 における境界 j の等価温度, degree C, [j, 1]
        theta_ei_js_n_pls = get_theta_ei_js_n_pls(
            a_s_js=self.bs.a_s_js,
            beta_is_n=beta_is_n,
            f_mrt_is_js=self.f_mrt_is_js,
            f_flr_js_is_n=f_flr_js_is_n,
            h_s_c_js=self.bs.h_s_c_js,
            h_s_r_js=self.bs.h_s_r_js,
            l_rs_is_n=l_rs_is_n,
            p_js_is=self.bs.p_js_is,
            q_s_sol_js_n_pls=self.q_s_sol_js_ns[:, n + 1].reshape(-1, 1),
            theta_r_is_n_pls=theta_r_is_n_pls,
            theta_s_js_n_pls=theta_s_js_n_pls
        )

        # ステップ n+1 における境界 j の裏面温度, degree C, [j, 1]
        # TODO: この値は記録にしか使用していないので、ポスト処理にまわせる。
        theta_rear_js_n_pls = get_theta_s_rear_js_n(
            k_s_er_js_js=self.bs.k_ei_js_js,
            theta_er_js_n=theta_ei_js_n_pls,
            k_s_eo_js=self.bs.k_eo_js,
            theta_eo_js_n=self.bs.theta_o_eqv_js_nspls[:, n+1].reshape(-1, 1),
            k_s_r_js_is=self.bs.k_s_r_js_is,
            theta_r_is_n=theta_r_is_n_pls
        )

        # ステップ n+1 における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
        q_s_js_n_pls = get_q_s_js_n_pls(
            h_s_c_js=self.bs.h_s_c_js,
            h_s_r_js=self.bs.h_s_r_js,
            theta_ei_js_n_pls=theta_ei_js_n_pls,
            theta_s_js_n_pls=theta_s_js_n_pls
        )

        # ステップ n+1 における室 i∗ の絶対湿度がステップ n から n+1 における室 i の潜熱負荷に与える影響を表す係数, kg/(s (kg/kg(DA))), [i, i*]
        # ステップ n から n+1 における室 i の潜熱負荷に与える影響を表す係数, kg/s, [i, 1]
        f_l_cl_cst_is_n, f_l_cl_wgt_is_is_n = self.get_f_l_cl(
            l_cs_is_n=l_cs_is_n,
            theta_r_is_n_pls=theta_r_is_n_pls,
            x_r_ntr_is_n_pls=x_r_ntr_is_n_pls
        )

        # ステップ n+1 における室 i の 絶対湿度, kg/kg(DA), [i, 1]
        x_r_is_n_pls = get_x_r_is_n_pls(
            f_h_cst_is_n=f_h_cst_is_n,
            f_h_wgt_is_is_n=f_h_wgt_is_is_n,
            f_l_cl_cst_is_n=f_l_cl_cst_is_n,
            f_l_cl_wgt_is_is_n=f_l_cl_wgt_is_is_n
        )

        # ステップ n から ステップ n+1 における室 i の潜熱負荷（加湿を正・除湿を負とする）, W, [i, 1]
        l_cl_is_n = get_l_cl_is_n(
            f_l_cl_wgt_is_is_n=f_l_cl_wgt_is_is_n,
            f_l_cl_cst_is_n=f_l_cl_cst_is_n,
            l_wtr=get_l_wtr(),
            x_r_is_n_pls=x_r_is_n_pls
        )

        # ステップ n+1 における室 i の備品等等の絶対湿度, kg/kg(DA), [i, 1]
        x_frt_is_n_pls = get_x_frt_is_n_pls(
            c_lh_frt_is=self.rms.c_lh_frt_is,
            delta_t=delta_t,
            g_lh_frt_is=self.rms.g_lh_frt_is,
            x_frt_is_n=c_n.x_frt_is_n,
            x_r_is_n_pls=x_r_is_n_pls
        )

        if exe_verify:
            
            if n == 0:
                print("Executing verification tests at step {}.".format(n))

            # 室空気の熱収支のテスト
            test_air_heat_balance(
                theta_o_ns_plus=self.weather.theta_o_ns_plus[n+1].reshape(-1, 1),
                theta_r_is_n_pls=theta_r_is_n_pls,
                theta_r_is_n=c_n.theta_r_is_n,
                theta_s_js_n_pls=theta_s_js_n_pls,
                theta_frt_is_n_pls=theta_frt_is_n_pls,
                v_r_is=self.rms.v_r_is, a_s_js=self.bs.a_s_js,
                v_leak_is_n=v_leak_is_n,
                v_vent_ntr_is_n=v_vent_ntr_is_n,
                v_vent_int_is_is=self.mvs.v_vent_int_is_is,
                v_vent_mec_is_ns=self.v_vent_mec_is_ns[:, n].reshape(-1, 1),
                q_gen_is_ns=self.scd.q_gen_is_ns[:, n].reshape(-1, 1),
                q_hum_is_n=q_hum_is_n,
                l_cs_is_n=l_cs_is_n,
                l_rs_is_n=l_rs_is_n,
                beta_is_n=beta_is_n,
                p_js_is=self.bs.p_js_is,
                p_is_js=self.bs.p_is_js,
                h_s_c_js=self.bs.h_s_c_js,
                g_sh_frt_is=self.rms.g_sh_frt_is,
                delta_t=delta_t
            )

            # 室空気の湿収支のテスト
            test_air_moisture_balance(
                x_o_ns_plus=self.weather.x_o_ns_plus[n+1].reshape(-1, 1),
                x_r_is_n_pls=x_r_is_n_pls,
                x_r_is_n=c_n.x_r_is_n,
                x_frt_is_n_pls=x_frt_is_n_pls,
                v_r_is=self.rms.v_r_is,
                v_vent_int_is_is=self.mvs.v_vent_int_is_is,
                v_leak_is_n=v_leak_is_n,
                v_vent_ntr_is_n=v_vent_ntr_is_n,
                v_vent_mec_is_n=self.v_vent_mec_is_ns[:, n].reshape(-1, 1),
                x_gen_is_n=self.scd.x_gen_is_ns[:, n].reshape(-1,1),
                l_cl_is_n=l_cl_is_n,
                x_hum_is_n=x_hum_is_n,
                g_lh_frt_is=self.rms.g_lh_frt_is,
                delta_t=delta_t
            )
        
            #### 備品の熱収支のテスト ####
            test_frt_heat_balance(
                theta_frt_is_n_pls=theta_frt_is_n_pls,
                theta_frt_is_n=c_n.theta_frt_is_n,
                theta_r_is_n_pls=theta_r_is_n_pls,
                q_sol_frt_is_ns=self.q_sol_frt_is_ns[:, n].reshape(-1, 1),
                c_sh_frt_is=self.rms.c_sh_frt_is,
                g_sh_frt_is=self.rms.g_sh_frt_is,
                delta_t=delta_t
            )
            
            # 備品の湿収支のテスト
            test_frt_moisture_balance(
                x_frt_is_n_pls=x_frt_is_n_pls,
                x_frt_is_n=c_n.x_frt_is_n,
                x_r_is_n_pls=x_r_is_n_pls,
                c_lh_frt_is=self.rms.c_lh_frt_is,
                g_lh_frt_is=self.rms.g_lh_frt_is,
                delta_t=delta_t
            )

            #### 室内表面の放射熱収支のテスト ####
            test_surface_radiation_balance(
                theta_s_js_n_pls=theta_s_js_n_pls,
                p_js_is=self.bs.p_js_is,
                f_mrt_is_js=self.f_mrt_is_js,
                h_s_r_js=self.bs.h_s_r_js,
                a_s_js=self.bs.a_s_js,
                p_is_js=self.bs.p_is_js
            )
            
            #### 透過日射熱取得の収支のテスト ####
            test_solar_heat_gain_balance(
                p_is_js=self.bs.p_is_js,
                q_trs_sol_is_ns=self.q_trs_sol_is_ns[:, n + 1].reshape(-1, 1),
                q_sol_frt_is_ns=self.q_sol_frt_is_ns[:, n + 1].reshape(-1, 1),
                q_s_sol_js_ns=self.q_s_sol_js_ns[:, n + 1].reshape(-1, 1),
                a_s_js=self.bs.a_s_js
                )
            
            #### 境界表面温度の計算結果のテスト ####
            test_theta_surface(
                theta_s_js=theta_s_js_n_pls,
                theta_rear_js=theta_rear_js_n_pls,
                f_cvl_js=f_cvl_js_n_pls,
                q_i_s_js=q_s_js_n_pls,
                phi_a0_js=self.bs.phi_a0_js,
                phi_t0_js=self.bs.phi_t0_js
            )

        if recorder is not None:
            recorder.recording(
                n=n,
                theta_r_is_n_pls=theta_r_is_n_pls,
                theta_mrt_hum_is_n_pls=theta_mrt_hum_is_n_pls,
                x_r_is_n_pls=x_r_is_n_pls,
                theta_frt_is_n_pls=theta_frt_is_n_pls,
                x_frt_is_n_pls=x_frt_is_n_pls,
                theta_ei_js_n_pls=theta_ei_js_n_pls,
                q_s_js_n_pls=q_s_js_n_pls,
                theta_ot_is_n_pls=theta_ot_is_n_pls,
                theta_s_js_n_pls=theta_s_js_n_pls,
                theta_rear_js_n=theta_rear_js_n_pls,
                f_cvl_js_n_pls=f_cvl_js_n_pls,
                operation_mode_is_n=operation_mode_is_n,
                l_cs_is_n=l_cs_is_n,
                l_rs_is_n=l_rs_is_n,
                l_cl_is_n=l_cl_is_n,
                h_hum_c_is_n=h_hum_c_is_n,
                h_hum_r_is_n=h_hum_r_is_n,
                q_hum_is_n=q_hum_is_n,
                x_hum_is_n=x_hum_is_n,
                v_leak_is_n=v_leak_is_n,
                v_vent_ntr_is_n=v_vent_ntr_is_n
            )

        return Conditions(
            operation_mode_is_n=operation_mode_is_n,
            theta_r_is_n=theta_r_is_n_pls,
            theta_mrt_hum_is_n=theta_mrt_hum_is_n_pls,
            x_r_is_n=x_r_is_n_pls,
            theta_dsh_s_a_js_ms_n=theta_dsh_s_a_js_ms_n_pls,
            theta_dsh_s_t_js_ms_n=theta_dsh_s_t_js_ms_n_pls,
            q_s_js_n=q_s_js_n_pls,
            theta_frt_is_n=theta_frt_is_n_pls,
            x_frt_is_n=x_frt_is_n_pls,
            theta_ei_js_n=theta_ei_js_n_pls
        )


    def run_tick_ground(self, gc_n: GroundConditions, n: int):

        return _run_tick_ground(self=self, gc_n=gc_n, n=n)


def test_air_heat_balance(
        theta_r_is_n_pls: np.ndarray,
        theta_o_ns_plus: np.ndarray,
        theta_r_is_n: np.ndarray,
        theta_s_js_n_pls: np.ndarray,
        theta_frt_is_n_pls: np.ndarray,
        v_r_is: np.ndarray,
        a_s_js: np.ndarray,
        v_leak_is_n: np.ndarray,
        v_vent_ntr_is_n: np.ndarray,
        v_vent_int_is_is: np.ndarray,
        v_vent_mec_is_ns: np.ndarray,
        q_gen_is_ns: np.ndarray,
        q_hum_is_n: np.ndarray,
        l_cs_is_n: np.ndarray,
        l_rs_is_n: np.ndarray,
        beta_is_n: np.ndarray,
        p_js_is: np.ndarray,
        p_is_js: np.ndarray,
        h_s_c_js: np.ndarray,
        g_sh_frt_is: np.ndarray,
        delta_t: float
    ):
    """
    test_air_heat_balance の Docstring
    
    :param theta_o_ns_plus: ステップn+1の外気温, degree C, [i, 1]
    :type theta_o_ns_plus: np.ndarray
    :param theta_r_is_n_pls: ステップn+1の室温, degree C, [i, 1]
    :type theta_r_is_n_pls: np.ndarray
    :param theta_r_is_n: ステップnの室温, degree C, [i, 1]
    :type theta_r_is_n: np.ndarray
    :param theta_s_js_n_pls: ステップn+1の境界jの表面温度, degree C, [j, 1]
    :type theta_s_js_n_pls: np.ndarray
    :param theta_frt_is_n_pls: ステップn+1の備品等の温度, degree C, [i, 1]
    :type theta_frt_is_n_pls: np.ndarray
    :param v_r_is: 室容積, m3, [i, 1]
    :type v_r_is: np.ndarray
    :param a_s_js: 部位面積, m2, [j, 1]
    :type a_s_js: np.ndarray
    :param v_leak_is_n: ステップnのすきま風量, m3/s, [i, 1]
    :type v_leak_is_n: np.ndarray
    :param v_vent_ntr_is_n: ステップnの自然換気量, m3/s, [i, 1]
    :type v_vent_ntr_is_n: np.ndarray
    :param v_vent_mec_is_ns: ステップnの機械換気量, m3/s, [i, 1]
    :type v_vent_mec_is_ns: np.ndarray
    :param q_gen_is_ns: ステップnの内部発熱量, W, [i, 1]
    :type q_gen_is_ns: np.ndarray
    :param q_hum_is_n: ステップnの人体発熱量, W, [i, 1]
    :type q_hum_is_n: np.ndarray
    :param l_cs_is_n: ステップnの顕熱負荷, W, [i, 1]
    :type l_cs_is_n: np.ndarray
    :param l_rs_is_n: ステップnの放射顕熱負荷, W, [i, 1]
    :type l_rs_is_n: np.ndarray
    :param beta_is_n: ステップnの室iにおける放射暖冷房設備の対流成分比率, -, [i, 1]
    :type beta_is_n: np.ndarray
    :param delta_t: 時間間隔, s
    :type delta_t: float
    """

    #### 室空気の熱収支テスト ####
    rho_c_a = get_c_a() * get_rho_a()
    # 室空気の熱容量, [J/K]
    cap_r_air_is = rho_c_a * v_r_is
    # 室空気の温度変化に伴う熱負荷, W
    left = (theta_r_is_n_pls - theta_r_is_n) * cap_r_air_is / delta_t
    # 部位からの対流熱取得量, W
    q_c_surf_js = (theta_s_js_n_pls - np.dot(p_js_is, theta_r_is_n_pls)) * h_s_c_js * a_s_js
    q_c_surf = np.dot(p_is_js, q_c_surf_js)
    # 備品からの熱取得量, W
    q_c_frt = (theta_frt_is_n_pls - theta_r_is_n_pls) * g_sh_frt_is
    # すきま風による熱取得量, W
    q_c_leak = rho_c_a * v_leak_is_n * (theta_o_ns_plus - theta_r_is_n_pls)
    # 機械換気による熱取得量, W
    v_vent_mec_is_n = v_vent_mec_is_ns
    q_c_vent = rho_c_a * v_vent_mec_is_n * (theta_o_ns_plus - theta_r_is_n_pls)
    # 自然換気による熱取得量, W
    q_c_ntrl_vent = rho_c_a * v_vent_ntr_is_n * (theta_o_ns_plus - theta_r_is_n_pls)
    # 隣室間換気による熱取得量, W
    theta_pls = theta_r_is_n_pls  # (n_pls時点の室温) shape=(n_room,1) を想定
    v_in = np.clip(v_vent_int_is_is, 0.0, None)  # 負→0、正はそのまま
    v_sum_in = v_in.sum(axis=1, keepdims=True)            # 各室への総流入量  shape=(n_room,1)
    q_c_int_vent = rho_c_a * (v_in @ theta_pls - v_sum_in * theta_pls)
    # 局所換気による熱取得量, W
    # 内部発熱による熱取得量, W
    q_c_gen = q_gen_is_ns + q_hum_is_n
    # 顕熱負荷, W
    l_cs = l_cs_is_n + l_rs_is_n * beta_is_n
    # 熱収支式の右辺, W
    right = q_c_surf + q_c_frt + q_c_leak + q_c_vent + q_c_ntrl_vent + q_c_int_vent + q_c_gen + l_cs

    test_balance_check(left=left, right=right, quantity="air heat")


def test_balance_check(left: np.ndarray, right: np.ndarray, quantity: str):
    """
    test_balance_check の Docstring
    
    :param left: 収支式の左辺
    :type left: np.ndarray
    :param right: 収支式の右辺
    :type right: np.ndarray
    :param quantity: 収支の対象（例：heat, moisture）
    :type quantity: str
    """

    if not np.allclose(left, right, rtol=1e-6, atol=1e-6, equal_nan=True):
        diff = left - right
        max_abs = np.max(np.abs(diff))
        idx = np.unravel_index(np.argmax(np.abs(diff)), diff.shape)
        logger.error(
            f"{quantity} balance is not correct. "
            f"max|left-right|={max_abs} at index={idx}, "
            f"left={left[idx]}, right={right[idx]}"
        )


def test_air_moisture_balance(
        x_o_ns_plus: np.ndarray,
        x_r_is_n_pls: np.ndarray,
        x_r_is_n: np.ndarray,
        x_frt_is_n_pls: np.ndarray,
        v_r_is: np.ndarray,
        v_vent_mec_is_n: np.ndarray,
        v_vent_int_is_is: np.ndarray,
        v_leak_is_n: np.ndarray,
        v_vent_ntr_is_n: np.ndarray,
        x_gen_is_n: np.ndarray,
        x_hum_is_n: np.ndarray,
        g_lh_frt_is: np.ndarray,
        l_cl_is_n: np.ndarray,
        delta_t: float
    ):
    """
    test_air_moisture_balance の Docstring
    
    :param n: 計算ステップ
    :type n: int
    :param x_r_is_n_pls: ステップn+1の室絶対湿度, kg/kg(DA), [i, 1]
    :type x_r_is_n_pls: np.ndarray
    :param x_r_is_n: ステップnの室絶対湿度, kg/kg(DA), [i, 1]
    :type x_r_is_n: np.ndarray
    :param x_frt_is_n_pls: ステップn+1の備品等の絶対湿度, kg/kg(DA), [i, 1]
    :type x_frt_is_n_pls: np.ndarray
    :param v_leak_is_n: ステップnのすきま風量, m3/s, [i, 1]
    :type v_leak_is_n: np.ndarray
    :param v_vent_ntr_is_n: ステップnの自然換気風量, m3/s, [i, 1]
    :type v_vent_ntr_is_n: np.ndarray
    :param x_hum_is_n: ステップnの人体発湿量, kg/s, [i, 1]
    :type x_hum_is_n: np.ndarray
    :param l_cl_is_n: 潜熱負荷, W, [i, 1]
    :type l_cl_is_n: np.ndarray
    :param delta_t: 時間間隔, s
    :type delta_t: float
    """

    #### 室空気の湿収支テスト ####
    rho_a = get_rho_a()
    # 室空気の湿度変化に伴う湿負荷, kg/s
    left = (x_r_is_n_pls - x_r_is_n) * rho_a * v_r_is / delta_t
    # 備品等からの湿取得量, kg/s
    q_w_frt = (x_frt_is_n_pls - x_r_is_n_pls) * g_lh_frt_is
    # すきま風による湿取得量, kg/s
    q_w_leak = rho_a * v_leak_is_n * (x_o_ns_plus - x_r_is_n_pls)
    # 機械換気による湿取得量, kg/s
    q_w_vent = rho_a * v_vent_mec_is_n * (x_o_ns_plus - x_r_is_n_pls)
    # 自然換気による湿取得量, kg/s
    q_w_ntrl_vent = rho_a * v_vent_ntr_is_n * (x_o_ns_plus - x_r_is_n_pls)
    # 隣室間換気による湿取得量, kg/s
    x_pls = x_r_is_n_pls  # (n_pls時点の室湿度) shape=(n_room,1) を想定
    v_in = np.clip(v_vent_int_is_is, 0.0, None)  # 負→0、正はそのまま
    v_sum_in = v_in.sum(axis=1, keepdims=True)            # 各室への総流入量  shape=(n_room,1)
    q_w_int_vent = rho_a * (v_in @ x_pls - v_sum_in * x_pls)
    # 内部発湿による湿取得量, kg/s
    q_w_gen = x_gen_is_n + x_hum_is_n
    # 潜熱負荷, kg/s
    l_cl = l_cl_is_n / get_l_wtr()
    # 湿収支式の右辺, kg/s
    right = q_w_frt + q_w_leak + q_w_vent + q_w_ntrl_vent + q_w_int_vent + q_w_gen + l_cl

    test_balance_check(left=left, right=right, quantity="air moisture")


def test_frt_heat_balance(
        theta_frt_is_n_pls: np.ndarray,
        theta_frt_is_n: np.ndarray,
        theta_r_is_n_pls: np.ndarray,
        c_sh_frt_is: np.ndarray,
        g_sh_frt_is: np.ndarray,
        q_sol_frt_is_ns: np.ndarray,
        delta_t: float
    ):
    """
    test_frt_heat_balance の Docstring
    
    :param n: 計算ステップ
    :type n: int
    :param theta_frt_is_n_pls: ステップn+1の備品等の温度, degree C, [i, 1]
    :type theta_frt_is_n_pls: np.ndarray
    :param theta_frt_is_n: ステップnの備品等の温度, degree C, [i, 1]
    :type theta_frt_is_n: np.ndarray
    :param theta_r_is_n_pls: ステップn+1の室温, degree C, [i, 1]
    :type theta_r_is_n_pls: np.ndarray
    :param delta_t: 時間間隔, s
    :type delta_t: float
    """

    #### 備品の熱収支のテスト ####
    # 備品等の熱容量, [J/K]
    cap_frt_is = c_sh_frt_is
    # 備品等の温度変化に伴う熱負荷, W
    left = (theta_frt_is_n_pls - theta_frt_is_n) * cap_frt_is / delta_t
    # 備品等の熱収支式の右辺, W
    right = (theta_r_is_n_pls - theta_frt_is_n_pls) * g_sh_frt_is + q_sol_frt_is_ns
    test_balance_check(left=left, right=right, quantity="furniture heat")

def test_frt_moisture_balance(
        x_frt_is_n_pls: np.ndarray,
        x_frt_is_n: np.ndarray,
        x_r_is_n_pls: np.ndarray,
        c_lh_frt_is: np.ndarray,
        g_lh_frt_is: np.ndarray,
        delta_t: float
    ):
    """
    test_frt_moisture_balance の Docstring
    
    :param self: 説明
    :param n: 計算ステップ
    :type n: int
    :param x_frt_is_n_pls: ステップn+1の備品等の絶対湿度, kg/kg(DA), [i, 1]
    :type x_frt_is_n_pls: np.ndarray
    :param x_frt_is_n: ステップnの備品等の絶対湿度, kg/kg(DA), [i, 1]
    :type x_frt_is_n: np.ndarray
    :param x_r_is_n_pls: ステップn+1の室絶対湿度, kg/kg(DA), [i, 1]
    :type x_r_is_n_pls: np.ndarray
    :param delta_t: 時間間隔, s
    :type delta_t: float
    """

    # 備品等の湿容量, [kg/(kg(DA))]
    cap_frt_is = c_lh_frt_is
    # 備品等の湿度変化に伴う湿負荷, kg/s
    left = (x_frt_is_n_pls - x_frt_is_n) * cap_frt_is / delta_t
    # 備品等の湿収支式の右辺, kg/s
    right = (x_r_is_n_pls - x_frt_is_n_pls) * g_lh_frt_is
    test_balance_check(left=left, right=right, quantity="furniture moisture")

def test_surface_radiation_balance(
        theta_s_js_n_pls: np.ndarray,
        p_js_is: np.ndarray,
        f_mrt_is_js: np.ndarray,
        h_s_r_js: np.ndarray,
        a_s_js: np.ndarray,
        p_is_js: np.ndarray
    ):
    """
    test_surface_radiation_balance の Docstring
    
    :param theta_s_js_n_pls: ステップn+1の境界jの表面温度, degree C, [j, 1]
    :type theta_s_js_n_pls: np.ndarray
    """

    #### 室内表面の放射熱収支のテスト ####
    # 部位jの表面放射熱収支式の左辺, W
    theta_mrt_is_n_pls = np.dot(np.dot(p_js_is, f_mrt_is_js), theta_s_js_n_pls)
    q_r_surf = h_s_r_js * a_s_js * (theta_mrt_is_n_pls - theta_s_js_n_pls)
    left = np.dot(p_is_js, q_r_surf)
    # 部位jの表面放射熱収支式の右辺, W
    right = np.zeros_like(left)
    test_balance_check(left=left, right=right, quantity="surface radiation heat")

def test_solar_heat_gain_balance(
        p_is_js: np.ndarray,
        q_trs_sol_is_ns: np.ndarray,
        q_sol_frt_is_ns: np.ndarray,
        q_s_sol_js_ns: np.ndarray,
        a_s_js: np.ndarray
    ):
    """
    test_solar_heat_gain_balance の Docstring
    透過日射熱取得が家具と部位の吸収日射熱取得と一致することのテスト
    :param p_is_js: 部位-室分布係数, -, [i, j]
    :type p_is_js: np.ndarray
    :param q_trs_sol_is_ns: 透過日射熱取得, W, [i, 1]
    :type q_trs_sol_is_ns: np.ndarray
    :param q_sol_frt_is_ns: 備品の吸収日射熱取得, W, [i, 1]
    :type q_sol_frt_is_ns: np.ndarray
    :param q_s_sol_js_ns: 部位の吸収日射熱取得, W/m2, [j, 1]
    :type q_s_sol_js_ns: np.ndarray
    :param a_s_js: 部位の面積, m2, [j, 1]
    :type a_s_js: np.ndarray
    """

    # 透過日射熱取得の合計, W
    left = q_trs_sol_is_ns
    # 備品の吸収日射熱取得と部位の吸収日射熱取得の合計, W
    Q_s_sol_js_ns = q_s_sol_js_ns * a_s_js  # 部位の吸収日射熱取得を面積で換
    right = q_sol_frt_is_ns + np.dot(p_is_js, Q_s_sol_js_ns)

    test_balance_check(left=left, right=right, quantity="solar heat gain")

def test_theta_surface(
    theta_s_js: np.ndarray,
    theta_rear_js: np.ndarray,
    f_cvl_js: np.ndarray,
    q_i_s_js: np.ndarray,
    phi_a0_js: np.ndarray,
    phi_t0_js: np.ndarray
):
    """
    test_theta_surface の Docstring
    表面温度の計算結果のテスト
    
    :param theta_s_js: 表面温度, degree C, [j, 1]
    :type theta_s_js: np.ndarray
    :param theta_rear_js: 裏面温度, degree C, [j, 1]
    :type theta_rear_js: np.ndarray
    :param f_cvl_js: 係数 f_{CVL}, -, [j, 1]
    :type f_cvl_js: np.ndarray
    :param q_i_s_js: 室内表面熱流, W/m2, [j, 1]
    :type q_i_s_js: np.ndarray
    :param phi_a0_js: 吸熱応答の初項, m2 K/W, [j, 1]
    :type phi_a0_js: np.ndarray
    :param phi_t0_js: 貫流応答の初項, -, [j, 1]
    :type phi_t0_js: np.ndarray
    """

    # 表面温度
    left = theta_s_js
    right = phi_a0_js * q_i_s_js + phi_t0_js * theta_rear_js + f_cvl_js
    test_balance_check(left=left, right=right, quantity="surface temperature")

def _run_tick_ground(self, gc_n: GroundConditions, n: int):
    """地盤の計算

    Args:
        pp:
        gc_n:
        n:

    Returns:

    """

    is_ground = self.bs.b_ground_js.flatten()

    theta_o_eqv_js_ns = self.bs.theta_o_eqv_js_nspls[is_ground, :]

    h_i_js = self.bs.h_s_r_js[is_ground, :] + self.bs.h_s_c_js[is_ground, :]

    theta_dsh_srf_a_js_ms_npls = self.bs.phi_a1_js_ms[is_ground, :] * gc_n.q_srf_js_n + self.bs.r_js_ms[is_ground, :] * gc_n.theta_dsh_srf_a_js_ms_n

    theta_dsh_srf_t_js_ms_npls = self.bs.phi_t1_js_ms[is_ground, :] * self.bs.k_eo_js[is_ground, :] * theta_o_eqv_js_ns[:, [n]] + self.bs.r_js_ms[is_ground, :] * gc_n.theta_dsh_srf_t_js_ms_n

    theta_s_js_npls = (
        self.bs.phi_a0_js[is_ground, :] * h_i_js * self.weather.theta_o_ns_plus[n + 1]
        + self.bs.phi_t0_js[is_ground, :] * self.bs.k_eo_js[is_ground, :] * theta_o_eqv_js_ns[:, [n+1]]
        + np.sum(theta_dsh_srf_a_js_ms_npls, axis=1, keepdims=True)
        + np.sum(theta_dsh_srf_t_js_ms_npls, axis=1, keepdims=True)
    ) / (1.0 + self.bs.phi_a0_js[is_ground, :] * h_i_js)

    q_srf_js_n = h_i_js * (self.weather.theta_o_ns_plus[n + 1] - theta_s_js_npls)

    return GroundConditions(
        theta_dsh_srf_a_js_ms_n=theta_dsh_srf_a_js_ms_npls,
        theta_dsh_srf_t_js_ms_n=theta_dsh_srf_t_js_ms_npls,
        q_srf_js_n=q_srf_js_n,
    )


# region equation 4 (pre calculation)

def get_f_wsc_js_ns(f_ax_js_js, f_crx_js_ns):
    """

    Args:
        f_ax_js_js: 係数 f_{AX}, -, [j, j]
        f_crx_js_ns: 係数 f_{CRX,n}, degree C, [j, n]

    Returns:
        係数 f_{WSC,n}, degree C, [j, n]

    Notes:
        式(4.1)
    """

    return np.linalg.solve(f_ax_js_js, f_crx_js_ns)


def get_f_wsr_js_is(f_ax_js_js, f_fia_js_is):
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


def get_v_vent_mec_is_ns(v_vent_mec_general_is, v_vent_mec_local_is_ns):
    """

    Args:
        v_vent_mec_general_is: ステップ n からステップ n+1 における室 i の機械換気量（全般換気量）, m3/s, [i, 1]
        v_vent_mec_local_is_ns: ステップ n からステップ n+1 における室 i の機械換気量（局所換気量）, m3/s, [i, 1]

    Returns:
        ステップ n からステップ n+1 における室 i の機械換気量（全般換気量と局所換気量の合計値）, m3/s, [i, 1]

    Notes:
        式(4.7)
    """

    return v_vent_mec_general_is + v_vent_mec_local_is_ns

# endregion


# region equation 1-2 (sequence calculation)

def get_x_frt_is_n_pls(c_lh_frt_is, delta_t: float, g_lh_frt_is, x_frt_is_n, x_r_is_n_pls):
    """

    Args:
        c_lh_frt_is: 室 i の備品等の湿気容量, kg/(kg/kg(DA)), [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_lh_frt_is: 室 i の備品等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA)), [i, 1]
        x_frt_is_n: ステップ n における室 i の備品等の絶対湿度, kg/kg(DA), [i, 1]
        x_r_is_n_pls: ステップ n+1 における室 i の絶対湿度, kg/kg(DA), [i, 1]

    Returns:
        ステップ n+1 における室 i の備品等等の絶対湿度, kg/kg(DA), [i, 1]

    Notes:
        式(1.1)

    """

    return (c_lh_frt_is * x_frt_is_n + delta_t * g_lh_frt_is * x_r_is_n_pls) / (c_lh_frt_is + delta_t * g_lh_frt_is)


def get_l_cl_is_n(f_l_cl_wgt_is_is_n, f_l_cl_cst_is_n, l_wtr, x_r_is_n_pls):
    """

    Args:
        f_l_cl_wgt_is_is_n: 係数, kg/(s (kg/kg(DA)))
        f_l_cl_cst_is_n: 係数, kg/s
        l_wtr: 水の蒸発潜熱, J/kg
        x_r_is_n_pls: ステップ n+1 における室 i の絶対湿度, kg/kg(DA)

    Returns:
        ステップ n から ステップ n+1 における室 i の潜熱負荷（加湿を正・除湿を負とする）, W

    Notes:
        式(1.2)

    """

    return (np.dot(f_l_cl_wgt_is_is_n, x_r_is_n_pls) + f_l_cl_cst_is_n) * l_wtr


def get_x_r_is_n_pls(f_h_cst_is_n, f_h_wgt_is_is_n, f_l_cl_cst_is_n, f_l_cl_wgt_is_is_n):
    """

    Args:
        f_h_cst_is_n: 係数, kg/s
        f_h_wgt_is_is_n: 係数, kg/(s (kg/kg(DA)))
        f_l_cl_cst_is_n: 係数, kg/s
        f_l_cl_wgt_is_is_n: 係数, kg/(s (kg/kg(DA)))

    Returns:
        ステップ n+1 における室 i の 絶対湿度, kg/kg(DA), [i, 1]

    Notes:
        式(1.3)

    """

    return np.linalg.solve(f_h_wgt_is_is_n - f_l_cl_wgt_is_is_n, f_h_cst_is_n + f_l_cl_cst_is_n)


def get_x_r_ntr_is_n_pls(
        f_h_cst_non_nv_is_n: np.ndarray,
        f_h_wgt_non_nv_is_is_n: np.ndarray,
        f_h_cst_nv_is_n: np.ndarray,
        f_h_wgt_nv_is_is_n: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """

    Args:
        f_h_cst_non_nv_is_n: ステップnにおける自然風非利用時の室iの係数f_h_cst, kg/s
        f_h_wgt_non_nv_is_is_n: ステップnにおける自然風利用時の室iの係数f_h_wgt, kg/(s (kg/kg(DA)))
        f_h_cst_nv_is_n: ステップnにおける自然風利用時の室iの係数f_h_cst, kg/s
        f_h_wgt_nv_is_is_n: ステップnにおける自然風利用時の室iの係数f_wgt, kg/(s (kg/kg(DA)))

    Returns:
        ステップ n+1 における室 i の加湿・除湿を行わない場合の絶対湿度, kg/kg(DA) [i, 1]

    Notes:
        式(1.4)

    """

    x_r_ntr_non_nv_is_n_pls = np.linalg.solve(f_h_wgt_non_nv_is_is_n, f_h_cst_non_nv_is_n)
    x_r_ntr_nv_is_n_pls = np.linalg.solve(f_h_wgt_nv_is_is_n, f_h_cst_nv_is_n)

    return x_r_ntr_non_nv_is_n_pls, x_r_ntr_nv_is_n_pls


def get_f_h_wgt_is_is_n(
        c_lh_frt_is: np.ndarray,
        delta_t: float,
        g_lh_frt_is: np.ndarray,
        rho_a: float,
        v_rm_is: np.ndarray,
        v_vent_int_is_is_n: np.ndarray,
        v_vent_out_non_nv_is_n: np.ndarray,
        v_vent_ntr_is: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """

    Args:
        c_lh_frt_is: 室 i の備品等の湿気容量, kg/(kg/kg(DA)), [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_lh_frt_is: 室 i の備品等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA)), [i, 1]
        rho_a: 空気の密度, kg/m3
        v_rm_is: 室 i の容量, m3, [i, 1]
        v_vent_int_is_is_n:　ステップ n から ステップ n+1 における室 i* から室 i への室間の空気移動量（流出換気量を含む）, m3/s
        v_vent_out_non_nv_is_n: ステップnからステップn+1における室iの換気・隙間風による外気の流入量, m3/s, [i, 1]
        v_vent_ntr_is: 室iの自然風利用時の換気量, m3/s, [i, 1]

    Returns:
        ステップnにおける自然風非利用時の室i*の絶対湿度が室iの潜熱バランスに与える影響を表す係数,　kg/(s kg/kg(DA)), [i, i]
        ステップnにおける自然風利用時の室i*の絶対湿度が室iの潜熱バランスに与える影響を表す係数,　kg/(s kg/kg(DA)), [i, i]

    Notes:
        式(1.5)

    """

    f_h_wgt_non_nv_is_is_n = v_diag(
        rho_a * (v_rm_is / delta_t + v_vent_out_non_nv_is_n)
        + c_lh_frt_is * g_lh_frt_is / (c_lh_frt_is + delta_t * g_lh_frt_is)
    ) - rho_a * v_vent_int_is_is_n

    f_h_wgt_nv_is_is_n = f_h_wgt_non_nv_is_is_n + v_diag(rho_a * v_vent_ntr_is)

    return f_h_wgt_non_nv_is_is_n, f_h_wgt_nv_is_is_n


def get_f_h_cst_is_n(
        c_lh_frt_is: np.ndarray,
        delta_t: float,
        g_lh_frt_is: np.ndarray,
        rho_a: float,
        v_rm_is: np.ndarray,
        x_frt_is_n: np.ndarray,
        x_gen_is_n: np.ndarray,
        x_hum_is_n: np.ndarray,
        x_o_n_pls: np.ndarray,
        x_r_is_n: np.ndarray,
        v_vent_out_non_nv_is_n: np.ndarray,
        v_vent_ntr_is: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """

    Args:
        c_lh_frt_is: 室 i の備品等の湿気容量, kg/(kg/kg(DA)), [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_lh_frt_is: 室 i の備品等と空気間の湿気コンダクタンス, kg/(s kg/kg(DA)), [i, 1]
        rho_a: 空気の密度, kg/m3
        v_rm_is: 室 i の容量, m3, [i, 1]
        x_frt_is_n: ステップ n における室 i の備品等の絶対湿度, kg/kg(DA), [i, 1]
        x_gen_is_n: ステップ n からステップ n+1 における室 i の人体発湿を除く内部発湿, kg/s
        x_hum_is_n: ステップ n からステップ n+1 における室 i の人体発湿, kg/s
        x_o_n_pls: ステップ n における外気絶対湿度, kg/kg(DA)
        x_r_is_n: ステップ n における室 i の絶対湿度, kg/kg(DA)
        v_vent_out_non_nv_is_n: ステップnからステップn+1における室iの換気・隙間風による外気の流入量, m3/s, [i, 1]
        v_vent_ntr_is: 室iの自然風利用時の換気量, m3/s, [i, 1]

    Returns:
        ステップnにおける室iの自然風の非利用時の潜熱バランスに関する係数f_h_cst, kg/s, [i, 1]
        ステップnにおける室iの自然風の利用時の潜熱バランスに関する係数f_h_cst, kg/s, [i, 1]

    Notes:
        式(1.6)

    """
    f_h_cst_non_nv_is_n = rho_a * v_rm_is / delta_t * x_r_is_n \
       + rho_a * v_vent_out_non_nv_is_n * x_o_n_pls \
       + c_lh_frt_is * g_lh_frt_is / (c_lh_frt_is + delta_t * g_lh_frt_is) * x_frt_is_n \
       + x_gen_is_n + x_hum_is_n

    f_h_cst_nv_is_n = f_h_cst_non_nv_is_n + rho_a * v_vent_ntr_is * x_o_n_pls

    return f_h_cst_non_nv_is_n, f_h_cst_nv_is_n


def get_x_hum_is_n(n_hum_is_n, x_hum_psn_is_n):
    """

    Args:
        n_hum_is_n: ステップ n からステップ n+1 における室 i の在室人数, -
        x_hum_psn_is_n: ステップ n からステップ n+1 における室 i の1人あたりの人体発湿, kg/s

    Returns:
        ステップnの室iにおける人体発湿, kg/s, [i, 1]

    Notes:
        式(1.7)

    """

    return x_hum_psn_is_n * n_hum_is_n


def get_q_s_js_n_pls(h_s_c_js, h_s_r_js, theta_ei_js_n_pls, theta_s_js_n_pls):
    """

    Args:
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        theta_ei_js_n_pls: ステップ n+1 における境界 j の等価温度, degree C, [j, 1]
        theta_s_js_n_pls: ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Returns:
        ステップ n+1 における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]

    Notes:
        式(2.1)

    """

    return (theta_ei_js_n_pls - theta_s_js_n_pls) * (h_s_c_js + h_s_r_js)


def get_theta_ei_js_n_pls(a_s_js, beta_is_n, f_mrt_is_js, f_flr_js_is_n, h_s_c_js, h_s_r_js, l_rs_is_n, p_js_is, q_s_sol_js_n_pls, theta_r_is_n_pls, theta_s_js_n_pls):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        beta_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
        f_mrt_is_js: 室 i の微小球に対する境界 j の形態係数, -, [i, j]
        f_flr_js_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        h_s_r_js: 境界 j の室内側放射熱伝達率, W/(m2 K), [j, 1]
        l_rs_is_n: ステップ n からステップ n+1 における室 i に放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W, [i, 1]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        q_s_sol_js_n_pls: ステップ n+1 における境界 j の透過日射吸収熱量, W/m2, [j, 1]
        theta_r_is_n_pls: ステップ n+1 における室 i の温度, degree C, [i, 1]
        theta_s_js_n_pls: ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Returns:
        ステップ n+1 における境界 j の等価温度, degree C, [j, 1]
    Notes:
        式(2.2)

    """

    return (
        h_s_c_js * np.dot(p_js_is, theta_r_is_n_pls)
        + h_s_r_js * np.dot(np.dot(p_js_is, f_mrt_is_js), theta_s_js_n_pls)
        + q_s_sol_js_n_pls
        + np.dot(f_flr_js_is_n, (1.0 - beta_is_n) * l_rs_is_n) / a_s_js
    ) / (h_s_c_js + h_s_r_js)


def get_theta_mrt_hum_is_n_pls(f_mrt_hum_is_js, theta_s_js_n_pls):
    """

    Args:
        f_mrt_hum_is_js: 室 i の人体に対する境界 j の形態係数, -, [i, j]
        theta_s_js_n_pls: ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Returns:
        ステップ n+1 における室 i の人体に対する平均放射温度, degree C, [i, 1]

    Notes:
        式(2.3)

    """

    return np.dot(f_mrt_hum_is_js, theta_s_js_n_pls)


def get_theta_frt_is_n_pls(c_sh_frt_is, delta_t: float, g_sh_frt_is, q_sol_frt_is_n, theta_frt_is_n, theta_r_is_n_pls):
    """

    Args:
        c_sh_frt_is: 室 i の備品等の熱容量, J/K, [i, 1]
        delta_t: 1ステップの時間間隔, s
        g_sh_frt_is: 室 i の備品等と空気間の熱コンダクタンス, W/K, [i, 1]
        q_sol_frt_is_n: ステップ n からステップ n+1 における室 i に設置された備品等による透過日射吸収熱量時間平均値, W, [i, 1]
        theta_frt_is_n: ステップ n における室 i の備品等の温度, degree C, [i, 1]
        theta_r_is_n_pls: ステップ n+1 における室 i の温度, degree C, [i, 1]

    Returns:
        ステップ n+1 における室 i　の備品等の温度, degree C, [i, 1]

    Notes:
        式(2.4)

    """

    return (
        c_sh_frt_is * theta_frt_is_n + delta_t * g_sh_frt_is * theta_r_is_n_pls + q_sol_frt_is_n * delta_t
    ) / (c_sh_frt_is + delta_t * g_sh_frt_is)


def get_theta_s_js_n_pls(f_wsb_js_is_n_pls, f_wsc_js_n_pls, f_wsr_js_is, f_wsv_js_n_pls, l_rs_is_n, theta_r_is_n_pls):
    """

    Args:
        f_wsb_js_is_n_pls: ステップ n+1 における係数 f_WSB, K/W, [j, 1]
        f_wsc_js_n_pls: ステップ n+1 における係数 f_WSC, degree C, [j, 1]
        f_wsr_js_is: 係数 f_WSR, - [j, i]
        f_wsv_js_n_pls: ステップ n+1 における係数 f_WSV, degree C, [j, 1]
        l_rs_is_n: ステップ n からステップ n+1 における室 i に放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W, [i, 1]
        theta_r_is_n_pls: ステップ n+1 における室 i の温度, degree C, [i, 1]

    Returns:
        ステップ n+1 における境界 j の表面温度, degree C, [j, 1]

    Notes:
        式(2.5)

    """

    return np.dot(f_wsr_js_is, theta_r_is_n_pls) + f_wsc_js_n_pls + np.dot(f_wsb_js_is_n_pls, l_rs_is_n) + f_wsv_js_n_pls


def get_theta_r_is_n_pls(f_xc_is_n_pls, f_xlr_is_is_n_pls, f_xot_is_is_n_pls, l_rs_is_n, theta_ot_is_n_pls):
    """

    Args:
        f_xc_is_n_pls: ステップ n+1 における係数 f_XC, degree C, [i, 1]
        f_xlr_is_is_n_pls: ステップ n+1 における係数 f_XLR, K/W, [i, i]
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]
        l_rs_is_n: ステップ n からステップ n+1 における室 i に放射暖冷房設備の顕熱処理量（暖房を正・冷房を負とする）, W, [i, 1]
        theta_ot_is_n_pls: ステップ n+1 における室 i の作用温度, ℃

    Returns:
        ステップ n+1 における室 i の室温, degree C, [i, 1]

    Notes:
        式(2.6)

    """

    return np.dot(f_xot_is_is_n_pls, theta_ot_is_n_pls) - np.dot(f_xlr_is_is_n_pls, l_rs_is_n) - f_xc_is_n_pls


def get_f_brl_ot_is_is_n(f_brl_is_is_n, f_brm_is_is_n_pls, f_xlr_is_is_n_pls):
    """

    Args:
        f_brl_is_is_n: ステップ n における係数 f_BRL, -, [i, i]
        f_brm_is_is_n_pls: ステップ n+1 における係数 f_BRM, W/K, [i, i]
        f_xlr_is_is_n_pls: ステップ n+1 における係数 f_XLR, K/W, [i, i]

    Returns:
        ステップ n における係数 f_BRL,OT, -, [i, i]

    Notes:
        式(2.8)

    """

    return f_brl_is_is_n + np.dot(f_brm_is_is_n_pls, f_xlr_is_is_n_pls)


def get_f_xlr_is_is_n_pls(f_mrt_hum_is_js, f_wsb_js_is_n_pls, f_xot_is_is_n_pls, k_r_is_n):
    """

    Args:
        f_mrt_hum_is_js: 室 i の人体に対する境界 j の形態係数, -, [i, j]
        f_wsb_js_is_n_pls: ステップ n+1 における係数 f_WSB, K/W, [j, 1]
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]
        k_r_is_n: ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Returns:
        ステップ n+1 における係数 f_XLR, K/W, [i, i]

    Notes:
        式(2.9)

    """

    return np.dot(f_xot_is_is_n_pls, k_r_is_n * np.dot(f_mrt_hum_is_js, f_wsb_js_is_n_pls))


def get_f_brl_is_is_n(a_s_js, beta_is_n, f_wsb_js_is_n_pls, h_s_c_js, p_is_js):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        beta_is_n: ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]
        f_wsb_js_is_n_pls: ステップ n+1 における係数 f_WSB, K/W, [j, 1]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]

    Returns:
        ステップ n における係数 f_BRL, -, [i, i]

    Notes:
        式(2.10)

    """

    return np.dot(p_is_js, f_wsb_js_is_n_pls * h_s_c_js * a_s_js) + v_diag(beta_is_n)


def get_f_wsb_js_is_n_pls(f_flb_js_is_n_pls, f_ax_js_js):
    """

    Args:
        f_flb_js_is_n_pls: ステップ n+1 における係数 f_FLB, K/W, [j, i]
        f_ax_js_js: 係数 f_AX, -, [j, j]

    Returns:
        ステップ n+1 における係数 f_WSB, K/W, [j, i]

    Notes:
        式(2.11)

    """

    return np.linalg.solve(f_ax_js_js, f_flb_js_is_n_pls)


def get_beta_is_n(
        beta_c_is: np.ndarray,
        beta_h_is: np.ndarray,
        operation_mode_is_n: np.ndarray
):
    """

    Args:
        beta_c_is: 室 i の放射冷房設備の対流成分比率, -, [i, 1]
        beta_h_is: 室 i の放射暖房設備の対流成分比率, -, [i, 1]
        operation_mode_is_n: ステップnにおける室iの運転モード, [i, 1]

    Returns:
        ステップ n からステップ n+1 における室 i の放射暖冷房設備の対流成分比率, -, [i, 1]

    Notes:
        式(2.13)
    """

    return beta_h_is * (operation_mode_is_n == OperationMode.HEATING)\
        + beta_c_is * (operation_mode_is_n == OperationMode.COOLING)


def get_f_flr_js_is_n(
        f_flr_c_js_is: np.ndarray,
        f_flr_h_js_is: np.ndarray,
        operation_mode_is_n: np.ndarray
):
    """

    Args:
        f_flr_c_js_is: 室 i の放射冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        f_flr_h_js_is: 室 i の放射暖房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]
        operation_mode_is_n: ステップnにおける室iの運転モード, [i, 1]

    Returns:
        ステップ n からステップ n+1 における室 i の放射暖冷房設備の放熱量の放射成分に対する境界 j の室内側表面の吸収比率, -, [j, i]

    Notes:
        式(2.14)

    """

    return f_flr_h_js_is * (operation_mode_is_n == OperationMode.HEATING).flatten() \
        + f_flr_c_js_is * (operation_mode_is_n == OperationMode.COOLING).flatten()


def get_theta_r_ot_ntr_is_n_pls(
        f_brc_ot_non_nv_is_n_pls,
        f_brc_ot_nv_is_n_pls,
        f_brm_ot_non_nv_is_is_n_pls,
        f_brm_ot_nv_is_is_n_pls
):
    """

    Args:
        f_brc_ot_non_nv_is_n_pls: ステップ n+1 における自然風の利用なし時の係数 f_BRC,OT, W, [i, 1]
        f_brc_ot_nv_is_n_pls: ステップ n+1 における自然風の利用時の係数 f_BRC,OT, W, [i, 1]
        f_brm_ot_non_nv_is_is_n_pls: ステップ n+1 における自然風の利用なし時の係数 f_BRM,OT, W/K, [i, 1]
        f_brm_ot_nv_is_is_n_pls: ステップ n+1 における自然風の利用時の係数 f_BRM,OT, W/K, [i, 1]


    Returns:
        ステップn+1における自然風非利用時の室iの自然作用温度, degree C, [i, 1]
        ステップn+1における自然風利用時の室iの自然作用温度, degree C, [i, 1]

    Notes:
        式(2.16)
    """
    theta_r_ot_ntr_non_nv_is_n_pls = np.linalg.solve(f_brm_ot_non_nv_is_is_n_pls, f_brc_ot_non_nv_is_n_pls)
    theta_r_ot_ntr_nv_is_n_pls = np.linalg.solve(f_brm_ot_nv_is_is_n_pls, f_brc_ot_nv_is_n_pls)
    return theta_r_ot_ntr_non_nv_is_n_pls, theta_r_ot_ntr_nv_is_n_pls


def get_f_brc_ot_is_n_pls(
        f_xc_is_n_pls,
        f_brc_non_nv_is_n_pls,
        f_brc_nv_is_n_pls,
        f_brm_non_nv_is_is_n_pls,
        f_brm_nv_is_is_n_pls
):
    """

    Args:
        f_xc_is_n_pls: ステップ n+1 における係数 f_XC, degree C, [i, 1]
        f_brc_non_nv_is_n_pls: ステップn+1における自然風非利用時の係数f_BRC,OT, W, [i,1]
        f_brc_nv_is_n_pls: ステップn+1における自然風利用時の係数f_BRC,OT, W, [i,1]
        f_brm_non_nv_is_is_n_pls: ステップn+1における自然風非利用時の係数f_BRM,OT, W, [i,i]
        f_brm_nv_is_is_n_pls: ステップn+1における自然風利用時の係数f_BRM,OT, W, [i,i]
    Returns:
        ステップn+1における自然風非利用時の係数f_BRC,OT, W, [i, 1]
        ステップn+1における自然風利用時の係数f_BRC,OT, W, [i, 1]

    Notes:
        式(2.17)
    """

    f_brc_ot_non_nv_is_n_pls = f_brc_non_nv_is_n_pls + np.dot(f_brm_non_nv_is_is_n_pls, f_xc_is_n_pls)
    f_brc_ot_nv_is_n_pls = f_brc_nv_is_n_pls + np.dot(f_brm_nv_is_is_n_pls, f_xc_is_n_pls)
    return f_brc_ot_non_nv_is_n_pls, f_brc_ot_nv_is_n_pls


def get_f_brm_ot_is_is_n_pls(f_xot_is_is_n_pls, f_brm_non_nv_is_is_n_pls, f_brm_nv_is_is_n_pls):
    """

    Args:
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]
        f_brm_non_nv_is_is_n_pls: ステップ n+1 における自然風非利用時の係数 f_BRM, W/K, [i, i]
        f_brm_nv_is_is_n_pls: ステップ n+1 における自然風利用時の係数 f_BRM, W/K, [i, i]


    Returns:
        ステップn+1における自然風非利用時の係数f_BRM,OT, W/K, [i, 1]
        ステップn+1における自然風利用時の係数f_BRM,OT, W/K, [i, 1]

    Notes:
        式(2.18)
    """
    return np.dot(f_brm_non_nv_is_is_n_pls, f_xot_is_is_n_pls), np.dot(f_brm_nv_is_is_n_pls, f_xot_is_is_n_pls)


def get_f_xc_is_n_pls(f_mrt_hum_is_js, f_wsc_js_n_pls, f_wsv_js_n_pls, f_xot_is_is_n_pls, k_r_is_n):
    """

    Args:
        f_mrt_hum_is_js: 室 i の人体に対する境界 j の形態係数, -, [i, j]
        f_wsc_js_n_pls: ステップ n+1 における係数 f_WSC, degree C, [j, 1]
        f_wsv_js_n_pls: ステップ n+1 における係数 f_WSV, degree C, [j, 1]
        f_xot_is_is_n_pls: ステップ n+1 における係数 f_XOT, -, [i, i]
        k_r_is_n: ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Returns:
        ステップ n+1 における係数 f_XC, degree C, [i, 1]

    Notes:
        式(2.19)
    """

    return np.dot(f_xot_is_is_n_pls, k_r_is_n * np.dot(f_mrt_hum_is_js, (f_wsc_js_n_pls + f_wsv_js_n_pls)))


def get_f_xot_is_is_n_pls(f_mrt_hum_is_js, f_wsr_js_is, k_c_is_n, k_r_is_n):
    """

    Args:
        f_mrt_hum_is_js: 室 i の人体に対する境界 j の形態係数, -, [i, j]
        f_wsr_js_is: 係数 f_WSR, - [j, i]
        k_c_is_n: ステップ n における室 i の人体表面の対流熱伝達率が総合熱伝達率に占める割合, -, [i, 1]
        k_r_is_n: ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Returns:
        ステップ n+1 における係数 f_XOT, -, [i, i]

    Notes:
        式(2.20)
    """

    return np.linalg.inv(v_diag(k_c_is_n) + k_r_is_n * np.dot(f_mrt_hum_is_js, f_wsr_js_is))


def get_k_c_is_n(n_rm: int) -> np.ndarray:
    """

    Args:
        室の数
    Returns:
        ステップ n における室 i の人体表面の対流熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Notes:
        式(2.21)
    """
    # TODO: 仕様書を修正する必要あり
    return np.full((n_rm, 1), 0.5)


def get_k_r_is_n(n_rm: int) -> np.ndarray:
    """

    Args:
        室の数
    Returns:
        ステップ n における室 i の人体表面の放射熱伝達率が総合熱伝達率に占める割合, -, [i, 1]

    Notes:
        式(2.22)
    """
    # TODO: 仕様書を修正する必要あり
    return np.full((n_rm, 1), 0.5)


def get_f_brm_is_is_n_pls(
        a_s_js, c_a: float, v_rm_is, c_sh_frt_is, delta_t, f_wsr_js_is, g_sh_frt_is, h_s_c_js, p_is_js,
        p_js_is, rho_a, v_vent_int_is_is_n, v_vent_out_non_nv_is_n,
        v_vent_ntr_set_is
):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        c_a: 空気の比熱, J/(kg K)
        v_rm_is: 室 i の容積, m3, [i, 1]
        c_sh_frt_is: 室 i の備品等の熱容量, J/K, [i, 1]
        delta_t: 1ステップの時間間隔, s
        f_wsr_js_is: 係数 f_WSR, - [j, i]
        g_sh_frt_is: 室 i の備品等と空気間の熱コンダクタンス, W/K, [i, 1]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]
        p_js_is: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [j, i]
        rho_a: 空気の密度, kg/m3
        v_vent_int_is_is_n: ステップ n から ステップ n+1 における室 i* から室 i への室間の空気移動量（流出換気量を含む）, m3/s
        v_vent_out_non_nv_is_n: ステップnからステップn+1 における室iの換気・すきま風による外気の流入量, m3/s
        v_vent_ntr_set_is: ステップnからステップn+1における室iの自然風の利用による外気の流入量, m3/s

    Returns:
        ステップn+1における自然風非利用時の係数f_BRM, W/K, [i, i]
        ステップn+1における自然風利用時の係数f_BRM, W/K, [i, i]

    Notes:
        式(2.23)
    """
    f_brm_non_ntr_is_is_n_pls = v_diag(v_rm_is * rho_a * c_a / delta_t) \
        + np.dot(p_is_js, (p_js_is - f_wsr_js_is) * a_s_js * h_s_c_js) \
        + v_diag(c_sh_frt_is * g_sh_frt_is / (c_sh_frt_is + g_sh_frt_is * delta_t)) \
        + c_a * rho_a * (v_diag(v_vent_out_non_nv_is_n) - v_vent_int_is_is_n)
    f_brm_ntr_is_is_n_pls = f_brm_non_ntr_is_is_n_pls + c_a * rho_a * v_diag(v_vent_ntr_set_is)
    return f_brm_non_ntr_is_is_n_pls, f_brm_ntr_is_is_n_pls


def get_f_brc_is_n_pls(
        a_s_js, c_a, v_rm_is, c_sh_frt_is, delta_t, f_wsc_js_n_pls, f_wsv_js_n_pls, g_sh_frt_is,
        h_s_c_js, p_is_js, q_gen_is_n, q_hum_is_n, q_sol_frt_is_n, rho_a, theta_frt_is_n,
        theta_o_n_pls, theta_r_is_n, v_vent_out_non_nv_is_n, v_vent_ntr_is_n
):
    """

    Args:
        a_s_js: 境界 j の面積, m2, [j, 1]
        c_a: 空気の比熱, J/(kg K)
        v_rm_is: 室容量, m3, [i, 1]
        c_sh_frt_is: 室 i の備品等の熱容量, J/K, [i, 1]
        delta_t: 1ステップの時間間隔, s
        f_wsc_js_n_pls: ステップ n+1 における係数 f_WSC, degree C, [j, 1]
        f_wsv_js_n_pls: ステップ n+1 における係数 f_WSV, degree C, [j, 1]
        g_sh_frt_is: 室 i の備品等と空気間の熱コンダクタンス, W/K, [i, 1]
        h_s_c_js: 境界 j の室内側対流熱伝達率, W/(m2 K), [j, 1]
        p_is_js: 室 i と境界 j の接続に関する係数（境界 j が室 i に接している場合は 1 とし、それ以外の場合は 0 とする。）, -, [i, j]
        q_gen_is_n: ステップ n からステップ n+1 における室 i の人体発熱を除く内部発熱, W, [i, 1]
        q_hum_is_n: ステップ n からステップ n+1 における室 i の人体発熱, W, [i, 1]
        q_sol_frt_is_n: ステップ n からステップ n+1 における室 i に設置された備品等による透過日射吸収熱量時間平均値, W, [i, 1]
        rho_a: 空気の密度, kg/m3
        theta_frt_is_n: ステップ n における室 i の備品等の温度, degree C, [i, 1]
        theta_o_n_pls: ステップ n+1 における外気温度, ℃
        theta_r_is_n: ステップ n における室 i の温度, ℃
        v_vent_out_non_nv_is_n: ステップnからステップn+1における室iの換気・すきま風による外気の流入量, m3/s
        v_vent_ntr_is_n: ステップnからステップn+1における室iの自然風の利用による外気の流入量, m3/s
    Returns:
        ステップn+1における係数 f_BRC,OT,non-ntr, W, [i, 1]
        ステップn+1における係数　f_BRC,OT,ntr, W, [i, 1]

    Notes:
        式(2.24)
    """

    f_brc_non_ntr_is_n_pls = v_rm_is * c_a * rho_a / delta_t * theta_r_is_n \
                             + np.dot(p_is_js, h_s_c_js * a_s_js * (f_wsc_js_n_pls + f_wsv_js_n_pls)) \
                             + c_a * rho_a * v_vent_out_non_nv_is_n * theta_o_n_pls \
                             + q_gen_is_n + q_hum_is_n \
                             + g_sh_frt_is * (c_sh_frt_is * theta_frt_is_n + q_sol_frt_is_n * delta_t) / (c_sh_frt_is + delta_t * g_sh_frt_is)

    f_brc_ntr_is_n_pls = f_brc_non_ntr_is_n_pls + c_a * rho_a * v_vent_ntr_is_n * theta_o_n_pls

    return f_brc_non_ntr_is_n_pls, f_brc_ntr_is_n_pls


def get_v_vent_out_non_ntr_is_n(v_leak_is_n, v_vent_mec_is_n):
    """

    Args:
        v_leak_is_n: ステップ n からステップ n+1 における室 i のすきま風量, m3/s, [i, 1]
        v_vent_mec_is_n: ステップ n からステップ n+1 における室 i の機械換気量（全般換気量と局所換気量の合計値）, m3/s, [i, 1]

    Returns:
        ステップnからステップn+1における室iの換気・すきま風の利用による外気の流入量, m3/s

    Notes:
        式(2.25)
    """

    return v_leak_is_n + v_vent_mec_is_n


def get_f_wsv_js_n_pls(f_cvl_js_n_pls, f_ax_js_js):
    """

    Args:
        f_cvl_js_n_pls: ステップ n+1 における係数 f_CVL, degree C, [j, 1]
        f_ax_js_js: 係数 f_AX, -, [j, j]

    Returns:
        ステップ n+1 の係数 f_WSV, degree C, [j, 1]

    Notes:
        式(2.27)
    """

    return np.linalg.solve(f_ax_js_js, f_cvl_js_n_pls)


def get_q_hum_is_n(n_hum_is_n, q_hum_psn_is_n):
    """

    Args:
        n_hum_is_n: ステップ n からステップ n+1 における室 i の在室人数, -, [i, 1]
        q_hum_psn_is_n: ステップ n からステップ n+1 における室 i の1人あたりの人体発熱, W, [i, 1]

    Returns:
        ステップ n からステップ n+1 における室 i の人体発熱, W, [i, 1]

    Notes:
        式(2.31)
    """

    return q_hum_psn_is_n * n_hum_is_n


def get_theta_s_rear_js_n(
        k_s_er_js_js: np.ndarray,
        theta_er_js_n: np.ndarray,
        k_s_eo_js: np.ndarray,
        theta_eo_js_n: np.ndarray,
        k_s_r_js_is: np.ndarray,
        theta_r_is_n: np.ndarray
):
    """

    Args:
        k_s_er_js_js: 境界 j の裏面温度に境界　j* の等価温度が与える影響, -, [j*, j]
        theta_er_js_n: ステップ n における境界 j の等価温度, degree C, [j, 1]
        k_s_eo_js: 境界 j の裏面温度に境界 j の相当外気温度が与える影響（温度差係数）, -, [j, 1]
        theta_eo_js_n: ステップ n の境界 j における相当外気温度, ℃, [j, n]
        k_s_r_js_is: 境界 j の裏面温度に境界 j の裏面が接する室 i の空気温度が与える影響, -, [j, i]
        theta_r_is_n: ステップ n における室 i の空気温度, degree C, [i, 1]

    Returns:
        ステップ n における境界 j の裏面温度, degree C, [j, 1]

    Notes:
        式(2.32)
    """

    return np.dot(k_s_er_js_js, theta_er_js_n) + k_s_eo_js * theta_eo_js_n + np.dot(k_s_r_js_is, theta_r_is_n)

# endregion

