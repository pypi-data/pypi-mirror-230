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
@cython.final
cdef class ControlParameters:
    cdef public double measuringheightwindspeed
@cython.final
cdef class DerivedParameters:
    cdef public double hours
    cdef public double days
    cdef public numpy.int32_t nmblogentries
@cython.final
cdef class Sequences:
    cdef public InputSequences inputs
    cdef public FactorSequences factors
    cdef public FluxSequences fluxes
    cdef public LogSequences logs
@cython.final
cdef class InputSequences:
    cdef public double airtemperature
    cdef public int _airtemperature_ndim
    cdef public int _airtemperature_length
    cdef public bint _airtemperature_ramflag
    cdef public double[:] _airtemperature_array
    cdef public bint _airtemperature_diskflag_reading
    cdef public bint _airtemperature_diskflag_writing
    cdef public double[:] _airtemperature_ncarray
    cdef public bint _airtemperature_inputflag
    cdef double *_airtemperature_inputpointer
    cdef public double relativehumidity
    cdef public int _relativehumidity_ndim
    cdef public int _relativehumidity_length
    cdef public bint _relativehumidity_ramflag
    cdef public double[:] _relativehumidity_array
    cdef public bint _relativehumidity_diskflag_reading
    cdef public bint _relativehumidity_diskflag_writing
    cdef public double[:] _relativehumidity_ncarray
    cdef public bint _relativehumidity_inputflag
    cdef double *_relativehumidity_inputpointer
    cdef public double windspeed
    cdef public int _windspeed_ndim
    cdef public int _windspeed_length
    cdef public bint _windspeed_ramflag
    cdef public double[:] _windspeed_array
    cdef public bint _windspeed_diskflag_reading
    cdef public bint _windspeed_diskflag_writing
    cdef public double[:] _windspeed_ncarray
    cdef public bint _windspeed_inputflag
    cdef double *_windspeed_inputpointer
    cdef public double atmosphericpressure
    cdef public int _atmosphericpressure_ndim
    cdef public int _atmosphericpressure_length
    cdef public bint _atmosphericpressure_ramflag
    cdef public double[:] _atmosphericpressure_array
    cdef public bint _atmosphericpressure_diskflag_reading
    cdef public bint _atmosphericpressure_diskflag_writing
    cdef public double[:] _atmosphericpressure_ncarray
    cdef public bint _atmosphericpressure_inputflag
    cdef double *_atmosphericpressure_inputpointer
    cdef public double globalradiation
    cdef public int _globalradiation_ndim
    cdef public int _globalradiation_length
    cdef public bint _globalradiation_ramflag
    cdef public double[:] _globalradiation_array
    cdef public bint _globalradiation_diskflag_reading
    cdef public bint _globalradiation_diskflag_writing
    cdef public double[:] _globalradiation_ncarray
    cdef public bint _globalradiation_inputflag
    cdef double *_globalradiation_inputpointer
    cdef public double clearskysolarradiation
    cdef public int _clearskysolarradiation_ndim
    cdef public int _clearskysolarradiation_length
    cdef public bint _clearskysolarradiation_ramflag
    cdef public double[:] _clearskysolarradiation_array
    cdef public bint _clearskysolarradiation_diskflag_reading
    cdef public bint _clearskysolarradiation_diskflag_writing
    cdef public double[:] _clearskysolarradiation_ncarray
    cdef public bint _clearskysolarradiation_inputflag
    cdef double *_clearskysolarradiation_inputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._airtemperature_inputflag:
            self.airtemperature = self._airtemperature_inputpointer[0]
        elif self._airtemperature_diskflag_reading:
            self.airtemperature = self._airtemperature_ncarray[0]
        elif self._airtemperature_ramflag:
            self.airtemperature = self._airtemperature_array[idx]
        if self._relativehumidity_inputflag:
            self.relativehumidity = self._relativehumidity_inputpointer[0]
        elif self._relativehumidity_diskflag_reading:
            self.relativehumidity = self._relativehumidity_ncarray[0]
        elif self._relativehumidity_ramflag:
            self.relativehumidity = self._relativehumidity_array[idx]
        if self._windspeed_inputflag:
            self.windspeed = self._windspeed_inputpointer[0]
        elif self._windspeed_diskflag_reading:
            self.windspeed = self._windspeed_ncarray[0]
        elif self._windspeed_ramflag:
            self.windspeed = self._windspeed_array[idx]
        if self._atmosphericpressure_inputflag:
            self.atmosphericpressure = self._atmosphericpressure_inputpointer[0]
        elif self._atmosphericpressure_diskflag_reading:
            self.atmosphericpressure = self._atmosphericpressure_ncarray[0]
        elif self._atmosphericpressure_ramflag:
            self.atmosphericpressure = self._atmosphericpressure_array[idx]
        if self._globalradiation_inputflag:
            self.globalradiation = self._globalradiation_inputpointer[0]
        elif self._globalradiation_diskflag_reading:
            self.globalradiation = self._globalradiation_ncarray[0]
        elif self._globalradiation_ramflag:
            self.globalradiation = self._globalradiation_array[idx]
        if self._clearskysolarradiation_inputflag:
            self.clearskysolarradiation = self._clearskysolarradiation_inputpointer[0]
        elif self._clearskysolarradiation_diskflag_reading:
            self.clearskysolarradiation = self._clearskysolarradiation_ncarray[0]
        elif self._clearskysolarradiation_ramflag:
            self.clearskysolarradiation = self._clearskysolarradiation_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._airtemperature_diskflag_writing:
            self._airtemperature_ncarray[0] = self.airtemperature
        if self._airtemperature_ramflag:
            self._airtemperature_array[idx] = self.airtemperature
        if self._relativehumidity_diskflag_writing:
            self._relativehumidity_ncarray[0] = self.relativehumidity
        if self._relativehumidity_ramflag:
            self._relativehumidity_array[idx] = self.relativehumidity
        if self._windspeed_diskflag_writing:
            self._windspeed_ncarray[0] = self.windspeed
        if self._windspeed_ramflag:
            self._windspeed_array[idx] = self.windspeed
        if self._atmosphericpressure_diskflag_writing:
            self._atmosphericpressure_ncarray[0] = self.atmosphericpressure
        if self._atmosphericpressure_ramflag:
            self._atmosphericpressure_array[idx] = self.atmosphericpressure
        if self._globalradiation_diskflag_writing:
            self._globalradiation_ncarray[0] = self.globalradiation
        if self._globalradiation_ramflag:
            self._globalradiation_array[idx] = self.globalradiation
        if self._clearskysolarradiation_diskflag_writing:
            self._clearskysolarradiation_ncarray[0] = self.clearskysolarradiation
        if self._clearskysolarradiation_ramflag:
            self._clearskysolarradiation_array[idx] = self.clearskysolarradiation
    cpdef inline set_pointerinput(self, str name, pointerutils.PDouble value):
        if name == "airtemperature":
            self._airtemperature_inputpointer = value.p_value
        if name == "relativehumidity":
            self._relativehumidity_inputpointer = value.p_value
        if name == "windspeed":
            self._windspeed_inputpointer = value.p_value
        if name == "atmosphericpressure":
            self._atmosphericpressure_inputpointer = value.p_value
        if name == "globalradiation":
            self._globalradiation_inputpointer = value.p_value
        if name == "clearskysolarradiation":
            self._clearskysolarradiation_inputpointer = value.p_value
