from Wall import Wall, Layer
from ResponseFactor import ResponseFactor
from Window import Window
from SolarPosision import defSolpos
from Gdata import Gdata
from Exsrf import Exsrf
# from Exsrf import create_exsurfaces
from Sunbrk import SunbrkType

# 室内部位に関連するクラス
class Surface:

    # 初期化
    def __init__(self, d: dict, Gdata: Gdata):
        self.is_skin = d['skin']  # 外皮フラグ
        # 外皮の場合は方位クラスを取得する
        self.__objExsrf = Exsrf(d['boundary'])

        self.unsteady = d['unsteady']  # 非定常フラグ
        # self.direction = d['direction'] # 室内から見た部位の方向（人体に対する形態係数計算用）
        self.name = d['name']  # 壁体名称

        self.Floor = d['floor']        #床フラグ

        self.area = float(d['area'])  # 面積
        self.a = 0.0                    # 部位の面積比率（全面積に対する面積比）
        self.sunbreakname = d['sunbreak']  # ひさし名称
        self.Fsdw = 0.0  # 影面積率の初期化
        self.flr = 0,0
        if 'flr' in d:
            self.flr = float(d['flr'])  # 放射暖房吸収比率
        self.fot = 0.0  # 人体に対する形態係数の初期化
        self.__IsSoil = False
        if 'IsSoil' in d:
            self.__IsSoil = d['IsSoil']     # 壁体に土壌が含まれる場合True
        # self.Floor = floor          #床フラグ

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

        # 庇フラグの初期化
        self.has_sunbrk = False

        # 窓フラグの初期化
        self.is_window = False

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

        self.__Qt = 0.0
        self.__Qc = 0.0  # 対流成分
        self.__Qr = 0.0  # 放射成分
        self.__RS = 0.0  # 短波長熱取得成分
        self.__Lr = 0.0  # 放射暖房成分

        self.oldTeo = 15.0  # 前時刻の室外側温度
        self.oldqi = 0.0  # 前時刻の室内側表面熱流

        # 壁体の初期化
        if self.unsteady == True:
            # 壁体情報,応答係数の取得
            wall, rf = WalldataRead(self.name, d['Wall'], Gdata.DTime, self.__IsSoil)
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
            self.__as = wall.Solas  # 室側側日射吸収率
            self.Eo = wall.Eo  # 室外側表面放射率
            self.Ei = wall.Ei   # 室内側表面放射率
        # 定常部位の初期化
        else:
            self.__window = Window(Name=self.name, **d['Window'])
            self.is_window = True
            self.tau = self.__window.T  # 日射透過率＝日射熱取得率
            # self.B = self.__window.B  # 吸収日射取得率
            self.B = 0.0                # 吸収日射取得率
            self.Uso = self.__window.Uso  # 熱貫流率（表面熱伝達抵抗除く）
            self.RFA0 = 1.0 / self.Uso  # 吸熱応答係数の初項
            self.RFT0 = 1.0  # 貫流応答係数の初項
            self.hi = self.__window.hi  # 室内側表面総合熱伝達率
            self.ho = self.__window.ho  # 室外側表面総合熱伝達率
            self.U = 1.0 / (1.0 / self.Uso + 1.0 / self.hi)  # 熱貫流率（表面熱伝達抵抗含む）
            self.Eo = self.__window.Eo  # 室外側表面放射率
            self.Ei = self.__window.Ei  # 室内側表面放射率
            self.has_sunbrk = type(self.sunbreakname) is dict # 庇がついているかのフラグ
            # print(type(self.sunbreakname))
            if self.has_sunbrk:
                sunbreakname = 'NoName'
                if 'name' in self.sunbreakname:
                    sunbreakname = self.sunbreakname['name']
                self.sunbrk = SunbrkType(sunbreakname, self.sunbreakname['D'], \
                        self.sunbreakname['WI1'], self.sunbreakname['WI2'], self.sunbreakname['hi'], \
                        self.sunbreakname['WR'], self.sunbreakname['WH'])

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
        self.__Tei = Tr * self.hic / self.hi \
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
        # 前時刻熱流の保持
        self.oldqi = self.__Qt / self.area

        # 対流成分
        self.__Qc = self.hic * self.area * (Tr - self.Ts)

        # 放射成分
        self.__Qr = self.hir * self.area * (Tsx - self.Ts)

        # 短波長熱取得成分
        self.__RS = self.RSsol * self.area

        # 放射暖房成分
        self.__Lr = self.flr * Lr * (1.0 - Beta)

        # 表面熱流合計
        self.__Qt = self.__Qc + self.__Qr + self.__Lr + self.__RS

    # 透過日射の室内部位表面吸収日射量の初期化
    def update_RSsol(self, TotalQgt: float):
        """
        :param TotalQgt: 透過日射熱取得
        """
        self.RSsol = TotalQgt * self.SolR / self.area

    # 相当外気温度の計算
    def calcTeo(self, Ta, RN, oldTr, AnnualTave, spaces):
        self.oldTeo = self.Teo

        # 日射の当たる外皮の場合
        if self.__objExsrf.Type == "Outdoor":
            if self.unsteady:
                # 非定常部位の場合（相当外気温度もしくは隣室温度差係数から計算）
                self.Teo = self.__objExsrf.get_Te(self.__as, self.ho, self.Eo, Ta, RN)
            else:
                # 定常部位（窓）の場合
                self.Teo = self.Qga / self.area / self.U \
                        - self.Eo * self.__objExsrf.Fs * RN / self.ho + Ta
        # 年平均気温の場合
        elif self.__objExsrf.Type == "AnnualAverage":
            self.Teo = AnnualTave
        elif self.__objExsrf.Type == "DeltaTCoeff":
            self.Teo = self.__objExsrf.get_NextRoom_fromR(Ta, oldTr)
        elif self.__objExsrf.Type == "NextRoom":
            # 内壁の場合（前時刻の室温）
            self.Teo = self.__objExsrf.get_oldNextRoom(spaces)

    # 地面反射率の取得
    @property
    def Rg(self):
        return self.__objExsrf.Rg

    # 透過日射量、吸収日射量の計算
    def update_Qgt_Qga(self):
        # 直達成分
        Qgtd = self.__window.get_QGTD(self.__Id, self.__objExsrf.CosT, self.Fsdw) * self.area

        # 拡散成分
        Qgts = self.__window.get_QGTS(self.__Isky, self.__Ir) * self.area

        # 透過日射量の計算
        self.Qgt = Qgtd + Qgts

        # 吸収日射量
        self.Qga = self.__window.get_QGA(self.__Id, self.__Isky, self.__Ir, self.__objExsrf.CosT, self.Fsdw) * self.area

    # 日影面積率の計算
    def update_Fsdw(self, Solpos: defSolpos):
        self.Fsdw = self.sunbrk.get_Fsdw(Solpos, self.__objExsrf.Wa)

    # 公比の取得
    @property
    def Row(self):
        return self.__Row if self.unsteady == True else 0.0

    # 傾斜面日射量を計算する
    def update_slope_sol(self, Solpos, Idn, Isky):
        if self.__objExsrf.Type == 'Outdoor':
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
        # 境界条件種類が一致
        return self.__objExsrf.exsrf_comp(comp_surface.__objExsrf)

