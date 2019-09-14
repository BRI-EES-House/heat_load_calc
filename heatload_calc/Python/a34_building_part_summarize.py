import numpy as np
from Surface import Surface, GroupedSurface

"""
付録34．境界条件が同じ部位の集約
"""


# 部位の集約（同一境界条件の部位を集約する）
def get_grouped_surfaces(surfaces):

    # 部位番号とグループ番号の対応表 (-1は未割当)
    g_k = np.zeros(surfaces.Nsurf, dtype=np.int64) - 1

    # 部位のグループ化
    for k in range(surfaces.Nsurf):
        # 同じ境界条件の部位を探す
        gs_index = np.array([l for l in range(surfaces.Nsurf) if g_k[l] < 0 and compare_surfaces(surfaces, k, l)], dtype=np.int64)

        # 部位番号とグループ番号の対応表に新しいグループ番号を記述
        g_k[gs_index] = np.max(g_k) + 1

    # グループごとの集約処理
    gs = []
    for g_num in np.unique(g_k):
        gs.append(aggregate_surfaces(surfaces, g_k == g_num, g_num))

    return gs

# 境界条件が一致するかどうかを判定
def compare_surfaces(surfaces, a, b):
    temp = False
    if surfaces.boundary_type[a] == surfaces.boundary_type[b]:
        # 間仕切りの場合
        if surfaces.boundary_type[a] == "internal":
            # 隣室名が同じ壁体は集約対象
            temp = surfaces.next_room_type[a] == surfaces.next_room_type[b]
            # 室内側熱伝達率の比較
            temp = temp and abs(surfaces.hi_i_k_n[a] - surfaces.hi_i_k_n[b]) < 1.0E-5
            # 室外側総合熱伝達率の比較
            ###temp = temp and abs(surfaces.ho_i_k_n[a] - surfaces.ho_i_k_n[b]) < 1.0E-5
        # 外皮_一般部位の場合
        elif surfaces.boundary_type[a] == "external_general_part":
            # 日射の有無の比較
            temp = surfaces.is_sun_striked_outside[a] == surfaces.is_sun_striked_outside[b]
            # 温度差係数の比較
            temp = temp and abs(surfaces.a_i_k[a] - surfaces.a_i_k[b]) < 1.0E-5
            # 方位の比較
            temp = temp and surfaces.direction[a] == surfaces.direction[b]
            # 室内侵入日射吸収の有無の比較
            temp = temp and surfaces.is_solar_absorbed_inside[a] == surfaces.is_solar_absorbed_inside[b]
            # 屋外側放射率の比較
            temp = temp and abs(surfaces.eps_i_k[a] - surfaces.eps_i_k[b]) < 1.0E-5
            # 屋外側日射吸収率の比較
            temp = temp and abs(surfaces.as_i_k[a] - surfaces.as_i_k[b]) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surfaces.hi_i_k_n[a] - surfaces.hi_i_k_n[b]) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surfaces.ho_i_k_n[a] - surfaces.ho_i_k_n[b]) < 1.0E-5
        # 透明な開口部の場合
        elif surfaces.boundary_type[a] == "external_transparent_part":
            # 日射の有無の比較
            temp = surfaces.is_sun_striked_outside[a] == surfaces.is_sun_striked_outside[b]
            # 方位の比較
            temp = temp and surfaces.direction[a] == surfaces.direction[b]
            # 屋外側放射率の比較
            temp = temp and abs(surfaces.eps_i_k[a] - surfaces.eps_i_k[b]) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surfaces.hi_i_k_n[a] - surfaces.hi_i_k_n[b]) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surfaces.ho_i_k_n[a] - surfaces.ho_i_k_n[b]) < 1.0E-5
        # 不透明な開口部の場合
        elif surfaces.boundary_type[a] == "external_opaque_part":
            # 日射の有無の比較
            temp = surfaces.is_sun_striked_outside[a] == surfaces.is_sun_striked_outside[b]
            # 方位の比較
            temp = temp and surfaces.direction[a] == surfaces.direction[b]
            # 屋外側放射率の比較
            temp = temp and abs(surfaces.eps_i_k[a] - surfaces.eps_i_k[b]) < 1.0E-5
            # 屋外側日射吸収率の比較
            temp = temp and abs(surfaces.as_i_k[a] - surfaces.as_i_k[b]) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surfaces.hi_i_k_n[a] - surfaces.hi_i_k_n[b]) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surfaces.ho_i_k_n[a] - surfaces.ho_i_k_n[b]) < 1.0E-5
        # 地盤の場合
        elif surfaces.boundary_type[a] == "ground":
            # 室内側熱伝達率の比較
            temp = temp and abs(surfaces.hi[a] - surfaces.hi[b]) < 1.0E-5
        # else:
        #     print("境界の種類が不適です。 name=", self.name)
    
    # 室内側放射率
    #temp = temp and abs(surface_a.Ei - comp_surface.Ei) < 1.0E-5

    return(temp)

