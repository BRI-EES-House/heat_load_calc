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

from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.initializer.boundary_simple import BoundarySimple


def integrate(bss: List[BoundarySimple]) -> List[BoundarySimple]:
    """壁体を集約する。

    Args:
        bss: 境界, [j]

    Returns:
        集約された境界, [j*]
    """

    bss = np.array(bss)

    # 集約化可能な境界には同じIDを振り、境界ごとにそのIDを取得する。
    # BoundarySimple の数のIDを持つ ndarray
    # 例
    # [ 0  1  2  3  4  5  6  7  8  9  9 10 11 12 13 14 15 16 11 12 15 16 17 18
    #  19 11 12 15 16 17 20 11 12 13 21 15 16 22 23 24 25 26 27 28 29 30 31 31
    #  31 31]
    gp_idxs = get_group_indices(bss=bss)

    # 先頭のインデックスのリスト
    # [ 0  1  2  3  4  5  6  7  8  9 11 12 13 14 15 16 17 22 23 24 30 34 37 38
    #  39 40 41 42 43 44 45 46]
    first_idx = np.array([np.where(gp_idxs == k)[0][0] for k in np.unique(gp_idxs)], dtype=np.int)

    # 統合された境界j*の総数
    bs_n = len(first_idx)

    # 境界jの名称, [j]
    name_js = ['integrated_boundary' + str(i) for i in np.unique(gp_idxs)]

    # 境界jの副名称（統合する前の境界の名前を'+'記号でつなげたもの）, [j]
    sub_name_js = ['+'.join([bs.name for bs in bss[gp_idxs == i]]) for i in np.unique(gp_idxs)]

    # 境界jの面する室のID, [j]
    connected_room_id_js = [bss[first_idx[i]].connected_room_id for i in np.unique(gp_idxs)]

    # 境界jの種類, [j]
    boundary_type_js = [bss[first_idx[i]].boundary_type for i in np.unique(gp_idxs)]

    # 境界jの面積, m2, [j]
    a_js = [sum([bs.area for bs in bss[gp_idxs == i]]) for i in np.unique(gp_idxs)]

    # 境界jの温度差係数, [j]
    h_td_js = [bss[first_idx[i]].h_td for i in np.unique(gp_idxs)]

    # 隣接する室のタイプ(int), [j]
    next_room_type_js = [bss[first_idx[i]].next_room_type for i in np.unique(gp_idxs)]

    # 境界jの裏面の境界ID, [j]
    rear_surface_boundary_id_js = []
    for i in np.unique(gp_idxs):
        # 統合する前の裏面の境界id
        id = bss[first_idx[i]].rear_surface_boundary_id
        # 統合後の裏面の境界id (None の場合は None を代入する。）
        id2 = None if id is None else gp_idxs[id]
        rear_surface_boundary_id_js.append(id2)

    # 日射吸収の有無, [j]
    is_solar_absorbed_inside_js = [bss[first_idx[i]].is_solar_absorbed_inside for i in np.unique(gp_idxs)]

    # 室外側の日射の有無
    # True: 当たる
    # False: 当たらない
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    is_sun_striked_outside_js = [bss[first_idx[i]].is_sun_striked_outside for i in np.unique(gp_idxs)]

    # 面する方位
    # 's', 'sw', 'w', 'nw', 'n', 'ne', 'e', 'se', 'top', 'bottom'
    # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
    direction_js = [bss[first_idx[i]].direction for i in np.unique(gp_idxs)]

    # 室内側表面総合熱伝達率, W/m2K
    # 境界jの室内側表面総合熱伝達率, W/m2K, [j]
    h_i_js = [bss[first_idx[i]].h_i for i in np.unique(gp_idxs)]


    return [
        BoundarySimple(
            id=j,
            name=name_js[j],
            sub_name=sub_name_js[j],
            connected_room_id=connected_room_id_js[j],
            boundary_type=boundary_type_js[j],
            area=a_js[j],
            h_td=h_td_js[j],
            next_room_type=next_room_type_js[j],
            rear_surface_boundary_id=rear_surface_boundary_id_js[j],
            is_solar_absorbed_inside=is_solar_absorbed_inside_js[j],
            is_sun_striked_outside=is_sun_striked_outside_js[j],
            direction=direction_js[j],
            h_i=h_i_js[j],
            theta_o_sol=None,
            q_trs_sol=None,
            n_root=None,
            row=None,
            rft0=None,
            rfa0=None,
            rft1=None,
            rfa1=None
        )
        for j in range(bs_n)
    ]


