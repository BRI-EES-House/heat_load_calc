from typing import Optional, List, Dict
from heat_load_calc.convert import ees_house
from heat_load_calc.convert import factor_f
from heat_load_calc.convert.ees_house import GeneralPartType
from heat_load_calc.convert.ees_house import SpaceType
from heat_load_calc.external.factor_h import NextSpace


def get_model_house_no_spec(
        house_type: str, floor_ins_type: str,
        a_evp_ef_total: float,
        a_evp_f_total: float,
        l_base_total_outside: (float, float, float, float),
        l_base_total_inside: float,
        a_evp_roof: float,
        a_evp_base_total_outside: (float, float, float, float),
        a_evp_base_total_inside: float,
        a_evp_window: (float, float, float, float),
        a_evp_door: (float, float, float, float),
        a_evp_wall: (float, float, float, float),
        **kwargs):
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
        モデルハウスを表す辞書（spec = None）
    """

    # region roof

    if house_type == 'detached':
        roofs = [
            ees_house.GeneralPartNoSpec(
                name='roof',
                general_part_type=GeneralPartType.CEILING,
                next_space=NextSpace.OUTDOOR,
                direction='top',
                area=a_evp_roof,
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            )
        ]
    elif house_type == 'attached':
        roofs = [
            ees_house.GeneralPartNoSpec(
                name='roof',
                general_part_type=GeneralPartType.UPWARD_BOUNDARY_FLOOR,
                next_space=NextSpace.AIR_CONDITIONED,
                direction='upward',
                area=a_evp_roof,
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotDefined()
            )
        ]
    else:
        raise Exception

    # endregion

    # region wall

    if house_type == 'detached':
        walls = [
            ees_house.GeneralPartNoSpec(
                name='wall_sw',
                general_part_type=GeneralPartType.WALL,
                next_space=NextSpace.OUTDOOR,
                direction='sw',
                area=a_evp_wall[0],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            ),
            ees_house.GeneralPartNoSpec(
                name='wall_nw',
                general_part_type=GeneralPartType.WALL,
                next_space=NextSpace.OUTDOOR,
                direction='nw',
                area=a_evp_wall[1],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            ),
            ees_house.GeneralPartNoSpec(
                name='wall_ne',
                general_part_type=GeneralPartType.WALL,
                next_space=NextSpace.OUTDOOR,
                direction='ne',
                area=a_evp_wall[2],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            ),
            ees_house.GeneralPartNoSpec(
                name='wall_se',
                general_part_type=GeneralPartType.WALL,
                next_space=NextSpace.OUTDOOR,
                direction='se',
                area=a_evp_wall[3],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            )
        ]
    elif house_type == 'attached':
        walls = [
            ees_house.GeneralPartNoSpec(
                name='wall_sw',
                general_part_type=GeneralPartType.WALL,
                next_space=NextSpace.OUTDOOR,
                direction='sw',
                area=a_evp_wall[0],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            ),
            ees_house.GeneralPartNoSpec(
                name='wall_nw',
                general_part_type=GeneralPartType.WALL,
                next_space=NextSpace.OUTDOOR,
                direction='nw',
                area=a_evp_wall[1],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            ),
            ees_house.GeneralPartNoSpec(
                name='wall_ne',
                general_part_type=GeneralPartType.WALL,
                next_space=NextSpace.OPEN_SPACE,
                direction='horizontal',
                area=a_evp_wall[2],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotDefined()
            ),
            ees_house.GeneralPartNoSpec(
                name='wall_se',
                general_part_type=GeneralPartType.BOUNDARY_WALL,
                next_space=NextSpace.AIR_CONDITIONED,
                direction='horizontal',
                area=a_evp_wall[3],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotDefined()
            )
        ]
    else:
        raise Exception

    # endregion

    # region window

    if house_type == 'detached':
        windows = [
            ees_house.WindowNoSpec(
                name='window_sw',
                next_space=NextSpace.OUTDOOR,
                direction='sw',
                area=a_evp_window[0],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeTransientExistSimple(depth=0.3, d_h=1.0, d_e=0.0)
            ),
            ees_house.WindowNoSpec(
                name='window_nw',
                next_space=NextSpace.OUTDOOR,
                direction='nw',
                area=a_evp_window[1],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeTransientExistSimple(depth=0.3, d_h=1.0, d_e=0.0)
            ),
            ees_house.WindowNoSpec(
                name='window_ne',
                next_space=NextSpace.OUTDOOR,
                direction='ne',
                area=a_evp_window[2],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeTransientExistSimple(depth=0.3, d_h=1.0, d_e=0.0)
            ),
            ees_house.WindowNoSpec(
                name='window_se',
                next_space=NextSpace.OUTDOOR,
                direction='se',
                area=a_evp_window[3],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeTransientExistSimple(depth=0.3, d_h=1.0, d_e=0.0)
            )
        ]
    elif house_type == 'attached':
        if a_evp_window[3] > 0.0:
            raise Exception('集合住宅において、Direction 270 側に窓が設定（面積が0より大）されました。')
        windows = [
            ees_house.WindowNoSpec(
                name='window_sw',
                next_space=NextSpace.OUTDOOR,
                direction='sw',
                area=a_evp_window[0],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeTransientExistSimple(depth=0.3, d_h=1.0, d_e=0.0)
            ),
            ees_house.WindowNoSpec(
                name='window_nw',
                next_space=NextSpace.OUTDOOR,
                direction='nw',
                area=a_evp_window[1],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeTransientExistSimple(depth=0.3, d_h=1.0, d_e=0.0)
            ),
            ees_house.WindowNoSpec(
                name='window_ne',
                next_space=NextSpace.OPEN_SPACE,
                direction='horizontal',
                area=a_evp_window[2],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeTransientExistSimple(depth=0.3, d_h=1.0, d_e=0.0)
            )
        ]
    else:
        raise Exception

    # endregion

    # region door

    if house_type == 'detached':
        if a_evp_door[0] > 0.0:
            raise Exception('戸建て住宅において、Direction 0 側にドアが設定（面積が0より大）されました。')
        if a_evp_door[3] > 0.0:
            raise Exception('戸建て住宅において、Direction 270 側にドアが設定（面積が0より大）されました。')
        doors = [
            ees_house.DoorNoSpec(
                name='door_nw',
                next_space=NextSpace.OUTDOOR,
                direction='nw',
                area=a_evp_door[1],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            ),
            ees_house.DoorNoSpec(
                name='door_ne',
                next_space=NextSpace.OUTDOOR,
                direction='ne',
                area=a_evp_door[2],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotInput()
            )
        ]
    elif house_type == 'attached':
        if a_evp_door[0] > 0.0:
            raise Exception('集合住宅において、Direction 0 側にドアが設定（面積が0より大）されました。')
        if a_evp_door[1] > 0.0:
            raise Exception('集合住宅において、Direction 90 側にドアが設定（面積が0より大）されました。')
        if a_evp_door[3] > 0.0:
            raise Exception('集合住宅において、Direction 270 側にドアが設定（面積が0より大）されました。')
        doors = [
            ees_house.DoorNoSpec(
                name='door_ne',
                next_space=NextSpace.OPEN_SPACE,
                direction='horizontal',
                area=a_evp_door[2],
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotDefined()
            )
        ]
    else:
        raise Exception

    # endregion

    # region earth_floor
    if house_type == 'detached':
        earth_floor_centers = [
            ees_house.EarthfloorCenterNoSpec(name='earth_floor', area=a_evp_ef_total, space_type='undefined')
        ]
    elif house_type == 'attached':
        if a_evp_ef_total > 0.0:
            raise Exception('集合住宅において土間床が設定（面積が0より大）されました。')
        earth_floor_centers = []
    else:
        raise Exception

    # endregion

    # region floor

    if house_type == 'detached':
        if floor_ins_type == 'floor':
            floors = [
                ees_house.GeneralPartNoSpec(
                    name='floor',
                    general_part_type=GeneralPartType.FLOOR,
                    next_space=NextSpace.OPEN_UNDERFLOOR,
                    direction='downward',
                    area=a_evp_f_total,
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotDefined()
                )
            ]
        elif floor_ins_type == 'base':
            if a_evp_f_total > 0.0:
                raise Exception('戸建住宅の基礎断熱住宅において床が設定（面積が0より大）されました。')
            floors = []
        else:
            raise Exception
    elif house_type == 'attached':
        floors = [
            ees_house.GeneralPartNoSpec(
                name='floor',
                general_part_type=GeneralPartType.DOWNWARD_BOUNDARY_FLOOR,
                next_space=NextSpace.AIR_CONDITIONED,
                direction='downward',
                area=a_evp_f_total,
                space_type=SpaceType.UNDEFINED,
                sunshade=factor_f.SunshadeOpaqueNotDefined()
            )
        ]
    else:
        raise Exception

    # endregion

    # region base outside

    if house_type == 'detached':
        if floor_ins_type == 'floor':
            if a_evp_base_total_outside[0] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 0 側に基礎が設定（面積が0より大）されました。')
            if a_evp_base_total_outside[3] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 270 側に基礎が設定（面積が0より大）されました。')
            base_outsides = [
                ees_house.GeneralPartNoSpec(
                    name='base_outside_nw',
                    general_part_type=GeneralPartType.WALL,
                    next_space=NextSpace.OUTDOOR,
                    direction='nw',
                    area=a_evp_base_total_outside[1],
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotInput()
                ),
                ees_house.GeneralPartNoSpec(
                    name='base_outside_ne',
                    general_part_type=GeneralPartType.WALL,
                    next_space=NextSpace.OUTDOOR,
                    direction='ne',
                    area=a_evp_base_total_outside[2],
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotInput()
                )
            ]
        elif floor_ins_type == 'base':
            base_outsides = [
                ees_house.GeneralPartNoSpec(
                    name='base_outside_sw',
                    general_part_type=GeneralPartType.WALL,
                    next_space=NextSpace.OUTDOOR,
                    direction='sw',
                    area=a_evp_base_total_outside[0],
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotInput()
                ),
                ees_house.GeneralPartNoSpec(
                    name='base_outside_nw',
                    general_part_type=GeneralPartType.WALL,
                    next_space=NextSpace.OUTDOOR,
                    direction='nw',
                    area=a_evp_base_total_outside[1],
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotInput()
                ),
                ees_house.GeneralPartNoSpec(
                    name='base_outside_ne',
                    general_part_type=GeneralPartType.WALL,
                    next_space=NextSpace.OUTDOOR,
                    direction='ne',
                    area=a_evp_base_total_outside[2],
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotInput()
                ),
                ees_house.GeneralPartNoSpec(
                    name='base_outside_se',
                    general_part_type=GeneralPartType.WALL,
                    next_space=NextSpace.OUTDOOR,
                    direction='se',
                    area=a_evp_base_total_outside[3],
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotInput()
                ),
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
        base_outsides = []
    else:
        raise Exception

    # endregion

    # region base inside

    if house_type == 'detached':
        if floor_ins_type == 'floor':
            base_insides = [
                ees_house.GeneralPartNoSpec(
                    name='base_inside',
                    general_part_type=GeneralPartType.WALL,
                    next_space=NextSpace.OPEN_UNDERFLOOR,
                    direction='horizontal',
                    area=a_evp_base_total_inside,
                    space_type=SpaceType.UNDEFINED,
                    sunshade=factor_f.SunshadeOpaqueNotDefined()
                )
            ]
        elif floor_ins_type == 'base':
            if a_evp_base_total_inside > 0.0:
                raise Exception('戸建住宅（基礎断熱）において、基礎（室内側）が設定（面積が0より大）されました。')
            base_insides = []
        else:
            raise Exception
    elif house_type == 'attached':
        if a_evp_base_total_inside > 0.0:
            raise Exception('集合住宅において、基礎（室内側）が設定（面積が0より大）されました。')
        base_insides = []
    else:
        raise Exception

    # endregion

    # region earth floor perimeter outside

    if house_type == 'detached':
        if floor_ins_type == 'floor':
            if l_base_total_outside[0] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 0 側に土間床周辺部が設定（長さが0より大）されました。')
            if l_base_total_outside[3] > 0.0:
                raise Exception('戸建住宅（床断熱）において、Direction 270 側に土間床周辺部が設定（長さが0より大）されました。')
            earth_floor_perimeters_outside = [
                ees_house.EarthfloorPerimeterNoSpec(
                    name='earth_floor_perimeter_nw',
                    next_space='outdoor',
                    length=l_base_total_outside[1],
                    space_type='undefined'
                ),
                ees_house.EarthfloorPerimeterNoSpec(
                    name='earth_floor_perimeter_ne',
                    next_space='outdoor',
                    length=l_base_total_outside[2],
                    space_type='undefined'
                )
            ]
        elif floor_ins_type == 'base':
            earth_floor_perimeters_outside = [
                ees_house.EarthfloorPerimeterNoSpec(
                    name='earth_floor_perimeter_sw',
                    next_space='outdoor',
                    length=l_base_total_outside[0],
                    space_type='undefined'
                ),
                ees_house.EarthfloorPerimeterNoSpec(
                    name='earth_floor_perimeter_nw',
                    next_space='outdoor',
                    length=l_base_total_outside[1],
                    space_type='undefined'
                ),
                ees_house.EarthfloorPerimeterNoSpec(
                    name='earth_floor_perimeter_ne',
                    next_space='outdoor',
                    length=l_base_total_outside[2],
                    space_type='undefined'
                ),
                ees_house.EarthfloorPerimeterNoSpec(
                    name='earth_floor_perimeter_se',
                    next_space='outdoor',
                    length=l_base_total_outside[3],
                    space_type='undefined'
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
        earth_floor_perimeters_outside = []
    else:
        raise Exception

    # endregion

    # region earth floor perimeter inside

    if house_type == 'detached':
        if floor_ins_type == 'floor':
            earth_floor_perimeters_inside = [
                ees_house.EarthfloorPerimeterNoSpec(
                    name='earth_floor_perimeter_inside',
                    next_space='open_underfloor',
                    length=l_base_total_inside,
                    space_type='undefined'
                )
            ]
        elif floor_ins_type == 'base':
            if l_base_total_inside > 0.0:
                raise Exception('戸建住宅（基礎断熱）において、土間床周辺部（室内側）が設定（長さが0より大）されました。')
            earth_floor_perimeters_inside = []
        else:
            raise Exception
    elif house_type == 'attached':
        if l_base_total_inside > 0.0:
            raise Exception('集合住宅において、土間床周辺部（室内側）が設定（長さが0より大）されました。')
        earth_floor_perimeters_inside = []
    else:
        raise Exception

    # endregion

    return roofs + walls + floors + base_outsides + base_insides, windows, doors, earth_floor_perimeters_outside + earth_floor_perimeters_inside, earth_floor_centers


def _get_a_f(house_type: str, a_f_total: float, r_fa: Optional[float]) -> List[float]:
    """
    Args:
        house_type: 住戸の種類
        a_f_total: 床面積の合計, m2
        r_fa: 1階の床面積に対する2階の床面積の比
    Returns:
        各階の床面積, m2
    Notes:
        戸建住戸の場合は2つの要素からなる配列で、配列0番目が1階、配列1番目が2階の値である。
        集合住宅の場合は1つの要素からなる配列（集合住宅の場合、平屋を想定している。）
    """

    if house_type == 'detached':
        return [a_f_total / (1 + r_fa), a_f_total * r_fa / (1 + r_fa)]
    elif house_type == 'attached':
        return [a_f_total]
    else:
        raise Exception


def _get_entrance(
        house_type: str, floor_ins_type: str, l_etrc_ms: float, l_etrc_os: float
) -> (float, float, (float, float, float, float), float):
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床断熱の種類
        l_etrc_ms: 主開口方位側の玄関の土間床等の周辺部の基礎長さ, m
        l_etrc_os: その他方位側の玄関の土間床等の周辺部の基礎長さ, m
    Returns:
        次の7つの変数からなるタプル
            (1) 玄関の土間床等の面積, m2
            (2) 玄関の断熱した床の面積, m2
            (3) 玄関の土間床等の外周部の長さ（室外側）（4方向）, m
            (4) 玄関の土間床等の外周部の長さ（室内側）, m
    """

    # 玄関の土間床等の外周部の長さ（主方位から0度）, m
    # 玄関の土間床等の外周部の長さ（主方位から90度）, m
    # 玄関の土間床等の外周部の長さ（主方位から180度）, m
    # 玄関の土間床等の外周部の長さ（主方位から270度）, m
    if house_type == 'detached':
        l_base_etrc_000, l_base_etrc_090, l_base_etrc_180, l_base_etrc_270 \
            = 0.0, l_etrc_os, l_etrc_ms, 0.0
    elif house_type == 'attached':
        l_base_etrc_000, l_base_etrc_090, l_base_etrc_180, l_base_etrc_270 = 0.0, 0.0, 0.0, 0.0
    else:
        raise Exception

    # 玄関の土間床等の外周部の長さ（室内側）, m
    if house_type == 'detached':
        if floor_ins_type == 'floor':
            l_base_etrc_inside = l_etrc_ms + l_etrc_os
        elif floor_ins_type == 'base':
            l_base_etrc_inside = 0.0
        else:
            raise Exception
    elif house_type == 'attached':
        l_base_etrc_inside = 0.0
    else:
        raise Exception

    # 玄関の土間床等の面積, m2
    if house_type == 'detached':
        a_evp_ef_etrc = l_etrc_ms * l_etrc_os
        a_evp_f_etrc = 0.0
    elif house_type == 'attached':
        a_evp_ef_etrc = 0.0
        a_evp_f_etrc = l_etrc_ms * l_etrc_os
    else:
        raise Exception

    l_base_etrc_outside = (l_base_etrc_000, l_base_etrc_090, l_base_etrc_180, l_base_etrc_270)

    return a_evp_ef_etrc, a_evp_f_etrc, l_base_etrc_outside, l_base_etrc_inside


