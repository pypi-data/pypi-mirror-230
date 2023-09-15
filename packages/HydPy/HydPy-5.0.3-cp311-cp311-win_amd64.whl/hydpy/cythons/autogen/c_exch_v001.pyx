#!python
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
# cython: language_level=3
# cython: cpow=True
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True
import numpy
cimport numpy
from libc.math cimport exp, fabs, log, sin, cos, tan, asin, acos, atan, isnan, isinf
from libc.math cimport NAN as nan
from libc.math cimport INFINITY as inf
import cython
from cpython.mem cimport PyMem_Malloc
from cpython.mem cimport PyMem_Realloc
from cpython.mem cimport PyMem_Free
from hydpy.cythons.autogen cimport configutils
from hydpy.cythons.autogen cimport interputils
from hydpy.cythons.autogen import pointerutils
from hydpy.cythons.autogen cimport pointerutils
from hydpy.cythons.autogen cimport quadutils
from hydpy.cythons.autogen cimport rootutils
from hydpy.cythons.autogen cimport smoothutils

@cython.final
cdef class Parameters:
    cdef public ControlParameters control
@cython.final
cdef class ControlParameters:
    cdef public double crestheight
    cdef public double crestwidth
    cdef public double flowcoefficient
    cdef public double flowexponent
    cdef public double allowedexchange
@cython.final
cdef class Sequences:
    cdef public ReceiverSequences receivers
    cdef public FactorSequences factors
    cdef public FluxSequences fluxes
    cdef public LogSequences logs
    cdef public OutletSequences outlets
@cython.final
cdef class ReceiverSequences:
    cdef double **l
    cdef public int len_l
    cdef public numpy.int32_t[:] _l_ready
    cdef public int _l_ndim
    cdef public int _l_length
    cdef public int _l_length_0
    cpdef inline alloc(self, name, numpy.int32_t length):
        if name == "l":
            self._l_length_0 = length
            self._l_ready = numpy.full(length, 0, dtype=numpy.int32)
            self.l = <double**> PyMem_Malloc(length * sizeof(double*))
    cpdef inline dealloc(self, name):
        if name == "l":
            PyMem_Free(self.l)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, int idx):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "l":
            self.l[idx] = pointer.p_value
            self._l_ready[idx] = 1
    cpdef get_value(self, str name):
        cdef int idx
        if name == "l":
            values = numpy.empty(self.len_l)
            for idx in range(self.len_l):
                pointerutils.check0(self._l_length_0)
                if self._l_ready[idx] == 0:
                    pointerutils.check1(self._l_length_0, idx)
                    pointerutils.check2(self._l_ready, idx)
                values[idx] = self.l[idx][0]
            return values
    cpdef set_value(self, str name, value):
        if name == "l":
            for idx in range(self.len_l):
                pointerutils.check0(self._l_length_0)
                if self._l_ready[idx] == 0:
                    pointerutils.check1(self._l_length_0, idx)
                    pointerutils.check2(self._l_ready, idx)
                self.l[idx][0] = value[idx]
@cython.final
cdef class FactorSequences:
    cdef public double[:] waterlevel
    cdef public int _waterlevel_ndim
    cdef public int _waterlevel_length
    cdef public int _waterlevel_length_0
    cdef public bint _waterlevel_ramflag
    cdef public double[:,:] _waterlevel_array
    cdef public bint _waterlevel_diskflag_reading
    cdef public bint _waterlevel_diskflag_writing
    cdef public double[:] _waterlevel_ncarray
    cdef public bint _waterlevel_outputflag
    cdef double *_waterlevel_outputpointer
    cdef public double deltawaterlevel
    cdef public int _deltawaterlevel_ndim
    cdef public int _deltawaterlevel_length
    cdef public bint _deltawaterlevel_ramflag
    cdef public double[:] _deltawaterlevel_array
    cdef public bint _deltawaterlevel_diskflag_reading
    cdef public bint _deltawaterlevel_diskflag_writing
    cdef public double[:] _deltawaterlevel_ncarray
    cdef public bint _deltawaterlevel_outputflag
    cdef double *_deltawaterlevel_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._waterlevel_diskflag_reading:
            k = 0
            for jdx0 in range(self._waterlevel_length_0):
                self.waterlevel[jdx0] = self._waterlevel_ncarray[k]
                k += 1
        elif self._waterlevel_ramflag:
            for jdx0 in range(self._waterlevel_length_0):
                self.waterlevel[jdx0] = self._waterlevel_array[idx, jdx0]
        if self._deltawaterlevel_diskflag_reading:
            self.deltawaterlevel = self._deltawaterlevel_ncarray[0]
        elif self._deltawaterlevel_ramflag:
            self.deltawaterlevel = self._deltawaterlevel_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._waterlevel_diskflag_writing:
            k = 0
            for jdx0 in range(self._waterlevel_length_0):
                self._waterlevel_ncarray[k] = self.waterlevel[jdx0]
                k += 1
        if self._waterlevel_ramflag:
            for jdx0 in range(self._waterlevel_length_0):
                self._waterlevel_array[idx, jdx0] = self.waterlevel[jdx0]
        if self._deltawaterlevel_diskflag_writing:
            self._deltawaterlevel_ncarray[0] = self.deltawaterlevel
        if self._deltawaterlevel_ramflag:
            self._deltawaterlevel_array[idx] = self.deltawaterlevel
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "deltawaterlevel":
            self._deltawaterlevel_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._deltawaterlevel_outputflag:
            self._deltawaterlevel_outputpointer[0] = self.deltawaterlevel
