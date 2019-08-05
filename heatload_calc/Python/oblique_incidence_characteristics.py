# 透明部位の入射角特性
# 直達日射の入射角特性の計算
def get_CID(CosT: float) -> float:
    """
    :param CosT: 入射角の方向余弦
    :return: 直達日射の入射角特性
    """
    CID = (2.392 * CosT - 3.8636 * CosT ** 3.0 + 3.7568 * CosT ** 5.0 - 1.3965 * CosT ** 7.0) / 0.88
    return CID