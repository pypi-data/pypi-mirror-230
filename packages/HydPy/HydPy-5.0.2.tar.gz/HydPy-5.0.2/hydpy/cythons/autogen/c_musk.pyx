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
    cdef public DerivedParameters derived
    cdef public SolverParameters solver
@cython.final
cdef class ControlParameters:
    cdef public double catchmentarea
    cdef public numpy.int32_t nmbsegments
    cdef public double[:] coefficients
    cdef public double[:] length
    cdef public double[:] bottomslope
    cdef public double[:] bottomwidth
    cdef public double[:] sideslope
    cdef public double[:] stricklercoefficient
@cython.final
cdef class DerivedParameters:
    cdef public double seconds
    cdef public double[:] perimeterincrease
@cython.final
cdef class SolverParameters:
    cdef public numpy.int32_t nmbruns
    cdef public double tolerancewaterlevel
    cdef public double tolerancedischarge
@cython.final
cdef class Sequences:
    cdef public InletSequences inlets
    cdef public FactorSequences factors
    cdef public FluxSequences fluxes
    cdef public StateSequences states
    cdef public OutletSequences outlets
    cdef public StateSequences old_states
    cdef public StateSequences new_states
@cython.final
cdef class InletSequences:
    cdef double **q
    cdef public int len_q
    cdef public numpy.int32_t[:] _q_ready
    cdef public int _q_ndim
    cdef public int _q_length
    cdef public int _q_length_0
    cpdef inline alloc(self, name, numpy.int32_t length):
        if name == "q":
            self._q_length_0 = length
            self._q_ready = numpy.full(length, 0, dtype=numpy.int32)
            self.q = <double**> PyMem_Malloc(length * sizeof(double*))
    cpdef inline dealloc(self, name):
        if name == "q":
            PyMem_Free(self.q)
    cpdef inline set_pointer1d(self, str name, pointerutils.Double value, int idx):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "q":
            self.q[idx] = pointer.p_value
            self._q_ready[idx] = 1
    cpdef get_value(self, str name):
        cdef int idx
        if name == "q":
            values = numpy.empty(self.len_q)
            for idx in range(self.len_q):
                pointerutils.check0(self._q_length_0)
                if self._q_ready[idx] == 0:
                    pointerutils.check1(self._q_length_0, idx)
                    pointerutils.check2(self._q_ready, idx)
                values[idx] = self.q[idx][0]
            return values
    cpdef set_value(self, str name, value):
        if name == "q":
            for idx in range(self.len_q):
                pointerutils.check0(self._q_length_0)
                if self._q_ready[idx] == 0:
                    pointerutils.check1(self._q_length_0, idx)
                    pointerutils.check2(self._q_ready, idx)
                self.q[idx][0] = value[idx]
