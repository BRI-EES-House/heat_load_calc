import unittest

import heat_load_calc.convert.convert_indices_to_lv2_info as t
import heat_load_calc.convert.check_ua_a_eta_a as cue


class TestConvertIndicesToLv2Info(unittest.TestCase):

    def test_convert_spec(self):

        input_data_1 = {
            'common': {
                'region': 6,
                'house_type': 'detached',
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 30.0,
                'total_floor_area': 90.0,
            },
            'envelope': {
                'input_method': 'index',
                'total_area': 266.0962919879752,
                'indices': {
                    'u_a': 0.87,
                    'eta_a_h': 2.8,
                    'eta_a_c': 1.4
                }
            }
        }

        result, _ = t.convert_spec(d=input_data_1)

        self.assertEqual('detail_without_room_usage', result['input_method'])

        gps = result['general_parts']

        gp = gps[0]
        self.assertEqual('roof', gp['name'])
        self.assertEqual('ceiling', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('top', gp['direction'])
        self.assertEqual(50.847457627118644, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.24097182568280665, spec['u_value_other'])

        gp = gps[1]
        self.assertEqual('wall_sw', gp['name'])
        self.assertEqual('wall', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('sw', gp['direction'])
        self.assertEqual(37.64267180619973, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.5321461150495314, spec['u_value_other'])

        gp = gps[2]
        self.assertEqual('wall_nw', gp['name'])
        self.assertEqual('wall', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('nw', gp['direction'])
        self.assertEqual(23.121235617221057, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.5321461150495314, spec['u_value_other'])

        gp = gps[3]
        self.assertEqual('wall_ne', gp['name'])
        self.assertEqual('wall', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('ne', gp['direction'])
        self.assertEqual(49.063660549306505, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.5321461150495314, spec['u_value_other'])

        gp = gps[4]
        self.assertEqual('wall_se', gp['name'])
        self.assertEqual('wall', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('se', gp['direction'])
        self.assertEqual(23.656239562213084, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.5321461150495314, spec['u_value_other'])

        gp = gps[5]
        self.assertEqual('floor', gp['name'])
        self.assertEqual('floor', gp['general_part_type'])
        self.assertEqual('open_underfloor', gp['next_space'])
        self.assertEqual('downward', gp['direction'])
        self.assertEqual(45.05075762711864, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.4819436513656133, spec['u_value_other'])

        gp = gps[6]
        self.assertEqual('base_outside_nw', gp['name'])
        self.assertEqual('wall', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('nw', gp['direction'])
        self.assertEqual(1.2376, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.5321461150495314, spec['u_value_other'])

        gp = gps[7]
        self.assertEqual('base_outside_ne', gp['name'])
        self.assertEqual('wall', gp['general_part_type'])
        self.assertEqual('outdoor', gp['next_space'])
        self.assertEqual('ne', gp['direction'])
        self.assertEqual(1.1557, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.5321461150495314, spec['u_value_other'])

        gp = gps[8]
        self.assertEqual('base_iside', gp['name'])
        self.assertEqual('wall', gp['general_part_type'])
        self.assertEqual('open_underfloor', gp['next_space'])
        self.assertEqual('horizontal', gp['direction'])
        self.assertEqual(2.3933, gp['area'])
        self.assertEqual(None, gp['space_type'])
        self.assertEqual(False, gp['is_sunshade_input'])
        spec = gp['spec']
        self.assertEqual('other', spec['structure'])
        self.assertEqual(0.5321461150495314, spec['u_value_other'])

        ws = result['windows']

        w = ws[0]
        self.assertEqual('window_sw', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('sw', w['direction'])
        self.assertEqual(15.522509064214855, w['area'])
        self.assertEqual(None, w['space_type'])
        self.assertEqual(False, w['is_sunshade_input'])
        spec = w['spec']
        self.assertEqual('single', spec['window_type'])
        self.assertEqual('u_value_directly', spec['windows'][0]['u_value_input_method'])
        self.assertEqual(4.66882912260438, spec['windows'][0]['u_value'])
        self.assertEqual('eta_d_value_directly', spec['windows'][0]['eta_value_input_method'])
        self.assertEqual(0.34657203976617956, spec['windows'][0]['eta_d_value'])
        self.assertEqual(0.5010751618181039, spec['windows'][0]['eta_d_h_value'])
        self.assertEqual(0.19206891771425533, spec['windows'][0]['eta_d_c_value'])
        self.assertEqual('single', spec['windows'][0]['glass_type'])
        self.assertEqual('none', spec['attachment_type'])
        self.assertEqual('none', spec['is_windbreak_room_attached'])
        self.assertEqual(True, spec['is_sunshade_input'])
        self.assertEqual(True, spec['sunshade']['existence'])
        self.assertEqual('simple', spec['sunshade']['input_method'])
        self.assertEqual(0.3, spec['sunshade']['depth'])
        self.assertEqual(1.0, spec['sunshade']['d_h'])
        self.assertEqual(0.0, spec['sunshade']['d_e'])
        self.assertEqual(None, spec['sunshade']['x1'])
        self.assertEqual(None, spec['sunshade']['x2'])
        self.assertEqual(None, spec['sunshade']['x3'])
        self.assertEqual(None, spec['sunshade']['y1'])
        self.assertEqual(None, spec['sunshade']['y2'])
        self.assertEqual(None, spec['sunshade']['y3'])
        self.assertEqual(None, spec['sunshade']['z_x_pls'])
        self.assertEqual(None, spec['sunshade']['z_x_mns'])
        self.assertEqual(None, spec['sunshade']['z_y_pls'])
        self.assertEqual(None, spec['sunshade']['z_y_mns'])
        self.assertEqual(None, spec['sunshade']['x3'])

        w = ws[1]
        self.assertEqual('window_nw', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('nw', w['direction'])
        self.assertEqual(1.6309718792333008, w['area'])
        self.assertEqual(None, w['space_type'])
        self.assertEqual(False, w['is_sunshade_input'])
        spec = w['spec']
        self.assertEqual('single', spec['window_type'])
        self.assertEqual('u_value_directly', spec['windows'][0]['u_value_input_method'])
        self.assertEqual(4.66882912260438, spec['windows'][0]['u_value'])
        self.assertEqual('eta_d_value_directly', spec['windows'][0]['eta_value_input_method'])
        self.assertEqual(0.34657203976617956, spec['windows'][0]['eta_d_value'])
        self.assertEqual(0.5010751618181039, spec['windows'][0]['eta_d_h_value'])
        self.assertEqual(0.19206891771425533, spec['windows'][0]['eta_d_c_value'])
        self.assertEqual('single', spec['windows'][0]['glass_type'])
        self.assertEqual('none', spec['attachment_type'])
        self.assertEqual('none', spec['is_windbreak_room_attached'])
        self.assertEqual(True, spec['is_sunshade_input'])
        self.assertEqual(True, spec['sunshade']['existence'])
        self.assertEqual('simple', spec['sunshade']['input_method'])
        self.assertEqual(0.3, spec['sunshade']['depth'])
        self.assertEqual(1.0, spec['sunshade']['d_h'])
        self.assertEqual(0.0, spec['sunshade']['d_e'])
        self.assertEqual(None, spec['sunshade']['x1'])
        self.assertEqual(None, spec['sunshade']['x2'])
        self.assertEqual(None, spec['sunshade']['x3'])
        self.assertEqual(None, spec['sunshade']['y1'])
        self.assertEqual(None, spec['sunshade']['y2'])
        self.assertEqual(None, spec['sunshade']['y3'])
        self.assertEqual(None, spec['sunshade']['z_x_pls'])
        self.assertEqual(None, spec['sunshade']['z_x_mns'])
        self.assertEqual(None, spec['sunshade']['z_y_pls'])
        self.assertEqual(None, spec['sunshade']['z_y_mns'])
        self.assertEqual(None, spec['sunshade']['x3'])

        w = ws[2]
        self.assertEqual('window_ne', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('ne', w['direction'])
        self.assertEqual(2.4815203211080874, w['area'])
        self.assertEqual(None, w['space_type'])
        self.assertEqual(False, w['is_sunshade_input'])
        spec = w['spec']
        self.assertEqual('single', spec['window_type'])
        self.assertEqual('u_value_directly', spec['windows'][0]['u_value_input_method'])
        self.assertEqual(4.66882912260438, spec['windows'][0]['u_value'])
        self.assertEqual('eta_d_value_directly', spec['windows'][0]['eta_value_input_method'])
        self.assertEqual(0.34657203976617956, spec['windows'][0]['eta_d_value'])
        self.assertEqual(0.5010751618181039, spec['windows'][0]['eta_d_h_value'])
        self.assertEqual(0.19206891771425533, spec['windows'][0]['eta_d_c_value'])
        self.assertEqual('single', spec['windows'][0]['glass_type'])
        self.assertEqual('none', spec['attachment_type'])
        self.assertEqual('none', spec['is_windbreak_room_attached'])
        self.assertEqual(True, spec['is_sunshade_input'])
        self.assertEqual(True, spec['sunshade']['existence'])
        self.assertEqual('simple', spec['sunshade']['input_method'])
        self.assertEqual(0.3, spec['sunshade']['depth'])
        self.assertEqual(1.0, spec['sunshade']['d_h'])
        self.assertEqual(0.0, spec['sunshade']['d_e'])
        self.assertEqual(None, spec['sunshade']['x1'])
        self.assertEqual(None, spec['sunshade']['x2'])
        self.assertEqual(None, spec['sunshade']['x3'])
        self.assertEqual(None, spec['sunshade']['y1'])
        self.assertEqual(None, spec['sunshade']['y2'])
        self.assertEqual(None, spec['sunshade']['y3'])
        self.assertEqual(None, spec['sunshade']['z_x_pls'])
        self.assertEqual(None, spec['sunshade']['z_x_mns'])
        self.assertEqual(None, spec['sunshade']['z_y_pls'])
        self.assertEqual(None, spec['sunshade']['z_y_mns'])
        self.assertEqual(None, spec['sunshade']['x3'])

        w = ws[3]
        self.assertEqual('window_se', w['name'])
        self.assertEqual('outdoor', w['next_space'])
        self.assertEqual('se', w['direction'])
        self.assertEqual(2.985967934241272, w['area'])
        self.assertEqual(None, w['space_type'])
        self.assertEqual(False, w['is_sunshade_input'])
        spec = w['spec']
        self.assertEqual('single', spec['window_type'])
        self.assertEqual('u_value_directly', spec['windows'][0]['u_value_input_method'])
        self.assertEqual(4.66882912260438, spec['windows'][0]['u_value'])
        self.assertEqual('eta_d_value_directly', spec['windows'][0]['eta_value_input_method'])
        self.assertEqual(0.34657203976617956, spec['windows'][0]['eta_d_value'])
        self.assertEqual(0.5010751618181039, spec['windows'][0]['eta_d_h_value'])
        self.assertEqual(0.19206891771425533, spec['windows'][0]['eta_d_c_value'])
        self.assertEqual('single', spec['windows'][0]['glass_type'])
        self.assertEqual('none', spec['attachment_type'])
        self.assertEqual('none', spec['is_windbreak_room_attached'])
        self.assertEqual(True, spec['is_sunshade_input'])
        self.assertEqual(True, spec['sunshade']['existence'])
        self.assertEqual('simple', spec['sunshade']['input_method'])
        self.assertEqual(0.3, spec['sunshade']['depth'])
        self.assertEqual(1.0, spec['sunshade']['d_h'])
        self.assertEqual(0.0, spec['sunshade']['d_e'])
        self.assertEqual(None, spec['sunshade']['x1'])
        self.assertEqual(None, spec['sunshade']['x2'])
        self.assertEqual(None, spec['sunshade']['x3'])
        self.assertEqual(None, spec['sunshade']['y1'])
        self.assertEqual(None, spec['sunshade']['y2'])
        self.assertEqual(None, spec['sunshade']['y3'])
        self.assertEqual(None, spec['sunshade']['z_x_pls'])
        self.assertEqual(None, spec['sunshade']['z_x_mns'])
        self.assertEqual(None, spec['sunshade']['z_y_pls'])
        self.assertEqual(None, spec['sunshade']['z_y_mns'])
        self.assertEqual(None, spec['sunshade']['x3'])

        ds = result['doors']

        d = ds[0]
        self.assertEqual('door_nw', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('nw', d['direction'])
        self.assertEqual(1.89, d['area'])
        self.assertEqual(None, d['space_type'])
        spec = d['spec']
        self.assertEqual(4.66882912260438, spec['u_value'])
        self.assertEqual(False, spec['is_sunshade_input'])

        d = ds[1]
        self.assertEqual('door_ne', d['name'])
        self.assertEqual('outdoor', d['next_space'])
        self.assertEqual('ne', d['direction'])
        self.assertEqual(1.62, d['area'])
        self.assertEqual(None, d['space_type'])
        spec = d['spec']
        self.assertEqual(4.66882912260438, spec['u_value'])
        self.assertEqual(False, spec['is_sunshade_input'])

        eps = result['earthfloor_perimeters']

        ep = eps[0]
        self.assertEqual('earth_floor_perimeter_nw', ep['name'])
        self.assertEqual('outdoor', ep['next_space'])
        self.assertEqual(3.64, ep['length'])
        self.assertEqual(None, ep['space_type'])
        spec = ep['spec']
        self.assertEqual(0.7630774479955544, spec['psi_value'])

        ep = eps[1]
        self.assertEqual('earth_floor_perimeter_ne', ep['name'])
        self.assertEqual('outdoor', ep['next_space'])
        self.assertEqual(3.185, ep['length'])
        self.assertEqual(None, ep['space_type'])
        spec = ep['spec']
        self.assertEqual(0.7630774479955544, spec['psi_value'])

        ep = eps[2]
        self.assertEqual('earth_floor_perimeter_inside', ep['name'])
        self.assertEqual('open_underfloor', ep['next_space'])
        self.assertEqual(6.825, ep['length'])
        self.assertEqual(None, ep['space_type'])
        spec = ep['spec']
        self.assertEqual(0.7630774479955544, spec['psi_value'])

        ecs = result['earthfloor_centers']

        ec = ecs[0]
        self.assertEqual('earth_floor', ec['name'])
        self.assertEqual(5.7967, ec['area'])
        self.assertEqual(None, ec['space_type'])
        spec = ec['spec']
        self.assertEqual(False, spec['is_layers_input'])

    def test_check_u_a_eta_a(self):

        input_data_1 = {
            'common': {
                'region': 6,
                'house_type': 'detached',
                'main_occupant_room_floor_area': 30.0,
                'other_occupant_room_floor_area': 30.0,
                'total_floor_area': 90.0,
            },
            'envelope': {
                'input_method': 'index',
                'total_area': 266.0962919879752,
                'indices': {
                    'u_a': 0.87,
                    'eta_a_h': 2.8,
                    'eta_a_c': 1.4
                }
            }
        }

        result, sunshade = t.convert_spec(d=input_data_1)

        checked_u_a1, checked_eta_a_h1, checked_eta_a_c1 = cue.check_u_a_and_eta_a(
            region=input_data_1['common']['region'],
            model_house_envelope=result
        )

        indices = input_data_1['envelope']['indices']

        self.assertAlmostEqual(indices['u_a'], checked_u_a1)
        self.assertAlmostEqual(indices['eta_a_h'], checked_eta_a_h1)
        self.assertAlmostEqual(indices['eta_a_c'], checked_eta_a_c1)


if __name__ == '__main__':
    unittest.main()
