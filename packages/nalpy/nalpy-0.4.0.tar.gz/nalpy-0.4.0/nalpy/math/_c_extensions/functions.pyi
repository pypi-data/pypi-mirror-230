from typing import Iterable, overload


def round(__x: float) -> int:
    """
    Round a number to an integer.
    When a number is halfway between two others, it's rounded toward the nearest number that's away from zero.

    This method ends up being around 40 % faster than the built-in Python round function.
    """
    ...

def remap(value: float, from1: float, to1: float, from2: float, to2: float) -> float:
    """Converts a value to another value within the given arguments. Ends are inclusive."""
    ...

def remap01(value: float, from1: float, to1: float) -> float:
    """Converts a value to another value within 0.0 and 1.0. Ends are inclusive."""
    ...

@overload
def clamp(value: int, _min: int, _max: int) -> int:
    """Clamps the value to the specified range. Both ends are inclusive."""
    ...
@overload
def clamp(value: float, _min: float, _max: float) -> float:
    """Clamps the value to the specified range. Both ends are inclusive."""
    ...

def clamp01(value: float) -> float:
    """Shorthand for `math.clamp(value, 0.0, 1.0)`"""
    ...

def delta_angle(current: float, target: float) -> float:
    """Calculates the shortest difference between two given angles."""
    ...

def sign(__x: float) -> int:
    """
    A number that indicates the sign of ``__x``.

    ```
    -1 | less than zero
     0 | equal to zero
    +1 | greater than zero
    ```
    """
    ...


def lerp(a: float, b: float, t: float) -> float:
    """
    Linearly interpolates between ``a`` and ``b`` by ``t``.

    The parameter ``t`` is clamped to the range [0, 1].
    """
    ...

def lerp_unclamped(a: float, b: float, t: float) -> float:
    """
    Linearly interpolates between ``a`` and ``b`` by ``t``.

    The parameter ``t`` is not clamped.
    """
    ...

def lerp_angle(a: float, b: float, t: float) -> float:
    """
    Same as ``lerp``, but makes sure the values interpolate correctly when they wrap around 360 degrees.

    The parameter t is clamped to the range [0, 1]. Variables a and b are assumed to be in degrees.
    """
    ...

def inverse_lerp(a: float, b: float, value: float) -> float:
    """Calculates the clamped parameter ``t`` in ``lerp`` when output is the given ``value``."""
    ...

def smooth_step(a: float, b: float, t: float) -> float:
    """
    Smoothly interpolates between a and b by t.

    The parameter t is clamped to the range [0, 1].
    """
    ...

def move_towards(current: float, target: float, maxDelta: float) -> float:
    """
    Moves a value current towards target.

    This is essentially the same as Lerp, but instead the function will ensure that the speed never exceeds maxDelta. Negative values of maxDelta pushes the value away from target.
    """
    ...

def move_towards_angle(current: float, target: float, maxDelta: float) -> float:
    """
    Same as MoveTowards but makes sure the values interpolate correctly when they wrap around 360 degrees.

    Variables current and target are assumed to be in degrees. For optimization reasons, negative values of maxDelta are not supported and may cause oscillation. To push current away from a target angle, add 180 to that angle instead.
    """
    ...

def ping_pong(t: float, length: float) -> float:
    """
    Returns a value that will increment and decrement between the value 0 and length.

   ``t`` has to be a self-incrementing value.
    """
    ...

def kahan_sum(float_values: Iterable[float]) -> float:
    """
    Implements the Kahan summation algorithm.

    This algorithm greatly reduces the numerical error of the returned floating point values compared to basic summation.
    """
