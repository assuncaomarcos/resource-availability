#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Tests the availability profile """

import unittest

from availability import (
    DiscreteRange,
    ContinuousRange,
    DiscreteSet,
    ContinuousSet,
    DiscreteProfile,
    ContinuousProfile,
)


class TestResourceRanges(unittest.TestCase):
    """Tests the resource ranges"""

    def test_discrete_range(self) -> None:
        """Tests the discrete resource range"""
        span = DiscreteRange(0, 5)
        self.assertEqual(span.last, 4)
        span = DiscreteRange(0, 5, upper_inc=True)
        self.assertEqual(span.last, 5)
        span = DiscreteRange(0, 10) - DiscreteRange(0, 5)
        self.assertEqual(len(span), 5)

    def test_continuous_range(self) -> None:
        """Tests the continuous (float) resource range"""
        span = ContinuousRange(0.0, 5.0)
        self.assertEqual(span.upper, 5.0)
        span = ContinuousRange(0.0, 5.0, upper_inc=True)
        self.assertEqual(span.upper, 5)
        span = ContinuousRange(0.0, 10.0) - ContinuousRange(0.0, 5.0)
        self.assertEqual(span, ContinuousRange(5.0, 10.0))


class TestResourceSets(unittest.TestCase):
    """Tests some basic operations of range sets.

    The main functionality is provided by spans:
    https://github.com/runfalk/spans/
    """

    def test_create_discrete_set(self) -> None:
        """Tests a few operations of discrete sets."""
        spans = DiscreteSet([DiscreteRange(0, 10)])
        self.assertEqual(spans.contains(DiscreteRange(5, 7)), True)
        self.assertEqual(spans.quantity, 10)
        spans |= DiscreteSet([DiscreteRange(10, 20)])
        self.assertEqual(spans.quantity, 20)
        spans -= DiscreteSet([DiscreteRange(10, 20)])
        self.assertEqual(spans.quantity, 10)

    def test_create_continuous_set(self) -> None:
        """Tests a few operations of continuous sets."""
        spans = ContinuousSet([ContinuousRange(0.0, 10.0)])
        self.assertEqual(spans.contains(ContinuousRange(5.0, 7.0)), True)
        self.assertEqual(spans.quantity, 10.0)
        spans |= ContinuousSet([ContinuousRange(10.0, 20.0)])
        self.assertEqual(spans.quantity, 20.0)
        spans -= ContinuousSet([ContinuousRange(10.0, 20.0)])
        self.assertEqual(spans.quantity, 10.0)


class TestDiscreteProfile(unittest.TestCase):
    """Tests the discrete availability profile."""

    def setUp(self) -> None:
        self.max_capacity = 10
        self.profile = DiscreteProfile(max_capacity=self.max_capacity)

    def tearDown(self) -> None:
        del self.profile

    def test_capacity(self) -> None:
        """Test the profile's capacity"""
        self.assertEqual(self.profile.max_capacity, self.max_capacity)
        slot = self.profile.find_start_time(self.max_capacity, 0, 1)
        self.assertEqual(slot.period.lower, 0)
        self.assertEqual(slot.period.upper, 1)
        self.assertEqual(slot.resources.quantity, self.max_capacity)

    def test_find_start_time(self):
        """Tests finding the start time for a task"""
        slot = self.profile.find_start_time(quantity=5, ready_time=0, duration=10)
        self.assertEqual(slot.period.lower, 0)
        self.assertEqual(slot.period.upper, 10)
        self.assertEqual(
            slot.resources, DiscreteSet([DiscreteRange(0, self.max_capacity)])
        )
        self._allocate()
        slot = self.profile.find_start_time(quantity=5, ready_time=0, duration=10)
        self.assertEqual(slot.period.lower, 5)
        self.assertEqual(slot.period.upper, 15)
        self.assertIn(DiscreteRange(7, 10), slot.resources)

    def _allocate(self) -> None:
        """Allocates a few resources from the pool"""
        span1 = DiscreteSet([DiscreteRange(2, 7)])
        span2 = DiscreteSet([DiscreteRange(0, 2)])
        self.profile.allocate_resources(resources=span1, start_time=5, end_time=10)
        self.profile.allocate_resources(resources=span2, start_time=0, end_time=5)

    def test_time_slots(self) -> None:
        """Tests obtaining the free time slots in the pool"""
        self._allocate()
        slots = self.profile.free_time_slots(start_time=0, end_time=20)
        self.assertEqual(len(slots), 4)
        self.assertIn(DiscreteRange(0, 20), slots[0].period)
        self.assertIn(DiscreteRange(7, 10), slots[0].resources)
        self.assertIn(DiscreteRange(2, 7), slots[1].resources)
        self.assertIn(DiscreteRange(0, 2), slots[2].resources)
        self.assertIn(DiscreteRange(2, 7), slots[3].resources)
        self.assertIn(DiscreteRange(10, 20), slots[3].period)

    def test_allocate(self) -> None:
        """Test multiple allocations"""
        span = DiscreteSet([DiscreteRange(0, 8)])
        self.profile.allocate_resources(resources=span, start_time=5, end_time=10)
        slot = self.profile.check_availability(5, start_time=5, duration=5)
        self.assertEqual(slot.resources, None)

    def test_scheduling_options(self) -> None:
        """Test obtaining the scheduling options"""
        self._allocate()
        slots = self.profile.scheduling_options(
            start_time=0, end_time=20, min_duration=2
        )
        self.assertEqual(len(slots), 4)
        self.assertIn(DiscreteRange(0, 5), slots[0].period)
        self.assertIn(DiscreteRange(0, 20), slots[1].period)
        self.assertIn(DiscreteRange(5, 20), slots[2].period)
        self.assertIn(DiscreteRange(10, 20), slots[3].period)
        self.assertIn(DiscreteRange(2, 10), slots[0].resources)
        self.assertIn(DiscreteRange(7, 10), slots[1].resources)
        self.assertIn(DiscreteRange(0, 2), slots[2].resources)
        self.assertIn(DiscreteRange(0, 10), slots[3].resources)