# 新しい室内表面の作成
def aggregate_surfaces(surfaces, f, group_number):
    gs = GroupedSurface()
    gs.group_number = group_number

    def first(arr):
        return np.array(arr)[f][0]

    # 境界条件名称
    gs.name = "summarize_building_part_" + str(group_number)

    # 1) 境界の種類
    gs.boundary_type = first(surfaces.boundary_type)

    # 2) 隣室タイプ
    gs.nextroomname = first(surfaces.nextroomname)

    if gs.boundary_type in ["external_general_part", "external_transparent_part", "external_opaque_part"]:
        # 3) 日射の有無
        gs.is_sun_striked_outside = first(surfaces.is_sun_striked_outside)

        # 4) 温度差係数
        gs.a_i_k = first(surfaces.a_i_k)

        # 5) 向き
        gs.direction = first(surfaces.direction)

        # 6) 地面反射率
        gs.RhoG_l = first(surfaces.RhoG_l)

        # 7) 方位角
        gs.Wa = first(surfaces.Wa)

        # 8) 傾斜角
        gs.Wb = first(surfaces.Wb)

        # 9) 太陽入射角の方向余弦計算パラメータ
        gs.cos_Theta_i_k_n = first(surfaces.cos_Theta_i_k_n)
        gs.Wz = first(surfaces.Wz)
        gs.WW= first(surfaces.WW)
        gs.Ws = first(surfaces.Ws)

        # 10) 傾斜面の天空に対する形態係数
        gs.PhiS_i_k= first(surfaces.PhiS_i_k)

        # 11) 傾斜面の地面に対する形態係数
        gs.PhiG_i_k = first(surfaces.PhiG_i_k)

    # 12) 室外側日射吸収率
    gs.as_i_k = first(surfaces.as_i_k)

    # 13) 室外側放射率
    gs.eps_i_k = first(surfaces.eps_i_k)

    # 14) 室内侵入日射吸収の有無
    # TODO: 仕様書とずれ
    gs.is_solar_absorbed_inside = first(surfaces.is_solar_absorbed_inside)

    # 15) 放射暖房発熱の有無
    # TODO: 仕様書とずれ

    # 16) 室内側熱伝達率
    gs.hi_i_k_n = first(surfaces.hi_i_k_n)

    # 17) 室内側放射率
    # TODO: 仕様書とずれ

    # 18) 室外側熱伝達率
    # TODO: 仕様書とずれ (internalは許容されるように仕様にはある
    gs.ho_i_k_n = first(surfaces.ho_i_k_n)

    # 19) 面積
    gs.A_i_k = np.sum(surfaces.A_i_k[f])

    # 20) 裏面境界温度
    gs.Teolist = first(surfaces.Teolist)
    gs.Teo = 15.0

    # 21) 前時刻の裏面境界温度
    gs.oldTsd_t = np.zeros(first(surfaces.Nroot))
    gs.oldTeo = 15.0  # 前時刻の室外側温度

    # 22) 前時刻の室内表面熱流
    gs.oldTsd_a = np.zeros(first(surfaces.Nroot))
    gs.oldqi = 0.0  # 前時刻の室内側表面熱流

    # 23) 根の数
    gs.Nroot = first(surfaces.Nroot)

    # 24) 公比
    gs.Row = first(surfaces.Row)

    # 25) 室内表面から室外側空気までの熱貫流率
    gs.Uso = sum(surfaces.A_i_k[f] * surfaces.Uso[f]) / gs.A_i_k
    gs.U = sum(surfaces.A_i_k[f] * surfaces.U[f]) / gs.A_i_k

    # 26) 吸熱応答係数の初項
    gs.RFA0 = sum(surfaces.A_i_k[f] * surfaces.RFA0[f]) / gs.A_i_k

    # 27) 貫流応答係数の初項
    gs.RFT0 = sum(surfaces.A_i_k[f] * surfaces.RFT0[f]) / gs.A_i_k

    # 28) 指数項別吸熱応答係数
    gs.RFT1 = np.sum(surfaces.A_i_k[f,np.newaxis]  * surfaces.RFT1[f,:], axis=0) / gs.A_i_k

    # 29) 指数項別貫流応答係数
    gs.RFA1 = np.sum(surfaces.A_i_k[f,np.newaxis] * surfaces.RFA1[f,:], axis=0) / gs.A_i_k

    return gs