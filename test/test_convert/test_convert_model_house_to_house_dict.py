import unittest
from typing import List

from heat_load_calc.external.factor_h import NextSpace
from heat_load_calc.convert.ees_house import GeneralPartType
from heat_load_calc.convert.ees_house import GeneralPartNoSpec
from heat_load_calc.convert.ees_house import DoorNoSpec
from heat_load_calc.convert.ees_house import WindowNoSpec
from heat_load_calc.convert.ees_house import EarthfloorPerimeterNoSpec
from heat_load_calc.convert.ees_house import EarthfloorCenter
from heat_load_calc.convert import model_house
from heat_load_calc.external.factor_nu import Direction


class ConvertModelHouseToHouseDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print('\n testing convert model house')

    def setUp(self):

        mh1_input = {
            'house_type': 'detached',
            'floor_ins_type': 'floor',
            'bath_ins_type': 'base',
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843,
            'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 3.185,
            'a_evp_ef_bath': 3.3124000000000002,
            'a_evp_f_bath': 0.0,
            'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
            'l_base_bath_inside': 3.64,
            'f_s': [1.0800250894877579, 1.0400241602474705],
            'l_prm': [30.805513843979707, 26.030553554896883],
            'l_ms': [10.610634821709455, 8.295602321670247],
            'l_os': [4.792122100280398, 4.719674455778196],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 5.7967,
            'a_evp_f_other': 45.05075762711864,
            'a_evp_f_total': 45.05075762711864,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 3.64, 3.185, 0.0),
            'l_base_total_inside': 6.825,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.5733,
            'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
            'a_evp_base_bath_inside': 1.82,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 1.2376, 1.1557, 0.0),
            'a_evp_base_total_inside': 2.3933,
            'a_evp_srf': (
                [30.77084098295742, 22.398126268509667],
                [13.897154090813155, 12.74312103060113],
                [30.77084098295742, 22.398126268509667],
                [13.897154090813155, 12.74312103060113]
            ),
            'a_evp_total_not_base': 261.3134,
            'a_evp_total': 266.1,
            'a_evp_open_total': 36.583876000000004,
            'a_evp_window_total': 33.073876000000006,
            'a_evp_window': (22.695293711200005, 2.3846264596, 3.628204197200001, 4.365751632000001),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.473673540267082, 22.365648661814284, 47.92076305426709, 22.274523489414282)
        }

        mh2_input = {
            'house_type': 'detached',
            'floor_ins_type': 'floor',
            'bath_ins_type': 'floor',
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843,
            'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 3.185, 'a_evp_ef_bath': 0.0,
            'a_evp_f_bath': 3.3124000000000002,
            'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.0800250894877574, 1.04002416024747],
            'l_prm': [30.805513843979693, 26.030553554896873],
            'l_ms': [10.610634821709443, 8.295602321670234],
            'l_os': [4.7921221002804035, 4.719674455778203],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 2.4843,
            'a_evp_f_other': 45.05075762711864,
            'a_evp_f_total': 48.36315762711864,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_total_inside': 3.185,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.5733,
            'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_total_inside': 0.5733,
            'a_evp_srf': (
                [30.770840982957385, 22.398126268509635],
                [13.897154090813169, 12.743121030601149],
                [30.770840982957385, 22.398126268509635],
                [13.897154090813169, 12.743121030601149]
            ),
            'a_evp_total_not_base': 261.3134,
            'a_evp_total': 262.46000000000004,
            'a_evp_open_total': 36.583876000000004,
            'a_evp_window_total': 33.073876000000006,
            'a_evp_window': (22.695293711200005, 2.3846264596, 3.628204197200001, 4.365751632000001),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.47367354026702, 22.36564866181432, 47.92076305426703, 22.274523489414317)
        }

        mh3_input = {
            'house_type': 'detached',
            'floor_ins_type': 'floor',
            'bath_ins_type': 'not_exist',
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843, 'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 3.185,
            'a_evp_ef_bath': 0.0,
            'a_evp_f_bath': 3.3124000000000002,
            'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.0800250894877574, 1.04002416024747],
            'l_prm': [30.805513843979693, 26.030553554896873],
            'l_ms': [10.610634821709443, 8.295602321670234],
            'l_os': [4.7921221002804035, 4.719674455778203],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 2.4843,
            'a_evp_f_other': 45.05075762711864,
            'a_evp_f_total': 48.36315762711864,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_total_inside': 3.185,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.5733,
            'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_total_inside': 0.5733,
            'a_evp_srf': (
                [30.770840982957385, 22.398126268509635],
                [13.897154090813169, 12.743121030601149],
                [30.770840982957385, 22.398126268509635],
                [13.897154090813169, 12.743121030601149]
            ),
            'a_evp_total_not_base': 261.3134,
            'a_evp_total': 262.46000000000004,
            'a_evp_open_total': 36.583876000000004,
            'a_evp_window_total': 33.073876000000006,
            'a_evp_window': (22.695293711200005, 2.3846264596, 3.628204197200001, 4.365751632000001),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.47367354026702, 22.36564866181432, 47.92076305426703, 22.274523489414317)
        }

        mh4_input = {
            'house_type': 'detached',
            'floor_ins_type': 'base',
            'bath_ins_type': None,
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843,
            'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 0.0,
            'a_evp_ef_bath': 3.3124000000000002,
            'a_evp_f_bath': 0.0,
            'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.0799821595540935, 1.0399828203113493],
            'l_prm': [30.80428935514265, 26.029518866028788],
            'l_ms': [10.60951823652745, 8.294401932913006],
            'l_os': [4.7926264410438755, 4.720357500101388],
            'a_evp_ef_other': 45.05075762711864,
            'a_evp_ef_total': 50.847457627118644,
            'a_evp_f_other': 0.0,
            'a_evp_f_total': 0.0,
            'l_base_other_outside': (10.60951823652745, 1.1526264410438751, 7.424518236527449, 4.7926264410438755),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (10.60951823652745, 4.7926264410438755, 10.60951823652745, 4.7926264410438755),
            'l_base_total_inside': 0.0,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.0,
            'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (5.304759118263725, 0.5763132205219376, 3.7122591182637246, 2.3963132205219377),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (5.304759118263725, 1.8139132205219375, 4.867959118263724, 2.3963132205219377),
            'a_evp_base_total_inside': 0.0,
            'a_evp_srf': (
                [30.767602885929602, 22.394885218865117],
                [13.898616679027239, 12.744965250273747],
                [30.767602885929602, 22.394885218865117],
                [13.898616679027239, 12.744965250273747]
            ),
            'a_evp_total_not_base': 261.3070553224287,
            'a_evp_total': 275.69000000000005,
            'a_evp_open_total': 36.582987745140024,
            'a_evp_window_total': 33.072987745140026,
            'a_evp_window': (22.694684190715087, 2.3845624164245955, 3.628106755641861, 4.365634382358484),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.46780391407963, 22.36901951287639, 47.91438134915286, 22.277947546942503)
        }

        mh5_input = {
            'house_type': 'attached',
            'floor_ins_type': None,
            'bath_ins_type': None,
            'a_f': [70.0],
            'a_evp_ef_etrc': 0.0,
            'a_evp_f_etrc': 1.0,
            'l_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_etrc_inside': 0.0,
            'a_evp_ef_bath': 0.0,
            'a_evp_f_bath': 2.8665000000000003,
            'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.0481728036502156],
            'l_prm': [35.07857142857143],
            'l_ms': [6.1415949424661225],
            'l_os': [11.397690771819592],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 0.0,
            'a_evp_f_other': 66.1335,
            'a_evp_f_total': 70.0,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_total_inside': 0.0,
            'a_evp_roof': 70.0,
            'a_evp_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_etrc_inside': 0.0,
            'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_total_inside': 0.0,
            'a_evp_srf': ([17.19646583890514], [31.913534161094855], [17.19646583890514], [31.913534161094855]),
            'a_evp_total_not_base': 238.22,
            'a_evp_total': 238.22,
            'a_evp_open_total': 14.019247,
            'a_evp_window_total': 12.264247000000001,
            'a_evp_window': (7.763268351000001, 1.8604862699000002, 2.6404923791, 0.0),
            'a_evp_door': (0.0, 0.0, 1.755, 0.0),
            'a_evp_wall': (9.43319748790514, 30.053047891194854, 12.800973459805142, 31.913534161094855)
        }

        mh6_input = {
            'house_type': 'detached',
            'floor_ins_type': 'floor',
            'bath_ins_type': 'base',
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843,
            'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 3.185,
            'a_evp_ef_bath': 3.3124000000000002,
            'a_evp_f_bath': 0.0,
            'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
            'l_base_bath_inside': 3.64,
            'f_s': [1.08, 1.04],
            'l_prm': [30.80479821749104, 26.029948852968104],
            'l_ms': [10.609982280729707, 8.29490083566609],
            'l_os': [4.7924168280158135, 4.720073590817963],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 5.7967,
            'a_evp_f_other': 45.05075762711864,
            'a_evp_f_total': 45.05075762711864,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 3.64, 3.185, 0.0),
            'l_base_total_inside': 6.825,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.5733,
            'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
            'a_evp_base_bath_inside': 1.82,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 1.2376, 1.1557, 0.0),
            'a_evp_base_total_inside': 2.3933,
            'a_evp_srf': (
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085],
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085]
            ),
            'a_evp_total_not_base': 261.30969198797516,
            'a_evp_total': 266.0962919879752,
            'a_evp_open_total': 36.58335687831652,
            'a_evp_window_total': 33.073356878316524,
            'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
        }

        mh7_input = {
            'house_type': 'detached',
            'floor_ins_type': 'floor',
            'bath_ins_type': 'floor',
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843,
            'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 3.185,
            'a_evp_ef_bath': 0.0,
            'a_evp_f_bath': 3.3124000000000002,
            'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.08, 1.04],
            'l_prm': [30.80479821749104, 26.029948852968104],
            'l_ms': [10.609982280729707, 8.29490083566609],
            'l_os': [4.7924168280158135, 4.720073590817963],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 2.4843,
            'a_evp_f_other': 45.05075762711864,
            'a_evp_f_total': 48.36315762711864,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_total_inside': 3.185,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.5733,
            'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_total_inside': 0.5733,
            'a_evp_srf': (
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085],
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085]
            ),
            'a_evp_total_not_base': 261.30969198797516,
            'a_evp_total': 262.4562919879752,
            'a_evp_open_total': 36.58335687831652,
            'a_evp_window_total': 33.073356878316524,
            'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
        }

        mh8_input = {
            'house_type': 'detached',
            'floor_ins_type': 'floor',
            'bath_ins_type': 'not_exist',
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843,
            'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 3.185,
            'a_evp_ef_bath': 0.0,
            'a_evp_f_bath': 3.3124000000000002,
            'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.08, 1.04],
            'l_prm': [30.80479821749104, 26.029948852968104],
            'l_ms': [10.609982280729707, 8.29490083566609],
            'l_os': [4.7924168280158135, 4.720073590817963],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 2.4843,
            'a_evp_f_other': 45.05075762711864,
            'a_evp_f_total': 48.36315762711864,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_total_inside': 3.185,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.5733,
            'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_total_inside': 0.5733,
            'a_evp_srf': (
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085],
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085]
            ),
            'a_evp_total_not_base': 261.30969198797516,
            'a_evp_total': 262.4562919879752,
            'a_evp_open_total': 36.58335687831652,
            'a_evp_window_total': 33.073356878316524,
            'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
        }

        mh9_input = {
            'house_type': 'detached',
            'floor_ins_type': 'base',
            'bath_ins_type': None,
            'a_f': [50.847457627118644, 39.152542372881356],
            'a_evp_ef_etrc': 2.4843,
            'a_evp_f_etrc': 0.0,
            'l_base_etrc_outside': (0.0, 1.82, 1.365, 0.0),
            'l_base_etrc_inside': 0.0,
            'a_evp_ef_bath': 3.3124000000000002,
            'a_evp_f_bath': 0.0,
            'l_base_bath_outside': (0.0, 1.82, 1.82, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.08, 1.04],
            'l_prm': [30.80479821749104, 26.029948852968104],
            'l_ms': [10.609982280729707, 8.29490083566609],
            'l_os': [4.7924168280158135, 4.720073590817963],
            'a_evp_ef_other': 45.05075762711864,
            'a_evp_ef_total': 50.847457627118644,
            'a_evp_f_other': 0.0,
            'a_evp_f_total': 0.0,
            'l_base_other_outside': (10.609982280729707, 1.1524168280158131, 7.424982280729706, 4.7924168280158135),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (10.609982280729707, 4.7924168280158135, 10.609982280729707, 4.7924168280158135),
            'l_base_total_inside': 0.0,
            'a_evp_roof': 50.847457627118644,
            'a_evp_base_etrc_outside': (0.0, 0.3276, 0.2457, 0.0),
            'a_evp_base_etrc_inside': 0.0,
            'a_evp_base_bath_outside': (0.0, 0.91, 0.91, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (5.304991140364853, 0.5762084140079066, 3.712491140364853, 2.3962084140079067),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (5.304991140364853, 1.8138084140079065, 4.868191140364853, 2.3962084140079067),
            'a_evp_base_total_inside': 0.0,
            'a_evp_srf': (
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085],
                [30.768948614116148, 22.396232256298443],
                [13.898008801245858, 12.7441986952085]
            ),
            'a_evp_total_not_base': 261.30969198797516,
            'a_evp_total': 275.6928910967207,
            'a_evp_open_total': 36.58335687831652,
            'a_evp_window_total': 33.073356878316524,
            'a_evp_window': (22.6949374899008, 2.3845890309266213, 3.628147249551323, 4.365683107937781),
            'a_evp_door': (0.0, 1.89, 1.62, 0.0),
            'a_evp_wall': (30.47024338051379, 22.367618465527734, 47.917033620863265, 22.276524388516577)
        }

        mh10_input = {
            'house_type': 'attached',
            'floor_ins_type': None,
            'bath_ins_type': None,
            'a_f': [70.0],
            'a_evp_ef_etrc': 0.0,
            'a_evp_f_etrc': 1.0,
            'l_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_etrc_inside': 0.0,
            'a_evp_ef_bath': 0.0,
            'a_evp_f_bath': 2.8665000000000003,
            'l_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_bath_inside': 0.0,
            'f_s': [1.048215],
            'l_prm': [35.079983588536635],
            'l_ms': [6.140770148791126],
            'l_os': [11.39922164547719],
            'a_evp_ef_other': 0.0,
            'a_evp_ef_total': 0.0,
            'a_evp_f_other': 66.1335,
            'a_evp_f_total': 70.0,
            'l_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_other_inside': 0.0,
            'l_base_total_outside': (0.0, 0.0, 0.0, 0.0),
            'l_base_total_inside': 0.0,
            'a_evp_roof': 70.0,
            'a_evp_base_etrc_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_etrc_inside': 0.0,
            'a_evp_base_bath_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_bath_inside': 0.0,
            'a_evp_base_other_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_other_inside': 0.0,
            'a_evp_base_total_outside': (0.0, 0.0, 0.0, 0.0),
            'a_evp_base_total_inside': 0.0,
            'a_evp_srf': ([17.19415641661515], [31.917820607336132], [17.19415641661515], [31.917820607336132]),
            'a_evp_total_not_base': 238.22395404790257,
            'a_evp_total': 238.22395404790257,
            'a_evp_open_total': 14.019479695719065,
            'a_evp_window_total': 12.264479695719064,
            'a_evp_window': (7.763415647390167, 1.8605215698405821, 2.6405424784883142, 0.0),
            'a_evp_door': (0.0, 0.0, 1.755, 0.0),
            'a_evp_wall': (9.430740769224983, 30.05729903749555, 12.798613938126838, 31.917820607336132)
        }

        self.gps1, self.ws1, self.ds1, self.eps1, self.ecs1 = model_house.get_model_house_no_spec(**mh1_input)
        self.gps2, self.ws2, self.ds2, self.eps2, self.ecs2 = model_house.get_model_house_no_spec(**mh2_input)
        self.gps3, self.ws3, self.ds3, self.eps3, self.ecs3 = model_house.get_model_house_no_spec(**mh3_input)
        self.gps4, self.ws4, self.ds4, self.eps4, self.ecs4 = model_house.get_model_house_no_spec(**mh4_input)
        self.gps5, self.ws5, self.ds5, self.eps5, self.ecs5 = model_house.get_model_house_no_spec(**mh5_input)
        self.gps6, self.ws6, self.ds6, self.eps6, self.ecs6 = model_house.get_model_house_no_spec(**mh6_input)
        self.gps7, self.ws7, self.ds7, self.eps7, self.ecs7 = model_house.get_model_house_no_spec(**mh7_input)
        self.gps8, self.ws8, self.ds8, self.eps8, self.ecs8 = model_house.get_model_house_no_spec(**mh8_input)
        self.gps9, self.ws9, self.ds9, self.eps9, self.ecs9 = model_house.get_model_house_no_spec(**mh9_input)
        self.gps10, self.ws10, self.ds10, self.eps10, self.ecs10 = model_house.get_model_house_no_spec(**mh10_input)

    def test_general_parts_number(self):

        self.assertEqual(len(self.gps1), 9)
        self.assertEqual(len(self.gps2), 9)
        self.assertEqual(len(self.gps3), 9)
        self.assertEqual(len(self.gps4), 9)
        self.assertEqual(len(self.gps5), 6)
        self.assertEqual(len(self.gps6), 9)
        self.assertEqual(len(self.gps7), 9)
        self.assertEqual(len(self.gps8), 9)
        self.assertEqual(len(self.gps9), 9)
        self.assertEqual(len(self.gps10), 6)

    def test_windows_number(self):

        self.assertEqual(len(self.ws1), 4)
        self.assertEqual(len(self.ws2), 4)
        self.assertEqual(len(self.ws3), 4)
        self.assertEqual(len(self.ws4), 4)
        self.assertEqual(len(self.ws5), 3)
        self.assertEqual(len(self.ws6), 4)
        self.assertEqual(len(self.ws7), 4)
        self.assertEqual(len(self.ws8), 4)
        self.assertEqual(len(self.ws9), 4)
        self.assertEqual(len(self.ws10), 3)

    def test_doors_number(self):

        self.assertEqual(len(self.ds1), 2)
        self.assertEqual(len(self.ds2), 2)
        self.assertEqual(len(self.ds3), 2)
        self.assertEqual(len(self.ds4), 2)
        self.assertEqual(len(self.ds5), 1)
        self.assertEqual(len(self.ds6), 2)
        self.assertEqual(len(self.ds7), 2)
        self.assertEqual(len(self.ds8), 2)
        self.assertEqual(len(self.ds9), 2)
        self.assertEqual(len(self.ds10), 1)

    def test_earthfloor_perimeters_number(self):

        self.assertEqual(len(self.eps1), 3)
        self.assertEqual(len(self.eps2), 3)
        self.assertEqual(len(self.eps3), 3)
        self.assertEqual(len(self.eps4), 4)
        self.assertEqual(len(self.eps5), 0)
        self.assertEqual(len(self.eps6), 3)
        self.assertEqual(len(self.eps7), 3)
        self.assertEqual(len(self.eps8), 3)
        self.assertEqual(len(self.eps9), 4)
        self.assertEqual(len(self.eps10), 0)

    def test_earthfloor_centers_number(self):

        self.assertEqual(len(self.ecs1), 1)
        self.assertEqual(len(self.ecs2), 1)
        self.assertEqual(len(self.ecs3), 1)
        self.assertEqual(len(self.ecs4), 1)
        self.assertEqual(len(self.ecs5), 0)
        self.assertEqual(len(self.ecs6), 1)
        self.assertEqual(len(self.ecs7), 1)
        self.assertEqual(len(self.ecs8), 1)
        self.assertEqual(len(self.ecs9), 1)
        self.assertEqual(len(self.ecs10), 0)

    def test_roof(self):

        def get_roof_number(gps: List[GeneralPartNoSpec]):
            return len([s for s in gps if s.general_part_type == GeneralPartType.ROOF])

        self.assertEqual(get_roof_number(self.gps1), 0)
        self.assertEqual(get_roof_number(self.gps2), 0)
        self.assertEqual(get_roof_number(self.gps3), 0)
        self.assertEqual(get_roof_number(self.gps4), 0)
        self.assertEqual(get_roof_number(self.gps5), 0)
        self.assertEqual(get_roof_number(self.gps6), 0)
        self.assertEqual(get_roof_number(self.gps7), 0)
        self.assertEqual(get_roof_number(self.gps8), 0)
        self.assertEqual(get_roof_number(self.gps9), 0)
        self.assertEqual(get_roof_number(self.gps10), 0)

    def test_ceiling(self):

        def get_ceiling_number(gps: List[GeneralPartNoSpec]):
            return len([s for s in gps if s.general_part_type == GeneralPartType.CEILING])

        self.assertEqual(get_ceiling_number(self.gps1), 1)
        self.assertEqual(get_ceiling_number(self.gps2), 1)
        self.assertEqual(get_ceiling_number(self.gps3), 1)
        self.assertEqual(get_ceiling_number(self.gps4), 1)
        self.assertEqual(get_ceiling_number(self.gps5), 0)
        self.assertEqual(get_ceiling_number(self.gps6), 1)
        self.assertEqual(get_ceiling_number(self.gps7), 1)
        self.assertEqual(get_ceiling_number(self.gps8), 1)
        self.assertEqual(get_ceiling_number(self.gps9), 1)
        self.assertEqual(get_ceiling_number(self.gps10), 0)

        def get_ceiling_next_space_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.CEILING and s.next_space == key])

        self.assertEqual(get_ceiling_next_space_number(self.gps1, NextSpace.OUTDOOR), 1)
        self.assertEqual(get_ceiling_next_space_number(self.gps2, NextSpace.OUTDOOR), 1)
        self.assertEqual(get_ceiling_next_space_number(self.gps3, NextSpace.OUTDOOR), 1)
        self.assertEqual(get_ceiling_next_space_number(self.gps4, NextSpace.OUTDOOR), 1)
        self.assertEqual(get_ceiling_next_space_number(self.gps6, NextSpace.OUTDOOR), 1)
        self.assertEqual(get_ceiling_next_space_number(self.gps7, NextSpace.OUTDOOR), 1)
        self.assertEqual(get_ceiling_next_space_number(self.gps8, NextSpace.OUTDOOR), 1)
        self.assertEqual(get_ceiling_next_space_number(self.gps9, NextSpace.OUTDOOR), 1)

        def get_ceiling_direction_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.CEILING and s.direction == key])

        self.assertEqual(get_ceiling_direction_number(self.gps1, Direction.TOP), 1)
        self.assertEqual(get_ceiling_direction_number(self.gps2, Direction.TOP), 1)
        self.assertEqual(get_ceiling_direction_number(self.gps3, Direction.TOP), 1)
        self.assertEqual(get_ceiling_direction_number(self.gps4, Direction.TOP), 1)
        self.assertEqual(get_ceiling_direction_number(self.gps6, Direction.TOP), 1)
        self.assertEqual(get_ceiling_direction_number(self.gps7, Direction.TOP), 1)
        self.assertEqual(get_ceiling_direction_number(self.gps8, Direction.TOP), 1)
        self.assertEqual(get_ceiling_direction_number(self.gps9, Direction.TOP), 1)

        def get_ceiling_area(gps: List[GeneralPartNoSpec]):
            return sorted([s.area for s in gps if s.general_part_type == GeneralPartType.CEILING])

        self.assertAlmostEqual(get_ceiling_area(self.gps1)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.gps2)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.gps3)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.gps4)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.gps6)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.gps7)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.gps8)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.gps9)[0], 50.847457627118644)

    def test_wall(self):

        def get_wall_number(gps: List[GeneralPartNoSpec]):
            return len([s for s in gps if s.general_part_type == GeneralPartType.WALL])

        self.assertEqual(get_wall_number(self.gps1), 7)
        self.assertEqual(get_wall_number(self.gps2), 7)
        self.assertEqual(get_wall_number(self.gps3), 7)
        self.assertEqual(get_wall_number(self.gps4), 8)
        self.assertEqual(get_wall_number(self.gps5), 3)
        self.assertEqual(get_wall_number(self.gps6), 7)
        self.assertEqual(get_wall_number(self.gps7), 7)
        self.assertEqual(get_wall_number(self.gps8), 7)
        self.assertEqual(get_wall_number(self.gps9), 8)
        self.assertEqual(get_wall_number(self.gps10), 3)

        def get_wall_next_space_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.WALL and s.next_space == key])

        self.assertEqual(get_wall_next_space_number(self.gps1, NextSpace.OUTDOOR), 6)
        self.assertEqual(get_wall_next_space_number(self.gps1, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_wall_next_space_number(self.gps2, NextSpace.OUTDOOR), 6)
        self.assertEqual(get_wall_next_space_number(self.gps2, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_wall_next_space_number(self.gps3, NextSpace.OUTDOOR), 6)
        self.assertEqual(get_wall_next_space_number(self.gps3, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_wall_next_space_number(self.gps4, NextSpace.OUTDOOR), 8)
        self.assertEqual(get_wall_next_space_number(self.gps5, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_wall_next_space_number(self.gps5, NextSpace.OPEN_SPACE), 1)
        self.assertEqual(get_wall_next_space_number(self.gps6, NextSpace.OUTDOOR), 6)
        self.assertEqual(get_wall_next_space_number(self.gps6, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_wall_next_space_number(self.gps7, NextSpace.OUTDOOR), 6)
        self.assertEqual(get_wall_next_space_number(self.gps7, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_wall_next_space_number(self.gps8, NextSpace.OUTDOOR), 6)
        self.assertEqual(get_wall_next_space_number(self.gps8, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_wall_next_space_number(self.gps9, NextSpace.OUTDOOR), 8)
        self.assertEqual(get_wall_next_space_number(self.gps10, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_wall_next_space_number(self.gps10, NextSpace.OPEN_SPACE), 1)

        def get_wall_direction_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.WALL and s.direction == key])

        self.assertEqual(get_wall_direction_number(self.gps1, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps1, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps1, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps1, Direction.SE), 1)
        self.assertEqual(get_wall_direction_number(self.gps1, Direction.HORIZONTAL), 1)
        self.assertEqual(get_wall_direction_number(self.gps2, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps2, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps2, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps2, Direction.SE), 1)
        self.assertEqual(get_wall_direction_number(self.gps2, Direction.HORIZONTAL), 1)
        self.assertEqual(get_wall_direction_number(self.gps3, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps3, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps3, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps3, Direction.SE), 1)
        self.assertEqual(get_wall_direction_number(self.gps3, Direction.HORIZONTAL), 1)
        self.assertEqual(get_wall_direction_number(self.gps4, Direction.SW), 2)
        self.assertEqual(get_wall_direction_number(self.gps4, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps4, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps4, Direction.SE), 2)
        self.assertEqual(get_wall_direction_number(self.gps5, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps5, Direction.NW), 1)
        self.assertEqual(get_wall_direction_number(self.gps5, Direction.HORIZONTAL), 1)
        self.assertEqual(get_wall_direction_number(self.gps6, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps6, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps6, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps6, Direction.SE), 1)
        self.assertEqual(get_wall_direction_number(self.gps6, Direction.HORIZONTAL), 1)
        self.assertEqual(get_wall_direction_number(self.gps7, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps7, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps7, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps7, Direction.SE), 1)
        self.assertEqual(get_wall_direction_number(self.gps7, Direction.HORIZONTAL), 1)
        self.assertEqual(get_wall_direction_number(self.gps8, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps8, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps8, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps8, Direction.SE), 1)
        self.assertEqual(get_wall_direction_number(self.gps8, Direction.HORIZONTAL), 1)
        self.assertEqual(get_wall_direction_number(self.gps9, Direction.SW), 2)
        self.assertEqual(get_wall_direction_number(self.gps9, Direction.NW), 2)
        self.assertEqual(get_wall_direction_number(self.gps9, Direction.NE), 2)
        self.assertEqual(get_wall_direction_number(self.gps9, Direction.SE), 2)
        self.assertEqual(get_wall_direction_number(self.gps10, Direction.SW), 1)
        self.assertEqual(get_wall_direction_number(self.gps10, Direction.NW), 1)
        self.assertEqual(get_wall_direction_number(self.gps10, Direction.HORIZONTAL), 1)

        def get_wall_area_with_direction(gps: List[GeneralPartNoSpec], key):
            return sorted([s.area for s in gps if s.general_part_type == GeneralPartType.WALL and s.direction == key])

        self.assertAlmostEqual(get_wall_area_with_direction(self.gps1, Direction.SW)[0], 30.473673540267082)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps1, Direction.NW)[0], 1.2376)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps1, Direction.NW)[1], 22.365648661814284)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps1, Direction.NE)[0], 1.1557)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps1, Direction.NE)[1], 47.92076305426709)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps1, Direction.SE)[0], 22.274523489414282)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps1, Direction.HORIZONTAL)[0], 2.3933)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps2, Direction.SW)[0], 30.473673540267082)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps2, Direction.NW)[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps2, Direction.NW)[1], 22.365648661814284)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps2, Direction.NE)[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps2, Direction.NE)[1], 47.92076305426709)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps2, Direction.SE)[0], 22.274523489414282)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps2, Direction.HORIZONTAL)[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps3, Direction.SW)[0], 30.473673540267082)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps3, Direction.NW)[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps3, Direction.NW)[1], 22.365648661814284)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps3, Direction.NE)[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps3, Direction.NE)[1], 47.92076305426709)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps3, Direction.SE)[0], 22.274523489414282)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps3, Direction.HORIZONTAL)[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.SW)[0], 5.304759118263725)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.SW)[1], 30.46780391407963)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.NW)[0], 1.8139132205219375)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.NW)[1], 22.36901951287639)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.NE)[0], 4.867959118263724)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.NE)[1], 47.91438134915286)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.SE)[0], 2.3963132205219377)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps4, Direction.SE)[1], 22.277947546942503)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps5, Direction.SW)[0], 9.43319748790514)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps5, Direction.NW)[0], 30.053047891194854)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps5, Direction.HORIZONTAL)[0], 12.800973459805142)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps6, Direction.SW)[0], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps6, Direction.NW)[0], 1.2376)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps6, Direction.NW)[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps6, Direction.NE)[0], 1.1557)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps6, Direction.NE)[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps6, Direction.SE)[0], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps6, Direction.HORIZONTAL)[0], 2.3933)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps7, Direction.SW)[0], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps7, Direction.NW)[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps7, Direction.NW)[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps7, Direction.NE)[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps7, Direction.NE)[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps7, Direction.SE)[0], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps7, Direction.HORIZONTAL)[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps8, Direction.SW)[0], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps8, Direction.NW)[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps8, Direction.NW)[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps8, Direction.NE)[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps8, Direction.NE)[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps8, Direction.SE)[0], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps8, Direction.HORIZONTAL)[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.SW)[0], 5.304991140364853)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.SW)[1], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.NW)[0], 1.8138084140079065)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.NW)[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.NE)[0], 4.868191140364853)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.NE)[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.SE)[0], 2.3962084140079067)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps9, Direction.SE)[1], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps10, Direction.SW)[0], 9.430740769224983)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps10, Direction.NW)[0], 30.05729903749555)
        self.assertAlmostEqual(get_wall_area_with_direction(self.gps10, Direction.HORIZONTAL)[0], 12.798613938126838)

    def test_floor(self):

        def get_floor_number(gps: List[GeneralPartNoSpec]):
            return len([s for s in gps if s.general_part_type == GeneralPartType.FLOOR])

        self.assertEqual(get_floor_number(self.gps1), 1)
        self.assertEqual(get_floor_number(self.gps2), 1)
        self.assertEqual(get_floor_number(self.gps3), 1)
        self.assertEqual(get_floor_number(self.gps4), 0)
        self.assertEqual(get_floor_number(self.gps5), 0)
        self.assertEqual(get_floor_number(self.gps6), 1)
        self.assertEqual(get_floor_number(self.gps7), 1)
        self.assertEqual(get_floor_number(self.gps8), 1)
        self.assertEqual(get_floor_number(self.gps9), 0)
        self.assertEqual(get_floor_number(self.gps10), 0)

        def get_floor_next_space_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.FLOOR and s.next_space == key])

        self.assertEqual(get_floor_next_space_number(self.gps1, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_floor_next_space_number(self.gps2, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_floor_next_space_number(self.gps3, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_floor_next_space_number(self.gps6, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_floor_next_space_number(self.gps7, NextSpace.OPEN_UNDERFLOOR), 1)
        self.assertEqual(get_floor_next_space_number(self.gps8, NextSpace.OPEN_UNDERFLOOR), 1)

        def get_floor_direction_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.FLOOR and s.direction == key])

        self.assertEqual(get_floor_direction_number(self.gps1, Direction.DOWNWARD), 1)
        self.assertEqual(get_floor_direction_number(self.gps2, Direction.DOWNWARD), 1)
        self.assertEqual(get_floor_direction_number(self.gps3, Direction.DOWNWARD), 1)
        self.assertEqual(get_floor_direction_number(self.gps6, Direction.DOWNWARD), 1)
        self.assertEqual(get_floor_direction_number(self.gps7, Direction.DOWNWARD), 1)
        self.assertEqual(get_floor_direction_number(self.gps8, Direction.DOWNWARD), 1)

        def get_floor_area_with_direction(gps: List[GeneralPartNoSpec], key):
            return sorted([s.area for s in gps if s.general_part_type == GeneralPartType.FLOOR and s.direction == key])

        self.assertAlmostEqual(get_floor_area_with_direction(self.gps1, Direction.DOWNWARD)[0], 45.05075762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.gps2, Direction.DOWNWARD)[0], 48.36315762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.gps3, Direction.DOWNWARD)[0], 48.36315762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.gps6, Direction.DOWNWARD)[0], 45.05075762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.gps7, Direction.DOWNWARD)[0], 48.36315762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.gps8, Direction.DOWNWARD)[0], 48.36315762711864)

    def test_boundary_wall(self):

        def get_boundary_wall_number(gps: List[GeneralPartNoSpec]):
            return len([s for s in gps if s.general_part_type == GeneralPartType.BOUNDARY_WALL])

        self.assertEqual(get_boundary_wall_number(self.gps1), 0)
        self.assertEqual(get_boundary_wall_number(self.gps2), 0)
        self.assertEqual(get_boundary_wall_number(self.gps3), 0)
        self.assertEqual(get_boundary_wall_number(self.gps4), 0)
        self.assertEqual(get_boundary_wall_number(self.gps5), 1)
        self.assertEqual(get_boundary_wall_number(self.gps6), 0)
        self.assertEqual(get_boundary_wall_number(self.gps7), 0)
        self.assertEqual(get_boundary_wall_number(self.gps8), 0)
        self.assertEqual(get_boundary_wall_number(self.gps9), 0)
        self.assertEqual(get_boundary_wall_number(self.gps10), 1)

        def get_boundary_wall_next_space_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.BOUNDARY_WALL and s.next_space == key])

        self.assertEqual(get_boundary_wall_next_space_number(self.gps5, NextSpace.AIR_CONDITIONED), 1)
        self.assertEqual(get_boundary_wall_next_space_number(self.gps10, NextSpace.AIR_CONDITIONED), 1)

        def get_boundary_wall_direction_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.BOUNDARY_WALL and s.direction == key])

        self.assertEqual(get_boundary_wall_direction_number(self.gps5, Direction.HORIZONTAL), 1)
        self.assertEqual(get_boundary_wall_direction_number(self.gps10, Direction.HORIZONTAL), 1)

        def get_boundary_wall_area_with_direction(gps: List[GeneralPartNoSpec], key):
            return sorted([s.area for s in gps if s.general_part_type == GeneralPartType.BOUNDARY_WALL and s.direction == key])

        self.assertAlmostEqual(get_boundary_wall_area_with_direction(self.gps5, Direction.HORIZONTAL)[0], 31.913534161094855)
        self.assertAlmostEqual(get_boundary_wall_area_with_direction(self.gps10, Direction.HORIZONTAL)[0], 31.917820607336132)

    def test_upward_boundary_floor(self):

        def get_upward_boundary_floor_number(gps: List[GeneralPartNoSpec]):
            return len([s for s in gps if s.general_part_type == GeneralPartType.UPWARD_BOUNDARY_FLOOR])

        self.assertEqual(get_upward_boundary_floor_number(self.gps1), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps2), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps3), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps4), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps5), 1)
        self.assertEqual(get_upward_boundary_floor_number(self.gps6), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps7), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps8), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps9), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.gps10), 1)

        def get_upward_boundary_floor_next_space_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.UPWARD_BOUNDARY_FLOOR and s.next_space == key])

        self.assertEqual(get_upward_boundary_floor_next_space_number(self.gps5, NextSpace.AIR_CONDITIONED), 1)
        self.assertEqual(get_upward_boundary_floor_next_space_number(self.gps10, NextSpace.AIR_CONDITIONED), 1)

        def get_upward_boundary_floor_direction_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.UPWARD_BOUNDARY_FLOOR and s.direction == key])

        self.assertEqual(get_upward_boundary_floor_direction_number(self.gps5, Direction.UPWARD), 1)
        self.assertEqual(get_upward_boundary_floor_direction_number(self.gps10, Direction.UPWARD), 1)

        def get_upward_boundary_floor_area_with_direction(gps: List[GeneralPartNoSpec], key):
            return sorted([s.area for s in gps if s.general_part_type == GeneralPartType.UPWARD_BOUNDARY_FLOOR and s.direction == key])

        self.assertAlmostEqual(get_upward_boundary_floor_area_with_direction(self.gps5, Direction.UPWARD)[0], 70.0)
        self.assertAlmostEqual(get_upward_boundary_floor_area_with_direction(self.gps10, Direction.UPWARD)[0], 70.0)

    def test_downward_boundary_floor(self):

        def get_downward_boundary_floor_number(gps: List[GeneralPartNoSpec]):
            return len([s for s in gps if s.general_part_type == GeneralPartType.DOWNWARD_BOUNDARY_FLOOR])

        self.assertEqual(get_downward_boundary_floor_number(self.gps1), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps2), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps3), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps4), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps5), 1)
        self.assertEqual(get_downward_boundary_floor_number(self.gps6), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps7), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps8), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps9), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.gps10), 1)

        def get_downward_boundary_floor_next_space_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.DOWNWARD_BOUNDARY_FLOOR and s.next_space == key])

        self.assertEqual(get_downward_boundary_floor_next_space_number(self.gps5, NextSpace.AIR_CONDITIONED), 1)
        self.assertEqual(get_downward_boundary_floor_next_space_number(self.gps10, NextSpace.AIR_CONDITIONED), 1)

        def get_downward_boundary_floor_direction_number(gps: List[GeneralPartNoSpec], key):
            return len([s for s in gps if s.general_part_type == GeneralPartType.DOWNWARD_BOUNDARY_FLOOR and s.direction == key])

        self.assertEqual(get_downward_boundary_floor_direction_number(self.gps5, Direction.DOWNWARD), 1)
        self.assertEqual(get_downward_boundary_floor_direction_number(self.gps10, Direction.DOWNWARD), 1)

        def get_downward_boundary_floor_area_with_direction(gps: List[GeneralPartNoSpec], key):
            return sorted([s.area for s in gps if s.general_part_type == GeneralPartType.DOWNWARD_BOUNDARY_FLOOR and s.direction == key])

        self.assertAlmostEqual(get_downward_boundary_floor_area_with_direction(self.gps5, Direction.DOWNWARD)[0], 70.0)
        self.assertAlmostEqual(get_downward_boundary_floor_area_with_direction(self.gps10, Direction.DOWNWARD)[0], 70.0)

    def test_windows(self):

        def get_windows_number(ws: List[WindowNoSpec]):
            return len(ws)

        self.assertEqual(get_windows_number(self.ws1), 4)
        self.assertEqual(get_windows_number(self.ws2), 4)
        self.assertEqual(get_windows_number(self.ws3), 4)
        self.assertEqual(get_windows_number(self.ws4), 4)
        self.assertEqual(get_windows_number(self.ws5), 3)
        self.assertEqual(get_windows_number(self.ws6), 4)
        self.assertEqual(get_windows_number(self.ws7), 4)
        self.assertEqual(get_windows_number(self.ws8), 4)
        self.assertEqual(get_windows_number(self.ws9), 4)
        self.assertEqual(get_windows_number(self.ws10), 3)

        def get_windows_next_space_number(ws: List[WindowNoSpec], key):
            return len([s for s in ws if s.next_space == key])

        self.assertEqual(get_windows_next_space_number(self.ws1, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws2, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws3, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws4, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws5, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_windows_next_space_number(self.ws5, NextSpace.OPEN_SPACE), 1)
        self.assertEqual(get_windows_next_space_number(self.ws6, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws7, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws8, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws9, NextSpace.OUTDOOR), 4)
        self.assertEqual(get_windows_next_space_number(self.ws10, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_windows_next_space_number(self.ws10, NextSpace.OPEN_SPACE), 1)

        def get_windows_direction_number(ws: List[WindowNoSpec], key):
            return len([s for s in ws if s.direction == key])

        self.assertEqual(get_windows_direction_number(self.ws1, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws1, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws1, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws1, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws2, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws2, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws2, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws2, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws3, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws3, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws3, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws3, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws4, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws4, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws4, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws4, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws5, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws5, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws5, Direction.HORIZONTAL), 1)
        self.assertEqual(get_windows_direction_number(self.ws6, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws6, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws6, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws6, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws7, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws7, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws7, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws7, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws8, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws8, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws8, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws8, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws9, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws9, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws9, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ws9, Direction.SE), 1)
        self.assertEqual(get_windows_direction_number(self.ws10, Direction.SW), 1)
        self.assertEqual(get_windows_direction_number(self.ws10, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ws10, Direction.HORIZONTAL), 1)

        def get_windows_area_with_direction(ws: List[WindowNoSpec], key):
            return sorted([s.area for s in ws if s.direction == key])

        self.assertAlmostEqual(get_windows_area_with_direction(self.ws1, Direction.SW)[0], 22.695293711200005)
        self.assertAlmostEqual(get_windows_area_with_direction(self.ws1, Direction.NW)[0], 2.3846264596)
        self.assertAlmostEqual(get_windows_area_with_direction(self.ws1, Direction.NE)[0], 3.628204197200001)
        self.assertAlmostEqual(get_windows_area_with_direction(self.ws1, Direction.SE)[0], 4.365751632000001)

    def test_doors(self):

        def get_doors_number(ds):
            return len(ds)

        self.assertEqual(get_doors_number(self.ds1), 2)
        self.assertEqual(get_doors_number(self.ds2), 2)
        self.assertEqual(get_doors_number(self.ds3), 2)
        self.assertEqual(get_doors_number(self.ds4), 2)
        self.assertEqual(get_doors_number(self.ds5), 1)
        self.assertEqual(get_doors_number(self.ds6), 2)
        self.assertEqual(get_doors_number(self.ds7), 2)
        self.assertEqual(get_doors_number(self.ds8), 2)
        self.assertEqual(get_doors_number(self.ds9), 2)
        self.assertEqual(get_doors_number(self.ds10), 1)

        def get_doors_next_space_number(ds: List[DoorNoSpec], key):
            return len([s for s in ds if s.next_space == key])

        self.assertEqual(get_doors_next_space_number(self.ds1, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds2, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds3, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds4, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds5, NextSpace.OPEN_SPACE), 1)
        self.assertEqual(get_doors_next_space_number(self.ds6, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds7, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds8, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds9, NextSpace.OUTDOOR), 2)
        self.assertEqual(get_doors_next_space_number(self.ds10, NextSpace.OPEN_SPACE), 1)

        def get_windows_direction_number(ds: List[DoorNoSpec], key):
            return len([s for s in ds if s.direction == key])

        self.assertEqual(get_windows_direction_number(self.ds1, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds1, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds2, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds2, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds3, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds3, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds4, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds4, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds5, Direction.HORIZONTAL), 1)
        self.assertEqual(get_windows_direction_number(self.ds6, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds6, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds7, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds7, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds8, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds8, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds9, Direction.NW), 1)
        self.assertEqual(get_windows_direction_number(self.ds9, Direction.NE), 1)
        self.assertEqual(get_windows_direction_number(self.ds10, Direction.HORIZONTAL), 1)

        def get_doors_area_with_direction(ds: List[DoorNoSpec], key):
            return sorted([s.area for s in ds if s.direction == key])

        self.assertAlmostEqual(get_doors_area_with_direction(self.ds1, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds1, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds2, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds2, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds3, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds3, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds4, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds4, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds5, Direction.HORIZONTAL)[0], 1.755)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds6, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds6, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds7, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds7, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds8, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds8, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds9, Direction.NW)[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds9, Direction.NE)[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.ds10, Direction.HORIZONTAL)[0], 1.755)

    def test_earthfloor_perimeters(self):

        def get_earthfloor_perimeters_number(eps: List[EarthfloorPerimeterNoSpec]):
            return len(eps)

        self.assertEqual(get_earthfloor_perimeters_number(self.eps1), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps2), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps3), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps4), 4)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps5), 0)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps6), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps7), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps8), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps9), 4)
        self.assertEqual(get_earthfloor_perimeters_number(self.eps10), 0)

        def get_earthfloor_perimeters_next_space_number(eps: List[EarthfloorPerimeterNoSpec], key):
            return len([s for s in eps if s.next_space == key])

        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps1, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps1, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps2, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps2, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps3, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps3, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps4, 'outdoor'), 4)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps6, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps6, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps7, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps7, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps8, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps8, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.eps9, 'outdoor'), 4)

        def get_earthfloor_perimeters_length(eps: List[EarthfloorPerimeterNoSpec]):
            return sorted([s.length for s in eps])

        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps1)[0], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps1)[1], 3.64)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps1)[2], 6.825)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps2)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps2)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps2)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps3)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps3)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps3)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps4)[0], 4.7926264410438755)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps4)[1], 4.7926264410438755)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps4)[2], 10.60951823652745)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps4)[3], 10.60951823652745)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps6)[0], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps6)[1], 3.64)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps6)[2], 6.825)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps7)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps7)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps7)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps8)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps8)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps8)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps9)[0], 4.7924168280158135)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps9)[1], 4.7924168280158135)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps9)[2], 10.609982280729707)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.eps9)[3], 10.609982280729707)

    def test_earthfloor_centers(self):

        def get_earthfloor_centers_number(ecs: List[EarthfloorCenter]):
            return len(ecs)

        self.assertEqual(get_earthfloor_centers_number(self.ecs1), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs2), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs3), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs4), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs5), 0)
        self.assertEqual(get_earthfloor_centers_number(self.ecs6), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs7), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs8), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs9), 1)
        self.assertEqual(get_earthfloor_centers_number(self.ecs10), 0)

        def get_earthfloor_centers_area(ecs: List[EarthfloorCenter]):
            return sorted([s.area for s in ecs])

        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs1)[0], 5.7967)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs2)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs3)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs4)[0], 50.847457627118644)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs6)[0], 5.7967)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs7)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs8)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.ecs9)[0], 50.847457627118644)


if __name__ == '__main__':
    unittest.main()