@cython.final
cdef class FluxSequences:
    cdef public double potentialexchange
    cdef public int _potentialexchange_ndim
    cdef public int _potentialexchange_length
    cdef public bint _potentialexchange_ramflag
    cdef public double[:] _potentialexchange_array
    cdef public bint _potentialexchange_diskflag_reading
    cdef public bint _potentialexchange_diskflag_writing
    cdef public double[:] _potentialexchange_ncarray
    cdef public bint _potentialexchange_outputflag
    cdef double *_potentialexchange_outputpointer
    cdef public double actualexchange
    cdef public int _actualexchange_ndim
    cdef public int _actualexchange_length
    cdef public bint _actualexchange_ramflag
    cdef public double[:] _actualexchange_array
    cdef public bint _actualexchange_diskflag_reading
    cdef public bint _actualexchange_diskflag_writing
    cdef public double[:] _actualexchange_ncarray
    cdef public bint _actualexchange_outputflag
    cdef double *_actualexchange_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._potentialexchange_diskflag_reading:
            self.potentialexchange = self._potentialexchange_ncarray[0]
        elif self._potentialexchange_ramflag:
            self.potentialexchange = self._potentialexchange_array[idx]
        if self._actualexchange_diskflag_reading:
            self.actualexchange = self._actualexchange_ncarray[0]
        elif self._actualexchange_ramflag:
            self.actualexchange = self._actualexchange_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._potentialexchange_diskflag_writing:
            self._potentialexchange_ncarray[0] = self.potentialexchange
        if self._potentialexchange_ramflag:
            self._potentialexchange_array[idx] = self.potentialexchange
        if self._actualexchange_diskflag_writing:
            self._actualexchange_ncarray[0] = self.actualexchange
        if self._actualexchange_ramflag:
            self._actualexchange_array[idx] = self.actualexchange
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "potentialexchange":
            self._potentialexchange_outputpointer = value.p_value
        if name == "actualexchange":
            self._actualexchange_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._potentialexchange_outputflag:
            self._potentialexchange_outputpointer[0] = self.potentialexchange
        if self._actualexchange_outputflag:
            self._actualexchange_outputpointer[0] = self.actualexchange
@cython.final
cdef class LogSequences:
    cdef public double[:] loggedwaterlevel
    cdef public int _loggedwaterlevel_ndim
    cdef public int _loggedwaterlevel_length
    cdef public int _loggedwaterlevel_length_0
@cython.final
cdef class OutletSequences:
    cdef double **e
    cdef public int len_e
    cdef public numpy.int32_t[:] _e_ready
    cdef public int _e_ndim
    cdef public int _e_length
    cdef public int _e_length_0
    cpdef inline alloc(self, name, numpy.int32_t length):
        if name == "e":
            self._e_length_0 = length
            self._e_ready = numpy.full(length, 0, dtype=numpy.int32)
            self.e = <double**> PyMem_Malloc(length * sizeof(double*))
    cpdef inline dealloc(self, name):
        if name == "e":
            PyMem_Free(self.e)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, int idx):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "e":
            self.e[idx] = pointer.p_value
            self._e_ready[idx] = 1
    cpdef get_value(self, str name):
        cdef int idx
        if name == "e":
            values = numpy.empty(self.len_e)
            for idx in range(self.len_e):
                pointerutils.check0(self._e_length_0)
                if self._e_ready[idx] == 0:
                    pointerutils.check1(self._e_length_0, idx)
                    pointerutils.check2(self._e_ready, idx)
                values[idx] = self.e[idx][0]
            return values
    cpdef set_value(self, str name, value):
        if name == "e":
            for idx in range(self.len_e):
                pointerutils.check0(self._e_length_0)
                if self._e_ready[idx] == 0:
                    pointerutils.check1(self._e_length_0, idx)
                    pointerutils.check2(self._e_ready, idx)
                self.e[idx][0] = value[idx]


