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

