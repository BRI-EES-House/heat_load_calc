import copy
import math

import numpy

from heat_load_calc.external import factor_nu as nu
from heat_load_calc.external import factor_h
import factor_f_2 as f


class Parts:

    def __init__(self, area, ptype, nextspace, direction):
        self.__area = area
        self.__ptype = ptype
        self.__nextspace = nextspace
        self.__direction = direction

    @property
    def area(self):
        return self.__area

    @property
    def ptype(self):
        return self.__ptype

    @property
    def nextspace(self):
        return self.__nextspace

    @property
    def direction(self):
        return self.__direction


def get_total_area(d):
    d_area = []
    for x in ['general_parts', 'windows', 'doors', 'earthfloors']:
        if (x in d) == True:
            d_area.extend(d[x])

    return sum(x['area'] for x in d_area)


def get_list_part_type():
    return ['roof','ceiling','wall','floor','boundary_ceiling','boundary_wall','boundary_floor','window','door','earthfloor_perimeter']


def get_list_sunshine_part_type():
    return ['roof','ceiling','wall','window','door']


def get_list_no_sunshine_part_type():
    return ['floor','boundary_ceiling','boundary_wall','boundary_floor','earthfloor_perimeter']


def get_std_U(region, part_type) :

    return {
        'roof'                 : {1: 0.17, 2: 0.17, 3: 0.24, 4: 0.24, 5: 0.24, 6: 0.24, 7: 0.24, 8: 0.24 },
        'ceiling'              : {1: 0.17, 2: 0.17, 3: 0.24, 4: 0.24, 5: 0.24, 6: 0.24, 7: 0.24, 8: 0.24 },
        'wall'                 : {1: 0.35, 2: 0.35, 3: 0.53, 4: 0.53, 5: 0.53, 6: 0.53, 7: 0.53, 8: 4.10 },
        'floor'                : {1: 0.34, 2: 0.34, 3: 0.34, 4: 0.48, 5: 0.48, 6: 0.48, 7: 0.48, 8: 3.52 },
        'boundary_ceiling'     : {1: 0.17, 2: 0.17, 3: 0.24, 4: 0.24, 5: 0.24, 6: 0.24, 7: 0.24, 8: 0.24 },
        'boundary_wall'        : {1: 0.35, 2: 0.35, 3: 0.53, 4: 0.53, 5: 0.53, 6: 0.53, 7: 0.53, 8: 4.10 },
        'boundary_floor'       : {1: 0.34, 2: 0.34, 3: 0.34, 4: 0.48, 5: 0.48, 6: 0.48, 7: 0.48, 8: 3.52 },
        'window'               : {1: 2.33, 2: 2.33, 3: 3.49, 4: 4.65, 5: 4.65, 6: 4.65, 7: 4.65, 8: 6.51 },
        'door'                 : {1: 2.33, 2: 2.33, 3: 3.49, 4: 4.65, 5: 4.65, 6: 4.65, 7: 4.65, 8: 6.51 },
        'earthfloor_perimeter' : {1: 0.53, 2: 0.53, 3: 0.53, 4: 0.76, 5: 0.76, 6: 0.76, 7: 0.76, 8: 1.80 }
    }[part_type][region]


def get_min_U(ptype):    # 熱貫流率の下限値 W/m2 K
    return {
        'roof'            : 0.001,
        'ceiling'         : 0.001,
        'wall'            : 0.001,
        'floor'           : 0.001,
        'boundary_ceiling': 0.001,
        'boundary_wall'   : 0.001,
        'boundary_floor'  : 0.001,
        'window'          : 0.001,
        'door'            : 0.001,
        'earthfloor_perimeter'     : 0.001
    }[ptype]


def get_max_U(ptype):    # 部位別の熱貫流率の上限値, W/m2 K
    return {
        'roof'            : 1/(0.09+0.0095/0.22+0.04),
        'ceiling'         : 1/(0.09+0.0095/0.22+0.09),
        'wall'            : 1/(0.11+0.0095/0.22+0.04),
        'floor'           : 1/(0.15+0.012 /0.16+0.04),
        'boundary_ceiling': 1/(0.09+0.0095/0.22+0.09),
        'boundary_wall'   : 1/(0.11+0.0095/0.22+0.11),
        'boundary_floor'  : 1/(0.15+0.012 /0.16+0.15),
        'window'          : 6.51,
        'door'            : 6.51,
        'earthfloor_perimeter'     : 100
    }[ptype]