@cython.final
cdef class Model:
    cdef public int idx_sim
    cdef public Parameters parameters
    cdef public Sequences sequences
    cpdef inline void simulate(self, int idx)  nogil:
        self.idx_sim = idx
        self.run()
        self.update_outlets()
        self.update_outputs()
    cpdef inline void save_data(self, int idx) nogil:
        self.sequences.factors.save_data(self.idx_sim)
        self.sequences.fluxes.save_data(self.idx_sim)
    cpdef inline void run(self) nogil:
        self.update_waterlevel_v1()
        self.calc_deltawaterlevel_v1()
        self.calc_potentialexchange_v1()
        self.calc_actualexchange_v1()
    cpdef inline void update_inlets(self) nogil:
        pass
    cpdef inline void update_outlets(self) nogil:
        self.pass_actualexchange_v1()
    cpdef inline void update_receivers(self, int idx) nogil:
        self.idx_sim = idx
        self.pic_loggedwaterlevel_v1()
    cpdef inline void update_senders(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_outputs(self) nogil:
        self.sequences.factors.update_outputs()
        self.sequences.fluxes.update_outputs()

    cpdef inline void pic_loggedwaterlevel_v1(self)  nogil:
        cdef int idx
        for idx in range(2):
            self.sequences.logs.loggedwaterlevel[idx] = self.sequences.receivers.l[idx][0]
    cpdef inline void pic_loggedwaterlevel(self)  nogil:
        cdef int idx
        for idx in range(2):
            self.sequences.logs.loggedwaterlevel[idx] = self.sequences.receivers.l[idx][0]
    cpdef inline void update_waterlevel_v1(self)  nogil:
        cdef int idx
        for idx in range(2):
            self.sequences.factors.waterlevel[idx] = self.sequences.logs.loggedwaterlevel[idx]
    cpdef inline void calc_deltawaterlevel_v1(self)  nogil:
        cdef double d_wl1
        cdef double d_wl0
        d_wl0 = max(self.sequences.factors.waterlevel[0], self.parameters.control.crestheight)
        d_wl1 = max(self.sequences.factors.waterlevel[1], self.parameters.control.crestheight)
        self.sequences.factors.deltawaterlevel = d_wl0 - d_wl1
    cpdef inline void calc_potentialexchange_v1(self)  nogil:
        cdef double d_sig
        cdef double d_dwl
        if self.sequences.factors.deltawaterlevel >= 0.0:
            d_dwl = self.sequences.factors.deltawaterlevel
            d_sig = 1.0
        else:
            d_dwl = -self.sequences.factors.deltawaterlevel
            d_sig = -1.0
        self.sequences.fluxes.potentialexchange = d_sig * (            self.parameters.control.flowcoefficient * self.parameters.control.crestwidth * d_dwl**self.parameters.control.flowexponent        )
    cpdef inline void calc_actualexchange_v1(self)  nogil:
        if self.sequences.fluxes.potentialexchange >= 0.0:
            self.sequences.fluxes.actualexchange = min(self.sequences.fluxes.potentialexchange, self.parameters.control.allowedexchange)
        else:
            self.sequences.fluxes.actualexchange = max(self.sequences.fluxes.potentialexchange, -self.parameters.control.allowedexchange)
    cpdef inline void update_waterlevel(self)  nogil:
        cdef int idx
        for idx in range(2):
            self.sequences.factors.waterlevel[idx] = self.sequences.logs.loggedwaterlevel[idx]
    cpdef inline void calc_deltawaterlevel(self)  nogil:
        cdef double d_wl1
        cdef double d_wl0
        d_wl0 = max(self.sequences.factors.waterlevel[0], self.parameters.control.crestheight)
        d_wl1 = max(self.sequences.factors.waterlevel[1], self.parameters.control.crestheight)
        self.sequences.factors.deltawaterlevel = d_wl0 - d_wl1
    cpdef inline void calc_potentialexchange(self)  nogil:
        cdef double d_sig
        cdef double d_dwl
        if self.sequences.factors.deltawaterlevel >= 0.0:
            d_dwl = self.sequences.factors.deltawaterlevel
            d_sig = 1.0
        else:
            d_dwl = -self.sequences.factors.deltawaterlevel
            d_sig = -1.0
        self.sequences.fluxes.potentialexchange = d_sig * (            self.parameters.control.flowcoefficient * self.parameters.control.crestwidth * d_dwl**self.parameters.control.flowexponent        )
    cpdef inline void calc_actualexchange(self)  nogil:
        if self.sequences.fluxes.potentialexchange >= 0.0:
            self.sequences.fluxes.actualexchange = min(self.sequences.fluxes.potentialexchange, self.parameters.control.allowedexchange)
        else:
            self.sequences.fluxes.actualexchange = max(self.sequences.fluxes.potentialexchange, -self.parameters.control.allowedexchange)
    cpdef inline void pass_actualexchange_v1(self)  nogil:
        self.sequences.outlets.e[0][0] = self.sequences.outlets.e[0][0] - (self.sequences.fluxes.actualexchange)
        self.sequences.outlets.e[1][0] = self.sequences.outlets.e[1][0] + (self.sequences.fluxes.actualexchange)
    cpdef inline void pass_actualexchange(self)  nogil:
        self.sequences.outlets.e[0][0] = self.sequences.outlets.e[0][0] - (self.sequences.fluxes.actualexchange)
        self.sequences.outlets.e[1][0] = self.sequences.outlets.e[1][0] + (self.sequences.fluxes.actualexchange)