def _get_bath(
        house_type: str, floor_ins_type: str, bath_ins_type: str, l_base_bath_ms: float, l_base_bath_os: float
) -> (float, float, (float, float, float, float),float):
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床の断熱の種類
        bath_ins_type: 浴室の断熱の種類
        l_base_bath_ms: 主開口方位側の浴室の土間床等の周辺部の基礎長さ, m
        l_base_bath_os: その他方位側の浴室の土間床等の周辺部の基礎長さ, m
    Returns:
        次の7つの変数からなるタプル
            (1) 浴室の土間床等の面積, m2,
            (2) 浴室の断熱した床の面積, m2
            (3) 浴室の土間床等の外周部の長さ（4方位）, m
            (4) 浴室の土間床等の外周部の長さ（室内側）, m
    """

    # 浴室の土間床等の外周部の長さ（主方位から0度）, m
    # 浴室の土間床等の外周部の長さ（主方位から90度）, m
    # 浴室の土間床等の外周部の長さ（主方位から180度）, m
    # 浴室の土間床等の外周部の長さ（主方位から270度）, m
    if house_type == 'detached':
        if (floor_ins_type == 'floor' and bath_ins_type == 'base') or floor_ins_type == 'base':
            l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 \
                = 0.0, l_base_bath_os, l_base_bath_ms, 0.0
        elif floor_ins_type == 'floor' and (bath_ins_type == 'floor' or bath_ins_type == 'not_exist'):
            l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 = 0.0, 0.0, 0.0, 0.0
        else:
            raise Exception
    elif house_type == 'attached':
        l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 = 0.0, 0.0, 0.0, 0.0
    else:
        raise Exception

    # 浴室の土間床等の外周部の長さ（室内側）, m
    if house_type == 'detached':
        if floor_ins_type == 'base':
            l_base_bath_inside = 0.0
        elif floor_ins_type == 'floor':
            if bath_ins_type == 'base':
                l_base_bath_inside = l_base_bath_ms + l_base_bath_os
            elif bath_ins_type == 'floor' or bath_ins_type == 'not_exist':
                l_base_bath_inside = 0.0
            else:
                raise Exception
        else:
            raise Exception
    elif house_type == 'attached':
        l_base_bath_inside = 0.0
    else:
        raise Exception

    # 浴室の土間床等の面積, m2
    if house_type == 'detached':
        if floor_ins_type == 'base':
            a_ef_bath = l_base_bath_ms * l_base_bath_os
            a_f_bath = 0.0
        elif floor_ins_type == 'floor':
            if bath_ins_type == 'base':
                a_ef_bath = l_base_bath_ms * l_base_bath_os
                a_f_bath = 0.0
            elif bath_ins_type == 'floor' or bath_ins_type == 'not_exist':
                a_ef_bath = 0.0
                a_f_bath = l_base_bath_ms * l_base_bath_os
            else:
                raise Exception
        else:
            raise Exception
    elif house_type == 'attached':
        a_ef_bath = 0.0
        a_f_bath = l_base_bath_ms * l_base_bath_os
    else:
        raise Exception

    l_base_bath_outside = (l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270)

    return a_ef_bath, a_f_bath, l_base_bath_outside, l_base_bath_inside


def _get_f_s(house_type: str, floor_ins_type: str, bath_ins_type: str,
             a_env: float, a_f: List[float],
             h: List[float], h_base_other: float, h_base_bath: float, h_base_etrc: float,
             l_base_bath_outside: (float, float, float, float), l_base_bath_inside: float,
             l_base_etrc_outside: (float, float, float, float), l_base_etrc_inside: float,
             f_s_default: List[float]):
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床の断熱の種類
        bath_ins_type: 浴室の床の断熱の種類
        a_env: 外皮面積の合計, m2
        a_f: 各階の床面積, m2
        h: 各階の高さ, m
        h_base_other: 基礎の高さ, m
        h_base_bath: 浴室の基礎の高さ, m
        h_base_etrc: 玄関の基礎の高さ, m
        l_base_bath_outside: 浴室の土間床等の外周部の長さ（４方位）, m
        l_base_bath_inside: 浴室の土間床等の外周部の長さ（室内側）, m
        l_base_etrc_outside: 玄関の土間床等の外周部の長さ（4方位）, m
        l_base_etrc_inside: 玄関の土間床等の外周部の長さ（室内側）, m
        f_s_default: 形状係数のデフォルト値
    Returns:
        形状係数（リスト）
    Notes:
        戸建住戸の場合は2つの要素からなる配列で、配列0番目が1階、配列1番目が2階の値である。
        集合住宅の場合は1つの要素からなる配列（集合住宅の場合、平屋を想定している。）
    """

    l_base_etrc_total = sum(l_base_etrc_outside) + l_base_etrc_inside
    l_base_bath_total = sum(l_base_bath_outside) + l_base_bath_inside

    x = a_env - 2 * a_f[0] \
        - l_base_etrc_total * h_base_etrc \
        - l_base_bath_total * h_base_bath \
        + (l_base_etrc_total + l_base_bath_total) * h_base_other

    if house_type == 'detached':
        y = 4 * a_f[0] ** 0.5 * (h[0] + h_base_other) + 4 * a_f[1] ** 0.5 * f_s_default[1] / f_s_default[0] * h[1]
        f_s_2 = max(x / y * f_s_default[1] / f_s_default[0], 1.0)
        f_s_1 = f_s_2 * f_s_default[0] / f_s_default[1]
        return [f_s_1, f_s_2]
    elif house_type == 'attached':
        y = 4 * a_f[0] ** 0.5 * h[0]
        f_s_1 = max(x / y, 1.0)
        return [f_s_1]
    else:
        raise Exception


