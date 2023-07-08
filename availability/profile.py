#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sortedcontainers import SortedKeyList
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Tuple, Hashable, List
from dataclasses import dataclass
from .sets import DiscreteSet, ContinuousSet, DiscreteRange, ContinuousRange
from .util import ABCComparator, IntFloatComparator
from operator import attrgetter
import copy

T = TypeVar("T", DiscreteRange, ContinuousRange)
C = TypeVar("C", DiscreteSet, ContinuousSet, None)
K = TypeVar("K", int, float)


@dataclass(slots=True)
class TimeSlot(Generic[T, C]):
    period: T
    """ The time period """
    resources: C
    """ The resources available during the period """


@dataclass(slots=True)
class ProfileEntry(Generic[K, C], Hashable):
    time: K
    """ The time of the entry """
    resources: C
    """ The resource sets available at the time """
    num_units: int = 1
    """ The number of jobs/work units that use this entry to mark either their start or end time """

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


def key_by_time():
    return attrgetter("time")


class ABCProfile(ABC, Generic[K, C, T]):
    """Abstract class with basic profile behavior

    This class represents the availability profile containing the ranges of
    resources available over time. Each entry in the profile contains a time and
    a set containing the resource ranges available at the specific time.
    """

    _max_capacity: K
    """ The maximum resource capacity at any given time """
    _comp: ABCComparator[K]
    """ Comparator to compare times and quantities (they may be floats) """
    _avail: SortedKeyList[ProfileEntry[K, C]]
    """ The data structure used to store the availability information """

    @abstractmethod
    def __init__(self, **kwargs):
        self._max_capacity = kwargs.get("max_capacity", 0)
        if "comparator" not in kwargs:
            raise ValueError("Comparator needed to compare time and quantities")

        self._comp = kwargs.get("comparator", None)
        self._avail = SortedKeyList(key=key_by_time())
        # Create the start entry at time 0, lower resource 0, upper resource as max capacity
        self._avail.add(
            self.make_entry(time=0, lower_res=0, upper_res=self._max_capacity)
        )

    def _find_le(self, value: K) -> Tuple[int, ProfileEntry]:
        index: int = self._avail.bisect_right(ProfileEntry.make(value)) - 1
        return index, None if index < 0 else self._avail[index]

    def _clone_availability(
        self, start_time: K, end_time: K
    ) -> SortedKeyList[ProfileEntry]:
        idx, _ = self._find_le(start_time)
        cloned: SortedKeyList[ProfileEntry] = SortedKeyList(key=key_by_time())

        while idx < len(self._avail):
            entry: ProfileEntry = self._avail[idx]
            if self._comp.value_gt(entry.time, end_time):
                break
            cloned.add(copy.copy(entry))
            idx += 1

        return cloned

    @staticmethod
    @abstractmethod
    def make_entry(time: K, lower_res: K, upper_res: K) -> ProfileEntry[K, C]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def make_slot(start_time: K, end_time: K, resources: C) -> TimeSlot[T, C]:
        raise NotImplementedError

    @property
    def max_capacity(self) -> K:
        return self._max_capacity

    def remove_past_entries(self, earliest_time: K):
        index, the_set = self._find_le(earliest_time)
        if index > 0:
            self._avail = self._avail[index:]

    def check_availability(
        self, quantity: K, start_time: K, duration: K
    ) -> TimeSlot[T, C]:
        index, entry = self._find_le(start_time)
        end_time: K = start_time + duration
        resources: C = entry.resources.copy()
        for e in self._avail[index + 1 :]:
            if e.time >= end_time:
                break
            resources &= e.resources
            if resources.quantity < quantity:
                resources = None
                break

        return TimeSlot(
            period=DiscreteRange(start_time, start_time + duration), resources=resources
        )

    def find_start_time(
        self, quantity: K, ready_time: K, duration: K
    ) -> TimeSlot | None:
        index, entry = self._find_le(ready_time)
        sub_list = self._avail[index:]

        for idx_out, anchor in enumerate(sub_list):
            intersect: C = anchor.resources.copy()
            pos_start = anchor.time
            pos_end = pos_start + duration

            idx_in = idx_out + 1
            while idx_in < len(sub_list) and self._comp.value_ge(
                intersect.quantity, quantity
            ):
                in_entry = sub_list[idx_in]
                if self._comp.value_ge(in_entry.time, pos_end):
                    break

                intersect &= in_entry.resources
                idx_in += 1

            in_quantity = intersect.quantity
            if self._comp.value_ge(in_quantity, quantity):
                return TimeSlot(
                    period=DiscreteRange(pos_start, pos_start + duration),
                    resources=intersect,
                )

        return None

    def allocate_slot(self, resources: C, start_time: K, end_time: K) -> None:
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

    def time_slots(self, start_time: K, end_time: K) -> List[TimeSlot]:
        slots: List[TimeSlot] = []
        profile: SortedKeyList[ProfileEntry] = self._clone_availability(
            start_time, end_time
        )

        for idx, entry in enumerate(profile):
            if self._comp.value_eq(entry.resources.quantity, 0):
                continue

            slot_start = entry.time
            slot_start_idx = slot_end_idx = idx

            # check all possible time slots starting at slot_start
            while self._comp.value_gt(entry.resources.quantity, 0):
                slot_res: C = copy.copy(entry.resources)
                intersection: C = slot_res
                slot_end = end_time

                for idx_in in range(idx + 1, len(profile)):
                    follow_entry = profile[idx_in]
                    intersection &= follow_entry.resources

                    if self._comp.value_eq(intersection.quantity, 0):
                        slot_end = follow_entry.time
                        break

                    slot_res = intersection
                    slot_end_idx = idx_in

                slot = self.make_slot(slot_start, slot_end, slot_res)
                slots.append(slot)

                for idx_in in range(slot_start_idx, slot_end_idx + 1):
                    entry = profile[idx_in]
                    entry.resources -= slot_res

        return slots

    def scheduling_options(
        self, start_time: K, end_time: K, min_duration: K, min_quantity: K = 1
    ) -> List[TimeSlot]:
        slots: List[TimeSlot[T, C]] = []
        index, _ = self._find_le(start_time)

        for idx_out, entry in enumerate(self._avail[index:]):
            if self._comp.value_ge(entry.time, end_time):
                break
            elif self._comp.value_eq(entry.resources.quantity, 0):
                continue

            slot_ranges = copy.copy(entry.resources)
            slot_start = max(entry.time, start_time)
            while slot_ranges is not None and slot_ranges.quantity > 0:
                start_quantity = slot_ranges.quantity
                changed = False
                for idx_in, next_entry in enumerate(self._avail[index + 1 :]):
                    if changed or self._comp.value_ge(next_entry.time, end_time):
                        break
                    intersection = slot_ranges & next_entry.resources
                    if self._comp.value_eq(intersection.quantity, slot_ranges.quantity):
                        continue

                    # if there is a change in the quantity, so that less
                    # resources are available after the next entry, then considers
                    # the next entry as the end of the current time slot
                    slot_end = min(next_entry.time, end_time)
                    if self._comp.value_ge(
                        slot_end - slot_start, min_duration
                    ) and self._comp.value_ge(slot_ranges.quantity, min_quantity):
                        slots.append(
                            TimeSlot(
                                period=DiscreteRange(slot_start, slot_end),
                                resources=copy.copy(slot_ranges),
                            )
                        )
                    changed = True
                    slot_ranges = intersection

                if self._comp.value_eq(slot_ranges.quantity, start_quantity):
                    if self._comp.value_ge(
                        end_time - slot_start, min_duration
                    ) and self._comp.value_ge(slot_ranges.quantity, min_quantity):
                        slots.append(
                            TimeSlot(
                                period=DiscreteRange(slot_start, end_time),
                                resources=copy.copy(slot_ranges),
                            )
                        )
                        slot_ranges = None
        return slots

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(max_capacity={self.max_capacity}, "
            f"avail={self._avail.__repr__()})"
        )


class DiscreteProfile(ABCProfile[int, DiscreteSet, DiscreteRange]):
    def __init__(self, max_capacity: int):
        super().__init__(max_capacity=max_capacity, comparator=IntFloatComparator)

    @staticmethod
    def make_entry(
        time: int, lower_res: int, upper_res: int
    ) -> ProfileEntry[int, DiscreteSet]:
        return ProfileEntry(time, DiscreteSet([DiscreteRange(lower_res, upper_res)]))

    @staticmethod
    def make_slot(
        start_time: int, end_time: int, resources: DiscreteSet
    ) -> TimeSlot[DiscreteRange, DiscreteSet]:
        return TimeSlot(period=DiscreteRange(start_time, end_time), resources=resources)
