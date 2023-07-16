#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides the availability profile classes, which use
the ranges and sets to manage the resources available over time.
Although :py:func:`ABCProfile` implements most of the availability
profile behavior, as it is common to all profile structures, you
will most likely instantiate :py:func:`DiscreteProfile` and
:py:func:`ContinuousProfile` to manage CPUs and memory resources.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import (
    Generic,
    TypeVar,
    Tuple,
    Hashable,
    List,
    Callable,
    AnyStr,
    Any
)
from dataclasses import dataclass
from functools import singledispatchmethod
from operator import attrgetter
import copy
from sortedcontainers import SortedKeyList
from .sets import DiscreteSet, ContinuousSet, DiscreteRange, ContinuousRange
from .util import ABCComparator, IntFloatComparator


__all__ = [
    "TimeSlot",
    "ABCProfile",
    "ProfileEntry",
    "DiscreteProfile",
    "ContinuousProfile",
]


T = TypeVar("T", DiscreteRange, ContinuousRange)
C = TypeVar("C", DiscreteSet, ContinuousSet, None)
K = TypeVar("K", int, float)


@dataclass
class TimeSlot(Generic[T, C]):
    """
    A time slot.

    This class represents a time slot when a resource set is
    available. Most of the operations of the availability profiles
    return a time slot or sets thereof.
    """

    __slots__ = ["period", "resources"]

    period: T
    """ The time period (a range). """
    resources: C
    """ The resources available during the period. """


@dataclass
class ProfileEntry(Generic[K, C], Hashable):
    """
    A profile entry.

    An entry in the availability profile contains the `time` of a
    change in resources and the `set` of available resources.
    """

    time: K
    """ The time of the entry. """
    resources: C
    """ The resource set available at the time. """
    num_units: int = 1
    """ 
    The number of jobs/work units that use this entry to
    mark either their start or end time. 
    """

    def __hash__(self):
        return self.time.__hash__()

    @classmethod
    def make(cls, time: K, resources: C = None) -> ProfileEntry[K, C]:
        """
        Builds an entry with the given time and resources.

        Args:
            time: the time of the entry
            resources: the sets of resources available after the time.

        Returns:
            A profile entry.
        """
        return ProfileEntry(time=time, resources=resources)

    def copy(self, time: K = None) -> ProfileEntry[K, C]:
        """
        Makes a copy of this entry, changing the time to the time provided.

        Args:
            time: the time to use in the copy.

        Returns:
            A copy of this entry.
        """
        time_used = self.time if time is None else time
        return ProfileEntry(time=time_used, resources=copy.copy(self.resources))

    def __copy__(self):
        return ProfileEntry(time=self.time, resources=copy.copy(self.resources))


