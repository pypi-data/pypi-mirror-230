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
cdef public bint TYPE_CHECKING = False
@cython.final
cdef class Parameters:
    cdef public ControlParameters control
    cdef public DerivedParameters derived
    cdef public SolverParameters solver
@cython.final
cdef class ControlParameters:
    cdef public double surfacearea
    cdef public double catchmentarea
    cdef public double correctionprecipitation
    cdef public double correctionevaporation
    cdef public double weightevaporation
    cdef public double[:] neardischargeminimumthreshold
    cdef public double[:] watervolumeminimumthreshold
    cdef public double thresholdevaporation
    cdef public double toleranceevaporation
    cdef public interputils.SimpleInterpolator watervolume2waterlevel
    cdef public interputils.SeasonalInterpolator waterlevel2flooddischarge
    cdef public double allowedwaterleveldrop
    cdef public double[:] allowedrelease
    cdef public double[:] targetvolume
    cdef public double targetrangeabsolute
    cdef public double targetrangerelative
    cdef public double volumetolerance
    cdef public double dischargetolerance
@cython.final
cdef class DerivedParameters:
    cdef public numpy.int32_t[:] toy
    cdef public double seconds
    cdef public double inputfactor
    cdef public double smoothparevaporation
    cdef public double volumesmoothparlog1
    cdef public double volumesmoothparlog2
    cdef public double dischargesmoothpar
@cython.final
cdef class SolverParameters:
    cdef public double abserrormax
    cdef public double relerrormax
    cdef public double reldtmin
    cdef public double reldtmax
@cython.final
cdef class Sequences:
    cdef public InletSequences inlets
    cdef public InputSequences inputs
    cdef public FactorSequences factors
    cdef public FluxSequences fluxes
    cdef public StateSequences states
    cdef public LogSequences logs
    cdef public AideSequences aides
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
cdef class InputSequences:
    cdef public double precipitation
    cdef public int _precipitation_ndim
    cdef public int _precipitation_length
    cdef public bint _precipitation_ramflag
    cdef public double[:] _precipitation_array
    cdef public bint _precipitation_diskflag_reading
    cdef public bint _precipitation_diskflag_writing
    cdef public double[:] _precipitation_ncarray
    cdef public bint _precipitation_inputflag
    cdef double *_precipitation_inputpointer
    cdef public double evaporation
    cdef public int _evaporation_ndim
    cdef public int _evaporation_length
    cdef public bint _evaporation_ramflag
    cdef public double[:] _evaporation_array
    cdef public bint _evaporation_diskflag_reading
    cdef public bint _evaporation_diskflag_writing
    cdef public double[:] _evaporation_ncarray
    cdef public bint _evaporation_inputflag
    cdef double *_evaporation_inputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._precipitation_inputflag:
            self.precipitation = self._precipitation_inputpointer[0]
        elif self._precipitation_diskflag_reading:
            self.precipitation = self._precipitation_ncarray[0]
        elif self._precipitation_ramflag:
            self.precipitation = self._precipitation_array[idx]
        if self._evaporation_inputflag:
            self.evaporation = self._evaporation_inputpointer[0]
        elif self._evaporation_diskflag_reading:
            self.evaporation = self._evaporation_ncarray[0]
        elif self._evaporation_ramflag:
            self.evaporation = self._evaporation_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._precipitation_diskflag_writing:
            self._precipitation_ncarray[0] = self.precipitation
        if self._precipitation_ramflag:
            self._precipitation_array[idx] = self.precipitation
        if self._evaporation_diskflag_writing:
            self._evaporation_ncarray[0] = self.evaporation
        if self._evaporation_ramflag:
            self._evaporation_array[idx] = self.evaporation
    cpdef inline set_pointerinput(self, str name, pointerutils.PDouble value):
        if name == "precipitation":
            self._precipitation_inputpointer = value.p_value
        if name == "evaporation":
            self._evaporation_inputpointer = value.p_value
@cython.final
cdef class FactorSequences:
    cdef public double waterlevel
    cdef public int _waterlevel_ndim
    cdef public int _waterlevel_length
    cdef public bint _waterlevel_ramflag
    cdef public double[:] _waterlevel_array
    cdef public bint _waterlevel_diskflag_reading
    cdef public bint _waterlevel_diskflag_writing
    cdef public double[:] _waterlevel_ncarray
    cdef public bint _waterlevel_outputflag
    cdef double *_waterlevel_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._waterlevel_diskflag_reading:
            self.waterlevel = self._waterlevel_ncarray[0]
        elif self._waterlevel_ramflag:
            self.waterlevel = self._waterlevel_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._waterlevel_diskflag_writing:
            self._waterlevel_ncarray[0] = self.waterlevel
        if self._waterlevel_ramflag:
            self._waterlevel_array[idx] = self.waterlevel
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "waterlevel":
            self._waterlevel_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._waterlevel_outputflag:
            self._waterlevel_outputpointer[0] = self.waterlevel
