#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from availability import DiscreteSet, ContinuousSet, DiscreteRange, ContinuousRange, DiscreteProfile


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
        # print(entry)

    def test_allocate_slot(self):
        slot = DiscreteSet([DiscreteRange(2, 7)])
        slot2 = DiscreteSet([DiscreteRange(0, 2)])
        self.pr.allocate_slot(resources=slot, start_time=5, end_time=10)
        self.pr.allocate_slot(resources=slot2, start_time=0, end_time=3)
        entry = self.pr.find_start_time(quantity=10, ready_time=0, duration=10)
        self.assertEqual(entry.time, 10)
        entry = self.pr.find_start_time(quantity=1, ready_time=0, duration=10)

    def test_time_slots(self):
        self.pr.time_slots(start_time=0, end_time=20, min_duration=5)


if __name__ == '__main__':
    unittest.main()
