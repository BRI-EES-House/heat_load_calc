import unittest
import os, json
import itertools
from typing import Dict, List
import numpy as np

from heat_load_calc.schedule import Schedule


class TestSchedule(unittest.TestCase):

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

        cls._s_name_is = ['main_occupant_room', 'other_occupant_room', 'non_occupant_room', 'zero']

    def test_one(self):

        a_floor_is = [10.0, 10.0, 10.0, 10.0]

        s = Schedule.get_schedule(number_of_occupants='1', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=1, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_two(self):

        a_floor_is = [10.0, 10.0, 10.0, 10.0]

        s = Schedule.get_schedule(number_of_occupants='2', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=2, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_three(self):

        a_floor_is = [10.0, 10.0, 10.0, 10.0]

        s = Schedule.get_schedule(number_of_occupants='3', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=3, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_four(self):

        a_floor_is = [10.0, 10.0, 10.0, 10.0]

        s = Schedule.get_schedule(number_of_occupants='4', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=4, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_auto_20(self):

        a_floor_is = [5.0, 5.0, 5.0, 5.0]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=1, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_auto_30(self):

        a_floor_is = [7.5, 7.5, 7.5, 7.5]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=1, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_auto_40(self):

        a_floor_is = [10.0, 10.0, 10.0, 10.0]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns_30 = self.make_test_patterns_all(d=d, nop=1, a_floor_i=a_floor_is[i])
            test_patterns_60 = self.make_test_patterns_all(d=d, nop=2, a_floor_i=a_floor_is[i])

            test_patterns = {
                "q_gen_is_ns": test_patterns_30["q_gen_is_ns"] * 2 / 3 + test_patterns_60["q_gen_is_ns"] * 1 / 3,
                "x_gen_is_ns": test_patterns_30["x_gen_is_ns"] * 2 / 3 + test_patterns_60["x_gen_is_ns"] * 1 / 3,
                "v_mec_vent_local_is_ns": test_patterns_30["v_mec_vent_local_is_ns"] * 2 / 3 + test_patterns_60["v_mec_vent_local_is_ns"] * 1 / 3,
                "n_hum_is_ns": test_patterns_30["n_hum_is_ns"] * 2 / 3 + test_patterns_60["n_hum_is_ns"] * 1 / 3,
                "ac_demand_is_ns": test_patterns_30["ac_demand_is_ns"] * 2 / 3 + test_patterns_60["ac_demand_is_ns"] * 1 / 3
            }

            self.check(i=i, s=s, test_patterns=test_patterns, is_almost=True)

    def test_auto_60(self):

        a_floor_is = [15.0, 15.0, 15.0, 15.0]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=2, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_auto_80(self):

        a_floor_is = [20.0, 20.0, 20.0, 20.0]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns_60 = self.make_test_patterns_all(d=d, nop=2, a_floor_i=a_floor_is[i])
            test_patterns_90 = self.make_test_patterns_all(d=d, nop=3, a_floor_i=a_floor_is[i])

            test_patterns = {
                "q_gen_is_ns": test_patterns_60["q_gen_is_ns"] * 1 / 3 + test_patterns_90["q_gen_is_ns"] * 2 / 3,
                "x_gen_is_ns": test_patterns_60["x_gen_is_ns"] * 1 / 3 + test_patterns_90["x_gen_is_ns"] * 2 / 3,
                "v_mec_vent_local_is_ns": test_patterns_60["v_mec_vent_local_is_ns"] * 1 / 3 + test_patterns_90["v_mec_vent_local_is_ns"] * 2 / 3,
                "n_hum_is_ns": test_patterns_60["n_hum_is_ns"] * 1 / 3 + test_patterns_90["n_hum_is_ns"] * 2 / 3,
                "ac_demand_is_ns": test_patterns_60["ac_demand_is_ns"] * 1 / 3 + test_patterns_90["ac_demand_is_ns"] * 2 / 3
            }

            self.check(i=i, s=s, test_patterns=test_patterns, is_almost=True)

    def test_auto_90(self):

        a_floor_is = [22.5, 22.5, 22.5, 22.5]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=3, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_auto_105(self):

        a_floor_is = [26.25, 26.25, 26.25, 26.25]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns_90 = self.make_test_patterns_all(d=d, nop=3, a_floor_i=a_floor_is[i])
            test_patterns_120 = self.make_test_patterns_all(d=d, nop=4, a_floor_i=a_floor_is[i])

            test_patterns = {
                "q_gen_is_ns": test_patterns_90["q_gen_is_ns"] * 1 / 2 + test_patterns_120["q_gen_is_ns"] * 1 / 2,
                "x_gen_is_ns": test_patterns_90["x_gen_is_ns"] * 1 / 2 + test_patterns_120["x_gen_is_ns"] * 1 / 2,
                "v_mec_vent_local_is_ns": test_patterns_90["v_mec_vent_local_is_ns"] * 1 / 2 + test_patterns_120["v_mec_vent_local_is_ns"] * 1 / 2,
                "n_hum_is_ns": test_patterns_90["n_hum_is_ns"] * 1 / 2 + test_patterns_120["n_hum_is_ns"] * 1 / 2,
                "ac_demand_is_ns": test_patterns_90["ac_demand_is_ns"] * 1 / 2 + test_patterns_120["ac_demand_is_ns"] * 1 / 2
            }

            self.check(i=i, s=s, test_patterns=test_patterns, is_almost=True)

    def test_auto_120(self):

        a_floor_is = [30.0, 30.0, 30.0, 30.0]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=4, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def test_auto_150(self):

        a_floor_is = [37.5, 37.5, 37.5, 37.5]

        s = Schedule.get_schedule(number_of_occupants='auto', s_name_is=self._s_name_is, a_floor_is=a_floor_is)

        for i, d in zip([0, 1, 2, 3], [self._mor, self._oor, self._nor, self._zero]):

            test_patterns = self.make_test_patterns_all(d=d, nop=4, a_floor_i=a_floor_is[i])

            self.check(i=i, s=s, test_patterns=test_patterns)

    def check(self, i: int, s: Schedule, test_patterns: Dict, is_almost=False):

        if is_almost:
            for n, expected in zip(self._test_indices, test_patterns["q_gen_is_ns"]):
                with self.subTest(name="q_gen", n=n, i=i, results=s.q_gen_is_ns[i, n], expected=expected):
                    self.assertAlmostEqual(s.q_gen_is_ns[i, n], expected)

            for n, expected in zip(self._test_indices, test_patterns["x_gen_is_ns"]):
                with self.subTest(name="x_gen", n=n, i=i, result=s.x_gen_is_ns[i, n], expected=expected):
                    self.assertAlmostEqual(s.x_gen_is_ns[i, n], expected)

            for n, expected in zip(self._test_indices, test_patterns["v_mec_vent_local_is_ns"]):
                with self.subTest(name="v_mec", n=n, i=i, result=s.x_gen_is_ns[i, n], expected=expected):
                    self.assertAlmostEqual(s.v_mec_vent_local_is_ns[i, n], expected)

            for n, expected in zip(self._test_indices, test_patterns["n_hum_is_ns"]):
                with self.subTest(name="n_hum", n=n, i=i, result=s.x_gen_is_ns[i, n], expected=expected):
                    self.assertAlmostEqual(s.n_hum_is_ns[i, n], expected)

            for n, expected in zip(self._test_indices, test_patterns["ac_demand_is_ns"]):
                with self.subTest(name="ac_demand", n=n, i=i, result=s.x_gen_is_ns[i, n], expected=expected):
                    self.assertAlmostEqual(s.ac_demand_is_ns[i, n], expected)
        else:
            self.assertTrue((s.q_gen_is_ns[i][self._test_indices] == test_patterns["q_gen_is_ns"]).all())
            self.assertTrue((s.x_gen_is_ns[i][self._test_indices] == test_patterns["x_gen_is_ns"]).all())
            self.assertTrue((s.v_mec_vent_local_is_ns[i][self._test_indices] == test_patterns["v_mec_vent_local_is_ns"]).all())
            self.assertTrue((s.n_hum_is_ns[i][self._test_indices] == test_patterns["n_hum_is_ns"]).all())
            self.assertTrue((s.ac_demand_is_ns[i][self._test_indices] == test_patterns["ac_demand_is_ns"]).all())

    @classmethod
    def make_test_patterns_all(cls, d:Dict, nop: int, a_floor_i: List[float]):

        v_mec_vent_local_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="local_vent_amount") / 3600

        q_gen_app_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="heat_generation_appliances")

        q_gen_ckg_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="heat_generation_cooking")

        x_gen_ckg_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="vapor_generation_cooking") / 1000.0 / 3600.0

        q_gen_lght_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="heat_generation_lighting")

        n_hum_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="number_of_people")

        ac_demand_is_ns = cls.make_test_patterns(d=d, nop=nop, target_key="is_temp_limit_set")

        q_gen_is_ns = q_gen_app_is_ns + q_gen_ckg_is_ns + q_gen_lght_is_ns * a_floor_i

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
