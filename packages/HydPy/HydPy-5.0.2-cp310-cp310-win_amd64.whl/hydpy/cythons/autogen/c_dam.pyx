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
    cdef public double surfacearea
    cdef public double catchmentarea
    cdef public numpy.int32_t nmblogentries
    cdef public double correctionprecipitation
    cdef public double correctionevaporation
    cdef public double weightevaporation
    cdef public double[:] remotedischargeminimum
    cdef public double[:] remotedischargesafety
    cdef public interputils.SimpleInterpolator waterlevel2possibleremoterelief
    cdef public double remoterelieftolerance
    cdef public double[:] neardischargeminimumthreshold
    cdef public double[:] neardischargeminimumtolerance
    cdef public bint restricttargetedrelease
    cdef public double[:] watervolumeminimumthreshold
    cdef public double waterlevelminimumthreshold
    cdef public double waterlevelminimumtolerance
    cdef public double thresholdevaporation
    cdef public double toleranceevaporation
    cdef public double waterlevelminimumremotethreshold
    cdef public double waterlevelminimumremotetolerance
    cdef public double[:] highestremoterelief
    cdef public double[:] waterlevelreliefthreshold
    cdef public double[:] waterlevelrelieftolerance
    cdef public double[:] highestremotesupply
    cdef public double[:] waterlevelsupplythreshold
    cdef public double[:] waterlevelsupplytolerance
    cdef public double highestremotedischarge
    cdef public double highestremotetolerance
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
    cdef public double[:] remotedischargesmoothpar
    cdef public double[:] neardischargeminimumsmoothpar1
    cdef public double[:] neardischargeminimumsmoothpar2
    cdef public double waterlevelminimumsmoothpar
    cdef public double smoothparevaporation
    cdef public double waterlevelminimumremotesmoothpar
    cdef public double[:] waterlevelreliefsmoothpar
    cdef public double[:] waterlevelsupplysmoothpar
    cdef public double highestremotesmoothpar
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
    cdef public ReceiverSequences receivers
    cdef public InputSequences inputs
    cdef public FactorSequences factors
    cdef public FluxSequences fluxes
    cdef public StateSequences states
    cdef public LogSequences logs
    cdef public AideSequences aides
    cdef public OutletSequences outlets
    cdef public SenderSequences senders
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
    cdef double *s
    cdef public int _s_ndim
    cdef public int _s_length
    cdef double *r
    cdef public int _r_ndim
    cdef public int _r_length
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "s":
            self.s = pointer.p_value
        if name == "r":
            self.r = pointer.p_value
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
        if name == "s":
            return self.s[0]
        if name == "r":
            return self.r[0]
    cpdef set_value(self, str name, value):
        if name == "q":
            for idx in range(self.len_q):
                pointerutils.check0(self._q_length_0)
                if self._q_ready[idx] == 0:
                    pointerutils.check1(self._q_length_0, idx)
                    pointerutils.check2(self._q_ready, idx)
                self.q[idx][0] = value[idx]
        if name == "s":
            self.s[0] = value
        if name == "r":
            self.r[0] = value
