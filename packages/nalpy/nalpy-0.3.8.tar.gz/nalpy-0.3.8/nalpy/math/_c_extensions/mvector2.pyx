#cython: language_level=3

from libc.math cimport hypot

from .vector2 cimport Vector2

cdef class MVector2:
    @staticmethod
    def zero():
        return MVector2(0.0, 0.0)
    @staticmethod
    def one():
        return MVector2(1.0, 1.0)
    @staticmethod
    def up():
        return MVector2(0.0, 1.0)
    @staticmethod
    def down():
        return MVector2(0.0, -1.0)
    @staticmethod
    def left():
        return MVector2(-1.0, 0.0)
    @staticmethod
    def right():
        return MVector2(1.0, 0.0)

    def __init__(self, double x, double y):
        self.x = x
        self.y = y

    @staticmethod
    def from_immutable(Vector2 immutable):
        return MVector2(immutable.x, immutable.y)

    def __getitem__(self, Py_ssize_t i):
        if i == 0:
            return self.x
        if i == 1:
            return self.y

        raise IndexError(i)

    def __repr__(self):
        return f"MVector2({self.x}, {self.y})"

    def __len__(self):
        return 2

    # Only in-place arithmetic supported. For other arithmetic operations, conversion to Vector2 is required.
    def __iadd__(self, other):
        if not isinstance(other, (MVector2, Vector2)):
            return NotImplemented

        self.x += <double>other.x # Casting to force C addition instead of Python addition
        self.y += <double>other.y

        return self

    def __isub__(self, other):
        if not isinstance(other, (MVector2, Vector2)):
            return NotImplemented

        self.x += <double>other.x
        self.y += <double>other.y

        return self

    def __imul__(self, other): # Template from Vector2
        cdef double x
        cdef double y
        if isinstance(other, (MVector2, Vector2)):
            x = other.x
            y = other.y
        elif isinstance(other, (float, int)):
            x = y = other
        else:
            return NotImplemented

        self.x *= x
        self.y *= y

        return self

    def __itruediv__(self, other):
        cdef double x
        cdef double y
        if isinstance(other, (MVector2, Vector2)):
            x = other.x
            y = other.y
        elif isinstance(other, (float, int)):
            x = y = other
        else:
            return NotImplemented

        self.x /= x
        self.y /= y

        return self

    def __ifloordiv__(self, other):
        cdef double x
        cdef double y
        if isinstance(other, (MVector2, Vector2)):
            x = other.x
            y = other.y
        elif isinstance(other, (float, int)):
            x = y = other
        else:
            return NotImplemented

        self.x //= x
        self.y //= y

        return self

    def __imod__(self, other):
        cdef double x
        cdef double y
        if isinstance(other, (MVector2, Vector2)):
            x = other.x
            y = other.y
        elif isinstance(other, (float, int)):
            x = y = other
        else:
            return NotImplemented

        self.x %= x
        self.y %= y

        return self

    def __eq__(self, MVector2 other):
        return self.x == other.x and self.y == other.y

    # NOTE: Object is mutable, do not implement __hash__


    @property
    def magnitude(self):
        return hypot(self.x, self.y)

    @property
    def normalized(self):
        cdef MVector2 v = self.copy()
        v.normalize()
        return v


    cpdef normalize(self) noexcept:
        cdef double magnitude = hypot(self.x, self.y)
        if magnitude == 0.0:
            self.x = self.y = 0.0
        else:
            self.x /= magnitude
            self.y /= magnitude

    cpdef MVector2 copy(self) noexcept:
        return MVector2(self.x, self.y)


    @staticmethod
    def min(MVector2 a, MVector2 b):
        return MVector2(min(a.x, b.x), min(a.y, b.y))

    @staticmethod
    def max(MVector2 a, MVector2 b):
        return MVector2(max(a.x, b.x), max(a.y, b.y))


    def to_immutable(self):
        return Vector2(self.x, self.y)

    def to_tuple(self):
        return (self.x, self.y)

    def to_dict(self):
        return {"x": self.x, "y": self.y}
