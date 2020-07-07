import numpy as np

import heat_load_calc.x_07_inclined_surface_solar_radiation as x_07
import heat_load_calc.x_19_external_boundaries_direction as x_19
from heat_load_calc.initializer.boundary_type import BoundaryType

"""
付録9．	裏面相当温度
"""


def get_theta_o_sol_i_j_ns(boundary_i_j, theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, a_sun_ns, h_sun_ns):
    """
    相当外気温度を計算する。

    Args:
        boundary_i_j: 室iの境界j
        theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
        i_dn_ns: ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
        i_sky_ns: ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
        r_n_ns: ステップnにおける夜間放射量, W/m2, [8760 * 4]
        a_sun_ns: ステップnにおける太陽高度, deg, [8760*4]
        h_sun_ns: ステップnにおける太陽方位, deg, [8760*4]

    Returns:
        室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
    """

    # 間仕切りの場合
    if boundary_i_j.boundary_type == BoundaryType.Internal:

        # この値は使用しないのでNoneでもよいはず
        # 集約化する際にNoneだと変な挙動を示すかも知れないのでとりあえずゼロにしておく。
        return np.zeros(24 * 365 * 4)

    # 一般部位・透明な開口部・不透明な開口部の場合
    elif (boundary_i_j.boundary_type == BoundaryType.ExternalGeneralPart) \
            or (boundary_i_j.boundary_type == BoundaryType.ExternalOpaquePart) \
            or (boundary_i_j.boundary_type == BoundaryType.ExternalTransparentPart):

        # 日射が当たる場合
        if boundary_i_j.is_sun_striked_outside:

            # 室iの境界jの傾斜面の方位角, rad
            # 室iの境界jの傾斜面の傾斜角, rad
            w_alpha_i_j, w_beta_i_j = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=boundary_i_j.direction)

            # ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2, [8760 * 4]
            r_n_is_i_j_ns = x_07.get_r_n_is_i_j_ns(r_n_ns=r_n_ns, w_beta_i_j=w_beta_i_j)

            # 一般部位・不透明な部位の場合
            if (boundary_i_j.boundary_type == BoundaryType.ExternalGeneralPart) \
                    or (boundary_i_j.boundary_type == BoundaryType.ExternalOpaquePart):

                # ステップnにおける室iの境界jにおける傾斜面の日射量のうち直達成分, W/m2K [8760*4]
                # ステップnにおける室iの境界jにおける傾斜面の日射量のうち天空成分, W/m2K [8760*4]
                # ステップnにおける室iの境界jにおける傾斜面の日射量のうち地盤反射成分, W/m2K [8760*4]
                i_is_d_i_j_ns, i_is_sky_i_j_ns, i_is_ref_i_j_ns = x_07.get_i_is_i_j_ns(
                    i_dn_ns=i_dn_ns, i_sky_ns=i_sky_ns, h_sun_ns=h_sun_ns, a_sun_ns=a_sun_ns,
                    w_alpha_i_j=w_alpha_i_j, w_beta_i_j=w_beta_i_j)

                # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
                # 一般部位・不透明な開口部の場合、日射・長波長放射を考慮する。
                return get_theta_o_sol_i_j_ns_with_solar(
                    a_s_i_j=boundary_i_j.spec.outside_solar_absorption,
                    eps_r_i_j=boundary_i_j.spec.outside_emissivity,
                    r_surf_o_i_j=boundary_i_j.spec.outside_heat_transfer_resistance,
                    theta_o_ns=theta_o_ns,
                    i_is_d_i_j_ns=i_is_d_i_j_ns,
                    i_is_sky_i_j_ns=i_is_sky_i_j_ns,
                    i_is_ref_i_j_ns=i_is_ref_i_j_ns,
                    r_n_is_i_j_ns=r_n_is_i_j_ns)

            # 透明な開口部の場合
            elif boundary_i_j.boundary_type == BoundaryType.ExternalTransparentPart:

                # 室iの境界jの傾斜面のステップnにおける相当外気温度, ℃, [8760*4]
                # 透明な開口部の場合、日射はガラス面への透過・吸収の項で扱うため、ここでは長波長放射のみ考慮する。
                return get_theta_o_sol_i_j_ns_without_solar(
                    eps_r_i_j=boundary_i_j.spec.outside_emissivity,
                    r_surf_o_i_j=boundary_i_j.spec.outside_heat_transfer_resistance,
                    theta_o_ns=theta_o_ns,
                    r_n_is_i_j_ns=r_n_is_i_j_ns)

        # 日射が当たらない場合
        else:

            return theta_o_ns

    # 地盤の場合
    elif boundary_i_j.boundary_type == BoundaryType.Ground:

        return np.full(24 * 365 * 4, np.average(theta_o_ns))

    else:

        raise ValueError()


def get_theta_o_sol_i_j_ns_with_solar(
        a_s_i_j: float, eps_r_i_j: float, r_surf_o_i_j,
        theta_o_ns: np.ndarray, i_is_d_i_j_ns, i_is_sky_i_j_ns, i_is_ref_i_j_ns, r_n_is_i_j_ns
) -> np.ndarray:
    """
    日射の当たる一般部位・不透明な開口部における傾斜面の相当外気温度を計算する。

    Args:
        a_s_i_j: 室iの境界jにおける室外側日射吸収率
        eps_r_i_j: 室iの境界jにおける室外側長波長放射率
        r_surf_o_i_j: 室iの境界jにおける室外側熱伝達抵抗, m2K/W
        theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
        i_is_d_i_j_ns: ステップnにおける室iの境界jにおける傾斜面の日射量のうち直達成分, W/m2K [8760*4]
        i_is_sky_i_j_ns: ステップnにおける室iの境界jにおける傾斜面の日射量のうち天空成分, W/m2K [8760*4]
        i_is_ref_i_j_ns: ステップnにおける室iの境界jにおける傾斜面の日射量のうち地盤反射成分, W/m2K [8760*4]
        r_n_is_i_j_ns: ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2 [8760 * 4]

    Returns:
        ステップnにおける室iの境界jにおける傾斜面の相当外気温度, ℃ [8760*4]
    """

    theta_o_sol_i_j_ns = theta_o_ns\
        + (a_s_i_j * (i_is_d_i_j_ns + i_is_sky_i_j_ns + i_is_ref_i_j_ns) - eps_r_i_j * r_n_is_i_j_ns) * r_surf_o_i_j

    return theta_o_sol_i_j_ns


def get_theta_o_sol_i_j_ns_without_solar(
        eps_r_i_j: float, r_surf_o_i_j,
        theta_o_ns: np.ndarray, r_n_is_i_j_ns
) -> np.ndarray:
    """
    日射の当たる透明な開口部における傾斜面の相当外気温度を計算する。

    Args:
        eps_r_i_j: 室iの境界jにおける室外側長波長放射率
        r_surf_o_i_j: 室iの境界jにおける室外側熱伝達抵抗, m2K/W
        theta_o_ns: ステップnにおける外気温度, ℃, [8760 * 4]
        r_n_is_i_j_ns: ステップnにおける室iの境界jにおける傾斜面の夜間放射量, W/m2 [8760 * 4]

    Returns:
        ステップnにおける室iの境界jにおける傾斜面の相当外気温度, ℃ [8760*4]
    """

    theta_o_sol_i_j_ns = theta_o_ns + (- eps_r_i_j * r_n_is_i_j_ns) * r_surf_o_i_j

    return theta_o_sol_i_j_ns


