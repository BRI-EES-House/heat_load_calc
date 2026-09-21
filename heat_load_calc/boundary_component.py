from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
import numpy as np


from heat_load_calc.input_models.input_boundary import (
    InputBoundary,
    InputBoundaryInternal,
    InputBoundaryExternalGeneralPart,
    InputBoundaryExternalTransparentPart,
    InputBoundaryExternalOpaquePart,
    InputBoundaryGround
)
from heat_load_calc.response_factor import ResponseFactor

@dataclass
class BoundaryComponent(ABC):

    ...


@dataclass
class BoundaryComponentResponseFactor(BoundaryComponent):

    rf: ResponseFactor
    f_fi: float
    f_fo: float

    @classmethod
    def create(cls, rf: ResponseFactor, h_s: float):

        f_fi = rf.phi_a0_js * h_s / (1 + rf.phi_a0_js * h_s)
        f_fo = rf.phi_t0_js / (1 + rf.phi_a0_js * h_s)  

        return BoundaryComponentResponseFactor(
            rf=rf,
            f_fi=f_fi,
            f_fo=f_fo
        )

    @classmethod
    def create_for_unsteady_not_ground(cls, cs, rs, r_o, h_s):

        rf = ResponseFactor.create_for_unsteady_not_ground(cs=cs, rs=rs, r_o=r_o)

        return cls.create(rf=rf, h_s=h_s)
    
    @classmethod
    def create_for_unsteady_ground(cls, cs, rs, h_s):

        rf = ResponseFactor.create_for_unsteady_ground(cs=cs, rs=rs)

        return cls.create(rf=rf, h_s=h_s)
    
    @classmethod
    def create_for_steady(cls, u_w, r_i, h_s):
        
        rf = ResponseFactor.create_for_steady(u_w=u_w, r_i=r_i)

        return cls.create(rf=rf, h_s=h_s)
    
    @property
    def r_total(self) -> float:

        return self.rf.r_total
    
    @property
    def rfa0(self) -> float:

        return self.rf.phi_a0_js
    
    @property
    def rft0(self) -> float:

        return self.rf.phi_t0_js

    def get_f_cf_j_n_pls(self, bcs_j_n_pls: list[BoundaryComponentStatus], h_s_j: float) -> float:
        """

        Args:
            bcs_j_n_pls: 境界 j のBoundaryComponentStatus
            h_s_j: 境界 j の表面熱伝達率, W/m2K

        Returns:
            ステップ n+1 における係数 f_CF, degree C, [J, 1]
        Notes:
            式(2.28)
        """

        return (sum(bcs_j_n_pls.theta_dsh_s_a_j_ms) + sum(bcs_j_n_pls.theta_dsh_s_t_j_ms))/(1 + self.rf.phi_a0_js * h_s_j)


@dataclass
class BoundaryComponentStatus:

    theta_dsh_s_t_j_ms: np.ndarray

    theta_dsh_s_a_j_ms: np.ndarray

    @classmethod
    def initialize(cls):
        """initialize status

        Returns:
            BoundaryComponentStatus
        """

        return BoundaryComponentStatus(
            theta_dsh_s_t_j_ms=np.full((12), 0.0),
            theta_dsh_s_a_j_ms=np.full((12), 0.0)
        )


