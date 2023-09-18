import sys as __sys
import typing as __typing

#region public imports of math library functions

# Operations
from math import pow as pow
from math import sqrt as sqrt
from math import cbrt as cbrt

from math import log as log
from math import log10 as log10
from math import log2 as log2
from math import log1p as log1p

# Geometry
from math import tan as tan
from math import atan as atan
from math import atan2 as atan2
from math import sin as sin
from math import asin as asin
from math import cos as cos
from math import acos as acos

from math import degrees as degrees
from math import radians as radians
from math import hypot as hypot

# Rounding
from math import ceil as ceil
from math import floor as floor

# Value checking
from math import isclose as isclose
from math import isinf as isinf
from math import isnan as isnan
from math import isfinite as isfinite

# Value manipulation
from math import trunc as trunc
from math import modf as modf
from math import nextafter as nextafter

# Functions
from math import gcd as gcd
from math import lcm as lcm

#endregion

#region public imports of c extension functions
from nalpy.math._c_extensions.functions import round as round
from nalpy.math._c_extensions.functions import remap as remap
from nalpy.math._c_extensions.functions import remap01 as remap01
from nalpy.math._c_extensions.functions import clamp as clamp
from nalpy.math._c_extensions.functions import clamp01 as clamp01
from nalpy.math._c_extensions.functions import delta_angle as delta_angle
from nalpy.math._c_extensions.functions import sign as sign

from nalpy.math._c_extensions.functions import lerp as lerp
from nalpy.math._c_extensions.functions import lerp_unclamped as lerp_unclamped
from nalpy.math._c_extensions.functions import lerp_angle as lerp_angle
from nalpy.math._c_extensions.functions import inverse_lerp as inverse_lerp
from nalpy.math._c_extensions.functions import smooth_step as smooth_step
from nalpy.math._c_extensions.functions import move_towards as move_towards
from nalpy.math._c_extensions.functions import move_towards_angle as move_towards_angle
from nalpy.math._c_extensions.functions import ping_pong as ping_pong

from nalpy.math._c_extensions.functions import kahan_sum as kahan_sum
#endregion

# Public component imports at the bottom

#region Constants
PI: __typing.Final[float] = 3.14159265358979323846
"""The mathematical constant `3.14159...`"""

EULER: __typing.Final[float] = 2.7182818284590452354
"""Euler's number. The mathematical constant `2.71828...`"""

EPSILON: __typing.Final[float] = __sys.float_info.epsilon
"""Difference between `1.0` and the least value greater than `1.0` that is representable as a float."""

INFINITY: __typing.Final[float] = float("inf")
"""Same as `float("inf")`"""

NEGATIVE_INFINITY: __typing.Final[float] = float("-inf")
"""Same as `float("-inf")`"""

NAN: __typing.Final[float] = float("nan")
"""
Same as `float('nan')`.

NOTE: NaN values are not equal to anything, including themselves. To check if a float is NaN, use `math.isnan()`.
"""

MAXVALUE: __typing.Final[int] = __sys.maxsize
"""
Maximum size of integer-dependant things.

NOTE: Python integers don't have a maximum value.
"""

MINVALUE: __typing.Final[int] = -MAXVALUE - 1
"""
Minimum size of integer-dependant things.

NOTE: Python integers don't have a minimum value.
"""
#endregion

# Initialize TypeVar
_NumberT = __typing.TypeVar("_NumberT", int, float)

#region Basic math functions
def is_positive_inf(__x: __typing.SupportsFloat) -> bool:
    """Return ``True`` if ``x`` is positive infinity, and ``False`` otherwise."""
    x = float(__x)
    return isinf(x) and x > 0 # faster than f == INFINITY, supposedly

def is_negative_inf(__x: __typing.SupportsFloat) -> bool:
    """Return ``True`` if ``x`` is negative infinity, and ``False`` otherwise."""
    x = float(__x)
    return isinf(x) and x < 0 # faster than f == NEGATIVE_INFINITY, supposedly
#endregion

#region Rounding
#region Nearest n
def round_to_nearest_n(__x: __typing.SupportsFloat, n: int) -> int:
    """
    Round a number to the nearest multiple of ``n``.
    When a number is halfway between two multiples of n, it's rounded toward the nearest number that's away from zero.
    """
    if n == 0: # Prevent division by zero. Any multiple of zero is always zero.
        return 0
    return round(float(__x) / n) * n