@cython.final
cdef class FluxSequences:
    cdef public double adjustedprecipitation
    cdef public int _adjustedprecipitation_ndim
    cdef public int _adjustedprecipitation_length
    cdef public double[:] _adjustedprecipitation_points
    cdef public double[:] _adjustedprecipitation_results
    cdef public double[:] _adjustedprecipitation_integrals
    cdef public double _adjustedprecipitation_sum
    cdef public bint _adjustedprecipitation_ramflag
    cdef public double[:] _adjustedprecipitation_array
    cdef public bint _adjustedprecipitation_diskflag_reading
    cdef public bint _adjustedprecipitation_diskflag_writing
    cdef public double[:] _adjustedprecipitation_ncarray
    cdef public bint _adjustedprecipitation_outputflag
    cdef double *_adjustedprecipitation_outputpointer
    cdef public double adjustedevaporation
    cdef public int _adjustedevaporation_ndim
    cdef public int _adjustedevaporation_length
    cdef public bint _adjustedevaporation_ramflag
    cdef public double[:] _adjustedevaporation_array
    cdef public bint _adjustedevaporation_diskflag_reading
    cdef public bint _adjustedevaporation_diskflag_writing
    cdef public double[:] _adjustedevaporation_ncarray
    cdef public bint _adjustedevaporation_outputflag
    cdef double *_adjustedevaporation_outputpointer
    cdef public double actualevaporation
    cdef public int _actualevaporation_ndim
    cdef public int _actualevaporation_length
    cdef public double[:] _actualevaporation_points
    cdef public double[:] _actualevaporation_results
    cdef public double[:] _actualevaporation_integrals
    cdef public double _actualevaporation_sum
    cdef public bint _actualevaporation_ramflag
    cdef public double[:] _actualevaporation_array
    cdef public bint _actualevaporation_diskflag_reading
    cdef public bint _actualevaporation_diskflag_writing
    cdef public double[:] _actualevaporation_ncarray
    cdef public bint _actualevaporation_outputflag
    cdef double *_actualevaporation_outputpointer
    cdef public double inflow
    cdef public int _inflow_ndim
    cdef public int _inflow_length
    cdef public double[:] _inflow_points
    cdef public double[:] _inflow_results
    cdef public double[:] _inflow_integrals
    cdef public double _inflow_sum
    cdef public bint _inflow_ramflag
    cdef public double[:] _inflow_array
    cdef public bint _inflow_diskflag_reading
    cdef public bint _inflow_diskflag_writing
    cdef public double[:] _inflow_ncarray
    cdef public bint _inflow_outputflag
    cdef double *_inflow_outputpointer
    cdef public double actualrelease
    cdef public int _actualrelease_ndim
    cdef public int _actualrelease_length
    cdef public double[:] _actualrelease_points
    cdef public double[:] _actualrelease_results
    cdef public double[:] _actualrelease_integrals
    cdef public double _actualrelease_sum
    cdef public bint _actualrelease_ramflag
    cdef public double[:] _actualrelease_array
    cdef public bint _actualrelease_diskflag_reading
    cdef public bint _actualrelease_diskflag_writing
    cdef public double[:] _actualrelease_ncarray
    cdef public bint _actualrelease_outputflag
    cdef double *_actualrelease_outputpointer
    cdef public double flooddischarge
    cdef public int _flooddischarge_ndim
    cdef public int _flooddischarge_length
    cdef public double[:] _flooddischarge_points
    cdef public double[:] _flooddischarge_results
    cdef public double[:] _flooddischarge_integrals
    cdef public double _flooddischarge_sum
    cdef public bint _flooddischarge_ramflag
    cdef public double[:] _flooddischarge_array
    cdef public bint _flooddischarge_diskflag_reading
    cdef public bint _flooddischarge_diskflag_writing
    cdef public double[:] _flooddischarge_ncarray
    cdef public bint _flooddischarge_outputflag
    cdef double *_flooddischarge_outputpointer
    cdef public double outflow
    cdef public int _outflow_ndim
    cdef public int _outflow_length
    cdef public double[:] _outflow_points
    cdef public double[:] _outflow_results
    cdef public double[:] _outflow_integrals
    cdef public double _outflow_sum
    cdef public bint _outflow_ramflag
    cdef public double[:] _outflow_array
    cdef public bint _outflow_diskflag_reading
    cdef public bint _outflow_diskflag_writing
    cdef public double[:] _outflow_ncarray
    cdef public bint _outflow_outputflag
    cdef double *_outflow_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._adjustedprecipitation_diskflag_reading:
            self.adjustedprecipitation = self._adjustedprecipitation_ncarray[0]
        elif self._adjustedprecipitation_ramflag:
            self.adjustedprecipitation = self._adjustedprecipitation_array[idx]
        if self._adjustedevaporation_diskflag_reading:
            self.adjustedevaporation = self._adjustedevaporation_ncarray[0]
        elif self._adjustedevaporation_ramflag:
            self.adjustedevaporation = self._adjustedevaporation_array[idx]
        if self._actualevaporation_diskflag_reading:
            self.actualevaporation = self._actualevaporation_ncarray[0]
        elif self._actualevaporation_ramflag:
            self.actualevaporation = self._actualevaporation_array[idx]
        if self._inflow_diskflag_reading:
            self.inflow = self._inflow_ncarray[0]
        elif self._inflow_ramflag:
            self.inflow = self._inflow_array[idx]
        if self._actualrelease_diskflag_reading:
            self.actualrelease = self._actualrelease_ncarray[0]
        elif self._actualrelease_ramflag:
            self.actualrelease = self._actualrelease_array[idx]
        if self._flooddischarge_diskflag_reading:
            self.flooddischarge = self._flooddischarge_ncarray[0]
        elif self._flooddischarge_ramflag:
            self.flooddischarge = self._flooddischarge_array[idx]
        if self._outflow_diskflag_reading:
            self.outflow = self._outflow_ncarray[0]
        elif self._outflow_ramflag:
            self.outflow = self._outflow_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._adjustedprecipitation_diskflag_writing:
            self._adjustedprecipitation_ncarray[0] = self.adjustedprecipitation
        if self._adjustedprecipitation_ramflag:
            self._adjustedprecipitation_array[idx] = self.adjustedprecipitation
        if self._adjustedevaporation_diskflag_writing:
            self._adjustedevaporation_ncarray[0] = self.adjustedevaporation
        if self._adjustedevaporation_ramflag:
            self._adjustedevaporation_array[idx] = self.adjustedevaporation
        if self._actualevaporation_diskflag_writing:
            self._actualevaporation_ncarray[0] = self.actualevaporation
        if self._actualevaporation_ramflag:
            self._actualevaporation_array[idx] = self.actualevaporation
        if self._inflow_diskflag_writing:
            self._inflow_ncarray[0] = self.inflow
        if self._inflow_ramflag:
            self._inflow_array[idx] = self.inflow
        if self._actualrelease_diskflag_writing:
            self._actualrelease_ncarray[0] = self.actualrelease
        if self._actualrelease_ramflag:
            self._actualrelease_array[idx] = self.actualrelease
        if self._flooddischarge_diskflag_writing:
            self._flooddischarge_ncarray[0] = self.flooddischarge
        if self._flooddischarge_ramflag:
            self._flooddischarge_array[idx] = self.flooddischarge
        if self._outflow_diskflag_writing:
            self._outflow_ncarray[0] = self.outflow
        if self._outflow_ramflag:
            self._outflow_array[idx] = self.outflow
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "adjustedprecipitation":
            self._adjustedprecipitation_outputpointer = value.p_value
        if name == "adjustedevaporation":
            self._adjustedevaporation_outputpointer = value.p_value
        if name == "actualevaporation":
            self._actualevaporation_outputpointer = value.p_value
        if name == "inflow":
            self._inflow_outputpointer = value.p_value
        if name == "actualrelease":
            self._actualrelease_outputpointer = value.p_value
        if name == "flooddischarge":
            self._flooddischarge_outputpointer = value.p_value
        if name == "outflow":
            self._outflow_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._adjustedprecipitation_outputflag:
            self._adjustedprecipitation_outputpointer[0] = self.adjustedprecipitation
        if self._adjustedevaporation_outputflag:
            self._adjustedevaporation_outputpointer[0] = self.adjustedevaporation
        if self._actualevaporation_outputflag:
            self._actualevaporation_outputpointer[0] = self.actualevaporation
        if self._inflow_outputflag:
            self._inflow_outputpointer[0] = self.inflow
        if self._actualrelease_outputflag:
            self._actualrelease_outputpointer[0] = self.actualrelease
        if self._flooddischarge_outputflag:
            self._flooddischarge_outputpointer[0] = self.flooddischarge
        if self._outflow_outputflag:
            self._outflow_outputpointer[0] = self.outflow