def get_group_indices(bss: np.ndarray) -> np.ndarray:
    """
    集約化できるBoundaryには共通のIDをふっていく。

    Args:
        bss: 境界j

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
                if g_k[l] < 0 and _is_boundary_integratable(bs1=bss[k], bs2=bss[l])
            ], dtype=np.int64
        )

        # 部位番号とグループ番号の対応表に新しいグループ番号を記述
        g_k[gs_index] = np.max(g_k) + 1

    return g_k


def _is_boundary_integratable(bs1: BoundarySimple, bs2: BoundarySimple) -> bool:
    """
    境界1と境界2が同じであるかを判定する。

    Args:
        bs1: 境界1
        bs2: 境界2

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

    # 接する室のID
    if bs1.connected_room_id != bs2.connected_room_id:
        return False

    # 境界の種類
    if bs1.boundary_type != bs2.boundary_type:
        return False

    # 室内侵入日射吸収の有無
    if bs1.is_solar_absorbed_inside != bs2.is_solar_absorbed_inside:
        return False

    # 室内側熱伝達率
    if not _is_almost_equal(bs1.h_i, bs2.h_i):
        return False

    # 境界の種類が「外皮_一般部位」、「外皮_透明な開口部」又は「外皮_不透明な開口部」の場合
    if (bs1.boundary_type == BoundaryType.ExternalGeneralPart) \
            or (bs1.boundary_type == BoundaryType.ExternalTransparentPart) \
            or (bs1.boundary_type == BoundaryType.ExternalOpaquePart):

        # 日射の有無
        if bs1.is_sun_striked_outside != bs2.is_sun_striked_outside:
            return False

        # 温度差係数
        if not _is_almost_equal(bs1.h_td, bs2.h_td):
            return False

        # 日射の有無が当たるの場合
        if bs1.is_sun_striked_outside:

            # 向き
            if bs1.direction != bs2.direction:
                return False

    # 境界の種類が間仕切りの場合
    if bs1.boundary_type == BoundaryType.Internal:

        # 隣室タイプ
        if bs1.next_room_type != bs2.next_room_type:
            return False

    # 上記のチェックすべてでFalse判定がでなければ、それは同一であるとみなす。
    return True


def _is_almost_equal(v1: float, v2: float) -> bool:
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


def get_area_weighted_averaged_values_one_dimension(v: np.ndarray, a: np.ndarray) -> np.ndarray:
    """
    あるデータを面積荷重平均する。
    Args:
        v: ベクトル（1次元）, [m] (m=境界の数）
        a: 面積, m2, [m] (m=境界の数）

    Returns:
        面積荷重平均化された値
    """
    return np.sum(v * a / np.sum(a))


def get_area_weighted_averaged_values_two_dimension(v: np.ndarray, a: np.ndarray) -> np.ndarray:
    """
    時系列データ等複数の値もつ1次元配列のデータを複数もつマトリックスを面積加重平均する。

    Args:
        v: ベクトル（2次元） [m, n] （m=境界の数）
        a: 面積, m2, [境界の数]

    Returns:
        面積荷重平均化された1次元配列の値 [n]
    """

    # 面積割合, [境界の数]　ただし、行列計算可能なように[m,1]の2次元配列としている。
    r = (a / np.sum(a)).reshape(-1, 1)

    result = np.sum(v * r, axis=0)

    return result

