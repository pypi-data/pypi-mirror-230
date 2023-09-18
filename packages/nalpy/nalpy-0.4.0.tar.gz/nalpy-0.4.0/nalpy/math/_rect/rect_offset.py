from typing import NamedTuple, final

from .. import Rect

@final
class RectOffset(NamedTuple):
    """
    Offsets for rectangles, borders, etc.

    Assumes that X increases to the right and Y increases downwards.
    """

    left: float
    right: float
    top: float
    bottom: float

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom

    def add(self, rect: Rect) -> Rect:
        """Add the border offsets to a rect."""

        return Rect.from_min_max(
            rect.xmin + self.left,
            rect.ymin + self.top,
            rect.xmax - self.right,
            rect.ymax - self.bottom
        )

    def remove(self, rect: Rect) -> Rect:
        """Remove the border offsets from a rect."""

        return Rect.from_min_max(
            rect.xmin - self.left,
            rect.ymin - self.top,
            rect.xmax + self.right,
            rect.ymax + self.bottom
        )

    def to_int_tuple(self) -> tuple[int, int, int, int]:
        left: int = round(self.left)
        right: int = round(self.right)
        top: int = round(self.top)
        bottom: int = round(self.bottom)
        return (left, right, top, bottom)

    def to_float_dict(self) -> dict[str, float]:
        return self._asdict()
