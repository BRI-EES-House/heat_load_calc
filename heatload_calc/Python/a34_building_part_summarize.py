import numpy as np
from Surface import Surface, GroupedSurface

"""
付録34．境界条件が同じ部位の集約
"""


# 部位の集約（同一境界条件の部位を集約する）
def get_grouped_surfaces(surfaces):

    # 部位番号とグループ番号の対応表 (-1は未割当)
    g_k = np.zeros(len(surfaces), dtype=np.int64) - 1

    # 部位のグループ化
    for k, surface in enumerate(surfaces):
        # 同じ境界条件の部位を探す
        gs_index = np.array([l for l in range(len(surfaces)) if g_k[l] < 0 and compare_surfaces(surface, surfaces[l])], dtype=np.int64)

        # 部位番号とグループ番号の対応表に新しいグループ番号を記述
        g_k[gs_index] = np.max(g_k) + 1

    # グループごとの集約処理
    gs = []
    for g_num in np.unique(g_k):
        gs_x = [surfaces[x] for x in range(len(surfaces)) if g_k[x] == g_num]
        gs.append(aggregate_surfaces(gs_x, g_num))

    return gs

# 境界条件が一致するかどうかを判定
def compare_surfaces(surface_a, comp_surface):
    temp = False
    if surface_a.boundary_type == comp_surface.boundary_type:
        # 間仕切りの場合
        if surface_a.boundary_type == "internal":
            # 隣室名が同じ壁体は集約対象
            temp = surface_a.next_room_type == comp_surface.next_room_type
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi_i_k_n - comp_surface.hi_i_k_n) < 1.0E-5
            # 室外側総合熱伝達率の比較
            ###temp = temp and abs(surface_a.ho_i_k_n - comp_surface.ho_i_k_n) < 1.0E-5
        # 外皮_一般部位の場合
        elif surface_a.boundary_type == "external_general_part":
            # 日射の有無の比較
            temp = surface_a.is_sun_striked_outside == comp_surface.is_sun_striked_outside
            # 温度差係数の比較
            temp = temp and abs(surface_a.a_i_k - comp_surface.a_i_k) < 1.0E-5
            # 方位の比較
            temp = temp and surface_a.direction == comp_surface.direction
            # 室内侵入日射吸収の有無の比較
            temp = temp and surface_a.is_solar_absorbed_inside == comp_surface.is_solar_absorbed_inside
            # 屋外側放射率の比較
            temp = temp and abs(surface_a.eps_i_k - comp_surface.eps_i_k) < 1.0E-5
            # 屋外側日射吸収率の比較
            temp = temp and abs(surface_a.as_i_k - comp_surface.as_i_k) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi_i_k_n - comp_surface.hi_i_k_n) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho_i_k_n - comp_surface.ho_i_k_n) < 1.0E-5
        # 透明な開口部の場合
        elif surface_a.boundary_type == "external_transparent_part":
            # 日射の有無の比較
            temp = surface_a.is_sun_striked_outside == comp_surface.is_sun_striked_outside
            # 方位の比較
            temp = temp and surface_a.direction == comp_surface.direction
            # 屋外側放射率の比較
            temp = temp and abs(surface_a.eps_i_k - comp_surface.eps_i_k) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi_i_k_n - comp_surface.hi_i_k_n) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho_i_k_n - comp_surface.ho_i_k_n) < 1.0E-5
        # 不透明な開口部の場合
        elif surface_a.boundary_type == "external_opaque_part":
            # 日射の有無の比較
            temp = surface_a.is_sun_striked_outside == comp_surface.is_sun_striked_outside
            # 方位の比較
            temp = temp and surface_a.direction == comp_surface.direction
            # 屋外側放射率の比較
            temp = temp and abs(surface_a.eps_i_k - comp_surface.eps_i_k) < 1.0E-5
            # 屋外側日射吸収率の比較
            temp = temp and abs(surface_a.as_i_k - comp_surface.as_i_k) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi_i_k_n - comp_surface.hi_i_k_n) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho_i_k_n - comp_surface.ho_i_k_n) < 1.0E-5
        # 地盤の場合
        elif surface_a.boundary_type == "ground":
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi - comp_surface.hi) < 1.0E-5
        # else:
        #     print("境界の種類が不適です。 name=", self.name)
    
    # 室内側放射率
    #temp = temp and abs(surface_a.Ei - comp_surface.Ei) < 1.0E-5

    return(temp)

