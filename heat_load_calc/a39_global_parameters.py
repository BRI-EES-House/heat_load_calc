from enum import Enum, auto


class BoundaryType(Enum):
    """
        境界の種類
    """

    # 'internal': 間仕切り
    Internal = auto()

    # 'external_general_part': 外皮_一般部位
    ExternalGeneralPart = auto()

    # 'external_transparent_part': 外皮_透明な開口部
    ExternalTransparentPart = auto()

    # 'external_opaque_part': 外皮_不透明な開口部
    ExternalOpaquePart = auto()

    # 'ground': 地盤
    Ground = auto()


class SpaceType(Enum):

    # 主たる居室
    MAIN_HABITABLE_ROOM = auto()

    # その他の居室
    OTHER_HABITABLE_ROOM = auto()

    # 非居室
    NON_HABITABLE_ROOM = auto()

    # 床下空間
    UNDERFLOOR = auto()