def get_q_std_U(region, parts, l_target):
    return sum(
        (part.area * get_std_U(region, part.ptype) * factor_h.get_h(region,
                                                                                 part.nextspace) if part.ptype in l_target else 0)
               for part in parts)


def get_q_max_U(region, parts, l_target):
    return sum((part.area * get_max_U(part.ptype) * factor_h.get_h(region,
                                                                         part.nextspace) if part.ptype in l_target else 0)
               for part in parts)


def get_q_min_U(region, parts, l_target):
    return sum((part.area * get_min_U(part.ptype) * factor_h.get_h(region,
                                                                         part.nextspace) if part.ptype in l_target else 0)
               for part in parts)


def get_fUs_range(region, std_UA, total_area, qs_std_U, qn_max_U, qn_min_U, l_sunshine_part_type):
    # 日射の当たる部位の熱貫流率補正係数の最小値
    fUs_max = min(
        (std_UA * total_area - qn_min_U) / qs_std_U,
        min(get_max_U(x) / get_std_U(region, x) for x in l_sunshine_part_type)
    )

    # 日射の当たる部位の熱貫流率補正係数の最大値
    fUs_min = max(
        (std_UA * total_area - qn_max_U) / qs_std_U,
        max(get_min_U(x) / get_std_U(region, x) for x in l_sunshine_part_type)
    )

    return fUs_max, fUs_min


def get_fUn_range(region, std_UA, total_area, qs_std_U, qn_std_U, l_sunshine_part_type, l_no_sunshine_part_type):
    # 日射の当たらない部位（床）の熱貫流率補正係数の最小値
    fUn_max = min(
        (std_UA * total_area - qs_std_U * max(
            get_min_U(x) / get_std_U(region, x) for x in l_sunshine_part_type)) / qn_std_U,
        min(get_max_U(x) / get_std_U(region, x) for x in l_no_sunshine_part_type)
    )

    # 日射の当たらない部位（床）の熱貫流率補正係数の最大値
    fUn_min = max(
        (std_UA * total_area - qs_std_U * min(
            get_max_U(x) / get_std_U(region, x) for x in l_sunshine_part_type)) / qn_std_U,
        min(get_min_U(x) / get_std_U(region, x) for x in l_no_sunshine_part_type)
    )

    return fUn_max, fUn_min


