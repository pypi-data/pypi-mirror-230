from typing import ClassVar, Iterator, SupportsIndex
from .mvector2 import MVector2

class Vector2:
    """An immutable two-dimensional vector"""

    zero: ClassVar[Vector2]
    """Shorthand for ``Vector2(0.0, 0.0)``"""
    one: ClassVar[Vector2]
    """Shorthand for ``Vector2(1.0, 1.0)``"""
    up: ClassVar[Vector2]
    """A unit vector pointing up (vector j). Shorthand for ``Vector2(0.0, 1.0)``"""
    down: ClassVar[Vector2]
    """A unit vector pointing down. Shorthand for ``Vector2(0.0, -1.0)``"""
    left: ClassVar[Vector2]
    """A unit vector pointing left. Shorthand for ``Vector2(-1.0, 0.0)``"""
    right: ClassVar[Vector2]
    """A unit vector pointing right (vector i). Shorthand for ``Vector2(1.0, 0.0)``"""

    def __init__(self, x: float, y: float) -> None: ...

    def __getitem__(self, i: SupportsIndex) -> float: ...

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...

    def __add__(self, other: Vector2) -> Vector2: ...

    def __sub__(self, other: Vector2) -> Vector2: ...

    def __mul__(self, other: Vector2 | float | int) -> Vector2: ...

    def __rmul__(self, other: Vector2 | float | int) -> Vector2: ...

    def __truediv__(self, other: Vector2 | float | int) -> Vector2: ...

    def __floordiv__(self, other: Vector2 | float | int) -> Vector2: ...

    def __mod__(self, other: Vector2 | float | int) -> Vector2: ...

    def __divmod__(self, other: Vector2 | float | int) -> tuple[Vector2, Vector2]: ...

    def __neg__(self) -> Vector2: ...

    def __abs__(self) -> Vector2: ...

    def __eq__(self, other: Vector2) -> bool: ...

    def __iter__(self) -> Iterator[float]: ...

    def __hash__(self) -> int: ...

    @property
    def magnitude(self) -> float:
        """The length of this vector."""
        ...

    @property
    def normalized(self) -> Vector2:
        """A copy of this vector with a magnitude of 1"""
        ...

    @staticmethod
    def dot(a: Vector2, b: Vector2) -> float:
        """Dot Product of two `Vector2` vectors."""
        ...

    @staticmethod
    def lerp(a: Vector2, b: Vector2, t: float) -> Vector2:
        """
        Linearly interpolates between vectors ``a`` and ``b`` by ``t``.

        The parameter ``t`` is clamped to the range [0, 1].
        """
        ...

    @staticmethod
    def lerp_unclamped(a: Vector2, b: Vector2, t: float) -> Vector2:
        """
        Linearly interpolates between vectors ``a`` and ``b`` by ``t``.

        The parameter ``t`` is not clamped.
        """
        ...

    @staticmethod
    def move_towards(current: Vector2, target: Vector2, max_distance_delta: float) -> Vector2:
        """Moves a point current towards target."""
        ...

    @staticmethod
    def smooth_damp(current: Vector2, target: Vector2, current_velocity: MVector2, smooth_time: float, delta_time: float, max_speed: float = float("inf")) -> Vector2:
        """Gradually changes a vector towards a desired goal over time."""
        ...

    @staticmethod
    def perpendicular(vector: Vector2) -> Vector2:
        """
        Returns a 2D vector with the same magnitude, but perpendicular to the given 2D vector.
        The result is always rotated 90-degrees in a counter-clockwise direction for a 2D coordinate system where the positive Y axis goes up.
        """
        ...

    @staticmethod
    def reflect(vector: Vector2, normal: Vector2) -> Vector2:
        """Reflects a vector off the vector defined by a normal."""
        ...

    @staticmethod
    def angle(_from: Vector2, _to: Vector2) -> float:
        """
        Gets the unsigned angle in degrees between from and to.

        NOTE: The angle returned will always be between 0 and 180 degrees, because the method returns the smallest angle between the vectors.
        """
        ...

    @staticmethod
    def signed_angle(_from: Vector2, _to: Vector2) -> float:
        """
        Gets the signed angle in degrees between from and to. The angle returned is the signed counterclockwise angle between the two vectors.

        NOTE: The angle returned will always be between -180 and 180 degrees, because the method returns the smallest angle between the vectors.
        """
        ...

    @staticmethod
    def distance(a: Vector2, b: Vector2) -> float:
        """Returns the distance between a and b."""
        ...

    @staticmethod
    def min(a: Vector2, b: Vector2) -> Vector2:
        """Create a new `Vector2` by selecting the smallest components of the two given `Vector2` instances."""
        ...

    @staticmethod
    def max(a: Vector2, b: Vector2) -> Vector2:
        """Create a new `Vector2` by selecting the largest components of the two given `Vector2` instances."""
        ...

    def to_tuple(self) -> tuple[float, float]: ...
    def to_dict(self) -> dict[str, float]: ...
