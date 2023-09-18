from typing import Self, final

from .. import hypot, ceil, floor, Vector2Int, Vector2, MVector2

@final
class MVector2Int:
    """A mutable two-dimensional vector with integer precision."""
    __slots__ = "x", "y"

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    @classmethod
    def from_immutable(cls, immutable: Vector2Int) -> Self:
        return cls(immutable.x, immutable.y)

    #region Instantiation Helpers
    @classmethod
    def zero(cls) -> Self:
        """Shorthand for ``math.Vector2Int(0, 0)``"""
        return cls(0, 0)

    @classmethod
    def one(cls) -> Self:
        """Shorthand for ``math.Vector2Int(1, 1)``"""
        return cls(1, 1)


    @classmethod
    def up(cls) -> Self:
        """A unit vector pointing up (vector j). Shorthand for ``math.Vector2Int(0, 1)``"""
        return cls(0, 1)

    @classmethod
    def down(cls) -> Self:
        """A unit vector pointing down. Shorthand for ``math.Vector2Int(0, -1)``"""
        return cls(0, -1)

    @classmethod
    def left(cls) -> Self:
        """A unit vector pointing left. Shorthand for ``math.Vector2Int(-1, 0)``"""
        return cls(-1, 0)

    @classmethod
    def right(cls) -> Self:
        """A unit vector pointing right (vector i). Shorthand for ``math.Vector2Int(1, 0)``"""
        return cls(1, 0)
    #endregion

    #region Operators
    def __getitem__(self, i: int) -> int:
        if i == 0:
            return self.x
        if i == 1:
            return self.y
        raise IndexError(i)

    # Provides __str__ also
    def __repr__(self) -> str:
        """Unambiguous string representation of the vector."""
        return f"MVector2Int({self.x}, {self.y})"

    def __add__(self, other: Self | Vector2Int) -> Vector2Int:
        """Add (self + other)"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__add__(other)

    def __iadd__(self, other: Self | Vector2Int) -> Self:
        """Inline Add (self += other)"""
        if not isinstance(other, MVector2Int | Vector2Int):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: Self | Vector2Int) -> Vector2Int:
        """Subtract (self - other)"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__sub__(other)

    def __isub__(self, other: Self | Vector2Int) -> Self:
        """Inline Subtract (self -= other)"""
        if not isinstance(other, MVector2Int | Vector2Int):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other: Self | Vector2Int | int) -> Vector2Int:
        """Multiply (self * other)"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__mul__(other)

    def __rmul__(self, other: Self | Vector2Int | int) -> Vector2Int:
        """Reverse multiply (other * self)"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__rmul__(other)

    def __imul__(self, other: Self | Vector2Int | int) -> Self:
        """Inline Multiply (self *= other)"""
        x: int
        y: int
        if isinstance(other, MVector2Int | Vector2Int):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = other
            y = other
        else:
            return NotImplemented

        self.x *= x
        self.y *= y
        return self

    def __truediv__(self, other: Self | Vector2Int | int | float) -> Vector2:
        """Divide (self / other)"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__truediv__(other)

    def __floordiv__(self, other: Self | Vector2Int | int) -> Vector2Int:
        """Floor Divide (self // other)"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__floordiv__(other)

    def __ifloordiv__(self, other: Self | Vector2Int | int) -> Self:
        """Inline Floor Divide (self //= other)"""
        x: int
        y: int
        if isinstance(other, MVector2Int | Vector2Int):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = other
            y = other
        else:
            return NotImplemented

        self.x //= x
        self.y //= y
        return self


    def __mod__(self, other: Self | Vector2Int | int) -> Vector2Int:
        """Modulo (self % other)"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__mod__(other)

    def __divmod__(self, other: Self | Vector2Int | int) -> tuple[Vector2Int, Vector2Int]:
        """Floor division and modulo (divmod(self, other))"""
        if isinstance(other, MVector2Int):
            other = other.to_immutable()
        return self.to_immutable().__divmod__(other)


    def __eq__(self, other: Self) -> bool:
        if isinstance(other, MVector2Int):
            return self.x == other.x and self.y == other.y
        raise TypeError(f"Cannot compare equality between {type(self)} and {type(other)}")

    # Hash not implemented because object is mutable.

    #endregion

    #region Instance Properties
    @property
    def magnitude(self) -> float:
        """The length of this vector."""
        return hypot(self.x, self.y)
    #endregion

    #region Operations
    def copy(self) -> Self:
        """Make a new vector where the components' values match this vectors values."""
        return MVector2Int(self.x, self.y)
    #endregion

    #region Constructors
    @classmethod
    def ceil(cls, v: MVector2) -> Self:
        return cls(ceil(v.x), ceil(v.y))

    @classmethod
    def floor(cls, v: MVector2) -> Self:
        return cls(floor(v.x), floor(v.y))

    @classmethod
    def round(cls, v: MVector2) -> Self:
        return cls(round(v.x), round(v.y))

    @classmethod
    def min(cls, a: Self, b: Self) -> Self:
        """Returns a vector that is made from the smallest components of two vectors."""
        return cls(min(a.x, b.x), min(a.y, b.y))

    @classmethod
    def max(cls, a: Self, b: Self) -> Self:
        """Returns a vector that is made from the largest components of two vectors."""
        return cls(max(a.x, b.x), max(a.y, b.y))
    #endregion

    #region Conversions
    def to_mvector2(self) -> MVector2:
        return MVector2(float(self.x), float(self.y))

    def to_immutable(self) -> Vector2Int:
        return Vector2Int(self.x, self.y)

    def to_int_dict(self) -> dict[str, int]:
        return {"x": self.x, "y": self.y}
    #endregion