# 壁体構成データの読み込みと応答係数の作成
def WalldataRead(Name, d, DTime, IsSoil):
    # 時間間隔(s)
    dblDTime = DTime

    # 壁体構成部材の情報を保持するクラスをインスタンス化
    layers = [
        Layer(
            name=d_layers['name'],
            cond=d_layers['cond'],
            spech=d_layers['specH'],
            thick=d_layers['thick']
        )
        for d_layers in d['Layers']
    ]

    # 壁体情報を保持するクラスをインスタンス化
    OutEmissiv = 0.9
    if 'OutEmissiv' in d:
        OutEmissiv = d['OutEmissiv']
    OutSolarAbs = 0.8
    if 'OutSolarAbs' in d:
        OutSolarAbs = d['OutSolarAbs']
    wall = Wall(
        Name=Name,
        IsSoil=IsSoil,
        OutEmissiv=OutEmissiv,
        OutSolarAbs=OutSolarAbs,
        InHeatTrans=d['InHeatTrans'],
        Layers=layers
    )
    walltype = 'wall'
    if IsSoil:
        walltype = 'soil'
    # 応答係数を保持するクラスをインスタンス化
    rf = ResponseFactor(
        WallType=walltype,
        DTime=dblDTime,
        NcalTime=50,
        Wall=wall
    )

    return wall, rf
