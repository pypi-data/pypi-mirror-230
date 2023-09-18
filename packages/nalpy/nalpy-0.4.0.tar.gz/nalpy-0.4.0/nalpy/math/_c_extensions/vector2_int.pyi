from typing import ClassVar, Iterator, SupportsIndex
from .vector2 import Vector2

class Vector2Int:
    """An immutable two-dimensional vector with integer precision."""
    zero: ClassVar[Vector2Int]
    """Shorthand for ``Vector2Int(0, 0)``"""
    one: ClassVar[Vector2Int]
    """Shorthand for ``Vector2Int(1, 1)``"""
    up: ClassVar[Vector2Int]
    """A unit vector pointing up (vector j). Shorthand for ``Vector2Int(0, 1)``"""
    down: ClassVar[Vector2Int]
    """A unit vector pointing down. Shorthand for ``Vector2Int(0, -1)``"""
    left: ClassVar[Vector2Int]
    """A unit vector pointing left. Shorthand for ``Vector2Int(-1, 0)``"""
    right: ClassVar[Vector2Int]
    """A unit vector pointing right (vector i). Shorthand for ``Vector2Int(1, 0)``"""

    def __init__(self, x: int, y: int) -> None: ...

    def __getitem__(self, i: SupportsIndex) -> int: ...

    @property
    def x(self) -> int: ...

    @property
    def y(self) -> int: ...

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...

    def __add__(self, other: Vector2Int) -> Vector2Int: ...

    def __sub__(self, other: Vector2Int) -> Vector2Int: ...

    def __mul__(self, other: Vector2Int | int) -> Vector2Int: ...

    def __rmul__(self, other: Vector2Int | int) -> Vector2Int: ...

    def __truediv__(self, other: Vector2Int | int | float) -> Vector2: ...

    def __floordiv__(self, other: Vector2Int | int) -> Vector2Int: ...

    def __mod__(self, other: Vector2Int | int) -> Vector2Int: ...

    def __divmod__(self, other: Vector2Int | int) -> tuple[Vector2Int, Vector2Int]: ...

    def __neg__(self) -> Vector2Int: ...

    def __abs__(self) -> Vector2Int: ...

    def __eq__(self, other: Vector2Int) -> bool: ...

    def __iter__(self) -> Iterator[int]: ...

    def __hash__(self) -> int: ...

    @property
    def magnitude(self) -> float:
        """The length of this vector."""
        ...

    @staticmethod
    def distance(a: Vector2Int, b: Vector2Int) -> float:
        """Returns the distance between a and b."""
        ...

    @staticmethod
    def ceil(v: Vector2) -> Vector2Int:
        """Create a new `Vector2Int` by ceiling the components of the given `Vector2`."""
        ...

    @staticmethod
    def floor(v: Vector2) -> Vector2Int:
        """Create a new `Vector2Int` by flooring the components of the given `Vector2`."""
        ...

    @staticmethod
    def round(v: Vector2) -> Vector2Int:
        """Create a new `Vector2Int` by rounding the components of the given `Vector2`."""
        ...

    @staticmethod
    def trunc(v: Vector2) -> Vector2Int:
        """Create a new `Vector2Int` by truncating the components of the given `Vector2`. Truncating is equivalent to `int(float_value)`."""
        ...

    @staticmethod
    def min(a: Vector2Int, b: Vector2Int) -> Vector2Int:
        """Create a new `Vector2Int` by selecting the smallest components of the two given `Vector2Int` instances."""
        ...

    @staticmethod
    def max(a: Vector2Int, b: Vector2Int) -> Vector2Int:
        """Create a new `Vector2Int` by selecting the largest components of the two given `Vector2Int` instances."""
        ...

    def to_vector2(self) -> Vector2:
        """`Vector2Int` to `Vector2` conversion."""
        ...

    def to_tuple(self) -> tuple[int, int]: ...
    def to_dict(self) -> dict[str, int]: ...
