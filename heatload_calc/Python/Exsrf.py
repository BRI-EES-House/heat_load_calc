import math
from apdx5_solar_position import defSolpos

# from inclined_surface_solar_radiation import calc_inclined_surface_solar_radiation
from common import is_float_equal

# 外表面の情報を保持するクラス
class Exsrf:
    """外表面の基本情報（方位角、傾斜角、地面反射率、温度差係数等）を保持するクラスを定義します。"""

    # 初期化
    def __init__(self):
        pass
        """
        :param boundary_type: 境界の種類（1:間仕切り、2:外皮、3:地盤）
        :param direction: 向き
        :param is_sun_striked_outside: 日射の有無
        :param temp_dif_coef: 温度差係数
        :param next_room_type: 隣室タイプ
        """
    
        
def internal_init(exsrf, next_room_type):
    # 隣室の場合
    exsrf.Type = "internal"
    exsrf.nextroomname = next_room_type          # 隣室名称

def ground_init(exsrf):
    exsrf.Type = "ground"                        # 土壌の場合

# 傾斜面の相当外気温度の計算
def get_Te(exsrf, Iw,  _as, ho, e, Ta, RN):
    """
    :param _as: 日射吸収率 [-]
    :param ho: 外表面の総合熱伝達率[W/m2K]
    :param e: 外表面の放射率[-]
    :param Ta: 外気温度[℃]
    :param RN: 夜間放射量[W/m2]
    :return: 傾斜面の相当外気温度 [℃]
    """
    Te = Ta + (_as * Iw - exsrf.Fs * e * RN) / ho

    return Te

# 温度差係数を設定した隣室温度
def get_NextRoom_fromR(exsrf, Ta, Tr):
    Te = exsrf.R * Ta + (1.0 - exsrf.R) * Tr
    return Te

# 前時刻の隣室温度の場合
def get_oldNextRoom(exsrf, spaces):
    Te = spaces[exsrf.nextroomname].oldTr
    return Te

# 外皮として初期化
def external_init(exsrf, direction, is_sun_striked_outside, temp_dif_coef):
    exsrf.Type = "external"                      # 境界条件タイプ

    # 外皮の場合
    exsrf.Rg = 0.1                           # 地面反射率[-]
    exsrf.direction = direction
    exsrf.Wa, exsrf.Wb = convert_slope_angle(direction)
                                            # 方位角、傾斜面方位角 [rad]
    # 太陽入射角の方向余弦cosθ　計算用パラメータ
    exsrf.Wz = math.cos(exsrf.Wb)
    exsrf.Ww = math.sin(exsrf.Wb) * math.sin(exsrf.Wa)
    exsrf.Ws = math.sin(exsrf.Wb) * math.cos(exsrf.Wa)
    exsrf.Fs = (1.0 + exsrf.Wz) / 2.0           # 傾斜面の天空に対する形態係数の計算
    exsrf.dblFg = 1.0 - exsrf.Fs                # 傾斜面の地面に対する形態係数

    exsrf.R = temp_dif_coef                      # 温度差係数
    exsrf.is_sun_striked_outside = is_sun_striked_outside

# 方向名称から方位角、傾斜角の計算
def convert_slope_angle(direction_string):
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

# 外表面情報インスタンスの辞書を作成
# def create_exsurfaces(d):
#     # for d_surface in d:
#     dic = Exsrf(
#         d['boundary_type'],
#         d['direction'],
#         d['is_sun_striked_outside'],
#         d['temp_dif_coef'],
#         d['next_room_type']
#     )
#     return dic
