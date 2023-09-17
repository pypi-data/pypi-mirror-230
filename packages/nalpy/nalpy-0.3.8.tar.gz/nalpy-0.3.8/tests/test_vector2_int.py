import unittest

from nalpy.math import Vector2Int, Vector2


class BasicFunctionality(unittest.TestCase):
    def test_index(self):
        v = Vector2Int(3, 7)
        self.assertEqual(v[0], 3)
        self.assertEqual(v[1], 7)
        self.assertRaises(IndexError, lambda: v[3])

        class MockIndexObj:
            def __init__(self, i: int) -> None:
                self.__internal_index = i
            def __index__(self) -> int:
                return self.__internal_index
        self.assertEqual(v[MockIndexObj(0)], 3)
        self.assertEqual(v[MockIndexObj(1)], 7)

    def test_xy(self):
        v = Vector2Int(3, 7)
        self.assertEqual(v.x, 3)
        self.assertEqual(v.y, 7)
        self.assertRaises(AttributeError, lambda: v.z) # type: ignore

    def test_equals(self):
        v = Vector2Int(3, 3)
        self.assertEqual(v, Vector2Int(3, 3))
        self.assertNotEqual(v, Vector2Int(2, 3))
        self.assertNotEqual(v, Vector2Int(3, 2))
        self.assertNotEqual(v, Vector2Int(2, 2))

        self.assertRaises(TypeError, lambda: v == (3, 3))
        self.assertNotEqual(v, None)
        self.assertNotEqual(None, v)

    def test_hash(self):
        values: tuple[tuple[int, int], ...] = (
            (69, 420),
            (420, 69),
            (69, 69),
            (420, 420),

            (0, 0),
            (-1, -1),
            (-69, -69),
            (1000, 1000),
            (-10000, -10000)
        )

        # Vector2Int hash should match tuple hash
        for v in values:
            self.assertEqual(hash(v), hash(Vector2Int(*v)))

    def test_constants(self):
        self.assertEqual(Vector2Int.zero,  Vector2Int(0, 0))
        self.assertEqual(Vector2Int.one,   Vector2Int(1, 1))
        self.assertEqual(Vector2Int.up,    Vector2Int(0, 1))
        self.assertEqual(Vector2Int.down,  Vector2Int(0, -1))
        self.assertEqual(Vector2Int.left,  Vector2Int(-1, 0))
        self.assertEqual(Vector2Int.right, Vector2Int(1, 0))

    def test_repr(self):
        self.assertEqual(repr(Vector2Int(2, 2)), f"Vector2Int(2, 2)")
        self.assertEqual(repr(Vector2Int(69, 420)), f"Vector2Int(69, 420)")

        self.assertEqual(repr(Vector2Int(2, 2)), str(Vector2Int(2, 2)))
        self.assertEqual(repr(Vector2Int(69, 420)), str(Vector2Int(69, 420)))

    def test_addsub(self):
        b: Vector2Int = Vector2Int.one
        self.assertEqual(b + Vector2Int(2, 2), Vector2Int(3, 3))
        self.assertEqual(b + Vector2Int(0, 2), Vector2Int(1, 3))

        self.assertEqual(b - Vector2Int(2, 2), Vector2Int(-1, -1))
        self.assertEqual(b - Vector2Int(0, 2), Vector2Int(1, -1))

    def test_mult(self):
        b: Vector2Int = Vector2Int.one
        self.assertEqual(b * 2, Vector2Int(2, 2))
        self.assertEqual(2 * b, Vector2Int(2, 2))

        self.assertEqual(Vector2Int(3, 4) * b, Vector2Int(3, 4))
        self.assertEqual(b * Vector2Int(3, 4), Vector2Int(3, 4))

    def test_divmod(self):
        self.assertEqual(Vector2Int(9, 9) / 3, Vector2(3, 3))
        self.assertEqual(Vector2Int(9, 9) / Vector2Int(3, 6), Vector2(3.0, 1.5))
        self.assertEqual(Vector2Int(-9, -9) / 3, Vector2(-3, -3))
        self.assertEqual(Vector2Int(-9, -9) / Vector2Int(3, 6), Vector2(-3.0, -1.5))

        self.assertEqual(Vector2Int(10, 10) // 3, Vector2Int(3, 3))
        self.assertEqual(Vector2Int(10, 10) // Vector2Int(3, 6), Vector2Int(3, 1))
        self.assertEqual(Vector2Int(-10, -10) // 3, Vector2Int(-4, -4))
        self.assertEqual(Vector2Int(-10, -10) // Vector2Int(3, 6), Vector2Int(-4, -2))

        self.assertEqual(Vector2Int(10, 10) % 3, Vector2Int(1, 1))
        self.assertEqual(Vector2Int(10, 10) % Vector2Int(3, 5), Vector2Int(1, 0))
        self.assertEqual(Vector2Int(-10, -10) % 3, Vector2Int(2, 2))
        self.assertEqual(Vector2Int(-10, -10) % Vector2Int(3, 5), Vector2Int(2, 0))

        self.assertEqual(divmod(Vector2Int(10, 10), 3), (Vector2Int(3, 3), Vector2Int(1, 1)))
        self.assertEqual(divmod(Vector2Int(10, 10), Vector2Int(3, 5)), (Vector2Int(3, 2), Vector2Int(1, 0)))
        self.assertEqual(divmod(Vector2Int(-10, -10), 3), (Vector2Int(-4, -4), Vector2Int(2, 2)))
        self.assertEqual(divmod(Vector2Int(-10, -10), Vector2Int(3, 5)), (Vector2Int(-4, -2), Vector2Int(2, 0)))

        self.assertEqual(divmod(Vector2Int(5, 3), Vector2Int.one), (Vector2Int(5, 3), Vector2Int.zero))
        self.assertEqual(divmod(Vector2Int(-5, -3), Vector2Int.one), (Vector2Int(-5, -3), Vector2Int.zero))

        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2Int(10, 10), Vector2Int.zero))
        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2Int(10, 10), 0))
        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2Int(10, 10), Vector2Int(5, 0)))
        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2Int(10, 10), Vector2Int(0, 5)))

    def test_rest_operators(self):
        self.assertEqual(-Vector2Int.one, Vector2Int(-1, -1))
        self.assertEqual(-Vector2Int.zero, Vector2Int.zero)
        self.assertEqual(-Vector2Int(-3, -3), Vector2Int(3, 3))

        self.assertEqual(abs(Vector2Int(-2, -2)), Vector2Int(2, 2))
        self.assertEqual(abs(Vector2Int(2, -2)), Vector2Int(2, 2))
        self.assertEqual(abs(Vector2Int(-2, 2)), Vector2Int(2, 2))
        self.assertEqual(abs(Vector2Int(2, 2)), Vector2Int(2, 2))

    def test_properties(self):
        self.assertEqual(Vector2Int(3, 6).magnitude, 6.70820393249936908923)
        self.assertEqual(Vector2Int(7, 12).magnitude, 13.89244398944980450843)

    def test_iter(self):
        i1 = iter(Vector2Int(69, 420))
        self.assertEqual(next(i1), 69)
        self.assertEqual(next(i1), 420)
        self.assertRaises(StopIteration, lambda: next(i1))
        self.assertRaises(StopIteration, lambda: next(iter(i1)))

        i2 = iter(Vector2Int(0, 69420))
        self.assertEqual(next(i2), 0)
        self.assertEqual(next(iter(i2)), 69420)  # re-iterating an iterator should keep original iteration index.
        self.assertRaises(StopIteration, lambda: next(iter(i2)))
        self.assertRaises(StopIteration, lambda: next(i2))

        i3 = iter(iter(iter(iter(iter(Vector2Int(69, 420)))))) # re-iterating an iterator multiple times
        self.assertEqual(next(i3), 69.0)
        self.assertEqual(next(i3), 420.0)
        self.assertRaises(StopIteration, lambda: next(i3)) # Check raising for multiple nexts
        self.assertRaises(StopIteration, lambda: next(i3))

        # No need to test value changing mid iteration as Vector2Int is immutable.

    def test_math(self):
        a = Vector2Int(3, 7)
        b = Vector2Int(5, 3)

        self.assertEqual(Vector2Int.distance(a, b), 4.47213595499957939282)
        self.assertEqual(Vector2Int.distance(Vector2Int(3, 0), Vector2Int(0, 2)), 3.60555127546398929312)

    def test_constructors1(self):
        half_even_down = Vector2(0.5, 0.5)
        half_even_up = Vector2(1.5, 1.5)
        half_even_updown = Vector2(69.5, 420.5)
        half_even_downup = Vector2(-69.5, -420.5)

        above_half_positive = Vector2(1.75, 1.75)
        above_half_negative = Vector2(-1.75, -1.75)

        below_half_positive = Vector2(1.25, 1.25)
        below_half_negative = Vector2(-1.25, -1.25)

        exact1 = Vector2(0.0, 0.0)
        exact2 = Vector2(69.0, 420.0)
        exact3 = Vector2(4.0, 69420.0)

        self.assertEqual(Vector2Int.ceil(half_even_down), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.ceil(half_even_up), Vector2Int(2, 2))
        self.assertEqual(Vector2Int.ceil(half_even_updown), Vector2Int(70, 421))
        self.assertEqual(Vector2Int.ceil(half_even_downup), Vector2Int(-69, -420))
        self.assertEqual(Vector2Int.ceil(above_half_positive), Vector2Int(2, 2))
        self.assertEqual(Vector2Int.ceil(above_half_negative), Vector2Int(-1, -1))
        self.assertEqual(Vector2Int.ceil(below_half_positive), Vector2Int(2, 2))
        self.assertEqual(Vector2Int.ceil(below_half_negative), Vector2Int(-1, -1))
        self.assertEqual(Vector2Int.ceil(exact1), Vector2Int(0, 0))
        self.assertEqual(Vector2Int.ceil(exact2), Vector2Int(69, 420))
        self.assertEqual(Vector2Int.ceil(exact3), Vector2Int(4, 69420))

        self.assertEqual(Vector2Int.floor(half_even_down), Vector2Int(0, 0))
        self.assertEqual(Vector2Int.floor(half_even_up), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.floor(half_even_updown), Vector2Int(69, 420))
        self.assertEqual(Vector2Int.floor(half_even_downup), Vector2Int(-70, -421))
        self.assertEqual(Vector2Int.floor(above_half_positive), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.floor(above_half_negative), Vector2Int(-2, -2))
        self.assertEqual(Vector2Int.floor(below_half_positive), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.floor(below_half_negative), Vector2Int(-2, -2))
        self.assertEqual(Vector2Int.floor(exact1), Vector2Int(0, 0))
        self.assertEqual(Vector2Int.floor(exact2), Vector2Int(69, 420))
        self.assertEqual(Vector2Int.floor(exact3), Vector2Int(4, 69420))

        self.assertEqual(Vector2Int.round(half_even_down), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.round(half_even_up), Vector2Int(2, 2))
        self.assertEqual(Vector2Int.round(half_even_updown), Vector2Int(70, 421))
        self.assertEqual(Vector2Int.round(half_even_downup), Vector2Int(-70, -421))
        self.assertEqual(Vector2Int.round(above_half_positive), Vector2Int(2, 2))
        self.assertEqual(Vector2Int.round(above_half_negative), Vector2Int(-2, -2))
        self.assertEqual(Vector2Int.round(below_half_positive), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.round(below_half_negative), Vector2Int(-1, -1))
        self.assertEqual(Vector2Int.round(exact1), Vector2Int(0, 0))
        self.assertEqual(Vector2Int.round(exact2), Vector2Int(69, 420))
        self.assertEqual(Vector2Int.round(exact3), Vector2Int(4, 69420))

        self.assertEqual(Vector2Int.trunc(half_even_down), Vector2Int(0, 0))
        self.assertEqual(Vector2Int.trunc(half_even_up), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.trunc(half_even_updown), Vector2Int(69, 420))
        self.assertEqual(Vector2Int.trunc(half_even_downup), Vector2Int(-69, -420))
        self.assertEqual(Vector2Int.trunc(above_half_positive), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.trunc(above_half_negative), Vector2Int(-1, -1))
        self.assertEqual(Vector2Int.trunc(below_half_positive), Vector2Int(1, 1))
        self.assertEqual(Vector2Int.trunc(below_half_negative), Vector2Int(-1, -1))
        self.assertEqual(Vector2Int.trunc(exact1), Vector2Int(0, 0))
        self.assertEqual(Vector2Int.trunc(exact2), Vector2Int(69, 420))
        self.assertEqual(Vector2Int.trunc(exact3), Vector2Int(4, 69420))

    def test_constructors2(self):
        a = Vector2Int(2, 5)
        b1 = Vector2Int(3, 4)
        b2 = Vector2Int(1, 7)
        b3 = Vector2Int(0, 0)
        b4 = Vector2Int(10, 10)

        self.assertEqual(Vector2Int.min(a, b1), Vector2Int(2, 4))
        self.assertEqual(Vector2Int.min(a, b2), Vector2Int(1, 5))
        self.assertEqual(Vector2Int.min(a, b3), Vector2Int(0, 0))
        self.assertEqual(Vector2Int.min(a, b4), Vector2Int(2, 5))

        self.assertEqual(Vector2Int.max(a, b1), Vector2Int(3, 5))
        self.assertEqual(Vector2Int.max(a, b2), Vector2Int(2, 7))
        self.assertEqual(Vector2Int.max(a, b3), Vector2Int(2, 5))
        self.assertEqual(Vector2Int.max(a, b4), Vector2Int(10, 10))

    def test_converters(self):
        self.assertEqual(Vector2Int(3, 5).to_vector2(), Vector2(3.0, 5.0))
        self.assertEqual(Vector2Int(69, -420).to_vector2(), Vector2(69.0, -420.0))
        self.assertEqual(Vector2Int(-24, -42).to_vector2(), Vector2(-24.0, -42.0))

if __name__ == '__main__':
    unittest.main()