@cython.final
cdef class StateSequences:
    cdef public double watervolume
    cdef public int _watervolume_ndim
    cdef public int _watervolume_length
    cdef public double[:] _watervolume_points
    cdef public double[:] _watervolume_results
    cdef public bint _watervolume_ramflag
    cdef public double[:] _watervolume_array
    cdef public bint _watervolume_diskflag_reading
    cdef public bint _watervolume_diskflag_writing
    cdef public double[:] _watervolume_ncarray
    cdef public bint _watervolume_outputflag
    cdef double *_watervolume_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._watervolume_diskflag_reading:
            self.watervolume = self._watervolume_ncarray[0]
        elif self._watervolume_ramflag:
            self.watervolume = self._watervolume_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._watervolume_diskflag_writing:
            self._watervolume_ncarray[0] = self.watervolume
        if self._watervolume_ramflag:
            self._watervolume_array[idx] = self.watervolume
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "watervolume":
            self._watervolume_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._watervolume_outputflag:
            self._watervolume_outputpointer[0] = self.watervolume
@cython.final
cdef class LogSequences:
    cdef public double[:] loggedadjustedevaporation
    cdef public int _loggedadjustedevaporation_ndim
    cdef public int _loggedadjustedevaporation_length
    cdef public int _loggedadjustedevaporation_length_0
@cython.final
cdef class AideSequences:
    cdef public double surfacearea
    cdef public int _surfacearea_ndim
    cdef public int _surfacearea_length
    cdef public double[:] _surfacearea_points
    cdef public double[:] _surfacearea_results
    cdef public double alloweddischarge
    cdef public int _alloweddischarge_ndim
    cdef public int _alloweddischarge_length
    cdef public double[:] _alloweddischarge_points
    cdef public double[:] _alloweddischarge_results
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
cdef class NumConsts:
    cdef public numpy.int32_t nmb_methods
    cdef public numpy.int32_t nmb_stages
    cdef public double dt_increase
    cdef public double dt_decrease
    cdef public configutils.Config pub
    cdef public double[:, :, :] a_coefs