@cython.final
cdef class ReceiverSequences:
    cdef double *q
    cdef public int _q_ndim
    cdef public int _q_length
    cdef double *d
    cdef public int _d_ndim
    cdef public int _d_length
    cdef double *s
    cdef public int _s_ndim
    cdef public int _s_length
    cdef double *r
    cdef public int _r_ndim
    cdef public int _r_length
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "q":
            self.q = pointer.p_value
        if name == "d":
            self.d = pointer.p_value
        if name == "s":
            self.s = pointer.p_value
        if name == "r":
            self.r = pointer.p_value
    cpdef get_value(self, str name):
        cdef int idx
        if name == "q":
            return self.q[0]
        if name == "d":
            return self.d[0]
        if name == "s":
            return self.s[0]
        if name == "r":
            return self.r[0]
    cpdef set_value(self, str name, value):
        if name == "q":
            self.q[0] = value
        if name == "d":
            self.d[0] = value
        if name == "s":
            self.s[0] = value
        if name == "r":
            self.r[0] = value
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
    cdef public double exchange
    cdef public int _exchange_ndim
    cdef public int _exchange_length
    cdef public double[:] _exchange_points
    cdef public double[:] _exchange_results
    cdef public double[:] _exchange_integrals
    cdef public double _exchange_sum
    cdef public bint _exchange_ramflag
    cdef public double[:] _exchange_array
    cdef public bint _exchange_diskflag_reading
    cdef public bint _exchange_diskflag_writing
    cdef public double[:] _exchange_ncarray
    cdef public bint _exchange_outputflag
    cdef double *_exchange_outputpointer
    cdef public double totalremotedischarge
    cdef public int _totalremotedischarge_ndim
    cdef public int _totalremotedischarge_length
    cdef public bint _totalremotedischarge_ramflag
    cdef public double[:] _totalremotedischarge_array
    cdef public bint _totalremotedischarge_diskflag_reading
    cdef public bint _totalremotedischarge_diskflag_writing
    cdef public double[:] _totalremotedischarge_ncarray
    cdef public bint _totalremotedischarge_outputflag
    cdef double *_totalremotedischarge_outputpointer
    cdef public double naturalremotedischarge
    cdef public int _naturalremotedischarge_ndim
    cdef public int _naturalremotedischarge_length
    cdef public bint _naturalremotedischarge_ramflag
    cdef public double[:] _naturalremotedischarge_array
    cdef public bint _naturalremotedischarge_diskflag_reading
    cdef public bint _naturalremotedischarge_diskflag_writing
    cdef public double[:] _naturalremotedischarge_ncarray
    cdef public bint _naturalremotedischarge_outputflag
    cdef double *_naturalremotedischarge_outputpointer
    cdef public double remotedemand
    cdef public int _remotedemand_ndim
    cdef public int _remotedemand_length
    cdef public bint _remotedemand_ramflag
    cdef public double[:] _remotedemand_array
    cdef public bint _remotedemand_diskflag_reading
    cdef public bint _remotedemand_diskflag_writing
    cdef public double[:] _remotedemand_ncarray
    cdef public bint _remotedemand_outputflag
    cdef double *_remotedemand_outputpointer
    cdef public double remotefailure
    cdef public int _remotefailure_ndim
    cdef public int _remotefailure_length
    cdef public bint _remotefailure_ramflag
    cdef public double[:] _remotefailure_array
    cdef public bint _remotefailure_diskflag_reading
    cdef public bint _remotefailure_diskflag_writing
    cdef public double[:] _remotefailure_ncarray
    cdef public bint _remotefailure_outputflag
    cdef double *_remotefailure_outputpointer
    cdef public double requiredremoterelease
    cdef public int _requiredremoterelease_ndim
    cdef public int _requiredremoterelease_length
    cdef public bint _requiredremoterelease_ramflag
    cdef public double[:] _requiredremoterelease_array
    cdef public bint _requiredremoterelease_diskflag_reading
    cdef public bint _requiredremoterelease_diskflag_writing
    cdef public double[:] _requiredremoterelease_ncarray
    cdef public bint _requiredremoterelease_outputflag
    cdef double *_requiredremoterelease_outputpointer
    cdef public double allowedremoterelief
    cdef public int _allowedremoterelief_ndim
    cdef public int _allowedremoterelief_length
    cdef public bint _allowedremoterelief_ramflag
    cdef public double[:] _allowedremoterelief_array
    cdef public bint _allowedremoterelief_diskflag_reading
    cdef public bint _allowedremoterelief_diskflag_writing
    cdef public double[:] _allowedremoterelief_ncarray
    cdef public bint _allowedremoterelief_outputflag
    cdef double *_allowedremoterelief_outputpointer
    cdef public double requiredremotesupply
    cdef public int _requiredremotesupply_ndim
    cdef public int _requiredremotesupply_length
    cdef public bint _requiredremotesupply_ramflag
    cdef public double[:] _requiredremotesupply_array
    cdef public bint _requiredremotesupply_diskflag_reading
    cdef public bint _requiredremotesupply_diskflag_writing
    cdef public double[:] _requiredremotesupply_ncarray
    cdef public bint _requiredremotesupply_outputflag
    cdef double *_requiredremotesupply_outputpointer
    cdef public double possibleremoterelief
    cdef public int _possibleremoterelief_ndim
    cdef public int _possibleremoterelief_length
    cdef public double[:] _possibleremoterelief_points
    cdef public double[:] _possibleremoterelief_results
    cdef public double[:] _possibleremoterelief_integrals
    cdef public double _possibleremoterelief_sum
    cdef public bint _possibleremoterelief_ramflag
    cdef public double[:] _possibleremoterelief_array
    cdef public bint _possibleremoterelief_diskflag_reading
    cdef public bint _possibleremoterelief_diskflag_writing
    cdef public double[:] _possibleremoterelief_ncarray
    cdef public bint _possibleremoterelief_outputflag
    cdef double *_possibleremoterelief_outputpointer
    cdef public double actualremoterelief
    cdef public int _actualremoterelief_ndim
    cdef public int _actualremoterelief_length
    cdef public double[:] _actualremoterelief_points
    cdef public double[:] _actualremoterelief_results
    cdef public double[:] _actualremoterelief_integrals
    cdef public double _actualremoterelief_sum
    cdef public bint _actualremoterelief_ramflag
    cdef public double[:] _actualremoterelief_array
    cdef public bint _actualremoterelief_diskflag_reading
    cdef public bint _actualremoterelief_diskflag_writing
    cdef public double[:] _actualremoterelief_ncarray
    cdef public bint _actualremoterelief_outputflag
    cdef double *_actualremoterelief_outputpointer
    cdef public double requiredrelease
    cdef public int _requiredrelease_ndim
    cdef public int _requiredrelease_length
    cdef public bint _requiredrelease_ramflag
    cdef public double[:] _requiredrelease_array
    cdef public bint _requiredrelease_diskflag_reading
    cdef public bint _requiredrelease_diskflag_writing
    cdef public double[:] _requiredrelease_ncarray
    cdef public bint _requiredrelease_outputflag
    cdef double *_requiredrelease_outputpointer
    cdef public double targetedrelease
    cdef public int _targetedrelease_ndim
    cdef public int _targetedrelease_length
    cdef public bint _targetedrelease_ramflag
    cdef public double[:] _targetedrelease_array
    cdef public bint _targetedrelease_diskflag_reading
    cdef public bint _targetedrelease_diskflag_writing
    cdef public double[:] _targetedrelease_ncarray
    cdef public bint _targetedrelease_outputflag
    cdef double *_targetedrelease_outputpointer
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
    cdef public double missingremoterelease
    cdef public int _missingremoterelease_ndim
    cdef public int _missingremoterelease_length
    cdef public bint _missingremoterelease_ramflag
    cdef public double[:] _missingremoterelease_array
    cdef public bint _missingremoterelease_diskflag_reading
    cdef public bint _missingremoterelease_diskflag_writing
    cdef public double[:] _missingremoterelease_ncarray
    cdef public bint _missingremoterelease_outputflag
    cdef double *_missingremoterelease_outputpointer
    cdef public double actualremoterelease
    cdef public int _actualremoterelease_ndim
    cdef public int _actualremoterelease_length
    cdef public double[:] _actualremoterelease_points
    cdef public double[:] _actualremoterelease_results
    cdef public double[:] _actualremoterelease_integrals
    cdef public double _actualremoterelease_sum
    cdef public bint _actualremoterelease_ramflag
    cdef public double[:] _actualremoterelease_array
    cdef public bint _actualremoterelease_diskflag_reading
    cdef public bint _actualremoterelease_diskflag_writing
    cdef public double[:] _actualremoterelease_ncarray
    cdef public bint _actualremoterelease_outputflag
    cdef double *_actualremoterelease_outputpointer
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
        if self._exchange_diskflag_reading:
            self.exchange = self._exchange_ncarray[0]
        elif self._exchange_ramflag:
            self.exchange = self._exchange_array[idx]
        if self._totalremotedischarge_diskflag_reading:
            self.totalremotedischarge = self._totalremotedischarge_ncarray[0]
        elif self._totalremotedischarge_ramflag:
            self.totalremotedischarge = self._totalremotedischarge_array[idx]
        if self._naturalremotedischarge_diskflag_reading:
            self.naturalremotedischarge = self._naturalremotedischarge_ncarray[0]
        elif self._naturalremotedischarge_ramflag:
            self.naturalremotedischarge = self._naturalremotedischarge_array[idx]
        if self._remotedemand_diskflag_reading:
            self.remotedemand = self._remotedemand_ncarray[0]
        elif self._remotedemand_ramflag:
            self.remotedemand = self._remotedemand_array[idx]
        if self._remotefailure_diskflag_reading:
            self.remotefailure = self._remotefailure_ncarray[0]
        elif self._remotefailure_ramflag:
            self.remotefailure = self._remotefailure_array[idx]
        if self._requiredremoterelease_diskflag_reading:
            self.requiredremoterelease = self._requiredremoterelease_ncarray[0]
        elif self._requiredremoterelease_ramflag:
            self.requiredremoterelease = self._requiredremoterelease_array[idx]
        if self._allowedremoterelief_diskflag_reading:
            self.allowedremoterelief = self._allowedremoterelief_ncarray[0]
        elif self._allowedremoterelief_ramflag:
            self.allowedremoterelief = self._allowedremoterelief_array[idx]
        if self._requiredremotesupply_diskflag_reading:
            self.requiredremotesupply = self._requiredremotesupply_ncarray[0]
        elif self._requiredremotesupply_ramflag:
            self.requiredremotesupply = self._requiredremotesupply_array[idx]
        if self._possibleremoterelief_diskflag_reading:
            self.possibleremoterelief = self._possibleremoterelief_ncarray[0]
        elif self._possibleremoterelief_ramflag:
            self.possibleremoterelief = self._possibleremoterelief_array[idx]
        if self._actualremoterelief_diskflag_reading:
            self.actualremoterelief = self._actualremoterelief_ncarray[0]
        elif self._actualremoterelief_ramflag:
            self.actualremoterelief = self._actualremoterelief_array[idx]
        if self._requiredrelease_diskflag_reading:
            self.requiredrelease = self._requiredrelease_ncarray[0]
        elif self._requiredrelease_ramflag:
            self.requiredrelease = self._requiredrelease_array[idx]
        if self._targetedrelease_diskflag_reading:
            self.targetedrelease = self._targetedrelease_ncarray[0]
        elif self._targetedrelease_ramflag:
            self.targetedrelease = self._targetedrelease_array[idx]
        if self._actualrelease_diskflag_reading:
            self.actualrelease = self._actualrelease_ncarray[0]
        elif self._actualrelease_ramflag:
            self.actualrelease = self._actualrelease_array[idx]
        if self._missingremoterelease_diskflag_reading:
            self.missingremoterelease = self._missingremoterelease_ncarray[0]
        elif self._missingremoterelease_ramflag:
            self.missingremoterelease = self._missingremoterelease_array[idx]
        if self._actualremoterelease_diskflag_reading:
            self.actualremoterelease = self._actualremoterelease_ncarray[0]
        elif self._actualremoterelease_ramflag:
            self.actualremoterelease = self._actualremoterelease_array[idx]
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
        if self._exchange_diskflag_writing:
            self._exchange_ncarray[0] = self.exchange
        if self._exchange_ramflag:
            self._exchange_array[idx] = self.exchange
        if self._totalremotedischarge_diskflag_writing:
            self._totalremotedischarge_ncarray[0] = self.totalremotedischarge
        if self._totalremotedischarge_ramflag:
            self._totalremotedischarge_array[idx] = self.totalremotedischarge
        if self._naturalremotedischarge_diskflag_writing:
            self._naturalremotedischarge_ncarray[0] = self.naturalremotedischarge
        if self._naturalremotedischarge_ramflag:
            self._naturalremotedischarge_array[idx] = self.naturalremotedischarge
        if self._remotedemand_diskflag_writing:
            self._remotedemand_ncarray[0] = self.remotedemand
        if self._remotedemand_ramflag:
            self._remotedemand_array[idx] = self.remotedemand
        if self._remotefailure_diskflag_writing:
            self._remotefailure_ncarray[0] = self.remotefailure
        if self._remotefailure_ramflag:
            self._remotefailure_array[idx] = self.remotefailure
        if self._requiredremoterelease_diskflag_writing:
            self._requiredremoterelease_ncarray[0] = self.requiredremoterelease
        if self._requiredremoterelease_ramflag:
            self._requiredremoterelease_array[idx] = self.requiredremoterelease
        if self._allowedremoterelief_diskflag_writing:
            self._allowedremoterelief_ncarray[0] = self.allowedremoterelief
        if self._allowedremoterelief_ramflag:
            self._allowedremoterelief_array[idx] = self.allowedremoterelief
        if self._requiredremotesupply_diskflag_writing:
            self._requiredremotesupply_ncarray[0] = self.requiredremotesupply
        if self._requiredremotesupply_ramflag:
            self._requiredremotesupply_array[idx] = self.requiredremotesupply
        if self._possibleremoterelief_diskflag_writing:
            self._possibleremoterelief_ncarray[0] = self.possibleremoterelief
        if self._possibleremoterelief_ramflag:
            self._possibleremoterelief_array[idx] = self.possibleremoterelief
        if self._actualremoterelief_diskflag_writing:
            self._actualremoterelief_ncarray[0] = self.actualremoterelief
        if self._actualremoterelief_ramflag:
            self._actualremoterelief_array[idx] = self.actualremoterelief
        if self._requiredrelease_diskflag_writing:
            self._requiredrelease_ncarray[0] = self.requiredrelease
        if self._requiredrelease_ramflag:
            self._requiredrelease_array[idx] = self.requiredrelease
        if self._targetedrelease_diskflag_writing:
            self._targetedrelease_ncarray[0] = self.targetedrelease
        if self._targetedrelease_ramflag:
            self._targetedrelease_array[idx] = self.targetedrelease
        if self._actualrelease_diskflag_writing:
            self._actualrelease_ncarray[0] = self.actualrelease
        if self._actualrelease_ramflag:
            self._actualrelease_array[idx] = self.actualrelease
        if self._missingremoterelease_diskflag_writing:
            self._missingremoterelease_ncarray[0] = self.missingremoterelease
        if self._missingremoterelease_ramflag:
            self._missingremoterelease_array[idx] = self.missingremoterelease
        if self._actualremoterelease_diskflag_writing:
            self._actualremoterelease_ncarray[0] = self.actualremoterelease
        if self._actualremoterelease_ramflag:
            self._actualremoterelease_array[idx] = self.actualremoterelease
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
        if name == "exchange":
            self._exchange_outputpointer = value.p_value
        if name == "totalremotedischarge":
            self._totalremotedischarge_outputpointer = value.p_value
        if name == "naturalremotedischarge":
            self._naturalremotedischarge_outputpointer = value.p_value
        if name == "remotedemand":
            self._remotedemand_outputpointer = value.p_value
        if name == "remotefailure":
            self._remotefailure_outputpointer = value.p_value
        if name == "requiredremoterelease":
            self._requiredremoterelease_outputpointer = value.p_value
        if name == "allowedremoterelief":
            self._allowedremoterelief_outputpointer = value.p_value
        if name == "requiredremotesupply":
            self._requiredremotesupply_outputpointer = value.p_value
        if name == "possibleremoterelief":
            self._possibleremoterelief_outputpointer = value.p_value
        if name == "actualremoterelief":
            self._actualremoterelief_outputpointer = value.p_value
        if name == "requiredrelease":
            self._requiredrelease_outputpointer = value.p_value
        if name == "targetedrelease":
            self._targetedrelease_outputpointer = value.p_value
        if name == "actualrelease":
            self._actualrelease_outputpointer = value.p_value
        if name == "missingremoterelease":
            self._missingremoterelease_outputpointer = value.p_value
        if name == "actualremoterelease":
            self._actualremoterelease_outputpointer = value.p_value
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
        if self._exchange_outputflag:
            self._exchange_outputpointer[0] = self.exchange
        if self._totalremotedischarge_outputflag:
            self._totalremotedischarge_outputpointer[0] = self.totalremotedischarge
        if self._naturalremotedischarge_outputflag:
            self._naturalremotedischarge_outputpointer[0] = self.naturalremotedischarge
        if self._remotedemand_outputflag:
            self._remotedemand_outputpointer[0] = self.remotedemand
        if self._remotefailure_outputflag:
            self._remotefailure_outputpointer[0] = self.remotefailure
        if self._requiredremoterelease_outputflag:
            self._requiredremoterelease_outputpointer[0] = self.requiredremoterelease
        if self._allowedremoterelief_outputflag:
            self._allowedremoterelief_outputpointer[0] = self.allowedremoterelief
        if self._requiredremotesupply_outputflag:
            self._requiredremotesupply_outputpointer[0] = self.requiredremotesupply
        if self._possibleremoterelief_outputflag:
            self._possibleremoterelief_outputpointer[0] = self.possibleremoterelief
        if self._actualremoterelief_outputflag:
            self._actualremoterelief_outputpointer[0] = self.actualremoterelief
        if self._requiredrelease_outputflag:
            self._requiredrelease_outputpointer[0] = self.requiredrelease
        if self._targetedrelease_outputflag:
            self._targetedrelease_outputpointer[0] = self.targetedrelease
        if self._actualrelease_outputflag:
            self._actualrelease_outputpointer[0] = self.actualrelease
        if self._missingremoterelease_outputflag:
            self._missingremoterelease_outputpointer[0] = self.missingremoterelease
        if self._actualremoterelease_outputflag:
            self._actualremoterelease_outputpointer[0] = self.actualremoterelease
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
    cdef public double[:] loggedtotalremotedischarge
    cdef public int _loggedtotalremotedischarge_ndim
    cdef public int _loggedtotalremotedischarge_length
    cdef public int _loggedtotalremotedischarge_length_0
    cdef public double[:] loggedoutflow
    cdef public int _loggedoutflow_ndim
    cdef public int _loggedoutflow_length
    cdef public int _loggedoutflow_length_0
    cdef public double[:] loggedadjustedevaporation
    cdef public int _loggedadjustedevaporation_ndim
    cdef public int _loggedadjustedevaporation_length
    cdef public int _loggedadjustedevaporation_length_0
    cdef public double[:] loggedrequiredremoterelease
    cdef public int _loggedrequiredremoterelease_ndim
    cdef public int _loggedrequiredremoterelease_length
    cdef public int _loggedrequiredremoterelease_length_0
    cdef public double[:] loggedallowedremoterelief
    cdef public int _loggedallowedremoterelief_ndim
    cdef public int _loggedallowedremoterelief_length
    cdef public int _loggedallowedremoterelief_length_0
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
    cdef double *s
    cdef public int _s_ndim
    cdef public int _s_length
    cdef double *r
    cdef public int _r_ndim
    cdef public int _r_length
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "q":
            self.q = pointer.p_value
        if name == "s":
            self.s = pointer.p_value
        if name == "r":
            self.r = pointer.p_value
    cpdef get_value(self, str name):
        cdef int idx
        if name == "q":
            return self.q[0]
        if name == "s":
            return self.s[0]
        if name == "r":
            return self.r[0]
    cpdef set_value(self, str name, value):
        if name == "q":
            self.q[0] = value
        if name == "s":
            self.s[0] = value
        if name == "r":
            self.r[0] = value