class ABCProfile(ABC, Generic[K, C, T]):
    """
    Abstract class with common profile behavior.

    This class represents the availability profile containing the resource sets
    available over time. Each entry :py:func:`ProfileEntry` in the profile
    contains a time and a set containing the resource ranges available at
    the specific time.
    """

    _max_capacity: K
    """ The maximum resource capacity at any given time. """
    _comp: ABCComparator[K]
    """ Comparator to compare times and quantities (they may be floats). """
    _avail: SortedKeyList[ProfileEntry[K, C]]
    """ The data structure used to store the availability information. """

    def __init__(self, **kwargs):
        self._max_capacity = kwargs.get("max_capacity", 0)
        if "comparator" not in kwargs:
            raise ValueError("Comparator needed to compare time and quantities")

        self._comp = kwargs.get("comparator", None)
        self._avail = SortedKeyList(key=self.key_by_time())

    @staticmethod
    def key_by_time() -> Callable[[AnyStr], Any]:
        """
        Returns a function used for sorting the availability profile.

        Returns:
            The function to use.
        """
        return attrgetter("time")

    def add_entry(self, entry: ProfileEntry[K, C]) -> None:
        """
        Adds an entry to the availability data structure.

        Args:
            entry: the entry to be added.

        Returns:
            None
        """
        self._avail.add(entry)

    @property
    def max_capacity(self) -> K:
        """
        Obtains the maximum resource capacity of this profile.

        Returns:
            The maximum capacity
        """
        return self._max_capacity

    @staticmethod
    @abstractmethod
    def make_slot(start_time: K, end_time: K, resources: C) -> TimeSlot[T, C]:
        """
        Creates a time slot whose types are compliant with this profile.

        Args:
            start_time: the start time for the slot.
            end_time: the end time
            resources: the resources available during the slot.

        Returns:
            A time slot.
        """
        raise NotImplementedError

    def _find_place_before(self, value: K) -> Tuple[int, ProfileEntry]:
        """
        Returns the index and entry located before the position where
        the provided value would be placed in the data structure.

        Args:
            value: the value for which the position before it is to be found

        Returns:
            the index and value found at the searched position
        """
        index: int = self._avail.bisect_right(ProfileEntry.make(value)) - 1
        return index, None if index < 0 else self._avail[index]

    def _clone_availability(
        self, start_time: K, end_time: K
    ) -> SortedKeyList[ProfileEntry]:
        """
        Returns a shallow copy of the availability structure
        between the provided time interval.

        Args:
            start_time: the start time to consider
            end_time: the end time

        Returns:
            A shallow copy of the structure with the availability information
        """
        idx, _ = self._find_place_before(start_time)
        cloned: SortedKeyList[ProfileEntry] = SortedKeyList(key=self.key_by_time())

        while idx < len(self._avail):
            entry: ProfileEntry = self._avail[idx]
            if self._comp.value_gt(entry.time, end_time):
                break
            cloned.add(copy.copy(entry))
            idx += 1

        return cloned

    def remove_past_entries(self, earliest_time: K) -> None:
        """
        Removes entries in the availability structure
        whose time is before the provided time.

        Args:
            earliest_time: the earliest time to consider.

        Returns:
            None
        """
        index, _ = self._find_place_before(earliest_time)
        if index > 0:
            self._avail = self._avail[index:]

    def check_availability(
        self, quantity: K, start_time: K, duration: K
    ) -> TimeSlot[T, C]:
        """
        Checks the resource availability.

        Checks whether the quantity of required resources is
        available from the start time and for the duration expected.

        Args:
            quantity: the amount of resources required
            start_time: the start time
            duration: the duration over which the resources are needed.

        Returns:
            A time slot with the searched interval and resource sets available.
        """
        index, entry = self._find_place_before(start_time)
        end_time: K = start_time + duration
        resources: C = entry.resources.copy()
        for entry in self._avail[index:]:
            if entry.time >= end_time:
                break
            resources &= entry.resources
            if resources.quantity < quantity:
                resources = None
                break

        return self.make_slot(
            start_time=start_time, end_time=start_time + duration, resources=resources
        )

    def find_start_time(
        self, quantity: K, ready_time: K, duration: K
    ) -> TimeSlot | None:
        """
        Finds a start time.

        Find the possible start time for a given job or task with the provided duration.

        Args:
            quantity: the amount of resources required
            ready_time: the earliest time at which the job/task is ready
            duration: the job/task duration

        Returns:
            A time slot with the resources available or
            None if it is not possible to meet the task requirements
        """
        index, _ = self._find_place_before(ready_time)
        sub_list = self._avail[index:]

        for idx_out, anchor in enumerate(sub_list):
            intersect: C = anchor.resources.copy()
            pos_start = anchor.time
            pos_end = pos_start + duration

            idx_in = idx_out + 1
            while idx_in < len(sub_list) and self._comp.value_ge(
                intersect.quantity, quantity
            ):
                entry = sub_list[idx_in]
                if self._comp.value_ge(entry.time, pos_end):
                    break

                intersect &= entry.resources
                idx_in += 1

            in_quantity = intersect.quantity
            if self._comp.value_ge(in_quantity, quantity):
                return self.make_slot(
                    start_time=pos_start,
                    end_time=pos_start + duration,
                    resources=intersect,
                )

        return None

    def select_resources(self, resources: C, quantity: K) -> C:
        """
        Selects a quantity of resources.

        This is a helper method for selecting resource
        quantity from the given set.

        Args:
            resources: the set to select resources from
            quantity: the required quantity of resources

        Raises:
            ValueError: when requesting more resources than what
                        the resource set contains.

        Returns:
            The selected resource set.
        """
        if self._comp.value_gt(quantity, resources.quantity):
            raise ValueError(
                "The resource set does not offer the "
                "resource quantity required."
            )

        set_class = resources.__class__
        selected = set_class([])

        curr_quantity = quantity
        for res_range in resources:
            range_class = res_range.__class__
            if self._comp.value_ge(
                    res_range.quantity, curr_quantity
            ):
                begin = res_range.lower
                end = begin + curr_quantity
                selected.add(range_class(begin, end))
                break

            selected.add(copy.copy(res_range))
            curr_quantity -= res_range.quantity

        return selected

    def select_slot_resources(
            self, slot: TimeSlot[T, C], quantity: K
        ) -> C:
        """
        Selects a quantity of resources from a time slot.

        Args:
            slot: the time slot
            quantity: the quantity of resources required.

        Raises:
            ValueError: when requesting more resources than what
                        the resource set contains.

        Returns:
            The selected resource set.
        """
        if slot.resources is not None:
            return self.select_resources(
                resources=slot.resources,
                quantity=quantity
            )
        raise ValueError("Cannot select from resource less slot.")

    def allocate_resources(self, resources: C, start_time: K, end_time: K) -> None:
        """
        Allocates resources.

        Allocates the given resource sets during the start and end times.
        Updates the availability information during the period.

        Args:
            resources: the sets of resources to allocate
            start_time: the start time for using the resources
            end_time: the time the resources should be released

        Returns:
            None
        """
        index, start_entry = self._find_place_before(start_time)
        last_checked: ProfileEntry[K, C] = start_entry.copy(time=start_time)

        # If the time of anchor is equal to the finish time, then a new
        # anchor is not required. We increase the number of tasks
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

    def free_time_slots(self, start_time: K, end_time: K) -> List[TimeSlot]:
        """
        Gets the free time slots.

        Returns the free time slots contained in this availability profile
        within a specified time period.

        **NOTE:** The time slots returned by this method do not overlap.
        That is, they are not the scheduling options for a task. They are
        the windows of availability. Also, they are sorted by start time.
        For example::

                    |-------------------------------------
                  C |    Job 3     |     Time Slot 3     |
                  P |-------------------------------------
                  U |    Job 2  |      Time Slot 2       |
                  s |-------------------------------------
                    |  Job 1 |  Time Slot 1  |   Job 4   |
                    +-------------------------------------
                Start time         Time          Finish time

        Args:
            start_time: the start time to consider.
            end_time: the end time.

        Returns:
            A list of free time slots.
        """

        slots: List[TimeSlot] = []
        profile: SortedKeyList[ProfileEntry] = self._clone_availability(
            start_time, end_time
        )

        for idx, entry in enumerate(profile):
            if self._comp.value_eq(entry.resources.quantity, 0):
                continue

            slot_start = entry.time
            slot_start_idx = idx
            follow_entry: C

            # check all possible time slots starting at slot_start
            while self._comp.value_gt(entry.resources.quantity, 0):
                slot_res: C = entry.resources
                intersection: C = slot_res
                slot_end = end_time
                slot_end_idx = slot_start_idx

                for idx_in in range(idx + 1, len(profile)):
                    follow_entry = profile[idx_in]
                    intersection &= follow_entry.resources

                    if self._comp.value_eq(intersection.quantity, 0):
                        slot_end = follow_entry.time
                        break

                    slot_res = intersection
                    slot_end_idx = idx_in

                slots.append(self.make_slot(slot_start, slot_end, slot_res))

                for idx_in in range(slot_start_idx, slot_end_idx + 1):
                    follow_entry = profile[idx_in]
                    follow_entry.resources -= slot_res

        return slots

    def scheduling_options(
        self, start_time: K, end_time: K, min_duration: K, min_quantity: K = 1
    ) -> List[TimeSlot]:
        """
        Gets the scheduling options.

        Returns the scheduling options of this availability profile within the
        specified period of time.

        **NOTE:** The time slots returned by this method **OVERLAP** because they are
        the scheduling options for jobs with the provided characteristics.

        Args:
            start_time: the start time of the period.
            end_time: the finish time of the period.
            min_duration: the minimum duration of the free time slots. Free time
                    slots whose time frames are smaller than min_duration will be ignored.
                    If min_duration is 1, then all scheduling options will be returned.
            min_quantity: the minimum number of resources for the time slots. Slots whose
                    quantities are smaller than min_quantity will be ignored.

        Returns:
            A list with the scheduling options.
        """

        slots: List[TimeSlot[T, C]] = []
        index, _ = self._find_place_before(start_time)

        for index, entry in enumerate(self._avail[index:]):
            if self._comp.value_ge(entry.time, end_time):
                break
            if self._comp.value_eq(entry.resources.quantity, 0):
                continue

            slot_res = copy.copy(entry.resources)
            slot_start = max(entry.time, start_time)
            while slot_res is not None and slot_res.quantity > 0:
                start_quantity = slot_res.quantity
                changed = False
                for next_entry in self._avail[index + 1:]:
                    if changed or self._comp.value_ge(next_entry.time, end_time):
                        break
                    intersection = slot_res & next_entry.resources
                    if self._comp.value_eq(intersection.quantity, slot_res.quantity):
                        continue

                    # if there is a change in the quantity, so that less
                    # resources are available after the next entry, then considers
                    # the next entry as the end of the current time slot
                    slot_end = min(next_entry.time, end_time)
                    if self._comp.value_ge(
                        slot_end - slot_start, min_duration
                    ) and self._comp.value_ge(slot_res.quantity, min_quantity):
                        slots.append(
                            self.make_slot(
                                start_time=slot_start,
                                end_time=slot_end,
                                resources=copy.copy(slot_res),
                            )
                        )
                    changed = True
                    slot_res = intersection

                if self._comp.value_eq(slot_res.quantity, start_quantity):
                    if self._comp.value_ge(
                        end_time - slot_start, min_duration
                    ) and self._comp.value_ge(slot_res.quantity, min_quantity):
                        slots.append(
                            self.make_slot(
                                start_time=slot_start,
                                end_time=end_time,
                                resources=copy.copy(slot_res),
                            )
                        )
                    slot_res = None
        return slots

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(max_capacity={self.max_capacity}, "
            f"avail={self._avail.__repr__()})"
        )


