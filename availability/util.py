#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
import math

V = TypeVar('V', int, float)


class ABCComparator(ABC, Generic[V]):

    @classmethod
    @abstractmethod
    def value_lt(cls, first: V, other: V) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_le(cls, first: V, other: V) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_eq(cls, first: V, other: V) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_ge(cls, first: V, other: V) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_gt(cls, first: V, other: V) -> bool:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def value_ne(cls, first: V, other: V) -> bool:
        raise NotImplementedError


class IntegerComparator(ABCComparator[int]):
    @classmethod
    def value_lt(cls, first: int, other: int) -> bool:
        return first < other

    @classmethod
    def value_le(cls, first: int, other: int) -> bool:
        return first <= other

    @classmethod
    def value_eq(cls, first: int, other: int) -> bool:
        return first == other

    @classmethod
    def value_ge(cls, first: int, other: int) -> bool:
        return first >= other

    @classmethod
    def value_gt(cls, first: int, other: int) -> bool:
        return first > other

    @classmethod
    def value_ne(cls, first: int, other: int) -> bool:
        return first != other


class FloatComparator(ABCComparator[float]):
    @classmethod
    def value_lt(cls, first: float, other: float) -> bool:
        return first < other

    @classmethod
    def value_le(cls, first: float, other: float) -> bool:
        return first < other or math.isclose(first, other)

    @classmethod
    def value_eq(cls, first: float, other: float) -> bool:
        return math.isclose(first, other)

    @classmethod
    def value_ge(cls, first: float, other: float) -> bool:
        return first > other or math.isclose(first, other)

    @classmethod
    def value_gt(cls, first: float, other: float) -> bool:
        return first > other

    @classmethod
    def value_ne(cls, first: float, other: float) -> bool:
        return first != other
