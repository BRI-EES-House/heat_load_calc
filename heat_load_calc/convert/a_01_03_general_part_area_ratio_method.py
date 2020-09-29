from typing import Dict, List, Tuple

from heat_load_calc.convert.a_01_04_general_part_common_items import get_u_i as a_01_04_get_u_i
from heat_load_calc.convert.a_01_04_general_part_common_items import make_layer_hlc as a_01_04_make_layer_hlc


def get_wood_general_part_spec_hlc(general_part_type: str, spec: Dict, r_surf_i: float, r_surf_o: float) -> List[Tuple]:
    """
    面積比率法を用いてpartsリストを作成
    Args:
        general_part_type: 一般部位の種類（以下の値をとる）
            ceiling: 天井
            roof: 屋根
            wall: 壁
            floor: 床
            boundary_wall: 界壁
            upward_boundary_floor: 上界側界床
            downward_boundary_floor: 下界側界床
        spec: 仕様。以下の辞書型
                structure(str): 構造種別（以下の値をとる）
                    wood: 木造
                    rc: 鉄筋コンクリート造等
                    steel: 鉄骨造
                    other: その他／不明
                u_value_input_method_wood(str): U値の入力方法（木造）（以下の値をとる）
                    u_value_directly: U値を入力
                    detail_method: 詳細計算法
                    area_ratio_method: 面積比率法
                    r_corrected_mothod: 熱貫流率補正法
                u_value_input_method_rc(str): U値の入力方法（鉄筋コンクリート造等）（以下の値をとる）
                    u_value_directly(str): U値を入力
                    detail_method(str): 詳細計算法
                u_value_input_method_steel(str):U値の入力方法（鉄骨造）（以下の値をとる）
                    u_value_directly(str): U値を入力
                    detail_method(str): 詳細計算法
                u_value(float): 熱貫流率
                floor_construction_method(str): 床の工法の種類（以下の値をとる）
                    frame_beam_joist_insulation: 軸組構法・床梁工法（根太間に断熱）
                    footing_joist_insulation: 軸組構法・束立大引工法（根太間に断熱）
                    footing_sleeper_insulation: 軸組構法・束立大引工法（大引間に断熱）
                    footing_joist_sleeper_insulation: 軸組構法・束立大引工法（根太間及び大引間に断熱）
                    rigid_floor: 軸組構法・剛床工法
                    same_surface_joist_insulation: 軸組構法・床梁土台同面工法（根太間に断熱）
                    frame_wall_joist_insulation: 枠組壁工法（根太間に断熱）
                wall_construction_method(str): 壁の工法の種類（以下の値をとる）
                    frame_beam: 軸組構法（柱・間柱間に断熱）
                    frame_beam_additional_insulation_horizontal: 軸組構法（柱・間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
                    frame_beam_additional_insulation_vertical: 軸組構法（柱、間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））
                    frame_wall: 枠組壁工法（たて枠間に断熱）
                    frame_wall_additional_insulation_horizontal: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
                    frame_wall_additional_insulation_vertical: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））
                ceiling_construction_method(str):天井の工法の種類（以下の値をとる）
                    beam_insulation: 桁・梁間に断熱
                roof_construction_method(str):屋根の工法の種類（以下の値をとる）
                    rafter_insulation: たるき間に断熱
                    rafter_additional_insulation: たるき間に断熱し付加断熱（横下地）
                parts: 一般部位の部分。リスト形式。面積比率法に限り要素数は1以上をとり得る。以下の辞書型のリスト。
                    name(str) : 部分の名称
                    part_type(str) : 部分の種類（以下の値をとる）
                        ins: 断熱
                        hb: 熱橋
                        ins_ins:
                        ins_ins: 断熱＋断熱
                        ins_hb: 断熱＋熱橋
                        hb_ins: 熱橋＋断熱
                        hb_hb: 熱橋＋熱橋
                        magsa_ins: まぐさ＋断熱
                        magsa_hb: まぐさ＋熱橋
                    layers(List[dict]) : 層の物性値（層の名前・断熱性能の入力方法・熱伝導率・熱抵抗・容積比熱・厚さからなる辞書）のリスト
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W
    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K
    """

    # 面積比を取得
    # area_ratio は第一引数は部分の種類、第二引数は面積比率
    area_ratios = get_area_ratios(general_part_type, spec)

    parts = spec['parts']

    return [get_wood_general_part_spec_hlc_i(area_ratio_i, parts, r_surf_i=r_surf_i, r_surf_o=r_surf_o)
            for area_ratio_i in area_ratios]


