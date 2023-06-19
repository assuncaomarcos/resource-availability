#!/usr/bin/env python
# -*- coding: utf-8 -*-

from spans import intrangeset, floatrangeset, intrange, floatrange


class DiscreteRange(intrange):
    """
    Represents a range of discrete values (integers).
    This can be used to store node IDs of nodes in a cluster, for instance.
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ContinuousRange(floatrange):
    """
    Represents a range of continuous values (floats).
    This can be used to store the amount of memory in use in a cluster node.
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DiscreteSet(intrangeset):
    """ Represents a set of discrete ranges.
    (see :class:`availability.resources.DiscreteRange`).
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def quantity(self) -> int:
        return sum([len(i) for i in iter(self)])

    type = DiscreteRange  # used by intrangeset


class ContinuousSet(floatrangeset):
    """ Represents a set of continuous ranges.
    (see :class:`availability.resources.ContinuousRange`).
    """
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def quantity(self) -> float:
        return sum([i.upper - i.lower for i in iter(self)])

    type = ContinuousRange