def _get_l_prm(a_f: List[float], f_s: List[float]) -> List[float]:
    """
    Args:
        a_f: 各階の床面積, m2
        f_s: 形状係数（リスト）
    Returns:
        周長（リスト）, m
    Notes:
        戸建住戸の場合は2つの要素からなる配列で、配列0番目が1階、配列1番目が2階の値である。
        集合住宅の場合は1つの要素からなる配列（集合住宅の場合、平屋を想定している。）
    """

    return [4 * a_f_i ** 0.5 * f_s_i for a_f_i, f_s_i in zip(a_f, f_s)]


def _get_l(house_type: str, a_f: List[float], l_prm: List[float]) -> (List[float], List[float]):
    """
    Args:
        house_type: 住戸の種類
        a_f: 各階の床面積（リスト）, m2
        l_prm: 周長（リスト）, m
    Returns:
        次の2つの変数からなるタプル
            (1) 各階の主方位の辺の長さ（リスト）, m
            (2) 各階のその他方位の辺の長さ（リスト）, m
    """

    dif = [max((l_prm_i / 2) ** 2 - 4 * a_f_i, 0.0) ** 0.5 / 2 for l_prm_i, a_f_i in zip(l_prm, a_f)]

    # 長手方向の辺の長さ, m
    l_ls = [l_prm_i / 4 + dif_i for l_prm_i, dif_i in zip(l_prm, dif)]
    # 短手方向の辺の長さ, m
    l_ss = [l_prm_i / 4 - dif_i for l_prm_i, dif_i in zip(l_prm, dif)]

    # 主方位とその他方位の辺の長さ, m
    l_ms, l_os = {
        'detached': (l_ls, l_ss),
        'attached': (l_ss, l_ls),
    }[house_type]

    return l_ms, l_os


