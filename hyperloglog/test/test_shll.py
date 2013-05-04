#!/usr/bin/env python

import math
import time
from unittest import TestCase
from shll import SlidingHyperLogLog

class SlidingHyperLogLogTestCase(TestCase):
    def test_alpha(self):
        alpha = [SlidingHyperLogLog._get_alpha(b) for b in range(4, 10)]
        self.assertEqual(alpha, [0.673, 0.697, 0.709, 0.7152704932638152, 0.7182725932495458, 0.7197831133217303])

    def test_alpha_bad(self):
        self.assertRaises(ValueError, SlidingHyperLogLog._get_alpha, 1)
        self.assertRaises(ValueError, SlidingHyperLogLog._get_alpha, 17)

    def test_rho(self):
        arr = [ 1L << i for i in range(32 + 1) ]
        self.assertEqual(SlidingHyperLogLog._get_rho(0, arr), 33)
        self.assertEqual(SlidingHyperLogLog._get_rho(1, arr), 32)
        self.assertEqual(SlidingHyperLogLog._get_rho(2, arr), 31)
        self.assertEqual(SlidingHyperLogLog._get_rho(3, arr), 31)
        self.assertEqual(SlidingHyperLogLog._get_rho(4, arr), 30)
        self.assertEqual(SlidingHyperLogLog._get_rho(5, arr), 30)
        self.assertEqual(SlidingHyperLogLog._get_rho(6, arr), 30)
        self.assertEqual(SlidingHyperLogLog._get_rho(7, arr), 30)
        self.assertEqual(SlidingHyperLogLog._get_rho(1 << 31, arr), 1)
        self.assertRaises(ValueError, SlidingHyperLogLog._get_rho, 1 << 32, arr)

    def test_init(self):
        s = SlidingHyperLogLog(0.05, 100)
        self.assertEqual(s.window, 100)
        self.assertEqual(s.b, 9)
        self.assertEqual(s.alpha, 0.7197831133217303)
        self.assertEqual(s.m, 512)
        self.assertEqual(len(s.LPFM), 512)

    def test_add(self):
        s = SlidingHyperLogLog(0.05, 100)

        for i in range(10):
            s.add(i, str(i))

        M = [(i, max(R for ts, R in lpfm)) for i, lpfm in enumerate(s.LPFM) if lpfm]
        self.assertEqual(M, [(31, 1), (120, 1), (122, 4), (151, 5), (171, 3), (176, 1), (196, 1), (268, 1), (443, 2), (474, 1)])

    def test_calc_cardinality(self):
        for cardinality in (1, 2, 3, 5, 10, 1500, 100000):
            a = SlidingHyperLogLog(0.05, 100)

            for i in xrange(cardinality):
                a.add(int(time.time()), str(i))

            #print cardinality, len(a), a.m, cardinality * (1.0 - 1.04 / math.sqrt(a.m)), cardinality * (1.0 + 1.04 / math.sqrt(a.m))
            self.assertGreater(a.card(int(time.time())), cardinality * (1.0 - 1.04 / math.sqrt(a.m)))
            self.assertLess(a.card(int(time.time())), cardinality * (1.0 + 1.04 / math.sqrt(a.m)))

    def test_calc_cardinality_sliding1(self):
        a = SlidingHyperLogLog(0.05, 100)
        a.add(1, 'k1')
        self.assertEqual(int(a.card(1)), 1)
        self.assertEqual(int(a.card(101)), 1)
        self.assertEqual(int(a.card(102)), 0)
        a.add(2, 'k2')
        a.add(3, 'k3')
        self.assertEqual(int(a.card(3)), 3)
        self.assertEqual(int(a.card(101)), 3)
        self.assertEqual(int(a.card(102)), 2)
        self.assertEqual(int(a.card(103)), 1)
        self.assertEqual(int(a.card(104)), 0)

    def test_calc_cardinality_sliding2(self):
        for cardinality in (1, 2, 3, 5, 10, 1500, 100000, 1000000):
            a = SlidingHyperLogLog(0.05, 100)

            for i in xrange(cardinality):
                a.add(i / 2000.0, str(i))

            self.assertGreater(a.card(i / 2000.0), min(cardinality, 200000) * (1.0 - 1.04 / math.sqrt(a.m)))
            self.assertLess(a.card(i / 2000.0), min(cardinality, 200000) * (1.0 + 1.04 / math.sqrt(a.m)))

    def test_update(self):
        a = SlidingHyperLogLog(0.05, 100)
        b = SlidingHyperLogLog(0.05, 100)
        c = SlidingHyperLogLog(0.05, 100)

        for i in xrange(10000):
            a.add(i, str('k1-%d' % i))
            c.add(i, str('k1-%d' % i))

        for i in xrange(10000):
            b.add(i, str('k2-%d' % i))
            c.add(i, str('k2-%d' % i))

        a.update(b)

        self.assertNotEqual(a, b)
        self.assertNotEqual(b, c)
        self.assertEqual(a, c)

    def test_update_err(self):
        a = SlidingHyperLogLog(0.05, 100)
        b = SlidingHyperLogLog(0.01, 100)

        self.assertRaises(ValueError, a.update, b)
