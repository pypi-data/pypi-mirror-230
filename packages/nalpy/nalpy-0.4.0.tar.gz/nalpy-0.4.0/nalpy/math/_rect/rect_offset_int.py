from typing import NamedTuple, final

from .. import RectInt, RectOffset

@final
class RectOffsetInt(NamedTuple):
    """
    Offsets for rectangles, borders, etc. with integer precision.

    Assumes that X increases to the right and Y increases downwards.
    """

    left: int
    right: int
    top: int
    bottom: int

    @property
    def horizontal(self) -> int:
        return self.left + self.right

    @property
    def vertical(self) -> int:
        return self.top + self.bottom

    def add(self, rect: RectInt) -> RectInt:
        """Add the border offsets to a rect."""

        return RectInt.from_min_max(
            rect.xmin + self.left,
            rect.ymin + self.top,
            rect.xmax - self.right,
            rect.ymax - self.bottom
        )

    def remove(self, rect: RectInt) -> RectInt:
        """Remove the border offsets from a rect."""

        return RectInt.from_min_max(
            rect.xmin - self.left,
            rect.ymin - self.top,
            rect.xmax + self.right,
            rect.ymax + self.bottom
        )

    def to_rect_offset(self) -> RectOffset:
        return RectOffset(float(self.left), float(self.right), float(self.top), float(self.bottom))

    def to_int_tuple(self) -> tuple[int, int, int, int]:
        left: int = round(self.left)
        right: int = round(self.right)
        top: int = round(self.top)
        bottom: int = round(self.bottom)
        return (left, right, top, bottom)

    def to_int_dict(self) -> dict[str, int]:
        return self._asdict()
