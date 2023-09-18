from setuptools import setup, Extension, find_packages

setup(
    packages=find_packages(where=".", include=["nalpy*"]),
    ext_modules=[
        Extension("nalpy.math._c_extensions.functions", ["nalpy/math/_c_extensions/functions.c"]),
        Extension("nalpy.math._c_extensions.vector2", ["nalpy/math/_c_extensions/vector2.c"]),
        Extension("nalpy.math._c_extensions.vector2_int", ["nalpy/math/_c_extensions/vector2_int.c"]),
        Extension("nalpy.math._c_extensions.mvector2", ["nalpy/math/_c_extensions/mvector2.c"]),
        Extension("nalpy.math._c_extensions.mvector2_int", ["nalpy/math/_c_extensions/mvector2_int.c"])
    ],
    package_data={"nalpy": ["py.typed"], "nalpy.math._c_extensions": ["*.pyi"]},
    zip_safe=False
)