@dataclass
class BoundaryComponents:

    # initial term of heat absorption response factor, m2K/W, [J, 1]
    phi_a0_js: np.ndarray

    # initial term of m th component of heat absorption response factor
    # with common ratio method per term
    # m2K/W, [J, M]
    phi_a1_js_ms: np.ndarray

    # initial term of heat transmission response factor, -, [J, 1]
    phi_t0_js: np.ndarray

    # initial term of m th component of heat transmission response factor
    # with common ratio method per term
    # -, [J, M]
    phi_t1_js_ms: np.ndarray

    # common ratio of the m th term, [J, M]
    r_js_ms: np.ndarray

    r_total_js: np.ndarray

    f_fi_js: np.ndarray

    f_fo_js: np.ndarray

    bcomplist: list[BoundaryComponentResponseFactor]

    @classmethod
    def create(cls, bcomplist: list[BoundaryComponentResponseFactor]):

        if len(bcomplist) == 0:

            phi_a0_js = np.zeros(shape=(0,1))
            phi_a1_js_ms = np.zeros(shape=(0,12))
            phi_t0_js = np.zeros(shape=(0,1))
            phi_t1_js_ms = np.zeros(shape=(0,12))
            r_js_ms = np.zeros(shape=(0,12))
            r_total_js = np.zeros(shape=(0,1))
            f_fi_js = np.zeros(shape=(0,1))
            f_fo_js = np.zeros(shape=(0,1))
        
        else:

            phi_a0_js = np.array([bcomp.rf.phi_a0_js for bcomp in bcomplist]).reshape(-1, 1)
            phi_a1_js_ms = np.array([bcomp.rf.phi_a1_js_ms for bcomp in bcomplist])
            phi_t0_js = np.array([bcomp.rf.phi_t0_js for bcomp in bcomplist]).reshape(-1, 1)
            phi_t1_js_ms = np.array([bcomp.rf.phi_t1_js_ms for bcomp in bcomplist])
            r_js_ms = np.array([bcomp.rf.r_js_ms for bcomp in bcomplist])
            r_total_js = np.array([bcomp.rf.r_total for bcomp in bcomplist]).reshape(-1, 1)
            f_fi_js = np.array([bcomp.f_fi for bcomp in bcomplist]).reshape(-1, 1)
            f_fo_js = np.array([bcomp.f_fo for bcomp in bcomplist]).reshape(-1, 1)

        return BoundaryComponents(
            phi_a0_js=phi_a0_js,
            phi_a1_js_ms=phi_a1_js_ms,
            phi_t0_js=phi_t0_js,
            phi_t1_js_ms=phi_t1_js_ms,
            r_js_ms=r_js_ms,
            r_total_js=r_total_js,
            f_fi_js=f_fi_js,
            f_fo_js=f_fo_js,
            bcomplist=bcomplist
        )

    def _get_next_boundary_components_status(
            self,
            bcs_js_n: list[BoundaryComponentStatus],
            theta_rear_js_n: np.ndarray,
            q_s_js_n: np.ndarray
    ):

        n_j = len(theta_rear_js_n)

        theta_dsh_srf_t_js_ms_n_pls = np.zeros((n_j, 12))
        theta_dsh_srf_a_js_ms_n_pls = np.zeros((n_j, 12))

        for j in range(n_j):

            bcs_j_n_pls = bcs_js_n[j]

            #Args:
            #    theta_dsh_srf_t_js_ms_n: ステップ n における境界 j の項別公比法の指数項 m の貫流応答の項別成分, degree C, [j, m]
            #    theta_rear_js_n: ステップ n における境界 j の裏面温度, degree C, [j, 1]
            #Returns:
            #    ステップ n+1 における境界 j の項別公比法の指数項 m の貫流応答の項別成分, degree C, [j, m]
            #Notes:
            #    式(2.30)
            theta_dsh_srf_t_js_ms_n_pls[j,:] = self.phi_t1_js_ms[j, :] * theta_rear_js_n[j] + self.r_js_ms[j, :] * bcs_j_n_pls.theta_dsh_s_t_j_ms
            #Args:
            #    phi_a1_js_ms: 境界 j の項別公比法の指数項 m の吸熱応答係数, m2 K/W, [j, m]
            #    q_s_js_n: ステップ n における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
            #    r_js_ms: 境界 j の項別公比法の指数項 m の公比, -, [j, m]
            #    theta_dsh_srf_a_js_ms_n: ステップ n における境界 j の項別公比法の指数項 m の吸熱応答の項別成分, degree C, [j, m]
            #Returns:
            #    ステップ n+1 における境界 j の項別公比法の指数項 m の吸熱応答の項別成分, degree C, [j, m]
            #Notes:
            #    式(2.29)
            theta_dsh_srf_a_js_ms_n_pls[j,:] = self.phi_a1_js_ms[j, :] * q_s_js_n[j] + self.r_js_ms[j, :] * bcs_j_n_pls.theta_dsh_s_a_j_ms
        
        return [BoundaryComponentStatus(theta_dsh_s_t_j_ms=theta_dsh_srf_t_js_ms_n_pls[j, :], theta_dsh_s_a_j_ms=theta_dsh_srf_a_js_ms_n_pls[j, :]) for j in range(n_j)]
    
        
    def get_wall_steady_state_status(self, q_srf_js_n, theta_rear_js_n):

        theta_dsh_s_a_js_ms_n = q_srf_js_n * self.phi_a1_js_ms / (1.0 - self.r_js_ms)
        theta_dsh_s_t_js_ms_n = theta_rear_js_n * self.phi_t1_js_ms / (1.0 - self.r_js_ms)

        return [BoundaryComponentStatus(theta_dsh_s_t_j_ms=theta_dsh_s_t_js_ms_n[j, :], theta_dsh_s_a_j_ms=theta_dsh_s_a_js_ms_n[j, :]) for j in range(theta_dsh_s_t_js_ms_n.shape[0])]