def get_wood_general_part_spec_hlc_i(area_ratio_i: Tuple, parts: Dict, r_surf_i: float, r_surf_o: float) -> Tuple:
    """
    parts リストから parts_hlc リストを作成

    Args:
        area_ratio_i: 以下の変数をとるタプル
            (1) 部分の種類
            (2) 面積比率
        parts: 一般部位の部分。リスト形式であるがリスト長は必ず1。
        r_surf_i: 室内側熱伝達抵抗, m2K/W
        r_surf_o: 室外側熱伝達抵抗, m2K/W

    Returns:
        以下のタプル
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K
    """

    # area_ratio は第一引数は部分の種類、第二引数は面積比率
    part_type_i = area_ratio_i[0]
    r_a_i = area_ratio_i[1]

    # 部分の種類が、'ins', 'hb'...等適切に指定されているか、また、その数は唯一であるかをチェックする。
    ps = [p for p in parts if p['part_type'] == part_type_i]

    if len(ps) != 1:
        raise ValueError('部分partsの種類part_typeに適切な値が設定されていないか又は複数の値が設定されています。')

    # 部分i
    part_i = ps[0]

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

    # 負荷計算用の境界iの一般部位の仕様
    general_part_spec_hlc_i = {
        'outside_emissivity': 0.9,
        'outside_solar_absorption': 0.8,
        'inside_heat_transfer_resistance': r_surf_i,
        'outside_heat_transfer_resistance': r_surf_o,
        'layers': layers_hlc_i,
    }

    return name_i, r_a_i, general_part_spec_hlc_i, u_i


def get_area_ratios(general_part_type: str, spec: Dict) -> List[Tuple[str, float]]:
    """
    一般部位の部分の面積比率を取得する

    Args:
        general_part_type: 一般部位の種類
        spec: 仕様

    Returns:
        面積比率の辞書型（keyは以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分(柱・間柱間断熱材+付加断熱材)
            ins_hb: 断熱部分+熱橋部分(柱・間柱間断熱材+付加断熱層内熱橋部)
            hb_ins: 断熱部分＋熱橋部分(構造部材等+付加断熱材)
            hb_hb: 熱橋部分(構造部材等+付加断熱層内熱橋部)
            magsa_ins: 断熱部分＋熱橋部分(まぐさ+付加断熱材)
            magsa_hb: 熱橋部分(まぐさ+付加断熱層内熱橋部)
    """

    # 一般部位の種類が床・階天井・階床の場合
    if general_part_type == 'floor'\
            or general_part_type == 'upward_boundary_floor' \
            or general_part_type == 'downward_boundary_floor':

        return get_area_ratio_wood_floor(spec['floor_construction_method'])

    # 一般部位の種類が壁の場合
    elif general_part_type == 'wall' \
            or general_part_type == 'boundary_wall':

        return get_area_ratio_wood_wall(spec['wall_construction_method'])

    # 一般部位の種類が天井の場合
    elif general_part_type == 'ceiling':

        return get_area_ratio_wood_ceiling(spec['ceiling_construction_method'])

    # 一般部位の種類が屋根の場合
    elif general_part_type == 'roof':

        return get_area_ratio_wood_roof(spec['roof_construction_method'])

    else:

        raise ValueError()


