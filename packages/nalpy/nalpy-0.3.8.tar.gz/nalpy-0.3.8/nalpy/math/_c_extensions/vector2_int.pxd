#cython: language_level=3

ctypedef long long int _V2I_int_t

cdef class Vector2Int:
    cdef readonly _V2I_int_t x
    cdef readonly _V2I_int_t y
