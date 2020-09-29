from typing import Dict, Tuple, List

from heat_load_calc.convert.a_01_01_general_part_u_value_directly \
    import get_wood_general_part_spec_hlc as a_01_01_get_wood_general_part_spec_hlc
from heat_load_calc.convert.a_01_01_general_part_u_value_directly \
    import get_steel_general_part_spec_hlc as a_01_01_get_steel_general_part_spec_hlc
from heat_load_calc.convert.a_01_01_general_part_u_value_directly \
    import get_rc_general_part_spec_hlc as a_01_01_get_rc_general_part_spec_hlc
from heat_load_calc.convert.a_01_01_general_part_u_value_directly \
    import get_other_general_part_spec_hlc as a_01_01_get_other_general_part_spec_hlc
from heat_load_calc.convert.a_01_02_general_part_detail_method \
    import get_wood_general_part_spec_hlc as a_01_02_get_wood_general_part_spec_hlc
from heat_load_calc.convert.a_01_02_general_part_detail_method \
    import get_rc_general_part_spec_hlc as a_01_02_get_rc_general_part_spec_hlc
from heat_load_calc.convert.a_01_02_general_part_detail_method \
    import get_steel_general_part_spec_hlc as a_01_02_get_steel_general_part_spec_hlc
from heat_load_calc.convert.a_01_03_general_part_area_ratio_method \
    import get_wood_general_part_spec_hlc as a_01_03_get_wood_general_part_spec_hlc
from heat_load_calc.convert.a_06_common_items import get_r_surf as a_06_get_r_surf

from heat_load_calc.convert import ees_house

def get_general_part_spec_hlc(gp_dict: Dict, gp: ees_house.GeneralPart) -> List[Tuple]:
    """

    Args:
        gp_dict: 一般部位
        gp: 一般部位

    Returns:
        以下のタプルを持つリスト
            (1) 名前
            (2) 面積比率
            (3) 負荷計算用一般部位の仕様
            (4) U値, W/m2K
    """

    gp_type = gp_dict['general_part_type']
    next_space = gp_dict['next_space']
    spec = gp_dict['spec']
    structure = spec['structure']

    r_surf_i, r_surf_o = a_06_get_r_surf(general_part_type=gp_type, next_space=next_space)

    # 木造
    # 一般部位における木造の評価方法については、以下の3種類
    #   1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
    #   2) 詳細入力法
    #   3) 面積比率法
    if structure == 'wood':

        method_wood = spec['u_value_input_method_wood']

        # 1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
        if method_wood == 'u_value_directly':

            return a_01_01_get_wood_general_part_spec_hlc(
                general_part_type=gp_type, u_target=spec['u_value'], r_surf_i=r_surf_i, r_surf_o=r_surf_o)

        # 2) 詳細入力法
        elif method_wood == 'detail_method':

            return a_01_02_get_wood_general_part_spec_hlc(
                parts=spec['parts'], r_surf_i=r_surf_i, r_surf_o=r_surf_o)

        # 3) 面積比率法
        elif method_wood == 'area_ratio_method':

            return a_01_03_get_wood_general_part_spec_hlc(
                general_part_type=gp_type, spec=spec, r_surf_i=r_surf_i, r_surf_o=r_surf_o)

        # 4) R値補正法（断熱材の仕様から簡易にU値を求める方法がリリースされるため将来的に廃止予定）
        elif method_wood == 'r_corrected_method':

            raise KeyError('熱貫流率補正法は実装していません。')

        else:

            raise ValueError()

    # 鉄骨造
    # 一般部位における鉄骨造の評価方法については、以下の2種類
    #   1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
    #   2) 詳細入力法（ただし、詳細に入力した場合に鉄骨ブレース等の熱橋の影響を補正するために、U値補正が入る。）
    #      この場合、断熱材の厚さ（熱抵抗）を調整して負荷計算用の層構成を作成する。
    elif structure == 'steel':

        method_steel = spec['u_value_input_method_steel']

        # 1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
        if method_steel == 'u_value_directly':

            return a_01_01_get_steel_general_part_spec_hlc(
                general_part_type=gp_type, u_target=spec['u_value'], r_surf_i=r_surf_i, r_surf_o=r_surf_o)

        # 2) 詳細入力法（ただし、詳細に入力した場合に鉄骨ブレース等の熱橋の影響を補正するために、U値補正が入る。）
        elif method_steel == 'detail_method':

            return a_01_02_get_steel_general_part_spec_hlc(
                u_r_steel=gp_dict['u_r_value_steel'], parts=spec['parts'], r_surf_i=r_surf_i, r_surf_o=r_surf_o)

        else:

            raise ValueError()

    # 鉄筋コンクリート造等
    # 一般部位における鉄筋コンクリート造等の評価方法については、以下の2種類
    #   1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
    #   2) 詳細入力法
    elif structure == 'rc':

        method_rc = spec['u_value_input_method_rc']

        # 1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
        if method_rc == 'u_value_directly':

            return a_01_01_get_rc_general_part_spec_hlc(
                general_part_type=gp_type, u_target=spec['u_value'], r_surf_i=r_surf_i, r_surf_o=r_surf_o)

        # 2) 詳細入力法
        elif method_rc == 'detail_method':

            return a_01_02_get_rc_general_part_spec_hlc(
                parts=spec['parts'], r_surf_i=r_surf_i, r_surf_o=r_surf_o)

        else:

            raise ValueError()

    # その他
    # 一般部位におけるその他造の評価方法については、以下の1種類
    #   1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
    #   ※ 詳細入力法は、S造のように熱橋等が存在せず、層で均一であること、
    #      あるいはそうみなされた計算方法が存在することが保証できないため設けない。
    elif structure == 'other':

        # 1) 直接U値を指定する方法（特別な試験や型式等により取得したU値を活用することを想定）
        return a_01_01_get_other_general_part_spec_hlc(
            general_part_type=gp_type, u_target=spec['u_value'], r_surf_i=r_surf_i, r_surf_o=r_surf_o)

    else:

        raise ValueError()
