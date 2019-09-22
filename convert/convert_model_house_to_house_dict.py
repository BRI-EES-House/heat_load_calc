from typing import Optional, List, Dict, Union, Tuple


def get_general_part(
        name: str, general_part_type: str, next_space: str, direction: str, area: float
) -> Dict[str, Optional[Union[str, float]]]:
    """
    Args:
        name: 名称
        general_part_type: 種類
            ( = 'roof', 'ceiling', 'wall', 'floor', 'boundary_wall', 'upward_boundary_floor', 'downward_boundary_floor')
        next_space: 隣接空間の種類
            ( = 'outdoor', 'open_space', 'closed_space', 'open_underfloor', 'air_conditioned', 'closed_underfloor')
        direction: 方位
            ( = 'top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'bottom', 'upward', 'horizontal', 'downward')
        area: 面積, m2
    Returns:
        一般部位の辞書（リスト）
    """

    return {
        'name': name,
        'general_part_type': general_part_type,
        'next_space': next_space,
        'direction': direction,
        'area': area,
        'space_type': None,
        'spec': None
    }


def get_window(name: str, next_space: str, direction: str, area: float) -> Dict[str, Optional[Union[str, float]]]:
    """
    Args:
        name: 名称
        next_space: 隣接空間の種類
            ( = 'outdoor', 'open_space', 'closed_space', 'open_underfloor', 'air_conditioned', 'closed_underfloor')
        direction: 方位
            ( = 'top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'bottom', 'upward', 'horizontal', 'downward')
        area: 面積, m2
    Returns:
        窓の辞書（リスト）
    """

    return {
        'name': name,
        'next_space': next_space,
        'direction': direction,
        'area': area,
        'space_type': None,
        'spec': None
    }


def get_door(name: str, next_space: str, direction: str, area: float) -> Dict[str, Optional[Union[str, float]]]:
    """
    Args:
        name: 名称
        next_space: 隣接空間の種類
            ( = 'outdoor', 'open_space', 'closed_space', 'open_underfloor', 'air_conditioned', 'closed_underfloor')
        direction: 方位
            ( = 'top', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'bottom', 'upward', 'horizontal', 'downward')
        area: 面積, m2
    Returns:
        ドアの辞書（リスト）
    """

    return {
        'name': name,
        'next_space': next_space,
        'direction': direction,
        'area': area,
        'space_type': None,
        'spec': None
    }


def get_earth_floor(name: str, area: float) -> Dict[str, Optional[Union[str, float]]]:
    """
    Args:
        name: 名称
        area: 面積, m2
    Returns:
        土間床中央部の辞書（リスト）
    """
    return {
        'name': name,
        'area': area,
        'space_type': None,
        'spec': None
    }


def get_earth_floor_perimeter(name: str, next_space: str, length: float) -> Dict[str, Optional[Union[str, float]]]:
    """
    Args:
        name: 名称
        next_space: 隣接空間の種類
            ( = 'outdoor', 'open_space', 'closed_space', 'open_underfloor', 'air_conditioned', 'closed_underfloor')
        length: 長さ, m
    Returns:
        土間床周辺部の辞書（リスト）
    """

    return {
        'name': name,
        'next_space': next_space,
        'length': length,
        'space_type': None,
        'spec': None,
    }