@cython.final
cdef class FactorSequences:
    cdef public double[:] referencewaterlevel
    cdef public int _referencewaterlevel_ndim
    cdef public int _referencewaterlevel_length
    cdef public int _referencewaterlevel_length_0
    cdef public bint _referencewaterlevel_ramflag
    cdef public double[:,:] _referencewaterlevel_array
    cdef public bint _referencewaterlevel_diskflag_reading
    cdef public bint _referencewaterlevel_diskflag_writing
    cdef public double[:] _referencewaterlevel_ncarray
    cdef public bint _referencewaterlevel_outputflag
    cdef double *_referencewaterlevel_outputpointer
    cdef public double[:] wettedarea
    cdef public int _wettedarea_ndim
    cdef public int _wettedarea_length
    cdef public int _wettedarea_length_0
    cdef public bint _wettedarea_ramflag
    cdef public double[:,:] _wettedarea_array
    cdef public bint _wettedarea_diskflag_reading
    cdef public bint _wettedarea_diskflag_writing
    cdef public double[:] _wettedarea_ncarray
    cdef public bint _wettedarea_outputflag
    cdef double *_wettedarea_outputpointer
    cdef public double[:] wettedperimeter
    cdef public int _wettedperimeter_ndim
    cdef public int _wettedperimeter_length
    cdef public int _wettedperimeter_length_0
    cdef public bint _wettedperimeter_ramflag
    cdef public double[:,:] _wettedperimeter_array
    cdef public bint _wettedperimeter_diskflag_reading
    cdef public bint _wettedperimeter_diskflag_writing
    cdef public double[:] _wettedperimeter_ncarray
    cdef public bint _wettedperimeter_outputflag
    cdef double *_wettedperimeter_outputpointer
    cdef public double[:] surfacewidth
    cdef public int _surfacewidth_ndim
    cdef public int _surfacewidth_length
    cdef public int _surfacewidth_length_0
    cdef public bint _surfacewidth_ramflag
    cdef public double[:,:] _surfacewidth_array
    cdef public bint _surfacewidth_diskflag_reading
    cdef public bint _surfacewidth_diskflag_writing
    cdef public double[:] _surfacewidth_ncarray
    cdef public bint _surfacewidth_outputflag
    cdef double *_surfacewidth_outputpointer
    cdef public double[:] celerity
    cdef public int _celerity_ndim
    cdef public int _celerity_length
    cdef public int _celerity_length_0
    cdef public bint _celerity_ramflag
    cdef public double[:,:] _celerity_array
    cdef public bint _celerity_diskflag_reading
    cdef public bint _celerity_diskflag_writing
    cdef public double[:] _celerity_ncarray
    cdef public bint _celerity_outputflag
    cdef double *_celerity_outputpointer
    cdef public double[:] correctingfactor
    cdef public int _correctingfactor_ndim
    cdef public int _correctingfactor_length
    cdef public int _correctingfactor_length_0
    cdef public bint _correctingfactor_ramflag
    cdef public double[:,:] _correctingfactor_array
    cdef public bint _correctingfactor_diskflag_reading
    cdef public bint _correctingfactor_diskflag_writing
    cdef public double[:] _correctingfactor_ncarray
    cdef public bint _correctingfactor_outputflag
    cdef double *_correctingfactor_outputpointer
    cdef public double[:] coefficient1
    cdef public int _coefficient1_ndim
    cdef public int _coefficient1_length
    cdef public int _coefficient1_length_0
    cdef public bint _coefficient1_ramflag
    cdef public double[:,:] _coefficient1_array
    cdef public bint _coefficient1_diskflag_reading
    cdef public bint _coefficient1_diskflag_writing
    cdef public double[:] _coefficient1_ncarray
    cdef public bint _coefficient1_outputflag
    cdef double *_coefficient1_outputpointer
    cdef public double[:] coefficient2
    cdef public int _coefficient2_ndim
    cdef public int _coefficient2_length
    cdef public int _coefficient2_length_0
    cdef public bint _coefficient2_ramflag
    cdef public double[:,:] _coefficient2_array
    cdef public bint _coefficient2_diskflag_reading
    cdef public bint _coefficient2_diskflag_writing
    cdef public double[:] _coefficient2_ncarray
    cdef public bint _coefficient2_outputflag
    cdef double *_coefficient2_outputpointer
    cdef public double[:] coefficient3
    cdef public int _coefficient3_ndim
    cdef public int _coefficient3_length
    cdef public int _coefficient3_length_0
    cdef public bint _coefficient3_ramflag
    cdef public double[:,:] _coefficient3_array
    cdef public bint _coefficient3_diskflag_reading
    cdef public bint _coefficient3_diskflag_writing
    cdef public double[:] _coefficient3_ncarray
    cdef public bint _coefficient3_outputflag
    cdef double *_coefficient3_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._referencewaterlevel_diskflag_reading:
            k = 0
            for jdx0 in range(self._referencewaterlevel_length_0):
                self.referencewaterlevel[jdx0] = self._referencewaterlevel_ncarray[k]
                k += 1
        elif self._referencewaterlevel_ramflag:
            for jdx0 in range(self._referencewaterlevel_length_0):
                self.referencewaterlevel[jdx0] = self._referencewaterlevel_array[idx, jdx0]
        if self._wettedarea_diskflag_reading:
            k = 0
            for jdx0 in range(self._wettedarea_length_0):
                self.wettedarea[jdx0] = self._wettedarea_ncarray[k]
                k += 1
        elif self._wettedarea_ramflag:
            for jdx0 in range(self._wettedarea_length_0):
                self.wettedarea[jdx0] = self._wettedarea_array[idx, jdx0]
        if self._wettedperimeter_diskflag_reading:
            k = 0
            for jdx0 in range(self._wettedperimeter_length_0):
                self.wettedperimeter[jdx0] = self._wettedperimeter_ncarray[k]
                k += 1
        elif self._wettedperimeter_ramflag:
            for jdx0 in range(self._wettedperimeter_length_0):
                self.wettedperimeter[jdx0] = self._wettedperimeter_array[idx, jdx0]
        if self._surfacewidth_diskflag_reading:
            k = 0
            for jdx0 in range(self._surfacewidth_length_0):
                self.surfacewidth[jdx0] = self._surfacewidth_ncarray[k]
                k += 1
        elif self._surfacewidth_ramflag:
            for jdx0 in range(self._surfacewidth_length_0):
                self.surfacewidth[jdx0] = self._surfacewidth_array[idx, jdx0]
        if self._celerity_diskflag_reading:
            k = 0
            for jdx0 in range(self._celerity_length_0):
                self.celerity[jdx0] = self._celerity_ncarray[k]
                k += 1
        elif self._celerity_ramflag:
            for jdx0 in range(self._celerity_length_0):
                self.celerity[jdx0] = self._celerity_array[idx, jdx0]
        if self._correctingfactor_diskflag_reading:
            k = 0
            for jdx0 in range(self._correctingfactor_length_0):
                self.correctingfactor[jdx0] = self._correctingfactor_ncarray[k]
                k += 1
        elif self._correctingfactor_ramflag:
            for jdx0 in range(self._correctingfactor_length_0):
                self.correctingfactor[jdx0] = self._correctingfactor_array[idx, jdx0]
        if self._coefficient1_diskflag_reading:
            k = 0
            for jdx0 in range(self._coefficient1_length_0):
                self.coefficient1[jdx0] = self._coefficient1_ncarray[k]
                k += 1
        elif self._coefficient1_ramflag:
            for jdx0 in range(self._coefficient1_length_0):
                self.coefficient1[jdx0] = self._coefficient1_array[idx, jdx0]
        if self._coefficient2_diskflag_reading:
            k = 0
            for jdx0 in range(self._coefficient2_length_0):
                self.coefficient2[jdx0] = self._coefficient2_ncarray[k]
                k += 1
        elif self._coefficient2_ramflag:
            for jdx0 in range(self._coefficient2_length_0):
                self.coefficient2[jdx0] = self._coefficient2_array[idx, jdx0]
        if self._coefficient3_diskflag_reading:
            k = 0
            for jdx0 in range(self._coefficient3_length_0):
                self.coefficient3[jdx0] = self._coefficient3_ncarray[k]
                k += 1
        elif self._coefficient3_ramflag:
            for jdx0 in range(self._coefficient3_length_0):
                self.coefficient3[jdx0] = self._coefficient3_array[idx, jdx0]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._referencewaterlevel_diskflag_writing:
            k = 0
            for jdx0 in range(self._referencewaterlevel_length_0):
                self._referencewaterlevel_ncarray[k] = self.referencewaterlevel[jdx0]
                k += 1
        if self._referencewaterlevel_ramflag:
            for jdx0 in range(self._referencewaterlevel_length_0):
                self._referencewaterlevel_array[idx, jdx0] = self.referencewaterlevel[jdx0]
        if self._wettedarea_diskflag_writing:
            k = 0
            for jdx0 in range(self._wettedarea_length_0):
                self._wettedarea_ncarray[k] = self.wettedarea[jdx0]
                k += 1
        if self._wettedarea_ramflag:
            for jdx0 in range(self._wettedarea_length_0):
                self._wettedarea_array[idx, jdx0] = self.wettedarea[jdx0]
        if self._wettedperimeter_diskflag_writing:
            k = 0
            for jdx0 in range(self._wettedperimeter_length_0):
                self._wettedperimeter_ncarray[k] = self.wettedperimeter[jdx0]
                k += 1
        if self._wettedperimeter_ramflag:
            for jdx0 in range(self._wettedperimeter_length_0):
                self._wettedperimeter_array[idx, jdx0] = self.wettedperimeter[jdx0]
        if self._surfacewidth_diskflag_writing:
            k = 0
            for jdx0 in range(self._surfacewidth_length_0):
                self._surfacewidth_ncarray[k] = self.surfacewidth[jdx0]
                k += 1
        if self._surfacewidth_ramflag:
            for jdx0 in range(self._surfacewidth_length_0):
                self._surfacewidth_array[idx, jdx0] = self.surfacewidth[jdx0]
        if self._celerity_diskflag_writing:
            k = 0
            for jdx0 in range(self._celerity_length_0):
                self._celerity_ncarray[k] = self.celerity[jdx0]
                k += 1
        if self._celerity_ramflag:
            for jdx0 in range(self._celerity_length_0):
                self._celerity_array[idx, jdx0] = self.celerity[jdx0]
        if self._correctingfactor_diskflag_writing:
            k = 0
            for jdx0 in range(self._correctingfactor_length_0):
                self._correctingfactor_ncarray[k] = self.correctingfactor[jdx0]
                k += 1
        if self._correctingfactor_ramflag:
            for jdx0 in range(self._correctingfactor_length_0):
                self._correctingfactor_array[idx, jdx0] = self.correctingfactor[jdx0]
        if self._coefficient1_diskflag_writing:
            k = 0
            for jdx0 in range(self._coefficient1_length_0):
                self._coefficient1_ncarray[k] = self.coefficient1[jdx0]
                k += 1
        if self._coefficient1_ramflag:
            for jdx0 in range(self._coefficient1_length_0):
                self._coefficient1_array[idx, jdx0] = self.coefficient1[jdx0]
        if self._coefficient2_diskflag_writing:
            k = 0
            for jdx0 in range(self._coefficient2_length_0):
                self._coefficient2_ncarray[k] = self.coefficient2[jdx0]
                k += 1
        if self._coefficient2_ramflag:
            for jdx0 in range(self._coefficient2_length_0):
                self._coefficient2_array[idx, jdx0] = self.coefficient2[jdx0]
        if self._coefficient3_diskflag_writing:
            k = 0
            for jdx0 in range(self._coefficient3_length_0):
                self._coefficient3_ncarray[k] = self.coefficient3[jdx0]
                k += 1
        if self._coefficient3_ramflag:
            for jdx0 in range(self._coefficient3_length_0):
                self._coefficient3_array[idx, jdx0] = self.coefficient3[jdx0]
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        pass
    cpdef inline void update_outputs(self) nogil:
        pass
