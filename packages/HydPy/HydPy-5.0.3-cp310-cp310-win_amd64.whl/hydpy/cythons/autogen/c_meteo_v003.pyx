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
    cdef public FixedParameters fixed
@cython.final
cdef class ControlParameters:
    cdef public double latitude
    cdef public double longitude
    cdef public double[:] angstromconstant
    cdef public double[:] angstromfactor
    cdef public double[:] angstromalternative
@cython.final
cdef class DerivedParameters:
    cdef public numpy.int32_t[:] doy
    cdef public numpy.int32_t[:] moy
    cdef public double hours
    cdef public double days
    cdef public double[:] sct
    cdef public numpy.int32_t nmblogentries
    cdef public numpy.int32_t utclongitude
    cdef public double latituderad
@cython.final
cdef class FixedParameters:
    cdef public double pi
    cdef public double solarconstant
@cython.final
cdef class Sequences:
    cdef public InputSequences inputs
    cdef public FactorSequences factors
    cdef public FluxSequences fluxes
    cdef public LogSequences logs
@cython.final
cdef class InputSequences:
    cdef public double sunshineduration
    cdef public int _sunshineduration_ndim
    cdef public int _sunshineduration_length
    cdef public bint _sunshineduration_ramflag
    cdef public double[:] _sunshineduration_array
    cdef public bint _sunshineduration_diskflag_reading
    cdef public bint _sunshineduration_diskflag_writing
    cdef public double[:] _sunshineduration_ncarray
    cdef public bint _sunshineduration_inputflag
    cdef double *_sunshineduration_inputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._sunshineduration_inputflag:
            self.sunshineduration = self._sunshineduration_inputpointer[0]
        elif self._sunshineduration_diskflag_reading:
            self.sunshineduration = self._sunshineduration_ncarray[0]
        elif self._sunshineduration_ramflag:
            self.sunshineduration = self._sunshineduration_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._sunshineduration_diskflag_writing:
            self._sunshineduration_ncarray[0] = self.sunshineduration
        if self._sunshineduration_ramflag:
            self._sunshineduration_array[idx] = self.sunshineduration
    cpdef inline set_pointerinput(self, str name, pointerutils.PDouble value):
        if name == "sunshineduration":
            self._sunshineduration_inputpointer = value.p_value
