import numpy as np
from Surface import Surface

"""
付録34．境界条件が同じ部位の集約
"""

# 部位の集約（同一境界条件の部位を集約する）
def summarize_building_part(surfaces):
    # 部位のグループ化
    group_number = 0
    for surface in surfaces:
        # 最初の部位は最も若いグループ番号にする
        if not surface.is_grouping:
            # グループ化済みにする
            surface.is_grouping = True
            surface.group_number = group_number

            # 同じ境界条件の部位を探す
            for comp_surface in surfaces:
                # 境界条件が同じかどうかチェックする
                # グループ化していない部位だけを対象とする
                if not comp_surface.is_grouping:
                    if boundary_comp(surface, comp_surface):
                        comp_surface.is_grouping = True
                        comp_surface.group_number = group_number
            # グループ番号を増やす
            group_number += 1
    
    # print("集約前")
    # for surface in surfaces:
        # print('name=', surface.name, 'A_i_k=', surface.A_i_k, 'group=', surface.group_number)

    summarize_surfaces = []
    for i in range(group_number):
        summarize_surfaces.append(create_surface(surfaces, i))

    # for surface in summarize_surfaces:
    #     print(surface.boundary_type, surface.name, surface.group_number)
    return summarize_surfaces

# 境界条件が一致するかどうかを判定
def boundary_comp(surface_a, comp_surface):
    temp = False
    if surface_a.boundary_type == comp_surface.boundary_type:
        # 間仕切りの場合
        if surface_a.boundary_type == "internal":
            # 隣室名が同じ壁体は集約対象
            temp = surface_a.next_room_type == comp_surface.next_room_type
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi - comp_surface.hi) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho - comp_surface.ho) < 1.0E-5
        # 外皮_一般部位の場合
        elif surface_a.boundary_type == "external_general_part":
            # 日射の有無の比較
            temp = surface_a.is_sun_striked_outside == comp_surface.is_sun_striked_outside
            # 温度差係数の比較
            temp = temp and abs(surface_a.temp_dif_coef - comp_surface.temp_dif_coef) < 1.0E-5
            # 方位の比較
            temp = temp and surface_a.direction == comp_surface.direction
            # 室内侵入日射吸収の有無の比較
            temp = temp and surface_a.is_solar_absorbed_inside == comp_surface.is_solar_absorbed_inside
            # 屋外側放射率の比較
            temp = temp and abs(surface_a.eps_i_k - comp_surface.eps_i_k) < 1.0E-5
            # 屋外側日射吸収率の比較
            temp = temp and abs(surface_a.as_i_k - comp_surface.as_i_k) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi - comp_surface.hi) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho - comp_surface.ho) < 1.0E-5
        # 透明な開口部の場合
        elif surface_a.boundary_type == "external_transparent_part":
            # 日射の有無の比較
            temp = surface_a.is_sun_striked_outside == comp_surface.is_sun_striked_outside
            # 方位の比較
            temp = temp and surface_a.direction == comp_surface.direction
            # 屋外側放射率の比較
            temp = temp and abs(surface_a.eps_i_k - comp_surface.eps_i_k) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi - comp_surface.hi) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho - comp_surface.ho) < 1.0E-5
        # 不透明な開口部の場合
        elif surface_a.boundary_type == "external_opaque_part":
            # 日射の有無の比較
            temp = surface_a.is_sun_striked_outside == comp_surface.is_sun_striked_outside
            # 方位の比較
            temp = temp and surface_a.direction == comp_surface.direction
            # 屋外側放射率の比較
            temp = temp and abs(surface_a.Eo - comp_surface.Eo) < 1.0E-5
            # 屋外側日射吸収率の比較
            temp = temp and abs(surface_a.outside_solar_absorption - comp_surface.outside_solar_absorption) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi - comp_surface.hi) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho - comp_surface.ho) < 1.0E-5
        # 地盤の場合
        elif surface_a.boundary_type == "ground":
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi - comp_surface.hi) < 1.0E-5
        # else:
        #     print("境界の種類が不適です。 name=", self.name)
    
    # 室内側放射率
    temp = temp and abs(surface_a.Ei - comp_surface.Ei) < 1.0E-5

    return(temp)