@cython.final
cdef class FactorSequences:
    cdef public double adjustedwindspeed
    cdef public int _adjustedwindspeed_ndim
    cdef public int _adjustedwindspeed_length
    cdef public bint _adjustedwindspeed_ramflag
    cdef public double[:] _adjustedwindspeed_array
    cdef public bint _adjustedwindspeed_diskflag_reading
    cdef public bint _adjustedwindspeed_diskflag_writing
    cdef public double[:] _adjustedwindspeed_ncarray
    cdef public bint _adjustedwindspeed_outputflag
    cdef double *_adjustedwindspeed_outputpointer
    cdef public double saturationvapourpressure
    cdef public int _saturationvapourpressure_ndim
    cdef public int _saturationvapourpressure_length
    cdef public bint _saturationvapourpressure_ramflag
    cdef public double[:] _saturationvapourpressure_array
    cdef public bint _saturationvapourpressure_diskflag_reading
    cdef public bint _saturationvapourpressure_diskflag_writing
    cdef public double[:] _saturationvapourpressure_ncarray
    cdef public bint _saturationvapourpressure_outputflag
    cdef double *_saturationvapourpressure_outputpointer
    cdef public double saturationvapourpressureslope
    cdef public int _saturationvapourpressureslope_ndim
    cdef public int _saturationvapourpressureslope_length
    cdef public bint _saturationvapourpressureslope_ramflag
    cdef public double[:] _saturationvapourpressureslope_array
    cdef public bint _saturationvapourpressureslope_diskflag_reading
    cdef public bint _saturationvapourpressureslope_diskflag_writing
    cdef public double[:] _saturationvapourpressureslope_ncarray
    cdef public bint _saturationvapourpressureslope_outputflag
    cdef double *_saturationvapourpressureslope_outputpointer
    cdef public double actualvapourpressure
    cdef public int _actualvapourpressure_ndim
    cdef public int _actualvapourpressure_length
    cdef public bint _actualvapourpressure_ramflag
    cdef public double[:] _actualvapourpressure_array
    cdef public bint _actualvapourpressure_diskflag_reading
    cdef public bint _actualvapourpressure_diskflag_writing
    cdef public double[:] _actualvapourpressure_ncarray
    cdef public bint _actualvapourpressure_outputflag
    cdef double *_actualvapourpressure_outputpointer
    cdef public double psychrometricconstant
    cdef public int _psychrometricconstant_ndim
    cdef public int _psychrometricconstant_length
    cdef public bint _psychrometricconstant_ramflag
    cdef public double[:] _psychrometricconstant_array
    cdef public bint _psychrometricconstant_diskflag_reading
    cdef public bint _psychrometricconstant_diskflag_writing
    cdef public double[:] _psychrometricconstant_ncarray
    cdef public bint _psychrometricconstant_outputflag
    cdef double *_psychrometricconstant_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._adjustedwindspeed_diskflag_reading:
            self.adjustedwindspeed = self._adjustedwindspeed_ncarray[0]
        elif self._adjustedwindspeed_ramflag:
            self.adjustedwindspeed = self._adjustedwindspeed_array[idx]
        if self._saturationvapourpressure_diskflag_reading:
            self.saturationvapourpressure = self._saturationvapourpressure_ncarray[0]
        elif self._saturationvapourpressure_ramflag:
            self.saturationvapourpressure = self._saturationvapourpressure_array[idx]
        if self._saturationvapourpressureslope_diskflag_reading:
            self.saturationvapourpressureslope = self._saturationvapourpressureslope_ncarray[0]
        elif self._saturationvapourpressureslope_ramflag:
            self.saturationvapourpressureslope = self._saturationvapourpressureslope_array[idx]
        if self._actualvapourpressure_diskflag_reading:
            self.actualvapourpressure = self._actualvapourpressure_ncarray[0]
        elif self._actualvapourpressure_ramflag:
            self.actualvapourpressure = self._actualvapourpressure_array[idx]
        if self._psychrometricconstant_diskflag_reading:
            self.psychrometricconstant = self._psychrometricconstant_ncarray[0]
        elif self._psychrometricconstant_ramflag:
            self.psychrometricconstant = self._psychrometricconstant_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._adjustedwindspeed_diskflag_writing:
            self._adjustedwindspeed_ncarray[0] = self.adjustedwindspeed
        if self._adjustedwindspeed_ramflag:
            self._adjustedwindspeed_array[idx] = self.adjustedwindspeed
        if self._saturationvapourpressure_diskflag_writing:
            self._saturationvapourpressure_ncarray[0] = self.saturationvapourpressure
        if self._saturationvapourpressure_ramflag:
            self._saturationvapourpressure_array[idx] = self.saturationvapourpressure
        if self._saturationvapourpressureslope_diskflag_writing:
            self._saturationvapourpressureslope_ncarray[0] = self.saturationvapourpressureslope
        if self._saturationvapourpressureslope_ramflag:
            self._saturationvapourpressureslope_array[idx] = self.saturationvapourpressureslope
        if self._actualvapourpressure_diskflag_writing:
            self._actualvapourpressure_ncarray[0] = self.actualvapourpressure
        if self._actualvapourpressure_ramflag:
            self._actualvapourpressure_array[idx] = self.actualvapourpressure
        if self._psychrometricconstant_diskflag_writing:
            self._psychrometricconstant_ncarray[0] = self.psychrometricconstant
        if self._psychrometricconstant_ramflag:
            self._psychrometricconstant_array[idx] = self.psychrometricconstant
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "adjustedwindspeed":
            self._adjustedwindspeed_outputpointer = value.p_value
        if name == "saturationvapourpressure":
            self._saturationvapourpressure_outputpointer = value.p_value
        if name == "saturationvapourpressureslope":
            self._saturationvapourpressureslope_outputpointer = value.p_value
        if name == "actualvapourpressure":
            self._actualvapourpressure_outputpointer = value.p_value
        if name == "psychrometricconstant":
            self._psychrometricconstant_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._adjustedwindspeed_outputflag:
            self._adjustedwindspeed_outputpointer[0] = self.adjustedwindspeed
        if self._saturationvapourpressure_outputflag:
            self._saturationvapourpressure_outputpointer[0] = self.saturationvapourpressure
        if self._saturationvapourpressureslope_outputflag:
            self._saturationvapourpressureslope_outputpointer[0] = self.saturationvapourpressureslope
        if self._actualvapourpressure_outputflag:
            self._actualvapourpressure_outputpointer[0] = self.actualvapourpressure
        if self._psychrometricconstant_outputflag:
            self._psychrometricconstant_outputpointer[0] = self.psychrometricconstant