@cython.final
cdef class FactorSequences:
    cdef public double earthsundistance
    cdef public int _earthsundistance_ndim
    cdef public int _earthsundistance_length
    cdef public bint _earthsundistance_ramflag
    cdef public double[:] _earthsundistance_array
    cdef public bint _earthsundistance_diskflag_reading
    cdef public bint _earthsundistance_diskflag_writing
    cdef public double[:] _earthsundistance_ncarray
    cdef public bint _earthsundistance_outputflag
    cdef double *_earthsundistance_outputpointer
    cdef public double solardeclination
    cdef public int _solardeclination_ndim
    cdef public int _solardeclination_length
    cdef public bint _solardeclination_ramflag
    cdef public double[:] _solardeclination_array
    cdef public bint _solardeclination_diskflag_reading
    cdef public bint _solardeclination_diskflag_writing
    cdef public double[:] _solardeclination_ncarray
    cdef public bint _solardeclination_outputflag
    cdef double *_solardeclination_outputpointer
    cdef public double timeofsunrise
    cdef public int _timeofsunrise_ndim
    cdef public int _timeofsunrise_length
    cdef public bint _timeofsunrise_ramflag
    cdef public double[:] _timeofsunrise_array
    cdef public bint _timeofsunrise_diskflag_reading
    cdef public bint _timeofsunrise_diskflag_writing
    cdef public double[:] _timeofsunrise_ncarray
    cdef public bint _timeofsunrise_outputflag
    cdef double *_timeofsunrise_outputpointer
    cdef public double timeofsunset
    cdef public int _timeofsunset_ndim
    cdef public int _timeofsunset_length
    cdef public bint _timeofsunset_ramflag
    cdef public double[:] _timeofsunset_array
    cdef public bint _timeofsunset_diskflag_reading
    cdef public bint _timeofsunset_diskflag_writing
    cdef public double[:] _timeofsunset_ncarray
    cdef public bint _timeofsunset_outputflag
    cdef double *_timeofsunset_outputpointer
    cdef public double possiblesunshineduration
    cdef public int _possiblesunshineduration_ndim
    cdef public int _possiblesunshineduration_length
    cdef public bint _possiblesunshineduration_ramflag
    cdef public double[:] _possiblesunshineduration_array
    cdef public bint _possiblesunshineduration_diskflag_reading
    cdef public bint _possiblesunshineduration_diskflag_writing
    cdef public double[:] _possiblesunshineduration_ncarray
    cdef public bint _possiblesunshineduration_outputflag
    cdef double *_possiblesunshineduration_outputpointer
    cdef public double dailypossiblesunshineduration
    cdef public int _dailypossiblesunshineduration_ndim
    cdef public int _dailypossiblesunshineduration_length
    cdef public bint _dailypossiblesunshineduration_ramflag
    cdef public double[:] _dailypossiblesunshineduration_array
    cdef public bint _dailypossiblesunshineduration_diskflag_reading
    cdef public bint _dailypossiblesunshineduration_diskflag_writing
    cdef public double[:] _dailypossiblesunshineduration_ncarray
    cdef public bint _dailypossiblesunshineduration_outputflag
    cdef double *_dailypossiblesunshineduration_outputpointer
    cdef public double dailysunshineduration
    cdef public int _dailysunshineduration_ndim
    cdef public int _dailysunshineduration_length
    cdef public bint _dailysunshineduration_ramflag
    cdef public double[:] _dailysunshineduration_array
    cdef public bint _dailysunshineduration_diskflag_reading
    cdef public bint _dailysunshineduration_diskflag_writing
    cdef public double[:] _dailysunshineduration_ncarray
    cdef public bint _dailysunshineduration_outputflag
    cdef double *_dailysunshineduration_outputpointer
    cdef public double portiondailyradiation
    cdef public int _portiondailyradiation_ndim
    cdef public int _portiondailyradiation_length
    cdef public bint _portiondailyradiation_ramflag
    cdef public double[:] _portiondailyradiation_array
    cdef public bint _portiondailyradiation_diskflag_reading
    cdef public bint _portiondailyradiation_diskflag_writing
    cdef public double[:] _portiondailyradiation_ncarray
    cdef public bint _portiondailyradiation_outputflag
    cdef double *_portiondailyradiation_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._earthsundistance_diskflag_reading:
            self.earthsundistance = self._earthsundistance_ncarray[0]
        elif self._earthsundistance_ramflag:
            self.earthsundistance = self._earthsundistance_array[idx]
        if self._solardeclination_diskflag_reading:
            self.solardeclination = self._solardeclination_ncarray[0]
        elif self._solardeclination_ramflag:
            self.solardeclination = self._solardeclination_array[idx]
        if self._timeofsunrise_diskflag_reading:
            self.timeofsunrise = self._timeofsunrise_ncarray[0]
        elif self._timeofsunrise_ramflag:
            self.timeofsunrise = self._timeofsunrise_array[idx]
        if self._timeofsunset_diskflag_reading:
            self.timeofsunset = self._timeofsunset_ncarray[0]
        elif self._timeofsunset_ramflag:
            self.timeofsunset = self._timeofsunset_array[idx]
        if self._possiblesunshineduration_diskflag_reading:
            self.possiblesunshineduration = self._possiblesunshineduration_ncarray[0]
        elif self._possiblesunshineduration_ramflag:
            self.possiblesunshineduration = self._possiblesunshineduration_array[idx]
        if self._dailypossiblesunshineduration_diskflag_reading:
            self.dailypossiblesunshineduration = self._dailypossiblesunshineduration_ncarray[0]
        elif self._dailypossiblesunshineduration_ramflag:
            self.dailypossiblesunshineduration = self._dailypossiblesunshineduration_array[idx]
        if self._dailysunshineduration_diskflag_reading:
            self.dailysunshineduration = self._dailysunshineduration_ncarray[0]
        elif self._dailysunshineduration_ramflag:
            self.dailysunshineduration = self._dailysunshineduration_array[idx]
        if self._portiondailyradiation_diskflag_reading:
            self.portiondailyradiation = self._portiondailyradiation_ncarray[0]
        elif self._portiondailyradiation_ramflag:
            self.portiondailyradiation = self._portiondailyradiation_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._earthsundistance_diskflag_writing:
            self._earthsundistance_ncarray[0] = self.earthsundistance
        if self._earthsundistance_ramflag:
            self._earthsundistance_array[idx] = self.earthsundistance
        if self._solardeclination_diskflag_writing:
            self._solardeclination_ncarray[0] = self.solardeclination
        if self._solardeclination_ramflag:
            self._solardeclination_array[idx] = self.solardeclination
        if self._timeofsunrise_diskflag_writing:
            self._timeofsunrise_ncarray[0] = self.timeofsunrise
        if self._timeofsunrise_ramflag:
            self._timeofsunrise_array[idx] = self.timeofsunrise
        if self._timeofsunset_diskflag_writing:
            self._timeofsunset_ncarray[0] = self.timeofsunset
        if self._timeofsunset_ramflag:
            self._timeofsunset_array[idx] = self.timeofsunset
        if self._possiblesunshineduration_diskflag_writing:
            self._possiblesunshineduration_ncarray[0] = self.possiblesunshineduration
        if self._possiblesunshineduration_ramflag:
            self._possiblesunshineduration_array[idx] = self.possiblesunshineduration
        if self._dailypossiblesunshineduration_diskflag_writing:
            self._dailypossiblesunshineduration_ncarray[0] = self.dailypossiblesunshineduration
        if self._dailypossiblesunshineduration_ramflag:
            self._dailypossiblesunshineduration_array[idx] = self.dailypossiblesunshineduration
        if self._dailysunshineduration_diskflag_writing:
            self._dailysunshineduration_ncarray[0] = self.dailysunshineduration
        if self._dailysunshineduration_ramflag:
            self._dailysunshineduration_array[idx] = self.dailysunshineduration
        if self._portiondailyradiation_diskflag_writing:
            self._portiondailyradiation_ncarray[0] = self.portiondailyradiation
        if self._portiondailyradiation_ramflag:
            self._portiondailyradiation_array[idx] = self.portiondailyradiation
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "earthsundistance":
            self._earthsundistance_outputpointer = value.p_value
        if name == "solardeclination":
            self._solardeclination_outputpointer = value.p_value
        if name == "timeofsunrise":
            self._timeofsunrise_outputpointer = value.p_value
        if name == "timeofsunset":
            self._timeofsunset_outputpointer = value.p_value
        if name == "possiblesunshineduration":
            self._possiblesunshineduration_outputpointer = value.p_value
        if name == "dailypossiblesunshineduration":
            self._dailypossiblesunshineduration_outputpointer = value.p_value
        if name == "dailysunshineduration":
            self._dailysunshineduration_outputpointer = value.p_value
        if name == "portiondailyradiation":
            self._portiondailyradiation_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._earthsundistance_outputflag:
            self._earthsundistance_outputpointer[0] = self.earthsundistance
        if self._solardeclination_outputflag:
            self._solardeclination_outputpointer[0] = self.solardeclination
        if self._timeofsunrise_outputflag:
            self._timeofsunrise_outputpointer[0] = self.timeofsunrise
        if self._timeofsunset_outputflag:
            self._timeofsunset_outputpointer[0] = self.timeofsunset
        if self._possiblesunshineduration_outputflag:
            self._possiblesunshineduration_outputpointer[0] = self.possiblesunshineduration
        if self._dailypossiblesunshineduration_outputflag:
            self._dailypossiblesunshineduration_outputpointer[0] = self.dailypossiblesunshineduration
        if self._dailysunshineduration_outputflag:
            self._dailysunshineduration_outputpointer[0] = self.dailysunshineduration
        if self._portiondailyradiation_outputflag:
            self._portiondailyradiation_outputpointer[0] = self.portiondailyradiation
