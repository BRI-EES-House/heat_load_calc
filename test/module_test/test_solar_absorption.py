import unittest
import numpy as np

from heat_load_calc import solar_absorption


class TestSolarAbsorption(unittest.TestCase):

    q_trs_sol_is_ns = np.array([
        [100.0, 101.0, 102.0, 103.0, 104.0],
        [105.0, 106.0, 107.0, 108.0, 109.0],
        [110.0, 111.0, 112.0, 113.0, 114.0]
    ])

    p_is_js = np.array([
        [1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 1]
    ])

    a_s_js = np.array([15.0, 20.0, 10.0, 30.0, 25.0, 5.0]).reshape(-1, 1)

    p_s_sol_abs_js = np.array([True, True, True, False, False, True]).reshape(-1, 1)

    r_sol_frt_is = np.array([0.5, 0.0, 0.3]).reshape(-1, 1)


    def test_get_q_sol_frt(self):

        result = solar_absorption.get_q_sol_frt_is_ns(q_trs_sor_is_ns=self.q_trs_sol_is_ns, r_sol_frt_is=self.r_sol_frt_is)

        self.assertAlmostEqual(result[0][0], 50.0)
        self.assertAlmostEqual(result[1][0], 0.0)
        self.assertAlmostEqual(result[2][0], 33.0)
    
    def test_get_a_s_abs(self):

        result = solar_absorption._get_a_s_abs_is(
            p_is_js=self.p_is_js,
            a_s_js=self.a_s_js,
            p_s_sol_abs_js=self.p_s_sol_abs_js
        )

        self.assertAlmostEqual(result[0], 35.0)
        self.assertAlmostEqual(result[1], 10.0)
        self.assertAlmostEqual(result[2], 5.0)
    
    def test_get_q_s_sol(self):

        result = solar_absorption.get_q_s_sol_js_ns(
            p_is_js=self.p_is_js,
            a_s_js=self.a_s_js,
            p_s_sol_abs_js=self.p_s_sol_abs_js,
            p_js_is=self.p_is_js.T,
            q_trs_sol_is_ns=self.q_trs_sol_is_ns,
            r_sol_frt_is=self.r_sol_frt_is
        )

        r = np.array([
            [1/35.0, 0.0,    0.0   ],
            [1/35.0, 0.0,    0.0   ],
            [0.0,    1/10.0, 0.0   ],
            [0.0,    0.0,    0.0   ],
            [0.0,    0.0,    0.0   ],
            [0.0,    0.0,    1/5.0 ],
        ])

        self.assertAlmostEqual(result[0][0], np.dot(r * 0.5, self.q_trs_sol_is_ns)[0][0])
        self.assertAlmostEqual(result[0][1], np.dot(r * 0.5, self.q_trs_sol_is_ns)[0][1])
        self.assertAlmostEqual(result[0][2], np.dot(r * 0.5, self.q_trs_sol_is_ns)[0][2])
        self.assertAlmostEqual(result[0][3], np.dot(r * 0.5, self.q_trs_sol_is_ns)[0][3])
        self.assertAlmostEqual(result[0][4], np.dot(r * 0.5, self.q_trs_sol_is_ns)[0][4])
        self.assertAlmostEqual(result[1][0], np.dot(r * 0.5, self.q_trs_sol_is_ns)[1][0])
        self.assertAlmostEqual(result[1][1], np.dot(r * 0.5, self.q_trs_sol_is_ns)[1][1])
        self.assertAlmostEqual(result[1][2], np.dot(r * 0.5, self.q_trs_sol_is_ns)[1][2])
        self.assertAlmostEqual(result[1][3], np.dot(r * 0.5, self.q_trs_sol_is_ns)[1][3])
        self.assertAlmostEqual(result[1][4], np.dot(r * 0.5, self.q_trs_sol_is_ns)[1][4])
        self.assertAlmostEqual(result[2][0], np.dot(r * 1.0, self.q_trs_sol_is_ns)[2][0])
        self.assertAlmostEqual(result[2][1], np.dot(r * 1.0, self.q_trs_sol_is_ns)[2][1])
        self.assertAlmostEqual(result[2][2], np.dot(r * 1.0, self.q_trs_sol_is_ns)[2][2])
        self.assertAlmostEqual(result[2][3], np.dot(r * 1.0, self.q_trs_sol_is_ns)[2][3])
        self.assertAlmostEqual(result[2][4], np.dot(r * 1.0, self.q_trs_sol_is_ns)[2][4])
        self.assertAlmostEqual(result[3][0], np.dot(r * 1.0, self.q_trs_sol_is_ns)[3][0])
        self.assertAlmostEqual(result[3][1], np.dot(r * 1.0, self.q_trs_sol_is_ns)[3][1])
        self.assertAlmostEqual(result[3][2], np.dot(r * 1.0, self.q_trs_sol_is_ns)[3][2])
        self.assertAlmostEqual(result[3][3], np.dot(r * 1.0, self.q_trs_sol_is_ns)[3][3])
        self.assertAlmostEqual(result[3][4], np.dot(r * 1.0, self.q_trs_sol_is_ns)[3][4])
        self.assertAlmostEqual(result[4][0], np.dot(r * 0.7, self.q_trs_sol_is_ns)[4][0])
        self.assertAlmostEqual(result[4][1], np.dot(r * 0.7, self.q_trs_sol_is_ns)[4][1])
        self.assertAlmostEqual(result[4][2], np.dot(r * 0.7, self.q_trs_sol_is_ns)[4][2])
        self.assertAlmostEqual(result[4][3], np.dot(r * 0.7, self.q_trs_sol_is_ns)[4][3])
        self.assertAlmostEqual(result[4][4], np.dot(r * 0.7, self.q_trs_sol_is_ns)[4][4])
        self.assertAlmostEqual(result[5][0], np.dot(r * 0.7, self.q_trs_sol_is_ns)[5][0])
        self.assertAlmostEqual(result[5][1], np.dot(r * 0.7, self.q_trs_sol_is_ns)[5][1])
        self.assertAlmostEqual(result[5][2], np.dot(r * 0.7, self.q_trs_sol_is_ns)[5][2])
        self.assertAlmostEqual(result[5][3], np.dot(r * 0.7, self.q_trs_sol_is_ns)[5][3])
        self.assertAlmostEqual(result[5][4], np.dot(r * 0.7, self.q_trs_sol_is_ns)[5][4])




