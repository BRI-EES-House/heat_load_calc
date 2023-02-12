from enum import Enum


class NextSpace(Enum):
    """
    隣接する空間（相手方）の種類
    """

    # 外気
    OUTDOOR = 'outdoor'
    # 外気に通じる空間
    OPEN_SPACE = 'open_space'
    # 外気に通じない空間
    CLOSED_SPACE = 'closed_space'
    # 住戸及び住戸と同様の熱的環境の空問
    AIR_CONDITIONED = 'air_conditioned'
    # 外気に通じる床裏
    OPEN_UNDERFLOOR = 'open_underfloor'
    # 外気に通じない床裏
    CLOSED_UNDERFLOOR = 'closed_underfloor'

    def get_is_sun_striked_outside(self) -> bool:
        """
        相手方空間に日射が当たるか否かを判断する。
        Returns:
            相手方空間に日射が当たるか否か
        """
        return {
            NextSpace.OUTDOOR: True,
            NextSpace.OPEN_SPACE: False,
            NextSpace.CLOSED_SPACE: False,
            NextSpace.OPEN_UNDERFLOOR: False,
            NextSpace.AIR_CONDITIONED: False,
            NextSpace.CLOSED_UNDERFLOOR: False
        }[self]

    def get_h(self, region: int) -> float:
        """
        Args:
            region: 地域の区分
        Returns:
            温度差係数
        """

        return {
            NextSpace.OUTDOOR: 1.0,
            NextSpace.OPEN_SPACE: 1.0,
            NextSpace.CLOSED_SPACE: 0.7,
            NextSpace.OPEN_UNDERFLOOR: 0.7,
            NextSpace.AIR_CONDITIONED: {
                1: 0.05,
                2: 0.05,
                3: 0.05,
                4: 0.15,
                5: 0.15,
                6: 0.15,
                7: 0.15,
                8: 0.15
            }[region],
            NextSpace.CLOSED_UNDERFLOOR: {
                1: 0.05,
                2: 0.05,
                3: 0.05,
                4: 0.15,
                5: 0.15,
                6: 0.15,
                7: 0.15,
                8: 0.15
            }[region],
        }[self]

