from typing import NamedTuple, Self, final, Final

from .. import hypot, ceil, floor, trunc, round, Vector2

@final
class Vector2Int(NamedTuple):
    """An immutable two-dimensional vector with integer precision."""
    x: int
    y: int

    #region Class Properties
    @classmethod
    @property
    def zero(cls) -> Self:
        """Shorthand for ``math.Vector2Int(0, 0)``"""
        return _ZERO #  Returning single instance, because Vector2Int is immutable

    @classmethod
    @property
    def one(cls) -> Self:
        """Shorthand for ``math.Vector2Int(1, 1)``"""
        return _ONE #  Returning single instance, because Vector2Int is immutable


    @classmethod
    @property
    def up(cls) -> Self:
        """A unit vector pointing up (vector j). Shorthand for ``math.Vector2Int(0, 1)``"""
        return _UP #  Returning single instance, because Vector2Int is immutable

    @classmethod
    @property
    def down(cls) -> Self:
        """A unit vector pointing down. Shorthand for ``math.Vector2Int(0, -1)``"""
        return _DOWN #  Returning single instance, because Vector2Int is immutable

    @classmethod
    @property
    def left(cls) -> Self:
        """A unit vector pointing left. Shorthand for ``math.Vector2Int(-1, 0)``"""
        return _LEFT #  Returning single instance, because Vector2Int is immutable

    @classmethod
    @property
    def right(cls) -> Self:
        """A unit vector pointing right (vector i). Shorthand for ``math.Vector2Int(1, 0)``"""
        return _RIGHT #  Returning single instance, because Vector2Int is immutable
    #endregion

    #region Operators

    # Provides __str__ also
    def __repr__(self) -> str:
        """Unambiguous string representation of the vector."""
        return f"Vector2Int({self.x}, {self.y})"

    def __add__(self, other: Self) -> Self:
        """Add (self + other)"""
        if not isinstance(other, Vector2Int):
            return NotImplemented
        return Vector2Int(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        """Subtract (self - other)"""
        if not isinstance(other, Vector2Int):
            return NotImplemented
        return Vector2Int(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Self | int) -> Self:
        """Multiply (self * other)"""
        x: int
        y: int
        if isinstance(other, Vector2Int):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2Int(self.x * x, self.y * y)

    def __rmul__(self, other: Self | int) -> Self:
        """Reverse multiply (other * self)"""
        return self.__mul__(other) # other * self = self * other

    def __truediv__(self, other: Self | int | float) -> Vector2:
        """Divide (self / other)"""
        x: float
        y: float
        if isinstance(other, Vector2Int):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2(self.x / x, self.y / y)

    def __floordiv__(self, other: Self | int) -> Self:
        """Floor Divide (self // other)"""
        x: int
        y: int
        if isinstance(other, Vector2Int):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2Int(self.x // x, self.y // y)


    def __mod__(self, other: Self | int) -> Self:
        """Modulo (self % other)"""
        x: int
        y: int
        if isinstance(other, Vector2Int):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2Int(self.x % x, self.y % y)

    def __divmod__(self, other: Self | int) -> tuple[Self, Self]:
        """Floor division and modulo (divmod(self, other))"""
        x: int
        y: int
        if isinstance(other, Vector2Int):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = other
            y = other
        else:
            return NotImplemented

        x_fdiv, x_mod = divmod(self.x, x)
        y_fdiv, y_mod = divmod(self.y, y)
        return (Vector2Int(x_fdiv, y_fdiv), Vector2Int(x_mod, y_mod))


    def __neg__(self) -> Self:
        """Negate (-self)"""
        return Vector2Int(-self.x, -self.y)

    def __abs__(self) -> Self:
        """Absolute value (abs(self))"""
        return Vector2Int(abs(self.x), abs(self.y))

    # __eq__ and __hash__ are provided by NamedTuple

    #endregion

    #region Instance Properties
    @property
    def magnitude(self) -> float:
        """The length of this vector."""
        return hypot(self.x, self.y)
    #endregion

    #region Relation
    @classmethod
    def distance(cls, a: Self, b: Self):
        """Returns the distance between a and b."""
        diff = a - b
        return diff.magnitude
    #endregion

    #region Constructors
    @classmethod
    def ceil(cls, v: Vector2) -> Self:
        return cls(ceil(v.x), ceil(v.y))

    @classmethod
    def floor(cls, v: Vector2) -> Self:
        return cls(floor(v.x), floor(v.y))

    @classmethod
    def round(cls, v: Vector2) -> Self:
        return cls(round(v.x), round(v.y))

    @classmethod
    def trunc(cls, v: Vector2) -> Self:
        return cls(trunc(v.x), trunc(v.y))

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
    def to_vector2(self) -> Vector2:
        return Vector2(float(self.x), float(self.y))

    def to_int_dict(self) -> dict[str, int]:
        return self._asdict()
    #endregion

_ZERO: Final[Vector2Int] = Vector2Int(0, 0)
_ONE: Final[Vector2Int] = Vector2Int(1, 1)

_UP: Final[Vector2Int] = Vector2Int(0, 1)
_DOWN: Final[Vector2Int] = Vector2Int(0, -1)
_LEFT: Final[Vector2Int] = Vector2Int(-1, 0)
_RIGHT: Final[Vector2Int] = Vector2Int(1, 0)
