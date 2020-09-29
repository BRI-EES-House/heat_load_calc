import unittest
import standard_house_area as sha


class TestStandardHouseArea(unittest.TestCase):

    def test_area(self):

        gps, ws, iws = sha.get_area(
            a_f_total=120.0,
            a_f_mr=60.0,
            a_f_or=30.0,
            a_evp_total=360.0,
            house_type='condominium'
        )

        gp = gps[0]
        self.assertEqual(gp['name'], 'ceiling_main_occupant_room')
        self.assertEqual(gp['general_part_type'], 'ceiling')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'top')
        self.assertEqual(gp['area'], 60.0)
        self.assertEqual(gp['space_type'], 'main_occupant_room')

        gp = gps[1]
        self.assertEqual(gp['name'], 'ceiling_other_occupant_room')
        self.assertEqual(gp['general_part_type'], 'ceiling')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'top')
        self.assertEqual(gp['area'], 30.0)
        self.assertEqual(gp['space_type'], 'other_occupant_room')

        gp = gps[2]
        self.assertEqual(gp['name'], 'ceiling_non_occupant_room')
        self.assertEqual(gp['general_part_type'], 'ceiling')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'top')
        self.assertEqual(gp['area'], 30.0)
        self.assertEqual(gp['space_type'], 'non_occupant_room')

        gp = gps[3]
        self.assertEqual(gp['name'], 'floor_main_occupant_room')
        self.assertEqual(gp['general_part_type'], 'floor')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'bottom')
        self.assertEqual(gp['area'], 60.0)
        self.assertEqual(gp['space_type'], 'main_occupant_room')

        gp = gps[4]
        self.assertEqual(gp['name'], 'floor_other_occupant_room')
        self.assertEqual(gp['general_part_type'], 'floor')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'bottom')
        self.assertEqual(gp['area'], 30.0)
        self.assertEqual(gp['space_type'], 'other_occupant_room')

        gp = gps[5]
        self.assertEqual(gp['name'], 'floor_non_occupant_room')
        self.assertEqual(gp['general_part_type'], 'floor')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'bottom')
        self.assertEqual(gp['area'], 30.0)
        self.assertEqual(gp['space_type'], 'non_occupant_room')

        gp = gps[6]
        self.assertEqual(gp['name'], 'wall_n_other_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'n')
        self.assertEqual(gp['area'], 25.213980934427887)
        self.assertEqual(gp['space_type'], 'other_occupant_room')

        gp = gps[7]
        self.assertEqual(gp['name'], 'wall_s_main_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 's')
        self.assertEqual(gp['area'], 14.601675839125225)
        self.assertEqual(gp['space_type'], 'main_occupant_room')

        gp = gps[8]
        self.assertEqual(gp['name'], 'wall_e_main_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'e')
        self.assertEqual(gp['area'], 15.336231610144651)
        self.assertEqual(gp['space_type'], 'main_occupant_room')

        gp = gps[9]
        self.assertEqual(gp['name'], 'wall_e_other_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'e')
        self.assertEqual(gp['area'], 7.6681158050723255)
        self.assertEqual(gp['space_type'], 'other_occupant_room')

        gp = gps[10]
        self.assertEqual(gp['name'], 'wall_e_non_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'e')
        self.assertEqual(gp['area'], 7.6681158050723255)
        self.assertEqual(gp['space_type'], 'non_occupant_room')

        gp = gps[11]
        self.assertEqual(gp['name'], 'wall_w_main_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'w')
        self.assertEqual(gp['area'], 13.406721592816895)
        self.assertEqual(gp['space_type'], 'main_occupant_room')

        gp = gps[12]
        self.assertEqual(gp['name'], 'wall_w_other_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'w')
        self.assertEqual(gp['area'], 6.703360796408448)
        self.assertEqual(gp['space_type'], 'other_occupant_room')

        gp = gps[13]
        self.assertEqual(gp['name'], 'wall_w_non_occupant_room')
        self.assertEqual(gp['general_part_type'], 'wall')
        self.assertEqual(gp['next_space'], 'outdoor')
        self.assertEqual(gp['external_surface_type'], 'outdoor')
        self.assertEqual(gp['direction'], 'w')
        self.assertEqual(gp['area'], 6.703360796408448)
        self.assertEqual(gp['space_type'], 'non_occupant_room')

        w = ws[0]
        self.assertEqual(w['name'], 'n_other_occupant_room')
        self.assertEqual(w['next_space'], 'outdoor')
        self.assertEqual(w['direction'], 'n')
        self.assertEqual(w['area'], 5.458482285861416)
        self.assertEqual(w['space_type'], 'other_occupant_room')

        w = ws[1]
        self.assertEqual(w['name'], 's_main_occupant_room')
        self.assertEqual(w['next_space'], 'outdoor')
        self.assertEqual(w['direction'], 's')
        self.assertEqual(w['area'], 16.070787381164077)
        self.assertEqual(w['space_type'], 'main_occupant_room')

        w = ws[2]
        self.assertEqual(w['name'], 'w_main_occupant_room')
        self.assertEqual(w['next_space'], 'outdoor')
        self.assertEqual(w['direction'], 'w')
        self.assertEqual(w['area'], 1.9295100173277564)
        self.assertEqual(w['space_type'], 'main_occupant_room')

        w = ws[3]
        self.assertEqual(w['name'], 'w_other_occupant_room')
        self.assertEqual(w['next_space'], 'outdoor')
        self.assertEqual(w['direction'], 'w')
        self.assertEqual(w['area'], 0.9647550086638782)
        self.assertEqual(w['space_type'], 'other_occupant_room')

        w = ws[4]
        self.assertEqual(w['name'], 'w_non_occupant_room')
        self.assertEqual(w['next_space'], 'outdoor')
        self.assertEqual(w['direction'], 'w')
        self.assertEqual(w['area'], 0.9647550086638782)
        self.assertEqual(w['space_type'], 'non_occupant_room')

        iw = iws[0]
        self.assertEqual(iw['name'], 'inner_wall_main to other')
        self.assertEqual(iw['area'], 30.672463220289302)
        self.assertEqual(iw['space_type'], 'main to other')
        self.assertEqual(iw['type'], 'inner_wall')

        iw = iws[1]
        self.assertEqual(iw['name'], 'inner_wall_main to nonliving')
        self.assertEqual(iw['area'], 30.672463220289302)
        self.assertEqual(iw['space_type'], 'main to nonliving')
        self.assertEqual(iw['type'], 'inner_wall')

        iw = iws[2]
        self.assertEqual(iw['name'], 'inner_wall_other to nonliving')
        self.assertEqual(iw['area'], 30.672463220289302)
        self.assertEqual(iw['space_type'], 'other to nonliving')
        self.assertEqual(iw['type'], 'inner_wall')


if __name__ == '__main__':
    unittest.main()