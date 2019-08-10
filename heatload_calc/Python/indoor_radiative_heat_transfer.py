import math

# 微小体に対する部位の形態係数の計算
def calc_form_factor_of_microbodies(space_name, surfaces):
    # 面積比の計算
    # 面積比の最大値も同時に計算（ニュートン法の初期値計算用）
    max_a = 0.0
    Atotal = 0.0
    for surface in surfaces:
        Atotal += surface.area
    for surface in surfaces:
        surface.a = surface.area / Atotal
        max_a = max(max_a, surface.a)
    
    # 室のパラメータの計算（ニュートン法）
    # 初期値を設定
    fbd = max_a * 4.0 + 1.0e-5
    # 収束判定
    isConverge = False
    for i in range(50):
        L = -1.0
        Ld = 0.0
        for surface in surfaces:
            temp = math.sqrt(1.0 - 4.0 * surface.a / fbd)
            L += 0.5 * (1.0 - temp)
            Ld += surface.a / ((fbd ** 2.0) * temp)
            # print(surface.name, 'a=', surface.a, 'L=', 0.5 * (1.0 - math.sqrt(temp)), 'Ld=', -0.25 * (1.0 + 4.0 * surface.a / fbd ** (2.0)) / temp)
        fb = fbd + L / Ld
        # print(i, 'fb=', fb, 'fbd=', fbd)
        # 収束判定
        if abs(fb - fbd) < 1.e-4:
            isConverge = True
            break
        fbd = fb
    
    # 収束しないときには警告を表示
    if not isConverge:
        print(space_name, '形態係数パラメータが収束しませんでした。')
    # print('合計表面積=', self.Atotal)
    # 形態係数の計算（永田の方式）
    # 総和のチェック
    TotalFF = 0.0
    for surface in surfaces:
        FF = 0.5 * (1.0 - math.sqrt(1.0 - 4.0 * surface.a / fb))
        TotalFF += FF
        # 形態係数の設定（面の微小球に対する形態係数）
        surface.FF = FF
    
    if abs(TotalFF - 1.0) > 1.0e-3:
        print('形態係数の合計値が不正 name=', space_name, 'TotalFF=', TotalFF)

# 平均放射温度計算時の各部位表面温度の重み計算
def calc_mrt_weight(surfaces):
    # 各部位表面温度の重み=面積×放射熱伝達率の比率
    total_area_hir = 0.0
    for surface in surfaces:
        total_area_hir += surface.area * surface.hir
    
    for surface in surfaces:
        surface.Fmrt = surface.area * surface.hir / total_area_hir

# 透過日射の吸収比率を設定する（家具の吸収比率を返す）
def calc_absorption_ratio_of_transmitted_solar_radiation(room_name, tolal_floor_area, furniture_ratio, surfaces):
    # 部位の日射吸収比率の計算

    # 透過日射の室内部位表面吸収比率の計算
    # 50%を床、50%を家具に吸収させる
    # 床が複数の部位の場合は面積比で案分する
    FsolFlr = 0.5
    # 家具の吸収比率で初期化
    TotalR = furniture_ratio
    modify_furniture_ratio = furniture_ratio

    for surface in surfaces:
        SolR = 0.0
        # 床の室内部位表面吸収比率の設定
        if surface.is_solar_absorbed_inside == True:
            SolR = FsolFlr * surface.area / tolal_floor_area
        surface.SolR = SolR
        # 室内部位表面吸収比率の合計値（チェック用）
        TotalR += SolR
    # 日射吸収率の合計値のチェック
    if abs(TotalR - 1.0) > 0.00001:
        print(room_name, '日射吸収比率合計値エラー', TotalR)
        print("残りは家具に吸収させます")
        # 修正家具の日射吸収比率の計算
        modify_furniture_ratio = furniture_ratio + max(1.0 - TotalR, 0)
    
    return modify_furniture_ratio

# 部位の人体に対する形態係数の計算
def calc_form_factor_for_human_body(space):
    # 部位の人体に対する形態係数の計算
    total_Aex_floor = 0.0
    total_A_floor = 0.0
    # 設定合計値もチェック
    total_Fot = 0.0
    # 床と床以外の合計面積を計算
    for surface in space.input_surfaces:
        # 下向き部位（床）
        if surface.is_solar_absorbed_inside:
            total_A_floor += surface.area
        # 床以外
        else:
            total_Aex_floor += surface.area
    
    # 上向き、下向き、垂直部位の合計面積をチェックし人体に対する形態係数の割合を基準化
    fot_floor = 0.45
    fot_exfloor = 1.0 - fot_floor

    # 人体に対する部位の形態係数の計算
    for surface in space.input_surfaces:
        # 下向き部位（床）
        if surface.is_solar_absorbed_inside:
            surface.fot = surface.area / total_A_floor * fot_floor
        # 床以外
        else:
            surface.fot = surface.area / total_Aex_floor * fot_exfloor
        total_Fot += surface.fot
        # print(surface.name, surface.fot)

    if abs(total_Fot - 1.0) > 0.001:
        print(space.name, 'total_Fot=', total_Fot)

# 透過日射の家具、室内部位表面発熱量への分配
def distribution_transmitted_solar_radiation(space, Qgt):
    # RSsol:透過日射の内、室内部位表面での吸収量[W/m2]
    for surface in space.input_surfaces:
        surface.RSsol = Qgt * surface.SolR / surface.area
    # 家具の吸収日射量[W]
    space.Qsolfun = Qgt * space.rsolfun