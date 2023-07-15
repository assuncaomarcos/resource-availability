#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This package provides a data structure, termed an availability profile,
for tracking how to allocate computing resources to application
services or tasks.

The two main modules of this package are, namely, `sets` and `profile`.
The `sets` module provides classes for creating ranges of resources and sets
of ranges. The classes mainly piggyback on the ranges and sets provided by `Spans`.
The following uses the integer range and set as examples, but the same
concepts apply to other ranges and sets.

The :py:func:`sets.DiscreteRange` class can represent discrete computing
resources, such as CPUs, available in a compute cluster.
The class :py:func:`sets.DiscreteSet`, as the same implies, stores a
set of `DiscreteRange` objects. When simulating a task scheduler,
`DiscreteSet` can represent the ranges of CPUs or compute nodes
available for running jobs. As the scheduler assigns resources to tasks,
it removes ranges of resources from the set, whose ranges can become fragmented.
As tasks finish executing, the scheduler returns the ranges to the set.

An availability profile is a time-ordered list whose entries
(:py:func:`profile.ProfileEntry`) contain the time of the entry itself and
the resource set available at that specific time. When allocating
resources, say the CPU range `0..10` from time `10` to `20`, one can use
:py:meth:`profile.ABCProfile.allocate_resources` to allocate the ranges
(i.e., remove them from the profile):

.. code-block:: python

    from availability.sets import DiscreteRange, DiscreteSet
    from availability.profile import DiscreteProfile

    profile = DiscreteProfile(max_capacity=100)
    span = DiscreteSet([DiscreteRange(0, 10)])
    profile.allocate_resources(
            resources=span,
            start_time=10,
            end_time=20
    )

The `allocate_resources` method will find the entry that marks the
start time, or the entry before it, and sweep the profile until the end
time and remove the ranges from the entries. The very process happens
for other operations, such as :py:meth:`profile.ABCProfile.check_availability`.

The class :py:func:`profile.ABCProfile` is a generic abstract class that defines
the behavior common to all the other profile types. Most of its
operations return a :py:func:`profile.TimeSlot` object containing the
time period and the resource set available during the slot.

"""

__version__ = "0.0.1"

__all__ = ["sets", "profile", "util"]
