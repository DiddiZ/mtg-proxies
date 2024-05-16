from collections.abc import Iterable
from logging import getLogger
from typing import Any, Literal

import numpy as np
from nptyping import Float, NDArray, UInt
from nptyping.shape import Shape


logger = getLogger(__name__)


# TODO: Implement using pint
# MTG_CARD_INCHES: NDArray[Shape["2"], Float] = np.asarray([2.48425197, 3.46456693], dtype=float)
# MTG_CARD_MM: NDArray[Shape["2"], Float] = np.asarray([63.1, 88.0], dtype=float)
MTG_CARD_SIZE: dict[str, NDArray[Shape["2"], Float]] = {
    "in": np.asarray([2.48425197, 3.46456693], dtype=float),
    "mm": np.asarray([63.1, 88.0], dtype=float),
    "cm": np.asarray([6.31, 8.8], dtype=float),
}

# Paper sizes (sourced from the Adobe website)
PAPER_SIZE: dict[str, dict[str, NDArray[Shape["2"], Float]]] = {
    "A0": {
        "mm": np.asarray([841, 1189], dtype=float),
        "in": np.asarray([33.1, 46.8], dtype=float),
        "cm": np.asarray([84.1, 118.9], dtype=float),
    },
    "A1": {
        "mm": np.asarray([594, 841], dtype=float),
        "in": np.asarray([23.4, 33.1], dtype=float),
        "cm": np.asarray([59.4, 84.1], dtype=float),
    },
    "A2": {
        "mm": np.asarray([420, 594], dtype=float),
        "in": np.asarray([16.5, 23.4], dtype=float),
        "cm": np.asarray([42.0, 59.4], dtype=float),
    },
    "A3": {
        "mm": np.asarray([297, 420], dtype=float),
        "in": np.asarray([11.7, 16.5], dtype=float),
        "cm": np.asarray([29.7, 42.0], dtype=float),
    },
    "A4": {
        "mm": np.asarray([210, 297], dtype=float),
        "in": np.asarray([8.3, 11.7], dtype=float),
        "cm": np.asarray([21.0, 29.7], dtype=float),
    },
    "A5": {
        "mm": np.asarray([148, 210], dtype=float),
        "in": np.asarray([5.8, 8.3], dtype=float),
        "cm": np.asarray([14.8, 21.0], dtype=float),
    },
    "A6": {
        "mm": np.asarray([105, 148], dtype=float),
        "in": np.asarray([4.1, 5.8], dtype=float),
        "cm": np.asarray([10.5, 14.8], dtype=float),
    },
    "A7": {
        "mm": np.asarray([74, 105], dtype=float),
        "in": np.asarray([2.9, 4.1], dtype=float),
        "cm": np.asarray([7.4, 10.5], dtype=float),
    },
    "A8": {
        "mm": np.asarray([52, 74], dtype=float),
        "in": np.asarray([2.0, 2.9], dtype=float),
        "cm": np.asarray([5.2, 7.4], dtype=float),
    },
    "A9": {
        "mm": np.asarray([37, 52], dtype=float),
        "in": np.asarray([1.5, 2.0], dtype=float),
        "cm": np.asarray([3.7, 5.2], dtype=float),
    },
    "A10": {
        "mm": np.asarray([26, 37], dtype=float),
        "in": np.asarray([1.0, 1.5], dtype=float),
        "cm": np.asarray([2.6, 3.7], dtype=float),
    },
}

UNITS_TO_MM = {"in": 25.4, "mm": 1.0, "cm": 10}

UNITS_TO_IN = {"in": 1.0, "mm": 1 / 25.4, "cm": 10 / 25.4}


Units = Literal["in", "mm", "cm"]


def get_pixels_from_size_and_ppsu(ppsu: int, size: Iterable[float] | float) -> NDArray[Any, UInt]:
    """Calculate size in pixels from size and DPI.

    The code assumes that everything is handled in milimetres.

    Args:
        ppsu (int): Dots per inch. Dots here are pixels.
        size (Iterable[float] | float): Value or iterable of values representing size in inches.

    Returns:
        Iterable[int]: Sizes in pixels for each value in the input iterable.
    """
    return (np.asarray(size, dtype=np.float32) * ppsu).round(decimals=0).astype(int)


def get_ppsu_from_size_and_pixels(
    pixel_values: Iterable[int] | int,
    size: Iterable[float] | float,
) -> int:
    """Calculate PPSU (points per size unit) from size and amount of pixels.

    It calculates the PPSU by dividing the amount of pixels by the size in whatever units are used.
    If multiple dimensions are provided, it averages over the DPIs for each dimension.
    If the PPSUs differ, a warning is logged.

    Args:
        pixel_values (Iterable[int] | int): Value or iterable of values representing size in pixels.
        size (Iterable[float] | float): Value or iterable of values representing size in any units.

    Returns:
        int: Dots per inch. Averages over the input values, if multiple dimensions are provided.
    """
    ppsu = np.asarray(pixel_values, dtype=np.int32) / (np.asarray(size, dtype=np.float32))
    mean_ppsu = np.mean(ppsu)
    if not np.allclose(ppsu, mean_ppsu, atol=1):
        logger.warning(f"DPIs differ accross dimensions: {ppsu} = {pixel_values}/{size}")
    return int(mean_ppsu.round(decimals=0))


def parse_papersize_from_spec(spec: str, units: Units) -> NDArray[Shape["2"], Float]:
    if spec in PAPER_SIZE:
        if units in PAPER_SIZE[spec]:
            return PAPER_SIZE[spec][units]
        else:
            raise ValueError(f"Units {units} not supported for papersize {spec}")
    else:
        raise ValueError(f"Paper size not supported: {spec}")
