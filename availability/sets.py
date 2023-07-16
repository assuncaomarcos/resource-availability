#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides the ranges and sets of resources that an
availability profile can use for managing resources. The
:py:func:`DiscreteRange` and :py:func:`DiscreteSet` classes are suitable
for discrete resources such as CPUs and nodes, whereas
:py:func:`ContinuousRange` and :py:func:`ContinuousSet` are
more applicable to memory resources.
"""

from spans import intrangeset, floatrangeset, intrange, floatrange

__all__ = ["DiscreteRange", "ContinuousRange", "DiscreteSet", "ContinuousSet"]


class DiscreteRange(intrange):
    """
    A range of integers.

    Represents a range of discrete values (integers), which can
    represent CPU or node IDs in a cluster.

    **Note:** the implementation uses the `Spans` library, in which
    by default all ranges include all elements from `lower` up to
    but not including `upper`::

        >>> span = DiscreteRange(1, 5)
        >>> span.lower
        1
        >>> span.upper
        4
    """

    def __init__(self, lower=None, upper=None, lower_inc=None, upper_inc=None):
        """
        Creates a discrete range (integers).

        This constructor is just a convenience as this class mostly piggybacks
        on `Spans`' `intrange`.

        Args:
            lower: Lower end of range.
            upper: Upper end of range.
            lower_inc: ``True`` if lower end should be included. Default is ``True``
            upper_inc: ``True`` if upper end should be included. Default is ``False``

        Raises:
            TypeError: If lower or upper bound is not of the correct type.
            ValueError: If upper bound is lower than lower bound.
        """
        super().__init__(lower, upper, lower_inc, upper_inc)

    @property
    def quantity(self) -> int:
        """
        Obtains the number of resources in the range.

        Returns:
            The number of resources.
        """
        return len(self)

    __slots__ = ()


class ContinuousRange(floatrange):
    """
    A range of floats.

    Represents a range of continuous values (floats), which can
    represent the amount of memory in use in a cluster node.

    **Note:** the implementation uses the `Spans` library, in which
    by default all ranges include all elements from `lower` up to
    but not including `upper`.
    """

    def __init__(self, lower=None, upper=None, lower_inc=None, upper_inc=None):
        """
        Creates a continuous range (floats).

        This constructor just casts the bounds to floats to avoid
        an inconvenient error from `Spans` when providing integers.

        Args:
            lower: Lower end of range.
            upper: Upper end of range.
            lower_inc: ``True`` if lower end should be included. Default is ``True``
            upper_inc: ``True`` if upper end should be included. Default is ``False``
        Raises:
            TypeError: If lower or upper bound is not of the correct type.
            ValueError: If upper bound is lower than lower bound.
        """
        if lower is not None:
            lower = float(lower)
        if upper is not None:
            upper = float(upper)
        super().__init__(lower, upper, lower_inc, upper_inc)

    @property
    def quantity(self) -> float:
        """
        Obtains the amount of resources in the range.

        Returns:
            The amount of resources.
        """
        return self.upper - self.lower

    __slots__ = ()


class DiscreteSet(intrangeset):
    """
    A set of discrete ranges.

    Similar to ranges, range sets support union, difference, and intersection.
    Contrary to Python’s built-in sets, the operations return a new
    set and do not modify the range set in place since ranges are immutable.
    """

    __slots__ = ()

    @property
    def quantity(self) -> int:
        """
        Obtains the number of resources in the set.

        Returns:
            The number of resources.
        """
        return sum(i.quantity for i in iter(self))

    type = DiscreteRange  # used by intrangeset


class ContinuousSet(floatrangeset):
    """
    A set of continuous ranges.

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
            The resource amount.
        """
        return sum(i.quantity for i in iter(self))

    type = ContinuousRange  # used by floatrangeset