# 新しい室内表面の作成
def aggregate_surfaces(group_surfaces, group_number):
    gs = GroupedSurface()
    gs.group_number = group_number

    # 最初に見つかるgroup_numberの検索
    gs_0 = group_surfaces[0]

    # 境界条件名称
    gs.name = "summarize_building_part_" + str(group_number)

    # 1) 境界の種類
    gs.boundary_type = gs_0.boundary_type

    # 2) 隣室タイプ
    gs.nextroomname = gs_0.nextroomname

    if gs.boundary_type in ["external_general_part", "external_transparent_part", "external_opaque_part"]:
        # 3) 日射の有無
        gs.is_sun_striked_outside = gs_0.is_sun_striked_outside

        # 4) 温度差係数
        gs.a_i_k = gs_0.a_i_k

        # 5) 向き
        gs.direction = gs_0.direction

        # 6) 地面反射率
        gs.RhoG_l = gs_0.RhoG_l

        # 7) 方位角
        gs.Wa = gs_0.Wa

        # 8) 傾斜角
        gs.Wb = gs_0.Wb

        # 9) 太陽入射角の方向余弦計算パラメータ
        if hasattr(gs_0, 'cos_Theta_i_k_n'):
            gs.cos_Theta_i_k_n = gs_0.cos_Theta_i_k_n
        if hasattr(gs_0, 'Wz'):
            gs.Wz = gs_0.Wz
            gs.WW= gs_0.WW
            gs.Ws = gs_0.Ws

        # 10) 傾斜面の天空に対する形態係数
        if hasattr(gs_0, 'PhiS_i_k'):
            gs.PhiS_i_k= gs_0.PhiS_i_k

        # 11) 傾斜面の地面に対する形態係数
        if hasattr(gs_0, 'PhiG_i_k'):
            gs.PhiG_i_k = gs_0.PhiG_i_k

    # 12) 室外側日射吸収率
    gs.as_i_k = gs_0.as_i_k

    # 13) 室外側放射率
    gs.eps_i_k = gs_0.eps_i_k

    # 14) 室内侵入日射吸収の有無
    # TODO: 仕様書とずれ
    gs.is_solar_absorbed_inside = gs_0.is_solar_absorbed_inside

    # 15) 放射暖房発熱の有無
    # TODO: 仕様書とずれ

    # 16) 室内側熱伝達率
    gs.hi_i_k_n = gs_0.hi_i_k_n

    # 17) 室内側放射率
    # TODO: 仕様書とずれ

    # 18) 室外側熱伝達率
    # TODO: 仕様書とずれ (internalは許容されるように仕様にはある
    gs.ho_i_k_n = gs_0.ho_i_k_n

    # 19) 面積
    gs.A_i_k = sum([gs_x.A_i_k for gs_x in group_surfaces])

    # 20) 裏面境界温度
    gs.Teolist = gs_0.Teolist
    gs.Teo = 15.0

    # 21) 前時刻の裏面境界温度
    gs.oldTsd_t = np.zeros(gs_0.Nroot)
    gs.oldTeo = 15.0  # 前時刻の室外側温度

    # 22) 前時刻の室内表面熱流
    gs.oldTsd_a = np.zeros(gs_0.Nroot)
    gs.oldqi = 0.0  # 前時刻の室内側表面熱流

    # 23) 根の数
    gs.Nroot = gs_0.Nroot

    # 24) 公比
    gs.Row = gs_0.Row

    # 25) 室内表面から室外側空気までの熱貫流率
    gs.Uso = sum([gs_x.A_i_k * gs_x.Uso for gs_x in group_surfaces]) / gs.A_i_k
    gs.U = sum([gs_x.A_i_k * gs_x.U for gs_x in group_surfaces]) / gs.A_i_k

    # 26) 吸熱応答係数の初項
    gs.RFA0 = sum([gs_x.A_i_k * gs_x.RFA0 for gs_x in group_surfaces]) / gs.A_i_k

    # 27) 貫流応答係数の初項
    gs.RFT0 = sum([gs_x.A_i_k * gs_x.RFT0 for gs_x in group_surfaces]) / gs.A_i_k

    # 28) 指数項別吸熱応答係数
    gs.RFT1 = np.sum([gs_x.A_i_k * gs_x.RFT1[:gs.Nroot] for gs_x in group_surfaces], axis=0) / gs.A_i_k

    # 29) 指数項別貫流応答係数
    gs.RFA1 = np.sum([gs_x.A_i_k * gs_x.RFA1[:gs.Nroot] for gs_x in group_surfaces], axis=0) / gs.A_i_k

    return gs