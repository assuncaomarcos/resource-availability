#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ranges and sets of resources that can
be managed using the availability profile.
"""

from spans import intrangeset, floatrangeset, intrange, floatrange

__all__ = ["DiscreteRange", "ContinuousRange", "DiscreteSet", "ContinuousSet"]


class DiscreteRange(intrange):
    """
    A range of integers.

    Represents a range of discrete values (integers).
    This can be used to store node IDs of nodes in a cluster, for instance.
    """

    __slots__ = ()


class ContinuousRange(floatrange):
    """
    A range of floats.

    Represents a range of continuous values (floats).
    This can be used to store the amount of memory in use in a cluster node.
    """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DiscreteSet(intrangeset):
    """Represents a set of discrete ranges.
    (see :class:`availability.resources.DiscreteRange`).
    """

    __slots__ = ()

    @property
    def quantity(self) -> int:
        """
        Obtains the amount of resources in the set.
        Returns:
            The resource amount
        """
        return sum(len(i) for i in iter(self))

    type = DiscreteRange  # used by intrangeset


class ContinuousSet(floatrangeset):
    """
    Represents a set of continuous ranges.
    (see :class:`availability.resources.ContinuousRange`).
    """

    __slots__ = ()

    @property
    def quantity(self) -> float:
        """
        Obtains the amount of resources in the set.
        Returns:
            The resource amount
        """
        return sum(i.upper - i.lower for i in iter(self))

    type = ContinuousRange
