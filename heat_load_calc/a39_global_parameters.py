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


def get_l_wtr() -> float:
    """
    Returns:
         水の蒸発潜熱, J/kg
    """
    return 2501000.0


def get_c_air() -> float:
    """
    Returns:
        空気の比熱, J/kg K
    """
    return 1005.0


def get_rho_air() -> float:
    """
    Returns:
        空気の密度, kg/m3
    """
    return 1.2
