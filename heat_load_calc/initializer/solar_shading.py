"""ひさしの影面積の計算

"""

import numpy as np
from typing import Dict
import math

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

            # 境界ｊの傾斜面の方位角, rad
            # 境界jの傾斜面の傾斜角, rad
            w_alpha_j, _ = external_boundaries_direction.get_w_alpha_j_w_beta_j(direction_j=b['direction'])

            if input_method == 'simple':

                return SolarShadingSimple(
                    w_alpha=w_alpha_j,
                    depth=ssp['depth'],
                    d_h=ssp['d_h'],
                    d_e=ssp['d_e']
                )

            elif input_method == 'detail':

                return SolarShadingDetail(
                    w_alpha=w_alpha_j,
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

    def get_f_ss_d_j_ns(self, h_sun_n, a_sun_n):
        """
        直達日射に対する日よけの影面積比率を計算する。

        Args:
            h_sun_n: 太陽高度, rad, [8760*4]
            a_sun_n: 太陽方位角, rad, [8760*4]

        Returns:
            直達日射に対する日除けの影面積比率, [8760*4]
        """

        raise NotImplementedError()

    def get_f_ss_s_j(self):
        """
        天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率
        """

        raise NotImplementedError()


class SolarShadingSimple(SolarShading):

    def __init__(self, w_alpha, depth, d_h, d_e):

        super().__init__()

        self.w_alpha = w_alpha
        self.depth = depth
        self.d_h = d_h
        self.d_e = d_e

    def get_f_ss_d_j_ns(self, h_sun_n: np.ndarray, a_sun_n: np.ndarray) -> np.ndarray:
        """
        無限に長い庇がある場合の直達日射に対する日よけの影面積比率を計算する。

        Args:
            h_sun_n: 太陽高度, rad, [8760*4]
            a_sun_n: 太陽方位角, rad, [8760*4]

        Returns:
            直達日射に対する日除けの影面積比率, [8760*4]
        """

        h_s_n = np.where(h_sun_n > 0.0, h_sun_n, 0.0)
        a_s_n = np.where(h_sun_n > 0.0, a_sun_n, 0.0)

        # プロファイル角, tangent
        # TODO: cos が 0 になる可能性を整理して条件式を追加する必要あり。
        tan_fai = np.tan(h_s_n) / np.cos(a_s_n - self.w_alpha)

        # 日よけにより日射が遮られる長さ（窓上端からの長さ）, m
        DH_i_k = self.depth * tan_fai - self.d_e

        # 日影面積率の計算 式(79)
        #   マイナスの場合（日陰が窓上端にかからない場合）は 0.0 とする。
        #   1.0を超える場合（日陰が窓下端よりも下になる場合）は 1.0 とする。
        F_SDW_i_k = np.clip(DH_i_k / self.d_h, 0.0, 1.0)

        # 日が出ていないときは 0.0 とする。
        F_SDW_i_k[h_s_n <= 0] = 0.0

        return F_SDW_i_k

    def get_f_ss_s_j(self) -> float:
        """
        無限に長い庇がある場合の天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率
        """

        # 庇の出幅
        z = self.depth

        # 窓の高さ
        yw = self.d_h

        # 窓の上端から庇までの長さ
        y1 = self.d_e

        ac = y1 + yw
        ab = z
        ad = y1
        dc = yw
        bd = math.sqrt(ad ** 2.0 + ab ** 2.0)
        bc = math.sqrt((ad + dc) ** 2.0 + ab ** 2.0)

        return ((ac + bd) - (ad + bc)) / (2.0 * dc)


class SolarShadingDetail(SolarShading):

    def __init__(self, w_alpha, x1, x2, x3, y1, y2, y3, z_x_pls, z_x_mns, z_y_pls, z_y_mns):

        super().__init__()

        self.w_alpha = w_alpha
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

    def get_f_ss_d_j_ns(self, h_sun_n, a_sun_n):
        """
        直達日射に対する日よけの影面積比率を計算する。

        Args:
            h_sun_n: 太陽高度, rad, [8760*4]
            a_sun_n: 太陽方位角, rad, [8760*4]

        Returns:
            直達日射に対する日除けの影面積比率, [8760*4]
        """

        raise NotImplementedError()

    def get_f_ss_s_j(self):
        """
        天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率
        """

        raise NotImplementedError()


class SolarShadingNot(SolarShading):

    def __init__(self):

        super().__init__()

    def get_f_ss_d_j_ns(self, h_sun_n, a_sun_n):
        """
        直達日射に対する日よけの影面積比率を計算する。

        Args:
            h_sun_n: 太陽高度, rad, [8760*4]
            a_sun_n: 太陽方位角, rad, [8760*4]

        Returns:
            直達日射に対する日除けの影面積比率, [8760*4]
        """

        # TODO: 要確認（ここは1.0ではなくて0.0が正しい？）
        return np.full(len(h_sun_n), 1.0)

    def get_f_ss_s_j(self):
        """
        天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率
        """

        raise 0.0
