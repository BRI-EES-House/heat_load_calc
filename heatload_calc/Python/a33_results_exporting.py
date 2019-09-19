import numpy as np

def append_headers(spaces):
    # 出力リスト
    OutList = []
    rowlist = []
    # ヘッダの出力
    rowlist.append("日時")
    rowlist.append("外気温度[℃]")
    rowlist.append("外気絶対湿度[kg/kg(DA)]")
    for space in spaces.values():
        rowlist.append(space.name + "_窓開閉")
        rowlist.append(space.name + "_在室状況")
        rowlist.append(space.name + "_最終空調状態")
        rowlist.append(space.name + "_空気温度[℃]")
        rowlist.append(space.name + "_室相対湿度[%]")
        rowlist.append(space.name + "_室絶対湿度[kg/kg(DA)]")
        rowlist.append(space.name + "_室MRT[℃]")
        rowlist.append(space.name + "_室作用温度[℃]")
        rowlist.append(space.name + "_PMV[-]")
        rowlist.append(space.name + "_着衣量[clo]")
        rowlist.append(space.name + "_風速[m/s]")
        rowlist.append(space.name + "_透過日射熱取得[W]")
        rowlist.append(space.name + "_機器顕熱発熱[W]")
        rowlist.append(space.name + "_照明発熱[W]")
        rowlist.append(space.name + "_人体顕熱発熱[W]")
        rowlist.append(space.name + "_人体潜熱発熱[W]")
        rowlist.append(space.name + "_対流空調顕熱負荷[W]")
        rowlist.append(space.name + "_放射空調顕熱負荷[W]")
        rowlist.append(space.name + "_対流空調潜熱負荷[W]")
        rowlist.append(space.name + "_家具温度[℃]")
        rowlist.append(space.name + "_家具取得熱量[W]")
        rowlist.append(space.name + "_家具吸収日射熱量[W]")
        rowlist.append(space.name + "_家具絶対湿度[kg/kg(DA)]")
        rowlist.append(space.name + "_家具取得水蒸気量[kg/s]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_表面温度[℃]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_等価室温[℃]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_境界温度[℃]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_表面放射熱流[W]")
        if 1:
            for g in range(space.surfG_i.NsurfG_i):
                rowlist.append(space.name + "_" + space.surfG_i.name[g] + "_表面対流熱流[W]")
    OutList.append(rowlist)
    return OutList




def append_tick_log(spaces, OutList, To_n, dtlist, n, xo_n):
    dtmNow = dtlist[n]
    rowlist = [
        str(dtmNow),
        '{0:.1f}'.format(To_n[n]),
        '{0:.4f}'.format(xo_n[n])
    ]
    for space in spaces.values():
        rowlist.append(space.is_now_window_open_i_n[n])
        rowlist.append(space.air_conditioning_demand[n])
        rowlist.append('{0:.0f}'.format(space.now_air_conditioning_mode[n]))
        rowlist.append('{0:.2f}'.format(space.Tr_i_n[n]))
        rowlist.append('{0:.0f}'.format(space.RH_i_n[n]))
        rowlist.append('{0:.4f}'.format(space.xr_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.MRT_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.OT_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.PMV_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.Clo_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.Vel_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.QGT_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.heat_generation_appliances_schedule[n]))
        rowlist.append('{0:.2f}'.format(space.heat_generation_lighting_schedule[n]))
        rowlist.append('{0:.2f}'.format(space.Hhums[n]))
        rowlist.append('{0:.2f}'.format(space.Hhuml[n]))
        rowlist.append('{0:.1f}'.format(space.Lcs_i_n[n]))
        rowlist.append('{0:.1f}'.format(space.Lrs_i_n[n]))
        rowlist.append('{0:.1f}'.format(space.Lcl_i_n[n]))
        rowlist.append('{0:.2f}'.format(space.Tfun_i_n[n]))
        rowlist.append('{0:.1f}'.format(space.Qfuns_i_n[n]))
        rowlist.append('{0:.1f}'.format(space.Qsolfun_i_n[n]))
        rowlist.append('{0:.5f}'.format(space.xf_i_n[n]))
        rowlist.append('{0:.5f}'.format(space.Qfunl_i_n[n]))
        for g in range(space.surfG_i.NsurfG_i):
            rowlist.append('{0:.2f}'.format(space.Ts_i_k_n[g, n]))
        for g in range(space.surfG_i.NsurfG_i):
            rowlist.append('{0:.2f}'.format(space.Tei_i_k_n[g, n]))
        for g in range(space.surfG_i.NsurfG_i):
            rowlist.append('{0:.2f}'.format(space.Teo_i_k_n[g, n]))
        for g in range(space.surfG_i.NsurfG_i):
            rowlist.append('{0:.2f}'.format(space.Qr[g, n]))
        for g in range(space.surfG_i.NsurfG_i):
            rowlist.append('{0:.2f}'.format(space.Qc[g, n]))
    OutList.append(rowlist)


# 年間熱負荷の積算
def get_annual_loads(spaces):
    convert_J_GJ = 1.0e-9
    DTime = 900
    # 対流式空調（顕熱）の積算
    AnnualLoadcHs = sum(
        [np.sum(space.Lcs_i_n[space.Lcs_i_n > 0.0] * DTime * convert_J_GJ) for space in spaces.values()])
    AnnualLoadcCs = sum(
        [np.sum(space.Lcs_i_n[space.Lcs_i_n < 0.0] * DTime * convert_J_GJ) for space in spaces.values()])
    # 対流式空調（潜熱）の積算
    AnnualLoadcHl = sum(
        [np.sum(space.Lcl_i_n[space.Lcl_i_n > 0.0] * DTime * convert_J_GJ) for space in spaces.values()])
    AnnualLoadcCl = sum(
        [np.sum(space.Lcl_i_n[space.Lcl_i_n < 0.0] * DTime * convert_J_GJ) for space in spaces.values()])
    # 放射式空調（顕熱）の積算
    AnnualLoadrHs = sum(
        [np.sum(space.Lrs_i_n[space.Lrs_i_n > 0.0] * DTime * convert_J_GJ) for space in spaces.values()])
    AnnualLoadrCs = sum(
        [np.sum(space.Lrs_i_n[space.Lrs_i_n < 0.0] * DTime * convert_J_GJ) for space in spaces.values()])
    # 放射式空調（潜熱）の積算
    AnnualLoadrHl = sum(
        [np.sum(space.Lrl_i_n[space.Lrl_i_n > 0.0] * DTime * convert_J_GJ) for space in spaces.values()])
    AnnualLoadrCl = sum(
        [np.sum(space.Lrl_i_n[space.Lrl_i_n < 0.0] * DTime * convert_J_GJ) for space in spaces.values()])

    return AnnualLoadcHs, AnnualLoadcCs, AnnualLoadcHl, AnnualLoadcCl, AnnualLoadrHs, AnnualLoadrCs, AnnualLoadrHl, AnnualLoadrCl
