#!/usr/bin/env python

from unittest import TestCase
from hll import HyperLogLog
import math

class HyperLogLogTestCase(TestCase):
    def test_alpha(self):
        alpha = [HyperLogLog._get_alpha(b) for b in range(4, 10)]
        self.assertEqual(alpha, [0.673, 0.697, 0.709, 0.7152704932638152, 0.7182725932495458, 0.7197831133217303])

    def test_alpha_bad(self):
        self.assertRaises(ValueError, HyperLogLog._get_alpha, 1)
        self.assertRaises(ValueError,HyperLogLog. _get_alpha, 17)

    def test_rho(self):
        arr = [ 1L << i for i in range(32 + 1) ]
        self.assertEqual(HyperLogLog._get_rho(0, arr), 33)
        self.assertEqual(HyperLogLog._get_rho(1, arr), 32)
        self.assertEqual(HyperLogLog._get_rho(2, arr), 31)
        self.assertEqual(HyperLogLog._get_rho(3, arr), 31)
        self.assertEqual(HyperLogLog._get_rho(4, arr), 30)
        self.assertEqual(HyperLogLog._get_rho(5, arr), 30)
        self.assertEqual(HyperLogLog._get_rho(6, arr), 30)
        self.assertEqual(HyperLogLog._get_rho(7, arr), 30)
        self.assertEqual(HyperLogLog._get_rho(1 << 31, arr), 1)
        self.assertRaises(ValueError, HyperLogLog._get_rho, 1 << 32, arr)

    def test_init(self):
        s = HyperLogLog(0.05)
        self.assertEqual(s.b, 9)
        self.assertEqual(s.alpha, 0.7197831133217303)
        self.assertEqual(s.m, 512)
        self.assertEqual(len(s.M), 512)

    def test_add(self):
        s = HyperLogLog(0.05)

        for i in range(10):
            s.add(str(i))

        M = [(i, v) for i, v in enumerate(s.M) if v > 0]

        self.assertEqual(M, [(31, 1), (120, 1), (122, 4), (151, 5), (171, 3), (176, 1), (196, 1), (268, 1), (443, 2), (474, 1)])


    def test_calc_cardinality(self):

        for cardinality in (1, 2, 3, 5, 10, 1500, 100000, 1000000):
            a = HyperLogLog(0.05)

            for i in xrange(cardinality):
                a.add(str(i))

            #print cardinality, len(a), a.m, cardinality * (1.0 - 1.04 / math.sqrt(a.m)), cardinality * (1.0 + 1.04 / math.sqrt(a.m))
            self.assertGreater(len(a), cardinality * (1.0 - 1.04 / math.sqrt(a.m)))
            self.assertLess(len(a), cardinality * (1.0 + 1.04 / math.sqrt(a.m)))


    def test_update(self):
        a = HyperLogLog(0.05)
        b = HyperLogLog(0.05)
        c = HyperLogLog(0.05)

        for i in xrange(2):
            a.add(str(i))
            c.add(str(i))

        for i in xrange(2, 4):
            b.add(str(i))
            c.add(str(i))

        a.update(b)

        self.assertNotEqual(a, b)
        self.assertNotEqual(b, c)
        self.assertEqual(a, c)


    def test_update_err(self):
        a = HyperLogLog(0.05)
        b = HyperLogLog(0.01)

        self.assertRaises(ValueError, a.update, b)
