#cython: language_level=3

from libc.math cimport hypot

from .vector2_int cimport Vector2Int

ctypedef long long int int_t

# Modified from MVector2
cdef class MVector2Int:
    @staticmethod
    def zero():
        return MVector2Int(0, 0)
    @staticmethod
    def one():
        return MVector2Int(1, 1)
    @staticmethod
    def up():
        return MVector2Int(0, 1)
    @staticmethod
    def down():
        return MVector2Int(0, -1)
    @staticmethod
    def left():
        return MVector2Int(-1, 0)
    @staticmethod
    def right():
        return MVector2Int(1, 0)

    cdef public int_t x
    cdef public int_t y

    def __init__(self, int_t x, int_t y):
        self.x = x
        self.y = y

    @staticmethod
    def from_immutable(Vector2Int immutable):
        return MVector2Int(immutable.x, immutable.y)

    def __getitem__(self, Py_ssize_t i):
        if i == 0:
            return self.x
        if i == 1:
            return self.y

        raise IndexError(i)

    def __repr__(self):
        return f"MVector2Int({self.x}, {self.y})"

    def __len__(self):
        return 2

    # Only in-place arithmetic supported. For other arithmetic operations, conversion to Vector2Int is required.
    def __iadd__(self, other):
        if not isinstance(other, (MVector2Int, Vector2Int)):
            return NotImplemented

        self.x += <int_t>other.x # Casting to force C addition instead of Python addition
        self.y += <int_t>other.y

        return self

    def __isub__(self, other):
        if not isinstance(other, (MVector2Int, Vector2Int)):
            return NotImplemented

        self.x += <int_t>other.x
        self.y += <int_t>other.y

        return self

    def __imul__(self, other):
        cdef int_t x
        cdef int_t y
        if isinstance(other, (MVector2Int, Vector2Int)):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = y = other
        else:
            return NotImplemented

        self.x *= x
        self.y *= y

        return self

    def __ifloordiv__(self, other):
        cdef int_t x
        cdef int_t y
        if isinstance(other, (MVector2Int, Vector2Int)):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = y = other
        else:
            return NotImplemented

        self.x //= x
        self.y //= y

        return self

    def __imod__(self, other):
        cdef int_t x
        cdef int_t y
        if isinstance(other, (MVector2Int, Vector2Int)):
            x = other.x
            y = other.y
        elif isinstance(other, int):
            x = y = other
        else:
            return NotImplemented

        self.x %= x
        self.y %= y

        return self

    def __eq__(self, MVector2Int other):
        return self.x == other.x and self.y == other.y

    # NOTE: Object is mutable, do not implement __hash__


    @property
    def magnitude(self):
        return hypot(<double>self.x, <double>self.y)

    def copy(self):
        return MVector2Int(self.x, self.y)


    @staticmethod
    def min(MVector2Int a, MVector2Int b):
        return MVector2Int(min(a.x, b.x), min(a.y, b.y))

    @staticmethod
    def max(MVector2Int a, MVector2Int b):
        return MVector2Int(max(a.x, b.x), max(a.y, b.y))


    def to_immutable(self):
        return Vector2Int(self.x, self.y)

    def to_tuple(self):
        return (self.x, self.y)

    def to_dict(self):
        return {"x": self.x, "y": self.y}