@cython.final
cdef class FluxSequences:
    cdef public double inflow
    cdef public int _inflow_ndim
    cdef public int _inflow_length
    cdef public bint _inflow_ramflag
    cdef public double[:] _inflow_array
    cdef public bint _inflow_diskflag_reading
    cdef public bint _inflow_diskflag_writing
    cdef public double[:] _inflow_ncarray
    cdef public bint _inflow_outputflag
    cdef double *_inflow_outputpointer
    cdef public double[:] referencedischarge
    cdef public int _referencedischarge_ndim
    cdef public int _referencedischarge_length
    cdef public int _referencedischarge_length_0
    cdef public bint _referencedischarge_ramflag
    cdef public double[:,:] _referencedischarge_array
    cdef public bint _referencedischarge_diskflag_reading
    cdef public bint _referencedischarge_diskflag_writing
    cdef public double[:] _referencedischarge_ncarray
    cdef public bint _referencedischarge_outputflag
    cdef double *_referencedischarge_outputpointer
    cdef public double outflow
    cdef public int _outflow_ndim
    cdef public int _outflow_length
    cdef public bint _outflow_ramflag
    cdef public double[:] _outflow_array
    cdef public bint _outflow_diskflag_reading
    cdef public bint _outflow_diskflag_writing
    cdef public double[:] _outflow_ncarray
    cdef public bint _outflow_outputflag
    cdef double *_outflow_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._inflow_diskflag_reading:
            self.inflow = self._inflow_ncarray[0]
        elif self._inflow_ramflag:
            self.inflow = self._inflow_array[idx]
        if self._referencedischarge_diskflag_reading:
            k = 0
            for jdx0 in range(self._referencedischarge_length_0):
                self.referencedischarge[jdx0] = self._referencedischarge_ncarray[k]
                k += 1
        elif self._referencedischarge_ramflag:
            for jdx0 in range(self._referencedischarge_length_0):
                self.referencedischarge[jdx0] = self._referencedischarge_array[idx, jdx0]
        if self._outflow_diskflag_reading:
            self.outflow = self._outflow_ncarray[0]
        elif self._outflow_ramflag:
            self.outflow = self._outflow_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._inflow_diskflag_writing:
            self._inflow_ncarray[0] = self.inflow
        if self._inflow_ramflag:
            self._inflow_array[idx] = self.inflow
        if self._referencedischarge_diskflag_writing:
            k = 0
            for jdx0 in range(self._referencedischarge_length_0):
                self._referencedischarge_ncarray[k] = self.referencedischarge[jdx0]
                k += 1
        if self._referencedischarge_ramflag:
            for jdx0 in range(self._referencedischarge_length_0):
                self._referencedischarge_array[idx, jdx0] = self.referencedischarge[jdx0]
        if self._outflow_diskflag_writing:
            self._outflow_ncarray[0] = self.outflow
        if self._outflow_ramflag:
            self._outflow_array[idx] = self.outflow
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "inflow":
            self._inflow_outputpointer = value.p_value
        if name == "outflow":
            self._outflow_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._inflow_outputflag:
            self._inflow_outputpointer[0] = self.inflow
        if self._outflow_outputflag:
            self._outflow_outputpointer[0] = self.outflow
