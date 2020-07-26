from collections import namedtuple
from typing import Dict, List

from heat_load_calc.initializer.boundary_type import BoundaryType
from heat_load_calc.a8_shading import SolarShadingPart
from heat_load_calc import a8_shading as a8

Boundary = namedtuple('Boundary', [
    'name',
    'boundary_type',
    'area',
    'is_sun_striked_outside',
    'temp_dif_coef',
    'direction',
    'next_room_type',
    'is_solar_absorbed_inside',
    'spec',
    'solar_shading_part',
    'inside_heat_transfer_resistance'

])

InternalPartSpec = namedtuple('InternalPartSpec', [
    'outside_heat_transfer_resistance',
    'layers'
])

GeneralPartSpec = namedtuple('GeneralPartSpec', [
    'outside_emissivity',
    'outside_solar_absorption',
    'outside_heat_transfer_resistance',
    'layers'
])

TransparentOpeningPartSpec = namedtuple('TransparentOpeningPartSpec', [
    'eta_value',
    'u_value',
    'outside_emissivity',
    'outside_heat_transfer_resistance',
    'incident_angle_characteristics'
])

OpaqueOpeningPartSpec = namedtuple('OpaqueOpeningPartSpec', [
    'outside_emissivity',
    'outside_solar_absorption',
    'outside_heat_transfer_resistance',
    'u_value'
])

GroundSpec = namedtuple('GroundSpec', [
    'layers'
])

InternalPartSpecLayers = namedtuple('InternalPartSpecLayers', [
    'name',
    'thermal_resistance',
    'thermal_capacity'
])

GeneralPartSpecLayers = namedtuple('GeneralPartSpecLayers', [
    'name',
    'thermal_resistance',
    'thermal_capacity'
])

GroundSpecLayers = namedtuple('GroundSpecLayers', [
    'name',
    'thermal_resistance',
    'thermal_capacity'
])


def get_boundary(b: Dict) -> Boundary:
    """
    入力ファイルの辞書の'boundaries'を読み込む。

    Args:
        b: 'boundaries' キーの要素（リスト）のうちの1要素

    Returns:
        Boundary クラス
    """

    # 室iの境界k

    # 名前
    name = b['name']

    # 境界の種類
    # 'internal': 間仕切り
    # 'external_general_part': 外皮_一般部位
    # 'external_transparent_part': 外皮_透明な開口部
    # 'external_opaque_part': 外皮_不透明な開口部
    # 'ground': 地盤
    # boundary_type = b['boundary_type']
    boundary_type = {
        'internal': BoundaryType.Internal,
        'external_general_part': BoundaryType.ExternalGeneralPart,
        'external_transparent_part': BoundaryType.ExternalTransparentPart,
        'external_opaque_part': BoundaryType.ExternalOpaquePart,
        'ground': BoundaryType.Ground
    }[b['boundary_type']]

    # 面積, m2
    area = float(b['area'])

    # 日射の有無
    # True: 当たる
    # False: 当たらない
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    if b['boundary_type'] == 'external_general_part' \
            or b['boundary_type'] == 'external_transparent_part' \
            or b['boundary_type'] == 'external_opaque_part':
        is_sun_striked_outside = bool(b['is_sun_striked_outside'])
    else:
        is_sun_striked_outside = None

    # 温度差係数
    # 境界の種類が'external_general_part', 'external_transparent_part', 'external_opaque_part'の場合に定義される。
    if b['boundary_type'] == 'external_general_part' \
            or b['boundary_type'] == 'external_transparent_part' \
            or b['boundary_type'] == 'external_opaque_part':
        temp_dif_coef = float(b['temp_dif_coef'])
    else:
        temp_dif_coef = 0.0

    # 方位
    # 's', 'sw', 'w', 'nw', 'n', 'ne', 'e', 'se', 'top', 'bottom'
    # 日射の有無が定義されている場合でかつその値がTrueの場合のみ定義される。
    if 'is_sun_striked_outside' in b:
        if b['is_sun_striked_outside']:
            direction = b['direction']
        else:
            direction = None
    else:
        direction = None

    # 隣室タイプ
    # 'main_occupant_room': 主たる居室
    # 'other_occupant_room': その他の居室
    # 'non_occupant_room' : 非居室
    # 'underfloor': 床下空間
    # 境界の種類が'internal'の場合に定義される。
    if b['boundary_type'] == 'internal':
        next_room_type = b['next_room_type']
    else:
        next_room_type = None

    # 室内侵入日射吸収の有無
    # True: 吸収する
    # False: 吸収しない
    is_solar_absorbed_inside = bool(b['is_solar_absorbed_inside'])

    # 室内側熱伝達抵抗, m2K/W
    inside_heat_transfer_resistance = b['inside_heat_transfer_resistance']

    # spec
    # 境界の種類に応じて、それぞれ対応するクラスを取得する。
    if b['boundary_type'] == 'internal':
        spec = get_internal_part_spec(b)
    elif b['boundary_type'] == 'external_general_part':
        spec = get_general_part_spec(b)
    elif b['boundary_type'] == 'external_transparent_part':
        spec = get_transparent_opening_part_spec(b)
    elif b['boundary_type'] == 'external_opaque_part':
        spec = get_opaque_opening_part_spec(b)
    elif b['boundary_type'] == 'ground':
        spec = get_ground_spec(b)
    else:
        raise ValueError

    solar_shading_part = a8.SolarShadingPart.create(ssp=b['solar_shading_part'])

    return Boundary(
        name=name,
        boundary_type=boundary_type,
        area=area,
        is_sun_striked_outside=is_sun_striked_outside,
        temp_dif_coef=temp_dif_coef,
        direction=direction,
        next_room_type=next_room_type,
        is_solar_absorbed_inside=is_solar_absorbed_inside,
        spec=spec,
        solar_shading_part=solar_shading_part,
        inside_heat_transfer_resistance=inside_heat_transfer_resistance
    )


