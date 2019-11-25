import datetime
from typing import List

from s3_space_loader import Space


def append_headers(spaces: List[Space]) -> List[List]:

    # 出力リスト
    OutList = []
    rowlist = []
    # ヘッダの出力
    rowlist.append("日時")
    rowlist.append("外気温度[℃]")
    rowlist.append("外気絶対湿度[kg/kg(DA)]")

    for space in spaces:
        rowlist.append(space.name_i + "_窓開閉")
        rowlist.append(space.name_i + "_在室状況")
        rowlist.append(space.name_i + "_最終空調状態")
        rowlist.append(space.name_i + "_空気温度[℃]")
        rowlist.append(space.name_i + "_室相対湿度[%]")
        rowlist.append(space.name_i + "_室絶対湿度[kg/kg(DA)]")
        rowlist.append(space.name_i + "_室MRT[℃]")
        rowlist.append(space.name_i + "_室作用温度[℃]")
        rowlist.append(space.name_i + "_PMV[-]")
        rowlist.append(space.name_i + "_着衣量[clo]")
        rowlist.append(space.name_i + "_風速[m/s]")
        rowlist.append(space.name_i + "_透過日射熱取得[W]")
        rowlist.append(space.name_i + "_機器顕熱発熱[W]")
        rowlist.append(space.name_i + "_照明発熱[W]")
        rowlist.append(space.name_i + "_人体顕熱発熱[W]")
        rowlist.append(space.name_i + "_人体潜熱発熱[W]")
        rowlist.append(space.name_i + "_対流空調顕熱負荷[W]")
        rowlist.append(space.name_i + "_放射空調顕熱負荷[W]")
        rowlist.append(space.name_i + "_対流空調潜熱負荷[W]")
        rowlist.append(space.name_i + "_家具温度[℃]")
        rowlist.append(space.name_i + "_家具取得熱量[W]")
        rowlist.append(space.name_i + "_家具吸収日射熱量[W]")
        rowlist.append(space.name_i + "_家具絶対湿度[kg/kg(DA)]")
        rowlist.append(space.name_i + "_家具取得水蒸気量[kg/s]")
        n = space.n_bdry_i_jstrs
        if 1:
            for g in range(n):
                rowlist.append(space.name_i + "_" + space.name_bdry_i_jstrs[g] + "_表面温度[℃]")
        if 1:
            for g in range(n):
                rowlist.append(space.name_i + "_" + space.name_bdry_i_jstrs[g] + "_等価室温[℃]")
        if 1:
            for g in range(n):
                rowlist.append(space.name_i + "_" + space.name_bdry_i_jstrs[g] + "_境界温度[℃]")
        if 1:
            for g in range(n):
                rowlist.append(space.name_i + "_" + space.name_bdry_i_jstrs[g] + "_表面放射熱流[W]")
        if 1:
            for g in range(n):
                rowlist.append(space.name_i + "_" + space.name_bdry_i_jstrs[g] + "_表面対流熱流[W]")

    OutList.append(rowlist)

    return OutList


def append_tick_log(spaces: List[Space], log: List[List], To_n: float, n: int, xo_n: float):

    # DTMは1989年1月1日始まりとする
    start_date = datetime.datetime(1989, 1, 1)

    # 1/1 0:00 からの時間　単位はday
    delta_day = float(n) / float(96)

    # 1/1 0:00 からの時刻, datetime 型
    dtm = start_date + datetime.timedelta(days=delta_day)

    row = [
        str(dtm),
        '{0:.1f}'.format(To_n[n]),
        '{0:.4f}'.format(xo_n[n])
    ]

    for space in spaces:
        row.append(space.is_now_window_open_i_n[n])
        row.append(space.air_conditioning_demand[n])
        row.append('{0:.0f}'.format(space.now_air_conditioning_mode[n]))
        row.append('{0:.2f}'.format(space.Tr_i_n[n]))
        row.append('{0:.0f}'.format(space.RH_i_n[n]))
        row.append('{0:.4f}'.format(space.xr_i_n[n]))
        row.append('{0:.2f}'.format(space.MRT_i_n[n]))
        row.append('{0:.2f}'.format(space.OT_i_n[n]))
        row.append('{0:.2f}'.format(space.PMV_i_n[n]))
        row.append('{0:.2f}'.format(space.Clo_i_n[n]))
        row.append('{0:.2f}'.format(space.Vel_i_n[n]))
        row.append('{0:.2f}'.format(space.q_trs_sol_i_ns[n]))
        row.append('{0:.2f}'.format(space.heat_generation_appliances_schedule[n]))
        row.append('{0:.2f}'.format(space.heat_generation_lighting_schedule[n]))
        row.append('{0:.2f}'.format(space.Hhums[n]))
        row.append('{0:.2f}'.format(space.Hhuml[n]))
        row.append('{0:.1f}'.format(space.Lcs_i_n[n]))
        row.append('{0:.1f}'.format(space.Lrs_i_n[n]))
        row.append('{0:.1f}'.format(space.Lcl_i_n[n]))
        row.append('{0:.2f}'.format(space.Tfun_i_n[n]))
        row.append('{0:.1f}'.format(space.Qfuns_i_n[n]))
        row.append('{0:.1f}'.format(space.Qsolfun_i_n[n]))
        row.append('{0:.5f}'.format(space.xf_i_n[n]))
        row.append('{0:.5f}'.format(space.Qfunl_i_n[n]))
        n = space.n_bdry_i_jstrs
        for g in range(n):
            row.append('{0:.2f}'.format(space.Ts_i_k_n[g, n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.Tei_i_k_n[g, n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.Teo_i_k_n[g, n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.Qr[g, n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.Qc[g, n]))
    log.append(row)
