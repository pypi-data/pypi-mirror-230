import unittest

from nalpy.math import Vector2


class BasicFunctionality(unittest.TestCase):
    def test_index(self):
        v = Vector2(3.5, 7.25)
        self.assertEqual(v[0], 3.5)
        self.assertEqual(v[1], 7.25)
        self.assertRaises(IndexError, lambda: v[3])

        class MockIndexObj:
            def __init__(self, i: int) -> None:
                self.__internal_index = i
            def __index__(self) -> int:
                return self.__internal_index
        self.assertEqual(v[MockIndexObj(0)], 3.5)
        self.assertEqual(v[MockIndexObj(1)], 7.25)

    def test_xy(self):
        v = Vector2(3.5, 7.25)
        self.assertEqual(v.x, 3.5)
        self.assertEqual(v.y, 7.25)
        self.assertRaises(AttributeError, lambda: v.z) # type: ignore

    def test_equals(self):
        v = Vector2(3.0, 3.0)
        self.assertEqual(v, Vector2(3.0, 3.0))
        self.assertNotEqual(v, Vector2(2.0, 3.0))
        self.assertNotEqual(v, Vector2(3.0, 2.0))
        self.assertNotEqual(v, Vector2(2.0, 2.0))

        self.assertRaises(TypeError, lambda: v == (3.0, 3.0))
        self.assertNotEqual(v, None)
        self.assertNotEqual(None, v)

        self.assertEqual(Vector2(3, 3), Vector2(3.0, 3.0))
        self.assertEqual(Vector2(5, 2.5), Vector2(5.0, 2.5))
        self.assertNotEqual(Vector2(5, 2), Vector2(5.0, 2.5))

    def test_hash(self):
        test_values: tuple[tuple[float, float], ...] = (
            (69, 420),
            (420, 69),
            (69, 69),
            (420, 420),

            (69.420, 420.420),
            (420.420, 69.420),
            (69.69, 69.69),
            (420.420, 420.420),

            (0, 0),
            (0.0, 0.0),
            (-1, -1),
            (-69.420, -69.420),
            (1000, 1000),
            (1000.0, 1000.0),
            (-10000, -10000),
            (-10000.0, -10000.0),

            (float("inf"), float("inf")),
            (float("-inf"), float("-inf")),
            (float("inf"), float("-inf"))
        )

        # Vector2 hash should match tuple hash
        for v in test_values:
            self.assertEqual(hash(v), hash(Vector2(*v)), f"hash({v}) != hash({Vector2(*v)})")

        # Vector2 hash behaviour on nan values
        self.assertNotEqual(hash(Vector2(float("nan"), float("nan"))), hash(Vector2(float("nan"), float("nan"))))
        self.assertNotEqual(hash(Vector2(float("nan"), float("inf"))), hash(Vector2(float("nan"), float("inf"))))
        self.assertNotEqual(hash(Vector2(float("nan"), float("-inf"))), hash(Vector2(float("nan"), float("-inf"))))
        self.assertEqual(hash(Vector2(69.420, float("nan"))), hash(Vector2(69.420, float("nan"))))
        self.assertEqual(hash(Vector2(float("nan"), 69.420)), hash(Vector2(float("nan"), 69.420)))

    def test_constants(self):
        self.assertEqual(Vector2.zero,  Vector2(0.0, 0.0))
        self.assertEqual(Vector2.one,   Vector2(1.0, 1.0))
        self.assertEqual(Vector2.up,    Vector2(0.0, 1.0))
        self.assertEqual(Vector2.down,  Vector2(0.0, -1.0))
        self.assertEqual(Vector2.left,  Vector2(-1.0, 0.0))
        self.assertEqual(Vector2.right, Vector2(1.0, 0.0))

    def test_repr(self):
        self.assertEqual(repr(Vector2(2.0, 2.0)), f"Vector2(2.0, 2.0)")
        self.assertEqual(repr(Vector2(2.4, 3.075)), f"Vector2(2.4, 3.075)")

        self.assertEqual(repr(Vector2(2.0, 2.0)), str(Vector2(2.0, 2.0)))
        self.assertEqual(repr(Vector2(2.4, 3.075)), str(Vector2(2.4, 3.075)))

    def test_addsub(self):
        b: Vector2 = Vector2.one
        self.assertEqual(b + Vector2(2.5, 2.5), Vector2(3.5, 3.5))
        self.assertEqual(b + Vector2(0.0, 1.75), Vector2(1.0, 2.75))

        self.assertEqual(b - Vector2(2.5, 2.5), Vector2(-1.5, -1.5))
        self.assertEqual(b - Vector2(0.0, 1.75), Vector2(1.0, -0.75))

    def test_mult(self):
        b: Vector2 = Vector2.one
        self.assertEqual(b * 2, Vector2(2.0, 2.0))
        self.assertEqual(2 * b, Vector2(2.0, 2.0))
        self.assertEqual(b * 2.0, Vector2(2.0, 2.0))
        self.assertEqual(2.0 * b, Vector2(2.0, 2.0))

        self.assertEqual(Vector2(3, 4) * b, Vector2(3.0, 4.0))
        self.assertEqual(b * Vector2(3, 4), Vector2(3.0, 4.0))
        self.assertEqual(Vector2(3.0, 4.0) * b, Vector2(3.0, 4.0))
        self.assertEqual(b * Vector2(3.0, 4.0), Vector2(3.0, 4.0))

    def test_divmod(self):
        self.assertEqual(Vector2(9, 9.0) / 3, Vector2(3.0, 3))
        self.assertEqual(Vector2(9, 9.0) / 3.0, Vector2(3.0, 3))
        self.assertEqual(Vector2(9, 9.0) / Vector2(3, 6), Vector2(3.0, 1.5))
        self.assertEqual(Vector2(-9, -9.0) / 3, Vector2(-3.0, -3))
        self.assertEqual(Vector2(-9, -9.0) / 3.0, Vector2(-3.0, -3))
        self.assertEqual(Vector2(-9, -9.0) / Vector2(3, 6), Vector2(-3.0, -1.5))

        self.assertEqual(Vector2(10, 10.0) // 3, Vector2(3.0, 3))
        self.assertEqual(Vector2(10, 10.0) // 3.0, Vector2(3.0, 3))
        self.assertEqual(Vector2(10, 10.0) // Vector2(3, 6), Vector2(3.0, 1))
        self.assertEqual(Vector2(-10, -10.0) // 3, Vector2(-4.0, -4))
        self.assertEqual(Vector2(-10, -10.0) // 3.0, Vector2(-4.0, -4))
        self.assertEqual(Vector2(-10, -10.0) // Vector2(3, 6), Vector2(-4.0, -2))

        self.assertEqual(Vector2(10, 10.0) % 3, Vector2(1.0, 1))
        self.assertEqual(Vector2(10, 10.0) % Vector2(3, 5), Vector2(1.0, 0))
        self.assertEqual(Vector2(-10, -10.0) % 3, Vector2(2.0, 2))
        self.assertEqual(Vector2(-10, -10.0) % Vector2(3, 5), Vector2(2.0, 0.0))

        self.assertEqual(divmod(Vector2(10, 10.0), 3), (Vector2(3.0, 3), Vector2(1.0, 1)))
        self.assertEqual(divmod(Vector2(10, 10.0), Vector2(3, 5)), (Vector2(3.0, 2.0), Vector2(1.0, 0.0)))
        self.assertEqual(divmod(Vector2(-10, -10.0), 3), (Vector2(-4.0, -4), Vector2(2.0, 2)))
        self.assertEqual(divmod(Vector2(-10, -10.0), Vector2(3, 5)), (Vector2(-4.0, -2.0), Vector2(2.0, 0.0)))

        div1, mod1 = divmod(Vector2(5.5, 3.3), Vector2.one)
        self.assertAlmostEqual(div1.x, 5.0)
        self.assertAlmostEqual(div1.y, 3.0)
        self.assertAlmostEqual(mod1.x, 0.5)
        self.assertAlmostEqual(mod1.y, 0.3)

        div2, mod2 = divmod(Vector2(-5.5, -3.3), Vector2.one)
        self.assertAlmostEqual(div2.x, -6.0)
        self.assertAlmostEqual(div2.y, -4.0)
        self.assertAlmostEqual(mod2.x, 0.5)
        self.assertAlmostEqual(mod2.y, 0.7)

        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2(10.0, 10.0), Vector2.zero))
        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2(10.0, 10.0), 0.0))
        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2(10.0, 10.0), 0))
        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2(10.0, 10.0), Vector2(5.0, 0.0)))
        self.assertRaises(ZeroDivisionError, lambda: divmod(Vector2(10.0, 10.0), Vector2(0.0, 5.0)))

    def test_rest_operators(self):
        self.assertEqual(-Vector2.one, Vector2(-1, -1))
        self.assertEqual(-Vector2.zero, Vector2.zero)
        self.assertEqual(-Vector2(-3, -3.0), Vector2(3.0, 3))

        self.assertEqual(abs(Vector2(-2, -2)), Vector2(2, 2))
        self.assertEqual(abs(Vector2(2, -2)), Vector2(2, 2))
        self.assertEqual(abs(Vector2(-2, 2)), Vector2(2, 2))
        self.assertEqual(abs(Vector2(2, 2)), Vector2(2, 2))

        self.assertEqual(abs(Vector2(-2.258, -2.258)), Vector2(2.258, 2.258))
        self.assertEqual(abs(Vector2(2.258, -2.258)), Vector2(2.258, 2.258))
        self.assertEqual(abs(Vector2(-2.258, 2.258)), Vector2(2.258, 2.258))
        self.assertEqual(abs(Vector2(2.258, 2.258)), Vector2(2.258, 2.258))

    def test_properties(self):
        self.assertEqual(Vector2(3, 6).magnitude, 6.70820393249936908923)
        self.assertEqual(Vector2(7, 12).magnitude, 13.89244398944980450843)
        self.assertEqual(Vector2(0.15, 0.75).magnitude, 0.7648529270389177245)

        unnormalized = Vector2(4.5, 3.42)
        self.assertEqual(unnormalized.magnitude, 5.65211464851872940138)
        normalized = unnormalized.normalized
        self.assertEqual(normalized.magnitude, 1.0)
        self.assertEqual(normalized.x, 0.79616219412310251879)
        self.assertEqual(normalized.y, 0.60508326753355791428)

    def test_iter(self):
        i1 = iter(Vector2(69.420, 420.69))
        self.assertEqual(next(i1), 69.420)
        self.assertEqual(next(i1), 420.69)
        self.assertRaises(StopIteration, lambda: next(i1))
        self.assertRaises(StopIteration, lambda: next(iter(i1)))

        i2 = iter(Vector2(0.0, float("inf")))
        self.assertEqual(next(i2), 0.0)
        self.assertEqual(next(iter(i2)), float("inf")) # re-iterating an iterator should keep original iteration index.
        self.assertRaises(StopIteration, lambda: next(iter(i2)))
        self.assertRaises(StopIteration, lambda: next(i2))

        i3 = iter(iter(iter(iter(iter(Vector2(69.0, 420.0)))))) # re-iterating an iterator multiple times
        self.assertEqual(next(i3), 69.0)
        self.assertEqual(next(i3), 420.0)
        self.assertRaises(StopIteration, lambda: next(i3)) # Check raising for multiple nexts
        self.assertRaises(StopIteration, lambda: next(i3))

        # No need to test value changing mid iteration as Vector2Int is immutable.

    def test_math(self):
        a = Vector2(3.4, 7.6)
        a_perpendic = Vector2.perpendicular(a)

        b = Vector2(5.77, 3.22)

        self.assertEqual(Vector2.dot(a, b), 44.09)

        self.assertEqual(a_perpendic.x, -a.y)
        self.assertEqual(a_perpendic.y, a.x)
        self.assertEqual(Vector2.dot(a, a_perpendic), 0)

        self.assertAlmostEqual(Vector2.distance(a, b), 4.9800903606259997258)
        self.assertEqual(Vector2.distance(Vector2(3.0, 0.0), Vector2(0.0, 2.0)), 3.60555127546398929312)

    def test_angle(self):
        a = Vector2.right
        b1 = Vector2.up
        b2 = Vector2.down
        b3 = Vector2(1.0, -1.0)

        self.assertEqual(Vector2.angle(a, b1), 90)
        self.assertEqual(Vector2.angle(a, b2), 90)
        self.assertEqual(Vector2.signed_angle(a, b1), 90)
        self.assertEqual(Vector2.signed_angle(a, b2), -90)

        self.assertAlmostEqual(Vector2.angle(a, b3), 45)
        self.assertAlmostEqual(Vector2.signed_angle(a, b3), -45)

    def test_converters_and_constructors(self):
        a = Vector2(2.0, 5.0)
        b1 = Vector2(3.0, 4.0)
        b2 = Vector2(1.0, 7.0)
        b3 = Vector2(0.0, 0.0)
        b4 = Vector2(10, 10)

        self.assertEqual(Vector2.min(a, b1), Vector2(2.0, 4.0))
        self.assertEqual(Vector2.min(a, b2), Vector2(1.0, 5.0))
        self.assertEqual(Vector2.min(a, b3), Vector2(0.0, 0.0))
        self.assertEqual(Vector2.min(a, b4), Vector2(2.0, 5.0))

        self.assertEqual(Vector2.max(a, b1), Vector2(3.0, 5.0))
        self.assertEqual(Vector2.max(a, b2), Vector2(2.0, 7.0))
        self.assertEqual(Vector2.max(a, b3), Vector2(2.0, 5.0))
        self.assertEqual(Vector2.max(a, b4), Vector2(10.0, 10.0))

    def test_interpolation(self):
        a = Vector2(2, 4)
        b = Vector2(14.5, 7.85)

        lerp75 = Vector2.lerp(a, b, 0.75)
        lerpuncl75 = Vector2.lerp_unclamped(a, b, 0.75)
        res75 = Vector2(11.375, 6.8875)

        self.assertEqual(Vector2.lerp(a, b, 0.5), Vector2(8.25, 5.925))
        self.assertEqual(Vector2.lerp(a, b, 0.25), Vector2(5.125, 4.9625))
        self.assertAlmostEqual(lerp75.x, res75.x)
        self.assertAlmostEqual(lerp75.y, res75.y)
        self.assertEqual(Vector2.lerp(a, b, 0.0), a)
        self.assertEqual(Vector2.lerp(a, b, -10.0), a)
        self.assertEqual(Vector2.lerp(a, b, 1.0), b)
        self.assertEqual(Vector2.lerp(a, b, 10.0), b)

        self.assertEqual(Vector2.lerp_unclamped(a, b, 0.5), Vector2(8.25, 5.925))
        self.assertEqual(Vector2.lerp_unclamped(a, b, 0.25), Vector2(5.125, 4.9625))
        self.assertAlmostEqual(lerpuncl75.x, res75.x)
        self.assertAlmostEqual(lerpuncl75.y, res75.y)
        self.assertEqual(Vector2.lerp_unclamped(a, b, 0.0), a)
        self.assertEqual(Vector2.lerp_unclamped(a, b, -10.0), Vector2(-123, -34.5))
        self.assertEqual(Vector2.lerp_unclamped(a, b, 1.0), b)
        self.assertEqual(Vector2.lerp_unclamped(a, b, 10.0), Vector2(127, 42.5))

        # move_towards checks are generated.
        self.assertEqual(Vector2.move_towards(Vector2(29.431186908718228, 33.6621820548442), Vector2(23.120215968907857, 59.38576299316706), 66.61514209773944), Vector2(23.120215968907857, 59.38576299316706))
        self.assertEqual(Vector2.move_towards(Vector2(33.79504419784424, 15.245959830973579), Vector2(29.8970235981436, 56.87761092723505), 45.60931683390097), Vector2(29.8970235981436, 56.87761092723505))
        self.assertEqual(Vector2.move_towards(Vector2(36.967494011692054, 48.05636806402712), Vector2(64.7026491150305, 10.799301027132651), 22.62248852523597), Vector2(50.476173519781156, 29.90994789303563))
        self.assertEqual(Vector2.move_towards(Vector2(36.967494011692054, 48.05636806402712), Vector2(64.7026491150305, 10.799301027132651), 22.62248852523597), Vector2(50.476173519781156, 29.90994789303563))
        self.assertEqual(Vector2.move_towards(Vector2(17.304290257053363, 70.00883344211574), Vector2(25.30328000212717, 62.156384285746164), 73.68637824328094), Vector2(25.30328000212717, 62.156384285746164))
        self.assertEqual(Vector2.move_towards(Vector2(7.345439149536899, 27.733716913826783), Vector2(43.81449326240699, 53.65251153801417), 0.53), Vector2(7.7774480048922054, 28.04074842506724))

        # Max delta over the moveable distance
        self.assertEqual(Vector2.move_towards(Vector2(8.657950152375955, 4.180694783383892), Vector2(60.89320793752563, 64.02011771066626), 84948.51669138268), Vector2(60.89320793752563, 64.02011771066626))

if __name__ == '__main__':
    unittest.main()
