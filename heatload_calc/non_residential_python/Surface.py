from Wall import Wall, Layer
from ResponseFactor import ResponseFactor
from transparent_opening import transparent_opening
from SolarPosision import defSolpos
from Gdata import Gdata
from Exsrf import Exsrf
from Sunbrk import SunbrkType

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
            self.__objExsrf = Exsrf()

            self.name = d['name']                           # 壁体名称

            # 外皮の場合
            if "external" in self.boundary_type:
                self.__direction = None
                if self.is_sun_striked_outside:
                    self.__direction = d['direction']
                # 隣室温度差係数
                self.__temp_dif_coef = d['temp_dif_coef']
                # 境界条件の初期化
                self.__objExsrf.external_init(self.__direction, \
                    self.is_sun_striked_outside, self.__temp_dif_coef)
            # 内壁の場合
            elif self.boundary_type == "internal":
                self.next_room_type = d['next_room_type']
                self.__objExsrf.internal_init(self.next_room_type)
            # 土壌の場合
            elif self.boundary_type == "ground":
                self.__objExsrf.ground_init()
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
            self.__is_ground = self.boundary_type == "ground"     # 壁体に土壌が含まれる場合True
            self.Ei = 0.9                                   # 室内側表面放射率
            self.Eo = 0.9
            self.outside_solar_absorption = 0.8

            # 室内表面熱伝達率の初期化
            self.hi = 0.0
            self.hic = 0.0
            self.hir = 0.0

            self.SolR = None  # 透過日射の室内部位表面吸収比率

            # 形態係数収録用リストの定義
            self.__FF = []

            # 透過日射の室内部位表面吸収日射量の初期化
            self.RSsol = 0.0

            # 表面温度
            self.Ts = None

            # 直達日射量
            self.__Id = 0.0

            # 天空日射量
            self.__Isky = 0.0

            # 反射日射量
            self.__Ir = 0.0

            # 全天日射量
            self.__Iw = 0.0

            # 開口部透過日射量、吸収日射量の初期化
            self.Qgt = 0.0
            self.Qga = 0.0

            # 相当外気温度の初期化
            self.Teo = 15.0
            self.oldTeo = 15.0

            self.__Nroot = 0

            self.Qt = 0.0
            self.Qc = 0.0  # 対流成分
            self.Qr = 0.0  # 放射成分
            self.RS = 0.0  # 短波長熱取得成分
            self.__Lr = 0.0  # 放射暖房成分

            self.oldTeo = 15.0  # 前時刻の室外側温度
            self.oldqi = 0.0  # 前時刻の室内側表面熱流
            self.Fmrt = 0.0     # 平均放射温度に対する当該表面温度の重み

            # 一般部位の初期化
            if self.boundary_type == "external_general_part" or self.boundary_type == "internal" or self.boundary_type == "ground":
                # 壁体情報,応答係数の取得
                part_key_name = 'general_part_spec'
                if self.boundary_type == "ground":
                    part_key_name = 'ground_spec'
                wall, rf = WalldataRead(self.name, self.is_sun_striked_outside, self.boundary_type, d[part_key_name], Gdata.DTime, self.__is_ground)
                self.__Row = rf.Row  # 公比の取得
                self.__Nroot = rf.Nroot  # 根の数
                self.RFT0 = rf.RFT0  # 貫流応答の初項
                self.RFA0 = rf.RFA0  # 吸熱応答の初項
                self.RFT1 = rf.RFT1  # 指数項別貫流応答の初項
                self.RFA1 = rf.RFA1  # 指数項別吸熱応答の初項
                self.__oldTsd_a = []
                self.__oldTsd_t = []
                self.__oldTsd_a = [[0.0 for i in range(1)] for j in range(self.__Nroot)]
                self.__oldTsd_t = [[0.0 for i in range(1)] for j in range(self.__Nroot)]
                self.hi = wall.hi  # 室内側表面総合熱伝達率
                self.ho = wall.ho  # 室外側表面総合熱伝達率
                self.Ei = wall.Ei   # 室内側表面放射率
                if self.is_sun_striked_outside:
                    self.outside_solar_absorption = wall.Solas  # 室側側日射吸収率
                    self.Eo = wall.Eo  # 室外側表面放射率
            # 透明部位の初期化
            elif self.boundary_type == "external_transparent_part":
                self.__transparent_opening = transparent_opening(self.name, d['transparent_opening_part_spec'])
                self.tau = self.__transparent_opening.T     # 日射透過率＝日射熱取得率
                self.Uso = self.__transparent_opening.Uso   # 熱貫流率（表面熱伝達抵抗除く）
                self.RFA0 = 1.0 / self.Uso                  # 吸熱応答係数の初項
                self.RFT0 = 1.0                             # 貫流応答係数の初項
                self.hi = self.__transparent_opening.hi     # 室内側表面総合熱伝達率
                self.ho = self.__transparent_opening.ho     # 室外側表面総合熱伝達率
                self.U = 1.0 / (1.0 / self.Uso + 1.0 / self.hi)  # 熱貫流率（表面熱伝達抵抗含む）
                self.Ei = self.__transparent_opening.Ei     # 室内側表面放射率
                if self.is_sun_striked_outside:
                    self.Eo = self.__transparent_opening.Eo     # 室外側表面放射率
            # 不透明な開口部の初期化
            elif self.boundary_type == "external_opaque_part":
                self.U = d['opaque_opening_part_spec']['u_value']     # 熱貫流率[W/(m2･K)]
                self.ho = 1.0/d['opaque_opening_part_spec']['outside_heat_transfer_resistance']   # 室外側表面総合熱伝達率
                self.Ei = 0.9                               # 室内側表面放射率
                self.hi = 1.0/d['opaque_opening_part_spec']['inside_heat_transfer_resistance']    # 室内側表面総合熱伝達率
                self.Uso = 1.0 / (1.0 / self.U - 1.0 / self.hi)
                                                            # 熱貫流率（表面熱伝達抵抗除く）
                self.RFA0 = 1.0 / self.Uso                  # 吸熱応答係数の初項
                self.RFT0 = 1.0                             # 貫流応答係数の初項
                if self.is_sun_striked_outside:
                    self.outside_solar_absorption = d['opaque_opening_part_spec']['outside_solar_absorption']  # 室側側日射吸収率
                    self.Eo = d['opaque_opening_part_spec']['outside_emissivity']           # 室外側表面放射率
            else:
                print("境界条件が見当たりません。 name=", self.name)

            # 部位のグループ化に関する変数
            # グループ番号
            self.group_number = -999
            # グループ化済み変数
            self.is_grouping = False

    # 畳み込み積分
    def convolution(self):
        sumTsd = 0.0
        for i in range(self.__Nroot):
            self.__oldTsd_t[i][0] = self.oldTeo * self.RFT1[i] + self.__Row[i] * self.__oldTsd_t[i][0]
            self.__oldTsd_a[i][0] = self.oldqi * self.RFA1[i] + self.__Row[i] * self.__oldTsd_a[i][0]
            sumTsd += self.__oldTsd_t[i][0] + self.__oldTsd_a[i][0]

        return sumTsd

    # 室内等価温度の計算
    def update_Tei(self, Tr, Tsx, Lr, Beta):
        """
        :param Tr: 室温
        :param Tsx: 形態係数加重平均表面温度
        :param Lr:
        :param Beta:
        :return:
        """
        self.Tei = Tr * self.hic / self.hi \
                     + Tsx * self.hir / self.hi \
                     + self.RSsol / self.hi \
                     + self.flr * Lr * (1.0 - Beta) / self.hi / self.area

    # 室内表面熱流の計算
    def update_qi(self, Tr: float, Tsx: float, Lr: float, Beta: float):
        """
        :param Tr: 室温
        :param Tsx: 形態係数加重平均表面温度
        :param Lr:
        :param Beta:
        :return:
        """
        # 対流成分
        self.Qc = self.hic * self.area * (Tr - self.Ts)

        # 放射成分
        self.Qr = self.hir * self.area * (Tsx - self.Ts)

        # 短波長熱取得成分
        self.RS = self.RSsol * self.area

        # 放射暖房成分
        self.__Lr = self.flr * Lr * (1.0 - Beta)

        # 表面熱流合計
        self.Qt = self.Qc + self.Qr + self.__Lr + self.RS
        # 前時刻熱流の保持
        self.oldqi = self.Qt / self.area

    # 透過日射の室内部位表面吸収日射量の初期化
    def update_RSsol(self, TotalQgt: float):
        """
        :param TotalQgt: 透過日射熱取得
        """
        self.RSsol = TotalQgt * self.SolR / self.area

    # 相当外気温度の計算
    def calcTeo(self, Ta, RN, oldTr, AnnualTave, spaces):
        # 前時刻の相当外気温度を控える
        self.oldTeo = self.Teo

        # 日射の当たる一般部位または不透明部位の場合
        if self.boundary_type == "external_general_part" or self.boundary_type == "external_opaque_part":
            # 室外側に日射が当たる場合
            if self.is_sun_striked_outside:
                self.Teo = self.__objExsrf.get_Te(self.outside_solar_absorption, self.ho, self.Eo, Ta, RN)
            # 室外側に日射が当たらない場合
            else:
                self.Teo = Ta * self.__objExsrf.R + oldTr * (1.0 - self.__objExsrf.R)
        # 窓の場合
        elif self.boundary_type == "external_transparent_part":
            self.Teo = self.Qga / self.area / self.U \
                - self.Eo * self.__objExsrf.Fs * RN / self.ho + Ta
        # 土壌の場合
        elif self.boundary_type == "ground":
            self.Teo = AnnualTave
        # 内壁の場合（前時刻の室温）
        elif self.boundary_type == "internal":
            self.Teo = self.__objExsrf.get_oldNextRoom(spaces)
        # 例外
        else:
            print("境界条件が見つかりません。 name=", self.boundary_type)
    # 地面反射率の取得
    @property
    def Rg(self):
        return self.__objExsrf.Rg

    # 透過日射量、吸収日射量の計算
    def update_Qgt_Qga(self):
        # 直達成分
        Qgtd = self.__transparent_opening.get_QGTD(self.__Id, self.__objExsrf.CosT, self.Fsdw) * self.area

        # 拡散成分
        Qgts = self.__transparent_opening.get_QGTS(self.__Isky, self.__Ir) * self.area

        # 透過日射量の計算
        self.Qgt = Qgtd + Qgts

        # print('Id', self.__Id, 'Qgtd', Qgtd, 'Qgts', Qgts)
        # 吸収日射量
        self.Qga = self.__transparent_opening.get_QGA(self.__Id, self.__Isky, self.__Ir, self.__objExsrf.CosT, self.Fsdw) * self.area

    # 日影面積率の計算
    def update_Fsdw(self, Solpos: defSolpos):
        if self.sunbrk.existance:
            self.Fsdw = self.sunbrk.get_Fsdw(Solpos, self.__objExsrf.Wa)

    # 傾斜面日射量を計算する
    def update_slope_sol(self, Solpos, Idn, Isky):
        if 'external' in self.__objExsrf.Type and self.is_sun_striked_outside:
            # 傾斜面日射量を計算
            self.__objExsrf.update_slop_sol(Solpos, Idn, Isky)
            # 直達日射量
            self.__Id = self.__objExsrf.Id

            # 天空日射量
            self.__Isky = self.__objExsrf.Is

            # 反射日射量
            self.__Ir = self.__objExsrf.Ir

            # 全天日射量
            self.__Iw = self.__Id + self.__Isky + self.__Ir

    # 形態係数の設定（面の微小球に対する形態係数）
    def setFF(self, FFd):
        self.__FF = FFd

    # 形態係数の取得
    def FF(self):
        return self.__FF

    # 境界条件が一致するかどうかを判定
    def boundary_comp(self, comp_surface):
        temp = False
        if self.boundary_type == comp_surface.boundary_type:
            # 間仕切りの場合
            if self.boundary_type == "internal":
                # 隣室名が同じ壁体は集約対象
                temp = self.next_room_type == comp_surface.next_room_type
                # 室内側熱伝達率の比較
                temp = temp and abs(self.hi - comp_surface.hi) < 1.0E-5
            # 外皮_一般部位の場合
            elif self.boundary_type == "external_general_part":
                # 日射の有無の比較
                temp = self.is_sun_striked_outside == comp_surface.is_sun_striked_outside
                # 温度差係数の比較
                temp = temp and abs(self.__temp_dif_coef - comp_surface.__temp_dif_coef) < 1.0E-5
                # 方位の比較
                temp = temp and self.__direction == comp_surface.__direction
                # 室内侵入日射吸収の有無の比較
                temp = temp and self.is_solar_absorbed_inside == comp_surface.is_solar_absorbed_inside
                # 屋外側放射率の比較
                temp = temp and abs(self.Eo - comp_surface.Eo) < 1.0E-5
                # 屋外側日射吸収率の比較
                temp = temp and abs(self.outside_solar_absorption - comp_surface.outside_solar_absorption) < 1.0E-5
                # 室内側熱伝達率の比較
                temp = temp and abs(self.hi - comp_surface.hi) < 1.0E-5
            # 透明な開口部の場合
            elif self.boundary_type == "external_transparent_part":
                # 日射の有無の比較
                temp = self.is_sun_striked_outside == comp_surface.is_sun_striked_outside
                # 方位の比較
                temp = temp and self.__direction == comp_surface.__direction
                # 屋外側放射率の比較
                temp = temp and abs(self.Eo - comp_surface.Eo) < 1.0E-5
                # 室内側熱伝達率の比較
                temp = temp and abs(self.hi - comp_surface.hi) < 1.0E-5
            # 不透明な開口部の場合
            elif self.boundary_type == "external_transparent_part":
                # 日射の有無の比較
                temp = self.is_sun_striked_outside == comp_surface.is_sun_striked_outside
                # 方位の比較
                temp = temp and self.__direction == comp_surface.__direction
                # 屋外側放射率の比較
                temp = temp and abs(self.Eo - comp_surface.Eo) < 1.0E-5
                # 室内側熱伝達率の比較
                temp = temp and abs(self.hi - comp_surface.hi) < 1.0E-5
            # 地盤の場合
            elif self.boundary_type == "ground":
                # 室内側熱伝達率の比較
                temp = temp and abs(self.hi - comp_surface.hi) < 1.0E-5
            # else:
            #     print("境界の種類が不適です。 name=", self.name)
        
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
