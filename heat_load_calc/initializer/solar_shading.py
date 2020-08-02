"""ひさしの影面積の計算

"""

import numpy as np
from typing import Dict

from heat_load_calc.initializer import external_boundaries_direction


class SolarShading:

    def __init__(self):
        pass

    @classmethod
    def create(cls, b: Dict):
        """
        入力ファイルの辞書の'solar_shading_part'を読み込む。

        Args:
            b: 'boundary' の辞書

        Returns:
            SolarShadingPart クラス
        """

        ssp = b['solar_shading_part']

        existence = ssp['existence']

        if b['boundary_type'] in ['external_general_part', 'external_transparent_part', 'external_opaque_part']:
            is_sun_striked_outside = bool(b['is_sun_striked_outside'])
        elif b['boundary_type'] in ['internal', 'ground']:
            is_sun_striked_outside = False
        else:
            raise KeyError()

        if existence & is_sun_striked_outside:

            input_method = ssp['input_method']

            if input_method == 'simple':

                return SolarShadingSimple(
                    depth=ssp['depth'],
                    d_h=ssp['d_h'],
                    d_e=ssp['d_e']
                )

            elif input_method == 'detail':

                return SolarShadingDetail(
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

            return SolarShadingNot()

    def get_f_sdw_j_ns(self, h_sun_n, a_sun_n, direction_i_ks: str):

        raise NotImplementedError()


class SolarShadingSimple(SolarShading):

    def __init__(self, depth, d_h, d_e):

        super().__init__()
        self.depth = depth
        self.d_h = d_h
        self.d_e = d_e

    def get_f_sdw_j_ns(self, h_sun_n, a_sun_n, direction_i_ks: str):

        # 境界ｊの傾斜面の方位角, rad
        # 境界jの傾斜面の傾斜角, rad
        w_alpha_j, _ = external_boundaries_direction.get_w_alpha_j_w_beta_j(direction_j=direction_i_ks)

        ###################################################################################
        h_s_n = np.where(h_sun_n > 0.0, h_sun_n, 0.0)
        a_s_n = np.where(h_sun_n > 0.0, a_sun_n, 0.0)

        # プロファイル角, tangent
        # TODO: cos が 0 になる可能性を整理して条件式を追加する必要あり。
        tan_fai = np.tan(h_s_n) / np.cos(a_s_n - w_alpha_j)

        # 日よけにより日射が遮られる長さ（窓上端からの長さ）, m
        DH_i_k = self.depth * tan_fai - self.d_e

        # 日影面積率の計算 式(79)
        #   マイナスの場合（日陰が窓上端にかからない場合）は 0.0 とする。
        #   1.0を超える場合（日陰が窓下端よりも下になる場合）は 1.0 とする。
        F_SDW_i_k = np.clip(DH_i_k / self.d_h, 0.0, 1.0)

        # 日が出ていないときは 0.0 とする。
        F_SDW_i_k[h_s_n <= 0] = 0.0

        return F_SDW_i_k


class SolarShadingDetail(SolarShading):

    def __init__(self, x1, x2, x3, y1, y2, y3, z_x_pls, z_x_mns, z_y_pls, z_y_mns):

        super().__init__()

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

    def get_f_sdw_j_ns(self, h_sun_n, a_sun_n, direction_i_ks: str):

        raise NotImplementedError()


class SolarShadingNot(SolarShading):

    def __init__(self):

        super().__init__()

    def get_f_sdw_j_ns(self, h_sun_n, a_sun_n, direction_i_ks: str):

        return np.full(len(h_sun_n), 1.0)