@cython.final
cdef class SenderSequences:
    cdef double *d
    cdef public int _d_ndim
    cdef public int _d_length
    cdef double *s
    cdef public int _s_ndim
    cdef public int _s_length
    cdef double *r
    cdef public int _r_ndim
    cdef public int _r_length
    cpdef inline set_pointer0d(self, str name, pointerutils.Double value):
        cdef pointerutils.PDouble pointer = pointerutils.PDouble(value)
        if name == "d":
            self.d = pointer.p_value
        if name == "s":
            self.s = pointer.p_value
        if name == "r":
            self.r = pointer.p_value
    cpdef get_value(self, str name):
        cdef int idx
        if name == "d":
            return self.d[0]
        if name == "s":
            return self.s[0]
        if name == "r":
            return self.r[0]
    cpdef set_value(self, str name, value):
        if name == "d":
            self.d[0] = value
        if name == "s":
            self.s[0] = value
        if name == "r":
            self.r[0] = value
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
        self.calc_adjustedprecipitation_v1()
        self.calc_adjustedevaporation_v1()
        self.calc_actualevaporation_v1()
        self.pic_inflow_v1()
        self.pic_inflow_v2()
        self.calc_naturalremotedischarge_v1()
        self.calc_remotedemand_v1()
        self.calc_remotefailure_v1()
        self.calc_requiredremoterelease_v1()
        self.calc_requiredrelease_v1()
        self.calc_requiredrelease_v2()
        self.calc_targetedrelease_v1()
    cpdef inline void update_outlets(self) nogil:
        self.pass_outflow_v1()
        self.update_loggedoutflow_v1()
        self.pass_actualremoterelease_v1()
        self.pass_actualremoterelief_v1()
    cpdef inline void update_receivers(self, int idx) nogil:
        self.idx_sim = idx
        self.pic_totalremotedischarge_v1()
        self.update_loggedtotalremotedischarge_v1()
        self.pic_loggedrequiredremoterelease_v1()
        self.pic_loggedrequiredremoterelease_v2()
        self.calc_requiredremoterelease_v2()
        self.pic_loggedallowedremoterelief_v1()
        self.calc_allowedremoterelief_v1()
    cpdef inline void update_senders(self, int idx) nogil:
        self.idx_sim = idx
        self.calc_missingremoterelease_v1()
        self.pass_missingremoterelease_v1()
        self.calc_allowedremoterelief_v2()
        self.pass_allowedremoterelief_v1()
        self.calc_requiredremotesupply_v1()
        self.pass_requiredremotesupply_v1()
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
        self.pic_inflow_v1()
        self.pic_inflow_v2()
        self.calc_waterlevel_v1()
        self.calc_surfacearea_v1()
        self.calc_alloweddischarge_v1()
        self.calc_alloweddischarge_v2()
        self.calc_actualrelease_v1()
        self.calc_actualrelease_v2()
        self.calc_actualrelease_v3()
        self.calc_possibleremoterelief_v1()
        self.calc_actualremoterelief_v1()
        self.calc_actualremoterelease_v1()
        self.update_actualremoterelief_v1()
        self.update_actualremoterelease_v1()
        self.calc_flooddischarge_v1()
        self.calc_outflow_v1()
        self.calc_outflow_v2()
    cpdef inline void calculate_full_terms(self) nogil:
        self.update_watervolume_v1()
        self.update_watervolume_v2()
        self.update_watervolume_v3()
        self.update_watervolume_v4()
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
        self.sequences.fluxes.exchange = self.sequences.fluxes._exchange_sum
        self.sequences.fluxes.possibleremoterelief = self.sequences.fluxes._possibleremoterelief_sum
        self.sequences.fluxes.actualremoterelief = self.sequences.fluxes._actualremoterelief_sum
        self.sequences.fluxes.actualrelease = self.sequences.fluxes._actualrelease_sum
        self.sequences.fluxes.actualremoterelease = self.sequences.fluxes._actualremoterelease_sum
        self.sequences.fluxes.flooddischarge = self.sequences.fluxes._flooddischarge_sum
        self.sequences.fluxes.outflow = self.sequences.fluxes._outflow_sum
    cpdef inline void set_point_fluxes(self) nogil:
        self.sequences.fluxes._adjustedprecipitation_points[self.numvars.idx_stage] = self.sequences.fluxes.adjustedprecipitation
        self.sequences.fluxes._actualevaporation_points[self.numvars.idx_stage] = self.sequences.fluxes.actualevaporation
        self.sequences.fluxes._inflow_points[self.numvars.idx_stage] = self.sequences.fluxes.inflow
        self.sequences.fluxes._exchange_points[self.numvars.idx_stage] = self.sequences.fluxes.exchange
        self.sequences.fluxes._possibleremoterelief_points[self.numvars.idx_stage] = self.sequences.fluxes.possibleremoterelief
        self.sequences.fluxes._actualremoterelief_points[self.numvars.idx_stage] = self.sequences.fluxes.actualremoterelief
        self.sequences.fluxes._actualrelease_points[self.numvars.idx_stage] = self.sequences.fluxes.actualrelease
        self.sequences.fluxes._actualremoterelease_points[self.numvars.idx_stage] = self.sequences.fluxes.actualremoterelease
        self.sequences.fluxes._flooddischarge_points[self.numvars.idx_stage] = self.sequences.fluxes.flooddischarge
        self.sequences.fluxes._outflow_points[self.numvars.idx_stage] = self.sequences.fluxes.outflow
    cpdef inline void set_result_fluxes(self) nogil:
        self.sequences.fluxes._adjustedprecipitation_results[self.numvars.idx_method] = self.sequences.fluxes.adjustedprecipitation
        self.sequences.fluxes._actualevaporation_results[self.numvars.idx_method] = self.sequences.fluxes.actualevaporation
        self.sequences.fluxes._inflow_results[self.numvars.idx_method] = self.sequences.fluxes.inflow
        self.sequences.fluxes._exchange_results[self.numvars.idx_method] = self.sequences.fluxes.exchange
        self.sequences.fluxes._possibleremoterelief_results[self.numvars.idx_method] = self.sequences.fluxes.possibleremoterelief
        self.sequences.fluxes._actualremoterelief_results[self.numvars.idx_method] = self.sequences.fluxes.actualremoterelief
        self.sequences.fluxes._actualrelease_results[self.numvars.idx_method] = self.sequences.fluxes.actualrelease
        self.sequences.fluxes._actualremoterelease_results[self.numvars.idx_method] = self.sequences.fluxes.actualremoterelease
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
        self.sequences.fluxes.exchange = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.exchange = self.sequences.fluxes.exchange +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._exchange_points[jdx]
        self.sequences.fluxes.possibleremoterelief = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.possibleremoterelief = self.sequences.fluxes.possibleremoterelief +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._possibleremoterelief_points[jdx]
        self.sequences.fluxes.actualremoterelief = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.actualremoterelief = self.sequences.fluxes.actualremoterelief +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._actualremoterelief_points[jdx]
        self.sequences.fluxes.actualrelease = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.actualrelease = self.sequences.fluxes.actualrelease +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._actualrelease_points[jdx]
        self.sequences.fluxes.actualremoterelease = 0.
        for jdx in range(self.numvars.idx_method):
            self.sequences.fluxes.actualremoterelease = self.sequences.fluxes.actualremoterelease +self.numvars.dt * self.numconsts.a_coefs[self.numvars.idx_method-1, self.numvars.idx_stage, jdx]*self.sequences.fluxes._actualremoterelease_points[jdx]
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
        self.sequences.fluxes._exchange_sum = 0.
        self.sequences.fluxes._possibleremoterelief_sum = 0.
        self.sequences.fluxes._actualremoterelief_sum = 0.
        self.sequences.fluxes._actualrelease_sum = 0.
        self.sequences.fluxes._actualremoterelease_sum = 0.
        self.sequences.fluxes._flooddischarge_sum = 0.
        self.sequences.fluxes._outflow_sum = 0.
    cpdef inline void addup_fluxes(self) nogil:
        self.sequences.fluxes._adjustedprecipitation_sum = self.sequences.fluxes._adjustedprecipitation_sum + self.sequences.fluxes.adjustedprecipitation
        self.sequences.fluxes._actualevaporation_sum = self.sequences.fluxes._actualevaporation_sum + self.sequences.fluxes.actualevaporation
        self.sequences.fluxes._inflow_sum = self.sequences.fluxes._inflow_sum + self.sequences.fluxes.inflow
        self.sequences.fluxes._exchange_sum = self.sequences.fluxes._exchange_sum + self.sequences.fluxes.exchange
        self.sequences.fluxes._possibleremoterelief_sum = self.sequences.fluxes._possibleremoterelief_sum + self.sequences.fluxes.possibleremoterelief
        self.sequences.fluxes._actualremoterelief_sum = self.sequences.fluxes._actualremoterelief_sum + self.sequences.fluxes.actualremoterelief
        self.sequences.fluxes._actualrelease_sum = self.sequences.fluxes._actualrelease_sum + self.sequences.fluxes.actualrelease
        self.sequences.fluxes._actualremoterelease_sum = self.sequences.fluxes._actualremoterelease_sum + self.sequences.fluxes.actualremoterelease
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
        abserror = fabs(self.sequences.fluxes._exchange_results[self.numvars.idx_method]-self.sequences.fluxes._exchange_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._exchange_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._exchange_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._possibleremoterelief_results[self.numvars.idx_method]-self.sequences.fluxes._possibleremoterelief_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._possibleremoterelief_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._possibleremoterelief_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._actualremoterelief_results[self.numvars.idx_method]-self.sequences.fluxes._actualremoterelief_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._actualremoterelief_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._actualremoterelief_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._actualrelease_results[self.numvars.idx_method]-self.sequences.fluxes._actualrelease_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._actualrelease_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._actualrelease_results[self.numvars.idx_method]))
        abserror = fabs(self.sequences.fluxes._actualremoterelease_results[self.numvars.idx_method]-self.sequences.fluxes._actualremoterelease_results[self.numvars.idx_method-1])
        self.numvars.abserror = max(self.numvars.abserror, abserror)
        if self.numvars.use_relerror:
            if self.sequences.fluxes._actualremoterelease_results[self.numvars.idx_method] == 0.:
                self.numvars.relerror = inf
            else:
                self.numvars.relerror = max(self.numvars.relerror, fabs(abserror/self.sequences.fluxes._actualremoterelease_results[self.numvars.idx_method]))
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
    cpdef inline void pic_totalremotedischarge_v1(self)  nogil:
        self.sequences.fluxes.totalremotedischarge = self.sequences.receivers.q[0]
    cpdef inline void update_loggedtotalremotedischarge_v1(self)  nogil:
        cdef int i
        for i in range(self.parameters.control.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedtotalremotedischarge[i] = self.sequences.logs.loggedtotalremotedischarge[i - 1]
        self.sequences.logs.loggedtotalremotedischarge[0] = self.sequences.fluxes.totalremotedischarge
    cpdef inline void pic_loggedrequiredremoterelease_v1(self)  nogil:
        self.sequences.logs.loggedrequiredremoterelease[0] = self.sequences.receivers.d[0]
    cpdef inline void pic_loggedrequiredremoterelease_v2(self)  nogil:
        self.sequences.logs.loggedrequiredremoterelease[0] = self.sequences.receivers.s[0]
    cpdef inline void calc_requiredremoterelease_v2(self)  nogil:
        self.sequences.fluxes.requiredremoterelease = self.sequences.logs.loggedrequiredremoterelease[0]
    cpdef inline void pic_loggedallowedremoterelief_v1(self)  nogil:
        self.sequences.logs.loggedallowedremoterelief[0] = self.sequences.receivers.r[0]
    cpdef inline void calc_allowedremoterelief_v1(self)  nogil:
        self.sequences.fluxes.allowedremoterelief = self.sequences.logs.loggedallowedremoterelief[0]
    cpdef inline void pic_totalremotedischarge(self)  nogil:
        self.sequences.fluxes.totalremotedischarge = self.sequences.receivers.q[0]
    cpdef inline void update_loggedtotalremotedischarge(self)  nogil:
        cdef int i
        for i in range(self.parameters.control.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedtotalremotedischarge[i] = self.sequences.logs.loggedtotalremotedischarge[i - 1]
        self.sequences.logs.loggedtotalremotedischarge[0] = self.sequences.fluxes.totalremotedischarge
    cpdef inline void calc_requiredremoterelease(self)  nogil:
        self.sequences.fluxes.requiredremoterelease = self.sequences.fluxes.remotedemand + (            smoothutils.smooth_logistic1(                self.sequences.fluxes.remotefailure,                self.parameters.derived.remotedischargesmoothpar[self.parameters.derived.toy[self.idx_sim]],            )            * self.parameters.control.remotedischargesafety[self.parameters.derived.toy[self.idx_sim]]        )
    cpdef inline void pic_loggedallowedremoterelief(self)  nogil:
        self.sequences.logs.loggedallowedremoterelief[0] = self.sequences.receivers.r[0]
    cpdef inline void calc_allowedremoterelief(self)  nogil:
        cdef int toy
        toy = self.parameters.derived.toy[self.idx_sim]
        self.sequences.fluxes.allowedremoterelief = (            smoothutils.smooth_logistic1(                self.parameters.control.waterlevelreliefthreshold[toy] - self.sequences.factors.waterlevel,                self.parameters.derived.waterlevelreliefsmoothpar[toy],            )            * self.parameters.control.highestremoterelief[toy]        )
    cpdef inline void calc_adjustedprecipitation_v1(self)  nogil:
        self.sequences.fluxes.adjustedprecipitation = (            self.parameters.derived.inputfactor * self.parameters.control.correctionprecipitation * self.sequences.inputs.precipitation        )
    cpdef inline void calc_adjustedevaporation_v1(self)  nogil:
        cdef double d_old
        cdef double d_new
        cdef double d_weight
        d_weight = self.parameters.control.weightevaporation
        d_new = self.parameters.derived.inputfactor * self.parameters.control.correctionevaporation * self.sequences.inputs.evaporation
        d_old = self.sequences.logs.loggedadjustedevaporation[0]
        self.sequences.fluxes.adjustedevaporation = d_weight * d_new + (1.0 - d_weight) * d_old
        self.sequences.logs.loggedadjustedevaporation[0] = self.sequences.fluxes.adjustedevaporation
    cpdef inline void calc_actualevaporation_v1(self)  nogil:
        self.sequences.fluxes.actualevaporation = self.sequences.fluxes.adjustedevaporation * smoothutils.smooth_logistic1(            self.sequences.factors.waterlevel - self.parameters.control.thresholdevaporation, self.parameters.derived.smoothparevaporation        )
    cpdef inline void pic_inflow_v1(self)  nogil:
        cdef int idx
        self.sequences.fluxes.inflow = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx][0])
    cpdef inline void pic_inflow_v2(self)  nogil:
        cdef int idx
        self.sequences.fluxes.inflow = self.sequences.inlets.s[0] + self.sequences.inlets.r[0]
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.inflow = self.sequences.fluxes.inflow + (self.sequences.inlets.q[idx][0])
    cpdef inline void calc_naturalremotedischarge_v1(self)  nogil:
        cdef int idx
        self.sequences.fluxes.naturalremotedischarge = 0.0
        for idx in range(self.parameters.control.nmblogentries):
            self.sequences.fluxes.naturalremotedischarge = self.sequences.fluxes.naturalremotedischarge + ((                self.sequences.logs.loggedtotalremotedischarge[idx] - self.sequences.logs.loggedoutflow[idx]            ))
        if self.sequences.fluxes.naturalremotedischarge > 0.0:
            self.sequences.fluxes.naturalremotedischarge = self.sequences.fluxes.naturalremotedischarge / (self.parameters.control.nmblogentries)
        else:
            self.sequences.fluxes.naturalremotedischarge = 0.0
    cpdef inline void calc_remotedemand_v1(self)  nogil:
        cdef double d_rdm
        d_rdm = self.parameters.control.remotedischargeminimum[self.parameters.derived.toy[self.idx_sim]]
        self.sequences.fluxes.remotedemand = max(d_rdm - self.sequences.fluxes.naturalremotedischarge, 0.0)
    cpdef inline void calc_remotefailure_v1(self)  nogil:
        cdef int idx
        self.sequences.fluxes.remotefailure = 0
        for idx in range(self.parameters.control.nmblogentries):
            self.sequences.fluxes.remotefailure = self.sequences.fluxes.remotefailure - (self.sequences.logs.loggedtotalremotedischarge[idx])
        self.sequences.fluxes.remotefailure = self.sequences.fluxes.remotefailure / (self.parameters.control.nmblogentries)
        self.sequences.fluxes.remotefailure = self.sequences.fluxes.remotefailure + (self.parameters.control.remotedischargeminimum[self.parameters.derived.toy[self.idx_sim]])
    cpdef inline void calc_requiredremoterelease_v1(self)  nogil:
        self.sequences.fluxes.requiredremoterelease = self.sequences.fluxes.remotedemand + (            smoothutils.smooth_logistic1(                self.sequences.fluxes.remotefailure,                self.parameters.derived.remotedischargesmoothpar[self.parameters.derived.toy[self.idx_sim]],            )            * self.parameters.control.remotedischargesafety[self.parameters.derived.toy[self.idx_sim]]        )
    cpdef inline void calc_requiredrelease_v1(self)  nogil:
        self.sequences.fluxes.requiredrelease = self.parameters.control.neardischargeminimumthreshold[self.parameters.derived.toy[self.idx_sim]]
        self.sequences.fluxes.requiredrelease = self.sequences.fluxes.requiredrelease + smoothutils.smooth_logistic2(            self.sequences.fluxes.requiredremoterelease - self.sequences.fluxes.requiredrelease,            self.parameters.derived.neardischargeminimumsmoothpar2[self.parameters.derived.toy[self.idx_sim]],        )
    cpdef inline void calc_requiredrelease_v2(self)  nogil:
        self.sequences.fluxes.requiredrelease = self.parameters.control.neardischargeminimumthreshold[self.parameters.derived.toy[self.idx_sim]]
    cpdef inline void calc_targetedrelease_v1(self)  nogil:
        if self.parameters.control.restricttargetedrelease:
            self.sequences.fluxes.targetedrelease = smoothutils.smooth_logistic1(                self.sequences.fluxes.inflow - self.parameters.control.neardischargeminimumthreshold[self.parameters.derived.toy[self.idx_sim]],                self.parameters.derived.neardischargeminimumsmoothpar1[self.parameters.derived.toy[self.idx_sim]],            )
            self.sequences.fluxes.targetedrelease = (                self.sequences.fluxes.targetedrelease * self.sequences.fluxes.requiredrelease                + (1.0 - self.sequences.fluxes.targetedrelease) * self.sequences.fluxes.inflow            )
        else:
            self.sequences.fluxes.targetedrelease = self.sequences.fluxes.requiredrelease
    cpdef inline void calc_adjustedprecipitation(self)  nogil:
        self.sequences.fluxes.adjustedprecipitation = (            self.parameters.derived.inputfactor * self.parameters.control.correctionprecipitation * self.sequences.inputs.precipitation        )
    cpdef inline void calc_adjustedevaporation(self)  nogil:
        cdef double d_old
        cdef double d_new
        cdef double d_weight
        d_weight = self.parameters.control.weightevaporation
        d_new = self.parameters.derived.inputfactor * self.parameters.control.correctionevaporation * self.sequences.inputs.evaporation
        d_old = self.sequences.logs.loggedadjustedevaporation[0]
        self.sequences.fluxes.adjustedevaporation = d_weight * d_new + (1.0 - d_weight) * d_old
        self.sequences.logs.loggedadjustedevaporation[0] = self.sequences.fluxes.adjustedevaporation
    cpdef inline void calc_actualevaporation(self)  nogil:
        self.sequences.fluxes.actualevaporation = self.sequences.fluxes.adjustedevaporation * smoothutils.smooth_logistic1(            self.sequences.factors.waterlevel - self.parameters.control.thresholdevaporation, self.parameters.derived.smoothparevaporation        )
    cpdef inline void calc_naturalremotedischarge(self)  nogil:
        cdef int idx
        self.sequences.fluxes.naturalremotedischarge = 0.0
        for idx in range(self.parameters.control.nmblogentries):
            self.sequences.fluxes.naturalremotedischarge = self.sequences.fluxes.naturalremotedischarge + ((                self.sequences.logs.loggedtotalremotedischarge[idx] - self.sequences.logs.loggedoutflow[idx]            ))
        if self.sequences.fluxes.naturalremotedischarge > 0.0:
            self.sequences.fluxes.naturalremotedischarge = self.sequences.fluxes.naturalremotedischarge / (self.parameters.control.nmblogentries)
        else:
            self.sequences.fluxes.naturalremotedischarge = 0.0
    cpdef inline void calc_remotedemand(self)  nogil:
        cdef double d_rdm
        d_rdm = self.parameters.control.remotedischargeminimum[self.parameters.derived.toy[self.idx_sim]]
        self.sequences.fluxes.remotedemand = max(d_rdm - self.sequences.fluxes.naturalremotedischarge, 0.0)
    cpdef inline void calc_remotefailure(self)  nogil:
        cdef int idx
        self.sequences.fluxes.remotefailure = 0
        for idx in range(self.parameters.control.nmblogentries):
            self.sequences.fluxes.remotefailure = self.sequences.fluxes.remotefailure - (self.sequences.logs.loggedtotalremotedischarge[idx])
        self.sequences.fluxes.remotefailure = self.sequences.fluxes.remotefailure / (self.parameters.control.nmblogentries)
        self.sequences.fluxes.remotefailure = self.sequences.fluxes.remotefailure + (self.parameters.control.remotedischargeminimum[self.parameters.derived.toy[self.idx_sim]])
    cpdef inline void calc_targetedrelease(self)  nogil:
        if self.parameters.control.restricttargetedrelease:
            self.sequences.fluxes.targetedrelease = smoothutils.smooth_logistic1(                self.sequences.fluxes.inflow - self.parameters.control.neardischargeminimumthreshold[self.parameters.derived.toy[self.idx_sim]],                self.parameters.derived.neardischargeminimumsmoothpar1[self.parameters.derived.toy[self.idx_sim]],            )
            self.sequences.fluxes.targetedrelease = (                self.sequences.fluxes.targetedrelease * self.sequences.fluxes.requiredrelease                + (1.0 - self.sequences.fluxes.targetedrelease) * self.sequences.fluxes.inflow            )
        else:
            self.sequences.fluxes.targetedrelease = self.sequences.fluxes.requiredrelease
    cpdef inline void calc_waterlevel_v1(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.sequences.factors.waterlevel = self.parameters.control.watervolume2waterlevel.outputs[0]
    cpdef inline void calc_surfacearea_v1(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.parameters.control.watervolume2waterlevel.calculate_derivatives(0)
        self.sequences.aides.surfacearea = 1.0 / self.parameters.control.watervolume2waterlevel.output_derivatives[0]
    cpdef inline void calc_alloweddischarge_v1(self)  nogil:
        self.sequences.aides.alloweddischarge = (            self.parameters.control.allowedwaterleveldrop / self.parameters.derived.seconds * self.sequences.aides.surfacearea * 1e6            + self.sequences.fluxes.adjustedprecipitation            + self.sequences.fluxes.inflow            - self.sequences.fluxes.actualevaporation            + self.sequences.fluxes.exchange        )
    cpdef inline void calc_alloweddischarge_v2(self)  nogil:
        self.sequences.aides.alloweddischarge = smoothutils.smooth_min1(            self.parameters.control.allowedwaterleveldrop / self.parameters.derived.seconds * self.sequences.aides.surfacearea * 1e6            + self.sequences.fluxes.inflow,            self.parameters.control.allowedrelease[self.parameters.derived.toy[self.idx_sim]],            self.parameters.derived.dischargesmoothpar,        )
    cpdef inline void calc_actualrelease_v1(self)  nogil:
        self.sequences.fluxes.actualrelease = self.sequences.fluxes.targetedrelease * smoothutils.smooth_logistic1(            self.sequences.factors.waterlevel - self.parameters.control.waterlevelminimumthreshold,            self.parameters.derived.waterlevelminimumsmoothpar,        )
    cpdef inline void calc_actualrelease_v2(self)  nogil:
        self.sequences.fluxes.actualrelease = self.parameters.control.allowedrelease[            self.parameters.derived.toy[self.idx_sim]        ] * smoothutils.smooth_logistic1(            self.sequences.factors.waterlevel - self.parameters.control.waterlevelminimumthreshold,            self.parameters.derived.waterlevelminimumsmoothpar,        )
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
    cpdef inline void calc_possibleremoterelief_v1(self)  nogil:
        self.parameters.control.waterlevel2possibleremoterelief.inputs[0] = self.sequences.factors.waterlevel
        self.parameters.control.waterlevel2possibleremoterelief.calculate_values()
        self.sequences.fluxes.possibleremoterelief = self.parameters.control.waterlevel2possibleremoterelief.outputs[0]
    cpdef inline void calc_actualremoterelief_v1(self)  nogil:
        self.sequences.fluxes.actualremoterelief = self.fix_min1_v1(            self.sequences.fluxes.possibleremoterelief,            self.sequences.fluxes.allowedremoterelief,            self.parameters.control.remoterelieftolerance,            True,        )
    cpdef inline void calc_actualremoterelease_v1(self)  nogil:
        self.sequences.fluxes.actualremoterelease = (            self.sequences.fluxes.requiredremoterelease            * smoothutils.smooth_logistic1(                self.sequences.factors.waterlevel - self.parameters.control.waterlevelminimumremotethreshold,                self.parameters.derived.waterlevelminimumremotesmoothpar,            )        )
    cpdef inline void update_actualremoterelief_v1(self)  nogil:
        self.sequences.fluxes.actualremoterelief = self.fix_min1_v1(            self.sequences.fluxes.actualremoterelief,            self.parameters.control.highestremotedischarge,            self.parameters.derived.highestremotesmoothpar,            False,        )
    cpdef inline void update_actualremoterelease_v1(self)  nogil:
        self.sequences.fluxes.actualremoterelease = self.fix_min1_v1(            self.sequences.fluxes.actualremoterelease,            self.parameters.control.highestremotedischarge - self.sequences.fluxes.actualremoterelief,            self.parameters.derived.highestremotesmoothpar,            False,        )
    cpdef inline void calc_flooddischarge_v1(self)  nogil:
        self.parameters.control.waterlevel2flooddischarge.inputs[0] = self.sequences.factors.waterlevel
        self.parameters.control.waterlevel2flooddischarge.calculate_values(self.parameters.derived.toy[self.idx_sim])
        self.sequences.fluxes.flooddischarge = self.parameters.control.waterlevel2flooddischarge.outputs[0]
    cpdef inline void calc_outflow_v1(self)  nogil:
        self.sequences.fluxes.outflow = max(self.sequences.fluxes.actualrelease + self.sequences.fluxes.flooddischarge, 0.0)
    cpdef inline void calc_outflow_v2(self)  nogil:
        self.sequences.fluxes.outflow = self.fix_min1_v1(            self.sequences.fluxes.flooddischarge, self.sequences.aides.alloweddischarge, self.parameters.derived.dischargesmoothpar, False        )
    cpdef inline void calc_waterlevel(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.sequences.factors.waterlevel = self.parameters.control.watervolume2waterlevel.outputs[0]
    cpdef inline void calc_surfacearea(self)  nogil:
        self.parameters.control.watervolume2waterlevel.inputs[0] = self.sequences.new_states.watervolume
        self.parameters.control.watervolume2waterlevel.calculate_values()
        self.parameters.control.watervolume2waterlevel.calculate_derivatives(0)
        self.sequences.aides.surfacearea = 1.0 / self.parameters.control.watervolume2waterlevel.output_derivatives[0]
    cpdef inline void calc_possibleremoterelief(self)  nogil:
        self.parameters.control.waterlevel2possibleremoterelief.inputs[0] = self.sequences.factors.waterlevel
        self.parameters.control.waterlevel2possibleremoterelief.calculate_values()
        self.sequences.fluxes.possibleremoterelief = self.parameters.control.waterlevel2possibleremoterelief.outputs[0]
    cpdef inline void calc_actualremoterelief(self)  nogil:
        self.sequences.fluxes.actualremoterelief = self.fix_min1_v1(            self.sequences.fluxes.possibleremoterelief,            self.sequences.fluxes.allowedremoterelief,            self.parameters.control.remoterelieftolerance,            True,        )
    cpdef inline void calc_actualremoterelease(self)  nogil:
        self.sequences.fluxes.actualremoterelease = (            self.sequences.fluxes.requiredremoterelease            * smoothutils.smooth_logistic1(                self.sequences.factors.waterlevel - self.parameters.control.waterlevelminimumremotethreshold,                self.parameters.derived.waterlevelminimumremotesmoothpar,            )        )
    cpdef inline void update_actualremoterelief(self)  nogil:
        self.sequences.fluxes.actualremoterelief = self.fix_min1_v1(            self.sequences.fluxes.actualremoterelief,            self.parameters.control.highestremotedischarge,            self.parameters.derived.highestremotesmoothpar,            False,        )
    cpdef inline void update_actualremoterelease(self)  nogil:
        self.sequences.fluxes.actualremoterelease = self.fix_min1_v1(            self.sequences.fluxes.actualremoterelease,            self.parameters.control.highestremotedischarge - self.sequences.fluxes.actualremoterelief,            self.parameters.derived.highestremotesmoothpar,            False,        )
    cpdef inline void calc_flooddischarge(self)  nogil:
        self.parameters.control.waterlevel2flooddischarge.inputs[0] = self.sequences.factors.waterlevel
        self.parameters.control.waterlevel2flooddischarge.calculate_values(self.parameters.derived.toy[self.idx_sim])
        self.sequences.fluxes.flooddischarge = self.parameters.control.waterlevel2flooddischarge.outputs[0]
    cpdef inline void update_watervolume_v1(self)  nogil:
        self.sequences.new_states.watervolume = self.sequences.old_states.watervolume + self.parameters.derived.seconds / 1e6 * (            self.sequences.fluxes.adjustedprecipitation - self.sequences.fluxes.actualevaporation + self.sequences.fluxes.inflow - self.sequences.fluxes.outflow        )
    cpdef inline void update_watervolume_v2(self)  nogil:
        self.sequences.new_states.watervolume = self.sequences.old_states.watervolume + self.parameters.derived.seconds / 1e6 * (            self.sequences.fluxes.adjustedprecipitation            - self.sequences.fluxes.actualevaporation            + self.sequences.fluxes.inflow            - self.sequences.fluxes.outflow            - self.sequences.fluxes.actualremoterelease        )
    cpdef inline void update_watervolume_v3(self)  nogil:
        self.sequences.new_states.watervolume = self.sequences.old_states.watervolume + (self.parameters.derived.seconds / 1e6) * (            self.sequences.fluxes.adjustedprecipitation            - self.sequences.fluxes.actualevaporation            + self.sequences.fluxes.inflow            - self.sequences.fluxes.outflow            - self.sequences.fluxes.actualremoterelease            - self.sequences.fluxes.actualremoterelief        )
    cpdef inline void update_watervolume_v4(self)  nogil:
        self.sequences.new_states.watervolume = self.sequences.old_states.watervolume + self.parameters.derived.seconds / 1e6 * (            self.sequences.fluxes.adjustedprecipitation            - self.sequences.fluxes.actualevaporation            + self.sequences.fluxes.inflow            - self.sequences.fluxes.outflow            + self.sequences.fluxes.exchange        )
    cpdef inline double fix_min1_v1(self, double input_, double threshold, double smoothpar, bint relative)  nogil:
        cdef int _
        cdef double d_result
        if relative:
            smoothpar = smoothpar * (threshold)
        d_result = smoothutils.smooth_min1(input_, threshold, smoothpar)
        for _ in range(5):
            smoothpar = smoothpar / (5.0)
            d_result = smoothutils.smooth_max1(d_result, 0.0, smoothpar)
            smoothpar = smoothpar / (5.0)
            if relative:
                d_result = smoothutils.smooth_min1(d_result, input_, smoothpar)
            else:
                d_result = smoothutils.smooth_min1(d_result, threshold, smoothpar)
        return max(min(d_result, input_, threshold), 0.0)
    cpdef inline double fix_min1(self, double input_, double threshold, double smoothpar, bint relative)  nogil:
        cdef int _
        cdef double d_result
        if relative:
            smoothpar = smoothpar * (threshold)
        d_result = smoothutils.smooth_min1(input_, threshold, smoothpar)
        for _ in range(5):
            smoothpar = smoothpar / (5.0)
            d_result = smoothutils.smooth_max1(d_result, 0.0, smoothpar)
            smoothpar = smoothpar / (5.0)
            if relative:
                d_result = smoothutils.smooth_min1(d_result, input_, smoothpar)
            else:
                d_result = smoothutils.smooth_min1(d_result, threshold, smoothpar)
        return max(min(d_result, input_, threshold), 0.0)
    cpdef inline void pass_outflow_v1(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
    cpdef inline void update_loggedoutflow_v1(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.control.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedoutflow[idx] = self.sequences.logs.loggedoutflow[idx - 1]
        self.sequences.logs.loggedoutflow[0] = self.sequences.fluxes.outflow
    cpdef inline void pass_actualremoterelease_v1(self)  nogil:
        self.sequences.outlets.s[0] = self.sequences.outlets.s[0] + (self.sequences.fluxes.actualremoterelease)
    cpdef inline void pass_actualremoterelief_v1(self)  nogil:
        self.sequences.outlets.r[0] = self.sequences.outlets.r[0] + (self.sequences.fluxes.actualremoterelief)
    cpdef inline void pass_outflow(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.outflow)
    cpdef inline void update_loggedoutflow(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.control.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedoutflow[idx] = self.sequences.logs.loggedoutflow[idx - 1]
        self.sequences.logs.loggedoutflow[0] = self.sequences.fluxes.outflow
    cpdef inline void pass_actualremoterelease(self)  nogil:
        self.sequences.outlets.s[0] = self.sequences.outlets.s[0] + (self.sequences.fluxes.actualremoterelease)
    cpdef inline void pass_actualremoterelief(self)  nogil:
        self.sequences.outlets.r[0] = self.sequences.outlets.r[0] + (self.sequences.fluxes.actualremoterelief)
    cpdef inline void calc_missingremoterelease_v1(self)  nogil:
        self.sequences.fluxes.missingremoterelease = max(            self.sequences.fluxes.requiredremoterelease - self.sequences.fluxes.actualrelease, 0.0        )
    cpdef inline void pass_missingremoterelease_v1(self)  nogil:
        self.sequences.senders.d[0] = self.sequences.senders.d[0] + (self.sequences.fluxes.missingremoterelease)
    cpdef inline void calc_allowedremoterelief_v2(self)  nogil:
        cdef int toy
        toy = self.parameters.derived.toy[self.idx_sim]
        self.sequences.fluxes.allowedremoterelief = (            smoothutils.smooth_logistic1(                self.parameters.control.waterlevelreliefthreshold[toy] - self.sequences.factors.waterlevel,                self.parameters.derived.waterlevelreliefsmoothpar[toy],            )            * self.parameters.control.highestremoterelief[toy]        )
    cpdef inline void pass_allowedremoterelief_v1(self)  nogil:
        self.sequences.senders.r[0] = self.sequences.senders.r[0] + (self.sequences.fluxes.allowedremoterelief)
    cpdef inline void calc_requiredremotesupply_v1(self)  nogil:
        cdef int toy
        toy = self.parameters.derived.toy[self.idx_sim]
        self.sequences.fluxes.requiredremotesupply = (            smoothutils.smooth_logistic1(                self.parameters.control.waterlevelsupplythreshold[toy] - self.sequences.factors.waterlevel,                self.parameters.derived.waterlevelsupplysmoothpar[toy],            )            * self.parameters.control.highestremotesupply[toy]        )
    cpdef inline void pass_requiredremotesupply_v1(self)  nogil:
        self.sequences.senders.s[0] = self.sequences.senders.s[0] + (self.sequences.fluxes.requiredremotesupply)
    cpdef inline void calc_missingremoterelease(self)  nogil:
        self.sequences.fluxes.missingremoterelease = max(            self.sequences.fluxes.requiredremoterelease - self.sequences.fluxes.actualrelease, 0.0        )
    cpdef inline void pass_missingremoterelease(self)  nogil:
        self.sequences.senders.d[0] = self.sequences.senders.d[0] + (self.sequences.fluxes.missingremoterelease)
    cpdef inline void pass_allowedremoterelief(self)  nogil:
        self.sequences.senders.r[0] = self.sequences.senders.r[0] + (self.sequences.fluxes.allowedremoterelief)
    cpdef inline void calc_requiredremotesupply(self)  nogil:
        cdef int toy
        toy = self.parameters.derived.toy[self.idx_sim]
        self.sequences.fluxes.requiredremotesupply = (            smoothutils.smooth_logistic1(                self.parameters.control.waterlevelsupplythreshold[toy] - self.sequences.factors.waterlevel,                self.parameters.derived.waterlevelsupplysmoothpar[toy],            )            * self.parameters.control.highestremotesupply[toy]        )
    cpdef inline void pass_requiredremotesupply(self)  nogil:
        self.sequences.senders.s[0] = self.sequences.senders.s[0] + (self.sequences.fluxes.requiredremotesupply)
