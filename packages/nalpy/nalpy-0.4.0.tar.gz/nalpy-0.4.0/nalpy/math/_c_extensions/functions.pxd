#cython: language_level=3

cdef inline char doublesign(double x) noexcept: # Extracted into a separate function because cpdef doesn't support position only arguments.
    return (<unsigned char>(x > 0.0)) - (<unsigned char>(x < 0.0))