@cython.final
cdef class FluxSequences:
    cdef public double extraterrestrialradiation
    cdef public int _extraterrestrialradiation_ndim
    cdef public int _extraterrestrialradiation_length
    cdef public bint _extraterrestrialradiation_ramflag
    cdef public double[:] _extraterrestrialradiation_array
    cdef public bint _extraterrestrialradiation_diskflag_reading
    cdef public bint _extraterrestrialradiation_diskflag_writing
    cdef public double[:] _extraterrestrialradiation_ncarray
    cdef public bint _extraterrestrialradiation_outputflag
    cdef double *_extraterrestrialradiation_outputpointer
    cdef public double unadjustedglobalradiation
    cdef public int _unadjustedglobalradiation_ndim
    cdef public int _unadjustedglobalradiation_length
    cdef public bint _unadjustedglobalradiation_ramflag
    cdef public double[:] _unadjustedglobalradiation_array
    cdef public bint _unadjustedglobalradiation_diskflag_reading
    cdef public bint _unadjustedglobalradiation_diskflag_writing
    cdef public double[:] _unadjustedglobalradiation_ncarray
    cdef public bint _unadjustedglobalradiation_outputflag
    cdef double *_unadjustedglobalradiation_outputpointer
    cdef public double dailyglobalradiation
    cdef public int _dailyglobalradiation_ndim
    cdef public int _dailyglobalradiation_length
    cdef public bint _dailyglobalradiation_ramflag
    cdef public double[:] _dailyglobalradiation_array
    cdef public bint _dailyglobalradiation_diskflag_reading
    cdef public bint _dailyglobalradiation_diskflag_writing
    cdef public double[:] _dailyglobalradiation_ncarray
    cdef public bint _dailyglobalradiation_outputflag
    cdef double *_dailyglobalradiation_outputpointer
    cdef public double globalradiation
    cdef public int _globalradiation_ndim
    cdef public int _globalradiation_length
    cdef public bint _globalradiation_ramflag
    cdef public double[:] _globalradiation_array
    cdef public bint _globalradiation_diskflag_reading
    cdef public bint _globalradiation_diskflag_writing
    cdef public double[:] _globalradiation_ncarray
    cdef public bint _globalradiation_outputflag
    cdef double *_globalradiation_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._extraterrestrialradiation_diskflag_reading:
            self.extraterrestrialradiation = self._extraterrestrialradiation_ncarray[0]
        elif self._extraterrestrialradiation_ramflag:
            self.extraterrestrialradiation = self._extraterrestrialradiation_array[idx]
        if self._unadjustedglobalradiation_diskflag_reading:
            self.unadjustedglobalradiation = self._unadjustedglobalradiation_ncarray[0]
        elif self._unadjustedglobalradiation_ramflag:
            self.unadjustedglobalradiation = self._unadjustedglobalradiation_array[idx]
        if self._dailyglobalradiation_diskflag_reading:
            self.dailyglobalradiation = self._dailyglobalradiation_ncarray[0]
        elif self._dailyglobalradiation_ramflag:
            self.dailyglobalradiation = self._dailyglobalradiation_array[idx]
        if self._globalradiation_diskflag_reading:
            self.globalradiation = self._globalradiation_ncarray[0]
        elif self._globalradiation_ramflag:
            self.globalradiation = self._globalradiation_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._extraterrestrialradiation_diskflag_writing:
            self._extraterrestrialradiation_ncarray[0] = self.extraterrestrialradiation
        if self._extraterrestrialradiation_ramflag:
            self._extraterrestrialradiation_array[idx] = self.extraterrestrialradiation
        if self._unadjustedglobalradiation_diskflag_writing:
            self._unadjustedglobalradiation_ncarray[0] = self.unadjustedglobalradiation
        if self._unadjustedglobalradiation_ramflag:
            self._unadjustedglobalradiation_array[idx] = self.unadjustedglobalradiation
        if self._dailyglobalradiation_diskflag_writing:
            self._dailyglobalradiation_ncarray[0] = self.dailyglobalradiation
        if self._dailyglobalradiation_ramflag:
            self._dailyglobalradiation_array[idx] = self.dailyglobalradiation
        if self._globalradiation_diskflag_writing:
            self._globalradiation_ncarray[0] = self.globalradiation
        if self._globalradiation_ramflag:
            self._globalradiation_array[idx] = self.globalradiation
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "extraterrestrialradiation":
            self._extraterrestrialradiation_outputpointer = value.p_value
        if name == "unadjustedglobalradiation":
            self._unadjustedglobalradiation_outputpointer = value.p_value
        if name == "dailyglobalradiation":
            self._dailyglobalradiation_outputpointer = value.p_value
        if name == "globalradiation":
            self._globalradiation_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._extraterrestrialradiation_outputflag:
            self._extraterrestrialradiation_outputpointer[0] = self.extraterrestrialradiation
        if self._unadjustedglobalradiation_outputflag:
            self._unadjustedglobalradiation_outputpointer[0] = self.unadjustedglobalradiation
        if self._dailyglobalradiation_outputflag:
            self._dailyglobalradiation_outputpointer[0] = self.dailyglobalradiation
        if self._globalradiation_outputflag:
            self._globalradiation_outputpointer[0] = self.globalradiation
