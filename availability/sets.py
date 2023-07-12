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

    Note: the implementation uses the `spans` library, in which
    by default all ranges include all elements from and including
    lower up to but not including upper::

        >>> span = DiscreteRange(1, 5)
        >>> span.lower
        1
        >>> span.upper
        4
    """

    __slots__ = ()


class ContinuousRange(floatrange):
    """
    A range of floats.

    Represents a range of continuous values (floats).
    This can be used to store the amount of memory in use in a cluster node.

    Note: the implementation uses the `spans` library, in which
    by default all ranges include all elements from and including
    lower up to but not including upper.
    """

    __slots__ = ()


class DiscreteSet(intrangeset):
    """Represents a set of discrete ranges.

    Similar to ranges, range sets support union, difference, and intersection.
    Contrary to Python’s built-in sets, the operations return a new
    set and do not modify the range set in place since ranges are immutable.
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

    Similar to ranges, range sets support union, difference, and intersection.
    Contrary to Python’s built-in sets, the operations return a new
    set and do not modify the range set in place since ranges are immutable.
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