def get_internal_part_spec(b: Dict) -> InternalPartSpec:
    """
    入力ファイルの辞書の'internal_part_spec'を読み込む。

    Args:
        b: 'boundaries' キーの要素（リスト）のうちの1要素

    Returns:
        InternalPartSpec クラス
    """

    # 下記、key が間違っている。
    # jsonファイルを修正する必要あり。
    # spec = b['internal_part_spec']
    spec = b['general_part_spec']

    # 室外側熱伝達抵抗, m2K/W
    outside_heat_transfer_resistance = float(spec['outside_heat_transfer_resistance'])

    layers = get_internal_part_spec_layers(b)

    return InternalPartSpec(
        outside_heat_transfer_resistance=outside_heat_transfer_resistance,
        layers=layers
    )


def get_general_part_spec(b: Dict) -> GeneralPartSpec:
    """
    入力ファイルの辞書の'general_part_spec'を読み込む。

    Args:
        b: 'boundaries' キーの要素（リスト）のうちの1要素

    Returns:
        GeneralPartSpec クラス
    """

    spec = b['general_part_spec']

    # 室外側長波長放射率
    outside_emissivity = float(spec['outside_emissivity'])

    # 室外側日射吸収率
    outside_solar_absorption = float(spec['outside_solar_absorption'])

    # 室外側熱伝達抵抗, m2K/W
    outside_heat_transfer_resistance = float(spec['outside_heat_transfer_resistance'])

    layers = get_general_part_spec_layers(b)

    return GeneralPartSpec(
        outside_emissivity=outside_emissivity,
        outside_solar_absorption=outside_solar_absorption,
        outside_heat_transfer_resistance=outside_heat_transfer_resistance,
        layers=layers
    )


