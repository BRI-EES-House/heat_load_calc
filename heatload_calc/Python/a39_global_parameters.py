from enum import Enum, auto


class OperationMode(Enum):

    # 冷房
    COOLING = auto()

    # 暖房
    HEATING = auto()

    # 暖房・冷房停止で窓「開」
    STOP_OPEN = auto()

    # 暖房・冷房停止で窓「閉」
    STOP_CLOSE = auto()


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
