import numpy as np
from Surface import Surface, GroupedSurface

"""
付録34．境界条件が同じ部位の集約
"""


# 部位の集約（同一境界条件の部位を集約する）
def get_grouped_surfaces(surfaces):

    # 部位番号とグループ番号の対応表 (-1は未割当)
    g_k = np.zeros(surfaces.N_surf_i, dtype=np.int64) - 1

    # 部位のグループ化
    for k in range(surfaces.N_surf_i):
        # 同じ境界条件の部位を探す
        gs_index = np.array([l for l in range(surfaces.N_surf_i) if g_k[l] < 0 and compare_surfaces(surfaces, k, l)], dtype=np.int64)

        # 部位番号とグループ番号の対応表に新しいグループ番号を記述
        g_k[gs_index] = np.max(g_k) + 1

    # グループごとの集約処理
    surfG_i = aggregate_surfaces(surfaces, g_k)

    return surfG_i

# 境界条件が一致するかどうかを判定
def compare_surfaces(surfaces, a, b):
    temp = False
    if surfaces.boundary_type[a] == surfaces.boundary_type[b]:
        # 間仕切りの場合
        if surfaces.boundary_type[a] == "internal":
            # 隣室名が同じ壁体は集約対象
            temp = surfaces.Rnext_i_k[a] == surfaces.Rnext_i_k[b]
            # 室内側熱伝達率の比較
            temp = temp and abs(surfaces.hi_i_k_n[a] - surfaces.hi_i_k_n[b]) < 1.0E-5
            # 室外側総合熱伝達率の比較
            ###temp = temp and abs(surfaces.ho_i_g_n[a] - surfaces.ho_i_g_n[b]) < 1.0E-5
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
def aggregate_surfaces(surfaces, g_k):

    gs = GroupedSurface()

    gs.group_number = np.unique(g_k)

    gs.NsurfG_i = len(gs.group_number)

    # 境界条件名称
    gs.name = ["summarize_building_part_" + str(x) for x in gs.group_number]

    # 先頭インデックス一覧
    idx0 = np.array([np.where(g_k == k)[0][0] for k in gs.group_number], dtype=np.int)

    # グループBooleanIndexMap
    map_g = np.array([[g_k == k][0] for k in gs.group_number], dtype=np.int)

    def first(arr):
        return np.array(arr)[idx0]

    # 1) 境界の種類
    gs.boundary_type = first(surfaces.boundary_type)

    # 2) 隣室タイプ
    gs.Rnext_i_g = first(surfaces.Rnext_i_k)

    gs.is_sun_striked_outside = np.zeros(gs.NsurfG_i, dtype=np.bool)
    gs.a_i_g = np.zeros(gs.NsurfG_i)
    gs.direction_i_g = np.zeros(gs.NsurfG_i, dtype=np.object)
    gs.RhoG_l = np.zeros(gs.NsurfG_i)
    gs.w_alpha_i_g = np.zeros(gs.NsurfG_i)
    gs.w_beta_i_g = np.zeros(gs.NsurfG_i)
    gs.cos_Theta_i_g_n = np.zeros((gs.NsurfG_i, 24 * 365 * 4))
    gs.Wz_i_k = np.zeros(gs.NsurfG_i)
    gs.Ww_i_k = np.zeros(gs.NsurfG_i)
    gs.Ws_i_k = np.zeros(gs.NsurfG_i)
    gs.PhiS_i_k = np.zeros(gs.NsurfG_i)
    gs.PhiG_i_k = np.zeros(gs.NsurfG_i)

    for g in np.unique(g_k):

        def firstel(arr):
            return np.array(arr)[g_k == g][0]

        if gs.boundary_type[g] in ["external_general_part", "external_transparent_part", "external_opaque_part"]:
            # 3) 日射の有無
            gs.is_sun_striked_outside[g] = firstel(surfaces.is_sun_striked_outside)

            # 4) 温度差係数
            gs.a_i_g[g] = firstel(surfaces.a_i_k)

            # 5) 向き
            gs.direction_i_g[g] = firstel(surfaces.direction)

            # 6) 地面反射率
            gs.RhoG_l[g] = firstel(surfaces.RhoG_l)

            # 7) 方位角
            gs.w_alpha_i_g[g] = firstel(surfaces.w_alpha_i_k)

            # 8) 傾斜角
            gs.w_beta_i_g[g] = firstel(surfaces.w_beta_i_k)

            # 9) 太陽入射角の方向余弦計算パラメータ
            gs.cos_Theta_i_g_n[g] = firstel(surfaces.cos_Theta_i_k_n)
            gs.Wz_i_k[g] = firstel(surfaces.Wz_i_k)
            gs.Ww_i_k[g] = firstel(surfaces.Ww_i_k)
            gs.Ws_i_k[g] = firstel(surfaces.Ws_i_k)

            # 10) 傾斜面の天空に対する形態係数
            gs.PhiS_i_k[g] = firstel(surfaces.PhiS_i_k)

            # 11) 傾斜面の地面に対する形態係数
            gs.PhiG_i_k[g] = firstel(surfaces.PhiG_i_k)

    # 12) 室外側日射吸収率
    gs.as_i_g = first(surfaces.as_i_k)

    # 13) 室外側放射率
    gs.eps_i_g = first(surfaces.eps_i_k)

    # 14) 室内侵入日射吸収の有無
    # TODO: 仕様書とずれ
    gs.is_solar_absorbed_inside = first(surfaces.is_solar_absorbed_inside)

    # 15) 放射暖房発熱の有無
    # TODO: 仕様書とずれ

    # 16) 室内側熱伝達率
    gs.hi_i_g_n = first(surfaces.hi_i_k_n)

    # 17) 室内側放射率
    # TODO: 仕様書とずれ

    # 18) 室外側熱伝達率
    # TODO: 仕様書とずれ (internalは許容されるように仕様にはある
    gs.ho_i_g_n = first(surfaces.ho_i_k_n)

    # 19) 面積
    gs.A_i_g = np.sum(surfaces.A_i_k * map_g, axis=1)

    # 20) 裏面境界温度
    gs.Teolist = first(surfaces.Teolist)

    # 21) 前時刻の裏面境界温度
    gs.oldTsd_t = np.zeros((gs.NsurfG_i, 12))

    # 22) 前時刻の室内表面熱流
    gs.oldTsd_a = np.zeros((gs.NsurfG_i, 12))
    gs.oldqi = np.zeros(gs.NsurfG_i)  # 前時刻の室内側表面熱流

    # 23) 根の数
    gs.Nroot = first(surfaces.Nroot)

    # 24) 公比
    gs.Row = first(surfaces.Row)

    # 25) 室内表面から室外側空気までの熱貫流率
    gs.Uso_i_g = np.sum(surfaces.A_i_k * surfaces.Uso * map_g, axis=1) / gs.A_i_g
    gs.U_i_g = np.sum(surfaces.A_i_k * surfaces.U * map_g, axis=1) / gs.A_i_g

    # 26) 吸熱応答係数の初項
    gs.RFA0 = np.sum(surfaces.A_i_k * surfaces.RFA0 * map_g, axis=1) / gs.A_i_g

    # 27) 貫流応答係数の初項
    gs.RFT0 = np.sum(surfaces.A_i_k * surfaces.RFT0 * map_g, axis=1) / gs.A_i_g

    gs.RFT1 = np.zeros((gs.NsurfG_i, 12))
    gs.RFA1 = np.zeros((gs.NsurfG_i, 12))
    for g in np.unique(g_k):

        f = g_k == g

        # 28) 指数項別吸熱応答係数
        gs.RFT1[g] = np.sum(surfaces.A_i_k[f,np.newaxis] * surfaces.RFT1[f,:], axis=0) / gs.A_i_g[g]

        # 29) 指数項別貫流応答係数
        gs.RFA1[g] = np.sum(surfaces.A_i_k[f,np.newaxis] * surfaces.RFA1[f,:], axis=0) / gs.A_i_g[g]

    return gs