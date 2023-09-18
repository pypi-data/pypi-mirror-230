#cython: language_level=3

from libc.math cimport llround, fabs

def round(double x, /):
    return llround(x)

def remap(double value, double from1, double to1, double from2, double to2):
    return (value - from1) / (to1 - from1) * (to2 - from2) + from2

def remap01(double value, double from1, double to1):
    return (value - from1) / (to1 - from1)

def clamp(value, _min, _max): # types not verified due to performance reasons
    if value < _min:
        return _min
    if value > _max:
        return _max
    return value

cpdef clamp01(double value) noexcept:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value

cpdef delta_angle(double current, double target) noexcept:
    cdef double delta = (target - current) % 360.0
    if delta > 180.0:
        delta -= 360.0
    return delta

def sign(double x, /):
    return doublesign(x)


def lerp(double a, double b, double t):
    return a + (b - a) * clamp01(t)

def lerp_unclamped(double a, double b, double t):
    return a + (b - a) * t

def lerp_angle(double a, double b, double t):
    return a + delta_angle(a, b) * clamp01(t)

def inverse_lerp(double a, double b, double value):
    if a != b:
        return clamp01((value - a) / (b - a))
    else:
        return 0.0

def smooth_step(double a, double b, double t):
    t = clamp01(t)
    t = -2.0 * t * t * t + 3.0 * t * t
    return b * t + a * (1 - t)

cpdef move_towards(double current, double target, double max_delta) noexcept:
    if fabs(target - current) <= max_delta:
        return target
    return current + doublesign(target - current) * max_delta

def move_towards_angle(double current, double target, double max_delta):
    deltaAngle = delta_angle(current, target)
    if -max_delta < deltaAngle and deltaAngle < max_delta:
        return target
    target = current + deltaAngle
    return move_towards(current, target, max_delta)

def ping_pong(double t, double length):
    t = t % (length * 2.0)
    return length - fabs(t - length)

def kahan_sum(float_values):
    cdef double acc = 0.0
    cdef double c = 0.0

    cdef double f
    cdef double y
    cdef double t
    for f in float_values:
        y = f - c
        t = acc + y

        c = (t - acc) - y
        acc = t

    return acc
