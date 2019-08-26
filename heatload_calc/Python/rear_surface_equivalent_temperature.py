

# 裏面の相当温度を計算する
def calcTeo(surface, Ta, Iw, RN, oldTr, AnnualTave, spaces):
    # 前時刻の相当外気温度を控える
    surface.oldTeo = surface.Teo

    # 日射の当たる一般部位または不透明部位の場合
    if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
        # 室外側に日射が当たる場合
        if surface.is_sun_striked_outside:
            surface.Teo = get_Te(surface.backside_boundary_condition, Iw, surface.outside_solar_absorption, surface.ho, surface.Eo, Ta, RN)
        # 室外側に日射が当たらない場合
        else:
            surface.Teo = get_NextRoom_fromR(surface.backside_boundary_condition, Ta, oldTr)
    # 窓の場合
    elif surface.boundary_type == "external_transparent_part":
        surface.Teo = - surface.Eo * surface.backside_boundary_condition.Fs * RN / surface.ho + Ta
    # 土壌の場合
    elif surface.boundary_type == "ground":
        surface.Teo = AnnualTave
    # 内壁の場合（前時刻の室温）
    elif surface.boundary_type == "internal":
        surface.Teo = get_oldNextRoom(surface.backside_boundary_condition, spaces)
    # 例外
    else:
        print("境界条件が見つかりません。 name=", surface.boundary_type)

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