def get_transparent_opening_part_spec(b: Dict) -> TransparentOpeningPartSpec:
    """
    入力ファイルの辞書の'transparent_opening_part_spec'を読み込む。

    Args:
        b: 'boundaries' キーの要素（リスト）のうちの1要素

    Returns:
        TransparentOpeningPartSpec クラス
    """

    spec = b['transparent_opening_part_spec']

    # 日射熱取得率
    eta_value = float(spec['eta_value'])

    # 熱貫流率, W/m2K
    u_value = float(spec['u_value'])

    # 室外側長波長放射率
    outside_emissivity = float(spec['outside_emissivity'])

    # 室外側熱伝達抵抗, m2K/W
    outside_heat_transfer_resistance = float(spec['outside_heat_transfer_resistance'])

    # ガラスの入射角特性タイプ
    # 'single': 単層
    # 'double': 複層
    incident_angle_characteristics = spec['incident_angle_characteristics']

    return TransparentOpeningPartSpec(
        eta_value=eta_value,
        u_value=u_value,
        outside_emissivity=outside_emissivity,
        outside_heat_transfer_resistance=outside_heat_transfer_resistance,
        incident_angle_characteristics=incident_angle_characteristics
    )


def get_opaque_opening_part_spec(b: Dict) -> OpaqueOpeningPartSpec:
    """
    入力ファイルの辞書の'opaque_opening_part_spec'を読み込む。

    Args:
        b: 'boundaries' キーの要素（リスト）のうちの1要素

    Returns:
        OpaqueOpeningPartSpec クラス
    """

    spec = b['opaque_opening_part_spec']

    # 室外側長波長放射率
    outside_emissivity = float(spec['outside_emissivity'])

    # 室外側日射吸収率
    outside_solar_absorption = float(spec['outside_solar_absorption'])

    # 室外側熱伝達抵抗, m2K/W
    outside_heat_transfer_resistance = float(spec['outside_heat_transfer_resistance'])

    # 熱貫流率, W/m2K
    u_value = float(spec['u_value'])

    return OpaqueOpeningPartSpec(
        outside_emissivity=outside_emissivity,
        outside_solar_absorption=outside_solar_absorption,
        outside_heat_transfer_resistance=outside_heat_transfer_resistance,
        u_value=u_value
    )


def get_ground_spec(b: Dict) -> GroundSpec:
    """
    入力ファイルの辞書の'ground_spec'を読み込む。

    Args:
        b: 'boundaries' キーの要素（リスト）のうちの1要素

    Returns:
        GroundSpec クラス
    """

    spec = b['ground_spec']

    layers = get_ground_spec_layers(b)

    return GroundSpec(
        layers=layers
    )


def get_internal_part_spec_layers(b: Dict) -> List[InternalPartSpecLayers]:

    # 下記、key が間違っている。
    # jsonファイルを修正する必要あり。
    # spec = b['internal_part_spec']
    spec = b['general_part_spec']

    layers = spec['layers']

    return [
        InternalPartSpecLayers(

            # 名前
            name=layer['name'],

            # 熱抵抗, m2K/W
            thermal_resistance=float(layer['thermal_resistance']),

            # 熱容量, kJ/m2K
            thermal_capacity=float(layer['thermal_capacity'])

        ) for layer in layers
    ]


def get_general_part_spec_layers(b: Dict) -> List[InternalPartSpecLayers]:

    spec = b['general_part_spec']

    layers = spec['layers']

    return [
        InternalPartSpecLayers(

            # 名前
            name=layer['name'],

            # 熱抵抗, m2K/W
            thermal_resistance=float(layer['thermal_resistance']),

            # 熱容量, kJ/m2K
            thermal_capacity=float(layer['thermal_capacity'])

        ) for layer in layers
    ]


def get_ground_spec_layers(b: Dict) -> List[GroundSpecLayers]:

    spec = b['ground_spec']

    layers = spec['layers']

    return [
        GroundSpecLayers(

            # 名前
            name=layer['name'],

            # 熱抵抗, m2K/W
            thermal_resistance=float(layer['thermal_resistance']),

            # 熱容量, kJ/m2K
            thermal_capacity=float(layer['thermal_capacity'])

        ) for layer in layers
    ]