class DiscreteProfile(ABCProfile[int, DiscreteSet, DiscreteRange]):
    """Availability profile that handles discrete time and resources"""

    def __init__(self, max_capacity: int):
        super().__init__(max_capacity=max_capacity, comparator=IntFloatComparator)
        first_entry = ProfileEntry(
            0, DiscreteSet([DiscreteRange(0, self.max_capacity)])
        )
        self.add_entry(first_entry)

    @staticmethod
    def make_slot(
        start_time: int, end_time: int, resources: DiscreteSet
    ) -> TimeSlot[DiscreteRange, DiscreteSet]:
        return TimeSlot(period=DiscreteRange(start_time, end_time), resources=resources)


class ContinuousProfile(ABCProfile[float, ContinuousSet, ContinuousRange]):
    """
    Continuous availability profile.

    Availability profile that handles continuous time and resources (floats)
    """

    def __init__(self, max_capacity: K):
        super().__init__(max_capacity=max_capacity, comparator=IntFloatComparator)
        first_entry = ProfileEntry(
            0.0, ContinuousSet([ContinuousRange(0.0, self.max_capacity)])
        )
        self.add_entry(first_entry)

    @staticmethod
    def make_slot(
        start_time: float, end_time: float, resources: ContinuousSet
    ) -> TimeSlot[ContinuousRange, ContinuousSet]:
        return TimeSlot(
            period=ContinuousRange(start_time, end_time), resources=resources
        )
