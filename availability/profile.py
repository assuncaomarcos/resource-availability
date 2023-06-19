#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sortedcontainers import SortedKeyList
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple, Hashable
from dataclasses import dataclass
from .sets import DiscreteSet, ContinuousSet, DiscreteRange, ContinuousRange
from operator import attrgetter
import math
import copy

T = TypeVar('T', DiscreteRange, ContinuousRange)
C = TypeVar('C', DiscreteSet, ContinuousSet, None)
K = TypeVar('K', int, float)


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
    def make(cls, time: K):
        return ProfileEntry(time=time, resources=None)

    def __copy__(self):
        return ProfileEntry(time=self.time,
                            resources=copy.copy(self.resources),
                            num_units=self.num_units)


class ABCProfile(ABC, Generic[K, C]):
    _avail: SortedKeyList[ProfileEntry[K, C]]
    _max_capacity: K

    @abstractmethod
    def __init__(self, **kwargs):
        self._max_capacity = kwargs.get('max_capacity', 0)
        self._avail = SortedKeyList(key=attrgetter('time'))
        self._avail.add(self.make_entry(time=0, lower=0, upper=self._max_capacity))

    @abstractmethod
    def make_entry(self, time: K, lower: K, upper: K) -> ProfileEntry[K, C]:
        raise NotImplementedError

    @property
    def max_capacity(self) -> K:
        return self._max_capacity

    def remove_past_entries(self, earliest_time: K):
        index, the_set = self._find_le(earliest_time)
        if index > 0:
            self._avail = self._avail[index:]

    def _find_le(self, value: K) -> Tuple[int, ProfileEntry]:
        index: int = self._avail.bisect_right(ProfileEntry.make(value)) - 1
        return index, None if index < 0 else self._avail[index]

    def check_availability(self, quantity: K,
                           start_time: K,
                           duration: K) -> ProfileEntry[K, C]:
        index, entry = self._find_le(start_time)
        end_time: K = start_time + duration
        resources: C = entry.resources.copy()
        for e in self._avail[index + 1:]:
            resources &= e.resources
            if resources.quantity < quantity:
                resources = None
                break
            if e.time >= end_time:
                break

        return ProfileEntry(time=start_time, resources=resources)

    def find_start_time(self, quantity: K,
                        ready_time: K,
                        duration: K) -> ProfileEntry[K, C]:
        index, entry = self._find_le(ready_time)
        sub_list = self._avail[index:]
        pos_start = ready_time      # possible start time
        intersect: C = None

        for idx_out, anchor in enumerate(sub_list):
            intersect = anchor.resources.copy()
            pos_start = max(anchor.time, pos_start)
            pos_end = pos_start + duration

            idx_in = idx_out + 1
            while idx_in < len(sub_list) and not intersect.quantity < quantity:
                in_entry = sub_list[idx_in]
                intersect &= in_entry.resources.quantity
                idx_in += 1

                if in_entry.time > pos_end or math.isclose(in_entry.time, pos_end):
                    break

        return ProfileEntry(time=pos_start, resources=intersect)

    def allocate_slot(self, resources: C, start_time: K, end_time: K):
        index, anchor = self._find_le(start_time)
        # If the time of anchor is equal to the finish time, then a new
        # anchor is not required. We increase the number of work units
        # that rely on that entry to mark its completion or start time.
        new_anchor: ProfileEntry[K, C]
        last: ProfileEntry[K, C] = anchor
        if math.isclose(anchor.time, start_time):
            anchor.num_units += 1
        else:
            new_anchor = copy.copy(anchor)
            new_anchor.num_units = 1
            last = new_anchor

        # Iterate rest of list removing the resource ranges

    def time_slots(self):
        pass

    def scheduling_options(self):
        pass


class DiscreteProfile(ABCProfile[int, DiscreteSet]):

    def __init__(self, max_capacity: int):
        super().__init__(max_capacity=max_capacity)

    def make_entry(self, time: int, lower: int,
                   upper: int) -> ProfileEntry[int, DiscreteSet]:
        return ProfileEntry(time, DiscreteSet([DiscreteRange(lower, upper)]))
