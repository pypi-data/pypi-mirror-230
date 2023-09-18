from typing import NamedTuple, Self, final, Final

from .. import hypot, clamp01, sqrt, clamp, acos, degrees, sign

@final
class Vector2(NamedTuple):
    """An immutable two-dimensional vector"""
    x: float
    y: float

    #region Class Properties
    @classmethod
    @property
    def zero(cls) -> Self:
        """Shorthand for ``math.Vector2(0.0, 0.0)``"""
        return _ZERO #  Returning single instance, because Vector2 is immutable

    @classmethod
    @property
    def one(cls) -> Self:
        """Shorthand for ``math.Vector2(1.0, 1.0)``"""
        return _ONE #  Returning single instance, because Vector2 is immutable


    @classmethod
    @property
    def up(cls) -> Self:
        """A unit vector pointing up (vector j). Shorthand for ``math.Vector2(0.0, 1.0)``"""
        return _UP #  Returning single instance, because Vector2 is immutable

    @classmethod
    @property
    def down(cls) -> Self:
        """A unit vector pointing down. Shorthand for ``math.Vector2(0.0, -1.0)``"""
        return _DOWN #  Returning single instance, because Vector2 is immutable

    @classmethod
    @property
    def left(cls) -> Self:
        """A unit vector pointing left. Shorthand for ``math.Vector2(-1.0, 0.0)``"""
        return _LEFT #  Returning single instance, because Vector2 is immutable

    @classmethod
    @property
    def right(cls) -> Self:
        """A unit vector pointing right (vector i). Shorthand for ``math.Vector2(1.0, 0.0)``"""
        return _RIGHT #  Returning single instance, because Vector2 is immutable
    #endregion

    #region Operators

    # Provides __str__ also
    def __repr__(self) -> str:
        """Unambiguous string representation of the vector."""
        return f"Vector2({self.x}, {self.y})"

    def __add__(self, other: Self) -> Self:
        """Add (self + other)"""
        if not isinstance(other, Vector2):
            return NotImplemented
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        """Subtract (self - other)"""
        if not isinstance(other, Vector2):
            return NotImplemented
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Self | float | int) -> Self:
        """Multiply (self * other)"""
        x: float | int
        y: float | int
        if isinstance(other, Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2(self.x * x, self.y * y)

    def __rmul__(self, other: Self | float | int) -> Self:
        """Reverse multiply (other * self)"""
        return self.__mul__(other) # other * self = self * other

    def __truediv__(self, other: Self | float | int) -> Self:
        """Divide (self / other)"""
        x: float | int
        y: float | int
        if isinstance(other, Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2(self.x / x, self.y / y)

    def __floordiv__(self, other: Self | float | int) -> Self:
        """Floor Divide (self // other)"""
        x: float | int
        y: float | int
        if isinstance(other, Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2(self.x // x, self.y // y)


    def __mod__(self, other: Self | float | int) -> Self:
        """Modulo (self % other)"""
        x: float | int
        y: float | int
        if isinstance(other, Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        return Vector2(self.x % x, self.y % y)

    def __divmod__(self, other: Self | float | int) -> tuple[Self, Self]:
        """Floor division and modulo (divmod(self, other))"""
        x: float | int
        y: float | int
        if isinstance(other, Vector2):
            x = other.x
            y = other.y
        elif isinstance(other, int | float):
            x = other
            y = other
        else:
            return NotImplemented

        x_fdiv, x_mod = divmod(self.x, x)
        y_fdiv, y_mod = divmod(self.y, y)
        return (Vector2(x_fdiv, y_fdiv), Vector2(x_mod, y_mod))


    def __neg__(self) -> Self:
        """Negate (-self)"""
        return Vector2(-self.x, -self.y)

    def __abs__(self) -> Self:
        """Absolute value (abs(self))"""
        return Vector2(abs(self.x), abs(self.y))

    # __eq__ and __hash__ are provided by NamedTuple

    #endregion

    #region Instance Properties
    @property
    def magnitude(self) -> float:
        """The length of this vector."""
        return hypot(self.x, self.y)

    @property
    def normalized(self) -> Self:
        """A copy of this vector with a magnitude of 1"""
        mag: float = self.magnitude
        if mag == 0:
            raise ValueError("Vector does not have a direction to normalize to.")
        return Vector2(self.x / mag, self.y / mag)
    #endregion

    #region Mathematic Operations
    @classmethod
    def dot(cls, a: Self, b: Self) -> float:
        """Dot Product of two vectors."""
        return (a.x * b.x) + (a.y * b.y)
    #endregion

    #region Interpolation
    @classmethod
    def lerp(cls, a: Self, b: Self, t: float) -> Self:
        """
        Linearly interpolates between vectors ``a`` and ``b`` by ``t``.

        The parameter ``t`` is clamped to the range [0, 1].
        """
        t = clamp01(t)
        lerp_x = a.x + ((b.x - a.x) * t)
        lerp_y = a.y + ((b.y - a.y) * t)
        return Vector2(lerp_x, lerp_y)

    @classmethod
    def lerp_unclamped(cls, a: Self, b: Self, t: float) -> Self:
        """
        Linearly interpolates between vectors ``a`` and ``b`` by ``t``.

        The parameter ``t`` is not clamped.
        """
        lerp_x = a.x + ((b.x - a.x) * t)
        lerp_y = a.y + ((b.y - a.y) * t)
        return Vector2(lerp_x, lerp_y)

    @classmethod
    def move_towards(cls, current: Self, target: Self, max_distance_delta: float):
        """Moves a point current towards target."""
        to_vector_x: float = target.x - current.x
        to_vector_y: float = target.y - current.y

        sqDist: float = to_vector_x * to_vector_x + to_vector_y * to_vector_y

        if sqDist == 0 or (max_distance_delta >= 0 and sqDist <= max_distance_delta * max_distance_delta):
            return target

        dist: float = sqrt(sqDist)

        move_x = current.x + to_vector_x / dist * max_distance_delta
        move_y = current.y + to_vector_y / dist * max_distance_delta
        return Vector2(move_x, move_y)
    #endregion

    #region Rotation
    @classmethod
    def perpendicular(cls, vector: Self) -> Self:
        """
        Returns a 2D vector with the same magnitude, but perpendicular to the given 2D vector.
        The result is always rotated 90-degrees in a counter-clockwise direction for a 2D coordinate system where the positive Y axis goes up.
        """
        return Vector2(-vector.y, vector.x)

    @classmethod
    def reflect(cls, vector: Self, normal: Self):
        """Reflects a vector off the vector defined by a normal."""
        factor: float = -2 * Vector2.dot(normal, vector)
        return Vector2(factor * normal.x + vector.x, factor * normal.y + vector.y)
    #endregion

    #region Relation
    @classmethod
    def angle(cls, _from: Self, _to: Self) -> float:
        """
        Gets the unsigned angle in degrees between from and to.

        NOTE: The angle returned will always be between 0 and 180 degrees, because the method returns the smallest angle between the vectors.
        """
        denom: float = _from.magnitude * _to.magnitude
        if denom == 0.0:
            return 0.0

        dot: float = Vector2.dot(_from, _to)
        cos_val: float = clamp(dot / denom, -1.0, 1.0)
        return degrees(acos(cos_val))

    @classmethod
    def signed_angle(cls, _from: Self, _to: Self) -> float:
        """
        Gets the signed angle in degrees between from and to. The angle returned is the signed counterclockwise angle between the two vectors.

        NOTE: The angle returned will always be between -180 and 180 degrees, because the method returns the smallest angle between the vectors.
        """
        unsigned_angle: float = Vector2.angle(_from, _to)
        s: float = sign((_from.x * _to.y) - (_from.y * _to.x))
        return unsigned_angle * s

    @classmethod
    def distance(cls, a: Self, b: Self):
        """Returns the distance between a and b."""
        diff = a - b
        return diff.magnitude
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

    #region Conversions
    def to_int_tuple(self) -> tuple[int, int]:
        return (round(self.x), round(self.y))

    def to_float_dict(self) -> dict[str, float]:
        return self._asdict()
    #endregion

_ZERO: Final[Vector2] = Vector2(0.0, 0.0)
_ONE: Final[Vector2] = Vector2(1.0, 1.0)

_UP: Final[Vector2] = Vector2(0.0, 1.0)
_DOWN: Final[Vector2] = Vector2(0.0, -1.0)
_LEFT: Final[Vector2] = Vector2(-1.0, 0.0)
_RIGHT: Final[Vector2] = Vector2(1.0, 0.0)
