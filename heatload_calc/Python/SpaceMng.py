import Space
from Space import Space

class SpaceMng:
    def __init__(self, Gdata, ExsrfMng, SunbrkMng, d):
        #空間定義の配列を作成
        #self.__objSpaces = []
        #print(d)
        
        self.__objSpace = []
        for d_space in d:
            #print(d_space)
            #部位の情報を保持するクラスをインスタンス化
            # Surfaces = []
            # for d_surface in d_space['Surface']:
                #skin, boundary, unsteady, name, area, sunbreak, flr, fot, floor
                #surface = Surface(WallMng, WindowMng, SunbrkMng, d_surface['skin'], \
                #                  d_surface['boundary'], d_surface['unsteady'], \
                #                  d_surface['name'], d_surface['area'], \
                #                  d_surface['sunbrk'], \
                #                  d_surface['flr'], d_surface['fot'])
                # Surfaces.append(d_surface)
                #print(d_surface['boundary'])
            
            #計画換気の読み込み
            # Vent_season = d_space['Vent']
            #Vent_season = []
            #for d_vent in d_scpace['Vent']:
            #    Vent_season.append(d_vent)
            
            #すきま風の読み込み
            # Inf_season = d_space['Inf']
            #Inf_season = []
            #for d_inf in d_space['Inf']:
            #    Inf_season.append(d_inf)
            
            #室間換気量の読み込み
            # NextVentList = []
            # for d_nextvent in d_space['NextVent']:
            #     next_vent = NextVent(d_nextvent['Windward_roomname'], \
            #             d_nextvent['Season'], d_nextvent['VentVolume'])
            #     NextVentList.append(next_vent)
            
            
            #空間情報を保持するクラスをインスタンス化
            #def __init__(self, ExsrfMng, WallMng, WindowMng, SunbrkMng, roomname, roomdiv, \
            #     HeatCcap, HeatRcap, \
            #     CoolCcap, Vol, Fnt, Vent, Inf, CrossVentRoom, \
            #     RadHeat, Beta, RoomtoRoomVents, Surfaces):
            space = Space(Gdata, ExsrfMng, SunbrkMng, d_space['roomname'],\
                    d_space['HeatCcap'],\
                    d_space['HeatRcap'], d_space['CoolCcap'], d_space['Vol'],\
                    d_space['Fnt'], d_space['Vent'], d_space['Inf'],\
                    d_space['CrossVentRoom'], d_space['RadHeat'], d_space['Beta'], d_space['NextVent'], d_space['Surface'])
            #print(space)
            self.__objSpace.append(space)
        
        print(self.__objSpace)
        #return objSpace
    
    #前時刻の室温を取得する
    def oldTr(self, roomname):
        Tr = -999.0
        for space in self.__objSpace:
            if space.name() == roomname:
                Tr = space.oldTr()
                break
        return Tr

    #室温、熱負荷の計算
    def calcHload(self, Gdata, dtmDate, objWdata, objSchedule, objSunbrk):
        print(dtmDate, "", end="")
        for space in self.__objSpace:
            #def calcHload(self, spaces, SolarPosision, Schedule, Weather):
            space.calcHload(Gdata, self, dtmDate, objWdata.Solpos(dtmDate), objSchedule, objWdata, objSunbrk)
            print('{0:.2f}'.format(space.Tr()), '{0:.2f}'.format(space.MRT()),'{0:.2f}'.format(space.Lcs()), '{0:.2f}'.format(space.Lr()), "", end="")
            # if space.name() == '主たる居室':
            #     print('{0:.2f}'.format(space.Tr()), "", end="")
            #     space.surftemp_print()
                # print('{0:.2f}'.format(space.Qgt()))
        print("")

        #前時刻の室温を現在時刻の室温に置換
        for space in self.__objSpace:
            space.update_oldTr()
