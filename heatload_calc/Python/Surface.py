from Wall import Wall, Layer
from ResponseFactor import ResponseFactor
from transparent_opening import transparent_opening, get_QGTS, get_QGTD
from SolarPosision import defSolpos
from Gdata import Gdata
from Exsrf import Exsrf
from Sunbrk import SunbrkType
import datetime

# 室内部位に関連するクラス
class Surface:

    # 初期化
    def __init__(self, d = None, Gdata = None):
        if d != None and Gdata != None:
            self.is_sun_striked_outside = d['is_sun_striked_outside']
                                                            # True:外表面に日射が当たる
            # 境界条件タイプ
            self.boundary_type = d['boundary_type']

            # 境界条件クラスの初期化
            self.backside_boundary_condition = Exsrf()

            self.name = d['name']                           # 壁体名称

            # 外皮の場合
            if "external" in self.boundary_type:
                self.direction = None
                if self.is_sun_striked_outside:
                    self.direction = d['direction']
                # 隣室温度差係数
                self.temp_dif_coef = d['temp_dif_coef']
                # 境界条件の初期化
                self.backside_boundary_condition.external_init(self.direction, \
                    self.is_sun_striked_outside, self.temp_dif_coef)
            # 内壁の場合
            elif self.boundary_type == "internal":
                self.next_room_type = d['next_room_type']
                self.backside_boundary_condition.internal_init(self.next_room_type)
            # 土壌の場合
            elif self.boundary_type == "ground":
                self.backside_boundary_condition.ground_init()
            # 例外
            else:
                print("境界Typeが見つかりません。 name=", self.name, "boundary_type=", self.boundary_type)

            # 部位のタイプ
            self.is_solar_absorbed_inside = d['is_solar_absorbed_inside']      #床フラグ（透過日射の吸収部位）

            self.area = float(d['area'])                    # 面積
            self.a = 0.0                                    # 部位の面積比率（全面積に対する面積比）
            # 屋外に日射が当たる場合はひさしの情報を読み込む
            if self.is_sun_striked_outside:
                self.sunbrk = SunbrkType(d['solar_shading_part'])         # ひさし
            self.Fsdw = 0.0                                 # 影面積率の初期化
            self.flr = 0.0
            self.fot = 0.0  # 人体に対する形態係数の初期化
            self.is_ground = self.boundary_type == "ground"     # 壁体に土壌が含まれる場合True
            self.Ei = 0.9                                   # 室内側表面放射率

            # 室内表面熱伝達率の初期化
            self.hi = 0.0
            self.hic = 0.0
            self.hir = 0.0

            self.SolR = None  # 透過日射の室内部位表面吸収比率

            # 形態係数収録用リストの定義
            self.FF = []

            # 透過日射の室内部位表面吸収日射量の初期化
            self.RSsol = 0.0

            # 表面温度
            self.Ts = None

            # 直達日射量
            self.Id = 0.0

            # 天空日射量
            self.Isky = 0.0

            # 反射日射量
            self.Ir = 0.0

            # 全天日射量
            self.Iw = 0.0

            # 開口部透過日射量、吸収日射量の初期化
            # self.Qgt = 0.0

            # 相当外気温度の初期化
            self.Teo = 15.0
            self.oldTeo = 15.0

            self.Nroot = 0

            self.Qt = 0.0
            self.Qc = 0.0  # 対流成分
            self.Qr = 0.0  # 放射成分
            self.RS = 0.0  # 短波長熱取得成分
            self.Lr = 0.0  # 放射暖房成分

            self.oldTeo = 15.0  # 前時刻の室外側温度
            self.oldqi = 0.0  # 前時刻の室内側表面熱流
            self.Fmrt = 0.0     # 平均放射温度に対する当該表面温度の重み

            # 一般部位の初期化
            if self.boundary_type == "external_general_part" or self.boundary_type == "internal" or self.boundary_type == "ground":
                general_part_init(self, d, Gdata)
            # 透明部位の初期化
            elif self.boundary_type == "external_transparent_part":
                transparent_part_init(self, d)
            # 不透明な開口部の初期化
            elif self.boundary_type == "external_opaque_part":
                opaque_part_init(self, d)
            else:
                print("境界条件が見当たりません。 name=", self.name)

            # 部位のグループ化に関する変数
            # グループ番号
            self.group_number = -999
            # グループ化済み変数
            self.is_grouping = False

