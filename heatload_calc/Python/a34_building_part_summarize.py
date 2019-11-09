import numpy as np
from typing import List

from s3_surface_initializer import Initialized_Surface
from s3_surface_loader import Boundary
from s3_surface_loader import InternalPartSpec
from s3_surface_loader import GeneralPartSpec
from s3_surface_loader import TransparentOpeningPartSpec
from s3_surface_loader import OpaqueOpeningPartSpec
from s3_surface_loader import GroundSpec

"""
付録34．境界条件が同じ部位の集約
"""


def is_boundary_integratable(b1: Boundary, b2: Boundary) -> bool:
    """
    境界1と境界2が同じであるかを判定する。

    Args:
        b1: 境界1
        b2: 境界2

    Returns:
        判定結果
    """

    # 境界のメイン部分の整合性をチェックし、同じでなければFalseを返して終了。
    if not is_boundary_bodies_integratable(b1, b2):
        return False

    # 境界の種類が間仕切りの場合
    if b1.boundary_type == 'internal':

        return is_boundary_internals_integratable(bi1=b1.spec, bi2=b2.spec)

    # 境界の種類が一般部位の場合
    elif b1.boundary_type == 'external_general_part':

        return is_boundary_generals_integratable(bg1=b1.spec, bg2=b2.spec)

    # 境界の種類が透明な開口部の場合
    elif b1.boundary_type == 'external_transparent_part':

        return is_boundary_transparent_openings_integratable(bto1=b1.spec, bto2=b2.spec)

    # 境界の種類が非透明な開口部の場合
    elif b1.boundary_type == 'external_opaque_part':

        return is_boundary_opaque_openings_integratable(boo1=b1.spec, boo2=b2.spec)

    # 境界の種類が地盤の場合
    elif b1.boundary_type == 'ground':

        return is_boundary_grounds_integratable(bg1=b1.spec, bg2=b2.spec)

    else:
        raise ValueError()


def is_almost_equal(v1: float, v2: float) -> bool:
    """
    境界条件が同じかどうかを判定する際に値が同じであるかを判定する時に、プログラム上の誤差を拾わないために、
    少し余裕を見て10**(-5) 以内の差であれば、同じ値であるとみなすことにする。
    この部分はプログラムテクニックの部分であるため、仕様書には書く必要はない。

    Args:
        v1: 比較する値1
        v2: 比較する値2

    Returns:
        同じか否かの判定結果
    """

    return abs(v1 - v2) < 1.0E-5


def is_boundary_bodies_integratable(b1: Boundary, b2: Boundary) -> bool:
    """
    Boundary のメイン部分が統合可能であるかを判断する。

    Args:
        b1: 境界1
        b2: 境界2

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1のメイン部分と境界2のメイン部分に関して統合可能であると判断する。
        (1) 境界の種類
        (2) 室内侵入日射吸収の有無
        (3) 日射の有無（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
        (4) 温度差係数（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
        (5) 向き(日射の有無が「当たる」の場合）
        (6) 隣室タイプ（境界の種類が「間仕切り」の場合）
        なお、メイン部分とは、
        間仕切り・一般部位・透明な開口部・非透明な開口部・地盤などの仕様や、日除けの仕様を覗いた部分
    """

    # 境界の種類
    if b1.boundary_type != b2.boundary_type:
        return False

    # 室内侵入日射吸収の有無
    if b1.is_solar_absorbed_inside != b2.is_solar_absorbed_inside:
        return False

    # 境界の種類が「外皮_一般部位」、「外皮_透明な開口部」又は「外皮_不透明な開口部」の場合
    if (b1.boundary_type == 'external_general_part') \
            or (b1.boundary_type == 'external_transparent_part') \
            or (b1.boundary_type == 'external_opaque_part'):

        # 日射の有無
        if b1.is_sun_striked_outside != b2.is_sun_striked_outside:
            return False

        # 温度差係数
        if not is_almost_equal(b1.temp_dif_coef, b2.temp_dif_coef):
            return False

        # 日射の有無が当たるの場合
        if b1.is_sun_striked_outside:

            # 向き
            if b1.direction != b2.direction:
                return False

    # 境界の種類が間仕切りの場合
    if b1.boundary_type == 'internal':

        # 隣室タイプ
        if b1.next_room_type != b2.next_room_type:
            return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_internals_integratable(bi1: InternalPartSpec, bi2: InternalPartSpec) -> bool:
    """
    Boundary の InternalPartSpec が統合可能であるかを判断する。

    Args:
        bi1: 境界1の間仕切りの仕様
        bi2: 境界2の間仕切りの仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1の間仕切りの仕様と境界2の間仕切りの仕様に関して統合可能であると判断する。
        (1) 室内側熱伝達抵抗
    """

    return is_almost_equal(bi1.inside_heat_transfer_resistance, bi2.inside_heat_transfer_resistance)