def get_fU_and_eta(region, std_UA, total_area, parts, std_etaAH, std_etaAC,
                   fUs_min, fUs_max, fUn_min, fUn_max, q_std_U, qs_std_U, qn_std_U, l_sunshine_part_type):
    q_std = std_UA * total_area

    # A・ηA
    m_H_std = std_etaAH * total_area
    m_C_std = std_etaAC * total_area

    # Σ(A・U・ν)
    sum_AUnu_H = sum((part.area * get_std_U(region, part.ptype) * \
                      nu.get_nu(season=('heating' if region != 8 else 'cooling'), region=region,
                                direction=part.direction) \
                          if (part.ptype in l_sunshine_part_type and part.ptype != 'window') else 0) \
                     for part in parts)
    sum_AUnu_C = sum((part.area * get_std_U(region, part.ptype) * nu.get_nu(season='cooling', region=region,
                                                                            direction=part.direction) \
                          if (part.ptype in l_sunshine_part_type and part.ptype != 'window') else 0) \
                     for part in parts)

    # Σ(A・f・ν)
    sum_Afnu_H = sum((part.area * f.get_f(season='heating', region=region, direction=part.direction) \
                      * nu.get_nu(season=('heating' if region != 8 else 'cooling'), region=region,
                                  direction=part.direction)) \
                         if part.ptype == 'window' else 0 for part in parts)
    sum_Afnu_C = sum((part.area * f.get_f(season='cooling', region=region, direction=part.direction) \
                      * nu.get_nu(season='cooling', region=region,
                                  direction=part.direction)) if part.ptype == 'window' else 0
                     for part in parts)

    # 調整係数を事前に算出
    fUs_for_eta_H_000 = (m_H_std / 100 - 0.00 * sum_Afnu_H) / 0.034 / sum_AUnu_H
    fUs_for_eta_C_000 = (m_C_std / 100 - 0.00 * sum_Afnu_C) / 0.034 / sum_AUnu_C
    fUs_for_eta_H_088 = (m_H_std / 100 - 0.88 * sum_Afnu_H) / 0.034 / sum_AUnu_H
    fUs_for_eta_C_088 = (m_C_std / 100 - 0.88 * sum_Afnu_C) / 0.034 / sum_AUnu_C
    fUs_for_UA = q_std / q_std_U

    # 場合分けのためのη暫定値
    eta_H_temp = (m_H_std / 100 - 0.034 * fUs_for_UA * sum_AUnu_H) / sum_Afnu_H
    eta_C_temp = (m_C_std / 100 - 0.034 * fUs_for_UA * sum_AUnu_C) / sum_Afnu_C

    if eta_C_temp < 0:
        if eta_H_temp < 0:
            fUs = min(fUs_for_eta_H_000, fUs_for_eta_C_000)
        elif eta_H_temp > 0.88:
            fUs = min(fUs_max, fUs_for_UA)
        else:
            fUs = fUs_for_eta_C_000
    elif eta_C_temp > 0.88:
        if eta_H_temp < 0:
            fUs = min(fUs_max, fUs_for_UA)
        elif eta_H_temp > 0.88:
            fUs = max(fUs_for_eta_H_088, fUs_for_eta_C_088)
        else:
            fUs = fUs_for_eta_C_088
    else:
        if eta_H_temp < 0:
            fUs = fUs_for_eta_H_000
        elif eta_H_temp > 0.88:
            fUs = fUs_for_eta_H_088
        else:
            fUs = fUs_for_UA

    # 上下限値の適用
    fUs = max(fUs_min, min(fUs_max, fUs_for_UA))

    # 床の熱貫流率の調整係数
    fUn = max(fUn_min, min(fUn_max, (q_std - fUs * qs_std_U) / qn_std_U))

    # 開口部の日射熱取得率の算出
    eta = {
        'heating': max(0, min(0.88, (m_H_std / 100 - 0.034 * sum_AUnu_H * fUs) / sum_Afnu_H)),
        'cooling': max(0, min(0.88, (m_C_std / 100 - 0.034 * sum_AUnu_C * fUs) / sum_Afnu_C)),
    }
    eta['annual'] = eta['cooling']

    return fUs, fUn, eta


def check_UA_and_etaA(area_skin, l_general_parts, l_windows, l_doors, l_earthfloor_perimeters, part_U, eta, region,
                      parts, l_sunshine_parts, l_no_sunshine_parts):
    # Σ(A・f・ν)
    sum_Afnu = {
        'heating': sum((part.area * f.get_f(season='heating', region=region, direction=part.direction) * \
                        nu.get_nu(season=('heating' if region != 8 else 'cooling'), region=region,
                                  direction=part.direction) \
                            if part.ptype == 'window' else 0) \
                       for part in parts),
        'cooling': sum((part.area * f.get_f(season='cooling', region=region, direction=part.direction) * \
                        nu.get_nu(season='cooling', region=region,
                                  direction=part.direction) if part.ptype == 'window' else 0) \
                       for part in parts)
    }

    # UA値検算
    UA_check = (sum(x['area'] * part_U[x['general_part_type']] * factor_h.get_h(region, x['next_space'])
                    for x in l_general_parts) \
                + sum(x['area'] * part_U['window'] * factor_h.get_h(region, x['next_space']) for x in l_windows) \
                + sum(x['area'] * part_U['window'] * factor_h.get_h(region, x['next_space']) for x in l_doors) \
                + sum(x['length'] * part_U['earthfloor_perimeter'] * factor_h.get_h(region, x['next_space'])
                      for x in l_earthfloor_perimeters)) / area_skin

    # ηA値検算
    eta_check = {
        'heating': (0.034 * sum(x['area'] * part_U[x['general_part_type']] * \
                                (nu.get_nu(region=region, season=('heating' if region != 8 else 'cooling'),
                                           direction=x['direction']) if x['next_space'] == 'outdoor' else 0)
                                for x in l_general_parts) \
                    + 0.034 * sum(x['area'] * part_U['door'] * \
                                  (nu.get_nu(region=region, season=('heating' if region != 8 else 'cooling'),
                                             direction=x['direction']) if x['next_space'] == 'outdoor' else 0)
                                  for x in l_doors) \
                    + eta['heating'] * sum_Afnu['heating']) / area_skin * 100,
        'cooling': (0.034 * sum(x['area'] * part_U[x['general_part_type']] * \
                                nu.get_nu(region=region, season='cooling', direction=x['direction'])
                                for x in l_general_parts) \
                    + 0.034 * sum(
                    x['area'] * part_U['door'] * nu.get_nu(region=region, season='cooling', direction=x['direction'])
                    for x in l_doors) \
                    + eta['cooling'] * sum_Afnu['cooling']) / area_skin * 100,
    }

    return UA_check, eta_check


