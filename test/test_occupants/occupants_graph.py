# coding:utf-8

import copy
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from heat_load_calc.core import occupants
from heat_load_calc.core.operation_mode import OperationMode


# グラフ作成用辞書の取得
def get_graph_property():

    # 絶対湿度[kg/kgDA]の指定
    d_x_r = {'default': 0.001, 'min': 0.001, 'max': 0.1, 'list': [0.001 * x for x in range(1, 100)]}

    # 運転状態の指定
    d_operation_mode = {'default': OperationMode(4)}

    # 放射暖房の有無の指定
    d_radiative_heating = {'default': False}

    # 放射冷房の有無の指定
    d_radiative_cooling = {'default': False}

    # 空気温度の指定
    d_theta_r = {'default': 20.0, 'min': 0, 'max': 50, 'list': list(range(0, 50, 1))}

    # 在室者の着衣温度の指定
    d_theta_cl = {'default': 27.0, 'min': 0, 'max': 50, 'list': list(range(0, 50, 1))}

    # 在室者の平均放射温度の指定
    d_theta_mrt = {'default': 20.0, 'min': 0, 'max': 50, 'list': list(range(0, 50, 1))}

    # 空調需要の有無の指定
    d_ac_demand = {'default': True}

    # デフォルト辞書作成
    len_theta_r_list = len(d_theta_r['list'])
    d_default = {
        'title': 'title',
        'x_axis': 'theta_r',
        'x_label': 'room temperature, mrt[degree]',
        'x_min': d_theta_r['min'],
        'x_max': d_theta_r['max'],
        'x_r': [d_x_r['default']] * len_theta_r_list,
        'operation_mode': [d_operation_mode['default']] * len_theta_r_list,
        'radiative_heating': [d_radiative_heating['default']] * len_theta_r_list,
        'radiative_cooling': [d_radiative_cooling['default']] * len_theta_r_list,
        'theta_r': d_theta_r['list'],
        'theta_cl': [d_theta_cl['default']] * len_theta_r_list,
        'theta_mrt': d_theta_mrt['list'],
        'ac_demand': [d_ac_demand['default']] * len_theta_r_list
    }

    d_graph_property = {}
    for i in range(0, 11):
        d_graph_property['graph' + str(i + 101)[-2:]] = copy.deepcopy(d_default)

    # グラフ1　空調モード1
    d_graph_property['graph01']['operation_mode'] = [OperationMode(1)] * len_theta_r_list
    d_graph_property['graph01']['title'] = 'operation_mode: COOLING'

    # グラフ2　空調モード2
    d_graph_property['graph02']['operation_mode'] = [OperationMode(2)] * len_theta_r_list
    d_graph_property['graph02']['title'] = 'operation_mode: HEATING'

    # グラフ3　空調モード3
    d_graph_property['graph03']['operation_mode'] = [OperationMode(3)] * len_theta_r_list
    d_graph_property['graph03']['title'] = 'operation_mode: STOP_OPEN'

    # グラフ4　空調モード4
    d_graph_property['graph04']['operation_mode'] = [OperationMode(4)] * len_theta_r_list
    d_graph_property['graph04']['title'] = 'operation_mode: STOP_CLOSE'

    # グラフ5　放射暖房あり
    d_graph_property['graph05']['radiative_heating'] = [True] * len_theta_r_list
    d_graph_property['graph05']['title'] = 'radiative_heating: True'

    # グラフ6　放射冷房あり
    d_graph_property['graph06']['radiative_cooling'] = [True] * len_theta_r_list
    d_graph_property['graph06']['title'] = 'radiative_cooling: True'

    # グラフ7　空調需要なし
    d_graph_property['graph07']['ac_demand'] = [False] * len_theta_r_list
    d_graph_property['graph07']['title'] = 'ac_demand: False'

    # グラフ8　湿度変更
    len_x_r_list = len(d_x_r['list'])
    d_graph_property['graph08'] = {
        'title': 'horizontal axis: x_r',
        'x_axis': 'x_r',
        'x_label': 'x r[kg/kg(DA)]',
        'x_min': d_x_r['min'],
        'x_max': d_x_r['max'],
        'x_r': d_x_r['list'],
        'operation_mode': [d_operation_mode['default']] * len_x_r_list,
        'radiative_heating': [d_radiative_heating['default']] * len_x_r_list,
        'radiative_cooling': [d_radiative_cooling['default']] * len_x_r_list,
        'theta_r': [d_theta_r['default']] * len_x_r_list,
        'theta_cl': [d_theta_cl['default']] * len_x_r_list,
        'theta_mrt': [d_theta_mrt['default']] * len_x_r_list,
        'ac_demand': [d_ac_demand['default']] * len_x_r_list
    }

    # グラフ9　着衣温度変更
    len_theta_cl_list = len(d_theta_cl['list'])
    d_graph_property['graph09'] = {
        'title': 'horizontal axis: theta_cl',
        'x_axis': 'theta_cl',
        'x_label': 'theta cl[degree]',
        'x_min': d_theta_cl['min'],
        'x_max': d_theta_cl['max'],
        'x_r': [d_x_r['default']] * len_theta_cl_list,
        'operation_mode': [d_operation_mode['default']] * len_theta_cl_list,
        'radiative_heating': [d_radiative_heating['default']] * len_theta_cl_list,
        'radiative_cooling': [d_radiative_cooling['default']] * len_theta_cl_list,
        'theta_r': [d_theta_r['default']] * len_theta_cl_list,
        'theta_cl': d_theta_cl['list'],
        'theta_mrt': [d_theta_mrt['default']] * len_theta_cl_list,
        'ac_demand': [d_ac_demand['default']] * len_theta_cl_list
    }

    # グラフ10　室温変更
    d_graph_property['graph10']['theta_mrt'] = [d_theta_mrt['default']] * len_theta_r_list
    d_graph_property['graph10']['title'] = 'horizontal axis: theta_r'
    d_graph_property['graph10']['x_label'] = 'room temperature[degree]'

    # グラフ11　MRT変更
    d_graph_property['graph11']['theta_r'] = [d_theta_r['default']] * len_theta_r_list
    d_graph_property['graph11']['title'] = 'horizontal axis: theta_mrt'
    d_graph_property['graph11']['x_axis'] = 'theta_mrt'
    d_graph_property['graph11']['x_label'] = 'mrt[degree]'

    return d_graph_property


