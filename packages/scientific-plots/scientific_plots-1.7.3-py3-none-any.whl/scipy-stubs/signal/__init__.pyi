#!/usr/bin/env python
"""
Stub-files for scipy.signal. This module contains the type-annotations for
scipy's library for fourier-transformations and signal analysis.
"""
from typing import Tuple, Optional, Union, overload

from scientific_plots.types_ import Vector


def welch(
    Y: Union[Vector, list[float]],
    fs: Optional[float] = None,
    scaling: str = "density",
    window: Optional[str] = "hamming",
    nperseg: int = 10,
    detrend: bool = False) -> Tuple[Vector, Vector]: ...


def periodogram(
    Y: Union[Vector, list[float]],
    fs: Optional[float] = None,
    scaling: str = "density",
    window: Optional[str] = "hamming",
    detrend: bool = False) -> Tuple[Vector, Vector]: ...


Single = Union[Vector, list[float]]
Double = Union[tuple[Vector, Vector], tuple[list[float], list[float]]]


@overload
def savgol_filter(
    values: Single, window: int, order: int) -> Vector: ...


@overload
def savgol_filter(
    values: Double, window: int, order: int)\
        -> tuple[Vector, Vector]: ...
