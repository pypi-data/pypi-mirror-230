import unittest

from nalpy import math


class BasicMathFunctions(unittest.TestCase):
    def test_cbrt(self):
        self.assertAlmostEqual(math.cbrt(64), 4)
        self.assertAlmostEqual(math.cbrt(27), 3)
        self.assertAlmostEqual(math.cbrt(8), 2)
        self.assertAlmostEqual(math.cbrt(-8), -2)
        self.assertAlmostEqual(math.cbrt(0), 0)
        self.assertAlmostEqual(math.cbrt(1), 1)
        self.assertAlmostEqual(math.cbrt(-1), -1)

        self.assertAlmostEqual(math.cbrt(9), 2.08008382305190411453)
        self.assertAlmostEqual(math.cbrt(0.5), 0.79370052598409973738)
        self.assertAlmostEqual(math.cbrt(69), 4.10156592970234752185)
        self.assertAlmostEqual(math.cbrt(420), 7.48887238721850719787)

    def test_sign(self):
        self.assertEqual(math.sign(0), 0)
        self.assertEqual(math.sign(0.0), 0)
        self.assertEqual(math.sign(1), 1)
        self.assertEqual(math.sign(1.0), 1)
        self.assertEqual(math.sign(-1), -1)
        self.assertEqual(math.sign(-1.0), -1)

        self.assertEqual(math.sign(69), 1)
        self.assertEqual(math.sign(69.420), 1)
        self.assertEqual(math.sign(420.69), 1)

        self.assertEqual(math.sign(-69), -1)
        self.assertEqual(math.sign(-69.420), -1)
        self.assertEqual(math.sign(-420.69), -1)

    def test_is_positive_inf(self):
        self.assertEqual(math.is_positive_inf(float("inf")), True)
        self.assertEqual(math.is_positive_inf(float("-inf")), False)
        self.assertEqual(math.is_positive_inf(float("nan")), False)
        self.assertEqual(math.is_positive_inf(69), False)
        self.assertEqual(math.is_positive_inf(420), False)
        self.assertEqual(math.is_positive_inf(-420), False)
        self.assertEqual(math.is_positive_inf(-69), False)

    def test_is_negative_inf(self):
        self.assertEqual(math.is_negative_inf(float("inf")), False)
        self.assertEqual(math.is_negative_inf(float("-inf")), True)
        self.assertEqual(math.is_negative_inf(float("nan")), False)
        self.assertEqual(math.is_negative_inf(69), False)
        self.assertEqual(math.is_negative_inf(420), False)
        self.assertEqual(math.is_negative_inf(-420), False)
        self.assertEqual(math.is_negative_inf(-69), False)

    def test_delta_angle(self):
        self.assertAlmostEqual(math.delta_angle(69420, 42069), 9)
        self.assertAlmostEqual(math.delta_angle(42069, 69420), -9)
        self.assertAlmostEqual(math.delta_angle(-69420, -42069), -9)
        self.assertAlmostEqual(math.delta_angle(-42069, -69420), 9)
        self.assertAlmostEqual(math.delta_angle(-69420, 42069), -111)
        self.assertAlmostEqual(math.delta_angle(-42069, 69420), -111)

        self.assertAlmostEqual(math.delta_angle(360, 180), 180)
        self.assertAlmostEqual(math.delta_angle(180, 360), 180)

        self.assertAlmostEqual(math.delta_angle(53, 225), 172)
        self.assertAlmostEqual(math.delta_angle(225, 53), -172)

        self.assertAlmostEqual(math.delta_angle(33, 99), 66)
        self.assertAlmostEqual(math.delta_angle(444, 99), 15)

        self.assertAlmostEqual(math.delta_angle(0, 0), 0)
        self.assertAlmostEqual(math.delta_angle(1324, 1324), 0)
        self.assertAlmostEqual(math.delta_angle(-1324, -1324), 0)

        self.assertNotAlmostEqual(math.delta_angle(69, 69), 420)
        self.assertNotAlmostEqual(math.delta_angle(333, 122), 333)
        self.assertNotAlmostEqual(math.delta_angle(122, 122), 122)


