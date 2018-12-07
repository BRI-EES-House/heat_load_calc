# 季節ごとの特性値を保持するクラス
class SeasonalValue:
    """室ごとの季節別換気量を保持します。"""

    def __init__(self, winter, inter, summer):
        """
        :param winter: 冬期特性値
        :param inter: 中間期特性値
        :param summer: 夏期特性値
        """
        self.winter = winter  # 冬期の特性値
        self.inter = inter  # 中間期の特性値
        self.summer = summer  # 夏期の特性値