def convert(
        house_type: str, floor_ins_type: str,
        a_evp_ef_total, a_evp_f_total,
        l_base_total_outside, l_base_total_inside,
        a_evp_roof: float,
        a_evp_base_total_outside, a_evp_base_total_inside,
        a_evp_window: (float, float, float, float),
        a_evp_door: (float, float, float, float),
        a_evp_wall: (float, float, float, float), **kwargs):
    """
    Args:
        house_type: 住戸の種類(= 'detached' or 'attached')
        floor_ins_type: 床の断熱の種類(= 'floor' or 'base')
        a_evp_ef_total: 土間床の面積, m2
        a_evp_f_total: （床下を持つ）床の面積, m2
        l_base_total_outside: 土間床周辺部（外気側）の長さ, m
        l_base_total_inside: 土間床周辺部（室内側）の長さ, m
        a_evp_roof: 屋根の面積, m2
        a_evp_base_total_outside: 基礎（外気側）の面積, m2
        a_evp_base_total_inside: 基礎（室内側）の面積, m2
        a_evp_window: 各方位の窓の面積, m2
        a_evp_door: 各方位のドアの面積, m2
        a_evp_wall: 各方位の壁の面積, m2
        **kwargs:

    Returns:

    """

    # roof
    if house_type == 'detached':
        part_roof = [
            get_general_part(
                name='roof', general_part_type='ceiling', next_space='outdoor',direction='top', area=a_evp_roof
            )
        ]
    elif house_type == 'attached':
        part_roof = [
            get_general_part(
                name='roof', general_part_type='upward_boundary_floor', next_space='air_conditioned',
                direction='upward', area=a_evp_roof
            )
        ]
    else:
        raise Exception

    # wall
    if house_type == 'detached':
        part_wall = [
            get_general_part(
                name='wall_sw', general_part_type='wall', next_space='outdoor', direction='sw', area=a_evp_wall[0]
            ),
            get_general_part(
                name='wall_nw', general_part_type='wall', next_space='outdoor', direction='nw', area=a_evp_wall[1]
            ),
            get_general_part(
                name='wall_ne', general_part_type='wall', next_space='outdoor', direction='ne', area=a_evp_wall[2]
            ),
            get_general_part(
                name='wall_se', general_part_type='wall', next_space='outdoor', direction='se', area=a_evp_wall[3]
            )
        ]
    elif house_type == 'attached':
        part_wall = [
            get_general_part(
                name='wall_sw', general_part_type='wall', next_space='outdoor', direction='sw', area=a_evp_wall[0]
            ),
            get_general_part(
                name='wall_nw', general_part_type='wall', next_space='outdoor', direction='nw', area=a_evp_wall[1]
            ),
            get_general_part(
                name='wall_ne', general_part_type='wall', next_space='open_space',
                direction='horizontal', area=a_evp_wall[2]
            ),
            get_general_part(
                name='wall_se', general_part_type='boundary_wall', next_space='air_conditioned',
                direction='horizontal', area=a_evp_wall[3]
            )
        ]
    else:
        raise Exception

    # window
    if house_type == 'detached':
        part_window = [
            get_window(name='window_sw', next_space='outdoor', direction='sw', area=a_evp_window[0]),
            get_window(name='window_nw', next_space='outdoor', direction='nw', area=a_evp_window[1]),
            get_window(name='window_ne', next_space='outdoor', direction='ne', area=a_evp_window[2]),
            get_window(name='window_se', next_space='outdoor', direction='se', area=a_evp_window[3]),
        ]
    elif house_type == 'attached':
        if a_evp_window[3] > 0.0:
            raise Exception('集合住宅において、Direction 270 側に窓が設定（面積が0より大）されました。')
        part_window = [
            get_window(name='window_sw', next_space='outdoor', direction='sw', area=a_evp_window[0]),
            get_window(name='window_nw', next_space='outdoor', direction='nw', area=a_evp_window[1]),
            get_window(name='window_ne', next_space='open_space', direction='horizontal', area=a_evp_window[2]),
        ]
    else:
        raise Exception

    # door
    if house_type == 'detached':
        if a_evp_door[0] > 0.0:
            raise Exception('戸建て住宅において、Direction 0 側にドアが設定（面積が0より大）されました。')
        if a_evp_door[3] > 0.0:
            raise Exception('戸建て住宅において、Direction 270 側にドアが設定（面積が0より大）されました。')
        part_door = [
            get_door(name='door_nw', next_space='outdoor', direction='nw', area=a_evp_door[1]),
            get_door(name='door_ne', next_space='outdoor', direction='ne', area=a_evp_door[2]),
        ]
    elif house_type == 'attached':
        if a_evp_door[0] > 0.0:
            raise Exception('集合住宅において、Direction 0 側にドアが設定（面積が0より大）されました。')
        if a_evp_door[1] > 0.0:
            raise Exception('集合住宅において、Direction 90 側にドアが設定（面積が0より大）されました。')
        if a_evp_door[3] > 0.0:
            raise Exception('集合住宅において、Direction 270 側にドアが設定（面積が0より大）されました。')
        part_door = [
            get_door(name='door_ne', next_space='open_space', direction='horizontal', area=a_evp_door[2]),
        ]
    else:
        raise Exception

    # earth_floor
    if house_type == 'detached':
        part_earth_floor = [
            get_earth_floor(name='earth_floor', area=a_evp_ef_total)
        ]
    elif house_type == 'attached':
        if a_evp_ef_total > 0.0:
            raise Exception('集合住宅において土間床が設定（面積が0より大）されました。')
        part_earth_floor = []
    else:
        raise Exception

    # floor
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            part_floor = [
                get_general_part(
                    name='floor', general_part_type='floor', next_space='open_underfloor',
                    direction='downward', area=a_evp_f_total
                )
            ]
        elif floor_ins_type == 'base':
            if a_evp_f_total > 0.0:
                raise Exception('戸建住宅の基礎断熱住宅において床が設定（面積が0より大）されました。')
            part_floor = []
        else:
            raise Exception
    elif house_type == 'attached':
        part_floor = [
            get_general_part(
                name='floor', general_part_type='downward_boundary_floor', next_space='air_conditioned',
                direction='downward', area=a_evp_f_total
            )
        ]
    else:
        raise Exception

    # base outside
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            if a_evp_base_total_outside[0] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 0 側に基礎が設定（面積が0より大）されました。')
            if a_evp_base_total_outside[3] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 270 側に基礎が設定（面積が0より大）されました。')
            part_base_outside = [
                get_general_part(
                    name='base_outside_nw', general_part_type='wall', next_space='outdoor',
                    direction='nw', area=a_evp_base_total_outside[1]
                ),
                get_general_part(
                    name='base_outside_ne', general_part_type='wall', next_space='outdoor',
                    direction='ne', area=a_evp_base_total_outside[2]
                )
            ]
        elif floor_ins_type == 'base':
            part_base_outside = [
                get_general_part(
                    name='base_outside_sw', general_part_type='wall', next_space='outdoor',
                    direction='sw', area=a_evp_base_total_outside[0]
                ),
                get_general_part(
                    name='base_outside_nw', general_part_type='wall', next_space='outdoor',
                    direction='nw', area=a_evp_base_total_outside[1]
                ),
                get_general_part(
                    name='base_outside_ne', general_part_type='wall', next_space='outdoor',
                    direction='ne', area=a_evp_base_total_outside[2]
                ),
                get_general_part(
                    name='base_outside_se', general_part_type='wall', next_space='outdoor',
                    direction='se', area=a_evp_base_total_outside[3]
                )
            ]
        else:
            raise Exception
    elif house_type == 'attached':
        if a_evp_base_total_outside[0] > 0.0:
            raise Exception('集合住宅において、Direction 0 側に基礎が設定（面積が0より大）されました。')
        if a_evp_base_total_outside[1] > 0.0:
            raise Exception('集合住宅において、Direction 90 側に基礎が設定（面積が0より大）されました。')
        if a_evp_base_total_outside[2] > 0.0:
            raise Exception('集合住宅において、Direction 180 側に基礎が設定（面積が0より大）されました。')
        if a_evp_base_total_outside[3] > 0.0:
            raise Exception('集合住宅において、Direction 270 側に基礎が設定（面積が0より大）されました。')
        part_base_outside = []
    else:
        raise Exception

    # base inside
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            part_base_inside = [
                get_general_part(
                    name='base_iside', general_part_type='wall', next_space='open_underfloor',
                    direction='horizontal', area=a_evp_base_total_inside
                )
            ]
        elif floor_ins_type == 'base':
            if a_evp_base_total_inside > 0.0:
                raise Exception('戸建住宅（基礎断熱）において、基礎（室内側）が設定（面積が0より大）されました。')
            part_base_inside = []
        else:
            raise Exception
    elif house_type == 'attached':
        if a_evp_base_total_inside > 0.0:
            raise Exception('集合住宅において、基礎（室内側）が設定（面積が0より大）されました。')
        part_base_inside = []
    else:
        raise Exception

    # earth floor perimeter outside
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            if l_base_total_outside[0] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 0 側に土間床周辺部が設定（長さが0より大）されました。')
            if l_base_total_outside[3] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 270 側に土間床周辺部が設定（長さが0より大）されました。')
            part_earth_floor_perimeter_outside = [
                get_earth_floor_perimeter(
                    name='earth_floor_perimeter_nw', next_space='outdoor', length=l_base_total_outside[1]
                ),
                get_earth_floor_perimeter(
                    name='earth_floor_perimeter_ne', next_space='outdoor', length=l_base_total_outside[2]
                )
            ]
        elif floor_ins_type == 'base':
            part_earth_floor_perimeter_outside = [
                get_earth_floor_perimeter(
                    name='earth_floor_perimeter_sw', next_space='outdoor', length=l_base_total_outside[0]
                ),
                get_earth_floor_perimeter(
                    name='earth_floor_perimeter_nw', next_space='outdoor', length=l_base_total_outside[1]
                ),
                get_earth_floor_perimeter(
                    name='earth_floor_perimeter_ne', next_space='outdoor', length=l_base_total_outside[2]
                ),
                get_earth_floor_perimeter(
                    name='earth_floor_perimeter_se', next_space='outdoor', length=l_base_total_outside[3]
                )
            ]
        else:
            raise Exception
    elif house_type == 'attached':
        if l_base_total_outside[0] > 0.0:
            raise Exception('集合住宅において、Direction 0 側に土間床周辺部が設定（長さが0より大）されました。')
        if l_base_total_outside[1] > 0.0:
            raise Exception('集合住宅において、Direction 90 側に土間床周辺部が設定（長さが0より大）されました。')
        if l_base_total_outside[2] > 0.0:
            raise Exception('集合住宅において、Direction 180 側に土間床周辺部が設定（長さが0より大）されました。')
        if l_base_total_outside[3] > 0.0:
            raise Exception('集合住宅において、Direction 270 側に土間床周辺部が設定（長さが0より大）されました。')
        part_earth_floor_perimeter_outside = []
    else:
        raise Exception

    # base inside
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            part_earth_floor_perimeter_inside = [
                get_earth_floor_perimeter(
                    name='earth_floor_perimeter_inside', next_space='open_underfloor', length=l_base_total_inside
                )
            ]
        elif floor_ins_type == 'base':
            if l_base_total_inside > 0.0:
                raise Exception('戸建住宅（基礎断熱）において、土間床周辺部（室内側）が設定（長さが0より大）されました。')
            part_earth_floor_perimeter_inside = []
        else:
            raise Exception
    elif house_type == 'attached':
        if l_base_total_inside > 0.0:
            raise Exception('集合住宅において、土間床周辺部（室内側）が設定（長さが0より大）されました。')
        part_earth_floor_perimeter_inside = []
    else:
        raise Exception

    return {
        'general_parts': part_roof + part_wall + part_floor + part_base_outside + part_base_inside,
        'windows': part_window,
        'doors': part_door,
        'earthfloor_perimeters': part_earth_floor_perimeter_outside + part_earth_floor_perimeter_inside,
        'earthfloor_centers': part_earth_floor,
    }


