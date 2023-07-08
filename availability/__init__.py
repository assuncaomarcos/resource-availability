#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This package provides a data structure, termed as availability profile, that can
be used to keep track of how computing resources are allocated to application
services or tasks.
"""

__version__ = '0.0.1'

from .sets import ContinuousSet, DiscreteSet, DiscreteRange, ContinuousRange
from .profile import DiscreteProfile, TimeSlot

__all__ = [
    'ContinuousSet',
    'DiscreteSet',
    'DiscreteRange',
    'ContinuousRange',
    'DiscreteProfile',
    'TimeSlot'
]
