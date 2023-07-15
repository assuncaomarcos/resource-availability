#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module provides utility classes and functions, such as
comparators. As the availability profile manages floats (and dates
in the future) and most of its functionality is shared across
all profile types, we provide an object used to compare values
in ranges and sets, hence abstracting the comparison details
away from the profile. """

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import math

V = TypeVar("V", int, float)

__all__ = ["ABCComparator", "IntFloatComparator"]


class ABCComparator(ABC, Generic[V]):
    """
    Abstract comparator.

    As resource amounts and times that a profile manages can be floats,
    we need to provide it with a comparator that implements the methods
    of this abstract class.
    """

    @classmethod
    @abstractmethod
    def value_lt(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is smaller than other.

        Args:
            first: the first value to compare against the second value.
            other: the second value.

        Returns:
            True if the first value is smaller than the second.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_le(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is smaller than or equal to the other.

        Args:
            first: the first value to compare against the second value.
            other: the second value.

        Returns:
            True if the first value is smaller than or equal to the second.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_eq(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is equal to the other.

        Args:
            first: the first value to compare against the second value.
            other: the second value.

        Returns:
            True if the first value is equal to the second.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_ge(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is greater than or equal to the other.

        Args:
            first: the first value to compare against the second value.
            other: the second value.

        Returns:
            True if the first value is greater than or equal to the second.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_gt(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is greater than the other.

        Args:
            first: the first value to compare against the second value.
            other: the second value.

        Returns:
            True if the first value is greater than the second.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_ne(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is different from the other.

        Args:
            first: the first value to compare against the second value.
            other: the second value.

        Returns:
            True if the first value is different from the second.
        """
        raise NotImplementedError


class IntFloatComparator(ABCComparator[V]):
    """
    Comparator to compare floats and integers.
    """

    @classmethod
    def value_lt(cls, first: V, other: V) -> bool:
        return first < other

    @classmethod
    def value_le(cls, first: V, other: V) -> bool:
        return first < other or math.isclose(first, other)

    @classmethod
    def value_eq(cls, first: V, other: V) -> bool:
        return math.isclose(first, other)

    @classmethod
    def value_ge(cls, first: V, other: V) -> bool:
        return first > other or math.isclose(first, other)

    @classmethod
    def value_gt(cls, first: V, other: V) -> bool:
        return first > other

    @classmethod
    def value_ne(cls, first: V, other: V) -> bool:
        return first != other