cdef class NumVars:
    cdef public bint use_relerror
    cdef public numpy.int32_t nmb_calls
    cdef public numpy.int32_t idx_method
    cdef public numpy.int32_t idx_stage
    cdef public double t0
    cdef public double t1
    cdef public double dt
    cdef public double dt_est
    cdef public double abserror
    cdef public double relerror
    cdef public double last_abserror
    cdef public double last_relerror
    cdef public double extrapolated_abserror
    cdef public double extrapolated_relerror
    cdef public bint f0_ready

@cython.final
cdef class Model:
    cdef public int idx_sim
    cdef public Parameters parameters
    cdef public Sequences sequences
    cdef public NumConsts numconsts
    cdef public NumVars numvars
    cpdef inline void simulate(self, int idx)  nogil:
        self.idx_sim = idx
        self.load_data()
        self.update_inlets()
        self.solve()
        self.update_outlets()
        self.update_outputs()
    cpdef inline void load_data(self) nogil:
        self.sequences.inputs.load_data(self.idx_sim)
    cpdef inline void save_data(self, int idx) nogil:
        self.sequences.inputs.save_data(self.idx_sim)
        self.sequences.factors.save_data(self.idx_sim)
        self.sequences.fluxes.save_data(self.idx_sim)
        self.sequences.states.save_data(self.idx_sim)
    cpdef inline void new2old(self) nogil:
        self.sequences.old_states.watervolume = self.sequences.new_states.watervolume
    cpdef inline void update_inlets(self) nogil:
        self.calc_adjustedevaporation_v1()
    cpdef inline void update_outlets(self) nogil:
        self.calc_waterlevel_v1()
        self.pass_outflow_v1()
    cpdef inline void update_receivers(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_senders(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_outputs(self) nogil:
        self.sequences.factors.update_outputs()
        self.sequences.fluxes.update_outputs()
        self.sequences.states.update_outputs()
    cpdef inline void solve(self)  nogil:
        cdef int decrease_dt
        self.numvars.use_relerror = not isnan(            self.parameters.solver.relerrormax        )
        self.numvars.t0, self.numvars.t1 = 0.0, 1.0
        self.numvars.dt_est = 1.0 * self.parameters.solver.reldtmax
        self.numvars.f0_ready = False
        self.reset_sum_fluxes()
        while self.numvars.t0 < self.numvars.t1 - 1e-14:
            self.numvars.last_abserror = inf
            self.numvars.last_relerror = inf
            self.numvars.dt = min(                self.numvars.t1 - self.numvars.t0,                1.0 * self.parameters.solver.reldtmax,                max(self.numvars.dt_est, self.parameters.solver.reldtmin),            )
            if not self.numvars.f0_ready:
                self.calculate_single_terms()
                self.numvars.idx_method = 0
                self.numvars.idx_stage = 0
                self.set_point_fluxes()
                self.set_point_states()
                self.set_result_states()
            for self.numvars.idx_method in range(1, self.numconsts.nmb_methods + 1):
                for self.numvars.idx_stage in range(1, self.numvars.idx_method):
                    self.get_point_states()
                    self.calculate_single_terms()
                    self.set_point_fluxes()
                for self.numvars.idx_stage in range(1, self.numvars.idx_method + 1):
                    self.integrate_fluxes()
                    self.calculate_full_terms()
                    self.set_point_states()
                self.set_result_fluxes()
                self.set_result_states()
                self.calculate_error()
                self.extrapolate_error()
                if self.numvars.idx_method == 1:
                    continue
                if (self.numvars.abserror <= self.parameters.solver.abserrormax) or (                    self.numvars.relerror <= self.parameters.solver.relerrormax                ):
                    self.numvars.dt_est = self.numconsts.dt_increase * self.numvars.dt
                    self.numvars.f0_ready = False
                    self.addup_fluxes()
                    self.numvars.t0 = self.numvars.t0 + self.numvars.dt
                    self.new2old()
                    break
                decrease_dt = self.numvars.dt > self.parameters.solver.reldtmin
                decrease_dt = decrease_dt and (                    self.numvars.extrapolated_abserror                    > self.parameters.solver.abserrormax                )
                if self.numvars.use_relerror:
                    decrease_dt = decrease_dt and (                        self.numvars.extrapolated_relerror                        > self.parameters.solver.relerrormax                    )
                if decrease_dt:
                    self.numvars.f0_ready = True
                    self.numvars.dt_est = self.numvars.dt / self.numconsts.dt_decrease
                    break
                self.numvars.last_abserror = self.numvars.abserror
                self.numvars.last_relerror = self.numvars.relerror
                self.numvars.f0_ready = True
            else:
                if self.numvars.dt <= self.parameters.solver.reldtmin:
                    self.numvars.f0_ready = False
                    self.addup_fluxes()
                    self.numvars.t0 = self.numvars.t0 + self.numvars.dt
                    self.new2old()
                else:
                    self.numvars.f0_ready = True
                    self.numvars.dt_est = self.numvars.dt / self.numconsts.dt_decrease
        self.get_sum_fluxes()
    cpdef inline void calculate_single_terms(self) nogil:
        self.numvars.nmb_calls = self.numvars.nmb_calls + 1
        self.calc_adjustedprecipitation_v1()
        self.pic_inflow_v1()
        self.calc_waterlevel_v1()
        self.calc_actualevaporation_v1()
        self.calc_surfacearea_v1()
        self.calc_alloweddischarge_v2()
        self.calc_actualrelease_v3()
        self.calc_flooddischarge_v1()
        self.calc_outflow_v1()
    cpdef inline void calculate_full_terms(self) nogil:
        self.update_watervolume_v1()
    cpdef inline void get_point_states(self) nogil:
        self.sequences.states.watervolume = self.sequences.states._watervolume_points[self.numvars.idx_stage]
    cpdef inline void set_point_states(self) nogil:
        self.sequences.states._watervolume_points[self.numvars.idx_stage] = self.sequences.states.watervolume
    cpdef inline void set_result_states(self) nogil:
        self.sequences.states._watervolume_results[self.numvars.idx_method] = self.sequences.states.watervolume
    cpdef inline void get_sum_fluxes(self) nogil:
        self.sequences.fluxes.adjustedprecipitation = self.sequences.fluxes._adjustedprecipitation_sum
        self.sequences.fluxes.actualevaporation = self.sequences.fluxes._actualevaporation_sum
        self.sequences.fluxes.inflow = self.sequences.fluxes._inflow_sum
        self.sequences.fluxes.actualrelease = self.sequences.fluxes._actualrelease_sum
        self.sequences.fluxes.flooddischarge = self.sequences.fluxes._flooddischarge_sum
        self.sequences.fluxes.outflow = self.sequences.fluxes._outflow_sum
    cpdef inline void set_point_fluxes(self) nogil:
        self.sequences.fluxes._adjustedprecipitation_points[self.numvars.idx_stage] = self.sequences.fluxes.adjustedprecipitation
        self.sequences.fluxes._actualevaporation_points[self.numvars.idx_stage] = self.sequences.fluxes.actualevaporation
        self.sequences.fluxes._inflow_points[self.numvars.idx_stage] = self.sequences.fluxes.inflow
        self.sequences.fluxes._actualrelease_points[self.numvars.idx_stage] = self.sequences.fluxes.actualrelease
        self.sequences.fluxes._flooddischarge_points[self.numvars.idx_stage] = self.sequences.fluxes.flooddischarge
        self.sequences.fluxes._outflow_points[self.numvars.idx_stage] = self.sequences.fluxes.outflow
    cpdef inline void set_result_fluxes(self) nogil:
        self.sequences.fluxes._adjustedprecipitation_results[self.numvars.idx_method] = self.sequences.fluxes.adjustedprecipitation
        self.sequences.fluxes._actualevaporation_results[self.numvars.idx_method] = self.sequences.fluxes.actualevaporation
        self.sequences.fluxes._inflow_results[self.numvars.idx_method] = self.sequences.fluxes.inflow
        self.sequences.fluxes._actualrelease_results[self.numvars.idx_method] = self.sequences.fluxes.actualrelease
        self.sequences.fluxes._flooddischarge_results[self.numvars.idx_method] = self.sequences.fluxes.flooddischarge
        self.sequences.fluxes._outflow_results[self.numvars.idx_method] = self.sequences.fluxes.outflow
    cpdef inline void integrate_fluxes(self) nogil:
        cdef int jdx
        self.sequences.fluxes.adjustedprecipitation = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.adjustedprecipitation = self.sequences.fluxes.adjustedprecipitation +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._adjustedprecipitation_points[jdx]
        self.sequences.fluxes.actualevaporation = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.actualevaporation = self.sequences.fluxes.actualevaporation +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._actualevaporation_points[jdx]
        self.sequences.fluxes.inflow = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._inflow_points[jdx]
        self.sequences.fluxes.actualrelease = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.actualrelease = self.sequences.fluxes.actualrelease +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._actualrelease_points[jdx]
        self.sequences.fluxes.flooddischarge = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.flooddischarge = self.sequences.fluxes.flooddischarge +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._flooddischarge_points[jdx]
        self.sequences.fluxes.outflow = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.outflow = self.sequences.fluxes.outflow +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._outflow_points[jdx]
    cpdef inline void reset_sum_fluxes(self) nogil:
        self.sequences.fluxes._adjustedprecipitation_sum = 0.
        self.sequences.fluxes._actualevaporation_sum = 0.
        self.sequences.fluxes._inflow_sum = 0.
        self.sequences.fluxes._actualrelease_sum = 0.
        self.sequences.fluxes._flooddischarge_sum = 0.
        self.sequences.fluxes._outflow_sum = 0.
    cpdef inline void addup_fluxes(self) nogil:
        self.sequences.fluxes._adjustedprecipitation_sum = self.sequences.fluxes._adjustedprecipitation_sum + self.sequences.fluxes.adjustedprecipitation
        self.sequences.fluxes._actualevaporation_sum = self.sequences.fluxes._actualevaporation_sum + self.sequences.fluxes.actualevaporation
        self.sequences.fluxes._inflow_sum = self.sequences.fluxes._inflow_sum + self.sequences.fluxes.inflow
        self.sequences.fluxes._actualrelease_sum = self.sequences.fluxes._actualrelease_sum + self.sequences.fluxes.actualrelease
        self.sequences.fluxes._flooddischarge_sum = self.sequences.fluxes._flooddischarge_sum + self.sequences.fluxes.flooddischarge
        self.sequences.fluxes._outflow_sum = self.sequences.fluxes._outflow_sum + self.sequences.fluxes.outflow
    cpdef inline void calculate_error(self) nogil:
        cdef double abserror
        self.numvars.abserror = 0.
        if self.numvars.use_relerror:
            self.numvars.relerror = 0.
        else:
            self.numvars.relerror = inf
        abserror = fabs(self.sequences.fluxes._adjustedprecipitation_results[self.numvars.idx_method]-self.sequences.fluxes._adjustedprecipitation_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._adjustedprecipitation_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._adjustedprecipitation_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._actualevaporation_results[self.numvars.idx_method]-self.sequences.fluxes._actualevaporation_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._actualevaporation_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._actualevaporation_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._inflow_results[self.numvars.idx_method]-self.sequences.fluxes._inflow_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._inflow_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._inflow_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._actualrelease_results[self.numvars.idx_method]-self.sequences.fluxes._actualrelease_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._actualrelease_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._actualrelease_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._flooddischarge_results[self.numvars.idx_method]-self.sequences.fluxes._flooddischarge_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._flooddischarge_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._flooddischarge_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._outflow_results[self.numvars.idx_method]-self.sequences.fluxes._outflow_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._outflow_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._outflow_results[self.numvars.idx_method]))
    cpdef inline void extrapolate_error(self)  nogil:
        if self.numvars.abserror <= 0.0:
            self.numvars.extrapolated_abserror = 0.0
            self.numvars.extrapolated_relerror = 0.0
        else:
            if self.numvars.idx_method > 2:
                self.numvars.extrapolated_abserror = exp(                    log(self.numvars.abserror)                    + (                        log(self.numvars.abserror)                        - log(self.numvars.last_abserror)                    )                    * (self.numconsts.nmb_methods - self.numvars.idx_method)                )
            else:
                self.numvars.extrapolated_abserror = -999.9
            if self.numvars.use_relerror:
                if self.numvars.idx_method > 2:
                    if isinf(self.numvars.relerror):
                        self.numvars.extrapolated_relerror = inf
                    else:
                        self.numvars.extrapolated_relerror = exp(                            log(self.numvars.relerror)                            + (                                log(self.numvars.relerror)                                - log(self.numvars.last_relerror)                            )                            * (self.numconsts.nmb_methods - self.numvars.idx_method)                        )
                else:
                    self.numvars.extrapolated_relerror = -999.9
            else:
                self.numvars.extrapolated_relerror = inf
    cpdef inline void calc_adjustedevaporation_v1(self)  nogil:
        cdef double d_old
        cdef double d_new
        cdef double d_weight
        d_weight = self.parameters.control.weightevaporation
        d_new = self.parameters.derived.inputfactor * self.parameters.control.correctionevaporation * self.sequences.inputs.evaporation
        d_old = self.sequences.logs.loggedadjustedevaporation[0]
        self.sequences.fluxes.adjustedevaporation = d_weight * d_new + (1.0 - d_weight) * d_old
        self.sequences.logs.loggedadjustedevaporation[0] = self.sequences.fluxes.adjustedevaporation
    cpdef inline void calc_adjustedevaporation(self)  nogil:
        cdef double d_old
        cdef double d_new
        cdef double d_weight
        d_weight = self.parameters.control.weightevaporation
        d_new = self.parameters.derived.inputfactor * self.parameters.control.correctionevaporation * self.sequences.inputs.evaporation
        d_old = self.sequences.logs.loggedadjustedevaporation[0]
        self.sequences.fluxes.adjustedevaporation = d_weight * d_new + (1.0 - d_weight) * d_old
        self.sequences.logs.loggedadjustedevaporation[0] = self.sequences.fluxes.adjustedevaporation
    cpdef inline void calc_adjustedprecipitation_v1(self)  nogil:
        self.sequences.fluxes.adjustedprecipitation = (            self.parameters.derived.inputfactor * self.parameters.control.correctionprecipitation * self.sequences.inputs.precipitation        )
    cpdef inline void pic_inflow_v1(self)  nogil:
        cdef int idx
        self.sequences.fluxes.inflow = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx][0])
    cpdef inline void calc_waterlevel_v1(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.sequences.factors.waterlevel = self.parameters.control.watervolume2waterlevel.outputs[0]
    cpdef inline void calc_actualevaporation_v1(self)  nogil:
        self.sequences.fluxes.actualevaporation = self.sequences.fluxes.adjustedevaporation * smoothutils.smooth_logistic1(            self.sequences.factors.waterlevel - self.parameters.control.thresholdevaporation, self.parameters.derived.smoothparevaporation        )
    cpdef inline void calc_surfacearea_v1(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.parameters.control.watervolume2waterlevel.calculate_derivatives(0)
        self.sequences.aides.surfacearea = 1.0 / self.parameters.control.watervolume2waterlevel.output_derivatives[0]
    cpdef inline void calc_alloweddischarge_v2(self)  nogil:
        self.sequences.aides.alloweddischarge = smoothutils.smooth_min1(            self.parameters.control.allowedwaterleveldrop / self.parameters.derived.seconds * self.sequences.aides.surfacearea * 1e6            + self.sequences.fluxes.inflow,            self.parameters.control.allowedrelease[self.parameters.derived.toy[self.idx_sim]],            self.parameters.derived.dischargesmoothpar,        )
    cpdef inline void calc_actualrelease_v3(self)  nogil:
        cdef double d_weight
        cdef double d_release2
        cdef double d_neutral
        cdef double d_release1
        cdef double d_upperbound
        cdef double d_factor
        cdef double d_qmax
        cdef double d_qmin
        cdef double d_range
        cdef double d_target
        cdef int idx_toy
        idx_toy = self.parameters.derived.toy[self.idx_sim]
        d_target = self.parameters.control.targetvolume[idx_toy]
        d_range = max(self.parameters.control.targetrangeabsolute, self.parameters.control.targetrangerelative * d_target)
        d_range = max(d_range, 1e-6)
        d_qmin = self.parameters.control.neardischargeminimumthreshold[idx_toy]
        d_qmax = smoothutils.smooth_max1(            d_qmin, self.sequences.aides.alloweddischarge, self.parameters.derived.dischargesmoothpar        )
        d_factor = smoothutils.smooth_logistic3(            (self.sequences.new_states.watervolume - d_target + d_range) / d_range,            self.parameters.derived.volumesmoothparlog2,        )
        d_upperbound = smoothutils.smooth_min1(            d_qmax, self.sequences.fluxes.inflow, self.parameters.derived.dischargesmoothpar        )
        d_release1 = (1.0 - d_factor) * d_qmin + d_factor * smoothutils.smooth_max1(            d_qmin,            d_upperbound,            self.parameters.derived.dischargesmoothpar,        )
        d_factor = smoothutils.smooth_logistic3(            (d_target + d_range - self.sequences.new_states.watervolume) / d_range,            self.parameters.derived.volumesmoothparlog2,        )
        d_neutral = smoothutils.smooth_max1(d_qmin, self.sequences.fluxes.inflow, self.parameters.derived.dischargesmoothpar)
        d_release2 = (1.0 - d_factor) * d_qmax + d_factor * smoothutils.smooth_min1(            d_qmax,            d_neutral,            self.parameters.derived.dischargesmoothpar,        )
        d_weight = smoothutils.smooth_logistic1(            d_target - self.sequences.new_states.watervolume, self.parameters.derived.volumesmoothparlog1        )
        self.sequences.fluxes.actualrelease = d_weight * d_release1 + (1.0 - d_weight) * d_release2
        if self.parameters.derived.volumesmoothparlog1 > 0.0:
            d_weight = exp(                -(((self.sequences.new_states.watervolume - d_target) / self.parameters.derived.volumesmoothparlog1) ** 2)            )
        else:
            d_weight = 0.0
        d_neutral = smoothutils.smooth_max1(            d_upperbound, d_qmin, self.parameters.derived.dischargesmoothpar        )
        self.sequences.fluxes.actualrelease = d_weight * d_neutral + (1.0 - d_weight) * self.sequences.fluxes.actualrelease
        self.sequences.fluxes.actualrelease = smoothutils.smooth_max1(            self.sequences.fluxes.actualrelease, 0.0, self.parameters.derived.dischargesmoothpar        )
        self.sequences.fluxes.actualrelease = self.sequences.fluxes.actualrelease * (smoothutils.smooth_logistic1(            self.sequences.new_states.watervolume - self.parameters.control.watervolumeminimumthreshold[idx_toy],            self.parameters.derived.volumesmoothparlog1,        ))
    cpdef inline void calc_flooddischarge_v1(self)  nogil:
        self.parameters.control.waterlevel2flooddischarge.inputs[0] = self.sequences.factors.waterlevel
        self.parameters.control.waterlevel2flooddischarge.calculate_values(self.parameters.derived.toy[self.idx_sim])
        self.sequences.fluxes.flooddischarge = self.parameters.control.waterlevel2flooddischarge.outputs[0]
    cpdef inline void calc_outflow_v1(self)  nogil:
        self.sequences.fluxes.outflow = max(self.sequences.fluxes.actualrelease + self.sequences.fluxes.flooddischarge, 0.0)
    cpdef inline void calc_adjustedprecipitation(self)  nogil:
        self.sequences.fluxes.adjustedprecipitation = (            self.parameters.derived.inputfactor * self.parameters.control.correctionprecipitation * self.sequences.inputs.precipitation        )
    cpdef inline void pic_inflow(self)  nogil:
        cdef int idx
        self.sequences.fluxes.inflow = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx][0])
    cpdef inline void calc_waterlevel(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.sequences.factors.waterlevel = self.parameters.control.watervolume2waterlevel.outputs[0]
    cpdef inline void calc_actualevaporation(self)  nogil:
        self.sequences.fluxes.actualevaporation = self.sequences.fluxes.adjustedevaporation * smoothutils.smooth_logistic1(            self.sequences.factors.waterlevel - self.parameters.control.thresholdevaporation, self.parameters.derived.smoothparevaporation        )
    cpdef inline void calc_surfacearea(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.parameters.control.watervolume2waterlevel.calculate_derivatives(0)
        self.sequences.aides.surfacearea = 1.0 / self.parameters.control.watervolume2waterlevel.output_derivatives[0]
    cpdef inline void calc_alloweddischarge(self)  nogil:
        self.sequences.aides.alloweddischarge = smoothutils.smooth_min1(            self.parameters.control.allowedwaterleveldrop / self.parameters.derived.seconds * self.sequences.aides.surfacearea * 1e6            + self.sequences.fluxes.inflow,            self.parameters.control.allowedrelease[self.parameters.derived.toy[self.idx_sim]],            self.parameters.derived.dischargesmoothpar,        )
    cpdef inline void calc_actualrelease(self)  nogil:
        cdef double d_weight
        cdef double d_release2
        cdef double d_neutral
        cdef double d_release1
        cdef double d_upperbound
        cdef double d_factor
        cdef double d_qmax
        cdef double d_qmin
        cdef double d_range
        cdef double d_target
        cdef int idx_toy
        idx_toy = self.parameters.derived.toy[self.idx_sim]
        d_target = self.parameters.control.targetvolume[idx_toy]
        d_range = max(self.parameters.control.targetrangeabsolute, self.parameters.control.targetrangerelative * d_target)
        d_range = max(d_range, 1e-6)
        d_qmin = self.parameters.control.neardischargeminimumthreshold[idx_toy]
        d_qmax = smoothutils.smooth_max1(            d_qmin, self.sequences.aides.alloweddischarge, self.parameters.derived.dischargesmoothpar        )
        d_factor = smoothutils.smooth_logistic3(            (self.sequences.new_states.watervolume - d_target + d_range) / d_range,            self.parameters.derived.volumesmoothparlog2,        )
        d_upperbound = smoothutils.smooth_min1(            d_qmax, self.sequences.fluxes.inflow, self.parameters.derived.dischargesmoothpar        )
        d_release1 = (1.0 - d_factor) * d_qmin + d_factor * smoothutils.smooth_max1(            d_qmin,            d_upperbound,            self.parameters.derived.dischargesmoothpar,        )
        d_factor = smoothutils.smooth_logistic3(            (d_target + d_range - self.sequences.new_states.watervolume) / d_range,            self.parameters.derived.volumesmoothparlog2,        )
        d_neutral = smoothutils.smooth_max1(d_qmin, self.sequences.fluxes.inflow, self.parameters.derived.dischargesmoothpar)
        d_release2 = (1.0 - d_factor) * d_qmax + d_factor * smoothutils.smooth_min1(            d_qmax,            d_neutral,            self.parameters.derived.dischargesmoothpar,        )
        d_weight = smoothutils.smooth_logistic1(            d_target - self.sequences.new_states.watervolume, self.parameters.derived.volumesmoothparlog1        )
        self.sequences.fluxes.actualrelease = d_weight * d_release1 + (1.0 - d_weight) * d_release2
        if self.parameters.derived.volumesmoothparlog1 > 0.0:
            d_weight = exp(                -(((self.sequences.new_states.watervolume - d_target) / self.parameters.derived.volumesmoothparlog1) ** 2)            )
        else:
            d_weight = 0.0
        d_neutral = smoothutils.smooth_max1(            d_upperbound, d_qmin, self.parameters.derived.dischargesmoothpar        )
        self.sequences.fluxes.actualrelease = d_weight * d_neutral + (1.0 - d_weight) * self.sequences.fluxes.actualrelease
        self.sequences.fluxes.actualrelease = smoothutils.smooth_max1(            self.sequences.fluxes.actualrelease, 0.0, self.parameters.derived.dischargesmoothpar        )
        self.sequences.fluxes.actualrelease = self.sequences.fluxes.actualrelease * (smoothutils.smooth_logistic1(            self.sequences.new_states.watervolume - self.parameters.control.watervolumeminimumthreshold[idx_toy],            self.parameters.derived.volumesmoothparlog1,        ))
    cpdef inline void calc_flooddischarge(self)  nogil:
        self.parameters.control.waterlevel2flooddischarge.inputs[0] = self.sequences.factors.waterlevel
        self.parameters.control.waterlevel2flooddischarge.calculate_values(self.parameters.derived.toy[self.idx_sim])
        self.sequences.fluxes.flooddischarge = self.parameters.control.waterlevel2flooddischarge.outputs[0]
    cpdef inline void calc_outflow(self)  nogil:
        self.sequences.fluxes.outflow = max(self.sequences.fluxes.actualrelease + self.sequences.fluxes.flooddischarge, 0.0)
    cpdef inline void update_watervolume_v1(self)  nogil:
        self.sequences.new_states.watervolume = self.sequences.old_states.watervolume + self.parameters.derived.seconds / 1e6 * (            self.sequences.fluxes.adjustedprecipitation - self.sequences.fluxes.actualevaporation + self.sequences.fluxes.inflow - self.sequences.fluxes.outflow        )
    cpdef inline void update_watervolume(self)  nogil:
        self.sequences.new_states.watervolume = self.sequences.old_states.watervolume + self.parameters.derived.seconds / 1e6 * (            self.sequences.fluxes.adjustedprecipitation - self.sequences.fluxes.actualevaporation + self.sequences.fluxes.inflow - self.sequences.fluxes.outflow        )
    cpdef inline void pass_outflow_v1(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
    cpdef inline void pass_outflow(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
