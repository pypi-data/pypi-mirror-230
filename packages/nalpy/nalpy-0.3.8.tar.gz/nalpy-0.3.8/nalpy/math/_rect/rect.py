from typing import Final, NamedTuple, Self, final

from .. import lerp, inverse_lerp, Vector2


@final
class Rect(NamedTuple):
    """
    A 2D Rectangle defined by X and Y position, width and height.

    The functionality of this rect depends on the coordinate space used.
    When X increases to the right and Y increases upwards, position represents the bottom-left corner of the rectangle.
    When X increases to the right and Y increases downwards, position represents the top-left corner of the rectange.
    """

    x: float
    y: float
    w: float
    h: float

    @classmethod
    @property
    def zero(cls) -> Self:
        """Shorthand for ``math.Rect(0.0, 0.0, 0.0, 0.0)``"""
        return _ZERO #  Returning single instance, because Rect is immutable

    #region Constructors
    @classmethod
    def from_pos(cls, position: Vector2, size: Vector2) -> Self:
        return cls(position.x, position.y, size.x, size.y)

    @classmethod
    def from_center(cls, center: Vector2, size: Vector2) -> Self:
        x: float = center.x - (size.x / 2)
        y: float = center.y - (size.y / 2)
        return cls(x, y, size.x, size.y)

    @classmethod
    def from_min_max(cls, xmin: float, ymin: float, xmax: float, ymax: float) -> Self:
        w: float = xmax - xmin
        h: float = ymax - ymin

        return cls(xmin, ymin, w, h)

    @classmethod
    def from_min_max_vectors(cls, min: Vector2, max: Vector2) -> Self:
        return cls.from_min_max(min.x, min.y, max.x, max.y)
    #endregion

    #region Operators

    # Provides __str__ also
    def __repr__(self) -> str:
        return f"Rect({self.x}, {self.y}, {self.w}, {self.h})"
    #endregion

    #region Properties
    @property
    def center(self) -> Vector2:
        return Vector2(self.xcenter, self.ycenter)
    @property
    def xcenter(self) -> float:
        return self.x + (self.w / 2.0)
    @property
    def ycenter(self) -> float:
        return self.y + (self.h / 2.0)

    @property
    def min(self) -> Vector2:
        """Same as `Rect.position`"""
        return Vector2(self.xmin, self.ymin)
    @property
    def xmin(self) -> float:
        """Same as `Rect.x`"""
        return self.x
    @property
    def ymin(self) -> float:
        """Same as `Rect.y`"""
        return self.y

    @property
    def max(self) -> Vector2:
        return Vector2(self.xmax, self.ymax)
    @property
    def xmax(self) -> float:
        return self.x + self.w
    @property
    def ymax(self) -> float:
        return self.y + self.h

    @property
    def position(self) -> Vector2:
        return Vector2(self.x, self.y)
    @property
    def size(self) -> Vector2:
        return Vector2(self.w, self.h)
    #endregion

    #region Collisions
    def contains(self, point: Vector2) -> bool:
        return (point.x >= self.x) and (point.x < self.xmax) and (point.y >= self.y) and (point.y < self.ymax)

    def overlaps(self, other: Self) -> bool:
        return (
            other.xmax > self.x and
            other.x    < self.xmax and
            other.ymax > self.y and
            other.y    < self.ymax
        )
    #endregion

    #region Normalization
    @classmethod
    def normalized_to_point(cls, rect: Self, normalized_rect_coordinates: Vector2) -> Vector2:
        return Vector2(
            lerp(rect.x, rect.xmax, normalized_rect_coordinates.x),
            lerp(rect.y, rect.ymax, normalized_rect_coordinates.y)
        )

    @classmethod
    def point_to_normalized(cls, rect: Self, point: Vector2) -> Vector2:
        return Vector2(
            inverse_lerp(rect.x, rect.xmax, point.x),
            inverse_lerp(rect.y, rect.ymax, point.y)
        )
    #endregion

    #region Conversions
    def to_int_tuple(self) -> tuple[int, int, int, int]:
        return (round(self.x), round(self.y), round(self.w), round(self.h))

    def to_float_dict(self) -> dict[str, float]:
        return self._asdict()
    #endregion

_ZERO: Final[Rect] = Rect(0.0, 0.0, 0.0, 0.0)
