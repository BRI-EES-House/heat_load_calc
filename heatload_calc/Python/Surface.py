import nbimporter

# 室内部位に関連するクラス
class Surface:
    
    # 初期化
    def __init__(self, ExsrfMng, WallMng, WindowMng, SunbrkMng, skin, boundary,                  unsteady, name, area, sunbreak, flr, fot):
        self.__skin = skin            #外皮フラグ
        self.__boundary = boundary    #方位・隣室名
        
        # 外皮の場合は方位クラスを取得する
        if self.__skin == True :
            self.__objExsrf = ExsrfMng.ExsrfobjByName(self.__boundary)
        
        self.__unsteady = unsteady    #非定常フラグ
        self.__name = name            #壁体名称
        
        if '床' in self.__name :      #床フラグ
            self.__floor = True
        else:
            self.__floor = False
            
        self.__area = float(area)            #面積
        self.__sunbreakname = sunbreak    #ひさし名称
        self.__Fsdw = 0.0                   # 影面積率の初期化
        self.__flr = float(flr)              #放射暖房吸収比率
        self.__fot = float(fot)              #人体に対する形態係数
        #self.__floor = floor          #床フラグ
        
        #形態係数収録用リストの定義
        self.__FF = []
        
        #透過日射の室内部位表面吸収日射量の初期化
        self.__RSsol = 0.0

        #庇フラグの初期化
        self.__sunbrkflg = False
        #窓フラグの初期化
        self.__windowflg = False
        #開口部透過日射量、吸収日射量の初期化
        self.__Qgt = 0.0
        self.__Qga = 0.0
        #相当外気温度の初期化
        self.__Teo = 15.0
        self.__oldTeo = 15.0

        self.__Nroot = 0

        self.__Qt = 0.0
        self.__oldTeo = 15.0                         #前時刻の室外側温度
        self.__oldqi = 0.0                          #前時刻の室内側表面熱流
        #print(self.__unsteady)
        # 壁体の初期化
        if self.__unsteady == True :
            #print(self.__name)
            
            self.__Row = WallMng.Row(self.__name)        #公比の取得
            self.__Nroot = WallMng.Nroot(self.__name)    #根の数
            self.__RFT0 = WallMng.RFT0(self.__name)      #貫流応答の初項
            self.__RFA0 = WallMng.RFA0(self.__name)      #吸熱応答の初項
            self.__RFT1 = WallMng.RFT1(self.__name)      #指数項別貫流応答の初項
            self.__RFA1 = WallMng.RFA1(self.__name)      #指数項別吸熱応答の初項
            self.__oldTsd_a = []
            self.__oldTsd_t = []
            self.__oldTsd_a = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]
            self.__oldTsd_t = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]
            # self.__oldTsd_t = range(0, self.__Nroot-1)   #貫流応答の表面温度の履歴
            # self.__oldTsd_a = range(0, self.__Nroot-1)   #吸熱応答の表面温度の履歴
            self.__hi = WallMng.hi(self.__name)          #室内側表面総合熱伝達率
            self.__hic = WallMng.hic(self.__name)        #室内側表面対流熱伝達率
            self.__hir = WallMng.hir(self.__name)        #室内側表面放射熱伝達率
            self.__ho = WallMng.ho(self.__name)          #室外側表面総合熱伝達率
            self.__as = WallMng.Solas(self.__name)       #室側側日射吸収率
            self.__Eo = WallMng.Eo(self.__name)          #室内側表面総合熱伝達率
            #print('RFT0=', self.__RFT0)
            #print('RFA0=', self.__RFA0)
            #print('hi=', self.__hi)
        # 定常部位の初期化
        else:
            self.__objWindow = WindowMng.Window(self.__name)
            objWindow = WindowMng.Window(self.__name)    #Windowオブジェクトの取得
            self.__windowflg = True
            self.__tau = objWindow.T()        #日射透過率
            self.__B = objWindow.B()          #吸収日射取得率
            self.__Uso = objWindow.Uso()      #熱貫流率（表面熱伝達抵抗除く）
            self.__RFA0 = 1.0 / self.__Uso                 #吸熱応答係数の初項
            self.__RFT0 = 1.0                              #貫流応答係数の初項
            self.__hi = objWindow.hi()        #室内側表面総合熱伝達率
            self.__hic = objWindow.hic()      #室内側表面対流熱伝達率
            self.__hir = objWindow.hir()      #室内側表面放射熱伝達率
            self.__ho = objWindow.ho()        #室外側表面総合熱伝達率
            self.__U = 1.0 / (1.0 / self.__Uso + 1.0 / self.__hi)   #熱貫流率（表面熱伝達抵抗含む）
            self.__Eo = objWindow.Eo()        #室内側表面総合熱伝達率
            self.__sunbrkflg = len(self.__sunbreakname) > 0  #庇がついているかのフラグ
            if self.__sunbrkflg:
                self.__sunbkr = SunbrkMng.Sunbrk(self.__sunbreakname)
    
    #畳み込み演算のためのメモリ確保
    # def Tsd_malloc(self):
    #     self.__oldTsd_a = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]
    #     self.__oldTsd_t = [ [ 0.0 for i in range(1) ] for j in range(self.__Nroot) ]

    #畳み込み積分
    def convolution(self):
        sumTsd = 0.0
        for i in range(self.__Nroot):
            self.__oldTsd_t[i][0] = self.__oldTeo * self.__RFT1[i] \
                    + self.__Row[i] * self.__oldTsd_t[i][0]
            self.__oldTsd_a[i][0] = self.__oldqi * self.__RFA1[i] \
                    + self.__Row[i] * self.__oldTsd_a[i][0]
            sumTsd += self.__oldTsd_t[i][0] + self.__oldTsd_a[i][0]
        
        return sumTsd

    #人体に対する当該部位の形態係数の取得
    def fot(self):
        return self.__fot
    #表面温度の計算
    def setTs(self, Ts):
        self.__Ts = Ts
    #表面温度の取得
    def Ts(self):
        return self.__Ts
    #室内等価温度の計算
    def calcTei(self, Tr, Tsx, Lr, Beta):
        self.__Tei = Tr * self.__hic / self.__hi \
                + Tsx * self.__hir / self.__hi \
                + self.__RSsol / self.__hi \
                + self.__flr * Lr * (1.0 - Beta) / self.__hi / self.__area
    
    #前時刻の室内表面熱流の取得
    def oldqi(self):
        return self.__oldqi
    #室内表面熱流の計算
    def calcqi(self, Tr, Tsx, Lr, Beta):
        #前時刻熱流の保持
        self.__oldqi = self.__Qt / self.__area

        #対流成分
        self.__Qc = self.__hic * self.__area * (Tr - self.__Ts)
        #放射成分
        self.__Qr = self.__hir * self.__area * (Tsx - self.__Ts)
        #短波長熱取得成分
        self.__RS = self.__RSsol * self.__area
        #放射暖房成分
        self.__Lr = self.__flr * Lr * (1.0 - Beta)
        #表面熱流合計
        self.__Qt = self.__Qc + self.__Qr + self.__Lr + self.__RS

    #透過日射の室内部位表面吸収日射量の初期化
    def calcRSsol(self, TotalQgt):
        self.__RSsol = TotalQgt * self.__SolR / self.__area
        # print(self.__boundary, self.__RSsol)

    #透過日射の室内部位表面吸収日射の取得
    def RSsol(self):
        return self.__RSsol

    #透過日射の室内部位表面吸収比率の設定
    def setSolR(self, SolR):
        self.__SolR = SolR

    #境界条件
    def boundary(self):
        return self.__boundary

    #相当外気温度の計算
    def calcTeo(self, Ta, RN, oldTr, spaces):
        self.__oldTeo = self.__Teo
        #非定常部位の場合
        if self.__unsteady:
            #外皮の場合（相当外気温度もしくは隣室温度差係数から計算）
            if self.__skin:
                self.__Teo = self.__objExsrf.Te(self.__as, self.__ho, \
                        self.__Eo, Ta, RN, oldTr)
            #内壁の場合（前時刻の室温）
            else:
                self.__Teo = spaces.oldTr(self.__boundary)
        #定常部位（窓）の場合
        else:
            #外皮の場合
            if self.__skin:
                self.__Teo = self.__Qga / self.__area / self.__U \
                        - self.__Eo * self.__objExsrf.Fs() * RN / self.__ho \
                        + Ta
            #内壁の場合（前時刻の室温）
            else:
                self.__Teo = spaces.oldTr(self.__boundary)

    #相当外気温度の取得
    def Teo(self):
        return self.__Teo
    #前時刻の相当外気温度の取得
    def oldTeo(self):
        return self.__oldTeo
    
    #非定常フラグの取得
    def unstrady(self):
        return self.__unsteady

    #地面反射率の取得
    def rg(self):
        return self.__objExsrf.Rg()

    #透過日射量、吸収日射量の計算
    def calcQgt_Qga(self):
        #直達成分
        Qgtd = self.__objWindow.QGTD(self.__Id, self.__objExsrf.CosT(), self.__Fsdw) * self.__area
        #拡散成分
        Qgts = self.__objWindow.QGTS(self.__Isky, self.__Ir) * self.__area
        #透過日射量の計算
        self.__Qgt = Qgtd + Qgts
        #吸収日射量
        self.__Qga = self.__objWindow.QGA(self.__Id, self.__Isky, \
                self.__Ir, self.__objExsrf.CosT(), self.__Fsdw) * self.__area
    #透過日射量の取得
    def Qgt(self):
        return self.__Qgt
    #吸収日射量の取得
    def Qga(self):
        return self.__Qga
    #庇名称の取得
    def sunbrkname(self):
        return self.__sunbreakname

    #庇の有無フラグ
    def sunbrkflg(self):
        return self.__sunbrkflg

    #窓フラグ
    def windowflg(self):
        return self.__windowflg

    #日影面積率の計算
    def calcFsdw(self, Solpos):
        self.__Fsdw = self.__sunbkr.FSDW(Solpos, self.__objExsrf.Wa())

    #日影面積を取得
    def Fsdw(self, Solpos):
        return self.__sunbkr.FSDW(Solpos)

    #日影面積をセット
    def setFsdw(self, Fsdw):
        self.__Fsdw = Fsdw

    #床フラグの取得
    def Floor(self):
        return self.__floor
    
    #部位面積の取得
    def area(self):
        return self.__area
    
    #応答係数の初項の取得
    def RFA0(self):
        return self.__RFA0
    def RFT0(self):
        return self.__RFT0
    
    #指数項別応答係数
    def RFA1(self):
        return self.__RFA1
    def RFT1(self):
        return self.__RFT1
    
    #公比の取得
    def Row(self):
        if self.__unsteady == True:
            return self.__Row
        else:
            return 0
    
    #室内側表面総合熱伝達率
    def hi(self):
        return self.__hi
    
    #放射暖房吸収比率の取得
    def flr(self):
        return self.__flr
    
    #放射熱伝達率の取得
    def hir(self):
        return self.__hir
    
    #対流熱伝達率の取得
    def hic(self):
        return self.__hic
    
    #形態係数収録用メモリの確保
    #def FF_alloc(self, Nsurf):
    #    self.__FF = [0:Nsurf-1]
    #    #self.__FF = range(0, Nsurf-1)
    #    print('FFの要素数=', len(self.__FF))
    
    #傾斜面日射量を計算する
    def update_slope_sol(self):
        #直達日射量
        self.__Id = self.__objExsrf.Id()
        #天空日射量
        self.__Isky = self.__objExsrf.Isk()
        #反射日射量
        self.__Ir = self.__objExsrf.Ir()
        #全天日射量
        self.__Iw = self.__Id + self.__Isky + self.__Ir
    
    #傾斜面日射量の出力
    def print_slope_sol(self):
        print(self.__boundary, self.__name)
        print('直達日射量[W/m2]：', self.__Id)
        print('天空日射量[W/m2]：', self.__Isky)
        print('反射日射量[W/m2]：', self.__Ir)
        print('全天日射量[W/m2]：', self.__Iw)
    
    #部位の情報出力
    def print_surface(self):
        print(self.__boundary, self.__name)
        print('面積[m2]', self.__area)
    
    #外皮フラグを返す
    def skin(self):
        return self.__skin
    
    #形態係数の設定
    def setFF(self, FFd):
        self.__FF.append(FFd)
    #形態係数の取得
    def FF(self, i):
        return self.__FF[i]
