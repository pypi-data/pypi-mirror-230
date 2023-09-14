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
    cdef public SolverParameters solver
@cython.final
cdef class ControlParameters:
    cdef public numpy.int32_t nmbsegments
    cdef public double[:] coefficients
@cython.final
cdef class SolverParameters:
    cdef public numpy.int32_t nmbruns
@cython.final
cdef class Sequences:
    cdef public InletSequences inlets
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
        cdef int k
        if self._inflow_diskflag_reading:
            self.inflow = self._inflow_ncarray[0]
        elif self._inflow_ramflag:
            self.inflow = self._inflow_array[idx]
        if self._outflow_diskflag_reading:
            self.outflow = self._outflow_ncarray[0]
        elif self._outflow_ramflag:
            self.outflow = self._outflow_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._inflow_diskflag_writing:
            self._inflow_ncarray[0] = self.inflow
        if self._inflow_ramflag:
            self._inflow_array[idx] = self.inflow
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
cdef class Model:
    cdef public int idx_segment
    cdef public int idx_run
    cdef public int idx_sim
    cdef public Parameters parameters
    cdef public Sequences sequences
    cpdef inline void simulate(self, int idx)  nogil:
        self.idx_sim = idx
        self.update_inlets()
        self.run()
        self.new2old()
        self.update_outlets()
        self.update_outputs()
    cpdef inline void save_data(self, int idx) nogil:
        self.sequences.fluxes.save_data(self.idx_sim)
        self.sequences.states.save_data(self.idx_sim)
    cpdef inline void new2old(self) nogil:
        cdef int jdx0
        for jdx0 in range(self.sequences.states._discharge_length_0):
            self.sequences.old_states.discharge[jdx0] = self.sequences.new_states.discharge[jdx0]
    cpdef inline void run(self) nogil:
        cdef numpy.int32_t idx_segment, idx_run
        for idx_segment in range(self.parameters.control.nmbsegments):
            self.idx_segment = idx_segment
            for idx_run in range(self.parameters.solver.nmbruns):
                self.idx_run = idx_run
                self.calc_discharge_v1()
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
    cpdef inline void calc_discharge(self)  nogil:
        cdef int i
        i = self.idx_segment
        self.sequences.new_states.discharge[i + 1] = (            self.parameters.control.coefficients[0] * self.sequences.new_states.discharge[i]            + self.parameters.control.coefficients[1] * self.sequences.old_states.discharge[i]            + self.parameters.control.coefficients[2] * self.sequences.old_states.discharge[i + 1]        )
    cpdef inline void calc_outflow_v1(self)  nogil:
        self.sequences.fluxes.outflow = self.sequences.states.discharge[self.parameters.control.nmbsegments]
    cpdef inline void pass_outflow_v1(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
    cpdef inline void calc_outflow(self)  nogil:
        self.sequences.fluxes.outflow = self.sequences.states.discharge[self.parameters.control.nmbsegments]
    cpdef inline void pass_outflow(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