def _get_a_evp_wall(
        a_evp_door: (float, float, float, float),
        a_evp_srf: (List[float], List[float], List[float], List[float]),
        a_evp_window: (float, float, float, float)) -> (float, float, float, float):
    """
    Args:
        a_evp_door: ドアの面積（4方位）, m2
        a_evp_srf: 各階の壁面積（窓面積を含む）（4方位）, m2
        a_evp_window: 窓の面積の合計(4方位）, m2
    Returns:
        壁の面積（4方位）, m2
    """

    a_evp_srf_000, a_evp_srf_090, a_evp_srf_180, a_evp_srf_270 = a_evp_srf
    a_evp_window_000, a_evp_window_090, a_evp_window_180, a_evp_window_270 = a_evp_window
    a_evp_door_000, a_evp_door_090, a_evp_door_180, a_evp_door_270 = a_evp_door

    a_evp_wall_000 = sum(a_evp_srf_000) - a_evp_window_000 - a_evp_door_000
    a_evp_wall_090 = sum(a_evp_srf_090) - a_evp_window_090 - a_evp_door_090
    a_evp_wall_180 = sum(a_evp_srf_180) - a_evp_window_180 - a_evp_door_180
    a_evp_wall_270 = sum(a_evp_srf_270) - a_evp_window_270 - a_evp_door_270

    return a_evp_wall_000, a_evp_wall_090, a_evp_wall_180, a_evp_wall_270


def _get_a_evp_door(
        a_evp_door_back_entrance: float, a_evp_door_entrance: float, house_type: str
) -> (float, float, float, float):
    """
    Args:
        a_evp_door_back_entrance: 勝手口ドアの面積, m2
        a_evp_door_entrance: 玄関ドアの面積, m2
        house_type: 住宅の種類
    Returns:
        ドアの面積（4方位）, m2
    """

    a_evp_door_000 = 0.0

    a_evp_door_090 = {
        'detached': a_evp_door_entrance,
        'attached': 0.0,
    }[house_type]

    a_evp_door_180 = {
        'detached': a_evp_door_back_entrance,
        'attached': a_evp_door_entrance,
    }[house_type]

    a_evp_door_270 = 0.0

    return a_evp_door_000, a_evp_door_090, a_evp_door_180, a_evp_door_270


def _get_a_evp_window(a_window_total, r_window):
    """
    Args:
        a_window_total: 窓の面積の合計, m2
        r_window: 窓の面積の合計に対する方位別の窓の面積（4方位）
    Returns:
        窓の面積（4方位）, m2
    """

    r_window_000, r_window_090, r_window_180, r_window_270 = r_window

    a_window_000 = a_window_total * r_window_000
    a_window_090 = a_window_total * r_window_090
    a_window_180 = a_window_total * r_window_180
    a_window_270 = a_window_total * r_window_270

    return a_window_000, a_window_090, a_window_180, a_window_270