# 一般部位の初期化
def general_part_init(surface, d, Gdata):
    # 壁体情報,応答係数の取得
    part_key_name = 'general_part_spec'
    if surface.boundary_type == "ground":
        part_key_name = 'ground_spec'
    wall, rf = WalldataRead(surface.name, surface.is_sun_striked_outside, surface.boundary_type, d[part_key_name], Gdata.DTime, surface.is_ground)
    surface.Row = rf.Row  # 公比の取得
    surface.Nroot = rf.Nroot  # 根の数
    surface.RFT0 = rf.RFT0  # 貫流応答の初項
    surface.RFA0 = rf.RFA0  # 吸熱応答の初項
    surface.RFT1 = rf.RFT1  # 指数項別貫流応答の初項
    surface.RFA1 = rf.RFA1  # 指数項別吸熱応答の初項
    surface.oldTsd_a = []
    surface.oldTsd_t = []
    surface.oldTsd_a = [0.0 for j in range(surface.Nroot)]
    surface.oldTsd_t = [0.0 for j in range(surface.Nroot)]
    surface.hi = wall.hi  # 室内側表面総合熱伝達率
    surface.ho = wall.ho  # 室外側表面総合熱伝達率
    surface.Ei = wall.Ei   # 室内側表面放射率
    if surface.is_sun_striked_outside:
        surface.outside_solar_absorption = wall.Solas  # 室側側日射吸収率
        surface.Eo = wall.Eo  # 室外側表面放射率

# 透明部位の初期化
def transparent_part_init(surface, d):
    surface.transparent_opening = transparent_opening(surface.name, d['transparent_opening_part_spec'])
    surface.tau = surface.transparent_opening.T     # 日射透過率＝日射熱取得率
    surface.Uso = surface.transparent_opening.Uso   # 熱貫流率（表面熱伝達抵抗除く）
    surface.RFA0 = 1.0 / surface.Uso                  # 吸熱応答係数の初項
    surface.RFT0 = 1.0                             # 貫流応答係数の初項
    surface.hi = surface.transparent_opening.hi     # 室内側表面総合熱伝達率
    surface.ho = surface.transparent_opening.ho     # 室外側表面総合熱伝達率
    surface.U = 1.0 / (1.0 / surface.Uso + 1.0 / surface.hi)  # 熱貫流率（表面熱伝達抵抗含む）
    surface.Ei = surface.transparent_opening.Ei     # 室内側表面放射率
    if surface.is_sun_striked_outside:
        surface.Eo = surface.transparent_opening.Eo     # 室外側表面放射率

# 不透明開口部の初期化
def opaque_part_init(surface, d):
    surface.U = d['opaque_opening_part_spec']['u_value']     # 熱貫流率[W/(m2･K)]
    surface.ho = 1.0/d['opaque_opening_part_spec']['outside_heat_transfer_resistance']   # 室外側表面総合熱伝達率
    surface.Ei = 0.9                               # 室内側表面放射率
    surface.hi = 1.0/d['opaque_opening_part_spec']['inside_heat_transfer_resistance']    # 室内側表面総合熱伝達率
    surface.Uso = 1.0 / (1.0 / surface.U - 1.0 / surface.hi)
                                                # 熱貫流率（表面熱伝達抵抗除く）
    surface.RFA0 = 1.0 / surface.Uso                  # 吸熱応答係数の初項
    surface.RFT0 = 1.0                             # 貫流応答係数の初項
    if surface.is_sun_striked_outside:
        surface.outside_solar_absorption = d['opaque_opening_part_spec']['outside_solar_absorption']  # 室側側日射吸収率
        surface.Eo = d['opaque_opening_part_spec']['outside_emissivity']           # 室外側表面放射率

# 畳み込み積分
def convolution(surface):
    sumTsd = 0.0
    for i in range(surface.Nroot):
        surface.oldTsd_t[i] = surface.oldTeo * surface.RFT1[i] + surface.Row[i] * surface.oldTsd_t[i]
        surface.oldTsd_a[i] = surface.oldqi * surface.RFA1[i] + surface.Row[i] * surface.oldTsd_a[i]
        sumTsd += surface.oldTsd_t[i] + surface.oldTsd_a[i]

    return sumTsd