def floor_to_nearest_n(__x: __typing.SupportsFloat, n: int) -> int:
    """Floor a number to the nearest multiple of ``n``."""
    if n == 0: # Prevent division by zero. Any multiple of zero is always zero.
        return 0
    return floor(float(__x) / n) * n

def ceil_to_nearest_n(__x: __typing.SupportsFloat, n: int) -> int:
    """Ceil a number to the nearest multiple of ``n``."""
    if n == 0: # Prevent division by zero. Any multiple of zero is always zero.
        return 0
    return ceil(float(__x) / n) * n
#endregion

#region Round to digits
def ceil_to_digits(__x: __typing.SupportsFloat, digits: int = 0) -> float:
    """Return the ceiling of x as a float with specified decimal accuracy."""
    pow10: float = pow(10.0, digits)
    return ceil(float(__x) * pow10) / pow10 # dividing changes output to float

def floor_to_digits(__x: __typing.SupportsFloat, digits: int = 0) -> float:
    """Return the floor of x as a float with specified decimal accuracy."""
    pow10: float = pow(10.0, digits)
    return floor(float(__x) * pow10) / pow10 # dividing changes output to float


def round_to_digits(__x: __typing.SupportsFloat, digits: int = 0) -> float:
    """
    Round a number to a given precision in decimal digits.
    When a number is halfway between two others, it's rounded toward the nearest number that's away from zero.

    ``digits`` may be negative.
    """
    pow10: float = pow(10.0, digits)
    return round(float(__x) * pow10) / pow10 # dividing changes output to float


def round_to_nearest_n_to_digits(__x: __typing.SupportsFloat, n: int, digits: int = 0) -> float:
    """Round a number to the nearest multiple of ``n`` with specified decimal accuracy."""
    pow10: float = pow(10.0, digits)
    return round_to_nearest_n(float(__x) * pow10, n) / pow10 # dividing changes output to float

def floor_to_nearest_n_to_digits(__x: __typing.SupportsFloat, n: int, digits: int = 0) -> float:
    """Floor a number to the nearest multiple of ``n`` with specified decimal accuracy."""
    pow10: float = pow(10.0, digits)
    return floor_to_nearest_n(float(__x) * pow10, n) / pow10 # dividing changes output to float

def ceil_to_nearest_n_to_digits(__x: __typing.SupportsFloat, n: int, digits: int = 0) -> float:
    """Ceil a number to the nearest multiple of ``n`` with specified decimal accuracy."""
    pow10: float = pow(10.0, digits)
    return ceil_to_nearest_n(float(__x) * pow10, n) / pow10 # dividing changes output to float
#endregion
#endregion

#region Iterables
def closest(value: int | float, iterable: __typing.Iterable[_NumberT]) -> _NumberT:
    """Return the value in the iterable that is closest to the given value."""
    return min(iterable, key=lambda k: abs(k - value))

def furthest(value: int | float, iterable: __typing.Iterable[_NumberT]) -> _NumberT:
    """Return the value in the iterable that is furthest from the given value."""
    return max(iterable, key=lambda k: abs(k - value))
#endregion

#region Public imports of components
from nalpy.math._c_extensions.vector2 import Vector2 as Vector2
from nalpy.math._c_extensions.vector2_int import Vector2Int as Vector2Int
from nalpy.math._c_extensions.mvector2 import MVector2 as MVector2
from nalpy.math._c_extensions.mvector2_int import MVector2Int as MVector2Int

from nalpy.math._rect.rect import Rect as Rect
from nalpy.math._rect.rect_int import RectInt as RectInt
from nalpy.math._rect.rect_offset import RectOffset as RectOffset
from nalpy.math._rect.rect_offset_int import RectOffsetInt as RectOffsetInt
#endregion

#region Private imports of legacy components
from nalpy.math._legacy_vector2.vector2 import Vector2 as _Legacy_Vector2
from nalpy.math._legacy_vector2.vector2_int import Vector2Int as _Legacy_Vector2Int
from nalpy.math._legacy_vector2.mvector2 import MVector2 as _Legacy_MVector2
from nalpy.math._legacy_vector2.mvector2_int import MVector2Int as _Legacy_MVector2Int
#endregion
