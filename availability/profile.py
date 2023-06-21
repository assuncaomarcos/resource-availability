#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sortedcontainers import SortedKeyList
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple, Hashable, List
from dataclasses import dataclass
from .sets import DiscreteSet, ContinuousSet, DiscreteRange, ContinuousRange
from .util import ABCComparator, IntegerComparator
from operator import attrgetter
import copy

T = TypeVar('T', DiscreteRange, ContinuousRange)
C = TypeVar('C', DiscreteSet, ContinuousSet, None)
K = TypeVar('K', int, float)

COMPARATORS = {
    int: IntegerComparator
}


@dataclass
class TimeSlot(Generic[T, C]):
    period: T
    resources: C


@dataclass
class ProfileEntry(Generic[K, C], Hashable):
    time: K
    resources: C
    num_units: int = 1

    def __hash__(self):
        return self.time.__hash__()

    @classmethod
    def make(cls, time: K, resources: C = None):
        return ProfileEntry(time=time, resources=resources)

    def copy(self, time: K = None):
        # if time provided, return copy with new time
        time_used = self.time if time is None else time
        return ProfileEntry(time=time_used, resources=copy.copy(self.resources))

    def __copy__(self):
        return ProfileEntry(time=self.time, resources=copy.copy(self.resources))


class ABCProfile(ABC, Generic[K, C]):
    _avail: SortedKeyList[ProfileEntry[K, C]]
    _max_capacity: K
    _comp: ABCComparator[K]

    @abstractmethod
    def __init__(self, **kwargs):
        self._max_capacity = kwargs.get('max_capacity', 0)
        if 'comparator' not in kwargs:
            raise ValueError("Comparator required to compare times and quantities of resources")

        self._comp = kwargs.get('comparator', None)
        self._avail = SortedKeyList(key=attrgetter('time'))
        self._avail.add(self.make_entry(time=0, lower=0, upper=self._max_capacity))

    def _find_le(self, value: K) -> Tuple[int, ProfileEntry]:
        index: int = self._avail.bisect_right(ProfileEntry.make(value)) - 1
        return index, None if index < 0 else self._avail[index]

    @classmethod
    @abstractmethod
    def make_entry(cls, time: K, lower: K, upper: K) -> ProfileEntry[K, C]:
        raise NotImplementedError

    @property
    def max_capacity(self) -> K:
        return self._max_capacity

    def remove_past_entries(self, earliest_time: K):
        index, the_set = self._find_le(earliest_time)
        if index > 0:
            self._avail = self._avail[index:]

    def check_availability(self, quantity: K,
                           start_time: K,
                           duration: K) -> ProfileEntry[K, C]:
        index, entry = self._find_le(start_time)
        end_time: K = start_time + duration
        resources: C = entry.resources.copy()
        for e in self._avail[index + 1:]:
            if e.time >= end_time:
                break
            resources &= e.resources
            if resources.quantity < quantity:
                resources = None
                break

        return ProfileEntry(time=start_time, resources=resources)

    def find_start_time(self, quantity: K,
                        ready_time: K,
                        duration: K) -> ProfileEntry[K, C]:
        index, entry = self._find_le(ready_time)
        sub_list = self._avail[index:]

        for idx_out, anchor in enumerate(sub_list):
            intersect: C = anchor.resources.copy()
            pos_start = anchor.time
            pos_end = pos_start + duration

            idx_in = idx_out + 1
            while idx_in < len(sub_list) and \
                    self._comp.value_ge(intersect.quantity, quantity):
                in_entry = sub_list[idx_in]
                if self._comp.value_ge(in_entry.time, pos_end):
                    break

                intersect &= in_entry.resources
                idx_in += 1

            in_quantity = intersect.quantity
            if self._comp.value_ge(in_quantity, quantity):
                return ProfileEntry(time=pos_start, resources=intersect)

        return ProfileEntry(time=ready_time, resources=None)

    def allocate_slot(self, resources: C, start_time: K, end_time: K):
        index, start_entry = self._find_le(start_time)
        last_checked: ProfileEntry[K, C] = start_entry.copy(time=start_time)

        # If the time of anchor is equal to the finish time, then a new
        # anchor is not required. We increase the number of work units
        # that rely on that entry to mark its completion or start time.
        if self._comp.value_eq(start_entry.time, start_time):
            start_entry.num_units += 1
        else:
            self._avail.add(last_checked)
            last_checked = last_checked.copy()
            index += 1

        sub_list = self._avail[index:]
        for next_entry in sub_list:
            if self._comp.value_le(next_entry.time, end_time):
                last_checked.resources -= resources
                last_checked = next_entry
            else:
                break

        if self._comp.value_eq(last_checked.time, end_time):
            last_checked.num_units += 1
        else:
            self._avail.add(last_checked.copy(time=end_time))
            last_checked.resources -= resources

    def time_slots(self, start_time: K, end_time: K,
                   min_duration: K, min_quantity: K = 1) -> List[TimeSlot]:
        slots: List = []
        start_idx, _ = self._find_le(start_time)
        end_idx, _ = self._find_le(end_time)
        sub_list = self._avail[start_idx: end_idx]

        for start_idx, start_ent in enumerate(sub_list):
            if self._comp.value_eq(start_ent.resources.quantity, 0):
                continue

            slot_res = start_ent.resources.copy()
            start_time = start_ent.time
            curr_idx = start_idx
            end_slot: K = end_time

            while self._comp.value_gt(slot_res.quantity, 0):
                pass



        # TODO: Complete this method
        return slots

    def scheduling_options(self, start_time: K, end_time: K,
                           min_duration: K, min_quantity: K = 1) -> List[TimeSlot]:
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(max_capacity={self.max_capacity}, " \
               f"avail={self._avail.__repr__()})"


class DiscreteProfile(ABCProfile[int, DiscreteSet]):

    def __init__(self, max_capacity: int):
        super().__init__(max_capacity=max_capacity, comparator=IntegerComparator)

    @classmethod
    def make_entry(cls, time: int, lower: int,
                   upper: int) -> ProfileEntry[int, DiscreteSet]:
        return ProfileEntry(time, DiscreteSet([DiscreteRange(lower, upper)]))