def _get_a_evp_window_total(
        a_evp_door_back_entrance: float, a_evp_door_entrance: float, a_evp_open_total: float) -> float:
    """
    Args:
        a_evp_door_back_entrance: 勝手口ドアの面積, m2
        a_evp_door_entrance: 玄関ドアの面積, m2
        a_evp_open_total: 開口部の面積の合計, m2
    Returns:
        窓の面積の合計, m2
    """

    return a_evp_open_total - a_evp_door_entrance - a_evp_door_back_entrance


def _get_a_evp_open_total(a_d_env: float, r_open: float) -> float:
    """
    Args:
        a_d_env: 外皮の面積の合計（基礎の面積を除く）, m2
        r_open: 開口部の面積比率
    Returns:
        開口部の面積の合計, m2
    """

    return a_d_env * r_open


def _get_a_evp_total(
        a_evp_base_total_outside: (float, float, float, float), a_base_total_inside: float, a_evp_total_not_base: float
) -> float:
    """
    Args:
        a_evp_base_total_outside: 基礎の面積の合計（室外側）（4方位）, m2
        a_base_total_inside: 基礎の面積の合計（室内側）, m2
        a_evp_total_not_base: 外皮の面積の合計（基礎の面積を除く）, m2
    Returns: 外皮の面積の合計, m2
    """

    return a_evp_total_not_base + sum(a_evp_base_total_outside) + a_base_total_inside


def _get_a_evp_total_not_base(
        a_evp_ef_total: float, a_evp_f_total: float, a_evp_roof: float,
        a_evp_srf: (List[float], List[float], List[float], List[float])) -> float:
    """
    Args:
        a_evp_ef_total: 土間床の面積の合計, m2
        a_evp_f_total: 断熱した床面積の合計, m2
        a_evp_roof: 屋根又は天井の面積, m2
        a_evp_srf: 各階の壁面積（窓面積を含む）（4方位）, m2
    Returns:
        外皮の面積の合計（基礎の面積を除く）, m2
    """

    a_evp_srf_000, a_evp_srf_090, a_evp_srf_180, a_evp_srf_270 = a_evp_srf
    a_evp_srf_total = sum(a_evp_srf_000) + sum(a_evp_srf_090) + sum(a_evp_srf_180) + sum(a_evp_srf_270)

    return a_evp_f_total + a_evp_ef_total + a_evp_roof + a_evp_srf_total


def _get_a_evp_srf(l_ms: List[float], l_os: List[float], h: List[float]) -> (float, float, float, float):
    """
    Args:
        l_ms: 各階の主方位の長さ, m
        l_os: 各階のその他方位の長さ, m
        h: 各階の高さ, m
    Returns:
        各階の壁面積（窓面積を含む）（4方位）, m2
    """

    a_evp_srf_000 = [l_ms_i * h_i for l_ms_i, h_i in zip(l_ms, h)]
    a_evp_srf_090 = [l_os_i * h_i for l_os_i, h_i in zip(l_os, h)]
    a_evp_srf_180 = [l_ms_i * h_i for l_ms_i, h_i in zip(l_ms, h)]
    a_evp_srf_270 = [l_os_i * h_i for l_os_i, h_i in zip(l_os, h)]

    return a_evp_srf_000, a_evp_srf_090, a_evp_srf_180, a_evp_srf_270


def _get_a_evp_base_total(
        a_evp_base_etrc_outside: (float, float, float, float), a_evp_base_etrc_inside: float,
        a_evp_base_bath_outside: (float, float, float, float), a_evp_base_bath_inside: float,
        a_evp_base_other_outside: (float, float, float, float), a_evp_base_other_inside: float
) -> ((float, float, float, float), float):
    """
    Args:
        a_evp_base_etrc_outside: 玄関等の基礎の面積（室外側）（4方位）, m2
        a_evp_base_etrc_inside:  玄関等の基礎の面積（室内側）, m2
        a_evp_base_bath_outside: 浴室の基礎の面積（室外側）（4方位）, m2
        a_evp_base_bath_inside: 浴室の基礎の面積（室内側）, m2
        a_evp_base_other_outside: その他の基礎の面積（室外側）（4方位）, m2
        a_evp_base_other_inside: その他の基礎の面積（室内側）, m2
    Returns:
        タプル
            (1) 基礎の面積の合計（室外側）（4方位）, m2
            (2) 基礎の面積の合計（室内側）, m2
    """

    a_evp_base_etrc_000, a_evp_base_etrc_090, a_evp_base_etrc_180, a_evp_base_etrc_270 = a_evp_base_etrc_outside
    a_evp_base_bath_000, a_evp_base_bath_090, a_evp_base_bath_180, a_evp_base_bath_270 = a_evp_base_bath_outside
    a_evp_base_other_000, a_evp_base_other_090, a_evp_base_other_180, a_evp_base_other_270 = a_evp_base_other_outside

    a_evp_base_total_000 = a_evp_base_other_000 + a_evp_base_etrc_000 + a_evp_base_bath_000
    a_evp_base_total_090 = a_evp_base_other_090 + a_evp_base_etrc_090 + a_evp_base_bath_090
    a_evp_base_total_180 = a_evp_base_other_180 + a_evp_base_etrc_180 + a_evp_base_bath_180
    a_evp_base_total_270 = a_evp_base_other_270 + a_evp_base_etrc_270 + a_evp_base_bath_270

    a_evp_base_total_outside = a_evp_base_total_000, a_evp_base_total_090, a_evp_base_total_180, a_evp_base_total_270

    a_evp_base_total_inside = a_evp_base_other_inside + a_evp_base_etrc_inside + a_evp_base_bath_inside

    return a_evp_base_total_outside, a_evp_base_total_inside


def _get_a_evp_base_other(
        l_base_other_outside: (float, float, float, float), h_base_other: float
) -> ((float, float, float, float), float):
    """
    Args:
        l_base_other_outside: その他の土間床等の周辺部の長さ（室外側）（4方位）, m
        h_base_other: その他の基礎の高さ, m
    Returns:
        タプル
            (1) その他の基礎の面積（室外側）（4方位）, m2
            (2) その他の基礎の面積（室内側）, m2
    """

    l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270 = l_base_other_outside

    a_evp_base_other_000 = l_base_other_000 * h_base_other
    a_evp_base_other_090 = l_base_other_090 * h_base_other
    a_evp_base_other_180 = l_base_other_180 * h_base_other
    a_evp_base_other_270 = l_base_other_270 * h_base_other

    a_evp_base_other_outside = a_evp_base_other_000, a_evp_base_other_090, a_evp_base_other_180, a_evp_base_other_270

    a_evp_base_other_inside = 0.0

    return a_evp_base_other_outside, a_evp_base_other_inside


