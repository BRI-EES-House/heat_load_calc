import numpy as np

# 透明部位の入射角特性
# 直達日射の入射角特性の計算
def get_CID(CosT: np.ndarray, incident_angle_characteristics: str) -> np.ndarray:
    """
    :param CosT: 入射角の方向余弦
    :incident_angle_characteristics: ガラスの入射角特性タイプ
    :return: 直達日射の入射角特性
    """
    if incident_angle_characteristics == "single":
        CID = get_taud_n_single(CosT)
    elif incident_angle_characteristics == "multiple":
        CID = get_taud_n_double(CosT)
    else:
        print("ガラスの入射角特性タイプ ", incident_angle_characteristics, " が未定義です")

    CID[CosT <= 0.0] = 0.0

    return CID

# 拡散日射の入射角特性の計算
def get_Cd(incident_angle_characteristics: str) -> float:
    Cd = 0.0
    if incident_angle_characteristics == "single":
        Cd = get_taus_n_single()
    elif incident_angle_characteristics == "multiple":
        Cd = get_taus_n_double()
    else:
        print("ガラスの入射角特性タイプ ", incident_angle_characteristics, " が未定義です")
    return Cd

# 直達日射に対する基準化透過率の計算（単層ガラス）
def get_taud_n_single(cos_phi: float) -> float:
    return 0.000 * cos_phi ** 0.0 + 2.552 * cos_phi ** 1.0 + 1.364 * cos_phi ** 2.0 \
        - 11.388 * cos_phi ** 3.0 + 13.617 * cos_phi ** 4.0 - 5.146 * cos_phi ** 5.0

# 直達日射に対する基準化反射率の計算（単層ガラス）
def get_rhod_n_single(cos_phi: float) -> float:
    return 1.000 * cos_phi ** 0.0 - 5.189 * cos_phi ** 1.0 + 12.392 * cos_phi ** 2.0 \
        - 16.593 * cos_phi ** 3.0 + 11.851 * cos_phi ** 4.0 - 3.461 * cos_phi ** 5.0

# 直達日射に対する基準化透過率の計算（複層ガラス）
def get_taud_n_double(cos_phi: float) -> float:
    return get_taud_n_single(cos_phi) ** 2.0 / (1.0 - get_rhod_n_single(cos_phi) ** 2.0)

# 拡散日射に対する基準化透過率（単層ガラス）
def get_taus_n_single() -> float:
    return 0.900

# 拡散日射に対する基準化透過率（複層ガラス）
def get_taus_n_double() -> float:
    return 0.832
