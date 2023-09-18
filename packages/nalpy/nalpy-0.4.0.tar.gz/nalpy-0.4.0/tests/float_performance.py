from timeit import timeit
from nalpy import math

STATEMENT = "x % y"

vectorsetup = "x=math.Vector2(69.420, 420.69); y=math.Vector2(-6.9, 6.9)"
floatsetup = "x=69.420; y=-6.9"
glbls = { "math": math }
n = 25_000_000
vec = timeit(STATEMENT, setup=vectorsetup, number=n, globals=glbls)
print(vec)
flt = timeit(STATEMENT, setup=floatsetup, number=n, globals=glbls)
print(flt)
print(f"Float is {vec / flt:.3f} times faster")
