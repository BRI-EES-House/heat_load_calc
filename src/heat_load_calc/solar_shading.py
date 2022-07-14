import numpy as np
from typing import Dict
import math

from heat_load_calc.direction import Direction


class SolarShading:

    def __init__(self):
        pass

    @classmethod
    def create(cls, ssp_dict: Dict, direction: Direction):
        """
        入力ファイルの辞書の'solar_shading_part'を読み込む。

        Args:
            ssp_dict: 日除けの仕様に関する辞書
            direction: 方位

        Returns:
            SolarShadingPart クラス
        """

        if ssp_dict['existence']:

            input_method = ssp_dict['input_method']

            if direction in [Direction.TOP, Direction.BOTTOM]:

                raise ValueError("方位が「上方」「下方」の場合に日除けを定義することはできません。")

            # 境界ｊの傾斜面の方位角, rad
            alpha_w_j = direction.alpha_w_j

            if input_method == 'simple':

                return SolarShadingSimple(
                    alpha_w_j=alpha_w_j,
                    l_z_j=ssp_dict['depth'],
                    l_y_h_j=ssp_dict['d_h'],
                    l_y_e_j=ssp_dict['d_e']
                )

            elif input_method == 'detail':

                return SolarShadingDetail(
                    alpha_w_j=alpha_w_j,
                    x1=ssp_dict['x1'],
                    x2=ssp_dict['x2'],
                    x3=ssp_dict['x3'],
                    y1=ssp_dict['y1'],
                    y2=ssp_dict['y2'],
                    y3=ssp_dict['y3'],
                    z_x_pls=ssp_dict['z_x_pls'],
                    z_x_mns=ssp_dict['z_x_mns'],
                    z_y_pls=ssp_dict['z_y_pls'],
                    z_y_mns=ssp_dict['z_y_mns']
                )

            else:
                raise ValueError()

        else:

            return SolarShadingNot()

    def get_f_ss_d_j_ns(self, h_sun_n: np.ndarray, a_sun_n: np.ndarray) -> np.ndarray:
        """
        直達日射に対する日よけの影面積比率を計算する。

        Args:
            h_sun_n: 太陽高度, rad, [N+1]
            a_sun_n: 太陽方位角, rad, [N+1]

        Returns:
            直達日射に対する日除けの影面積比率, [N+1]
        """

        raise NotImplementedError()

    def get_f_ss_s_j(self) -> float:
        """
        天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率, -
        """

        raise NotImplementedError()


class SolarShadingSimple(SolarShading):

    def __init__(self, alpha_w_j: float, l_z_j: float, l_y_h_j: float, l_y_e_j: float):
        """

        Args:
            alpha_w_j: 開口部 j の方位角, rad
            l_z_j: 開口部 j のひさしの出幅, m
            l_y_h_j: 開口部 j の高さ, m
            l_y_e_j: 開口部 j の上端から日よけまでの長さ, m
        """

        super().__init__()

        self._alpha_w_j = alpha_w_j
        self._l_z_j = l_z_j
        self._l_y_h_j = l_y_h_j
        self._l_y_e_j = l_y_e_j

    def get_f_ss_d_j_ns(self, h_sun_n: np.ndarray, a_sun_n: np.ndarray) -> np.ndarray:
        """無限に長い庇がある場合の直達日射に対する日よけの日影面積比率を計算する。

        Args:
            h_sun_n: ステップ n における太陽高度, rad, [N+1]
            a_sun_n: ステップ n における太陽方位角, rad, [N+1]

        Returns:
            ステップ n における直達日射に対する日除けの日影面積比率, [N+1]

        Notes:
            日射が壁にあたらない場合は日影そのものができない。
            その場合は値として 0.0 を返す。
        """

        h_s_n = np.where(h_sun_n > 0.0, h_sun_n, 0.0)
        a_s_n = np.where(h_sun_n > 0.0, a_sun_n, 0.0)

        cos_a = np.where(np.cos(a_s_n - self._alpha_w_j) > 0, np.cos(a_s_n - self._alpha_w_j), 1.0)

        # ステップ n における境界 j に対する太陽のプロファイル角の正弦, -
        tan_phi_j_n = np.tan(h_s_n) / cos_a

        # ステップ n における開口部 j に影がかかる長さ（窓上端から下方への長さ）, m
        l_ss_d_y_j_n = self._l_z_j * tan_phi_j_n - self._l_y_e_j

        # 日影面積率の計算 式(79)
        #   マイナスの場合（日陰が窓上端にかからない場合）は 0.0 とする。
        #   1.0を超える場合（日陰が窓下端よりも下になる場合）は 1.0 とする。
        f_ss_d_j_n = np.clip(l_ss_d_y_j_n / self._l_y_h_j, 0.0, 1.0)

        # 日が出ていないときは 0.0 とする。
        f_ss_d_j_n[h_sun_n <= 0.0] = 0.0

        # 太陽位置が背面にある場合は 0.0 とする。
        f_ss_d_j_n[np.cos(a_s_n - self._alpha_w_j) <= 0.0] = 0.0

        return f_ss_d_j_n

    def get_f_ss_s_j(self) -> float:
        """
        無限に長い庇がある場合の天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率, -
        """

        return (
            ((self._l_y_e_j + self._l_y_h_j) + math.sqrt(self._l_y_e_j ** 2.0 + self._l_z_j ** 2.0))
            - (self._l_y_e_j + math.sqrt((self._l_y_e_j + self._l_y_h_j) ** 2.0 + self._l_z_j ** 2.0))
        ) / (2.0 * self._l_y_h_j)


class SolarShadingDetail(SolarShading):

    def __init__(self, alpha_w_j, x1, x2, x3, y1, y2, y3, z_x_pls, z_x_mns, z_y_pls, z_y_mns):

        super().__init__()

        self.w_alpha = alpha_w_j
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

    def get_f_ss_d_j_ns(self, h_sun_n: np.ndarray, a_sun_n: np.ndarray) -> np.ndarray:
        """
        直達日射に対する日よけの影面積比率を計算する。

        Args:
            h_sun_n: 太陽高度, rad, [N+1]
            a_sun_n: 太陽方位角, rad, [N+1]

        Returns:
            直達日射に対する日除けの影面積比率, [N+1]
        """

        raise NotImplementedError()

    def get_f_ss_s_j(self) -> float:
        """
        天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率, -
        """

        raise NotImplementedError()


class SolarShadingNot(SolarShading):

    def __init__(self):

        super().__init__()

    def get_f_ss_d_j_ns(self, h_sun_n: np.ndarray, a_sun_n: np.ndarray) -> np.ndarray:
        """
        直達日射に対する日よけの影面積比率を計算する。

        Args:
            h_sun_n: 太陽高度, rad, [N+1]
            a_sun_n: 太陽方位角, rad, [N+1]

        Returns:
            直達日射に対する日除けの影面積比率, [N+1]
        """

        return np.full(len(h_sun_n), 0.0)

    def get_f_ss_s_j(self) -> float:
        """
        天空放射に対する日よけの影面積比率を計算する。

        Returns:
            天空放射に対する日除けの影面積比率, -
        """

        return 0.0