# 室内等価温度の計算
def calc_Tei(surface, Tr, Tsx, Lr, Beta):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """
    return Tr * surface.hic / surface.hi \
                    + Tsx * surface.hir / surface.hi \
                    + surface.RSsol / surface.hi \
                    + surface.flr * Lr * (1.0 - Beta) / surface.hi / surface.area

# 室内表面熱流の計算
def update_qi(surface, Tr: float, Tsx: float, Lr: float, Beta: float):
    """
    :param Tr: 室温
    :param Tsx: 形態係数加重平均表面温度
    :param Lr:
    :param Beta:
    :return:
    """
    # 対流成分
    surface.Qc = surface.hic * surface.area * (Tr - surface.Ts)

    # 放射成分
    surface.Qr = surface.hir * surface.area * (Tsx - surface.Ts)

    # 短波長熱取得成分
    surface.RS = surface.RSsol * surface.area

    # 放射暖房成分
    surface.Lr = surface.flr * Lr * (1.0 - Beta)

    # 表面熱流合計
    surface.Qt = surface.Qc + surface.Qr + surface.Lr + surface.RS
    # 前時刻熱流の保持
    surface.oldqi = surface.Qt / surface.area

# 透過日射の室内部位表面吸収日射量の初期化
def calc_RSsol(surface, TotalQgt: float):
    """
    :param TotalQgt: 透過日射熱取得
    """
    return TotalQgt * surface.SolR / surface.area

# 相当外気温度の計算
def calcTeo(surface, Ta, RN, oldTr, AnnualTave, spaces):
    # 前時刻の相当外気温度を控える
    surface.oldTeo = surface.Teo

    # 日射の当たる一般部位または不透明部位の場合
    if surface.boundary_type == "external_general_part" or surface.boundary_type == "external_opaque_part":
        # 室外側に日射が当たる場合
        if surface.is_sun_striked_outside:
            surface.Teo = surface.backside_boundary_condition.get_Te(surface.outside_solar_absorption, surface.ho, surface.Eo, Ta, RN)
        # 室外側に日射が当たらない場合
        else:
            surface.Teo = Ta * surface.backside_boundary_condition.R + oldTr * (1.0 - surface.backside_boundary_condition.R)
    # 窓の場合
    elif surface.boundary_type == "external_transparent_part":
        surface.Teo = - surface.Eo * surface.backside_boundary_condition.Fs * RN / surface.ho + Ta
    # 土壌の場合
    elif surface.boundary_type == "ground":
        surface.Teo = AnnualTave
    # 内壁の場合（前時刻の室温）
    elif surface.boundary_type == "internal":
        surface.Teo = surface.backside_boundary_condition.get_oldNextRoom(spaces)
    # 例外
    else:
        print("境界条件が見つかりません。 name=", surface.boundary_type)

# 透過日射量[W]、吸収日射量[W]の計算
def calc_Qgt(surface):
    # 直達成分
    Qgtd = get_QGTD(surface.transparent_opening, surface.Id, surface.backside_boundary_condition.CosT, surface.Fsdw) * surface.area

    # 拡散成分
    Qgts = get_QGTS(surface.transparent_opening, surface.Isky, surface.Ir) * surface.area

    # 透過日射量の計算
    return Qgtd + Qgts

# 日影面積率の計算
def calc_Fsdw(suraface, Solpos: defSolpos):
    return suraface.sunbrk.get_Fsdw(Solpos, suraface.backside_boundary_condition.Wa)

# 傾斜面日射量を計算する
def calc_slope_sol(suraface, Solpos, Idn, Isky):
    if 'external' in suraface.backside_boundary_condition.Type and suraface.is_sun_striked_outside:
        # 傾斜面日射量を計算
        suraface.backside_boundary_condition.update_slop_sol(Solpos, Idn, Isky)
        # 直達日射量
        Id = suraface.backside_boundary_condition.Id

        # 天空日射量
        Isky = suraface.backside_boundary_condition.Is

        # 反射日射量
        Ir = suraface.backside_boundary_condition.Ir

        # 全天日射量
        Iw = Id + Isky + Ir

        return Id, Isky, Ir, Iw

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
            temp = temp and abs(surface_a.Eo - comp_surface.Eo) < 1.0E-5
            # 屋外側日射吸収率の比較
            temp = temp and abs(surface_a.outside_solar_absorption - comp_surface.outside_solar_absorption) < 1.0E-5
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
            temp = temp and abs(surface_a.Eo - comp_surface.Eo) < 1.0E-5
            # 室内側熱伝達率の比較
            temp = temp and abs(surface_a.hi - comp_surface.hi) < 1.0E-5
            # 室外側総合熱伝達率の比較
            temp = temp and abs(surface_a.ho - comp_surface.ho) < 1.0E-5
        # 不透明な開口部の場合
        elif surface_a.boundary_type == "external_transparent_part":
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

# 壁体構成データの読み込みと応答係数の作成
def WalldataRead(Name, is_solar_absorbed_inside, boundary_type, 
        d, DTime, is_ground):
    # 時間間隔(s)
    dblDTime = DTime

    # 壁体構成部材の情報を保持するクラスをインスタンス化
    layers = [
        Layer(
            name=d_layers['name'],
            thermal_resistance=d_layers['thermal_resistance'],
            thermal_capacity=d_layers['thermal_capacity']
        )
        for d_layers in d['layers']
    ]
    #室外側総合熱伝達率の追加（土壌は除く）
    if not is_ground:
        layers.append(Layer( \
            name="outside_heat_transfer_resistance", \
                thermal_resistance=d['outside_heat_transfer_resistance'], \
                    thermal_capacity=0.0))
    # 土壌の場合は土壌3mを追加
    # 土壌の熱伝導率λ=1.0W/mK、容積比熱cp=3300.0kJ/m3K
    else:
        layers.append(Layer( \
            name="soil", \
                thermal_resistance=3.0 / 1.0, \
                    thermal_capacity=3300.0 * 3.0))

    outside_emissivity = 0.0
    if boundary_type == "external_general_part":
        outside_emissivity = d['outside_emissivity']

    outside_solar_absorption = 0.0
    if is_solar_absorbed_inside:
        outside_solar_absorption = d['outside_solar_absorption']
    
    # 壁体情報を保持するクラスをインスタンス化
    outside_heat_transfer_coef = 0.0
    if boundary_type == "external_general_part":
        outside_heat_transfer_coef = 1.0 / d['outside_heat_transfer_resistance']
    wall = Wall(
        is_ground=is_ground,
        outside_emissivity=outside_emissivity,
        outside_solar_absorption=outside_solar_absorption,
        inside_heat_transfer_coef=1.0/d['inside_heat_transfer_resistance'],
        outside_heat_transfer_coef=outside_heat_transfer_coef,
        Layers=layers
    )
    walltype = 'wall'
    if is_ground:
        walltype = 'soil'
    # 応答係数を保持するクラスをインスタンス化
    rf = ResponseFactor(
        WallType=walltype,
        DTime=dblDTime,
        NcalTime=50,
        Wall=wall
    )

    return wall, rf

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

    # 床フラグ
    summarize_surface.flr = first_found_surface.flr

    # 室内側表面熱伝達率
    summarize_surface.hi = first_found_surface.hi
    # 室内側放射率
    summarize_surface.Ei = first_found_surface.Ei

    # 室外側日射有無フラグ
    summarize_surface.is_sun_striked_outside = first_found_surface.is_sun_striked_outside
    if summarize_surface.is_sun_striked_outside:
        # 日射吸収率
        if first_found_surface.boundary_type == "external_opaque_part" or first_found_surface.boundary_type == "external_general_part" :
            summarize_surface.outside_solar_absorption = first_found_surface.outside_solar_absorption
        # 室外側放射率
        summarize_surface.Eo = first_found_surface.Eo

    # 裏面境界温度のコピー
    summarize_surface.Teo = first_found_surface.Teo
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
            area.append(surface.area)
    summarize_surface.area = sum(area)

    # 過去の項別応答の履歴配列のメモリ確保
    summarize_surface.Nroot = first_found_surface.Nroot
    if first_found_surface.Nroot > 0:
        summarize_surface.oldTsd_a = [0.0 for j in range(summarize_surface.Nroot)]
        summarize_surface.oldTsd_t = [0.0 for j in range(summarize_surface.Nroot)]
        summarize_surface.Row = first_found_surface.Row
        summarize_surface.RFT1 = [0.0 for j in range(summarize_surface.Nroot)]
        summarize_surface.RFA1 = [0.0 for j in range(summarize_surface.Nroot)]

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
            summarize_surface.RFA0 += area[i] * surface.RFA0 / summarize_surface.area
            # 貫流応答係数の初項
            summarize_surface.RFT0 += area[i] * surface.RFT0 / summarize_surface.area
            # 熱貫流率
            if first_found_surface.boundary_type == "external_transparent_part" \
                or first_found_surface.boundary_type == "external_opaque_part":
                summarize_surface.Uso += area[i] * surface.Uso / summarize_surface.area
                summarize_surface.U += area[i] * surface.U / summarize_surface.area
            # 指数項別応答係数
            if summarize_surface.Nroot > 0:
                for j in range(summarize_surface.Nroot):
                    summarize_surface.RFT1[j] += area[i] * surface.RFT1[j] / summarize_surface.area
                    summarize_surface.RFA1[j] += area[i] * surface.RFA1[j] / summarize_surface.area
            i += 1

    return summarize_surface