@cython.final
cdef class FluxSequences:
    cdef public double netshortwaveradiation
    cdef public int _netshortwaveradiation_ndim
    cdef public int _netshortwaveradiation_length
    cdef public bint _netshortwaveradiation_ramflag
    cdef public double[:] _netshortwaveradiation_array
    cdef public bint _netshortwaveradiation_diskflag_reading
    cdef public bint _netshortwaveradiation_diskflag_writing
    cdef public double[:] _netshortwaveradiation_ncarray
    cdef public bint _netshortwaveradiation_outputflag
    cdef double *_netshortwaveradiation_outputpointer
    cdef public double netlongwaveradiation
    cdef public int _netlongwaveradiation_ndim
    cdef public int _netlongwaveradiation_length
    cdef public bint _netlongwaveradiation_ramflag
    cdef public double[:] _netlongwaveradiation_array
    cdef public bint _netlongwaveradiation_diskflag_reading
    cdef public bint _netlongwaveradiation_diskflag_writing
    cdef public double[:] _netlongwaveradiation_ncarray
    cdef public bint _netlongwaveradiation_outputflag
    cdef double *_netlongwaveradiation_outputpointer
    cdef public double netradiation
    cdef public int _netradiation_ndim
    cdef public int _netradiation_length
    cdef public bint _netradiation_ramflag
    cdef public double[:] _netradiation_array
    cdef public bint _netradiation_diskflag_reading
    cdef public bint _netradiation_diskflag_writing
    cdef public double[:] _netradiation_ncarray
    cdef public bint _netradiation_outputflag
    cdef double *_netradiation_outputpointer
    cdef public double soilheatflux
    cdef public int _soilheatflux_ndim
    cdef public int _soilheatflux_length
    cdef public bint _soilheatflux_ramflag
    cdef public double[:] _soilheatflux_array
    cdef public bint _soilheatflux_diskflag_reading
    cdef public bint _soilheatflux_diskflag_writing
    cdef public double[:] _soilheatflux_ncarray
    cdef public bint _soilheatflux_outputflag
    cdef double *_soilheatflux_outputpointer
    cdef public double referenceevapotranspiration
    cdef public int _referenceevapotranspiration_ndim
    cdef public int _referenceevapotranspiration_length
    cdef public bint _referenceevapotranspiration_ramflag
    cdef public double[:] _referenceevapotranspiration_array
    cdef public bint _referenceevapotranspiration_diskflag_reading
    cdef public bint _referenceevapotranspiration_diskflag_writing
    cdef public double[:] _referenceevapotranspiration_ncarray
    cdef public bint _referenceevapotranspiration_outputflag
    cdef double *_referenceevapotranspiration_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._netshortwaveradiation_diskflag_reading:
            self.netshortwaveradiation = self._netshortwaveradiation_ncarray[0]
        elif self._netshortwaveradiation_ramflag:
            self.netshortwaveradiation = self._netshortwaveradiation_array[idx]
        if self._netlongwaveradiation_diskflag_reading:
            self.netlongwaveradiation = self._netlongwaveradiation_ncarray[0]
        elif self._netlongwaveradiation_ramflag:
            self.netlongwaveradiation = self._netlongwaveradiation_array[idx]
        if self._netradiation_diskflag_reading:
            self.netradiation = self._netradiation_ncarray[0]
        elif self._netradiation_ramflag:
            self.netradiation = self._netradiation_array[idx]
        if self._soilheatflux_diskflag_reading:
            self.soilheatflux = self._soilheatflux_ncarray[0]
        elif self._soilheatflux_ramflag:
            self.soilheatflux = self._soilheatflux_array[idx]
        if self._referenceevapotranspiration_diskflag_reading:
            self.referenceevapotranspiration = self._referenceevapotranspiration_ncarray[0]
        elif self._referenceevapotranspiration_ramflag:
            self.referenceevapotranspiration = self._referenceevapotranspiration_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._netshortwaveradiation_diskflag_writing:
            self._netshortwaveradiation_ncarray[0] = self.netshortwaveradiation
        if self._netshortwaveradiation_ramflag:
            self._netshortwaveradiation_array[idx] = self.netshortwaveradiation
        if self._netlongwaveradiation_diskflag_writing:
            self._netlongwaveradiation_ncarray[0] = self.netlongwaveradiation
        if self._netlongwaveradiation_ramflag:
            self._netlongwaveradiation_array[idx] = self.netlongwaveradiation
        if self._netradiation_diskflag_writing:
            self._netradiation_ncarray[0] = self.netradiation
        if self._netradiation_ramflag:
            self._netradiation_array[idx] = self.netradiation
        if self._soilheatflux_diskflag_writing:
            self._soilheatflux_ncarray[0] = self.soilheatflux
        if self._soilheatflux_ramflag:
            self._soilheatflux_array[idx] = self.soilheatflux
        if self._referenceevapotranspiration_diskflag_writing:
            self._referenceevapotranspiration_ncarray[0] = self.referenceevapotranspiration
        if self._referenceevapotranspiration_ramflag:
            self._referenceevapotranspiration_array[idx] = self.referenceevapotranspiration
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "netshortwaveradiation":
            self._netshortwaveradiation_outputpointer = value.p_value
        if name == "netlongwaveradiation":
            self._netlongwaveradiation_outputpointer = value.p_value
        if name == "netradiation":
            self._netradiation_outputpointer = value.p_value
        if name == "soilheatflux":
            self._soilheatflux_outputpointer = value.p_value
        if name == "referenceevapotranspiration":
            self._referenceevapotranspiration_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._netshortwaveradiation_outputflag:
            self._netshortwaveradiation_outputpointer[0] = self.netshortwaveradiation
        if self._netlongwaveradiation_outputflag:
            self._netlongwaveradiation_outputpointer[0] = self.netlongwaveradiation
        if self._netradiation_outputflag:
            self._netradiation_outputpointer[0] = self.netradiation
        if self._soilheatflux_outputflag:
            self._soilheatflux_outputpointer[0] = self.soilheatflux
        if self._referenceevapotranspiration_outputflag:
            self._referenceevapotranspiration_outputpointer[0] = self.referenceevapotranspiration
