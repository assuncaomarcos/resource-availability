#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from availability import DiscreteSet, ContinuousSet, DiscreteRange, ContinuousRange, DiscreteProfile
# import math


class TestResourceSets(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_discrete_set(self):
        discrete_set = DiscreteSet([DiscreteRange(0, 10)])
        self.assertEqual(discrete_set.contains(DiscreteRange(5, 7)), True)
        self.assertEqual(discrete_set.quantity, 10)

    def test_create_continuous_set(self):
        cont_set = ContinuousSet([ContinuousRange(0.0, 10.0)])
        self.assertEqual(cont_set.contains(ContinuousRange(5.0, 7.0)), True)
        self.assertAlmostEqual(cont_set.quantity, 10.0)


class TestDiscreteProfile(unittest.TestCase):
    def setUp(self):
        self.max_capacity = 10
        self.pr = DiscreteProfile(max_capacity=self.max_capacity)

    def test_profile_creation(self):
        self.assertEqual(self.pr.max_capacity, self.max_capacity)

    def test_initial_capacity(self):
        res_set = self.pr.check_availability(quantity=1, start_time=0, duration=1)
        self.assertEqual(res_set.resources.quantity, self.max_capacity)

    def test_find_start_time(self):
        entry = self.pr.find_start_time(quantity=5, ready_time=0, duration=10)
        print(entry)

if __name__ == '__main__':
    unittest.main()
