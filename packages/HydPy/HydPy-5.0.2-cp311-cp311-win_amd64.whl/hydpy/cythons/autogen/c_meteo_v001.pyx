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
@cython.final
cdef class DerivedParameters:
    cdef public numpy.int32_t[:] doy
    cdef public numpy.int32_t[:] moy
    cdef public double hours
    cdef public double days
    cdef public double[:] sct
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
    cdef public double sunsethourangle
    cdef public int _sunsethourangle_ndim
    cdef public int _sunsethourangle_length
    cdef public bint _sunsethourangle_ramflag
    cdef public double[:] _sunsethourangle_array
    cdef public bint _sunsethourangle_diskflag_reading
    cdef public bint _sunsethourangle_diskflag_writing
    cdef public double[:] _sunsethourangle_ncarray
    cdef public bint _sunsethourangle_outputflag
    cdef double *_sunsethourangle_outputpointer
    cdef public double solartimeangle
    cdef public int _solartimeangle_ndim
    cdef public int _solartimeangle_length
    cdef public bint _solartimeangle_ramflag
    cdef public double[:] _solartimeangle_array
    cdef public bint _solartimeangle_diskflag_reading
    cdef public bint _solartimeangle_diskflag_writing
    cdef public double[:] _solartimeangle_ncarray
    cdef public bint _solartimeangle_outputflag
    cdef double *_solartimeangle_outputpointer
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
        if self._sunsethourangle_diskflag_reading:
            self.sunsethourangle = self._sunsethourangle_ncarray[0]
        elif self._sunsethourangle_ramflag:
            self.sunsethourangle = self._sunsethourangle_array[idx]
        if self._solartimeangle_diskflag_reading:
            self.solartimeangle = self._solartimeangle_ncarray[0]
        elif self._solartimeangle_ramflag:
            self.solartimeangle = self._solartimeangle_array[idx]
        if self._possiblesunshineduration_diskflag_reading:
            self.possiblesunshineduration = self._possiblesunshineduration_ncarray[0]
        elif self._possiblesunshineduration_ramflag:
            self.possiblesunshineduration = self._possiblesunshineduration_array[idx]
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
        if self._sunsethourangle_diskflag_writing:
            self._sunsethourangle_ncarray[0] = self.sunsethourangle
        if self._sunsethourangle_ramflag:
            self._sunsethourangle_array[idx] = self.sunsethourangle
        if self._solartimeangle_diskflag_writing:
            self._solartimeangle_ncarray[0] = self.solartimeangle
        if self._solartimeangle_ramflag:
            self._solartimeangle_array[idx] = self.solartimeangle
        if self._possiblesunshineduration_diskflag_writing:
            self._possiblesunshineduration_ncarray[0] = self.possiblesunshineduration
        if self._possiblesunshineduration_ramflag:
            self._possiblesunshineduration_array[idx] = self.possiblesunshineduration
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "earthsundistance":
            self._earthsundistance_outputpointer = value.p_value
        if name == "solardeclination":
            self._solardeclination_outputpointer = value.p_value
        if name == "sunsethourangle":
            self._sunsethourangle_outputpointer = value.p_value
        if name == "solartimeangle":
            self._solartimeangle_outputpointer = value.p_value
        if name == "possiblesunshineduration":
            self._possiblesunshineduration_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._earthsundistance_outputflag:
            self._earthsundistance_outputpointer[0] = self.earthsundistance
        if self._solardeclination_outputflag:
            self._solardeclination_outputpointer[0] = self.solardeclination
        if self._sunsethourangle_outputflag:
            self._sunsethourangle_outputpointer[0] = self.sunsethourangle
        if self._solartimeangle_outputflag:
            self._solartimeangle_outputpointer[0] = self.solartimeangle
        if self._possiblesunshineduration_outputflag:
            self._possiblesunshineduration_outputpointer[0] = self.possiblesunshineduration
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
    cdef public double clearskysolarradiation
    cdef public int _clearskysolarradiation_ndim
    cdef public int _clearskysolarradiation_length
    cdef public bint _clearskysolarradiation_ramflag
    cdef public double[:] _clearskysolarradiation_array
    cdef public bint _clearskysolarradiation_diskflag_reading
    cdef public bint _clearskysolarradiation_diskflag_writing
    cdef public double[:] _clearskysolarradiation_ncarray
    cdef public bint _clearskysolarradiation_outputflag
    cdef double *_clearskysolarradiation_outputpointer
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
        if self._clearskysolarradiation_diskflag_reading:
            self.clearskysolarradiation = self._clearskysolarradiation_ncarray[0]
        elif self._clearskysolarradiation_ramflag:
            self.clearskysolarradiation = self._clearskysolarradiation_array[idx]
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
        if self._clearskysolarradiation_diskflag_writing:
            self._clearskysolarradiation_ncarray[0] = self.clearskysolarradiation
        if self._clearskysolarradiation_ramflag:
            self._clearskysolarradiation_array[idx] = self.clearskysolarradiation
        if self._globalradiation_diskflag_writing:
            self._globalradiation_ncarray[0] = self.globalradiation
        if self._globalradiation_ramflag:
            self._globalradiation_array[idx] = self.globalradiation
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "extraterrestrialradiation":
            self._extraterrestrialradiation_outputpointer = value.p_value
        if name == "clearskysolarradiation":
            self._clearskysolarradiation_outputpointer = value.p_value
        if name == "globalradiation":
            self._globalradiation_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._extraterrestrialradiation_outputflag:
            self._extraterrestrialradiation_outputpointer[0] = self.extraterrestrialradiation
        if self._clearskysolarradiation_outputflag:
            self._clearskysolarradiation_outputpointer[0] = self.clearskysolarradiation
        if self._globalradiation_outputflag:
            self._globalradiation_outputpointer[0] = self.globalradiation


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
        self.calc_solardeclination_v1()
        self.calc_sunsethourangle_v1()
        self.calc_solartimeangle_v1()
        self.calc_possiblesunshineduration_v1()
        self.calc_extraterrestrialradiation_v1()
        self.calc_clearskysolarradiation_v1()
        self.calc_globalradiation_v1()
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
    cpdef inline void calc_solardeclination_v1(self)  nogil:
        self.sequences.factors.solardeclination = 0.409 * sin(            2 * self.parameters.fixed.pi / 366 * (self.parameters.derived.doy[self.idx_sim] + 1) - 1.39        )
    cpdef inline void calc_sunsethourangle_v1(self)  nogil:
        self.sequences.factors.sunsethourangle = acos(            -tan(self.parameters.derived.latituderad) * tan(self.sequences.factors.solardeclination)        )
    cpdef inline void calc_solartimeangle_v1(self)  nogil:
        cdef double d_time
        cdef double d_sc
        cdef double d_b
        d_b = 2.0 * self.parameters.fixed.pi * (self.parameters.derived.doy[self.idx_sim] - 80.0) / 365.0
        d_sc = (            0.1645 * sin(2.0 * d_b)            - 0.1255 * cos(d_b)            - 0.025 * sin(d_b)        )
        d_time = (            self.parameters.derived.sct[self.idx_sim] + (self.parameters.control.longitude - self.parameters.derived.utclongitude) / 15.0 + d_sc        )
        self.sequences.factors.solartimeangle = self.parameters.fixed.pi / 12.0 * (d_time - 12.0)
    cpdef inline void calc_possiblesunshineduration_v1(self)  nogil:
        cdef double d_thresh
        if self.parameters.derived.hours < 24.0:
            if self.sequences.factors.solartimeangle <= 0.0:
                d_thresh = -self.sequences.factors.solartimeangle - self.parameters.fixed.pi * self.parameters.derived.days
            else:
                d_thresh = self.sequences.factors.solartimeangle - self.parameters.fixed.pi * self.parameters.derived.days
            self.sequences.factors.possiblesunshineduration = min(                max(12.0 / self.parameters.fixed.pi * (self.sequences.factors.sunsethourangle - d_thresh), 0.0), self.parameters.derived.hours            )
        else:
            self.sequences.factors.possiblesunshineduration = 24.0 / self.parameters.fixed.pi * self.sequences.factors.sunsethourangle
    cpdef inline void calc_extraterrestrialradiation_v1(self)  nogil:
        cdef double d_omega2
        cdef double d_omega1
        cdef double d_delta
        if self.parameters.derived.days < 1.0:
            d_delta = self.parameters.fixed.pi * self.parameters.derived.days
            d_omega1 = self.sequences.factors.solartimeangle - d_delta
            d_omega2 = self.sequences.factors.solartimeangle + d_delta
            self.sequences.fluxes.extraterrestrialradiation = max(                (12.0 * self.parameters.fixed.solarconstant / self.parameters.fixed.pi * self.sequences.factors.earthsundistance)                * (                    (                        (d_omega2 - d_omega1)                        * sin(self.parameters.derived.latituderad)                        * sin(self.sequences.factors.solardeclination)                    )                    + (                        cos(self.parameters.derived.latituderad)                        * cos(self.sequences.factors.solardeclination)                        * (sin(d_omega2) - sin(d_omega1))                    )                ),                0.0,            )
        else:
            self.sequences.fluxes.extraterrestrialradiation = (                self.parameters.fixed.solarconstant / self.parameters.fixed.pi * self.sequences.factors.earthsundistance            ) * (                (                    self.sequences.factors.sunsethourangle                    * sin(self.parameters.derived.latituderad)                    * sin(self.sequences.factors.solardeclination)                )                + (                    cos(self.parameters.derived.latituderad)                    * cos(self.sequences.factors.solardeclination)                    * sin(self.sequences.factors.sunsethourangle)                )            )
    cpdef inline void calc_clearskysolarradiation_v1(self)  nogil:
        cdef int idx
        idx = self.parameters.derived.moy[self.idx_sim]
        self.sequences.fluxes.clearskysolarradiation = self.sequences.fluxes.extraterrestrialradiation * (            self.parameters.control.angstromconstant[idx] + self.parameters.control.angstromfactor[idx]        )
    cpdef inline void calc_globalradiation_v1(self)  nogil:
        cdef int idx
        if self.sequences.factors.possiblesunshineduration > 0.0:
            idx = self.parameters.derived.moy[self.idx_sim]
            self.sequences.fluxes.globalradiation = self.sequences.fluxes.extraterrestrialradiation * (                self.parameters.control.angstromconstant[idx]                + self.parameters.control.angstromfactor[idx]                * self.sequences.inputs.sunshineduration                / self.sequences.factors.possiblesunshineduration            )
        else:
            self.sequences.fluxes.globalradiation = 0.0
    cpdef inline void calc_earthsundistance(self)  nogil:
        self.sequences.factors.earthsundistance = 1.0 + 0.033 * cos(            2 * self.parameters.fixed.pi / 366.0 * (self.parameters.derived.doy[self.idx_sim] + 1)        )
    cpdef inline void calc_solardeclination(self)  nogil:
        self.sequences.factors.solardeclination = 0.409 * sin(            2 * self.parameters.fixed.pi / 366 * (self.parameters.derived.doy[self.idx_sim] + 1) - 1.39        )
    cpdef inline void calc_sunsethourangle(self)  nogil:
        self.sequences.factors.sunsethourangle = acos(            -tan(self.parameters.derived.latituderad) * tan(self.sequences.factors.solardeclination)        )
    cpdef inline void calc_solartimeangle(self)  nogil:
        cdef double d_time
        cdef double d_sc
        cdef double d_b
        d_b = 2.0 * self.parameters.fixed.pi * (self.parameters.derived.doy[self.idx_sim] - 80.0) / 365.0
        d_sc = (            0.1645 * sin(2.0 * d_b)            - 0.1255 * cos(d_b)            - 0.025 * sin(d_b)        )
        d_time = (            self.parameters.derived.sct[self.idx_sim] + (self.parameters.control.longitude - self.parameters.derived.utclongitude) / 15.0 + d_sc        )
        self.sequences.factors.solartimeangle = self.parameters.fixed.pi / 12.0 * (d_time - 12.0)
    cpdef inline void calc_possiblesunshineduration(self)  nogil:
        cdef double d_thresh
        if self.parameters.derived.hours < 24.0:
            if self.sequences.factors.solartimeangle <= 0.0:
                d_thresh = -self.sequences.factors.solartimeangle - self.parameters.fixed.pi * self.parameters.derived.days
            else:
                d_thresh = self.sequences.factors.solartimeangle - self.parameters.fixed.pi * self.parameters.derived.days
            self.sequences.factors.possiblesunshineduration = min(                max(12.0 / self.parameters.fixed.pi * (self.sequences.factors.sunsethourangle - d_thresh), 0.0), self.parameters.derived.hours            )
        else:
            self.sequences.factors.possiblesunshineduration = 24.0 / self.parameters.fixed.pi * self.sequences.factors.sunsethourangle
    cpdef inline void calc_extraterrestrialradiation(self)  nogil:
        cdef double d_omega2
        cdef double d_omega1
        cdef double d_delta
        if self.parameters.derived.days < 1.0:
            d_delta = self.parameters.fixed.pi * self.parameters.derived.days
            d_omega1 = self.sequences.factors.solartimeangle - d_delta
            d_omega2 = self.sequences.factors.solartimeangle + d_delta
            self.sequences.fluxes.extraterrestrialradiation = max(                (12.0 * self.parameters.fixed.solarconstant / self.parameters.fixed.pi * self.sequences.factors.earthsundistance)                * (                    (                        (d_omega2 - d_omega1)                        * sin(self.parameters.derived.latituderad)                        * sin(self.sequences.factors.solardeclination)                    )                    + (                        cos(self.parameters.derived.latituderad)                        * cos(self.sequences.factors.solardeclination)                        * (sin(d_omega2) - sin(d_omega1))                    )                ),                0.0,            )
        else:
            self.sequences.fluxes.extraterrestrialradiation = (                self.parameters.fixed.solarconstant / self.parameters.fixed.pi * self.sequences.factors.earthsundistance            ) * (                (                    self.sequences.factors.sunsethourangle                    * sin(self.parameters.derived.latituderad)                    * sin(self.sequences.factors.solardeclination)                )                + (                    cos(self.parameters.derived.latituderad)                    * cos(self.sequences.factors.solardeclination)                    * sin(self.sequences.factors.sunsethourangle)                )            )
    cpdef inline void calc_clearskysolarradiation(self)  nogil:
        cdef int idx
        idx = self.parameters.derived.moy[self.idx_sim]
        self.sequences.fluxes.clearskysolarradiation = self.sequences.fluxes.extraterrestrialradiation * (            self.parameters.control.angstromconstant[idx] + self.parameters.control.angstromfactor[idx]        )
    cpdef inline void calc_globalradiation(self)  nogil:
        cdef int idx
        if self.sequences.factors.possiblesunshineduration > 0.0:
            idx = self.parameters.derived.moy[self.idx_sim]
            self.sequences.fluxes.globalradiation = self.sequences.fluxes.extraterrestrialradiation * (                self.parameters.control.angstromconstant[idx]                + self.parameters.control.angstromfactor[idx]                * self.sequences.inputs.sunshineduration                / self.sequences.factors.possiblesunshineduration            )
        else:
            self.sequences.fluxes.globalradiation = 0.0
