import unittest
import os, json
import itertools
from typing import Dict, List
import numpy as np

from heat_load_calc.schedule import Schedule


class TestInterval(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # テストするインデックス
        # カレンダーは、　"休日在", "平日", "平日", "平日", "平日", "平日", "休日在", "休日外", ...
        # なので、すべてのパターンが試せるように、1/1, 1/2, 1/8 のそれぞれ96時間分をテストする。
        cls._test_indices = list(range(0, 96)) + list(range(96*1, 96*2)) + list(range(96*7, 96*8))

        schedule_file_path = os.path.join(os.path.dirname(__file__), "schedules_for_test.json")
        with open(schedule_file_path, 'r', encoding='utf-8') as js:
            rd = json.load(js)

        cls._mor = rd["daily_schedule"]["main_occupant_room"]
        cls._oor = rd["daily_schedule"]["other_occupant_room"]
        cls._nor = rd["daily_schedule"]["non_occupant_room"]
        cls._zero = rd["daily_schedule"]["zero"]

    def test_one(self):

        a_floor_is = [10.0, 10.0, 10.0, 10.0]

        s = Schedule.get_schedule(
            number_of_occupants='1',
            s_name_is=['main_occupant_room', 'other_occupant_room', 'non_occupant_room', 'zero'],
            a_floor_is=a_floor_is
        )

        test_patterns = self.make_test_patterns_all(d=self._mor, nop=1, a_floor_is=a_floor_is)

        # for i, expected in zip(self._test_indices, test_patterns["q_gen_is_ns"]):
        #     with self.subTest(i=i, expected=expected):
        #         self.assertEqual(s.q_gen_is_ns[0, i], expected)
        #
        # for i, expected in zip(self._test_indices, test_patterns["x_gen_is_ns"]):
        #     with self.subTest(i=i, result=s.x_gen_is_ns[0, i], expected=expected):
        #         self.assertEqual(s.x_gen_is_ns[0, i], expected)

        for i, expected in zip(self._test_indices, test_patterns["v_mec_vent_local_is_ns"]):
            with self.subTest(i=i, result=s.x_gen_is_ns[0, i], expected=expected):
                self.assertEqual(s.v_mec_vent_local_is_ns[0, i], expected)

        for i, expected in zip(self._test_indices, test_patterns["n_hum_is_ns"]):
            with self.subTest(i=i, result=s.x_gen_is_ns[0, i], expected=expected):
                self.assertEqual(s.n_hum_is_ns[0, i], expected)

        for i, expected in zip(self._test_indices, test_patterns["ac_demand_is_ns"]):
            with self.subTest(i=i, result=s.x_gen_is_ns[0, i], expected=expected):
                self.assertEqual(s.ac_demand_is_ns[0, i], expected)


    @classmethod
    def make_test_patterns_all(cls, d:Dict, nop: int, a_floor_is: List[float]):

        v_mec_vent_local_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="local_vent_amount") / 3600

        q_gen_app_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="heat_generation_appliances")

        q_gen_ckg_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="heat_generation_cooking")

        x_gen_ckg_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="vapor_generation_cooking") / 1000.0 / 3600.0

        q_gen_lght_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="heat_generation_lighting")

        n_hum_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="number_of_people")

        ac_demand_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="is_temp_limit_set")

        a_floor_is = np.array(a_floor_is)

        # ステップ n の室 i における人体発熱を除く内部発熱, W, [i, n]
        q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * a_floor_is[:, np.newaxis]

        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n]
        x_gen_is_ns = x_gen_ckg_is_ns

        return {
            "q_gen_is_ns": q_gen_is_ns,
            "x_gen_is_ns": x_gen_is_ns,
            "v_mec_vent_local_is_ns": v_mec_vent_local_is_ns,
            "n_hum_is_ns": n_hum_is_ns,
            "ac_demand_is_ns": ac_demand_is_ns
        }

    @classmethod
    def make_test_patterns(cls, d: Dict, nop: int, target_key: str):

        ds = [d[str(nop)][p][target_key] for p in ["休日在", "平日", "休日外"]]
        return np.array(list(itertools.chain(*ds)))
