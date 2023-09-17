#cython: language_level=3

cdef class MVector2:
    cdef public double x
    cdef public double y

    cpdef MVector2 copy(self)
    cpdef normalize(self)
