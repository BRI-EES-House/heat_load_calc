from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from typing import cast


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

    @property
    @abstractmethod
    def f_fi(self) -> float:
        pass

    @property
    @abstractmethod
    def f_fo(self) -> float:
        pass

    @property
    @abstractmethod
    def r_total(self) -> float:
        pass

    @abstractmethod
    def get_f_cf_j_n_pls(self, bcs_j_n_pls: BoundaryComponentStatus, h_s_j: float) -> float:
        pass

    @abstractmethod
    def get_bcs_j_steady_state(self, q_srf_j_n: float, theta_rear_j_n: float) -> BoundaryComponentStatus:
        pass

    @abstractmethod
    def get_bcs_j_n_pls(self, bcs_j_n: BoundaryComponentStatus, theta_rear_j_n: float, q_s_j_n: float) -> BoundaryComponentStatus:
        pass


@dataclass
class BoundaryComponentResponseFactor(BoundaryComponent):

    _rf: ResponseFactor
    _f_fi: float
    _f_fo: float

    @classmethod
    def create(cls, rf: ResponseFactor, h_s: float):

        f_fi = rf.phi_a0_js * h_s / (1 + rf.phi_a0_js * h_s)
        f_fo = rf.phi_t0_js / (1 + rf.phi_a0_js * h_s)  

        return BoundaryComponentResponseFactor(
            _rf=rf,
            _f_fi=f_fi,
            _f_fo=f_fo
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
    def f_fi(self) -> float:
        return self._f_fi

    @property
    def f_fo(self) -> float:
        return self._f_fo

    @property
    def r_total(self) -> float:

        return self._rf.r_total
    
    def get_f_cf_j_n_pls(self, bcs_j_n_pls: BoundaryComponentStatus, h_s_j: float) -> float:
        """

        Args:
            bcs_j_n_pls: 境界 j のBoundaryComponentStatus
            h_s_j: 境界 j の表面熱伝達率, W/m2K

        Returns:
            ステップ n+1 における係数 f_CF, degree C, [J, 1]
        Notes:
            式(2.28)
        """

        bcs_j_n_pls = cast(BoundaryComponentStatusResponseFactor, bcs_j_n_pls)

        return (sum(bcs_j_n_pls.theta_dsh_s_a_j_ms) + sum(bcs_j_n_pls.theta_dsh_s_t_j_ms))/(1 + self._rf.phi_a0_js * h_s_j)

    def get_bcs_j_steady_state(self, q_srf_j_n: float, theta_rear_j_n: float) -> BoundaryComponentStatus:

        return BoundaryComponentStatusResponseFactor(
            theta_dsh_s_t_j_ms=theta_rear_j_n * self._rf.phi_t1_js_ms / (1.0 - self._rf.r_js_ms),
            theta_dsh_s_a_j_ms=q_srf_j_n * self._rf.phi_a1_js_ms / (1.0 - self._rf.r_js_ms)
        )

    def get_bcs_j_n_pls(self, bcs_j_n: BoundaryComponentStatus, theta_rear_j_n: float, q_s_j_n: float) -> BoundaryComponentStatus:
        """

        Args:
            bcs_j_n: 境界 j のBoundaryComponentStatus
            theta_rear_j_n: ステップ n における境界 j の裏面温度, degree C
            q_s_j_n: ステップ n における境界 j の表面熱流（壁体吸熱を正とする）, W/m2

        Returns:
            ステップ n+1 における境界 j のBoundaryComponentStatus
        Notes:
            式(2.29)と式(2.30)
        """

        bcs_j_n = cast(BoundaryComponentStatusResponseFactor, bcs_j_n)

        return BoundaryComponentStatusResponseFactor(
            theta_dsh_s_t_j_ms=self._get_theta_dsh_srf_t_j_ms_n_pls(bcs_j_n=bcs_j_n, theta_rear_j_n=theta_rear_j_n),
            theta_dsh_s_a_j_ms=self._get_theta_dsh_srf_a_j_ms_n_pls(bcs_j_n=bcs_j_n, q_s_j_n=q_s_j_n)
        )

    def _get_theta_dsh_srf_t_j_ms_n_pls(self, bcs_j_n: BoundaryComponentStatusResponseFactor, theta_rear_j_n: float) -> np.ndarray:
        """

        Args:
            bcs_j_n: 境界 j のBoundaryComponentStatus
            theta_rear_j_n: ステップ n における境界 j の裏面温度, degree C

        Returns:
            ステップ n+1 における境界 j の項別公比法の指数項 m の貫流応答の項別成分, degree C, [m]
        Notes:
            式(2.30)
        """

        return self._rf.phi_t1_js_ms * theta_rear_j_n + self._rf.r_js_ms * bcs_j_n.theta_dsh_s_t_j_ms

    def _get_theta_dsh_srf_a_j_ms_n_pls(self, bcs_j_n: BoundaryComponentStatusResponseFactor, q_s_j_n: float) -> np.ndarray:
        """

        Args:
            bcs_j_n: 境界 j のBoundaryComponentStatus
            q_s_j_n: ステップ n における境界 j の表面熱流（壁体吸熱を正とする）, W/m2

        Returns:
            ステップ n+1 における境界 j の項別公比法の指数項 m の吸熱応答の項別成分, degree C, [m]
        Notes:
            式(2.29)
        """

        return self._rf.phi_a1_js_ms * q_s_j_n + self._rf.r_js_ms * bcs_j_n.theta_dsh_s_a_j_ms


@dataclass
class BoundaryComponentStatus(ABC):

    pass


@dataclass
class BoundaryComponentStatusResponseFactor(BoundaryComponentStatus):

    theta_dsh_s_t_j_ms: np.ndarray

    theta_dsh_s_a_j_ms: np.ndarray

    @classmethod
    def initialize(cls):
        """initialize status

        Returns:
            BoundaryComponentStatus
        """

        return BoundaryComponentStatusResponseFactor(
            theta_dsh_s_t_j_ms=np.full((12), 0.0),
            theta_dsh_s_a_j_ms=np.full((12), 0.0)
        )