def _get_a_evp_base_bath(
        l_base_bath_outside: (float, float, float, float), l_base_bath_inside: float, h_base_bath: float
) -> ((float, float, float, float), float):
    """
    Args:
        l_base_bath_outside: 浴室の土間床等の周辺部の長さ（室外側）（4方位）, m
        l_base_bath_inside:  浴室の土間床等の周辺部の長さ（室内側）, m
        h_base_bath:  浴室の基礎の高さ, m
    Returns:
        タプル
            (1) 浴室の基礎の面積（室外側）（4方位）, m2
            (2) 浴室の基礎の面積（室内側）, m2
    """

    l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 = l_base_bath_outside

    a_base_bath_000 = l_base_bath_000 * h_base_bath
    a_base_bath_090 = l_base_bath_090 * h_base_bath
    a_base_bath_180 = l_base_bath_180 * h_base_bath
    a_base_bath_270 = l_base_bath_270 * h_base_bath

    a_evp_base_bath_outside = a_base_bath_000, a_base_bath_090, a_base_bath_180, a_base_bath_270

    a_base_bath_inside = l_base_bath_inside * h_base_bath

    return a_evp_base_bath_outside, a_base_bath_inside


def _get_a_evp_base_entrance(
        l_base_etrc_outside: (float, float, float, float), l_base_etrc_inside: float, h_base_etrc: float
) -> ((float, float, float, float), float):
    """
    Args:
        l_base_etrc_outside: 玄関等の土間床周辺部の長さ（室外側）（4方位）, m
        l_base_etrc_inside:  玄関等の土間床周辺部の長さ（室内側）, m
        h_base_etrc: 玄関等の基礎の高さ, m
    Returns:
        タプル
            (1) 玄関等の基礎の面積（室外側）（4方位）, m
            (2) 玄関等の基礎の面積（室内側）, m
    """

    l_base_etrc_000, l_base_etrc_090, l_base_etrc_180, l_base_etrc_270 = l_base_etrc_outside

    a_evp_base_etrc_000 = l_base_etrc_000 * h_base_etrc
    a_evp_base_etrc_090 = l_base_etrc_090 * h_base_etrc
    a_evp_base_etrc_180 = l_base_etrc_180 * h_base_etrc
    a_evp_base_etrc_270 = l_base_etrc_270 * h_base_etrc

    a_evp_base_etrc_outside = a_evp_base_etrc_000, a_evp_base_etrc_090, a_evp_base_etrc_180, a_evp_base_etrc_270

    a_evp_base_etrc_inside = l_base_etrc_inside * h_base_etrc

    return a_evp_base_etrc_outside, a_evp_base_etrc_inside


def _get_a_evp_roof(a_f: List[float]) -> float:
    """
    Args:
        a_f: 各階の床面積, m2
    Returns:
        屋根又は天井の面積, m2
    """

    return a_f[0]


def _get_l_base_total(
        l_base_etrc_outside: (float, float, float, float), l_base_entrance_inside: float,
        l_base_bath_outside: (float, float, float, float), l_base_bath_inside: float,
        l_base_other_outside: (float, float, float, float), l_base_other_inside: float
) -> ((float, float, float, float), float):
    """
    Args:
        l_base_etrc_outside: 玄関等の土間床等の外周部の長さ（室外側）（4方位）, m
        l_base_entrance_inside: 玄関等の土間床等の外周部の長さ（室内側）, m
        l_base_bath_outside: 浴室の土間床等の外周部の長さ（室外側）（4方位）, m
        l_base_bath_inside: 浴室の土間床等の外周部の長さ（室内側）, m
        l_base_other_outside: その他の土間床等の外周部の長さ（室外側）（4方位）, m
        l_base_other_inside: その他の土間床等の外周部の長さ（室内側）, m
    Returns:
        タプル
            (1) 土間床等の外周部の長さの合計（室外側）（4方位）, m
            (2) 土間床等の外周部の長さの合計（室内側）, m
    """

    l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270 = l_base_etrc_outside
    l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 = l_base_bath_outside
    l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270 = l_base_other_outside

    l_base_total_000 = l_base_other_000 + l_base_entrance_000 + l_base_bath_000
    l_base_total_090 = l_base_other_090 + l_base_entrance_090 + l_base_bath_090
    l_base_total_180 = l_base_other_180 + l_base_entrance_180 + l_base_bath_180
    l_base_total_270 = l_base_other_270 + l_base_entrance_270 + l_base_bath_270

    l_base_total_outside = l_base_total_000, l_base_total_090, l_base_total_180, l_base_total_270

    l_base_total_inside = l_base_other_inside + l_base_entrance_inside + l_base_bath_inside

    return l_base_total_outside, l_base_total_inside


