from typing import List, Dict, Tuple

from a_01_04_general_part_common_items import get_r_layers_i as a_01_04_get_r_layers_i
from a_01_04_general_part_common_items import get_u_i as a_01_04_get_u_i
from a_01_04_general_part_common_items import make_layer_hlc as a_01_04_make_layer_hlc


# region 木造


def get_wood_general_part_spec_hlc(parts: List[dict], r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    parts リストから parts_hlc リストを作成

    Args:
        parts: 一般部位の部分。リスト形式であるがリスト長は必ず1。
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K

    Notes:
        引数としてのpartsはリスト形式であるが、面積比率法を使用する場合以外は常にリスト長は1である。
        ここでは、リスト長が1以外であった場合のエラー処理も行う。
    """

    return get_general_part_spec_hlc(parts=parts, r_surf_i=r_surf_i, r_surf_o=r_surf_o)


# endregion


# region 鉄骨造


def get_steel_general_part_spec_hlc(
        u_r_steel: float, parts: List[dict], r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    parts リストからpartsリストを作成
    Args:
        u_r_steel: 補正熱貫流率（Ur値）（鉄骨造）, W/m2K
        parts: 一般部位の部分。リスト形式であるがリスト長は必ず1。
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K

    Notes:
        引数としてのpartsはリスト形式であるが、面積比率法を使用する場合以外は常にリスト長は1である。
        ここでは、リスト長が1以外であった場合のエラー処理も行う。
        鉄骨造の場合に限り、補正熱貫流率を入力する
    """

    if len(parts) != 1:
        raise ValueError('与えられたpartsのリスト数が1ではありません。')

    # 部分i
    part_i = parts[0]

    # 部分i の層
    layers_i = part_i['layers']

    # 部分iの層の熱抵抗の合計（表面熱伝達抵抗を除く）, m2K/W
    r_layers_i = a_01_04_get_r_layers_i(layers_i=layers_i)

    # 部分iの熱貫流率, W/m2K
    u_i = a_01_04_get_u_i(layers_i=layers_i, r_i=r_surf_i, r_o=r_surf_o)

    # 部分iの補正熱貫流率を反映した熱貫流率, W/m2K
    u_steel_cor_i = get_u_steel_cor_i(u_i=u_i, u_r_steel=u_r_steel)

    # 部分iの補正熱貫流率を考慮した場合の各層にかける熱抵抗の低減率
    c_res_i = get_c_steel_res_i(
        r_layers_i=r_layers_i, u_steel_cor_i=u_steel_cor_i, r_surf_i=r_surf_i, r_surf_o=r_surf_o)

    if c_res_i > 0.0:
        alt_layers_i = [make_alt_layer(layer_i_j, c_res_i) for layer_i_j in layers_i]
    else:
        alt_layers_i = []

    # 負荷計算用の境界iの層を作成する。
    # layer_i_j: 部分i の 層j
    layers_hlc_i = [a_01_04_make_layer_hlc(alt_layer_i_j) for alt_layer_i_j in alt_layers_i]

    # 負荷計算用の境界iの名前
    # parts にある名前をここに反映する。
    name_hlc_i = part_i['name']

    # 負荷計算用の境界iの面積比率
    # 面積比率法以外は必ず1.0になる。
    r_a_hlc_i = 1.0

    # 負荷計算用の境界iの一般部位の仕様
    general_part_spec_hlc_i = {
        'outside_emissivity': 0.9,
        'outside_solar_absorption': 0.8,
        'inside_heat_transfer_resistance': r_surf_i,
        'outside_heat_transfer_resistance': r_surf_o,
        'layers': layers_hlc_i,
    }

    # 直接U値を指定する方法は必ず配列長さは1になる。
    # 面積比率法の場合のみ、複数の配列長さになる。
    return [(name_hlc_i, r_a_hlc_i, general_part_spec_hlc_i, u_steel_cor_i)]


def get_u_steel_cor_i(u_i: float, u_r_steel: float) -> float:
    """
    部分iの補正熱貫流率を反映した熱貫流率を計算する。

    Args:
        u_i: 部分iの熱貫流率, W/m2K
        u_r_steel: 補正熱貫流率（熱橋）, W/m2K

    Returns:
        部分iの補正熱貫流率を反映した熱貫流率, W/m2K
    """

    return u_i + u_r_steel


def get_c_steel_res_i(r_layers_i: float, u_steel_cor_i: float, r_surf_i: float, r_surf_o: float) -> float:
    """
    Args:
        r_layers_i: 部分iの層の熱抵抗の合計（表面熱伝達抵抗を除く）, m2K/W
        u_steel_cor_i: 部分iの補正熱貫流率を反映した熱貫流率, W/m2K
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        部分iの補正熱貫流率を考慮した場合の各層にかける熱抵抗の低減率

    Notes:
        部分iの補正熱貫流率を考慮した場合の各層にかける熱抵抗の低減率は、理論上1未満の数。
        また、補正熱貫流率が極めて大きい場合は（実際には極めて大きいことは考えにくいが）計算上は0未満が発生する。
        その場合は、厚さや熱抵抗がゼロか負の値になってしまうので、
        この関数の引用元で、なんらかの配慮が必要。
    """

    # 部分iの補正熱貫流率を考慮した場合の層の熱抵抗の合計（表面熱伝達抵抗を除く）, m2K/W
    r_layers_steel_cor_i = 1 / u_steel_cor_i - r_surf_i - r_surf_o

    # 部分iの補正熱貫流率を考慮した場合の各層にかける熱抵抗の低減率
    c_steel_res_i = r_layers_steel_cor_i / r_layers_i

    return c_steel_res_i


def make_alt_layer(layer: Dict, c_steel_res_i: float) -> Dict:
    """
    Args:
        layer: 層
        c_steel_res_i: 部分iの補正熱貫流率を考慮した場合の各層にかける熱抵抗の低減率
    Returns:
        補正された層
    """

    if layer['heat_resistance_input_method'] == 'conductivity':
        return {
            'name': layer['name'],
            'heat_resistance_input_method': layer['heat_resistance_input_method'],
            'thermal_conductivity': layer['thermal_conductivity'],
            'thickness': layer['thickness'] * c_steel_res_i,
            'volumetric_specific_heat': layer['volumetric_specific_heat'],
        }
    elif layer['heat_resistance_input_method'] == 'resistance':
        return {
            'name': layer['name'],
            'heat_resistance_input_method': layer['heat_resistance_input_method'],
            'thermal_resistance': layer['thermal_resistance'] * c_steel_res_i,
            'thickness': layer['thickness'] * c_steel_res_i,
            'volumetric_specific_heat': layer['volumetric_specific_heat'],
        }
    else:
        raise KeyError()


# endregion


# region 鉄筋コンクリート造等


def get_rc_general_part_spec_hlc(parts: List[dict], r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    parts リストから parts_hlc リストを作成

    Args:
        parts: 一般部位の部分。リスト形式であるがリスト長は必ず1。
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K

    Notes:
        引数としてのpartsはリスト形式であるが、面積比率法を使用する場合以外は常にリスト長は1である。
        ここでは、リスト長が1以外であった場合のエラー処理も行う。
    """

    return get_general_part_spec_hlc(parts=parts, r_surf_i=r_surf_i, r_surf_o=r_surf_o)


# endregion


# region 共通項目


def get_general_part_spec_hlc(parts: List[dict], r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    parts リストから parts_hlc リストを作成

    Args:
        parts: 一般部位の部分。リスト形式であるがリスト長は必ず1。
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K

    Notes:
        引数としてのpartsはリスト形式であるが、面積比率法を使用する場合以外は常にリスト長は1である。
        ここでは、リスト長が1以外であった場合のエラー処理も行う。
    """

    # 引数としてのpartsはリスト形式であるが、面積比率法を使用する場合以外は常にリスト長は1である。
    if len(parts) != 1:
        raise ValueError('与えられたpartsのリスト数が1ではありません。')

    # 部分i
    part_i = parts[0]

    # 部分i の層
    layers_i = part_i['layers']

    # 部分iの熱貫流率, W/m2K
    u_i = a_01_04_get_u_i(layers_i=layers_i, r_i=r_surf_i, r_o=r_surf_o)

    # 負荷計算用の境界iの層を作成する。
    # layer_i_j: 部分i の 層j
    layers_hlc_i = [a_01_04_make_layer_hlc(layer_i_j) for layer_i_j in layers_i]

    # 負荷計算用の境界iの名前
    # parts にある名前をここに反映する。
    name_i = part_i['name']

    # 負荷計算用の境界iの面積比率
    # 面積比率法以外は必ず1.0になる。
    r_a_i = 1.0

    # 負荷計算用の境界iの一般部位の仕様
    general_part_spec_hlc_i = {
        'outside_emissivity': 0.9,
        'outside_solar_absorption': 0.8,
        'inside_heat_transfer_resistance': r_surf_i,
        'outside_heat_transfer_resistance': r_surf_o,
        'layers': layers_hlc_i,
    }

    # 直接U値を指定する方法は必ず配列長さは1になる。
    # 面積比率法の場合のみ、複数の配列長さになる。
    return [(name_i, r_a_i, general_part_spec_hlc_i, u_i)]


# endregion
