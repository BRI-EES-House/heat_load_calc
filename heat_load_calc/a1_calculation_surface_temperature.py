import numpy as np


def get_theta_srf_dsh_a_i_jstrs_npls_ms(
        q_srf_jstrs_n: np.ndarray,
        phi_a_1_bnd_jstrs_ms: np.ndarray,
        r_bnd_i_jstrs_ms: np.ndarray,
        theta_dsh_srf_a_jstrs_n_ms: np.ndarray
) -> np.ndarray:
    """

    Args:
        q_srf_jstrs_n: ステップnの統合された境界j*における表面熱流（壁体吸熱を正とする）, W/m2, [j*]
        phi_a_1_bnd_jstrs_ms: 統合された境界j*における項別公比法の項mの吸熱応答係数の係数, m2K/W, [jstrs, 12]
        r_bnd_i_jstrs_ms: 室iの統合された境界j*の項mにおける公比, [jstrs, 12]
        theta_dsh_srf_a_jstrs_n_ms: ステップnの統合された境界j*における指数項mの吸熱応答の項別成分, degree C, [j*, 12]
    Returns:
        ステップn+1の室iの統合された境界j*における項別公比法の項mの吸熱応答に関する表面温度, degree C, [jstrs, 12]
    """

    return phi_a_1_bnd_jstrs_ms * q_srf_jstrs_n[:, np.newaxis] + r_bnd_i_jstrs_ms * theta_dsh_srf_a_jstrs_n_ms