def get_area_ratio_wood_floor(floor_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造床の部分の面積比率を取得する

    Args:
        floor_construction_method: 床の工法種類（以下の値をとる）
            1 frame_beam_joist_insulation: 軸組構法・床梁工法（根太間に断熱）
            2 footing_joist_insulation: 軸組構法・束立大引工法（根太間に断熱）
            3 footing_sleeper_insulation: 軸組構法・束立大引工法（大引間に断熱）
            4 footing_joist_sleeper_insulation: 軸組構法・束立大引工法（根太間及び大引間に断熱）
            5 rigid_floor: 軸組構法・剛床工法
            6 same_surface_joist_insulation: 軸組構法・床梁土台同面工法（根太間に断熱）
            7 frame_wall_joist_insulation: 枠組壁工法（根太間に断熱）

    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分(根太間断熱材+大引間断熱材)
            ins_hb: 断熱部分+熱橋部分(根太間断熱材+大引材等)
            hb_ins: 断熱部分＋熱橋部分(根太材+大引間断熱材)
            hb_hb: 熱橋部分(根太材+大引材等)
    """

    return {
        'frame_beam_joist_insulation': [('ins', 0.80), ('hb', 0.20)],
        'footing_joist_insulation': [('ins', 0.80), ('hb', 0.20)],
        'footing_sleeper_insulation': [('ins', 0.85), ('hb', 0.15)],
        'footing_joist_sleeper_insulation': [
            ('ins_ins', 0.72), ('ins_hb', 0.12), ('hb_ins', 0.13), ('hb_hb', 0.03)],
        'rigid_floor': [('ins', 0.85), ('hb', 0.15)],
        'same_surface_joist_insulation': [('ins', 0.70), ('hb', 0.30)],
        'frame_wall_joist_insulation': [('ins', 0.87), ('hb', 0.13)]
    }[floor_construction_method]


def get_area_ratio_wood_wall(wall_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造壁の部分の面積比率を取得する

    Args:
        wall_construction_method: 壁の工法種類（以下の値をとる）
            1 frame_beam:軸組構法（柱・間柱間に断熱）
            2 frame_beam_additional_insulation_horizontal: 軸組構法（柱・間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
            3 frame_beam_additional_insulation_vertical: 軸組構法（柱、間柱間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））
            4 frame_wall: 枠組壁工法（たて枠間に断熱）
            5 frame_wall_additional_insulation_horizontal: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「横下地」））
            6 frame_wall_additional_insulation_vertical: 枠組壁工法（たて枠間に断熱し付加断熱（付加断熱層内熱橋部分が「縦下地」））

    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分(柱・間柱間断熱材+付加断熱材)
            ins_hb: 断熱部分+熱橋部分(柱・間柱間断熱材+付加断熱層内熱橋部)
            hb_ins: 断熱部分＋熱橋部分(構造部材等+付加断熱材)
            hb_hb: 熱橋部分(構造部材等+付加断熱層内熱橋部)
            magsa_ins: 断熱部分＋熱橋部分(まぐさ+付加断熱材)
            magsa_hb: 熱橋部分(まぐさ+付加断熱層内熱橋部)
    """

    return {
        'frame_beam': [('ins', 0.83), ('hb', 0.17)],
        'frame_beam_additional_insulation_horizontal': [
            ('ins_ins', 0.75), ('ins_hb', 0.08), ('hb_ins', 0.12), ('hb_hb', 0.05)],
        'frame_beam_additional_insulation_vertical': [
            ('ins_ins', 0.79), ('ins_hb', 0.04), ('hb_ins', 0.04), ('hb_hb', 0.13)],
        'frame_wall': [
            ('ins', 0.77), ('hb', 0.23)],
        'frame_wall_additional_insulation_horizontal': [
            ('ins_ins', 0.69), ('ins_hb', 0.08), ('hb_ins', 0.14),
            ('magsa_ins', 0.02), ('hb_hb', 0.06), ('magsa_hb', 0.01)],
        'frame_wall_additional_insulation_vertical': [
            ('ins_ins', 0.76), ('ins_hb', 0.01), ('magsa_ins', 0.02), ('hb_hb', 0.20), ('magsa_hb', 0.01)]
    }[wall_construction_method]


def get_area_ratio_wood_ceiling(ceiling_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造天井の部分の面積比率を取得する

    Args:
        ceiling_construction_method: 天井の工法種類（以下の値をとる）
            1 beam_insulation: 桁・梁間に断熱

    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
    """

    return {
        'beam_insulation': [('ins', 0.83), ('hb', 0.17)]
    }[ceiling_construction_method]


def get_area_ratio_wood_roof(roof_construction_method: str) -> List[Tuple[str, float]]:
    """
    面積比率法において木造屋根の部分の面積比率を取得する

    Args:
        roof_construction_method: 屋根の工法種類（以下の値をとる）
            rafter_insulation: たるき間に断熱
            rafter_additional_insulation: たるき間に断熱し付加断熱（横下地）

    Returns:
        タプル（部分の種類, 面積比率）のリスト　（部分の種類は以下の値をとる）
            ins: 断熱部分
            hb: 熱橋部分
            ins_ins: 断熱部分（たる木間断熱材＋付加断熱材）
            ins_hb: 断熱部分＋熱橋部分（たる木間断熱材＋付加断熱層内熱橋部（下地たる木））
            hb_ins: 断熱部分＋熱橋部分（構造部材＋付加断熱材）
            hb_hb: 熱橋部分（構造部材＋付加断熱層内熱橋部（下地たる木））
    """

    return {
        'rafter_insulation': [('ins', 0.86), ('hb', 0.14)],
        'rafter_additional_insulation': [
            ('ins_ins', 0.79), ('ins_hb', 0.08), ('hb_ins', 0.12), ('hb_hb', 0.019)],
    }[roof_construction_method]