@cython.final
cdef class StateSequences:
    cdef public double[:] courantnumber
    cdef public int _courantnumber_ndim
    cdef public int _courantnumber_length
    cdef public int _courantnumber_length_0
    cdef public bint _courantnumber_ramflag
    cdef public double[:,:] _courantnumber_array
    cdef public bint _courantnumber_diskflag_reading
    cdef public bint _courantnumber_diskflag_writing
    cdef public double[:] _courantnumber_ncarray
    cdef public bint _courantnumber_outputflag
    cdef double *_courantnumber_outputpointer
    cdef public double[:] reynoldsnumber
    cdef public int _reynoldsnumber_ndim
    cdef public int _reynoldsnumber_length
    cdef public int _reynoldsnumber_length_0
    cdef public bint _reynoldsnumber_ramflag
    cdef public double[:,:] _reynoldsnumber_array
    cdef public bint _reynoldsnumber_diskflag_reading
    cdef public bint _reynoldsnumber_diskflag_writing
    cdef public double[:] _reynoldsnumber_ncarray
    cdef public bint _reynoldsnumber_outputflag
    cdef double *_reynoldsnumber_outputpointer
    cdef public double[:] discharge
    cdef public int _discharge_ndim
    cdef public int _discharge_length
    cdef public int _discharge_length_0
    cdef public bint _discharge_ramflag
    cdef public double[:,:] _discharge_array
    cdef public bint _discharge_diskflag_reading
    cdef public bint _discharge_diskflag_writing
    cdef public double[:] _discharge_ncarray
    cdef public bint _discharge_outputflag
    cdef double *_discharge_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._courantnumber_diskflag_reading:
            k = 0
            for jdx0 in range(self._courantnumber_length_0):
                self.courantnumber[jdx0] = self._courantnumber_ncarray[k]
                k += 1
        elif self._courantnumber_ramflag:
            for jdx0 in range(self._courantnumber_length_0):
                self.courantnumber[jdx0] = self._courantnumber_array[idx, jdx0]
        if self._reynoldsnumber_diskflag_reading:
            k = 0
            for jdx0 in range(self._reynoldsnumber_length_0):
                self.reynoldsnumber[jdx0] = self._reynoldsnumber_ncarray[k]
                k += 1
        elif self._reynoldsnumber_ramflag:
            for jdx0 in range(self._reynoldsnumber_length_0):
                self.reynoldsnumber[jdx0] = self._reynoldsnumber_array[idx, jdx0]
        if self._discharge_diskflag_reading:
            k = 0
            for jdx0 in range(self._discharge_length_0):
                self.discharge[jdx0] = self._discharge_ncarray[k]
                k += 1
        elif self._discharge_ramflag:
            for jdx0 in range(self._discharge_length_0):
                self.discharge[jdx0] = self._discharge_array[idx, jdx0]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._courantnumber_diskflag_writing:
            k = 0
            for jdx0 in range(self._courantnumber_length_0):
                self._courantnumber_ncarray[k] = self.courantnumber[jdx0]
                k += 1
        if self._courantnumber_ramflag:
            for jdx0 in range(self._courantnumber_length_0):
                self._courantnumber_array[idx, jdx0] = self.courantnumber[jdx0]
        if self._reynoldsnumber_diskflag_writing:
            k = 0
            for jdx0 in range(self._reynoldsnumber_length_0):
                self._reynoldsnumber_ncarray[k] = self.reynoldsnumber[jdx0]
                k += 1
        if self._reynoldsnumber_ramflag:
            for jdx0 in range(self._reynoldsnumber_length_0):
                self._reynoldsnumber_array[idx, jdx0] = self.reynoldsnumber[jdx0]
        if self._discharge_diskflag_writing:
            k = 0
            for jdx0 in range(self._discharge_length_0):
                self._discharge_ncarray[k] = self.discharge[jdx0]
                k += 1
        if self._discharge_ramflag:
            for jdx0 in range(self._discharge_length_0):
                self._discharge_array[idx, jdx0] = self.discharge[jdx0]
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        pass
    cpdef inline void update_outputs(self) nogil:
        pass