class TestContinuousProfile(unittest.TestCase):
    """Tests the continuous availability profile."""

    def setUp(self) -> None:
        self.max_capacity = 10.0
        self.profile = ContinuousProfile(max_capacity=self.max_capacity)

    def tearDown(self) -> None:
        del self.profile

    def test_capacity(self) -> None:
        """Test the profile's capacity"""
        self.assertEqual(self.profile.max_capacity, self.max_capacity)
        slot = self.profile.find_start_time(self.max_capacity, 0.0, 1.0)
        self.assertEqual(slot.period.lower, 0.0)
        self.assertEqual(slot.period.upper, 1.0)
        self.assertEqual(slot.resources.quantity, self.max_capacity)

    def _allocate(self) -> None:
        """Allocates a few resources from the pool"""
        span1 = ContinuousSet([ContinuousRange(2.0, 7.0)])
        span2 = ContinuousSet([ContinuousRange(0.0, 2.0)])
        self.profile.allocate_resources(resources=span1, start_time=5.0, end_time=10.0)
        self.profile.allocate_resources(resources=span2, start_time=0.0, end_time=5.0)

    def test_find_start_time(self):
        """Tests finding the start time for a task"""
        slot = self.profile.find_start_time(quantity=5.0, ready_time=0.0, duration=10.0)
        self.assertEqual(slot.period.lower, 0.0)
        self.assertEqual(slot.period.upper, 10.0)
        self.assertEqual(
            slot.resources, ContinuousSet([ContinuousRange(0.0, self.max_capacity)])
        )
        self._allocate()
        slot = self.profile.find_start_time(quantity=5.0, ready_time=0.0, duration=10.0)
        self.assertEqual(slot.period.lower, 5.0)
        self.assertEqual(slot.period.upper, 15.0)
        self.assertIn(ContinuousRange(7.0, 10.0), slot.resources)

    def test_time_slots(self) -> None:
        """Tests obtaining the free time slots in the pool"""
        self._allocate()
        slots = self.profile.free_time_slots(start_time=0.0, end_time=20.0)
        self.assertEqual(len(slots), 4)
        self.assertIn(ContinuousRange(0.0, 20.0), slots[0].period)
        self.assertIn(ContinuousRange(7.0, 10.0), slots[0].resources)
        self.assertIn(ContinuousRange(2.0, 7.0), slots[1].resources)
        self.assertIn(ContinuousRange(0.0, 2.0), slots[2].resources)
        self.assertIn(ContinuousRange(2.0, 7.0), slots[3].resources)
        self.assertIn(ContinuousRange(10.0, 20.0), slots[3].period)

    def test_allocate(self) -> None:
        """Test multiple allocations"""
        span = ContinuousSet([ContinuousRange(0, 8)])
        self.profile.allocate_resources(resources=span, start_time=5, end_time=10)
        slot = self.profile.check_availability(5, start_time=5, duration=5)
        self.assertEqual(slot.resources, None)

    def test_scheduling_options(self) -> None:
        """Test obtaining the scheduling options"""
        self._allocate()
        slots = self.profile.scheduling_options(
            start_time=0, end_time=20, min_duration=2
        )
        self.assertEqual(len(slots), 4)
        self.assertIn(ContinuousRange(0, 5), slots[0].period)
        self.assertIn(ContinuousRange(0, 20), slots[1].period)
        self.assertIn(ContinuousRange(5, 20), slots[2].period)
        self.assertIn(ContinuousRange(10, 20), slots[3].period)
        self.assertIn(ContinuousRange(2, 10), slots[0].resources)
        self.assertIn(ContinuousRange(7, 10), slots[1].resources)
        self.assertIn(ContinuousRange(0, 2), slots[2].resources)
        self.assertIn(ContinuousRange(0, 10), slots[3].resources)


if __name__ == "__main__":
    unittest.main()