@cython.final
cdef class LogSequences:
    cdef public double[:] loggedsunshineduration
    cdef public int _loggedsunshineduration_ndim
    cdef public int _loggedsunshineduration_length
    cdef public int _loggedsunshineduration_length_0
    cdef public double[:] loggedunadjustedglobalradiation
    cdef public int _loggedunadjustedglobalradiation_ndim
    cdef public int _loggedunadjustedglobalradiation_length
    cdef public int _loggedunadjustedglobalradiation_length_0


@cython.final
cdef class Model:
    cdef public int idx_sim
    cdef public Parameters parameters
    cdef public Sequences sequences
    cpdef inline void simulate(self, int idx)  nogil:
        self.idx_sim = idx
        self.load_data()
        self.run()
        self.update_outputs()
    cpdef inline void load_data(self) nogil:
        self.sequences.inputs.load_data(self.idx_sim)
    cpdef inline void save_data(self, int idx) nogil:
        self.sequences.inputs.save_data(self.idx_sim)
        self.sequences.factors.save_data(self.idx_sim)
        self.sequences.fluxes.save_data(self.idx_sim)
    cpdef inline void run(self) nogil:
        self.calc_earthsundistance_v1()
        self.calc_solardeclination_v2()
        self.calc_timeofsunrise_timeofsunset_v1()
        self.calc_dailypossiblesunshineduration_v1()
        self.calc_possiblesunshineduration_v2()
        self.update_loggedsunshineduration_v1()
        self.calc_dailysunshineduration_v1()
        self.calc_extraterrestrialradiation_v2()
        self.calc_dailyglobalradiation_v1()
        self.calc_portiondailyradiation_v1()
        self.calc_unadjustedglobalradiation_v1()
        self.update_loggedunadjustedglobalradiation_v1()
        self.calc_globalradiation_v2()
    cpdef inline void update_inlets(self) nogil:
        pass
    cpdef inline void update_outlets(self) nogil:
        pass
    cpdef inline void update_receivers(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_senders(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_outputs(self) nogil:
        self.sequences.factors.update_outputs()
        self.sequences.fluxes.update_outputs()

    cpdef inline void calc_earthsundistance_v1(self)  nogil:
        self.sequences.factors.earthsundistance = 1.0 + 0.033 * cos(            2 * self.parameters.fixed.pi / 366.0 * (self.parameters.derived.doy[self.idx_sim] + 1)        )
    cpdef inline void calc_solardeclination_v2(self)  nogil:
        self.sequences.factors.solardeclination = 0.41 * cos(            2.0 * self.parameters.fixed.pi * (self.parameters.derived.doy[self.idx_sim] - 171.0) / 365.0        )
    cpdef inline void calc_timeofsunrise_timeofsunset_v1(self)  nogil:
        cdef double d_dt
        self.sequences.factors.timeofsunrise = (12.0 / self.parameters.fixed.pi) * acos(            tan(self.sequences.factors.solardeclination) * tan(self.parameters.derived.latituderad)            + 0.0145            / cos(self.sequences.factors.solardeclination)            / cos(self.parameters.derived.latituderad)        )
        self.sequences.factors.timeofsunset = 24.0 - self.sequences.factors.timeofsunrise
        d_dt = (self.parameters.derived.utclongitude - self.parameters.control.longitude) * 4.0 / 60.0
        self.sequences.factors.timeofsunrise = self.sequences.factors.timeofsunrise + (d_dt)
        self.sequences.factors.timeofsunset = self.sequences.factors.timeofsunset + (d_dt)
    cpdef inline void calc_dailypossiblesunshineduration_v1(self)  nogil:
        self.sequences.factors.dailypossiblesunshineduration = self.sequences.factors.timeofsunset - self.sequences.factors.timeofsunrise
    cpdef inline void calc_possiblesunshineduration_v2(self)  nogil:
        cdef double d_t1
        cdef double d_t0
        cdef double d_stc
        d_stc = self.parameters.derived.sct[self.idx_sim]
        d_t0 = max((d_stc - self.parameters.derived.hours / 2.0), self.sequences.factors.timeofsunrise)
        d_t1 = min((d_stc + self.parameters.derived.hours / 2.0), self.sequences.factors.timeofsunset)
        self.sequences.factors.possiblesunshineduration = max(d_t1 - d_t0, 0.0)
    cpdef inline void update_loggedsunshineduration_v1(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedsunshineduration[idx] = self.sequences.logs.loggedsunshineduration[idx - 1]
        self.sequences.logs.loggedsunshineduration[0] = self.sequences.inputs.sunshineduration
    cpdef inline void calc_dailysunshineduration_v1(self)  nogil:
        cdef int idx
        self.sequences.factors.dailysunshineduration = 0.0
        for idx in range(self.parameters.derived.nmblogentries):
            self.sequences.factors.dailysunshineduration = self.sequences.factors.dailysunshineduration + (self.sequences.logs.loggedsunshineduration[idx])
    cpdef inline void calc_extraterrestrialradiation_v2(self)  nogil:
        cdef double d_sunsethourangle
        d_sunsethourangle = (self.sequences.factors.timeofsunset - self.sequences.factors.timeofsunrise) * self.parameters.fixed.pi / 24.0
        self.sequences.fluxes.extraterrestrialradiation = (            self.parameters.fixed.solarconstant * self.sequences.factors.earthsundistance / self.parameters.fixed.pi        ) * (            d_sunsethourangle            * sin(self.sequences.factors.solardeclination)            * sin(self.parameters.derived.latituderad)            + cos(self.sequences.factors.solardeclination)            * cos(self.parameters.derived.latituderad)            * sin(d_sunsethourangle)        )
    cpdef inline void calc_dailyglobalradiation_v1(self)  nogil:
        self.sequences.fluxes.dailyglobalradiation = self.return_dailyglobalradiation_v1(            self.sequences.factors.dailysunshineduration, self.sequences.factors.dailypossiblesunshineduration        )
    cpdef inline void calc_portiondailyradiation_v1(self)  nogil:
        cdef double d_temp
        cdef double d_p
        cdef double d_tlp
        cdef double d_dt
        cdef int i
        cdef double d_fac
        d_fac = 2.0 * self.parameters.fixed.pi / 360.0
        self.sequences.factors.portiondailyradiation = 0.0
        for i in range(2):
            if i:
                d_dt = self.parameters.derived.hours / 2.0
            else:
                d_dt = -self.parameters.derived.hours / 2.0
            d_tlp = (100.0 * d_fac) * (                (self.parameters.derived.sct[self.idx_sim] + d_dt - self.sequences.factors.timeofsunrise)                / (self.sequences.factors.timeofsunset - self.sequences.factors.timeofsunrise)            )
            if d_tlp <= 0.0:
                d_p = 0.0
            elif d_tlp < 100.0 * d_fac:
                d_p = 50.0 - 50.0 * cos(1.8 * d_tlp)
                d_temp = 3.4 * sin(3.6 * d_tlp) ** 2
                if d_tlp <= 50.0 * d_fac:
                    d_p = d_p - (d_temp)
                else:
                    d_p = d_p + (d_temp)
            else:
                d_p = 100.0
            if i:
                self.sequences.factors.portiondailyradiation = self.sequences.factors.portiondailyradiation + (d_p)
            else:
                self.sequences.factors.portiondailyradiation = self.sequences.factors.portiondailyradiation - (d_p)
    cpdef inline void calc_unadjustedglobalradiation_v1(self)  nogil:
        cdef double d_pos
        cdef double d_act
        if self.sequences.factors.possiblesunshineduration > 0.0:
            d_act = self.sequences.inputs.sunshineduration
            d_pos = self.sequences.factors.possiblesunshineduration
        else:
            d_act = self.sequences.factors.dailysunshineduration
            d_pos = self.sequences.factors.dailypossiblesunshineduration
        self.sequences.fluxes.unadjustedglobalradiation = (            self.parameters.derived.nmblogentries * self.sequences.factors.portiondailyradiation / 100.0        ) * self.return_dailyglobalradiation_v1(d_act, d_pos)
    cpdef inline void update_loggedunadjustedglobalradiation_v1(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedunadjustedglobalradiation[                idx            ] = self.sequences.logs.loggedunadjustedglobalradiation[idx - 1]
        self.sequences.logs.loggedunadjustedglobalradiation[0] = self.sequences.fluxes.unadjustedglobalradiation
    cpdef inline void calc_globalradiation_v2(self)  nogil:
        cdef double d_glob_mean
        cdef int idx
        cdef double d_glob_sum
        d_glob_sum = 0.0
        for idx in range(self.parameters.derived.nmblogentries):
            d_glob_sum = d_glob_sum + (self.sequences.logs.loggedunadjustedglobalradiation[idx])
        d_glob_mean = d_glob_sum / self.parameters.derived.nmblogentries
        self.sequences.fluxes.globalradiation = (            self.sequences.fluxes.unadjustedglobalradiation * self.sequences.fluxes.dailyglobalradiation / d_glob_mean        )
    cpdef inline void calc_earthsundistance(self)  nogil:
        self.sequences.factors.earthsundistance = 1.0 + 0.033 * cos(            2 * self.parameters.fixed.pi / 366.0 * (self.parameters.derived.doy[self.idx_sim] + 1)        )
    cpdef inline void calc_solardeclination(self)  nogil:
        self.sequences.factors.solardeclination = 0.41 * cos(            2.0 * self.parameters.fixed.pi * (self.parameters.derived.doy[self.idx_sim] - 171.0) / 365.0        )
    cpdef inline void calc_timeofsunrise_timeofsunset(self)  nogil:
        cdef double d_dt
        self.sequences.factors.timeofsunrise = (12.0 / self.parameters.fixed.pi) * acos(            tan(self.sequences.factors.solardeclination) * tan(self.parameters.derived.latituderad)            + 0.0145            / cos(self.sequences.factors.solardeclination)            / cos(self.parameters.derived.latituderad)        )
        self.sequences.factors.timeofsunset = 24.0 - self.sequences.factors.timeofsunrise
        d_dt = (self.parameters.derived.utclongitude - self.parameters.control.longitude) * 4.0 / 60.0
        self.sequences.factors.timeofsunrise = self.sequences.factors.timeofsunrise + (d_dt)
        self.sequences.factors.timeofsunset = self.sequences.factors.timeofsunset + (d_dt)
    cpdef inline void calc_dailypossiblesunshineduration(self)  nogil:
        self.sequences.factors.dailypossiblesunshineduration = self.sequences.factors.timeofsunset - self.sequences.factors.timeofsunrise
    cpdef inline void calc_possiblesunshineduration(self)  nogil:
        cdef double d_t1
        cdef double d_t0
        cdef double d_stc
        d_stc = self.parameters.derived.sct[self.idx_sim]
        d_t0 = max((d_stc - self.parameters.derived.hours / 2.0), self.sequences.factors.timeofsunrise)
        d_t1 = min((d_stc + self.parameters.derived.hours / 2.0), self.sequences.factors.timeofsunset)
        self.sequences.factors.possiblesunshineduration = max(d_t1 - d_t0, 0.0)
    cpdef inline void update_loggedsunshineduration(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedsunshineduration[idx] = self.sequences.logs.loggedsunshineduration[idx - 1]
        self.sequences.logs.loggedsunshineduration[0] = self.sequences.inputs.sunshineduration
    cpdef inline void calc_dailysunshineduration(self)  nogil:
        cdef int idx
        self.sequences.factors.dailysunshineduration = 0.0
        for idx in range(self.parameters.derived.nmblogentries):
            self.sequences.factors.dailysunshineduration = self.sequences.factors.dailysunshineduration + (self.sequences.logs.loggedsunshineduration[idx])
    cpdef inline void calc_extraterrestrialradiation(self)  nogil:
        cdef double d_sunsethourangle
        d_sunsethourangle = (self.sequences.factors.timeofsunset - self.sequences.factors.timeofsunrise) * self.parameters.fixed.pi / 24.0
        self.sequences.fluxes.extraterrestrialradiation = (            self.parameters.fixed.solarconstant * self.sequences.factors.earthsundistance / self.parameters.fixed.pi        ) * (            d_sunsethourangle            * sin(self.sequences.factors.solardeclination)            * sin(self.parameters.derived.latituderad)            + cos(self.sequences.factors.solardeclination)            * cos(self.parameters.derived.latituderad)            * sin(d_sunsethourangle)        )
    cpdef inline void calc_dailyglobalradiation(self)  nogil:
        self.sequences.fluxes.dailyglobalradiation = self.return_dailyglobalradiation_v1(            self.sequences.factors.dailysunshineduration, self.sequences.factors.dailypossiblesunshineduration        )
    cpdef inline void calc_portiondailyradiation(self)  nogil:
        cdef double d_temp
        cdef double d_p
        cdef double d_tlp
        cdef double d_dt
        cdef int i
        cdef double d_fac
        d_fac = 2.0 * self.parameters.fixed.pi / 360.0
        self.sequences.factors.portiondailyradiation = 0.0
        for i in range(2):
            if i:
                d_dt = self.parameters.derived.hours / 2.0
            else:
                d_dt = -self.parameters.derived.hours / 2.0
            d_tlp = (100.0 * d_fac) * (                (self.parameters.derived.sct[self.idx_sim] + d_dt - self.sequences.factors.timeofsunrise)                / (self.sequences.factors.timeofsunset - self.sequences.factors.timeofsunrise)            )
            if d_tlp <= 0.0:
                d_p = 0.0
            elif d_tlp < 100.0 * d_fac:
                d_p = 50.0 - 50.0 * cos(1.8 * d_tlp)
                d_temp = 3.4 * sin(3.6 * d_tlp) ** 2
                if d_tlp <= 50.0 * d_fac:
                    d_p = d_p - (d_temp)
                else:
                    d_p = d_p + (d_temp)
            else:
                d_p = 100.0
            if i:
                self.sequences.factors.portiondailyradiation = self.sequences.factors.portiondailyradiation + (d_p)
            else:
                self.sequences.factors.portiondailyradiation = self.sequences.factors.portiondailyradiation - (d_p)
    cpdef inline void calc_unadjustedglobalradiation(self)  nogil:
        cdef double d_pos
        cdef double d_act
        if self.sequences.factors.possiblesunshineduration > 0.0:
            d_act = self.sequences.inputs.sunshineduration
            d_pos = self.sequences.factors.possiblesunshineduration
        else:
            d_act = self.sequences.factors.dailysunshineduration
            d_pos = self.sequences.factors.dailypossiblesunshineduration
        self.sequences.fluxes.unadjustedglobalradiation = (            self.parameters.derived.nmblogentries * self.sequences.factors.portiondailyradiation / 100.0        ) * self.return_dailyglobalradiation_v1(d_act, d_pos)
    cpdef inline void update_loggedunadjustedglobalradiation(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedunadjustedglobalradiation[                idx            ] = self.sequences.logs.loggedunadjustedglobalradiation[idx - 1]
        self.sequences.logs.loggedunadjustedglobalradiation[0] = self.sequences.fluxes.unadjustedglobalradiation
    cpdef inline void calc_globalradiation(self)  nogil:
        cdef double d_glob_mean
        cdef int idx
        cdef double d_glob_sum
        d_glob_sum = 0.0
        for idx in range(self.parameters.derived.nmblogentries):
            d_glob_sum = d_glob_sum + (self.sequences.logs.loggedunadjustedglobalradiation[idx])
        d_glob_mean = d_glob_sum / self.parameters.derived.nmblogentries
        self.sequences.fluxes.globalradiation = (            self.sequences.fluxes.unadjustedglobalradiation * self.sequences.fluxes.dailyglobalradiation / d_glob_mean        )
    cpdef inline double return_dailyglobalradiation_v1(self, double sunshineduration, double possiblesunshineduration)  nogil:
        cdef int idx
        if possiblesunshineduration > 0.0:
            idx = self.parameters.derived.moy[self.idx_sim]
            if (sunshineduration <= 0.0) and (self.parameters.derived.days >= 1.0):
                return self.sequences.fluxes.extraterrestrialradiation * self.parameters.control.angstromalternative[idx]
            return self.sequences.fluxes.extraterrestrialradiation * (                self.parameters.control.angstromconstant[idx]                + self.parameters.control.angstromfactor[idx] * sunshineduration / possiblesunshineduration            )
        return 0.0
    cpdef inline double return_dailyglobalradiation(self, double sunshineduration, double possiblesunshineduration)  nogil:
        cdef int idx
        if possiblesunshineduration > 0.0:
            idx = self.parameters.derived.moy[self.idx_sim]
            if (sunshineduration <= 0.0) and (self.parameters.derived.days >= 1.0):
                return self.sequences.fluxes.extraterrestrialradiation * self.parameters.control.angstromalternative[idx]
            return self.sequences.fluxes.extraterrestrialradiation * (                self.parameters.control.angstromconstant[idx]                + self.parameters.control.angstromfactor[idx] * sunshineduration / possiblesunshineduration            )
        return 0.0
