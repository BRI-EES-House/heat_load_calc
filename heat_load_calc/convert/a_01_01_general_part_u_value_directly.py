from typing import List, Dict, Tuple

from heat_load_calc.convert.a_01_04_general_part_common_items import Layer
from heat_load_calc.convert.a_01_04_general_part_common_items import get_r_hlc_i as a_01_04_get_r_hlc_i
from heat_load_calc.convert.a_01_04_general_part_common_items import get_c_hlc_i as a_01_04_get_c_hlc_i

from heat_load_calc.convert import ees_house

# region 木造


def get_wood_general_part_spec_hlc(
        general_part_type: str, u_target: float, r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    直接U値を指定する方法から負荷計算用の一般部位の仕様を取得する。

    Args:
        general_part_type: 一般部位の種類
        u_target: 指定されたU値（このU値を満たすように断熱材厚みを調整する。）, W/m2K
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K
    """

    # 木造におけるデフォルトの層の構成（リスト）を取得する
    default_layers = get_wood_default_layers(general_part_type=general_part_type)

    # 取得した層の構成をもとに負荷計算用の層構成を取得する
    return get_general_part_spec_hlc(
        default_layers=default_layers, u_target=u_target, r_surf_i=r_surf_i, r_surf_o=r_surf_o)


def get_wood_default_layers(general_part_type: str) -> List[Layer]:
    """
    直接U値を指定する方法を採用した場合に、仮想的に想定する層のリストを定義する。

    Args:
        general_part_type: 一般部位の種類（以下の値をとる）

    Returns:
        層を構成する材料名のリスト（0番目は室内側）
    """

    return get_wood_steel_other_default_layers(general_part_type=general_part_type)


# endregion


# region 鉄骨造


def get_steel_general_part_spec_hlc(
        general_part_type: str, u_target: float, r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    直接U値を指定する方法から負荷計算用の一般部位の仕様を取得する。

    Args:
        general_part_type: 一般部位の種類
        u_target: 指定されたU値（このU値を満たすように断熱材厚みを調整する。）, W/m2K
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K
    """

    # 鉄骨造におけるデフォルトの層の構成（リスト）を取得する
    default_layers = get_steel_default_layers(general_part_type=general_part_type)

    # 取得した層の構成をもとに負荷計算用の層構成を取得する
    return get_general_part_spec_hlc(
        default_layers=default_layers, u_target=u_target, r_surf_i=r_surf_i, r_surf_o=r_surf_o)


def get_steel_default_layers(general_part_type: str) -> List[Layer]:
    """
    直接U値を指定する方法を採用した場合に、仮想的に想定する層の材料名称のリストを定義する。

    Args:
        general_part_type: 一般部位の種類（以下の値をとる）

    Returns:
        層を構成する材料名のリスト（0番目は室内側）
    """

    return get_wood_steel_other_default_layers(general_part_type=general_part_type)


# endregion


# region 鉄筋コンクリート造等


def get_rc_general_part_spec_hlc(
        general_part_type: str, u_target: float, r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    直接U値を指定する方法から負荷計算用の一般部位の仕様を取得する。

    Args:
        general_part_type: 一般部位の種類
        u_target: 指定されたU値（このU値を満たすように断熱材厚みを調整する。）, W/m2K
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K
    """

    # 鉄筋コンクリート造等におけるデフォルトの層の構成（リスト）を取得する
    default_layers = get_rc_default_layers(general_part_type=general_part_type)

    # 取得した層の構成をもとに負荷計算用の層構成を取得する
    return get_general_part_spec_hlc(
        default_layers=default_layers, u_target=u_target, r_surf_i=r_surf_i, r_surf_o=r_surf_o)


def get_rc_default_layers(general_part_type: str) -> List[Layer]:
    """
    直接U値を指定する方法を採用した場合に、仮想的に想定する層のリストを定義する。

    Args:
        general_part_type: 一般部位の種類

    Returns:
        層を構成する材料のリスト（配列番号は対象とする室側から数える）
    """

    return {
        # 屋根の場合：せっこうボード9.5mm + 断熱材 + コンクリート120mm
        'roof': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='concrete', method='conductivity', lambda_m=1.6, r_m=None, c_m=2000.0, t_m=0.120)
        ],
        # 天井の場合：せっこうボード9.5mm + 断熱材 + コンクリート120mm
        'ceiling': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='concrete', method='conductivity', lambda_m=1.6, r_m=None, c_m=2000.0, t_m=0.120)
        ],
        # 壁の場合：せっこうボード9.5mm + 断熱材 + コンクリート120mm
        'wall': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='concrete', method='conductivity', lambda_m=1.6, r_m=None, c_m=2000.0, t_m=0.120)
        ],
        # 床の場合：合板24mm + 断熱材 + コンクリート120mm
        'floor': [
            Layer(name='plywood', method='conductivity', lambda_m=0.16, r_m=None, c_m=720.0, t_m=0.024),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='concrete', method='conductivity', lambda_m=1.6, r_m=None, c_m=2000.0, t_m=0.120)
        ],
        # 壁の場合：せっこうボード9.5mm + 断熱材 + 合板12mm
        'boundary_wall': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
        ],
        # 間仕切り天井の場合：せっこうボード9.5mm + コンクリート120mm + 断熱材 + 合板24mm
        'upward_boundary_floor': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='concrete', method='conductivity', lambda_m=1.6, r_m=None, c_m=2000.0, t_m=0.120),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='plywood', method='conductivity', lambda_m=0.16, r_m=None, c_m=720.0, t_m=0.024),
        ],
        # 間仕切り床の場合： 合板24mm + 断熱材 + コンクリート120mm + せっこうボード9.5mm
        'downward_boundary_floor': [
            Layer(name='plywood', method='conductivity', lambda_m=0.16, r_m=None, c_m=720.0, t_m=0.024),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='concrete', method='conductivity', lambda_m=1.6, r_m=None, c_m=2000.0, t_m=0.120),
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
        ],
    }[general_part_type]


# endregion


# region その他


def get_other_general_part_spec_hlc(
        general_part_type: str, u_target: float, r_surf_i: float, r_surf_o: float, gp: ees_house.GeneralPart) -> List[Tuple]:
    """
    直接U値を指定する方法から負荷計算用の一般部位の仕様を取得する。

    Args:
        general_part_type: 一般部位の種類
        u_target: 指定されたU値（このU値を満たすように断熱材厚みを調整する。）, W/m2K
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K
    """

    # その他におけるデフォルトの層の構成（リスト）を取得する
    default_layers = get_other_default_layers(general_part_type=general_part_type)

    # 取得した層の構成をもとに負荷計算用の層構成を取得する
    v = get_general_part_spec_hlc(
        default_layers=default_layers, u_target=u_target, r_surf_i=r_surf_i, r_surf_o=r_surf_o)

    return v


def get_other_default_layers(general_part_type: str) -> List[Layer]:
    """
    直接U値を指定する方法を採用した場合に、仮想的に想定する層の材料名称のリストを定義する。

    Args:
        general_part_type: 一般部位の種類（以下の値をとる）

    Returns:
        層を構成する材料名のリスト（0番目は室内側）
    """

    return get_wood_steel_other_default_layers(general_part_type=general_part_type)


# endregion


# region 共通項目


def get_wood_steel_other_default_layers(general_part_type: str) -> List[Tuple]:
    """
    直接U値を指定する方法を採用した場合に、仮想的に想定する層のリストを定義する。

    Args:
        general_part_type: 一般部位の種類

    Returns:
        層を構成する材料のリスト（配列番号は対象とする室側から数える）

    Notes:
        この関数は木造・鉄骨造・その他／不明の場合共通である。
    """

    return {
        # 屋根の場合：せっこうボード9.5mm + 断熱材
        'roof': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None)
        ],
        # 天井の場合：せっこうボード9.5mm + 断熱材
        'ceiling': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None)
        ],
        # 壁の場合：せっこうボード9.5mm + 断熱材 + 合板12mm
        'wall': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='plywood', method='conductivity', lambda_m=0.16, r_m=None, c_m=720.0, t_m=0.012)
        ],
        # 床の場合：合板24mm + 断熱材
        'floor': [
            Layer(name='plywood', method='conductivity', lambda_m=0.16, r_m=None, c_m=720.0, t_m=0.024),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None)
        ],
        # 間仕切り壁の場合：せっこうボード9.5mm + 断熱材 + せっこうボード9.5mm
        'boundary_wall': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095)
        ],
        # 間仕切り天井の場合：せっこうボード9.5mm + 断熱材 + 合板24mm
        'upward_boundary_floor': [
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='plywood', method='conductivity', lambda_m=0.16, r_m=None, c_m=720.0, t_m=0.024)
        ],
        # 間仕切り床の場合： 合板24mm + 断熱材 + せっこうボード9.5mm
        'downward_boundary_floor': [
            Layer(name='plywood', method='conductivity', lambda_m=0.16, r_m=None, c_m=720.0, t_m=0.024),
            Layer(name='insulation', method='conductivity', lambda_m=0.045, r_m=None, c_m=13.0, t_m=None),
            Layer(name='gypsum_board', method='conductivity', lambda_m=0.221, r_m=None, c_m=830.0, t_m=0.0095)
        ],
    }[general_part_type]


def get_general_part_spec_hlc(
        default_layers: List[Layer], u_target: float, r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    直接U値を指定する方法において想定した層構成から負荷計算用一般部位の仕様を取得する。

    Args:
        default_layers: 直接U値を指定する方法において想定した層構成
        u_target: 指定されたU値（このU値を満たすように断熱材の厚さを調整する）, W/m2K
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K

    Notes:
        default_layers において断熱材の層は必ず1層であることを前提としている。
        0層の場合はエラーにはならないが、目標とするU値を満たすことはできない。（断熱材厚さで調整できないため。）
        また、複数層あった場合、目標とする断熱材の厚さが、複数層に対して同じ値が入ってしまう。
    """

    # 断熱材以外の熱抵抗の合計, m2K/W
    r_others_sum = get_r_others_sum(default_layers)

    # 目標とする断熱材の厚さ, m
    t_ins = get_t_ins(
        u_target=u_target, r_surf_o=r_surf_o, r_surf_i=r_surf_i, r_others_sum=r_others_sum)

    # 負荷計算用の層を作成する。
    layers_hlc = [make_layer_hlc(default_layer, t_ins) for default_layer in default_layers]

    # 負荷計算用の境界iの名前
    # parts にある名前をここに反映する。
    # しかし、U値を指定する場合、parts が無いので、ここは無し。
    name_hlc_i = ""

    # 負荷計算用の境界iの面積比率
    # 面積比率法以外は必ず1.0になる。
    r_a_hlc_i = 1.0

    # 負荷計算用の一般部位の仕様
    general_part_spec_hlc = {
        'outside_emissivity': 0.9,
        'outside_solar_absorption': 0.8,
        'inside_heat_transfer_resistance': r_surf_i,
        'outside_heat_transfer_resistance': r_surf_o,
        'layers': layers_hlc,
    }

    # 直接U値を指定する方法は必ず配列長さは1になる。
    # 面積比率法の場合のみ、複数の配列長さになる。
    return [(name_hlc_i, r_a_hlc_i, general_part_spec_hlc, u_target)]


def get_r_others_sum(default_layers: List[Layer]) -> float:
    """
    断熱材を除く層の熱抵抗の合計値を積算する。

    Args:
        default_layers: デフォルトで想定されている層

    Returns:
        断熱材を除く層の熱抵抗の合計, m2K/W
    """

    # 層の名前が断熱材でない場合に、厚さ÷熱伝導率 から各層の熱抵抗を算出し合計する
    return sum([layer.t_m / layer.lambda_m for layer in default_layers if layer.name != 'insulation'])


def get_t_ins(u_target: float, r_surf_o: float, r_surf_i: float, r_others_sum: float) -> float:
    """
    目標とする断熱材の厚さを算出する。

    Args:
        u_target: 目標とするU値, W/m2K
        r_surf_o: 室外側熱伝達抵抗, m2K/W
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_others_sum: 断熱材以外の層の熱抵抗の合計, m2K/W

    Returns:
        断熱材の厚さ, m
    """

    # 断熱材の熱伝導率, W/mK
    lambda_res = 0.045

    # 目標U値の逆数から目標R値をだす。
    # 次に室内側と室外側の熱伝達抵抗、および断熱材を除く層の熱抵抗を減じ、目標とする断熱材の熱抵抗をだす。
    r_res_target = 1 / u_target - r_surf_o - r_others_sum - r_surf_i

    # もし目標とする断熱材の熱抵抗値が0を下回っている場合は、目標とする断熱材の熱抵抗値を0とする。
    # この場合、無断熱になることを意味する。
    # また、目標とするU値を満たさないことになる。
    r_res_target = 0.0 if r_res_target < 0.0 else r_res_target

    # 目標とする断熱材の熱抵抗(m2K/W)に熱伝導率(W/mK)を乗じて目標とする厚さ(m)をだす。
    return r_res_target * lambda_res


def make_layer_hlc(default_layer_i: Layer, t_ins: float) -> Dict:
    """
    層(1つ)から負荷計算用の層を作成する。

    Args:
        default_layer_i: 層i
        t_ins: 目標とする断熱材の厚さ, m

    Returns:
        負荷計算用の層
    """

    # 層iにおける厚さ, m
    # 層の名前が断熱材の場合は、目標とする断熱材の厚さを使用する。
    # 断熱材以外の場合は、最初に想定した値を使用する。
    t_i = t_ins if default_layer_i.name == 'insulation' else default_layer_i.t_m

    # 負荷計算用の層を作成する。
    # 名前はデバッグ用にあったら便利なので作成
    # 応答係数法においては熱抵抗(m2K/W)と熱容量(kJ/m2K)があればよい。
    # 熱容量は層iの材料の容積比熱（単位体積あたりの熱容量）ではなくて単位面積あたりの層の熱容量であることに注意。
    return {
        'name': default_layer_i.name,
        'thermal_resistance': a_01_04_get_r_hlc_i(lambda_i=default_layer_i.lambda_m, t_i=t_i),
        'thermal_capacity': a_01_04_get_c_hlc_i(c_m_i=default_layer_i.c_m, t_i=t_i),
    }


# endregion
