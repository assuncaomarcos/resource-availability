#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Utility classes and methods """

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import math

V = TypeVar("V", int, float)

__all__ = ["ABCComparator", "IntFloatComparator"]


class ABCComparator(ABC, Generic[V]):
    """
    Abstract comparator.

    As resource amounts and times can be floats, we need a comparator"""

    @classmethod
    @abstractmethod
    def value_lt(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is smaller than other

        Args:
            first: the first value to compare against other
            other: the other value

        Returns:
            True if the first value is smaller than the other
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_le(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is smaller than or equal to the other

        Args:
            first: the first value to compare against the other
            other: the other value

        Returns:
            True if the first value is smaller than or equal to the other
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_eq(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is equal to the other

        Args:
            first: the first value to compare against other
            other: the other value

        Returns:
            True if the first value is equal to the other
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_ge(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is greater than or equal to the other

        Args:
            first: the first value to compare against other
            other: the other value

        Returns:
            True if the first value is greater than or equal to the other
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_gt(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is greater than the other

        Args:
            first: the first value to compare against other
            other: the other value

        Returns:
            True if the first value is greater than the other
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_ne(cls, first: V, other: V) -> bool:
        """
        Checks whether the first value is different from the other

        Args:
            first: the first value to compare against other
            other: the other value

        Returns:
            True if the first value is different from the other
        """
        raise NotImplementedError


class IntFloatComparator(ABCComparator[V]):
    """Comparator to compare floats and ints"""

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
