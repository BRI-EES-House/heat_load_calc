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

    @classmethod
    def create_for_unsteady_not_ground(cls, cs, rs, r_o):

        rf = ResponseFactor.create_for_unsteady_not_ground(cs=cs, rs=rs, r_o=r_o)

        return BoundaryComponentResponseFactor(rf=rf)
    
    @classmethod
    def create_for_unsteady_ground(cls, cs, rs):

        rf = ResponseFactor.create_for_unsteady_ground(cs=cs, rs=rs)

        return BoundaryComponentResponseFactor(rf=rf)
    
    @classmethod
    def create_for_steady(cls, u_w, r_i):
        
        rf = ResponseFactor.create_for_steady(u_w=u_w, r_i=r_i)

        return BoundaryComponentResponseFactor(rf=rf)
    
    @property
    def r_total(self) -> float:

        return self.rf.r_total
    
    @property
    def rfa0(self) -> float:

        return self.rf.rfa0
    
    @property
    def rft0(self) -> float:

        return self.rf.rft0
    

@dataclass
class BoundaryComponentsStatus:

    theta_dsh_s_t_js_ms: np.ndarray

    theta_dsh_s_a_js_ms: np.ndarray

    @classmethod
    def initialize(cls, n_b: int):
        """initialize status

        Args:
            n_b: number of boundaries
        """

        return BoundaryComponentsStatus(
            theta_dsh_s_t_js_ms=np.full((n_b, 12), 0.0),
            theta_dsh_s_a_js_ms=np.full((n_b, 12), 0.0)
        )
    
    def take_over(self, is_ground: np.ndarray, bcs_ground_js: BoundaryComponentsStatus):
        
        theta_dsh_s_t_js_ms = self.theta_dsh_s_t_js_ms
        theta_dsh_s_a_js_ms = self.theta_dsh_s_a_js_ms

        theta_dsh_s_t_js_ms[is_ground, :] = bcs_ground_js.theta_dsh_s_t_js_ms
        theta_dsh_s_a_js_ms[is_ground, :] = bcs_ground_js.theta_dsh_s_a_js_ms

        return BoundaryComponentsStatus(
            theta_dsh_s_t_js_ms=theta_dsh_s_t_js_ms,
            theta_dsh_s_a_js_ms=theta_dsh_s_a_js_ms
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


    @classmethod
    def create(cls, bcomplist: list[BoundaryComponentResponseFactor]):

        if len(bcomplist) == 0:

            phi_a0_js = np.zeros(shape=(0,1))
            phi_a1_js_ms = np.zeros(shape=(0,12))
            phi_t0_js = np.zeros(shape=(0,1))
            phi_t1_js_ms = np.zeros(shape=(0,12))
            r_js_ms = np.zeros(shape=(0,12))
            r_total_js = np.zeros(shape=(0,1))
        
        else:

            phi_a0_js = np.array([bcomp.rf.rfa0 for bcomp in bcomplist]).reshape(-1, 1)
            phi_a1_js_ms = np.array([bcomp.rf.rfa1 for bcomp in bcomplist])
            phi_t0_js = np.array([bcomp.rf.rft0 for bcomp in bcomplist]).reshape(-1, 1)
            phi_t1_js_ms = np.array([bcomp.rf.rft1 for bcomp in bcomplist])
            r_js_ms = np.array([bcomp.rf.row for bcomp in bcomplist])
            r_total_js = np.array([bcomp.rf.r_total for bcomp in bcomplist]).reshape(-1, 1)

        return BoundaryComponents(
            phi_a0_js=phi_a0_js,
            phi_a1_js_ms=phi_a1_js_ms,
            phi_t0_js=phi_t0_js,
            phi_t1_js_ms=phi_t1_js_ms,
            r_js_ms=r_js_ms,
            r_total_js=r_total_js
        )

    def _get_next_boundary_components_status(
            self,
            bcs_js_n: BoundaryComponentsStatus,
            theta_rear_js_n: np.ndarray,
            q_s_js_n: np.ndarray
    ):
        
        theta_dsh_srf_t_js_ms_n_pls = self._get_theta_dsh_s_t_js_ms_n_pls(
            theta_dsh_srf_t_js_ms_n=bcs_js_n.theta_dsh_s_t_js_ms,
            theta_rear_js_n=theta_rear_js_n
        )

        theta_dsh_srf_a_js_ms_n_pls = self._get_theta_dsh_s_a_js_ms_n_pls(
            q_s_js_n=q_s_js_n,
            theta_dsh_srf_a_js_ms_n=bcs_js_n.theta_dsh_s_a_js_ms
        )

        return BoundaryComponentsStatus(
            theta_dsh_s_t_js_ms=theta_dsh_srf_t_js_ms_n_pls,
            theta_dsh_s_a_js_ms=theta_dsh_srf_a_js_ms_n_pls            
        )
        
    def _get_theta_dsh_s_t_js_ms_n_pls(self, theta_dsh_srf_t_js_ms_n, theta_rear_js_n):
        """

        Args:
            theta_dsh_srf_t_js_ms_n: ステップ n における境界 j の項別公比法の指数項 m の貫流応答の項別成分, degree C, [j, m]
            theta_rear_js_n: ステップ n における境界 j の裏面温度, degree C, [j, 1]

        Returns:
            ステップ n+1 における境界 j の項別公比法の指数項 m の貫流応答の項別成分, degree C, [j, m]

        Notes:
            式(2.30)
        """

        # theta_dsh_s_t_js_ms_n_pls = np.zeros_like(theta_dsh_srf_t_js_ms_n)

        # for j in range(theta_dsh_srf_t_js_ms_n.shape[0]):

        #     phi_t1_j_ms = phi_t1_js_ms[j]
        #     r_j_ms = r_js_ms[j]
        #     theta_dsh_srf_t_j_ms_n = theta_dsh_srf_t_js_ms_n[j]
        #     theta_rear_j_n = theta_rear_js_n[j]

        #     theta_dsh_s_t_j_ms_n_pls = phi_t1_j_ms * theta_rear_j_n + r_j_ms * theta_dsh_srf_t_j_ms_n

        #     theta_dsh_s_t_js_ms_n_pls[j] =theta_dsh_s_t_j_ms_n_pls

        # return theta_dsh_s_t_js_ms_n_pls
        return self.phi_t1_js_ms * theta_rear_js_n + self.r_js_ms * theta_dsh_srf_t_js_ms_n

    def _get_theta_dsh_s_a_js_ms_n_pls(self, q_s_js_n, theta_dsh_srf_a_js_ms_n):
        """

        Args:
            phi_a1_js_ms: 境界 j の項別公比法の指数項 m の吸熱応答係数, m2 K/W, [j, m]
            q_s_js_n: ステップ n における境界 j の表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
            r_js_ms: 境界 j の項別公比法の指数項 m の公比, -, [j, m]
            theta_dsh_srf_a_js_ms_n: ステップ n における境界 j の項別公比法の指数項 m の吸熱応答の項別成分, degree C, [j, m]

        Returns:
            ステップ n+1 における境界 j の項別公比法の指数項 m の吸熱応答の項別成分, degree C, [j, m]

        Notes:
            式(2.29)
        """

        # theta_dsh_s_a_js_ms_n_pls = np.zeros_like(theta_dsh_srf_a_js_ms_n)

        # for j in range(theta_dsh_srf_a_js_ms_n.shape[0]):

        #     phi_a1_j_ms = phi_a1_js_ms[j]
        #     q_s_j_n = q_s_js_n[j]
        #     r_j_ms = r_js_ms[j]
        #     theta_dsh_srf_a_j_ms_n = theta_dsh_srf_a_js_ms_n[j]

        #     theta_dsh_s_a_j_ms_n_pls = phi_a1_j_ms * q_s_j_n + r_j_ms * theta_dsh_srf_a_j_ms_n

        #     theta_dsh_s_a_js_ms_n_pls[j] = theta_dsh_s_a_j_ms_n_pls

        # return theta_dsh_s_a_js_ms_n_pls
        return self.phi_a1_js_ms * q_s_js_n + self.r_js_ms * theta_dsh_srf_a_js_ms_n

    def _get_f_cvl_js_n_pls(self, bcs_js_n_pls: BoundaryComponentsStatus):
        """

        Args:
            bcs_js_n_pls: BoundaryComponentsStatus

        Returns:
            ステップ n+1 における係数 f_CVL, degree C, [j, 1]
        Notes:
            式(2.28)
        """
        return np.sum(bcs_js_n_pls.theta_dsh_s_t_js_ms + bcs_js_n_pls.theta_dsh_s_a_js_ms, axis=1, keepdims=True)

    def get_wall_steady_state_status(self, q_srf_js_n, theta_rear_js_n):

        theta_dsh_s_a_js_ms_n = q_srf_js_n * self.phi_a1_js_ms / (1.0 - self.r_js_ms)
        theta_dsh_s_t_js_ms_n = theta_rear_js_n * self.phi_t1_js_ms / (1.0 - self.r_js_ms)

        return BoundaryComponentsStatus(
            theta_dsh_s_t_js_ms=theta_dsh_s_t_js_ms_n,
            theta_dsh_s_a_js_ms=theta_dsh_s_a_js_ms_n
        )


