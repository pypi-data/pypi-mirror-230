# -*- coding: utf-8 -*-
# !python
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
# cython: language_level=3
# cython: cpow=True
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True

# -*- coding: utf-8 -*-
"""This Cython module implements the performance-critical features of the
Python module |quadtools|."""

cimport numpy

cdef class QuadBase:

    cdef double apply_method0(self, double x) nogil

    cdef double integrate(
        self,
        double x0,
        double x1,
        numpy.int32_t nmin,
        numpy.int32_t nmax,
        double tol,
    ) nogil
