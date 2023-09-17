from typing import Self, SupportsFloat, final

from .. import hypot, Vector2

@final
class MVector2:
    """A mutable two-dimensional vector"""
    __slots__ = "x", "y"

    def __init__(self, x: SupportsFloat, y: SupportsFloat) -> None:
        self.x: float = float(x)
        self.y: float = float(y)

    @classmethod
    def from_immutable(cls, immutable: Vector2) -> Self:
        return cls(immutable.x, immutable.y)

    #region Instantiation Helpers
    @classmethod
    def zero(cls) -> Self:
        """Shorthand for ``math.MVector2(0.0, 0.0)``"""
        return cls(0.0, 0.0)

    @classmethod
    def one(cls) -> Self:
        """Shorthand for ``math.MVector2(1.0, 1.0)``"""
        return cls(1.0, 1.0)


    @classmethod
    def up(cls) -> Self:
        """A unit vector pointing up (vector j). Shorthand for ``math.MVector2(0.0, 1.0)``"""
        return cls(0.0, 1.0)

    @classmethod
    def down(cls) -> Self:
        """A unit vector pointing down. Shorthand for ``math.MVector2(0.0, -1.0)``"""
        return cls(0.0, -1.0)

    @classmethod
    def left(cls) -> Self:
        """A unit vector pointing left. Shorthand for ``math.MVector2(-1.0, 0.0)``"""
        return cls(-1.0, 0.0)

    @classmethod
    def right(cls) -> Self:
        """A unit vector pointing right (vector i). Shorthand for ``math.MVector2(1.0, 0.0)``"""
        return cls(1.0, 0.0)
    #endregion

    #region Operators
    def __getitem__(self, i: int) -> float:
        if i == 0:
            return self.x
        if i == 1:
            return self.y
        raise IndexError(i)

    # Provides __str__ also
    def __repr__(self) -> str:
        """Unambiguous string representation of the vector."""
        return f"MVector2({self.x}, {self.y})"

    def __add__(self, other: Self | Vector2) -> Vector2:
        """Add (self + other)"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__add__(other)

    def __iadd__(self, other: Self | Vector2) -> Self:
        """Inline Add (self += other)"""
        if not isinstance(other, MVector2 | Vector2):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other: Self | Vector2) -> Vector2:
        """Subtract (self - other)"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__sub__(other)

    def __isub__(self, other: Self | Vector2) -> Self:
        """Inline Subtract (self -= other)"""
        if not isinstance(other, MVector2 | Vector2):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other: Self | Vector2 | float | int) -> Vector2:
        """Multiply (self * other)"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__mul__(other)

    def __rmul__(self, other: Self | Vector2 | float | int) -> Vector2:
        """Reverse multiply (other * self)"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__rmul__(other)

    def __imul__(self, other: Self | Vector2 | float | int) -> Self:
        """Inline Multiply (self *= other)"""
        x: float | int
        y: float | int
        if isinstance(other, MVector2 | Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        self.x *= x
        self.y *= y
        return self

    def __truediv__(self, other: Self | Vector2 | float | int) -> Vector2:
        """Divide (self / other)"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__truediv__(other)

    def __itruediv__(self, other: Self | Vector2 | float | int) -> Self:
        """Inline Divide (self /= other)"""
        x: float | int
        y: float | int
        if isinstance(other, MVector2 | Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        self.x /= x
        self.y /= y
        return self

    def __floordiv__(self, other: Self | Vector2 | float | int) -> Vector2:
        """Floor Divide (self // other)"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__floordiv__(other)

    def __ifloordiv__(self, other: Self | Vector2 | float | int) -> Self:
        """Inline Floor Divide (self //= other)"""
        x: float | int
        y: float | int
        if isinstance(other, MVector2 | Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        self.x //= x
        self.y //= y
        return self


    def __mod__(self, other: Self | Vector2 | float | int) -> Vector2:
        """Modulo (self % other)"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__mod__(other)

    def __divmod__(self, other: Self | Vector2 | float | int) -> tuple[Vector2, Vector2]:
        """Floor division and modulo (divmod(self, other))"""
        if isinstance(other, MVector2):
            other = other.to_immutable()
        return self.to_immutable().__divmod__(other)


    def __eq__(self, other: Self) -> bool:
        if isinstance(other, MVector2):
            return self.x == other.x and self.y == other.y
        raise TypeError(f"Cannot compare equality between {type(self)} and {type(other)}")

    # Hash not implemented because object is mutable.

    #endregion

    #region Instance Properties
    @property
    def magnitude(self) -> float:
        """The length of this vector."""
        return hypot(self.x, self.y)

    @property
    def normalized(self) -> Self:
        """A copy of this vector with a magnitude of 1"""
        v: MVector2 = self.copy()
        v.normalize()
        return v
    #endregion

    #region Operations
    def normalize(self) -> None:
        """Make this vector keep its direction, but have a magnitude of 1. Operates in place."""
        mag: float = self.magnitude
        if mag == 0:
            self.x = 0.0
            self.y = 0.0
        else:
            self.x /= mag
            self.y /= mag

    def copy(self) -> Self:
        """Make a new vector where the components' values match this vectors values."""
        return MVector2(self.x, self.y)
    #endregion

    #region Contructors
    @classmethod
    def min(cls, a: Self, b: Self) -> Self:
        """Returns a vector that is made from the smallest components of two vectors."""
        return cls(min(a.x, b.x), min(a.y, b.y))

    @classmethod
    def max(cls, a: Self, b: Self) -> Self:
        """Returns a vector that is made from the largest components of two vectors."""
        return cls(max(a.x, b.x), max(a.y, b.y))
    #endregion

    #region Conversion
    def to_int_tuple(self) -> tuple[int, int]:
        return (round(self.x), round(self.y))

    def to_immutable(self) -> Vector2:
        return Vector2(self.x, self.y)

    def to_float_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}
    #endregion
