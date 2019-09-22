import unittest
import convert_model_house_to_house_dict as cmhhd


class ConvertModelHouseToHouseDict(unittest.TestCase):

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

        self.mh1 = cmhhd.convert(**mh1_input)
        self.mh2 = cmhhd.convert(**mh2_input)
        self.mh3 = cmhhd.convert(**mh3_input)
        self.mh4 = cmhhd.convert(**mh4_input)
        self.mh5 = cmhhd.convert(**mh5_input)
        self.mh6 = cmhhd.convert(**mh6_input)
        self.mh7 = cmhhd.convert(**mh7_input)
        self.mh8 = cmhhd.convert(**mh8_input)
        self.mh9 = cmhhd.convert(**mh9_input)
        self.mh10 = cmhhd.convert(**mh10_input)

    def test_general_parts_number(self):

        self.assertEqual(len(self.mh1['general_parts']), 9)
        self.assertEqual(len(self.mh2['general_parts']), 9)
        self.assertEqual(len(self.mh3['general_parts']), 9)
        self.assertEqual(len(self.mh4['general_parts']), 9)
        self.assertEqual(len(self.mh5['general_parts']), 6)
        self.assertEqual(len(self.mh6['general_parts']), 9)
        self.assertEqual(len(self.mh7['general_parts']), 9)
        self.assertEqual(len(self.mh8['general_parts']), 9)
        self.assertEqual(len(self.mh9['general_parts']), 9)
        self.assertEqual(len(self.mh10['general_parts']), 6)

    def test_windows_number(self):

        self.assertEqual(len(self.mh1['windows']), 4)
        self.assertEqual(len(self.mh2['windows']), 4)
        self.assertEqual(len(self.mh3['windows']), 4)
        self.assertEqual(len(self.mh4['windows']), 4)
        self.assertEqual(len(self.mh5['windows']), 3)
        self.assertEqual(len(self.mh6['windows']), 4)
        self.assertEqual(len(self.mh7['windows']), 4)
        self.assertEqual(len(self.mh8['windows']), 4)
        self.assertEqual(len(self.mh9['windows']), 4)
        self.assertEqual(len(self.mh10['windows']), 3)

    def test_doors_number(self):

        self.assertEqual(len(self.mh1['doors']), 2)
        self.assertEqual(len(self.mh2['doors']), 2)
        self.assertEqual(len(self.mh3['doors']), 2)
        self.assertEqual(len(self.mh4['doors']), 2)
        self.assertEqual(len(self.mh5['doors']), 1)
        self.assertEqual(len(self.mh6['doors']), 2)
        self.assertEqual(len(self.mh7['doors']), 2)
        self.assertEqual(len(self.mh8['doors']), 2)
        self.assertEqual(len(self.mh9['doors']), 2)
        self.assertEqual(len(self.mh10['doors']), 1)

    def test_earthfloor_perimeters(self):

        self.assertEqual(len(self.mh1['earthfloor_perimeters']), 3)
        self.assertEqual(len(self.mh2['earthfloor_perimeters']), 3)
        self.assertEqual(len(self.mh3['earthfloor_perimeters']), 3)
        self.assertEqual(len(self.mh4['earthfloor_perimeters']), 4)
        self.assertEqual(len(self.mh5['earthfloor_perimeters']), 0)
        self.assertEqual(len(self.mh6['earthfloor_perimeters']), 3)
        self.assertEqual(len(self.mh7['earthfloor_perimeters']), 3)
        self.assertEqual(len(self.mh8['earthfloor_perimeters']), 3)
        self.assertEqual(len(self.mh9['earthfloor_perimeters']), 4)
        self.assertEqual(len(self.mh10['earthfloor_perimeters']), 0)

    def test_earthfloor_centers(self):

        self.assertEqual(len(self.mh1['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh2['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh3['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh4['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh5['earthfloor_centers']), 0)
        self.assertEqual(len(self.mh6['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh7['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh8['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh9['earthfloor_centers']), 1)
        self.assertEqual(len(self.mh10['earthfloor_centers']), 0)

    def test_roof(self):

        def get_roof_number(mh):
            return len([p for p in mh['general_parts'] if p['general_part_type'] == 'roof'])

        self.assertEqual(get_roof_number(self.mh1), 0)
        self.assertEqual(get_roof_number(self.mh2), 0)
        self.assertEqual(get_roof_number(self.mh3), 0)
        self.assertEqual(get_roof_number(self.mh4), 0)
        self.assertEqual(get_roof_number(self.mh5), 0)
        self.assertEqual(get_roof_number(self.mh6), 0)
        self.assertEqual(get_roof_number(self.mh7), 0)
        self.assertEqual(get_roof_number(self.mh8), 0)
        self.assertEqual(get_roof_number(self.mh9), 0)
        self.assertEqual(get_roof_number(self.mh10), 0)

    def test_ceiling(self):

        def get_ceiling_number(mh):
            return len([p for p in mh['general_parts'] if p['general_part_type'] == 'ceiling'])

        self.assertEqual(get_ceiling_number(self.mh1), 1)
        self.assertEqual(get_ceiling_number(self.mh2), 1)
        self.assertEqual(get_ceiling_number(self.mh3), 1)
        self.assertEqual(get_ceiling_number(self.mh4), 1)
        self.assertEqual(get_ceiling_number(self.mh5), 0)
        self.assertEqual(get_ceiling_number(self.mh6), 1)
        self.assertEqual(get_ceiling_number(self.mh7), 1)
        self.assertEqual(get_ceiling_number(self.mh8), 1)
        self.assertEqual(get_ceiling_number(self.mh9), 1)
        self.assertEqual(get_ceiling_number(self.mh10), 0)

        def get_ceiling_next_space_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'ceiling' and p['next_space'] == key])

        self.assertEqual(get_ceiling_next_space_number(self.mh1, 'outdoor'), 1)
        self.assertEqual(get_ceiling_next_space_number(self.mh2, 'outdoor'), 1)
        self.assertEqual(get_ceiling_next_space_number(self.mh3, 'outdoor'), 1)
        self.assertEqual(get_ceiling_next_space_number(self.mh4, 'outdoor'), 1)
        self.assertEqual(get_ceiling_next_space_number(self.mh6, 'outdoor'), 1)
        self.assertEqual(get_ceiling_next_space_number(self.mh7, 'outdoor'), 1)
        self.assertEqual(get_ceiling_next_space_number(self.mh8, 'outdoor'), 1)
        self.assertEqual(get_ceiling_next_space_number(self.mh9, 'outdoor'), 1)

        def get_ceiling_direction_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'ceiling' and p['direction'] == key])

        self.assertEqual(get_ceiling_direction_number(self.mh1, 'top'), 1)
        self.assertEqual(get_ceiling_direction_number(self.mh2, 'top'), 1)
        self.assertEqual(get_ceiling_direction_number(self.mh3, 'top'), 1)
        self.assertEqual(get_ceiling_direction_number(self.mh4, 'top'), 1)
        self.assertEqual(get_ceiling_direction_number(self.mh6, 'top'), 1)
        self.assertEqual(get_ceiling_direction_number(self.mh7, 'top'), 1)
        self.assertEqual(get_ceiling_direction_number(self.mh8, 'top'), 1)
        self.assertEqual(get_ceiling_direction_number(self.mh9, 'top'), 1)

        def get_ceiling_area(mh):
            return sorted([p['area'] for p in mh['general_parts'] if p['general_part_type'] == 'ceiling'])

        self.assertAlmostEqual(get_ceiling_area(self.mh1)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.mh2)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.mh3)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.mh4)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.mh6)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.mh7)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.mh8)[0], 50.847457627118644)
        self.assertAlmostEqual(get_ceiling_area(self.mh9)[0], 50.847457627118644)

    def test_wall(self):

        def get_wall_number(mh):
            return len([p for p in mh['general_parts'] if p['general_part_type'] == 'wall'])

        self.assertEqual(get_wall_number(self.mh1), 7)
        self.assertEqual(get_wall_number(self.mh2), 7)
        self.assertEqual(get_wall_number(self.mh3), 7)
        self.assertEqual(get_wall_number(self.mh4), 8)
        self.assertEqual(get_wall_number(self.mh5), 3)
        self.assertEqual(get_wall_number(self.mh6), 7)
        self.assertEqual(get_wall_number(self.mh7), 7)
        self.assertEqual(get_wall_number(self.mh8), 7)
        self.assertEqual(get_wall_number(self.mh9), 8)
        self.assertEqual(get_wall_number(self.mh10), 3)

        def get_wall_next_space_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'wall' and p['next_space'] == key])

        self.assertEqual(get_wall_next_space_number(self.mh1, 'outdoor'), 6)
        self.assertEqual(get_wall_next_space_number(self.mh1, 'open_underfloor'), 1)
        self.assertEqual(get_wall_next_space_number(self.mh2, 'outdoor'), 6)
        self.assertEqual(get_wall_next_space_number(self.mh2, 'open_underfloor'), 1)
        self.assertEqual(get_wall_next_space_number(self.mh3, 'outdoor'), 6)
        self.assertEqual(get_wall_next_space_number(self.mh3, 'open_underfloor'), 1)
        self.assertEqual(get_wall_next_space_number(self.mh4, 'outdoor'), 8)
        self.assertEqual(get_wall_next_space_number(self.mh5, 'outdoor'), 2)
        self.assertEqual(get_wall_next_space_number(self.mh5, 'open_space'), 1)
        self.assertEqual(get_wall_next_space_number(self.mh6, 'outdoor'), 6)
        self.assertEqual(get_wall_next_space_number(self.mh6, 'open_underfloor'), 1)
        self.assertEqual(get_wall_next_space_number(self.mh7, 'outdoor'), 6)
        self.assertEqual(get_wall_next_space_number(self.mh7, 'open_underfloor'), 1)
        self.assertEqual(get_wall_next_space_number(self.mh8, 'outdoor'), 6)
        self.assertEqual(get_wall_next_space_number(self.mh8, 'open_underfloor'), 1)
        self.assertEqual(get_wall_next_space_number(self.mh9, 'outdoor'), 8)
        self.assertEqual(get_wall_next_space_number(self.mh10, 'outdoor'), 2)
        self.assertEqual(get_wall_next_space_number(self.mh10, 'open_space'), 1)

        def get_wall_direction_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'wall' and p['direction'] == key])

        self.assertEqual(get_wall_direction_number(self.mh1, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh1, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh1, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh1, 'se'), 1)
        self.assertEqual(get_wall_direction_number(self.mh1, 'horizontal'), 1)
        self.assertEqual(get_wall_direction_number(self.mh2, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh2, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh2, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh2, 'se'), 1)
        self.assertEqual(get_wall_direction_number(self.mh2, 'horizontal'), 1)
        self.assertEqual(get_wall_direction_number(self.mh3, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh3, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh3, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh3, 'se'), 1)
        self.assertEqual(get_wall_direction_number(self.mh3, 'horizontal'), 1)
        self.assertEqual(get_wall_direction_number(self.mh4, 'sw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh4, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh4, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh4, 'se'), 2)
        self.assertEqual(get_wall_direction_number(self.mh5, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh5, 'nw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh5, 'horizontal'), 1)
        self.assertEqual(get_wall_direction_number(self.mh6, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh6, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh6, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh6, 'se'), 1)
        self.assertEqual(get_wall_direction_number(self.mh6, 'horizontal'), 1)
        self.assertEqual(get_wall_direction_number(self.mh7, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh7, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh7, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh7, 'se'), 1)
        self.assertEqual(get_wall_direction_number(self.mh7, 'horizontal'), 1)
        self.assertEqual(get_wall_direction_number(self.mh8, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh8, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh8, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh8, 'se'), 1)
        self.assertEqual(get_wall_direction_number(self.mh8, 'horizontal'), 1)
        self.assertEqual(get_wall_direction_number(self.mh9, 'sw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh9, 'nw'), 2)
        self.assertEqual(get_wall_direction_number(self.mh9, 'ne'), 2)
        self.assertEqual(get_wall_direction_number(self.mh9, 'se'), 2)
        self.assertEqual(get_wall_direction_number(self.mh10, 'sw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh10, 'nw'), 1)
        self.assertEqual(get_wall_direction_number(self.mh10, 'horizontal'), 1)

        def get_wall_area_with_direction(mh, key):
            return sorted([p['area'] for p in mh['general_parts']
                           if p['general_part_type'] == 'wall' and p['direction'] == key])

        self.assertAlmostEqual(get_wall_area_with_direction(self.mh1, 'sw')[0], 30.473673540267082)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh1, 'nw')[0], 1.2376)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh1, 'nw')[1], 22.365648661814284)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh1, 'ne')[0], 1.1557)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh1, 'ne')[1], 47.92076305426709)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh1, 'se')[0], 22.274523489414282)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh1, 'horizontal')[0], 2.3933)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh2, 'sw')[0], 30.473673540267082)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh2, 'nw')[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh2, 'nw')[1], 22.365648661814284)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh2, 'ne')[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh2, 'ne')[1], 47.92076305426709)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh2, 'se')[0], 22.274523489414282)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh2, 'horizontal')[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh3, 'sw')[0], 30.473673540267082)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh3, 'nw')[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh3, 'nw')[1], 22.365648661814284)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh3, 'ne')[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh3, 'ne')[1], 47.92076305426709)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh3, 'se')[0], 22.274523489414282)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh3, 'horizontal')[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'sw')[0], 5.304759118263725)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'sw')[1], 30.46780391407963)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'nw')[0], 1.8139132205219375)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'nw')[1], 22.36901951287639)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'ne')[0], 4.867959118263724)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'ne')[1], 47.91438134915286)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'se')[0], 2.3963132205219377)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh4, 'se')[1], 22.277947546942503)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh5, 'sw')[0], 9.43319748790514)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh5, 'nw')[0], 30.053047891194854)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh5, 'horizontal')[0], 12.800973459805142)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh6, 'sw')[0], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh6, 'nw')[0], 1.2376)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh6, 'nw')[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh6, 'ne')[0], 1.1557)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh6, 'ne')[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh6, 'se')[0], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh6, 'horizontal')[0], 2.3933)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh7, 'sw')[0], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh7, 'nw')[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh7, 'nw')[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh7, 'ne')[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh7, 'ne')[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh7, 'se')[0], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh7, 'horizontal')[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh8, 'sw')[0], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh8, 'nw')[0], 0.3276)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh8, 'nw')[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh8, 'ne')[0], 0.2457)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh8, 'ne')[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh8, 'se')[0], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh8, 'horizontal')[0], 0.5733)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'sw')[0], 5.304991140364853)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'sw')[1], 30.47024338051379)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'nw')[0], 1.8138084140079065)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'nw')[1], 22.367618465527734)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'ne')[0], 4.868191140364853)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'ne')[1], 47.917033620863265)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'se')[0], 2.3962084140079067)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh9, 'se')[1], 22.276524388516577)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh10, 'sw')[0], 9.430740769224983)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh10, 'nw')[0], 30.05729903749555)
        self.assertAlmostEqual(get_wall_area_with_direction(self.mh10, 'horizontal')[0], 12.798613938126838)

    def test_floor(self):

        def get_floor_number(mh):
            return len([p for p in mh['general_parts'] if p['general_part_type'] == 'floor'])

        self.assertEqual(get_floor_number(self.mh1), 1)
        self.assertEqual(get_floor_number(self.mh2), 1)
        self.assertEqual(get_floor_number(self.mh3), 1)
        self.assertEqual(get_floor_number(self.mh4), 0)
        self.assertEqual(get_floor_number(self.mh5), 0)
        self.assertEqual(get_floor_number(self.mh6), 1)
        self.assertEqual(get_floor_number(self.mh7), 1)
        self.assertEqual(get_floor_number(self.mh8), 1)
        self.assertEqual(get_floor_number(self.mh9), 0)
        self.assertEqual(get_floor_number(self.mh10), 0)

        def get_floor_next_space_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'floor' and p['next_space'] == key])

        self.assertEqual(get_floor_next_space_number(self.mh1, 'open_underfloor'), 1)
        self.assertEqual(get_floor_next_space_number(self.mh2, 'open_underfloor'), 1)
        self.assertEqual(get_floor_next_space_number(self.mh3, 'open_underfloor'), 1)
        self.assertEqual(get_floor_next_space_number(self.mh6, 'open_underfloor'), 1)
        self.assertEqual(get_floor_next_space_number(self.mh7, 'open_underfloor'), 1)
        self.assertEqual(get_floor_next_space_number(self.mh8, 'open_underfloor'), 1)

        def get_floor_direction_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'floor' and p['direction'] == key])

        self.assertEqual(get_floor_direction_number(self.mh1, 'downward'), 1)
        self.assertEqual(get_floor_direction_number(self.mh2, 'downward'), 1)
        self.assertEqual(get_floor_direction_number(self.mh3, 'downward'), 1)
        self.assertEqual(get_floor_direction_number(self.mh6, 'downward'), 1)
        self.assertEqual(get_floor_direction_number(self.mh7, 'downward'), 1)
        self.assertEqual(get_floor_direction_number(self.mh8, 'downward'), 1)

        def get_floor_area_with_direction(mh, key):
            return sorted([p['area'] for p in mh['general_parts']
                           if p['general_part_type'] == 'floor' and p['direction'] == key])

        self.assertAlmostEqual(get_floor_area_with_direction(self.mh1, 'downward')[0], 45.05075762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.mh2, 'downward')[0], 48.36315762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.mh3, 'downward')[0], 48.36315762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.mh6, 'downward')[0], 45.05075762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.mh7, 'downward')[0], 48.36315762711864)
        self.assertAlmostEqual(get_floor_area_with_direction(self.mh8, 'downward')[0], 48.36315762711864)

    def test_boundary_wall(self):

        def get_boundary_wall_number(mh):
            return len([p for p in mh['general_parts'] if p['general_part_type'] == 'boundary_wall'])

        self.assertEqual(get_boundary_wall_number(self.mh1), 0)
        self.assertEqual(get_boundary_wall_number(self.mh2), 0)
        self.assertEqual(get_boundary_wall_number(self.mh3), 0)
        self.assertEqual(get_boundary_wall_number(self.mh4), 0)
        self.assertEqual(get_boundary_wall_number(self.mh5), 1)
        self.assertEqual(get_boundary_wall_number(self.mh6), 0)
        self.assertEqual(get_boundary_wall_number(self.mh7), 0)
        self.assertEqual(get_boundary_wall_number(self.mh8), 0)
        self.assertEqual(get_boundary_wall_number(self.mh9), 0)
        self.assertEqual(get_boundary_wall_number(self.mh10), 1)

        def get_boundary_wall_next_space_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'boundary_wall' and p['next_space'] == key])

        self.assertEqual(get_boundary_wall_next_space_number(self.mh5, 'air_conditioned'), 1)
        self.assertEqual(get_boundary_wall_next_space_number(self.mh10, 'air_conditioned'), 1)

        def get_boundary_wall_direction_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'boundary_wall' and p['direction'] == key])

        self.assertEqual(get_boundary_wall_direction_number(self.mh5, 'horizontal'), 1)
        self.assertEqual(get_boundary_wall_direction_number(self.mh10, 'horizontal'), 1)

        def get_boundary_wall_area_with_direction(mh, key):
            return sorted([p['area'] for p in mh['general_parts']
                           if p['general_part_type'] == 'boundary_wall' and p['direction'] == key])

        self.assertAlmostEqual(get_boundary_wall_area_with_direction(self.mh5, 'horizontal')[0], 31.913534161094855)
        self.assertAlmostEqual(get_boundary_wall_area_with_direction(self.mh10, 'horizontal')[0], 31.917820607336132)

    def test_upward_boundary_floor(self):

        def get_upward_boundary_floor_number(mh):
            return len([p for p in mh['general_parts'] if p['general_part_type'] == 'upward_boundary_floor'])

        self.assertEqual(get_upward_boundary_floor_number(self.mh1), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh2), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh3), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh4), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh5), 1)
        self.assertEqual(get_upward_boundary_floor_number(self.mh6), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh7), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh8), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh9), 0)
        self.assertEqual(get_upward_boundary_floor_number(self.mh10), 1)

        def get_upward_boundary_floor_next_space_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'upward_boundary_floor' and p['next_space'] == key])

        self.assertEqual(get_upward_boundary_floor_next_space_number(self.mh5, 'air_conditioned'), 1)
        self.assertEqual(get_upward_boundary_floor_next_space_number(self.mh10, 'air_conditioned'), 1)

        def get_upward_boundary_floor_direction_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'upward_boundary_floor' and p['direction'] == key])

        self.assertEqual(get_upward_boundary_floor_direction_number(self.mh5, 'upward'), 1)
        self.assertEqual(get_upward_boundary_floor_direction_number(self.mh10, 'upward'), 1)

        def get_upward_boundary_floor_area_with_direction(mh, key):
            return sorted([p['area'] for p in mh['general_parts']
                           if p['general_part_type'] == 'upward_boundary_floor' and p['direction'] == key])

        self.assertAlmostEqual(get_upward_boundary_floor_area_with_direction(self.mh5, 'upward')[0], 70.0)
        self.assertAlmostEqual(get_upward_boundary_floor_area_with_direction(self.mh10, 'upward')[0], 70.0)

    def test_downward_boundary_floor(self):

        def get_downward_boundary_floor_number(mh):
            return len([p for p in mh['general_parts'] if p['general_part_type'] == 'downward_boundary_floor'])

        self.assertEqual(get_downward_boundary_floor_number(self.mh1), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh2), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh3), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh4), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh5), 1)
        self.assertEqual(get_downward_boundary_floor_number(self.mh6), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh7), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh8), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh9), 0)
        self.assertEqual(get_downward_boundary_floor_number(self.mh10), 1)

        def get_downward_boundary_floor_next_space_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'downward_boundary_floor' and p['next_space'] == key])

        self.assertEqual(get_downward_boundary_floor_next_space_number(self.mh5, 'air_conditioned'), 1)
        self.assertEqual(get_downward_boundary_floor_next_space_number(self.mh10, 'air_conditioned'), 1)

        def get_downward_boundary_floor_direction_number(mh, key):
            return len([p for p in mh['general_parts']
                        if p['general_part_type'] == 'downward_boundary_floor' and p['direction'] == key])

        self.assertEqual(get_downward_boundary_floor_direction_number(self.mh5, 'downward'), 1)
        self.assertEqual(get_downward_boundary_floor_direction_number(self.mh10, 'downward'), 1)

        def get_downward_boundary_floor_area_with_direction(mh, key):
            return sorted([p['area'] for p in mh['general_parts']
                           if p['general_part_type'] == 'downward_boundary_floor' and p['direction'] == key])

        self.assertAlmostEqual(get_downward_boundary_floor_area_with_direction(self.mh5, 'downward')[0], 70.0)
        self.assertAlmostEqual(get_downward_boundary_floor_area_with_direction(self.mh10, 'downward')[0], 70.0)

    def test_windows(self):

        def get_windows_number(mh):
            return len(mh['windows'])

        self.assertEqual(get_windows_number(self.mh1), 4)
        self.assertEqual(get_windows_number(self.mh2), 4)
        self.assertEqual(get_windows_number(self.mh3), 4)
        self.assertEqual(get_windows_number(self.mh4), 4)
        self.assertEqual(get_windows_number(self.mh5), 3)
        self.assertEqual(get_windows_number(self.mh6), 4)
        self.assertEqual(get_windows_number(self.mh7), 4)
        self.assertEqual(get_windows_number(self.mh8), 4)
        self.assertEqual(get_windows_number(self.mh9), 4)
        self.assertEqual(get_windows_number(self.mh10), 3)

        def get_windows_next_space_number(mh, key):
            return len([p for p in mh['windows'] if p['next_space'] == key])

        self.assertEqual(get_windows_next_space_number(self.mh1, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh2, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh3, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh4, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh5, 'outdoor'), 2)
        self.assertEqual(get_windows_next_space_number(self.mh5, 'open_space'), 1)
        self.assertEqual(get_windows_next_space_number(self.mh6, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh7, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh8, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh9, 'outdoor'), 4)
        self.assertEqual(get_windows_next_space_number(self.mh10, 'outdoor'), 2)
        self.assertEqual(get_windows_next_space_number(self.mh10, 'open_space'), 1)

        def get_windows_direction_number(mh, key):
            return len([p for p in mh['windows'] if p['direction'] == key])

        self.assertEqual(get_windows_direction_number(self.mh1, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh1, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh1, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh1, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh2, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh2, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh2, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh2, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh3, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh3, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh3, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh3, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh4, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh4, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh4, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh4, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh5, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh5, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh5, 'horizontal'), 1)
        self.assertEqual(get_windows_direction_number(self.mh6, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh6, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh6, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh6, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh7, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh7, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh7, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh7, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh8, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh8, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh8, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh8, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh9, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh9, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh9, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh9, 'se'), 1)
        self.assertEqual(get_windows_direction_number(self.mh10, 'sw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh10, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh10, 'horizontal'), 1)

        def get_windows_area_with_direction(mh, key):
            return sorted([p['area'] for p in mh['windows'] if p['direction'] == key])

        self.assertAlmostEqual(get_windows_area_with_direction(self.mh1, 'sw')[0], 22.695293711200005)
        self.assertAlmostEqual(get_windows_area_with_direction(self.mh1, 'nw')[0], 2.3846264596)
        self.assertAlmostEqual(get_windows_area_with_direction(self.mh1, 'ne')[0], 3.628204197200001)
        self.assertAlmostEqual(get_windows_area_with_direction(self.mh1, 'se')[0], 4.365751632000001)

    def test_doors(self):

        def get_doors_number(mh):
            return len(mh['doors'])

        self.assertEqual(get_doors_number(self.mh1), 2)
        self.assertEqual(get_doors_number(self.mh2), 2)
        self.assertEqual(get_doors_number(self.mh3), 2)
        self.assertEqual(get_doors_number(self.mh4), 2)
        self.assertEqual(get_doors_number(self.mh5), 1)
        self.assertEqual(get_doors_number(self.mh6), 2)
        self.assertEqual(get_doors_number(self.mh7), 2)
        self.assertEqual(get_doors_number(self.mh8), 2)
        self.assertEqual(get_doors_number(self.mh9), 2)
        self.assertEqual(get_doors_number(self.mh10), 1)

        def get_doors_next_space_number(mh, key):
            return len([p for p in mh['doors'] if p['next_space'] == key])

        self.assertEqual(get_doors_next_space_number(self.mh1, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh2, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh3, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh4, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh5, 'open_space'), 1)
        self.assertEqual(get_doors_next_space_number(self.mh6, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh7, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh8, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh9, 'outdoor'), 2)
        self.assertEqual(get_doors_next_space_number(self.mh10, 'open_space'), 1)

        def get_windows_direction_number(mh, key):
            return len([p for p in mh['doors'] if p['direction'] == key])

        self.assertEqual(get_windows_direction_number(self.mh1, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh1, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh2, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh2, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh3, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh3, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh4, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh4, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh5, 'horizontal'), 1)
        self.assertEqual(get_windows_direction_number(self.mh6, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh6, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh7, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh7, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh8, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh8, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh9, 'nw'), 1)
        self.assertEqual(get_windows_direction_number(self.mh9, 'ne'), 1)
        self.assertEqual(get_windows_direction_number(self.mh10, 'horizontal'), 1)

        def get_doors_area_with_direction(mh, key):
            return sorted([p['area'] for p in mh['doors'] if p['direction'] == key])

        self.assertAlmostEqual(get_doors_area_with_direction(self.mh1, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh1, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh2, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh2, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh3, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh3, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh4, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh4, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh5, 'horizontal')[0], 1.755)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh6, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh6, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh7, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh7, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh8, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh8, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh9, 'nw')[0], 1.89)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh9, 'ne')[0], 1.62)
        self.assertAlmostEqual(get_doors_area_with_direction(self.mh10, 'horizontal')[0], 1.755)

    def test_earthfloor_perimeters(self):

        def get_earthfloor_perimeters_number(mh):
            return len(mh['earthfloor_perimeters'])

        self.assertEqual(get_earthfloor_perimeters_number(self.mh1), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh2), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh3), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh4), 4)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh5), 0)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh6), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh7), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh8), 3)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh9), 4)
        self.assertEqual(get_earthfloor_perimeters_number(self.mh10), 0)

        def get_earthfloor_perimeters_next_space_number(mh, key):
            return len([p for p in mh['earthfloor_perimeters'] if p['next_space'] == key])

        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh1, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh1, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh2, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh2, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh3, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh3, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh4, 'outdoor'), 4)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh6, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh6, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh7, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh7, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh8, 'outdoor'), 2)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh8, 'open_underfloor'), 1)
        self.assertEqual(get_earthfloor_perimeters_next_space_number(self.mh9, 'outdoor'), 4)

        def get_earthfloor_perimeters_length(mh):
            return sorted([p['length'] for p in mh['earthfloor_perimeters']])

        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh1)[0], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh1)[1], 3.64)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh1)[2], 6.825)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh2)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh2)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh2)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh3)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh3)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh3)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh4)[0], 4.7926264410438755)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh4)[1], 4.7926264410438755)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh4)[2], 10.60951823652745)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh4)[3], 10.60951823652745)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh6)[0], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh6)[1], 3.64)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh6)[2], 6.825)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh7)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh7)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh7)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh8)[0], 1.365)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh8)[1], 1.82)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh8)[2], 3.185)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh9)[0], 4.7924168280158135)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh9)[1], 4.7924168280158135)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh9)[2], 10.609982280729707)
        self.assertAlmostEqual(get_earthfloor_perimeters_length(self.mh9)[3], 10.609982280729707)

    def test_earthfloor_centers(self):

        def get_earthfloor_centers_number(mh):
            return len(mh['earthfloor_centers'])

        self.assertEqual(get_earthfloor_centers_number(self.mh1), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh2), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh3), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh4), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh5), 0)
        self.assertEqual(get_earthfloor_centers_number(self.mh6), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh7), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh8), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh9), 1)
        self.assertEqual(get_earthfloor_centers_number(self.mh10), 0)

        def get_earthfloor_centers_area(mh):
            return sorted([p['area'] for p in mh['earthfloor_centers']])

        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh1)[0], 5.7967)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh2)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh3)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh4)[0], 50.847457627118644)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh6)[0], 5.7967)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh7)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh8)[0], 2.4843)
        self.assertAlmostEqual(get_earthfloor_centers_area(self.mh9)[0], 50.847457627118644)


if __name__ == '__main__':
    unittest.main()
