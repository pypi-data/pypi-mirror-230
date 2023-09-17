from typing import Final, Iterable, NamedTuple, Self, final

from .. import Vector2Int, Rect


@final
class RectInt(NamedTuple):
    """
    A 2D Rectangle defined by X and Y position, width and height with integer precision.

    The functionality of this rect depends on the coordinate space used.
    When X increases to the right and Y increases upwards, position represents the bottom-left corner of the rectangle.
    When X increases to the right and Y increases downwards, position represents the top-left corner of the rectange.
    """

    x: int
    y: int
    w: int
    h: int

    @classmethod
    @property
    def zero(cls) -> Self:
        """Shorthand for ``math.RectInt(0, 0, 0, 0)``"""
        return _ZERO #  Returning single instance, because Rect is immutable

    #region Constructors
    @classmethod
    def from_pos(cls, position: Vector2Int, size: Vector2Int) -> Self:
        return cls(position.x, position.y, size.x, size.y)

    @classmethod
    def from_min_max(cls, xmin: int, ymin: int, xmax: int, ymax: int) -> Self:
        w: int = xmax - xmin
        h: int = ymax - ymin

        return cls(xmin, ymin, w, h)

    @classmethod
    def from_min_max_vectors(cls, min: Vector2Int, max: Vector2Int) -> Self:
        return cls.from_min_max(min.x, min.y, max.x, max.y)
    #endregion

    #region Operators

    # Provides __str__ also
    def __repr__(self) -> str:
        return f"RectInt({self.x}, {self.y}, {self.w}, {self.h})"
    #endregion

    #region Properties
    @property
    def min(self) -> Vector2Int:
        """Same as `Rect.position`"""
        return Vector2Int(self.xmin, self.ymin)
    @property
    def xmin(self) -> int:
        """Same as `Rect.x`"""
        return self.x
    @property
    def ymin(self) -> int:
        """Same as `Rect.y`"""
        return self.y

    @property
    def max(self) -> Vector2Int:
        return Vector2Int(self.xmax, self.ymax)
    @property
    def xmax(self) -> int:
        return self.x + self.w
    @property
    def ymax(self) -> int:
        return self.y + self.h

    @property
    def position(self) -> Vector2Int:
        return Vector2Int(self.x, self.y)
    @property
    def size(self) -> Vector2Int:
        return Vector2Int(self.w, self.h)

    @property
    def all_positions_within(self) -> Iterable[Vector2Int]:
        for y in range(self.ymin, self.ymax): # Return by row. (x first then y)
            for x in range(self.xmin, self.xmax):
                yield Vector2Int(x, y)
    #endregion

    #region Collisions
    def contains(self, point: Vector2Int) -> bool:
        return (point.x >= self.x) and (point.x < self.xmax) and (point.y >= self.y) and (point.y < self.ymax)

    def overlaps(self, other: Self) -> bool:
        return (
            other.xmax > self.x and
            other.x    < self.xmax and
            other.ymax > self.y and
            other.y    < self.ymax
        )
    #endregion

    #region Conversions
    def clamped_to_bounds(self, bounds: Self) -> Self:
        x: int = max(min(bounds.xmax, self.x), bounds.x)
        y: int = max(min(bounds.ymax, self.y), bounds.y)
        w: int = min(bounds.xmax - self.x, self.w)
        h: int = min(bounds.ymax - self.y, self.h)

        return RectInt(x, y, w, h)

    def to_rect(self) -> Rect:
        return Rect(float(self.x), float(self.y), float(self.w), float(self.h))

    def to_int_dict(self) -> dict[str, int]:
        return self._asdict()
    #endregion

_ZERO: Final[RectInt] = RectInt(0, 0, 0, 0)
