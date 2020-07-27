import numpy as np
from collections import namedtuple
from typing import Dict

import heat_load_calc.x_19_external_boundaries_direction as x_19


"""
付録8．ひさしの影面積の計算
"""


class SolarShadingPart:

    def __init__(self, existence, input_method, depth, d_h, d_e, x1, x2, x3, y1, y2, y3, z_x_pls, z_x_mns, z_y_pls, z_y_mns):

        self.existence = existence
        self.input_method = input_method
        self.depth = depth
        self.d_h = d_h
        self.d_e = d_e
        self.x1 = x1
        self.x2 = x2
        self.x3 = x3
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.z_x_pls = z_x_pls
        self.z_x_mns = z_x_mns
        self.z_y_pls = z_y_pls
        self.z_y_mns = z_y_mns

    @classmethod
    def create(cls, ssp: Dict):
        """
        入力ファイルの辞書の'solar_shading_part'を読み込む。

        Args:
            ssp: 'solar shading part' の辞書

        Returns:
            SolarShadingPart クラス
        """

        existence = ssp['existence']

        if existence:

            input_method = ssp['input_method']

            if ssp['input_method'] == 'simple':

                return SolarShadingPart(
                    existence=existence,
                    input_method=input_method,
                    depth=ssp['depth'],
                    d_h=ssp['d_h'],
                    d_e=ssp['d_e'],
                    x1=None,
                    x2=None,
                    x3=None,
                    y1=None,
                    y2=None,
                    y3=None,
                    z_x_pls=None,
                    z_x_mns=None,
                    z_y_pls=None,
                    z_y_mns=None
                )

            elif ssp['input_method'] == 'detail':

                return SolarShadingPart(
                    existence=existence,
                    input_method=input_method,
                    depth=None,
                    d_h=None,
                    d_e=None,
                    x1=ssp['x1'],
                    x2=ssp['x2'],
                    x3=ssp['x3'],
                    y1=ssp['y1'],
                    y2=ssp['y2'],
                    y3=ssp['y3'],
                    z_x_pls=ssp['z_x_pls'],
                    z_x_mns=ssp['z_x_mns'],
                    z_y_pls=ssp['z_y_pls'],
                    z_y_mns=ssp['z_y_mns']
                )

            else:
                raise ValueError()

        else:

            return SolarShadingPart(
                existence=existence,
                input_method=None,
                depth=None,
                d_h=None,
                d_e=None,
                x1=None,
                x2=None,
                x3=None,
                y1=None,
                y2=None,
                y3=None,
                z_x_pls=None,
                z_x_mns=None,
                z_y_pls=None,
                z_y_mns=None
            )

    def get_FSDW_i_k_n2(self, h_sun_n, a_sun_n, direction_i_ks: str):

        # 室iの境界kの傾斜面の方位角, rad
        # 室iの境界kの傾斜面の傾斜角, rad
        w_alpha_i_k, _ = x_19.get_w_alpha_i_j_w_beta_i_j(direction_i_j=direction_i_ks)

        ###################################################################################
        h_s = np.where(h_sun_n > 0.0, h_sun_n, 0.0)
        a_s = np.where(h_sun_n > 0.0, a_sun_n, 0.0)
        # 日除けの日影面積率の計算
        if self.existence:
            if self.input_method == 'simple':


                return self.calc_F_SDW_i_k_n(
                    a_s_n=a_s,
                    h_s_n=h_s,
                    Wa_i_k=w_alpha_i_k
                )
            elif self.input_method == 'detailed':
                raise NotImplementedError()
            else:
                raise ValueError
        else:
            return np.full(len(h_sun_n), 1.0)


    # 日除けの影面積を計算する（当面、簡易入力のみに対応）式(79)
    def calc_F_SDW_i_k_n(self, a_s_n: np.ndarray, h_s_n: np.ndarray, Wa_i_k: float) -> np.ndarray:
        """
        :param a_s_n: 太陽方位角 [rad]
        :param h_s_n: 太陽高度 [rad]
        :param Wa_i_k: 庇の設置してある窓の傾斜面方位角[rad]
        :return: 日除けの影面積比率 [-]
        """

        # プロファイル角, tangent
        tan_fai = np.tan(h_s_n) / np.cos(a_s_n - Wa_i_k)

        # 日よけにより日射が遮られる長さ（窓上端からの長さ）, m
        DH_i_k = self.depth * tan_fai - self.d_e

        # 日影面積率の計算 式(79)
        #   マイナスの場合（日陰が窓上端にかからない場合）は 0.0 とする。
        #   1.0を超える場合（日陰が窓下端よりも下になる場合）は 1.0 とする。
        F_SDW_i_k = np.clip(DH_i_k / self.d_h, 0.0, 1.0)

        # 日が出ていないときは 0.0 とする。
        F_SDW_i_k[h_s_n <= 0] = 0.0

        return F_SDW_i_k