# 新しい室内表面の作成
def create_surface(surfaces, group_number):
    summarize_surface = Surface()
    summarize_surface.group_number = group_number

    # 最初に見つかるgroup_numberの検索
    for surface in surfaces:
        if surface.group_number == group_number:
            first_found_surface = surface
            break
    # 境界条件タイプのコピー
    summarize_surface.boundary_type = first_found_surface.boundary_type
    # 境界条件名称
    summarize_surface.name = "summarize_building_part_" + str(group_number)
    # 裏面境界条件
    summarize_surface.backside_boundary_condition = first_found_surface.backside_boundary_condition
    # 室内透過日射吸収フラグ
    summarize_surface.is_solar_absorbed_inside = first_found_surface.is_solar_absorbed_inside

    # 床フラグ あとで計算するから不要
    #summarize_surface.flr = first_found_surface.flr

    # 室内側表面熱伝達率
    summarize_surface.hi = first_found_surface.hi
    # 室内側放射率
    summarize_surface.Ei = first_found_surface.Ei

    # 室外側日射有無フラグ
    summarize_surface.is_sun_striked_outside = first_found_surface.is_sun_striked_outside
    if summarize_surface.is_sun_striked_outside:
        # 日射吸収率
        if first_found_surface.boundary_type == "external_opaque_part" or first_found_surface.boundary_type == "external_general_part" :
            summarize_surface.as_i_k = first_found_surface.as_i_k
        # 室外側放射率
        summarize_surface.eps_i_k = first_found_surface.eps_i_k

    # 裏面境界温度のコピー
    summarize_surface.Teo = first_found_surface.Teo
    summarize_surface.is_Teo_list = first_found_surface.is_Teo_list
    if summarize_surface.is_Teo_list:
        summarize_surface.Teolist = first_found_surface.Teolist
    # 前時刻の裏面境界温度
    summarize_surface.oldTeo = first_found_surface.oldTeo
    # 前時刻の室内表面熱流
    summarize_surface.oldqi = first_found_surface.oldqi

    # 室外側総合熱伝達率のコピー
    if first_found_surface.boundary_type != "ground":
        summarize_surface.ho = first_found_surface.ho

    # 面積を合計
    area = []
    for surface in surfaces:
        if surface.group_number == group_number:
            area.append(surface.A_i_k)
    summarize_surface.A_i_k = sum(area)

    # 過去の項別応答の履歴配列のメモリ確保
    summarize_surface.Nroot = first_found_surface.Nroot
    if first_found_surface.Nroot > 0:
        summarize_surface.oldTsd_a = np.zeros(summarize_surface.Nroot)
        summarize_surface.oldTsd_t = np.zeros(summarize_surface.Nroot)
        summarize_surface.Row = first_found_surface.Row
        summarize_surface.RFT1 = np.zeros(summarize_surface.Nroot)
        summarize_surface.RFA1 = np.zeros(summarize_surface.Nroot)
    else:
        summarize_surface.oldTsd_a = np.zeros(0)
        summarize_surface.oldTsd_t = np.zeros(0)
        summarize_surface.Row = 0.0
        summarize_surface.RFT1 = np.zeros(0)
        summarize_surface.RFA1 = np.zeros(0)

    # 伝熱計算のパラメータの面積荷重平均計算
    i = 0
    summarize_surface.RFA0 = 0.0
    summarize_surface.RFT0 = 0.0
    if first_found_surface.boundary_type == "external_transparent_part" \
        or first_found_surface.boundary_type == "external_opaque_part":
        summarize_surface.Uso = 0.0
        summarize_surface.U = 0.0
    for surface in surfaces:
        if surface.group_number == group_number:
            # 吸熱応答係数の初項
            summarize_surface.RFA0 += area[i] * surface.RFA0 / summarize_surface.A_i_k
            # 貫流応答係数の初項
            summarize_surface.RFT0 += area[i] * surface.RFT0 / summarize_surface.A_i_k
            # 熱貫流率
            if first_found_surface.boundary_type == "external_transparent_part" \
                or first_found_surface.boundary_type == "external_opaque_part":
                summarize_surface.Uso += area[i] * surface.Uso / summarize_surface.A_i_k
                summarize_surface.U += area[i] * surface.U / summarize_surface.A_i_k
            # 指数項別応答係数
            if summarize_surface.Nroot > 0:
                for j in range(summarize_surface.Nroot):
                    summarize_surface.RFT1[j] += area[i] * surface.RFT1[j] / summarize_surface.A_i_k
                    summarize_surface.RFA1[j] += area[i] * surface.RFA1[j] / summarize_surface.A_i_k
            i += 1



    return summarize_surface