@cython.final
cdef class OutletSequences:
    cdef double *q
    cdef public int _q_ndim
    cdef public int _q_length
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "q":
            self.q = pointer.p_value
    cpdef get_value(self, str name):
        cdef int idx
        if name == "q":
            return self.q[0]
    cpdef set_value(self, str name, value):
        if name == "q":
            self.q[0] = value

@cython.final
cdef class PegasusReferenceWaterLevel(rootutils.PegasusBase):
    cdef public Model model
    def __init__(self, Model model):
        self.model = model
    cpdef double apply_method0(self, double x) nogil:
        return self.model.return_referencedischargeerror_v1(x)
@cython.final
cdef class Model:
    cdef public int idx_segment
    cdef public int idx_run
    cdef public int idx_sim
    cdef public Parameters parameters
    cdef public Sequences sequences
    cdef public PegasusReferenceWaterLevel pegasusreferencewaterlevel
    def __init__(self):
        self.pegasusreferencewaterlevel = PegasusReferenceWaterLevel(self)
    cpdef inline void simulate(self, int idx)  nogil:
        self.idx_sim = idx
        self.update_inlets()
        self.run()
        self.new2old()
        self.update_outlets()
        self.update_outputs()
    cpdef inline void save_data(self, int idx) nogil:
        self.sequences.factors.save_data(self.idx_sim)
        self.sequences.fluxes.save_data(self.idx_sim)
        self.sequences.states.save_data(self.idx_sim)
    cpdef inline void new2old(self) nogil:
        cdef int jdx0
        for jdx0 in range(self.sequences.states._courantnumber_length_0):
            self.sequences.old_states.courantnumber[jdx0] = self.sequences.new_states.courantnumber[jdx0]
        for jdx0 in range(self.sequences.states._reynoldsnumber_length_0):
            self.sequences.old_states.reynoldsnumber[jdx0] = self.sequences.new_states.reynoldsnumber[jdx0]
        for jdx0 in range(self.sequences.states._discharge_length_0):
            self.sequences.old_states.discharge[jdx0] = self.sequences.new_states.discharge[jdx0]
    cpdef inline void run(self) nogil:
        cdef numpy.int32_t idx_segment, idx_run
        for idx_segment in range(self.parameters.control.nmbsegments):
            self.idx_segment = idx_segment
            for idx_run in range(self.parameters.solver.nmbruns):
                self.idx_run = idx_run
                self.calc_discharge_v1()
                self.calc_referencedischarge_v1()
                self.calc_referencewaterlevel_v1()
                self.calc_wettedarea_v1()
                self.calc_wettedperimeter_v1()
                self.calc_surfacewidth_v1()
                self.calc_celerity_v1()
                self.calc_correctingfactor_v1()
                self.calc_courantnumber_v1()
                self.calc_reynoldsnumber_v1()
                self.calc_coefficient1_coefficient2_coefficient3_v1()
                self.calc_discharge_v2()
    cpdef inline void update_inlets(self) nogil:
        self.pick_inflow_v1()
        self.update_discharge_v1()
    cpdef inline void update_outlets(self) nogil:
        self.calc_outflow_v1()
        self.pass_outflow_v1()
    cpdef inline void update_receivers(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_senders(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_outputs(self) nogil:
        self.sequences.fluxes.update_outputs()

    cpdef inline void pick_inflow_v1(self)  nogil:
        cdef int idx
        self.sequences.fluxes.inflow = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx][0])
    cpdef inline void update_discharge_v1(self)  nogil:
        self.sequences.states.discharge[0] = self.sequences.fluxes.inflow
    cpdef inline void pick_inflow(self)  nogil:
        cdef int idx
        self.sequences.fluxes.inflow = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx][0])
    cpdef inline void update_discharge(self)  nogil:
        self.sequences.states.discharge[0] = self.sequences.fluxes.inflow
    cpdef inline void calc_discharge_v1(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.new_states.discharge[i + 1] = (            self.parameters.control.coefficients[0] * self.sequences.new_states.discharge[i]            + self.parameters.control.coefficients[1] * self.sequences.old_states.discharge[i]            + self.parameters.control.coefficients[2] * self.sequences.old_states.discharge[i + 1]        )
    cpdef inline void calc_referencedischarge_v1(self)  nogil:
        cdef double d_est
        cdef int i
        i = self.idx_segment
        if self.idx_run == 0:
            d_est = self.sequences.old_states.discharge[i + 1] + self.sequences.new_states.discharge[i] - self.sequences.old_states.discharge[i]
        else:
            d_est = self.sequences.new_states.discharge[i + 1]
        self.sequences.fluxes.referencedischarge[i] = (self.sequences.new_states.discharge[i] + d_est) / 2.0
    cpdef inline void calc_referencewaterlevel_v1(self)  nogil:
        cdef double d_max
        cdef double d_min
        cdef double d_wl
        cdef int i
        i = self.idx_segment
        d_wl = self.sequences.factors.referencewaterlevel[i]
        if isnan(d_wl) or isinf(d_wl):
            d_min, d_max = 0.0, 2.0
        elif d_wl <= 0.001:
            d_min, d_max = 0.0, 0.01
        else:
            d_min, d_max = 0.9 * d_wl, 1.1 * d_wl
        self.sequences.factors.referencewaterlevel[i] = self.pegasusreferencewaterlevel.find_x(            d_min,            d_max,            0.0,            1000.0,            self.parameters.solver.tolerancewaterlevel,            self.parameters.solver.tolerancedischarge,            100,        )
    cpdef inline void calc_wettedarea_v1(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.wettedarea[i] = self.return_wettedarea_v1(self.sequences.factors.referencewaterlevel[i])
    cpdef inline void calc_wettedperimeter_v1(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.wettedperimeter[i] = self.return_wettedperimeter_v1(            self.sequences.factors.referencewaterlevel[i]        )
    cpdef inline void calc_surfacewidth_v1(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.surfacewidth[i] = self.return_surfacewidth_v1(self.sequences.factors.referencewaterlevel[i])
    cpdef inline void calc_celerity_v1(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.celerity[i] = self.return_celerity_v1()
    cpdef inline void calc_correctingfactor_v1(self)  nogil:
        cdef int i
        i = self.idx_segment
        if self.sequences.fluxes.referencedischarge[i] == 0.0:
            self.sequences.factors.correctingfactor[i] = 1.0
        else:
            self.sequences.factors.correctingfactor[i] = (                self.sequences.factors.celerity[i] * self.sequences.factors.wettedarea[i] / self.sequences.fluxes.referencedischarge[i]            )
    cpdef inline void calc_courantnumber_v1(self)  nogil:
        cdef int i
        i = self.idx_segment
        if self.sequences.factors.correctingfactor[i] == 0.0:
            self.sequences.states.courantnumber[i] = 0.0
        else:
            self.sequences.states.courantnumber[i] = (self.sequences.factors.celerity[i] / self.sequences.factors.correctingfactor[i]) * (                self.parameters.derived.seconds / (1000.0 * self.parameters.control.length[i])            )
    cpdef inline void calc_reynoldsnumber_v1(self)  nogil:
        cdef double d_denom
        cdef int i
        i = self.idx_segment
        d_denom = (            self.sequences.factors.correctingfactor[i]            * self.sequences.factors.surfacewidth[i]            * self.parameters.control.bottomslope[i]            * self.sequences.factors.celerity[i]            * (1000.0 * self.parameters.control.length[i])        )
        if d_denom == 0.0:
            self.sequences.states.reynoldsnumber[i] = 0.0
        else:
            self.sequences.states.reynoldsnumber[i] = self.sequences.fluxes.referencedischarge[i] / d_denom
    cpdef inline void calc_coefficient1_coefficient2_coefficient3_v1(self)  nogil:
        cdef double d_f
        cdef int i
        i = self.idx_segment
        d_f = 1.0 / (1.0 + self.sequences.new_states.courantnumber[i] + self.sequences.new_states.reynoldsnumber[i])
        self.sequences.factors.coefficient1[i] = (self.sequences.new_states.courantnumber[i] + self.sequences.new_states.reynoldsnumber[i] - 1.0) * d_f
        if self.sequences.old_states.courantnumber[i] != 0.0:
            d_f = d_f * (self.sequences.new_states.courantnumber[i] / self.sequences.old_states.courantnumber[i])
        self.sequences.factors.coefficient2[i] = (1 + self.sequences.old_states.courantnumber[i] - self.sequences.old_states.reynoldsnumber[i]) * d_f
        self.sequences.factors.coefficient3[i] = (1 - self.sequences.old_states.courantnumber[i] + self.sequences.old_states.reynoldsnumber[i]) * d_f
    cpdef inline void calc_discharge_v2(self)  nogil:
        cdef int i
        i = self.idx_segment
        if self.sequences.new_states.discharge[i] == self.sequences.old_states.discharge[i] == self.sequences.old_states.discharge[i + 1]:
            self.sequences.new_states.discharge[i + 1] = self.sequences.new_states.discharge[i]
        else:
            self.sequences.new_states.discharge[i + 1] = (                self.sequences.factors.coefficient1[i] * self.sequences.new_states.discharge[i]                + self.sequences.factors.coefficient2[i] * self.sequences.old_states.discharge[i]                + self.sequences.factors.coefficient3[i] * self.sequences.old_states.discharge[i + 1]            )
        self.sequences.new_states.discharge[i + 1] = max(self.sequences.new_states.discharge[i + 1], 0.0)
    cpdef inline void calc_referencedischarge(self)  nogil:
        cdef double d_est
        cdef int i
        i = self.idx_segment
        if self.idx_run == 0:
            d_est = self.sequences.old_states.discharge[i + 1] + self.sequences.new_states.discharge[i] - self.sequences.old_states.discharge[i]
        else:
            d_est = self.sequences.new_states.discharge[i + 1]
        self.sequences.fluxes.referencedischarge[i] = (self.sequences.new_states.discharge[i] + d_est) / 2.0
    cpdef inline void calc_referencewaterlevel(self)  nogil:
        cdef double d_max
        cdef double d_min
        cdef double d_wl
        cdef int i
        i = self.idx_segment
        d_wl = self.sequences.factors.referencewaterlevel[i]
        if isnan(d_wl) or isinf(d_wl):
            d_min, d_max = 0.0, 2.0
        elif d_wl <= 0.001:
            d_min, d_max = 0.0, 0.01
        else:
            d_min, d_max = 0.9 * d_wl, 1.1 * d_wl
        self.sequences.factors.referencewaterlevel[i] = self.pegasusreferencewaterlevel.find_x(            d_min,            d_max,            0.0,            1000.0,            self.parameters.solver.tolerancewaterlevel,            self.parameters.solver.tolerancedischarge,            100,        )
    cpdef inline void calc_wettedarea(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.wettedarea[i] = self.return_wettedarea_v1(self.sequences.factors.referencewaterlevel[i])
    cpdef inline void calc_wettedperimeter(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.wettedperimeter[i] = self.return_wettedperimeter_v1(            self.sequences.factors.referencewaterlevel[i]        )
    cpdef inline void calc_surfacewidth(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.surfacewidth[i] = self.return_surfacewidth_v1(self.sequences.factors.referencewaterlevel[i])
    cpdef inline void calc_celerity(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.factors.celerity[i] = self.return_celerity_v1()
    cpdef inline void calc_correctingfactor(self)  nogil:
        cdef int i
        i = self.idx_segment
        if self.sequences.fluxes.referencedischarge[i] == 0.0:
            self.sequences.factors.correctingfactor[i] = 1.0
        else:
            self.sequences.factors.correctingfactor[i] = (                self.sequences.factors.celerity[i] * self.sequences.factors.wettedarea[i] / self.sequences.fluxes.referencedischarge[i]            )
    cpdef inline void calc_courantnumber(self)  nogil:
        cdef int i
        i = self.idx_segment
        if self.sequences.factors.correctingfactor[i] == 0.0:
            self.sequences.states.courantnumber[i] = 0.0
        else:
            self.sequences.states.courantnumber[i] = (self.sequences.factors.celerity[i] / self.sequences.factors.correctingfactor[i]) * (                self.parameters.derived.seconds / (1000.0 * self.parameters.control.length[i])            )
    cpdef inline void calc_reynoldsnumber(self)  nogil:
        cdef double d_denom
        cdef int i
        i = self.idx_segment
        d_denom = (            self.sequences.factors.correctingfactor[i]            * self.sequences.factors.surfacewidth[i]            * self.parameters.control.bottomslope[i]            * self.sequences.factors.celerity[i]            * (1000.0 * self.parameters.control.length[i])        )
        if d_denom == 0.0:
            self.sequences.states.reynoldsnumber[i] = 0.0
        else:
            self.sequences.states.reynoldsnumber[i] = self.sequences.fluxes.referencedischarge[i] / d_denom
    cpdef inline void calc_coefficient1_coefficient2_coefficient3(self)  nogil:
        cdef double d_f
        cdef int i
        i = self.idx_segment
        d_f = 1.0 / (1.0 + self.sequences.new_states.courantnumber[i] + self.sequences.new_states.reynoldsnumber[i])
        self.sequences.factors.coefficient1[i] = (self.sequences.new_states.courantnumber[i] + self.sequences.new_states.reynoldsnumber[i] - 1.0) * d_f
        if self.sequences.old_states.courantnumber[i] != 0.0:
            d_f = d_f * (self.sequences.new_states.courantnumber[i] / self.sequences.old_states.courantnumber[i])
        self.sequences.factors.coefficient2[i] = (1 + self.sequences.old_states.courantnumber[i] - self.sequences.old_states.reynoldsnumber[i]) * d_f
        self.sequences.factors.coefficient3[i] = (1 - self.sequences.old_states.courantnumber[i] + self.sequences.old_states.reynoldsnumber[i]) * d_f
    cpdef inline double return_wettedarea_v1(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return waterlevel * (self.parameters.control.bottomwidth[i] + self.parameters.control.sideslope[i] * waterlevel)
    cpdef inline double return_wettedperimeter_v1(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return self.parameters.control.bottomwidth[i] + (            2.0 * waterlevel * (1.0 + self.parameters.control.sideslope[i] ** 2.0) ** 0.5        )
    cpdef inline double return_surfacewidth_v1(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return self.parameters.control.bottomwidth[i] + 2.0 * self.parameters.control.sideslope[i] * waterlevel
    cpdef inline double return_discharge_v1(self, double waterlevel)  nogil:
        cdef int i
        if waterlevel <= 0.0:
            return 0.0
        i = self.idx_segment
        return (            self.parameters.control.stricklercoefficient[i]            * self.parameters.control.bottomslope[i] ** 0.5            * self.return_wettedarea(waterlevel) ** (5.0 / 3.0)            / self.return_wettedperimeter(waterlevel) ** (2.0 / 3.0)        )
    cpdef inline double return_referencedischargeerror_v1(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return self.return_discharge(waterlevel) - self.sequences.fluxes.referencedischarge[i]
    cpdef inline double return_celerity_v1(self)  nogil:
        cdef double d_r
        cdef int i
        i = self.idx_segment
        if self.sequences.factors.wettedarea[i] == 0.0:
            return 0.0
        d_r = self.sequences.factors.wettedarea[i] / self.sequences.factors.wettedperimeter[i]
        return (            self.parameters.control.stricklercoefficient[i]            * self.parameters.control.bottomslope[i] ** 0.5            * d_r ** (2.0 / 3.0)            / 3.0        ) * (5.0 - (2.0 * d_r * self.parameters.derived.perimeterincrease[i] / self.sequences.factors.surfacewidth[i]))
    cpdef inline double return_wettedarea(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return waterlevel * (self.parameters.control.bottomwidth[i] + self.parameters.control.sideslope[i] * waterlevel)
    cpdef inline double return_wettedperimeter(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return self.parameters.control.bottomwidth[i] + (            2.0 * waterlevel * (1.0 + self.parameters.control.sideslope[i] ** 2.0) ** 0.5        )
    cpdef inline double return_surfacewidth(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return self.parameters.control.bottomwidth[i] + 2.0 * self.parameters.control.sideslope[i] * waterlevel
    cpdef inline double return_discharge(self, double waterlevel)  nogil:
        cdef int i
        if waterlevel <= 0.0:
            return 0.0
        i = self.idx_segment
        return (            self.parameters.control.stricklercoefficient[i]            * self.parameters.control.bottomslope[i] ** 0.5            * self.return_wettedarea(waterlevel) ** (5.0 / 3.0)            / self.return_wettedperimeter(waterlevel) ** (2.0 / 3.0)        )
    cpdef inline double return_referencedischargeerror(self, double waterlevel)  nogil:
        cdef int i
        i = self.idx_segment
        return self.return_discharge(waterlevel) - self.sequences.fluxes.referencedischarge[i]
    cpdef inline double return_celerity(self)  nogil:
        cdef double d_r
        cdef int i
        i = self.idx_segment
        if self.sequences.factors.wettedarea[i] == 0.0:
            return 0.0
        d_r = self.sequences.factors.wettedarea[i] / self.sequences.factors.wettedperimeter[i]
        return (            self.parameters.control.stricklercoefficient[i]            * self.parameters.control.bottomslope[i] ** 0.5            * d_r ** (2.0 / 3.0)            / 3.0        ) * (5.0 - (2.0 * d_r * self.parameters.derived.perimeterincrease[i] / self.sequences.factors.surfacewidth[i]))
    cpdef inline void calc_outflow_v1(self)  nogil:
        self.sequences.fluxes.outflow = self.sequences.states.discharge[self.parameters.control.nmbsegments]
    cpdef inline void pass_outflow_v1(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
    cpdef inline void calc_outflow(self)  nogil:
        self.sequences.fluxes.outflow = self.sequences.states.discharge[self.parameters.control.nmbsegments]
    cpdef inline void pass_outflow(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