def _get_l_base_other(
        house_type: str, floor_ins_type: str, l_ms: List[float], l_os: List[float],
        l_base_etrc_outside: (float, float, float, float), l_base_bath_outside: (float, float, float, float)
) -> ((float, float, float, float), float):
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床の断熱の種類
        l_ms: 主方位側の長さ, m
        l_os: その他方位側の長さ, m
        l_base_etrc_outside: 玄関等の土間床等の周辺部の長さ（室外側）（4方位）, m
        l_base_bath_outside: 浴室の土間床等の周辺部の長さ（室外側）（4方位）, m
    Returns:
        タプル
            (1) その他の土間床等の周辺部の長さ（室外側）（4方位）, m
            (2) その他の土間床等の周辺部の長さ（室内側）, m
    """

    l_base_entrance_000, l_base_entrance_090, l_base_entrance_180, l_base_entrance_270 = l_base_etrc_outside
    l_base_bath_000, l_base_bath_090, l_base_bath_180, l_base_bath_270 = l_base_bath_outside

    if house_type == 'detached' and floor_ins_type == 'base':
        l_base_other_000 = l_ms[0] - l_base_entrance_000 - l_base_bath_000
        l_base_other_090 = l_os[0] - l_base_entrance_090 - l_base_bath_090
        l_base_other_180 = l_ms[0] - l_base_entrance_180 - l_base_bath_180
        l_base_other_270 = l_os[0] - l_base_entrance_270 - l_base_bath_270
    else:
        l_base_other_000 = 0.0
        l_base_other_090 = 0.0
        l_base_other_180 = 0.0
        l_base_other_270 = 0.0

    l_base_other_outside = l_base_other_000, l_base_other_090, l_base_other_180, l_base_other_270

    l_base_other_inside = 0.0

    return l_base_other_outside, l_base_other_inside


def _get_a_evp_f_total(
        a_evp_f_etrc: float, a_evp_f_bath: float, a_evp_f_other: float) -> float:
    """
    Args:
        a_evp_f_etrc: 玄関の断熱した床の面積, m2
        a_evp_f_bath: 浴室の断熱した床の面積, m2
        a_evp_f_other: その他の断熱した床の面積, m2
    Returns:
        断熱した床の面積の合計, m2
    """

    return a_evp_f_etrc + a_evp_f_bath + a_evp_f_other


def _get_a_evp_f_other(
        a_f: List[float], a_evp_f_etrc: float, a_evp_f_bath: float, a_evp_ef_total: float) -> float:
    """
    Args:
        a_f: 各階の床面積, m2
        a_evp_f_etrc: 玄関の断熱した床の面積, m2
        a_evp_f_bath: 浴室の断熱した床の面積, m2
        a_evp_ef_total: 土間床の面積の合計, m2
    Returns:
        断熱した床の面積の合計, m2
    """

    return a_f[0] - a_evp_ef_total - a_evp_f_etrc - a_evp_f_bath


def _get_a_evp_ef_total(a_evp_ef_bath: float, a_evp_ef_etrc: float, a_evp_ef_other: float) -> float:
    """
    Args:
        a_evp_ef_bath: 浴室の土間の床面積, m2
        a_evp_ef_etrc: 玄関の土間の床面積, m2
        a_evp_ef_other: その他の土間の床面積, m2
    Returns:
        土間の床面積の合計, m2
    """

    return a_evp_ef_etrc + a_evp_ef_bath + a_evp_ef_other


def _get_a_evp_ef_other(
        house_type: str, floor_ins_type: str, a_f: List[float], a_evp_ef_bath: float, a_evp_ef_etrc: float) -> float:
    """
    Args:
        house_type: 住戸の種類
        floor_ins_type: 床の断熱の種類
        a_f: 各階の床面積, m2
        a_evp_ef_bath: 浴室の土間の床面積, m2
        a_evp_ef_etrc: 玄関の土間の床面積, m2
    Returns:
        その他の土間の床面積, m2
    """

    if house_type == 'detached' and floor_ins_type == 'base':
        return a_f[0] - a_evp_ef_etrc - a_evp_ef_bath
    else:
        return 0.0


def calc_area(
        house_type: str, a_f_total: float, r_open: float,
        floor_ins_type: str = None, bath_ins_type: str = None, a_env_input: float = None) -> Dict:
    """
    Args:
        house_type: 住戸の種類 (= 'detached', 'attached')
        a_f_total: 床面積の合計, m2
        r_open: 開口部の面積比率
        floor_ins_type: 床の断熱の種類 (= 'floor', 'base')
        bath_ins_type: 浴室の床の断熱の種類 (= 'floor', 'base', 'not_exist')
        a_env_input: 外皮面積の合計, m2
    Returns:

    """

    # region model house を作成するにあたってのデフォルト設定

    # 形状係数のデフォルト値
    # 集合住宅の場合
    #   デフォルト住宅の床面積は70.00m2であり、周長は、主方位側長さ6.14m、その他方位側長さ11.4mである。
    #   f_s = l_prm / (a_f ** 0.5 * 4) だから、
    #   f_s = (11.4 + 11.4 + 6.14 + 6.14) / (70 ** 0.5 * 4) = 1.048215... = 1.05
    f_s_default = {'detached': [1.08, 1.04], 'attached': [1.048215]}[house_type]

    # 1階の床面積に対する2階の床面積の比
    # 集合住宅の場合、平屋であるので、この値は定義できないため、Noneを返す。
    r_fa = {'detached': 0.77, 'attached': None}[house_type]

    # 玄関の基礎の高さ, m
    h_base_etrc = {'detached': 0.18, 'attached': 0.0}[house_type]

    # 浴室の基礎の高さ, m
    h_base_bath = {
        'detached': {
            'floor': {
                'floor': 0.0,
                'base': 0.5,
                'not_exist': 0.0,
                None: 0.0,
            }[bath_ins_type],
            'base': 0.5,
            None: 0.0,
        }[floor_ins_type],
        'attached': 0.0,
    }[house_type]

    # （玄関・浴室を除く）その他の部分の基礎の高さ
    h_base_other = {
        'detached': {'floor': 0.0, 'base': 0.5, None: 0.0}[floor_ins_type],
        'attached': 0.0,
    }[house_type]

    # 各階の高さ, m
    h = {'detached': [2.9, 2.7], 'attached': [2.8]}[house_type]

    # 玄関ドアの面積, m2
    #   集合住宅の玄関ドアは、0.9*1.95
    a_evp_door_entrance = {'detached': 1.89, 'attached': 1.755}[house_type]

    # 勝手口ドアの面積, m2
    a_evp_door_back_entrance = {'detached': 1.62, 'attached': 0.0}[house_type]

    # 主開口方位側の玄関の長さ, m
    # その他方位側の玄関の長さ, m
    l_etrc_ms, l_etrc_os = {'detached': (1.365, 1.82), 'attached': (1.0, 1.0)}[house_type]

    # 主開口方位側の浴室の長さ, m
    # その他方位側の浴室の長さ, m
    l_bath_ms, l_bath_os = {'detached': (1.82, 1.82), 'attached': (2.1, 1.365)}[house_type]

    # 窓の面積の合計に対する方位別の窓の面積
    # 集合住宅
    #   南側：2.26*2.0, 1.8*1.8
    #   西側：1.2*1.1, 0.6*0.9
    #   北側：1.2*1.1, 1.2*1.1
    #   南側の比率：0.632953..., 0.151713..., 0.215334... = 0.633, 0.1517, 0.2153, 0.0
    #   窓の面積の合計：12.26
    #   外皮の面積の合計：237.03
    #   面積比率：0.051723... = 0.052
    r_window = {
        'detached': (0.6862, 0.0721, 0.1097, 0.1320),
        'attached': (0.6330, 0.1517, 0.2153, 0.0000),
    }[house_type]

    # endregion

    # 各階の床面積, m2
    a_f = _get_a_f(house_type, a_f_total, r_fa)

    # 玄関の土間床等の面積, m2
    # 玄関の断熱した床の面積, m2
    # 玄関の土間床等の外周部の長さ, m
    a_evp_ef_etrc, a_evp_f_etrc, l_base_etrc_outside, l_base_etrc_inside = _get_entrance(
        house_type, floor_ins_type, l_etrc_ms, l_etrc_os)

    # 浴室の土間床等の面積, m2
    # 浴室の断熱した床の面積, m2
    # 浴室の土間床等の外周部の長さ, m
    a_evp_ef_bath, a_evp_f_bath, l_base_bath_outside, l_base_bath_inside = _get_bath(
        house_type, floor_ins_type, bath_ins_type, l_bath_ms, l_bath_os)

    # 各階の形状係数
    # 外皮の面積の合計が定義されていない場合はデフォルト値を使用する。
    # 外皮の面積の合計が定義されている場合は、そこから逆算して形状係数を求める。
    if a_env_input is None:
        f_s = f_s_default
    else:
        f_s = _get_f_s(
            house_type, floor_ins_type, bath_ins_type,
            a_env_input, a_f, h, h_base_other, h_base_bath, h_base_etrc,
            l_base_bath_outside, l_base_bath_inside, l_base_etrc_outside, l_base_etrc_inside, f_s_default)

    # 各階の周長, m
    l_prm = _get_l_prm(a_f, f_s)

    # 主方位の辺の長さ, m
    # その他方位の辺の長さ, m
    # 集合住宅の場合は修正する必要あり
    l_ms, l_os = _get_l(house_type, a_f, l_prm)

    # その他の土間の床面積, m2
    a_evp_ef_other = _get_a_evp_ef_other(house_type, floor_ins_type, a_f, a_evp_ef_bath, a_evp_ef_etrc)

    # 土間の床面積の合計, m2
    a_evp_ef_total = _get_a_evp_ef_total(a_evp_ef_bath, a_evp_ef_etrc, a_evp_ef_other)

    # その他の断熱した床面積, m2
    a_evp_f_other = _get_a_evp_f_other(a_f, a_evp_f_etrc, a_evp_f_bath, a_evp_ef_total)

    # 断熱した床面積の合計, m2
    a_evp_f_total = _get_a_evp_f_total(a_evp_f_etrc, a_evp_f_bath, a_evp_f_other)

    # その他の土間床等の外周部の長さ（室外側）（4方位）, m
    # その他の土間床等の外周部の長さ（室内側）, m
    l_base_other_outside, l_base_other_inside = _get_l_base_other(
        house_type, floor_ins_type, l_ms, l_os, l_base_etrc_outside, l_base_bath_outside)

    # 土間床等の外周部の長さの合計（室外側）（4方位）, m
    # 土間床等の外周部の長さの合計（室内側）, m
    l_base_total_outside, l_base_total_inside = _get_l_base_total(
        l_base_etrc_outside, l_base_etrc_inside,
        l_base_bath_outside, l_base_bath_inside,
        l_base_other_outside, l_base_other_inside)

    # 屋根又は天井の面積, m2
    a_evp_roof = _get_a_evp_roof(a_f)

    # 玄関等の基礎の面積（室外側）（4方位）, m2
    # 玄関等の基礎の面積（室内側）, m2
    a_evp_base_etrc_outside, a_evp_base_etrc_inside = _get_a_evp_base_entrance(
        l_base_etrc_outside, l_base_etrc_inside, h_base_etrc)

    # 浴室の基礎の面積（室外側）（4方位）, m2
    # 浴室の基礎の面積（室内側）, m2
    a_evp_base_bath_outside, a_evp_base_bath_inside = _get_a_evp_base_bath(
            l_base_bath_outside, l_base_bath_inside, h_base_bath)

    # その他の基礎の面積（室外側）（4方位）, m2
    # その他の基礎の面積（室内側）, m2
    a_evp_base_other_outside, a_evp_base_other_inside = _get_a_evp_base_other(l_base_other_outside, h_base_other)

    # 基礎の面積の合計（室外側）（4方位）, m2
    # 基礎の面積の合計（室内側）, m2
    a_evp_base_total_outside, a_evp_base_total_inside = _get_a_evp_base_total(
        a_evp_base_etrc_outside, a_evp_base_etrc_inside,
        a_evp_base_bath_outside, a_evp_base_bath_inside,
        a_evp_base_other_outside, a_evp_base_other_inside)

    # 各階の壁面積（窓面積を含む）（4方位）, m2
    a_evp_srf = _get_a_evp_srf(l_ms, l_os, h)

    # 外皮の面積の合計（基礎の面積を除く）, m2
    a_evp_total_not_base = _get_a_evp_total_not_base(a_evp_ef_total, a_evp_f_total, a_evp_roof, a_evp_srf)

    # 外皮の面積の合計, m2
    a_evp_total = _get_a_evp_total(a_evp_base_total_outside, a_evp_base_total_inside, a_evp_total_not_base)

    # 開口部の面積の合計, m2
    a_evp_open_total = _get_a_evp_open_total(a_evp_total_not_base, r_open)

    # 窓の面積の合計, m2
    a_evp_window_total = _get_a_evp_window_total(a_evp_door_back_entrance, a_evp_door_entrance, a_evp_open_total)

    # 窓の面積の合計, m2
    a_evp_window = _get_a_evp_window(a_evp_window_total, r_window)

    # ドアの面積, m2
    a_evp_door = _get_a_evp_door(a_evp_door_back_entrance, a_evp_door_entrance, house_type)

    # 壁の面積, m2
    a_evp_wall = _get_a_evp_wall(a_evp_door, a_evp_srf, a_evp_window)

    return dict(
        house_type=house_type,
        floor_ins_type=floor_ins_type,
        bath_ins_type=bath_ins_type,
        a_f=a_f,
        a_evp_ef_etrc=a_evp_ef_etrc,
        a_evp_f_etrc=a_evp_f_etrc,
        l_base_etrc_outside=l_base_etrc_outside,
        l_base_etrc_inside=l_base_etrc_inside,
        a_evp_ef_bath=a_evp_ef_bath,
        a_evp_f_bath=a_evp_f_bath,
        l_base_bath_outside=l_base_bath_outside,
        l_base_bath_inside=l_base_bath_inside,
        f_s=f_s,
        l_prm=l_prm,
        l_ms=l_ms,
        l_os=l_os,
        a_evp_ef_other=a_evp_ef_other,
        a_evp_ef_total=a_evp_ef_total,
        a_evp_f_other=a_evp_f_other,
        a_evp_f_total=a_evp_f_total,
        l_base_other_outside=l_base_other_outside,
        l_base_other_inside=l_base_other_inside,
        l_base_total_outside=l_base_total_outside,
        l_base_total_inside=l_base_total_inside,
        a_evp_roof=a_evp_roof,
        a_evp_base_etrc_outside=a_evp_base_etrc_outside,
        a_evp_base_etrc_inside=a_evp_base_etrc_inside,
        a_evp_base_bath_outside=a_evp_base_bath_outside,
        a_evp_base_bath_inside=a_evp_base_bath_inside,
        a_evp_base_other_outside=a_evp_base_other_outside,
        a_evp_base_other_inside=a_evp_base_other_inside,
        a_evp_base_total_outside=a_evp_base_total_outside,
        a_evp_base_total_inside=a_evp_base_total_inside,
        a_evp_srf=a_evp_srf,
        a_evp_total_not_base=a_evp_total_not_base,
        a_evp_total=a_evp_total,
        a_evp_open_total=a_evp_open_total,
        a_evp_window_total=a_evp_window_total,
        a_evp_window=a_evp_window,
        a_evp_door=a_evp_door,
        a_evp_wall=a_evp_wall,
    )


if __name__ == '__main__':

    result1 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='base',
        a_env_input=266.10)
    result2 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='floor',
        a_env_input=262.46)
    result3 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='not_exist',
        a_env_input=262.46)
    result4 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='base', a_env_input=275.69)
    result5 = calc_area(
        house_type='attached', a_f_total=70.00, r_open=0.05885, a_env_input=238.22)
    result6 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='base')
    result7 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='floor')
    result8 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='floor', bath_ins_type='not_exist')
    result9 = calc_area(
        house_type='detached', a_f_total=90.00, r_open=0.14, floor_ins_type='base')
    result10 = calc_area(
        house_type='attached', a_f_total=70.00, r_open=0.05885)

    print(result1)
    print(result2)
    print(result3)
    print(result4)
    print(result5)
    print(result6)
    print(result7)
    print(result8)
    print(result9)
    print(result10)