@cython.final
cdef class LogSequences:
    cdef public double[:] loggedglobalradiation
    cdef public int _loggedglobalradiation_ndim
    cdef public int _loggedglobalradiation_length
    cdef public int _loggedglobalradiation_length_0
    cdef public double[:] loggedclearskysolarradiation
    cdef public int _loggedclearskysolarradiation_ndim
    cdef public int _loggedclearskysolarradiation_length
    cdef public int _loggedclearskysolarradiation_length_0


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
        self.calc_adjustedwindspeed_v1()
        self.calc_saturationvapourpressure_v1()
        self.calc_saturationvapourpressureslope_v1()
        self.calc_actualvapourpressure_v1()
        self.update_loggedclearskysolarradiation_v1()
        self.update_loggedglobalradiation_v1()
        self.calc_netshortwaveradiation_v1()
        self.calc_netlongwaveradiation_v1()
        self.calc_netradiation_v1()
        self.calc_soilheatflux_v1()
        self.calc_psychrometricconstant_v1()
        self.calc_referenceevapotranspiration_v1()
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

    cpdef inline void calc_adjustedwindspeed_v1(self)  nogil:
        cdef double d_z0
        cdef double d_d
        d_d = 2.0 / 3.0 * 0.12
        d_z0 = 0.123 * 0.12
        self.sequences.factors.adjustedwindspeed = self.sequences.inputs.windspeed * (            log((2.0 - d_d) / d_z0)            / log((self.parameters.control.measuringheightwindspeed - d_d) / d_z0)        )
    cpdef inline void calc_saturationvapourpressure_v1(self)  nogil:
        self.sequences.factors.saturationvapourpressure = 6.108 * exp(            17.27 * self.sequences.inputs.airtemperature / (self.sequences.inputs.airtemperature + 237.3)        )
    cpdef inline void calc_saturationvapourpressureslope_v1(self)  nogil:
        self.sequences.factors.saturationvapourpressureslope = (            4098.0 * self.sequences.factors.saturationvapourpressure / (self.sequences.inputs.airtemperature + 237.3) ** 2        )
    cpdef inline void calc_actualvapourpressure_v1(self)  nogil:
        self.sequences.factors.actualvapourpressure = (            self.sequences.factors.saturationvapourpressure * self.sequences.inputs.relativehumidity / 100.0        )
    cpdef inline void update_loggedclearskysolarradiation_v1(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedclearskysolarradiation[idx] = self.sequences.logs.loggedclearskysolarradiation[                idx - 1            ]
        self.sequences.logs.loggedclearskysolarradiation[0] = self.sequences.inputs.clearskysolarradiation
    cpdef inline void update_loggedglobalradiation_v1(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedglobalradiation[idx] = self.sequences.logs.loggedglobalradiation[idx - 1]
        self.sequences.logs.loggedglobalradiation[0] = self.sequences.inputs.globalradiation
    cpdef inline void calc_netshortwaveradiation_v1(self)  nogil:
        self.sequences.fluxes.netshortwaveradiation = (1.0 - 0.23) * self.sequences.inputs.globalradiation
    cpdef inline void calc_netlongwaveradiation_v1(self)  nogil:
        cdef int idx
        cdef double d_clearskysolarradiation
        cdef double d_globalradiation
        if self.sequences.inputs.clearskysolarradiation > 0.0:
            d_globalradiation = self.sequences.inputs.globalradiation
            d_clearskysolarradiation = self.sequences.inputs.clearskysolarradiation
        else:
            d_globalradiation = 0.0
            d_clearskysolarradiation = 0.0
            for idx in range(self.parameters.derived.nmblogentries):
                d_clearskysolarradiation = d_clearskysolarradiation + (self.sequences.logs.loggedclearskysolarradiation[idx])
                d_globalradiation = d_globalradiation + (self.sequences.logs.loggedglobalradiation[idx])
        self.sequences.fluxes.netlongwaveradiation = (            5.674768518518519e-08            * (self.sequences.inputs.airtemperature + 273.16) ** 4            * (0.34 - 0.14 * (self.sequences.factors.actualvapourpressure / 10.0) ** 0.5)            * (1.35 * d_globalradiation / d_clearskysolarradiation - 0.35)        )
    cpdef inline void calc_netradiation_v1(self)  nogil:
        self.sequences.fluxes.netradiation = self.sequences.fluxes.netshortwaveradiation - self.sequences.fluxes.netlongwaveradiation
    cpdef inline void calc_soilheatflux_v1(self)  nogil:
        if self.parameters.derived.days < 1.0:
            if self.sequences.fluxes.netradiation >= 0.0:
                self.sequences.fluxes.soilheatflux = 0.1 * self.sequences.fluxes.netradiation
            else:
                self.sequences.fluxes.soilheatflux = 0.5 * self.sequences.fluxes.netradiation
        else:
            self.sequences.fluxes.soilheatflux = 0.0
    cpdef inline void calc_psychrometricconstant_v1(self)  nogil:
        self.sequences.factors.psychrometricconstant = 6.65e-4 * self.sequences.inputs.atmosphericpressure
    cpdef inline void calc_referenceevapotranspiration_v1(self)  nogil:
        self.sequences.fluxes.referenceevapotranspiration = (            0.0352512            * self.parameters.derived.days            * self.sequences.factors.saturationvapourpressureslope            * (self.sequences.fluxes.netradiation - self.sequences.fluxes.soilheatflux)            + (self.sequences.factors.psychrometricconstant * 3.75 * self.parameters.derived.hours)            / (self.sequences.inputs.airtemperature + 273.0)            * self.sequences.factors.adjustedwindspeed            * (self.sequences.factors.saturationvapourpressure - self.sequences.factors.actualvapourpressure)        ) / (            self.sequences.factors.saturationvapourpressureslope            + self.sequences.factors.psychrometricconstant * (1.0 + 0.34 * self.sequences.factors.adjustedwindspeed)        )
    cpdef inline void calc_adjustedwindspeed(self)  nogil:
        cdef double d_z0
        cdef double d_d
        d_d = 2.0 / 3.0 * 0.12
        d_z0 = 0.123 * 0.12
        self.sequences.factors.adjustedwindspeed = self.sequences.inputs.windspeed * (            log((2.0 - d_d) / d_z0)            / log((self.parameters.control.measuringheightwindspeed - d_d) / d_z0)        )
    cpdef inline void calc_saturationvapourpressure(self)  nogil:
        self.sequences.factors.saturationvapourpressure = 6.108 * exp(            17.27 * self.sequences.inputs.airtemperature / (self.sequences.inputs.airtemperature + 237.3)        )
    cpdef inline void calc_saturationvapourpressureslope(self)  nogil:
        self.sequences.factors.saturationvapourpressureslope = (            4098.0 * self.sequences.factors.saturationvapourpressure / (self.sequences.inputs.airtemperature + 237.3) ** 2        )
    cpdef inline void calc_actualvapourpressure(self)  nogil:
        self.sequences.factors.actualvapourpressure = (            self.sequences.factors.saturationvapourpressure * self.sequences.inputs.relativehumidity / 100.0        )
    cpdef inline void update_loggedclearskysolarradiation(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedclearskysolarradiation[idx] = self.sequences.logs.loggedclearskysolarradiation[                idx - 1            ]
        self.sequences.logs.loggedclearskysolarradiation[0] = self.sequences.inputs.clearskysolarradiation
    cpdef inline void update_loggedglobalradiation(self)  nogil:
        cdef int idx
        for idx in range(self.parameters.derived.nmblogentries - 1, 0, -1):
            self.sequences.logs.loggedglobalradiation[idx] = self.sequences.logs.loggedglobalradiation[idx - 1]
        self.sequences.logs.loggedglobalradiation[0] = self.sequences.inputs.globalradiation
    cpdef inline void calc_netshortwaveradiation(self)  nogil:
        self.sequences.fluxes.netshortwaveradiation = (1.0 - 0.23) * self.sequences.inputs.globalradiation
    cpdef inline void calc_netlongwaveradiation(self)  nogil:
        cdef int idx
        cdef double d_clearskysolarradiation
        cdef double d_globalradiation
        if self.sequences.inputs.clearskysolarradiation > 0.0:
            d_globalradiation = self.sequences.inputs.globalradiation
            d_clearskysolarradiation = self.sequences.inputs.clearskysolarradiation
        else:
            d_globalradiation = 0.0
            d_clearskysolarradiation = 0.0
            for idx in range(self.parameters.derived.nmblogentries):
                d_clearskysolarradiation = d_clearskysolarradiation + (self.sequences.logs.loggedclearskysolarradiation[idx])
                d_globalradiation = d_globalradiation + (self.sequences.logs.loggedglobalradiation[idx])
        self.sequences.fluxes.netlongwaveradiation = (            5.674768518518519e-08            * (self.sequences.inputs.airtemperature + 273.16) ** 4            * (0.34 - 0.14 * (self.sequences.factors.actualvapourpressure / 10.0) ** 0.5)            * (1.35 * d_globalradiation / d_clearskysolarradiation - 0.35)        )
    cpdef inline void calc_netradiation(self)  nogil:
        self.sequences.fluxes.netradiation = self.sequences.fluxes.netshortwaveradiation - self.sequences.fluxes.netlongwaveradiation
    cpdef inline void calc_soilheatflux(self)  nogil:
        if self.parameters.derived.days < 1.0:
            if self.sequences.fluxes.netradiation >= 0.0:
                self.sequences.fluxes.soilheatflux = 0.1 * self.sequences.fluxes.netradiation
            else:
                self.sequences.fluxes.soilheatflux = 0.5 * self.sequences.fluxes.netradiation
        else:
            self.sequences.fluxes.soilheatflux = 0.0
    cpdef inline void calc_psychrometricconstant(self)  nogil:
        self.sequences.factors.psychrometricconstant = 6.65e-4 * self.sequences.inputs.atmosphericpressure
    cpdef inline void calc_referenceevapotranspiration(self)  nogil:
        self.sequences.fluxes.referenceevapotranspiration = (            0.0352512            * self.parameters.derived.days            * self.sequences.factors.saturationvapourpressureslope            * (self.sequences.fluxes.netradiation - self.sequences.fluxes.soilheatflux)            + (self.sequences.factors.psychrometricconstant * 3.75 * self.parameters.derived.hours)            / (self.sequences.inputs.airtemperature + 273.0)            * self.sequences.factors.adjustedwindspeed            * (self.sequences.factors.saturationvapourpressure - self.sequences.factors.actualvapourpressure)        ) / (            self.sequences.factors.saturationvapourpressureslope            + self.sequences.factors.psychrometricconstant * (1.0 + 0.34 * self.sequences.factors.adjustedwindspeed)        )