class ValueManipulation(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(math.clamp(0, 0, 1), 0)
        self.assertEqual(math.clamp(-1, 0, 1), 0)
        self.assertEqual(math.clamp(-69, 0, 1), 0)
        self.assertEqual(math.clamp(1, 0, 1), 1)
        self.assertEqual(math.clamp(69, 0, 1), 1)

        self.assertEqual(math.clamp(0.5, 0, 1), 0.5)
        self.assertEqual(math.clamp(-1.22, 0, 1), 0)
        self.assertEqual(math.clamp(3.14159, 0, 1), 1)
        self.assertEqual(math.clamp(0.5555934, 0, 1), 0.5555934)
        self.assertEqual(math.clamp(0.12111, 0, 1), 0.12111)

        self.assertEqual(math.clamp(100000, 42069, 69420), 69420)
        self.assertEqual(math.clamp(100000, 42069, 1000000), 100000)

        self.assertEqual(math.clamp(3, 5, 5), 5)
        self.assertEqual(math.clamp(7, 5, 5), 5)
        self.assertEqual(math.clamp(5, 5, 5), 5)

        self.assertEqual(math.clamp(2, 7, 5), 7)
        self.assertEqual(math.clamp(9, 7, 5), 5)
        self.assertEqual(math.clamp(6, 7, 5), 7)
        self.assertEqual(math.clamp(5, 7, 5), 7)

        self.assertRaises(TypeError, lambda: math.clamp([], {}, "penis")) # type: ignore

    def test_clamp01(self):
        self.assertEqual(math.clamp(0, 0, 1), math.clamp01(0))
        self.assertEqual(math.clamp(-1, 0, 1), math.clamp01(-1))
        self.assertEqual(math.clamp(-69, 0, 1), math.clamp01(-69))
        self.assertEqual(math.clamp(1, 0, 1), math.clamp01(1))
        self.assertEqual(math.clamp(69, 0, 1), math.clamp01(69))
        self.assertEqual(math.clamp(0.5, 0, 1), math.clamp01(0.5))
        self.assertEqual(math.clamp(-1.22, 0, 1), math.clamp01(-1.22))
        self.assertEqual(math.clamp(3.14159, 0, 1), math.clamp01(3.14159))
        self.assertEqual(math.clamp(0.5555934, 0, 1), math.clamp01(0.5555934))
        self.assertEqual(math.clamp(0.12111, 0, 1), math.clamp01(0.12111))

    def test_remap(self):
        self.assertAlmostEqual(math.remap(0.5, 0, 1, 1, 0), 0.5)
        self.assertAlmostEqual(math.remap(0.75, 0, 1, 1, 0), 0.25)

        self.assertAlmostEqual(math.remap(0.5, 0, 1, 0, 2), 1)
        self.assertAlmostEqual(math.remap(0.5, 0, 1, 0, 4), 2)

        self.assertAlmostEqual(math.remap(4, 0, 2, 0, 1), 2)
        self.assertAlmostEqual(math.remap(4, 0, 4, 0, 1), 1)
        self.assertAlmostEqual(math.remap(-4, 0, 4, 0, 1), -1)
        self.assertAlmostEqual(math.remap(-16, 0, 4, 0, 1), -4)
        self.assertAlmostEqual(math.remap(0.25, 0, 4, 0, 1), 0.0625)

    def test_remap01(self):
        self.assertAlmostEqual(math.remap(4, 0, 2, 0, 1), math.remap01(4, 0, 2))
        self.assertAlmostEqual(math.remap(4, 0, 4, 0, 1), math.remap01(4, 0, 4))
        self.assertAlmostEqual(math.remap(-4, 0, 4, 0, 1), math.remap01(-4, 0, 4))
        self.assertAlmostEqual(math.remap(-16, 0, 4, 0, 1), math.remap01(-16, 0, 4))
        self.assertAlmostEqual(math.remap(0.25, 0, 4, 0, 1), math.remap01(0.25, 0, 4))


class Rounding(unittest.TestCase):
    def test_round(self):
        self.assertAlmostEqual(math.round(0.5), 1)
        self.assertAlmostEqual(math.round(1), 1)
        self.assertAlmostEqual(math.round(5), 5)
        self.assertAlmostEqual(math.round(15), 15)
        self.assertAlmostEqual(math.round(15.1), 15)
        self.assertAlmostEqual(math.round(15.25), 15)
        self.assertAlmostEqual(math.round(15.5), 16)
        self.assertAlmostEqual(math.round(15.51), 16)
        self.assertAlmostEqual(math.round(15.75), 16)
        self.assertAlmostEqual(math.round(69.420), 69)

        self.assertAlmostEqual(math.round(-0.5), -1)
        self.assertAlmostEqual(math.round(-1), -1)
        self.assertAlmostEqual(math.round(-5), -5)
        self.assertAlmostEqual(math.round(-15), -15)
        self.assertAlmostEqual(math.round(-15.1), -15)
        self.assertAlmostEqual(math.round(-15.25), -15)
        self.assertAlmostEqual(math.round(-15.5), -16)
        self.assertAlmostEqual(math.round(-15.51), -16)
        self.assertAlmostEqual(math.round(-15.75), -16)
        self.assertAlmostEqual(math.round(-69.420), -69)

    def test_round_to_nearest_n(self):
        self.assertAlmostEqual(math.round_to_nearest_n(0, 3), 0)
        self.assertAlmostEqual(math.round_to_nearest_n(0.5, 3), 0)
        self.assertAlmostEqual(math.round_to_nearest_n(1, 3), 0)
        self.assertAlmostEqual(math.round_to_nearest_n(2, 3), 3)
        self.assertAlmostEqual(math.round_to_nearest_n(5, 3), 6)
        self.assertAlmostEqual(math.round_to_nearest_n(15, 3), 15)
        self.assertAlmostEqual(math.round_to_nearest_n(15.1, 3), 15)
        self.assertAlmostEqual(math.round_to_nearest_n(15.25, 3), 15)
        self.assertAlmostEqual(math.round_to_nearest_n(15.5, 3), 15)
        self.assertAlmostEqual(math.round_to_nearest_n(15.51, 3), 15)
        self.assertAlmostEqual(math.round_to_nearest_n(15.75, 3), 15)
        self.assertAlmostEqual(math.round_to_nearest_n(16.5, 3), 18)
        self.assertAlmostEqual(math.round_to_nearest_n(69.420, 3), 69)

        self.assertAlmostEqual(math.round_to_nearest_n(14.9999, 2), 14)
        self.assertAlmostEqual(math.round_to_nearest_n(15, 2), 16)
        self.assertAlmostEqual(math.round_to_nearest_n(15.25, 2), 16)
        self.assertAlmostEqual(math.round_to_nearest_n(15.5, 2), 16)


        self.assertAlmostEqual(math.round_to_nearest_n(-0, 3), 0)
        self.assertAlmostEqual(math.round_to_nearest_n(-0.5, 3), 0)
        self.assertAlmostEqual(math.round_to_nearest_n(-1, 3), 0)
        self.assertAlmostEqual(math.round_to_nearest_n(-2, 3), -3)
        self.assertAlmostEqual(math.round_to_nearest_n(-5, 3), -6)
        self.assertAlmostEqual(math.round_to_nearest_n(-15, 3), -15)
        self.assertAlmostEqual(math.round_to_nearest_n(-15.1, 3), -15)
        self.assertAlmostEqual(math.round_to_nearest_n(-15.25, 3), -15)
        self.assertAlmostEqual(math.round_to_nearest_n(-15.5, 3), -15)
        self.assertAlmostEqual(math.round_to_nearest_n(-15.51, 3), -15)
        self.assertAlmostEqual(math.round_to_nearest_n(-15.75, 3), -15)
        self.assertAlmostEqual(math.round_to_nearest_n(-16.5, 3), -18)
        self.assertAlmostEqual(math.round_to_nearest_n(-69.420, 3), -69)

        self.assertAlmostEqual(math.round_to_nearest_n(-14.9999, 2), -14)
        self.assertAlmostEqual(math.round_to_nearest_n(-15, 2), -16)
        self.assertAlmostEqual(math.round_to_nearest_n(-15.25, 2), -16)
        self.assertAlmostEqual(math.round_to_nearest_n(-15.5, 2), -16)

    def test_floor_nearest_n(self):
        self.assertAlmostEqual(math.floor_to_nearest_n(0, 3), 0)
        self.assertAlmostEqual(math.floor_to_nearest_n(1, 3), 0)
        self.assertAlmostEqual(math.floor_to_nearest_n(2, 3), 0)
        self.assertAlmostEqual(math.floor_to_nearest_n(3, 3), 3)
        self.assertAlmostEqual(math.floor_to_nearest_n(4, 3), 3)
        self.assertAlmostEqual(math.floor_to_nearest_n(5, 3), 3)
        self.assertAlmostEqual(math.floor_to_nearest_n(6, 3), 6)

        self.assertAlmostEqual(math.floor_to_nearest_n(5.99, 3), 3)
        self.assertAlmostEqual(math.floor_to_nearest_n(6.001, 3), 6)

        self.assertAlmostEqual(math.floor_to_nearest_n(-0, 3), 0)
        self.assertAlmostEqual(math.floor_to_nearest_n(-1, 3), -3)
        self.assertAlmostEqual(math.floor_to_nearest_n(-2, 3), -3)
        self.assertAlmostEqual(math.floor_to_nearest_n(-3, 3), -3)
        self.assertAlmostEqual(math.floor_to_nearest_n(-4, 3), -6)
        self.assertAlmostEqual(math.floor_to_nearest_n(-5, 3), -6)
        self.assertAlmostEqual(math.floor_to_nearest_n(-6, 3), -6)

    def test_ceil_nearest_n(self):
        self.assertAlmostEqual(math.ceil_to_nearest_n(0, 3), 0)
        self.assertAlmostEqual(math.ceil_to_nearest_n(1, 3), 3)
        self.assertAlmostEqual(math.ceil_to_nearest_n(2, 3), 3)
        self.assertAlmostEqual(math.ceil_to_nearest_n(3, 3), 3)
        self.assertAlmostEqual(math.ceil_to_nearest_n(4, 3), 6)
        self.assertAlmostEqual(math.ceil_to_nearest_n(5, 3), 6)
        self.assertAlmostEqual(math.ceil_to_nearest_n(5, 3), 6)
        self.assertAlmostEqual(math.ceil_to_nearest_n(6, 3), 6)

        self.assertAlmostEqual(math.ceil_to_nearest_n(5.99, 3), 6)
        self.assertAlmostEqual(math.ceil_to_nearest_n(6.001, 3), 9)

        self.assertAlmostEqual(math.ceil_to_nearest_n(-0, 3), 0)
        self.assertAlmostEqual(math.ceil_to_nearest_n(-1, 3), 0)
        self.assertAlmostEqual(math.ceil_to_nearest_n(-2, 3), 0)
        self.assertAlmostEqual(math.ceil_to_nearest_n(-3, 3), -3)
        self.assertAlmostEqual(math.ceil_to_nearest_n(-4, 3), -3)
        self.assertAlmostEqual(math.ceil_to_nearest_n(-5, 3), -3)
        self.assertAlmostEqual(math.ceil_to_nearest_n(-6, 3), -6)

        self.assertAlmostEqual(math.ceil_to_nearest_n(-5.99, 3), -3)
        self.assertAlmostEqual(math.ceil_to_nearest_n(-6.001, 3), -6)


class Interpolation(unittest.TestCase):
    def test_lerp(self):
        self.assertAlmostEqual(math.lerp(0, 1, 0.5), 0.5)
        self.assertAlmostEqual(math.lerp(4, 8, 0.5), 6)

        self.assertAlmostEqual(math.lerp(69, 420, 2), 420)
        self.assertAlmostEqual(math.lerp(69, 420, -69), 69)

        self.assertAlmostEqual(math.lerp(0, 4, 0.25), 1)
        self.assertAlmostEqual(math.lerp(2, 8, 0.75), 6.5)

    def test_lerp_unclamped(self):
        self.assertAlmostEqual(math.lerp_unclamped(0, 1, 0.5), 0.5)
        self.assertAlmostEqual(math.lerp_unclamped(4, 8, 0.5), 6)

        self.assertAlmostEqual(math.lerp_unclamped(4, 8, 2), 12)
        self.assertAlmostEqual(math.lerp_unclamped(6, 10, -1), 2)

        self.assertAlmostEqual(math.lerp_unclamped(0, 4, 0.25), 1)
        self.assertAlmostEqual(math.lerp_unclamped(2, 8, 0.75), 6.5)

    def test_lerp_angle(self):
        self.assertAlmostEqual(math.lerp_angle(0, 360, 0.5), 0)
        self.assertAlmostEqual(math.lerp_angle(0, 720, 0.5), 0)

        self.assertAlmostEqual(math.lerp_angle(90, 180, 0.5), 135)
        self.assertAlmostEqual(math.lerp_angle(-45, -90, 0.5), -67.5)

        self.assertAlmostEqual(math.lerp_angle(-69, 420, 2), 60)
        self.assertAlmostEqual(math.lerp_angle(-69, 420, -2), -69)

        self.assertAlmostEqual(math.lerp_angle(180, 360, 0.5), 270)
        self.assertAlmostEqual(math.lerp_angle(360, 720, 0.5), 360)


class Arithmetic(unittest.TestCase):
    def test_kahan_sum(self):
        self.assertEqual(math.kahan_sum(0.1 for _ in range(10)), 1.0) # Iterable
        self.assertEqual(math.kahan_sum([0.1 for _ in range(10)]), 1.0) # List
        self.assertEqual(math.kahan_sum(tuple(0.1 for _ in range(10))), 1.0) # Tuple
        self.assertEqual(math.kahan_sum({0.1 * i: None for i in range(10)}), 4.5) # Dict keys
        self.assertEqual(math.kahan_sum({0.1 * i: None for i in range(10)}.keys()), 4.5) # Dict keys 2
        self.assertEqual(math.kahan_sum({i: 0.1 for i in range(10)}.values()), 1.0) # Dict values

        self.assertEqual(math.kahan_sum(0.1 if i % 2 == 0 else 1 for i in range(10)), 5.5) # int and float mixed
        self.assertEqual(math.kahan_sum(1 for _ in range(10)), 10) # int only

        self.assertRaises(TypeError, lambda: math.kahan_sum(0.1)) # type: ignore
        self.assertRaises(TypeError, lambda: math.kahan_sum({i: 0.1 * i for i in range(10)}.items())) # type: ignore
        self.assertRaises(TypeError, lambda: math.kahan_sum(None)) # type: ignore
        self.assertRaises(TypeError, lambda: math.kahan_sum(object())) # type: ignore
        self.assertRaises(TypeError, lambda: math.kahan_sum(...)) # type: ignore

        self.assertRaises(TypeError, lambda: math.kahan_sum([0.1, 0.2, 0.3, 0.4, None])) # type: ignore
        self.assertRaises(TypeError, lambda: math.kahan_sum([0.1, 0.2, 0.3, 0.4, object(), 0.6, 0.7])) # type: ignore
        self.assertRaises(TypeError, lambda: math.kahan_sum(None for _ in range(10))) # type: ignore

if __name__ == '__main__':
    unittest.main()