def is_boundary_generals_integratable(bg1: GeneralPartSpec, bg2: GeneralPartSpec) -> bool:
    """
    Boundary の GeneralPartSpec が統合可能であるかを判断する。

    Args:
        bg1: 境界1の一般部位の仕様
        bg2: 境界2の一般部位の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1の間仕切りの仕様と境界2の間仕切りの仕様に関して統合可能であると判断する。
        (1) 室外側長波長放射率
        (2) 室外側日射吸収率
        (3) 室外側日射吸収率
        (4) 室外側熱伝達抵抗
    """

    # 室外側長波長放射率
    if not is_almost_equal(bg1.outside_emissivity, bg2.outside_emissivity):
        return False

    # 室外側日射吸収率
    if not is_almost_equal(bg1.outside_solar_absorption, bg2.outside_solar_absorption):
        return False

    # 室内側熱伝達抵抗
    if not is_almost_equal(bg1.inside_heat_transfer_resistance, bg2.inside_heat_transfer_resistance):
        return False

    # 室外側熱伝達抵抗
    if not is_almost_equal(bg1.outside_heat_transfer_resistance, bg2.outside_heat_transfer_resistance):
        return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_transparent_openings_integratable(
        bto1: TransparentOpeningPartSpec, bto2: TransparentOpeningPartSpec) -> bool:
    """
    Boundary の TransparentOpeningPartSpec が統合可能であるかを判断する。
    Args:
        bto1: 境界1の透明な開口部の仕様
        bto2: 境界2の透明な開口部の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、
        境界の透明な開口部の仕様1と境界の透明な開口部の仕様2に関して統合可能であると判断する。
        (1) 室外側長波長放射率
        (2) 室内側熱伝達抵抗
        (3) 室外側熱伝達抵抗
    """

    # 室外側長波長放射率
    if not is_almost_equal(bto1.outside_emissivity, bto2.outside_emissivity):
        return False

    # 室内側熱伝達抵抗
    if not is_almost_equal(bto1.inside_heat_transfer_resistance, bto2.inside_heat_transfer_resistance):
        return False

    # 室外側熱伝達抵抗
    if not is_almost_equal(bto1.outside_heat_transfer_resistance, bto2.outside_heat_transfer_resistance):
        return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_opaque_openings_integratable(boo1: OpaqueOpeningPartSpec, boo2: OpaqueOpeningPartSpec) -> bool:
    """
    Boundary の OpaqueOpeningSpec が統合可能であるかを判断する。

    Args:
        boo1: 境界1の不透明な開口部の仕様
        boo2: 境界2の不透明な開口部の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、
        境界1の不透明な開口部の仕様と境界2の不透明な開口部の仕様に関して統合可能であると判断する。
        (1) 室外側長波長放射率
        (2) 室外側日射吸収率
        (3) 室外側日射吸収率
        (4) 室外側熱伝達抵抗
    """

    # 室外側長波長放射率
    if not is_almost_equal(boo1.outside_emissivity, boo2.outside_emissivity):
        return False

    # 室外側日射吸収率
    if not is_almost_equal(boo1.outside_solar_absorption, boo2.outside_solar_absorption):
        return False

    # 室内側熱伝達抵抗
    if not is_almost_equal(boo1.inside_heat_transfer_resistance, boo2.inside_heat_transfer_resistance):
        return False

    # 室外側熱伝達抵抗
    if not is_almost_equal(boo1.outside_heat_transfer_resistance, boo2.outside_heat_transfer_resistance):
        return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def is_boundary_grounds_integratable(bg1: GroundSpec, bg2: GroundSpec) -> bool:
    """
    Boundary の GroundSpec が統合可能であるかを判断する。

    Args:
        bg1: 境界1の地盤の仕様
        bg2: 境界2の地盤の仕様

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1の地盤の仕様と境界2の地盤の仕様に関して統合可能であると判断する。
        (1) 室内側熱伝達抵抗
    """

    return is_almost_equal(bg1.inside_heat_transfer_resistance, bg2.inside_heat_transfer_resistance)


