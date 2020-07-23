"""壁体を集約する。

以下のパラメータを参照して全て同じであれば集約可能と判断する。
    - 境界の種類
    - 室内侵入日射吸収の有無
    - 室内側熱伝達抵抗
    - 日射の有無（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
    - 温度差係数（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
    - 向き(日射の有無が「当たる」の場合）
    - 隣室タイプ（境界の種類が「間仕切り」の場合）

"""

import numpy as np
from typing import List

from heat_load_calc.s3_surface_loader import Boundary
from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.initializer.boundary_simple import BoundarySimple


def get_group_indices(boundaries: List[Boundary], bss: np.ndarray) -> np.ndarray:
    """
    集約化できるBoundaryには共通のIDをふっていく。

    Args:
        boundaries: 室iにおける境界kのリスト
        bss: 室iにおける境界k

    Returns:
        グループ番号 * 境界の数

    Notes:
        例えば、境界の種類が擬似的に、
        [A,B,C,B,A,C,D,E,F,D,E]
        だった場合は、Aからグループ番号を振り、
        [0,1,2,1,0,2,3,4,5,3,4]
        となる。
    """

    n = len(bss)

    # 部位番号とグループ番号の対応表 (-1は未割当)
    g_k = np.full(n, -1, dtype=int)

    # 部位のグループ化
    for k in range(n):

        # 同じ境界条件の部位を探す
        gs_index = np.array(
            [
                l for l in range(n)
                if g_k[l] < 0 and is_boundary_integratable(b1=boundaries[k], b2=boundaries[l], b3=bss[k], b4=bss[l])
            ], dtype=np.int64
        )

        # 部位番号とグループ番号の対応表に新しいグループ番号を記述
        g_k[gs_index] = np.max(g_k) + 1

    return g_k


def is_boundary_integratable(b1: Boundary, b2: Boundary, b3: BoundarySimple, b4: BoundarySimple) -> bool:
    """
    境界1と境界2が同じであるかを判定する。

    Args:
        b1: 境界1
        b2: 境界2

    Returns:
        判定結果

    Notes:
        以下の値がすべて同じである場合に、境界1のメイン部分と境界2のメイン部分に関して統合可能であると判断する。
        (1) 境界の種類
        (2) 室内侵入日射吸収の有無
        (3) 室内側熱伝達抵抗
        (4) 日射の有無（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
        (5) 温度差係数（境界の種類が「外皮_一般部位」・「外皮_透明な開口部」・「外皮_不透明な開口部」の場合のみ）
        (6) 向き(日射の有無が「当たる」の場合）
        (7) 隣室タイプ（境界の種類が「間仕切り」の場合）
        なお、メイン部分とは、
        間仕切り・一般部位・透明な開口部・非透明な開口部・地盤などの仕様や、日除けの仕様を覗いた部分
    """

    # 境界の種類
    if b3.boundary_type != b4.boundary_type:
        return False

    # 室内侵入日射吸収の有無
    if b3.is_solar_absorbed_inside != b4.is_solar_absorbed_inside:
        return False

    # 室内側熱伝達率
    if not is_almost_equal(b3.h_i, b4.h_i):
        return False

    # 境界の種類が「外皮_一般部位」、「外皮_透明な開口部」又は「外皮_不透明な開口部」の場合
    if (b3.boundary_type == BoundaryType.ExternalGeneralPart) \
            or (b3.boundary_type == BoundaryType.ExternalTransparentPart) \
            or (b3.boundary_type == BoundaryType.ExternalOpaquePart):

        # 日射の有無
        if b3.is_sun_striked_outside != b4.is_sun_striked_outside:
            return False

        # 温度差係数
        if not is_almost_equal(b3.h_td, b4.h_td):
            return False

        # 日射の有無が当たるの場合
        if b3.is_sun_striked_outside:

            # 向き
            if b3.direction != b4.direction:
                return False

    # 境界の種類が間仕切りの場合
    if b3.boundary_type == BoundaryType.Internal:

        # 隣室タイプ
        if b3.next_room_type != b4.next_room_type:
            return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


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

