from enum import Enum


class BoundaryType(Enum):
    """
    境界の種類
    """

    # 'internal': 間仕切り
    Internal = 'internal'

    # 'external_general_part': 外皮_一般部位
    ExternalGeneralPart = 'external_general_part'

    # 'external_transparent_part': 外皮_透明な開口部
    ExternalTransparentPart = 'external_transparent_part'

    # 'external_opaque_part': 外皮_不透明な開口部
    ExternalOpaquePart = 'external_opaque_part'

    # 'ground': 地盤
    Ground = 'ground'