# グラフ用のデータ取得
def get_graph_data(d):

    # データ格納用の辞書
    d_graph_data = {}

    for key in d.keys():

        # 人体周りの総合熱伝達率, 対流熱伝達率, 放射熱伝達率, 運転モード, 着衣量, 目標作用温度の取得
        arr = occupants.calc_operation(
            x_r_is_n=np.array(d[key]['x_r']),
            operation_mode_is_n_mns=np.array(d[key]['operation_mode']),
            is_radiative_heating_is=np.array(d[key]['radiative_heating']),
            is_radiative_cooling_is=np.array(d[key]['radiative_cooling']),
            theta_r_is_n=np.array(d[key]['theta_r']),
            theta_cl_is_n=np.array(d[key]['theta_cl']),
            theta_mrt_is_n=np.array(d[key]['theta_mrt']),
            ac_demand_is_n=np.array(d[key]['ac_demand'])
        )

        # 運転モード, 着衣量, 目標作用温度のデータ格納
        d_graph_data[key] = {
            'operation_mode': copy.deepcopy([om.value for om in arr[3]]),
            'clo': copy.deepcopy(arr[6]),
            'theta_ot_target': copy.deepcopy(arr[7])
        }

    return d_graph_data


# グラフ作成
def plot(d_graph_property, d_graph_data):

    font_size = 14

    fig = plt.figure(figsize=(5, 5), dpi=55)

    lng_i = 1
    for key in d_graph_property.keys():

        ax1 = fig.add_subplot(3, 4, lng_i)
        ax2 = ax1.twinx()

        # データ系列
        ax1.plot(d_graph_property[key][d_graph_property[key]['x_axis']],
                 d_graph_data[key]['operation_mode'], '_', c='red')
        ax1.plot(d_graph_property[key][d_graph_property[key]['x_axis']],
                 d_graph_data[key]['clo'], '_', c='blue')
        ax2.plot(d_graph_property[key][d_graph_property[key]['x_axis']],
                 d_graph_data[key]['theta_ot_target'], c='grey', linestyle='solid')

        # 軸範囲
        plt.xlim([d_graph_property[key]['x_min'], d_graph_property[key]['x_max']])
        plt.ylim(0, 40)

        # グラフトイトル
        plt.title(d_graph_property[key]['title'], fontsize=font_size)

        # 凡例
        ax1.set_xlabel(d_graph_property[key]['x_label'], fontsize=font_size)
        ax1.legend(['operation_mode', 'clo'], fontsize=font_size)
        ax2.legend(['theta_ot_target'], fontsize=font_size)

        # y軸タイトル
        ax1.set_ylabel('operation mode, clo[Cl]', fontsize=font_size)
        ax2.set_ylabel('OT target[degree]', fontsize=font_size)

        lng_i += 1

    # デフォルト値の表示
    ax1 = fig.add_subplot(3, 4, lng_i)
    ax1.xaxis.set_major_locator(mpl.ticker.LinearLocator(0))
    ax1.yaxis.set_major_locator(mpl.ticker.LinearLocator(0))
    plt.text(0.025, 0.9, r'default', fontsize=font_size)
    plt.text(0.025, 0.8, r' x_r:0.001kg/kg(DA)', fontsize=font_size)
    plt.text(0.025, 0.7, r' operation_mode:STOP_CLOSE', fontsize=font_size)
    plt.text(0.025, 0.6, r' radiative_heating:False', fontsize=font_size)
    plt.text(0.025, 0.5, r' radiative_cooling:False', fontsize=font_size)
    plt.text(0.025, 0.4, r' theta_r:20.0°C', fontsize=font_size)
    plt.text(0.025, 0.3, r' theta_cl:27.0°C', fontsize=font_size)
    plt.text(0.025, 0.2, r' mrt:20.0°C', fontsize=font_size)
    plt.text(0.025, 0.1, r' ac_demand:True', fontsize=font_size)
    plt.text(0.625, 0.9, r'operation_mode', fontsize=font_size)
    plt.text(0.625, 0.8, r' 1:COOLING', fontsize=font_size)
    plt.text(0.625, 0.7, r' 2:HEATING', fontsize=font_size)
    plt.text(0.625, 0.6, r' 3:STOP_OPEN', fontsize=font_size)
    plt.text(0.625, 0.5, r' 4:STOP_CLOSE', fontsize=font_size)

    # グラフ描画
    plt.show()


# 実行
def execute():

    # グラフ作成用辞書の取得
    d_graph_property = get_graph_property()

    # グラフ用のデータ取得
    d_graph_data = get_graph_data(d_graph_property)

    # グラフ作成
    plot(d_graph_property, d_graph_data)


if __name__ == '__main__':

    execute()
