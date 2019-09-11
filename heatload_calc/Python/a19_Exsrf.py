import math

# 外表面の情報を保持するクラス
class Exsrf:
    """外表面の基本情報（方位角、傾斜角、地面反射率、温度差係数等）を保持するクラスを定義します。"""

    # 初期化
    def __init__(self) -> None:
        self.Type = None
        self.nextroomname = None
        self.RhoG_l = None  # 地面反射率[-]
        self.direction = None
        self.Wa = None
        self.Wb = None
        self.Wz = None
        self.Ww = None
        self.Ws = None
        self.PhiS_i_k = None  # 傾斜面の天空に対する形態係数の計算
        self.PhiG_i_k = None  # 傾斜面の地面に対する形態係数

        self.a_i_k = None  # 温度差係数
        self.is_sun_striked_outside = None

        
def internal_init(next_room_type: str) -> Exsrf:
    exsrf = Exsrf()
    # 隣室の場合
    exsrf.Type = "internal"
    exsrf.nextroomname = next_room_type          # 隣室名称
    return exsrf


def ground_init() -> Exsrf:
    exsrf = Exsrf()
    exsrf.Type = "ground"                        # 土壌の場合
    return exsrf


# 外皮として初期化
def external_init(direction: str, is_sun_striked_outside: bool, a_i_k: float) -> Exsrf:
    exsrf = Exsrf()

    exsrf.Type = "external"                      # 境界条件タイプ

    # 地面反射率[-]
    exsrf.RhoG_l = 0.1

    exsrf.direction = direction

    # 方位角、傾斜面方位角 [rad]
    exsrf.Wa, exsrf.Wb = get_slope_angle(direction)

    # 傾斜面に関する変数であり、式(73)
    exsrf.Wz, exsrf.WW, exsrf.Ws = get_Wz_Ww_Ws(exsrf.Wa, exsrf.Wb)

    # 傾斜面の天空に対する形態係数の計算 式(120)
    exsrf.PhiS_i_k = get_Phi_S_i_k(exsrf.Wz)

    # 傾斜面の地面に対する形態係数 式(119)
    exsrf.PhiG_i_k = get_Phi_G_i_k(exsrf.PhiS_i_k)

    # 温度差係数
    exsrf.a_i_k = a_i_k

    exsrf.is_sun_striked_outside = is_sun_striked_outside

    return exsrf


# 傾斜面に関する変数であり、式(73)
def get_Wz_Ww_Ws(Wa, Wb):
    # 太陽入射角の方向余弦cosθ　計算用パラメータ
    Wz = math.cos(Wb)
    Ww = math.sin(Wb) * math.sin(Wa)
    Ws = math.sin(Wb) * math.cos(Wa)

    return Wz, Ww, Ws

# 方向名称から方位角、傾斜角の計算 表11 方位と方位角、傾斜角の対応
def get_slope_angle(direction_string: str) -> tuple:
    direction_angle = -999.0
    inclination_angle = -999.0
    if direction_string == 's':
        direction_angle = 0.0
        inclination_angle = 90.0
    elif direction_string == 'sw':
        direction_angle = 45.0
        inclination_angle = 90.0
    elif direction_string == 'w':
        direction_angle = 90.0
        inclination_angle = 90.0
    elif direction_string == 'nw':
        direction_angle = 135.0
        inclination_angle = 90.0
    elif direction_string == 'n':
        direction_angle = 180.0
        inclination_angle = 90.0
    elif direction_string == 'ne':
        direction_angle = -135.0
        inclination_angle = 90.0
    elif direction_string == 'e':
        direction_angle = -90.0
        inclination_angle = 90.0
    elif direction_string == 'se':
        direction_angle = -45.0
        inclination_angle = 90.0
    elif direction_string == 'top':
        direction_angle = 0.0
        inclination_angle = 0.0
    elif direction_string == 'bottom':
        direction_angle = 0.0
        inclination_angle = 180.0
    
    return math.radians(direction_angle), math.radians(inclination_angle)


# 傾斜面の地面に対する形態係数 式(119)
def get_Phi_G_i_k(PhiS_i_k):
    return 1.0 - PhiS_i_k


# 傾斜面の天空に対する形態係数の計算 式(120)
def get_Phi_S_i_k(Wz):
    return (1.0 + Wz) / 2.0