def get_group_indices(boundaries: List[Boundary]) -> np.ndarray:
    """
    集約化できるBoundaryには共通のIDをふっていく。

    Args:
        boundaries: 室iにおける境界kのリスト

    Returns:
        グループ番号 * 境界の数

    Notes:
        例えば、境界の種類が擬似的に、
        [A,B,C,B,A,C,D,E,F,D,E]
        だった場合は、Aからグループ番号を振り、
        [0,1,2,1,0,2,3,4,5,3,4]
        となる。
    """

    n = len(boundaries)

    # 部位番号とグループ番号の対応表 (-1は未割当)
    g_k = np.zeros(n, dtype=np.int64) - 1

    # 部位のグループ化
    for k in range(n):

        # 同じ境界条件の部位を探す
        gs_index = np.array(
            [l for l in range(n)
             if g_k[l] < 0 and is_boundary_integratable(boundaries[k], boundaries[l])], dtype=np.int64)

        # 部位番号とグループ番号の対応表に新しいグループ番号を記述
        g_k[gs_index] = np.max(g_k) + 1

    return g_k


# 部位の集約（同一境界条件の部位を集約する）
class GroupedSurface:
    def __init__(self, surfaces: Initialized_Surface):

        ib = surfaces.ib
        # グループごとの集約処理

        gpi = surfaces.gp_idx

        # 新しい室内表面の作成

        group_number = np.unique(gpi)

        self.NsurfG_i = len(group_number)

        # 先頭インデックス一覧
        idx0 = np.array([np.where(gpi == k)[0][0] for k in group_number], dtype=np.int)

        # グループBooleanIndexMap
        map_g = np.array([[gpi == k][0] for k in group_number], dtype=np.int)

        def first(arr):
            return np.array(arr)[idx0]

        self.name = ib.name_i_iks  # 名称
        self.sub_name = ib.sub_name_i_iks  # 副名称（統合する前の境界の名前を'+'記号でつなげたもの）
        self.boundary_type = ib.boundary_type_i_iks  # 境界の種類
        self.A_i_g = ib.a_i_iks  # 面積
        self.is_sun_striked_outside = ib.is_sun_striked_outside_i_iks  # 日射の有無
        self.a_i_g = ib.h_i_iks  # 温度差係数
        self.Rnext_i_g = ib.next_room_type_i_iks  # 隣室タイプ
        self.is_solar_absorbed_inside = ib.is_solar_absorbed_inside_i_ks  # 室内侵入日射吸収の有無
        self.hi_i_g_n = ib.h_i_i_iks  # 16) 室内側熱伝達率

        # 20) 裏面境界温度
        self.Teolist = first(surfaces.Teolist)

        # 21) 前時刻の裏面境界温度
        self.oldTsd_t = np.zeros((self.NsurfG_i, 12))

        # 22) 前時刻の室内表面熱流
        self.oldTsd_a = np.zeros((self.NsurfG_i, 12))
        self.oldqi = np.zeros(self.NsurfG_i)  # 前時刻の室内側表面熱流

        # 23) 根の数
        self.Nroot = first(surfaces.Nroot)

        # 24) 公比
        self.Row = first(surfaces.Row)

        # 26) 吸熱応答係数の初項
        self.RFA0 = np.sum(surfaces.A_i_k * surfaces.RFA0 * map_g, axis=1) / self.A_i_g

        # 27) 貫流応答係数の初項
        self.RFT0 = np.sum(surfaces.A_i_k * surfaces.RFT0 * map_g, axis=1) / self.A_i_g

        self.RFT1 = np.zeros((self.NsurfG_i, 12))
        self.RFA1 = np.zeros((self.NsurfG_i, 12))
        for g in np.unique(gpi):
            f = gpi == g

            # 28) 指数項別吸熱応答係数
            self.RFT1[g] = np.sum(surfaces.A_i_k[f, np.newaxis] * surfaces.RFT1[f, :], axis=0) / self.A_i_g[g]

            # 29) 指数項別貫流応答係数
            self.RFA1[g] = np.sum(surfaces.A_i_k[f, np.newaxis] * surfaces.RFA1[f, :], axis=0) / self.A_i_g[g]
