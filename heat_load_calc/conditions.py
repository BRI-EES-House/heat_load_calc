import numpy as np
from dataclasses import dataclass

from heat_load_calc.operation_mode import OperationMode
from heat_load_calc import psychrometrics as psy
from heat_load_calc.boundary_component import BoundaryComponentsStatus


@dataclass
class GroundConditions:

    # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
    q_srf_js_n: np.ndarray

    # ステップnの境界jにおける状態量, [J, 1]
    bcs_js_n: BoundaryComponentsStatus

    @classmethod
    def initialize(cls, n_grounds: int):

        # ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
        # 初期値を0.0℃とする。
        theta_dsh_srf_a_js_ms_n0 = np.full((n_grounds, 12), 0.0)

        # ステップnの統合された境界j*における指数項mの貫流応答の項別成分, degree C, [j*, 12]
        # 初期値を0.0℃とする。
        theta_dsh_srf_t_js_ms_n0 = np.full((n_grounds, 12), 0.0)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
        # 初期値を0.0W/m2とする。
        q_srf_js_n0 = np.zeros((n_grounds, 1), dtype=float)

        bcs_js_n = BoundaryComponentsStatus.initialize(n_b=n_grounds)

        return GroundConditions(
            q_srf_js_n=q_srf_js_n0,
            bcs_js_n=bcs_js_n
        )


@dataclass
class Conditions:

    # ステップnにおける室iの運転状態, [i, 1]
    # 列挙体 OperationMode で表される。
    #     COOLING ： 冷房
    #     HEATING : 暖房
    #     STOP_OPEN : 暖房・冷房停止で窓「開」
    #     STOP_CLOSE : 暖房・冷房停止で窓「閉」
    operation_mode_is_n: np.ndarray

    # ステップnにおける室iの空気温度, degree C, [i, 1]
    theta_r_is_n: np.ndarray

    # ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]
    theta_mrt_hum_is_n: np.ndarray

    # ステップnにおける室iの絶対湿度, kg/kgDA, [i, 1]
    x_r_is_n: np.ndarray

    # ステップnの境界jにおける項別公比法の指数項mの吸熱応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_s_a_js_ms_n: np.ndarray

    # ステップnの境界jにおける項別公比法の指数項mの貫流応答の項別成分, degree C, [j, m] (m=12)
    theta_dsh_s_t_js_ms_n: np.ndarray

    # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
    q_s_js_n: np.ndarray

    # ステップnの室iにおける家具の温度, degree C, [i, 1]
    theta_frt_is_n: np.ndarray

    # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i, 1]
    x_frt_is_n: np.ndarray

    # [i, 1]
    theta_ei_js_n: np.ndarray

    # Boundary component status
    bcs_n: GroundConditions



def initialize_conditions(n_r: int, n_b: int, is_ground: np.array, gc_n: GroundConditions):
    """Initialize the whole conditions and take over the ground conditions to the whole conditions

    Args:
        n_r: number of room
        n_b: number of boundary
        is_ground: is the boundary ground ?, [J]
        gc_n: Ground Conditions

    Returns:
        initialized conditions
    """

    # 空間iの数
    total_number_of_spaces = n_r

    # 統合された境界j*の数
    total_number_of_bdry = n_b

    # ステップnにおける室iの運転状態, [i, 1]
    # 初期値を暖房・冷房停止で窓「閉」とする。
    operation_mode_is_n = np.full((total_number_of_spaces, 1), OperationMode.STOP_CLOSE)

    # ステップnにおける室iの空気温度, degree C, [i, 1]
    # 初期値を15℃とする。
    theta_r_is_n = np.full((total_number_of_spaces, 1), 15.0)

    # ステップnにおける室iの在室者の平均放射温度, degree C, [i, 1]
    # 初期値を15℃と設定する。
    theta_mrt_hum_is_n = np.full((total_number_of_spaces, 1), 15.0)

    # ステップnにおける室iの絶対湿度, kg/kgDA, [i, 1]
    # 初期値を空気温度20℃相対湿度40%の時の値とする。
    # x_r_is_n = np.full((total_number_of_spaces, 1), psy.get_x(psy.get_p_vs(theta=20.0) * 0.4))
    x_r_is_n = np.full((total_number_of_spaces, 1), psy.get_x(psy.get_p_vs(theta=20.0) * 0.4))

    # ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
    # 初期値を0.0℃とする。
    theta_dsh_srf_a_js_ms_n0 = np.full((total_number_of_bdry, 12), 0.0)

    # ステップnの統合された境界j*における指数項mの貫流応答の項別成分, degree C, [j*, 12]
    # 初期値を0.0℃とする。
    theta_dsh_srf_t_js_ms_n0 = np.full((total_number_of_bdry, 12), 0.0)

    # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）, W/m2, [j, 1]
    # 初期値を0.0W/m2とする。
    q_srf_jstrs_n = np.zeros((total_number_of_bdry, 1), dtype=float)

    # ステップnの室iにおける家具の温度, degree C, [i]
    # 初期値を15℃とする。
    theta_frt_is_n = np.full(total_number_of_spaces, 15.0)

    # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i, 1]
    # 初期値を空気温度20℃相対湿度40%の時の値とする。
    x_frt_is_n = np.full((total_number_of_spaces, 1), psy.get_x(psy.get_p_vs(theta=20.0) * 0.4))

    theta_dsh_srf_a_js_ms_n0[is_ground, :] = gc_n.bcs_js_n.theta_dsh_s_a_js_ms

    q_srf_jstrs_n[is_ground, :] = gc_n.q_srf_js_n

    return Conditions(
        operation_mode_is_n=operation_mode_is_n,
        theta_r_is_n=theta_r_is_n,
        theta_mrt_hum_is_n=theta_mrt_hum_is_n,
        x_r_is_n=x_r_is_n,
        theta_dsh_s_a_js_ms_n=theta_dsh_srf_a_js_ms_n0,
        theta_dsh_s_t_js_ms_n=theta_dsh_srf_t_js_ms_n0,
        q_s_js_n=q_srf_jstrs_n,
        theta_frt_is_n=theta_frt_is_n.reshape(-1, 1),
        x_frt_is_n=x_frt_is_n,
        theta_ei_js_n=np.full(total_number_of_bdry, 15.0).reshape(-1, 1),
        bcs_n=BoundaryComponentsStatus(theta_dsh_s_t_js_ms=theta_dsh_srf_t_js_ms_n0, theta_dsh_s_a_js_ms=theta_dsh_srf_a_js_ms_n0)
    )