# 一般部位、窓、ドア、土間床等の外周部のリストを作成
def get_l_parts(l_general_parts, l_windows, l_doors, l_earthfloor_perimeters):
    # 一般部位
    general_parts = [
        Parts(area=p['area'], ptype=p['general_part_type'], nextspace=p['next_space'], direction=p['direction'])
        for p in l_general_parts]

    # 窓
    windows = [Parts(area=p['area'], ptype='window', nextspace=p['next_space'], direction=p['direction']) for p in
               l_windows]

    # ドア
    doors = [Parts(area=p['area'], ptype='door', nextspace=p['next_space'], direction=p['direction']) for p in l_doors]

    # 土間床等の外周部
    earthfloor_perimeters = [
        Parts(area=p['length'], ptype='earthfloor_perimeter', nextspace=p['next_space'], direction=p['direction'])
        for p in l_earthfloor_perimeters]

    return general_parts + windows + doors + earthfloor_perimeters


def calc_adjustment_factor(d):
    region = d['common']['region']
    envelope = d['envelope']
    total_area = get_total_area(envelope)

    # 部位のリスト作成
    parts = get_l_parts(envelope['general_parts'], envelope['windows'], envelope['doors'],
                        envelope['earthfloor_perimeters'])

    # 部位種類のリスト取得
    l_part_type = get_list_part_type()
    l_sunshine_part_type = get_list_sunshine_part_type()
    l_no_sunshine_part_type = get_list_no_sunshine_part_type()

    # 各種設定値の取得
    q_std_U = get_q_std_U(region, parts, l_part_type)
    qs_std_U = get_q_std_U(region, parts, l_sunshine_part_type)
    qn_std_U = get_q_std_U(region, parts, l_no_sunshine_part_type)
    qn_max_U = get_q_max_U(region, parts, l_no_sunshine_part_type)
    qn_min_U = get_q_min_U(region, parts, l_no_sunshine_part_type)

    # 熱貫流率の調整係数の上下限値
    fUs_max, fUs_min = get_fUs_range(region, envelope['index']['u_a'], total_area, qs_std_U, qn_max_U, qn_min_U,
                                     l_sunshine_part_type)
    fUn_max, fUn_min = get_fUn_range(region, envelope['index']['u_a'], total_area, qs_std_U, qn_std_U,
                                     l_sunshine_part_type, l_no_sunshine_part_type)

    # fUs, fUn, ηの算出
    fUs, fUn, eta = get_fU_and_eta(region, envelope['index']['u_a'], total_area, parts,
                                   envelope['index']['eta_a_h'], envelope['index']['eta_a_c'],
                                   fUs_min, fUs_max, fUn_min, fUn_max, q_std_U, qs_std_U, qn_std_U,
                                   l_sunshine_part_type)

    # 部位別のU値の上下限値
    part_U = {x: max(get_min_U(x), min(get_max_U(x),
                                       (fUn if x == 'floor' or x == 'earthfloor_perimeter' else fUs) * get_std_U(region,
                                                                                                                 x))) \
              for x in ['roof', 'ceiling', 'wall', 'floor', 'window', 'door', 'earthfloor_perimeter']}

    # 検算
    UA_check, eta_check = check_UA_and_etaA(total_area, envelope['general_parts'], envelope['windows'],
                                            envelope['doors'], \
                                            envelope['earthfloor_perimeters'], \
                                            part_U, eta, region, parts, l_sunshine_part_type, l_no_sunshine_part_type)

    print("U値{0},開口部η{1},開口部ηH{2},開口部ηC{3}".format(part_U, eta['annual'], eta['heating'], eta['cooling']))
    print("UA計算値{0},ηAH計算値{1},ηAC計算値{2}".format(UA_check, eta_check['heating'], eta_check['cooling']))

    return eta['annual'], eta['heating'], eta['cooling'], part_U