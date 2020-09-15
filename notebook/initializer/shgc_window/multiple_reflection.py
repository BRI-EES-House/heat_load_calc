"""
複数の層で構成されたガラスの日射特性値を計算するモジュール

このモジュールは複数の層で構成されたガラスの日射特性値を計算について記す。
ガラスの日射特性値とは、
- 正面側からの入射光に対する日射透過率
- 背面側からの入射光に対する日射透過率
- 正面側からの入射光に対する日射反射率
- 背面側からの入射光に対する日射反射率
- 各層における日射吸収率
である。
このモジュールの計算方法はJIS A2103に基づく。
"""

from typing import List


class SolarSpecSingleLayer:
    """
    ガラス1枚についての日射特性値を表すクラス

    Note:
        SolarSpecMultiLayer クラスとの違いは、メンバに日射吸収率を含んでいるところ。
    """

    def __init__(self, tau_f: float, tau_b: float, rho_f: float, rho_b: float):

        # 正面側からの入射光に対する日射透過率
        self.tau_f = tau_f

        # 背面側からの入射光に対する日射透過率
        self.tau_b = tau_b

        # 正面側からの入射光に対する日射反射率
        self.rho_f = rho_f

        # 背面側からの入射光に対する日射反射率
        self.rho_b = rho_b

        # 正面側からの入射光に対する日射吸収率
        self.a_f = 1.0 - tau_f - rho_f

        # 背面側からの入射光に対する日射吸収率
        self.a_b = 1.0 - tau_b - rho_b


class SolarSpecMultiLayer:
    """
    ガラス複数枚についての合成された日射特性値を表すクラス

    Note:
        SolarSpecSingleLayer クラスとの違いは、メンバに日射吸収率を含んでいないところ。
        ガラス複数枚についての日射吸収率について、定義しようと思えば定義可能であるが、
        複数枚の合成された日射吸収率については後々の計算に使用しないため、ここで保持しない。
    """

    def __init__(self, tau_f: float, tau_b: float, rho_f: float, rho_b:float):

        # 正面側からの入射光に対する日射透過率
        self.tau_f = tau_f

        # 背面側からの入射光に対する日射透過率
        self.tau_b = tau_b

        # 正面側からの入射光に対する日射反射率
        self.rho_f = rho_f

        # 背面側からの入射光に対する日射反射率
        self.rho_b = rho_b


class Glass:

    def __init__(self, ss: List[SolarSpecSingleLayer]):

        self._ss = ss

    def get_solar_spec_multi_layer(self, ss: List[SolarSpecSingleLayer], i: int, j: int) -> SolarSpecMultiLayer:
        """
        層iから層jの複合した日射特性値を計算する。

        Args:
            ss: ガラス1枚に対する日射特性値
            i: 層i
            j:　層j

        Returns:
            層iから層jの複合した日射特性値
        """

        # iとjの数値の範囲に関するエラー処理
        if i < 0:
            raise ValueError('レイヤー番号iは0以上の値をとらないといけません。')
        if j < 0:
            raise ValueError('レイヤー番号jは0以上の値をとらないといけません。')
        if i > j:
            raise ValueError('レイヤー番号iとjに関してつねにi<=jの関係がないといけません。')
        if j >= len(ss):
            raise ValueError('レイヤー番号jに計算する層構成の数以上の値が指定されています。')

        if i == j:

            return SolarSpecMultiLayer(tau_f=ss[j].tau_f, tau_b=ss[j].tau_b, rho_f=ss[j].rho_f, rho_b=ss[j].rho_b)

        else:

            # 層0から層j-1の日射特性値
            ss_ml = self.get_solar_spec_multi_layer(ss, i, j - 1)

            # 式(6)
            tau_f = (ss_ml.tau_f * ss[j].tau_f) / (1.0 - ss_ml.rho_b * ss[j].rho_f)

            # 式(7)
            tau_b = (ss[j].tau_b * ss_ml.tau_b) / (1.0 - ss_ml.rho_b * ss[j].rho_f)

            # 式(8)
            rho_f = ss_ml.rho_f + (ss_ml.tau_f * ss[j].rho_f * ss_ml.tau_b) / (1.0 - ss_ml.rho_b * ss[j].rho_f)

            # 式(9)
            rho_b = ss[j].rho_b + (ss[j].tau_b * ss_ml.rho_b * ss[j].tau_f) / (1.0 - ss_ml.rho_b * ss[j].rho_f)

            return SolarSpecMultiLayer(tau_f=tau_f, tau_b=tau_b, rho_f=rho_f, rho_b=rho_b)

    def get_abs_multi_layer(self) -> List[float]:
        """
        層iの日射吸収率を計算する。
        Args:
            ss: ガラス1枚に対する日射特性値

        Returns:
            層iの日射吸収率, [層の数]
        """

        # 層の数
        n = len(self._ss)

        # 層0から層jまでの日射特性値
        ss_ml_0_j = [self.get_solar_spec_multi_layer(self._ss, 0, j) for j in range(n)]

        # 層jから層n-1までの日射特性値
        ss_ml_j_n = [self.get_solar_spec_multi_layer(self._ss, j, n - 1) for j in range(n)]

        # 層jの正面側からの入射光
        sol_f = [0.0] * n
        for j in range(n):
            if j == 0:
                sol_f[j] = 1.0
            else:
                sol_f[j] = ss_ml_0_j[j-1].tau_f / (1.0 - ss_ml_0_j[j-1].rho_b * ss_ml_j_n[j].rho_f)

        # 層jの背面側からの入射光
        sol_b = [0.0] * n
        for j in range(n):
            if j == n - 1:
                sol_b[j] = 0.0
            else:
                sol_b[j] = ss_ml_0_j[j].tau_f * ss_ml_j_n[j+1].rho_f / (1.0 - ss_ml_0_j[j].rho_b * ss_ml_j_n[j+1].rho_f)

        return [sol_f[j] * self._ss[j].a_f + sol_b[j] * self._ss[j].a_b for j in range(n)]

    def get_total_solar_spec(self) -> SolarSpecMultiLayer:
        """
        グレージング複合体全体の日射特性値を計算する。
        Args:
            ss: ガラス1枚に対する日射特性値

        Returns:
            グレージング複合体全体の日射特性値
        """

        return self.get_solar_spec_multi_layer(self._ss, 0, len(self._ss) - 1)