if __name__ == '__main__':

    mh1 = {
        'house_type': 'detached',
        'floor_ins_type': 'floor',
        'bath_ins_type': 'base',
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843,
        'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 3.185,
        'a_evp_ef_bath': 3.3124000000000002,
        'a_evp_f_bath': 0.0,
        'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
        'l_base_bath_inside': 3.64,
        'f_s': [1.0800250894877579, 1.0400241602474705],
        'l_prm': [30.805513843979707, 26.030553554896883],
        'l_ms': [10.610634821709455, 8.295602321670247],
        'l_os': [4.792122100280398, 4.719674455778196],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 5.7967,
        'a_evp_f_other': 45.05075762711864,
        'a_evp_f_total': 45.05075762711864,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 3.64, 3.185, 0.0),
        'l_base_total_inside': 6.825,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.5733,
        'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
        'a_evp_base_bath_inside': 1.82,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 1.2376, 1.1557, 0.0),
        'a_evp_base_total_inside': 2.3933,
        'a_evp_srf': (
            [30.77084098295742, 22.398126268509667],
            [13.897154090813155, 12.74312103060113],
            [30.77084098295742, 22.398126268509667],
            [13.897154090813155, 12.74312103060113]
        ),
        'a_evp_total_not_base': 261.3134,
        'a_evp_total': 266.1,
        'a_evp_open_total': 36.583876000000004,
        'a_evp_window_total': 33.073876000000006,
        'a_evp_window': (22.695293711200005, 2.3846264596, 3.628204197200001, 4.365751632000001),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.473673540267082, 22.365648661814284, 47.92076305426709, 22.274523489414282)
    }

    mh2 = {
        'house_type': 'detached',
        'floor_ins_type': 'floor',
        'bath_ins_type': 'floor',
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843,
        'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 3.185, 'a_evp_ef_bath': 0.0,
        'a_evp_f_bath': 3.3124000000000002,
        'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.0800250894877574, 1.04002416024747],
        'l_prm': [30.805513843979693, 26.030553554896873],
        'l_ms': [10.610634821709443, 8.295602321670234],
        'l_os': [4.7921221002804035, 4.719674455778203],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 2.4843,
        'a_evp_f_other': 45.05075762711864,
        'a_evp_f_total': 48.36315762711864,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_total_inside': 3.185,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.5733,
        'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_total_inside': 0.5733,
        'a_evp_srf': (
            [30.770840982957385, 22.398126268509635],
            [13.897154090813169, 12.743121030601149],
            [30.770840982957385, 22.398126268509635],
            [13.897154090813169, 12.743121030601149]
        ),
        'a_evp_total_not_base': 261.3134,
        'a_evp_total': 262.46000000000004,
        'a_evp_open_total': 36.583876000000004,
        'a_evp_window_total': 33.073876000000006,
        'a_evp_window': (22.695293711200005, 2.3846264596, 3.628204197200001, 4.365751632000001),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.47367354026702, 22.36564866181432, 47.92076305426703, 22.274523489414317)
    }

    mh3 = {
        'house_type': 'detached',
        'floor_ins_type': 'floor',
        'bath_ins_type': 'not_exist',
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843, 'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 3.185,
        'a_evp_ef_bath': 0.0,
        'a_evp_f_bath': 3.3124000000000002,
        'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.0800250894877574, 1.04002416024747],
        'l_prm': [30.805513843979693, 26.030553554896873],
        'l_ms': [10.610634821709443, 8.295602321670234],
        'l_os': [4.7921221002804035, 4.719674455778203],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 2.4843,
        'a_evp_f_other': 45.05075762711864,
        'a_evp_f_total': 48.36315762711864,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_total_inside': 3.185,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.5733,
        'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_total_inside': 0.5733,
        'a_evp_srf': (
            [30.770840982957385, 22.398126268509635],
            [13.897154090813169, 12.743121030601149],
            [30.770840982957385, 22.398126268509635],
            [13.897154090813169, 12.743121030601149]
        ),
        'a_evp_total_not_base': 261.3134,
        'a_evp_total': 262.46000000000004,
        'a_evp_open_total': 36.583876000000004,
        'a_evp_window_total': 33.073876000000006,
        'a_evp_window': (22.695293711200005, 2.3846264596, 3.628204197200001, 4.365751632000001),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.47367354026702, 22.36564866181432, 47.92076305426703, 22.274523489414317)
    }

    mh4 = {
        'house_type': 'detached',
        'floor_ins_type': 'base',
        'bath_ins_type': None,
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843,
        'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 0.0,
        'a_evp_ef_bath': 3.3124000000000002,
        'a_evp_f_bath': 0.0,
        'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.0799821595540935, 1.0399828203113493],
        'l_prm': [30.80428935514265, 26.029518866028788],
        'l_ms': [10.60951823652745, 8.294401932913006],
        'l_os': [4.7926264410438755, 4.720357500101388],
        'a_evp_ef_other': 45.05075762711864,
        'a_evp_ef_total': 50.847457627118644,
        'a_evp_f_other': 0.0,
        'a_evp_f_total': 0.0,
        'l_base_other_outside': (10.60951823652745, 1.1526264410438751, 7.424518236527449, 4.7926264410438755),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (10.60951823652745, 4.7926264410438755, 10.60951823652745, 4.7926264410438755),
        'l_base_total_inside': 0.0,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.0,
        'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (5.304759118263725, 0.5763132205219376, 3.7122591182637246, 2.3963132205219377),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (5.304759118263725, 1.8139132205219375, 4.867959118263724, 2.3963132205219377),
        'a_evp_base_total_inside': 0.0,
        'a_evp_srf': (
            [30.767602885929602, 22.394885218865117],
            [13.898616679027239, 12.744965250273747],
            [30.767602885929602, 22.394885218865117],
            [13.898616679027239, 12.744965250273747]
        ),
        'a_evp_total_not_base': 261.3070553224287,
        'a_evp_total': 275.69000000000005,
        'a_evp_open_total': 36.582987745140024,
        'a_evp_window_total': 33.072987745140026,
        'a_evp_window': (22.694684190715087, 2.3845624164245955, 3.628106755641861, 4.365634382358484),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.46780391407963, 22.36901951287639, 47.91438134915286, 22.277947546942503)
    }

    mh5 = {
        'house_type': 'attached',
        'floor_ins_type': None,
        'bath_ins_type': None,
        'a_f': [70.0],
        'a_evp_ef_etrc': 0.0,
        'a_evp_f_etrc': 1.0,
        'l_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_etrc_inside': 0.0,
        'a_evp_ef_bath': 0.0,
        'a_evp_f_bath': 2.8665000000000003,
        'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.0481728036502156],
        'l_prm': [35.07857142857143],
        'l_ms': [6.1415949424661225],
        'l_os': [11.397690771819592],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 0.0,
        'a_evp_f_other': 66.1335,
        'a_evp_f_total': 70.0,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_total_inside': 0.0,
        'a_evp_roof': 70.0,
        'a_evp_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_etrc_inside': 0.0,
        'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_total_inside': 0.0,
        'a_evp_srf': ([17.19646583890514], [31.913534161094855], [17.19646583890514], [31.913534161094855]),
        'a_evp_total_not_base': 238.22,
        'a_evp_total': 238.22,
        'a_evp_open_total': 14.019247,
        'a_evp_window_total': 12.264247000000001,
        'a_evp_window': (7.763268351000001, 1.8604862699000002, 2.6404923791, 0.0),
        'a_evp_door': (0.0, 0.0, 1.755, 0.0),
        'a_evp_wall': (9.43319748790514, 30.053047891194854, 12.800973459805142, 31.913534161094855)
    }

    mh6 = {
        'house_type': 'detached',
        'floor_ins_type': 'floor',
        'bath_ins_type': 'base',
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843,
        'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 3.185,
        'a_evp_ef_bath': 3.3124000000000002,
        'a_evp_f_bath': 0.0,
        'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
        'l_base_bath_inside': 3.64,
        'f_s': [1.08, 1.04],
        'l_prm': [30.80479821749104, 26.029948852968104],
        'l_ms': [10.609982280729707, 8.29490083566609],
        'l_os': [4.7924168280158135, 4.720073590817963],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 5.7967,
        'a_evp_f_other': 45.05075762711864,
        'a_evp_f_total': 45.05075762711864,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 3.64, 3.185, 0.0),
        'l_base_total_inside': 6.825,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.5733,
        'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
        'a_evp_base_bath_inside': 1.82,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 1.2376, 1.1557, 0.0),
        'a_evp_base_total_inside': 2.3933,
        'a_evp_srf': (
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085],
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085]
        ),
        'a_evp_total_not_base': 261.30969198797516,
        'a_evp_total': 266.0962919879752,
        'a_evp_open_total': 36.58335687831652,
        'a_evp_window_total': 33.073356878316524,
        'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
    }

    mh7 = {
        'house_type': 'detached',
        'floor_ins_type': 'floor',
        'bath_ins_type': 'floor',
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843,
        'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 3.185,
        'a_evp_ef_bath': 0.0,
        'a_evp_f_bath': 3.3124000000000002,
        'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.08, 1.04],
        'l_prm': [30.80479821749104, 26.029948852968104],
        'l_ms': [10.609982280729707, 8.29490083566609],
        'l_os': [4.7924168280158135, 4.720073590817963],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 2.4843,
        'a_evp_f_other': 45.05075762711864,
        'a_evp_f_total': 48.36315762711864,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_total_inside': 3.185,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.5733,
        'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_total_inside': 0.5733,
        'a_evp_srf': (
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085],
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085]
        ),
        'a_evp_total_not_base': 261.30969198797516,
        'a_evp_total': 262.4562919879752,
        'a_evp_open_total': 36.58335687831652,
        'a_evp_window_total': 33.073356878316524,
        'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
    }

    mh8 = {
        'house_type': 'detached',
        'floor_ins_type': 'floor',
        'bath_ins_type': 'not_exist',
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843,
        'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 3.185,
        'a_evp_ef_bath': 0.0,
        'a_evp_f_bath': 3.3124000000000002,
        'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.08, 1.04],
        'l_prm': [30.80479821749104, 26.029948852968104],
        'l_ms': [10.609982280729707, 8.29490083566609],
        'l_os': [4.7924168280158135, 4.720073590817963],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 2.4843,
        'a_evp_f_other': 45.05075762711864,
        'a_evp_f_total': 48.36315762711864,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_total_inside': 3.185,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.5733,
        'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_total_inside': 0.5733,
        'a_evp_srf': (
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085],
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085]
        ),
        'a_evp_total_not_base': 261.30969198797516,
        'a_evp_total': 262.4562919879752,
        'a_evp_open_total': 36.58335687831652,
        'a_evp_window_total': 33.073356878316524,
        'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
    }

    mh9 = {
        'house_type': 'detached',
        'floor_ins_type': 'base',
        'bath_ins_type': None,
        'a_f': [50.847457627118644, 39.152542372881356],
        'a_evp_ef_etrc': 2.4843,
        'a_evp_f_etrc': 0.0,
        'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
        'l_base_etrc_inside': 0.0,
        'a_evp_ef_bath': 3.3124000000000002,
        'a_evp_f_bath': 0.0,
        'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.08, 1.04],
        'l_prm': [30.80479821749104, 26.029948852968104],
        'l_ms': [10.609982280729707, 8.29490083566609],
        'l_os': [4.7924168280158135, 4.720073590817963],
        'a_evp_ef_other': 45.05075762711864,
        'a_evp_ef_total': 50.847457627118644,
        'a_evp_f_other': 0.0,
        'a_evp_f_total': 0.0,
        'l_base_other_outside': (10.609982280729707, 1.1524168280158131, 7.424982280729706, 4.7924168280158135),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (10.609982280729707, 4.7924168280158135, 10.609982280729707, 4.7924168280158135),
        'l_base_total_inside': 0.0,
        'a_evp_roof': 50.847457627118644,
        'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
        'a_evp_base_etrc_inside': 0.0,
        'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (5.304991140364853, 0.5762084140079066, 3.712491140364853, 2.3962084140079067),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (5.304991140364853, 1.8138084140079065, 4.868191140364853, 2.3962084140079067),
        'a_evp_base_total_inside': 0.0,
        'a_evp_srf': (
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085],
            [30.768948614116148, 22.396232256298443],
            [13.898008801245858, 12.7441986952085]
        ),
        'a_evp_total_not_base': 261.30969198797516,
        'a_evp_total': 275.6928910967207,
        'a_evp_open_total': 36.58335687831652,
        'a_evp_window_total': 33.073356878316524,
        'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
        'a_evp_door': (0.0, 1.89, 1.62, 0.0),
        'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
    }

    mh10 = {
        'house_type': 'attached',
        'floor_ins_type': None,
        'bath_ins_type': None,
        'a_f': [70.0],
        'a_evp_ef_etrc': 0.0,
        'a_evp_f_etrc': 1.0,
        'l_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_etrc_inside': 0.0,
        'a_evp_ef_bath': 0.0,
        'a_evp_f_bath': 2.8665000000000003,
        'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_bath_inside': 0.0,
        'f_s': [1.048215],
        'l_prm': [35.079983588536635],
        'l_ms': [6.140770148791126],
        'l_os': [11.39922164547719],
        'a_evp_ef_other': 0.0,
        'a_evp_ef_total': 0.0,
        'a_evp_f_other': 66.1335,
        'a_evp_f_total': 70.0,
        'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_other_inside': 0.0,
        'l_base_total_outside': (0.0, 0.0, 0.0, 0.0),
        'l_base_total_inside': 0.0,
        'a_evp_roof': 70.0,
        'a_evp_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_etrc_inside': 0.0,
        'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_bath_inside': 0.0,
        'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_other_inside': 0.0,
        'a_evp_base_total_outside': (0.0, 0.0, 0.0, 0.0),
        'a_evp_base_total_inside': 0.0,
        'a_evp_srf': ([17.19415641661515], [31.917820607336132], [17.19415641661515], [31.917820607336132]),
        'a_evp_total_not_base': 238.22395404790257,
        'a_evp_total': 238.22395404790257,
        'a_evp_open_total': 14.019479695719065,
        'a_evp_window_total': 12.264479695719064,
        'a_evp_window': (7.763415647390167, 1.8605215698405821, 2.6405424784883142, 0.0),
        'a_evp_door': (0.0, 0.0, 1.755, 0.0),
        'a_evp_wall': (9.430740769224983, 30.05729903749555, 12.798613938126838, 31.917820607336132)
    }

    convert(**mh1)
    convert(**mh2)
    convert(**mh3)
    convert(**mh4)
    convert(**mh5)
    convert(**mh6)
    convert(**mh7)
    convert(**mh8)
    convert(**mh9)
    convert(**mh10)
