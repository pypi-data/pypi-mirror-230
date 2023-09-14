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
cdef public numpy.int32_t SIED_D = 1
cdef public numpy.int32_t SIED_L = 2
cdef public numpy.int32_t VERS = 3
cdef public numpy.int32_t ACKER = 4
cdef public numpy.int32_t WEINB = 5
cdef public numpy.int32_t OBSTB = 6
cdef public numpy.int32_t BODEN = 7
cdef public numpy.int32_t GLETS = 8
cdef public numpy.int32_t GRUE_I = 9
cdef public numpy.int32_t FEUCHT = 10
cdef public numpy.int32_t GRUE_E = 11
cdef public numpy.int32_t BAUMB = 12
cdef public numpy.int32_t NADELW = 13
cdef public numpy.int32_t LAUBW = 14
cdef public numpy.int32_t MISCHW = 15
cdef public numpy.int32_t WASSER = 16
cdef public numpy.int32_t FLUSS = 17
cdef public numpy.int32_t SEE = 18
@cython.final
cdef class Parameters:
    cdef public ControlParameters control
    cdef public DerivedParameters derived
    cdef public FixedParameters fixed
@cython.final
cdef class ControlParameters:
    cdef public double ft
    cdef public numpy.int32_t nhru
    cdef public numpy.int32_t[:] lnk
    cdef public double[:] fhru
    cdef public double[:] kg
    cdef public double[:] kt
    cdef public double[:] ke
    cdef public double[:,:] lai
    cdef public double hinz
    cdef public double[:] treft
    cdef public double[:] trefn
    cdef public double[:] tgr
    cdef public double[:] tsp
    cdef public double[:] gtf
    cdef public double[:] pwmax
    cdef public double[:] wfet0
    cdef public double[:,:] fln
    cdef public double grasref_r
    cdef public double[:] wmax
    cdef public double[:] fk
    cdef public double[:] pwp
    cdef public double[:] bsf
    cdef public double[:] dmin
    cdef public double[:] dmax
    cdef public double[:] beta
    cdef public double[:] fbeta
    cdef public double[:] kapmax
    cdef public double[:,:] kapgrenz
    cdef public bint rbeta
    cdef public double volbmax
    cdef public double gsbmax
    cdef public double gsbgrad1
    cdef public double gsbgrad2
    cdef public double a1
    cdef public double a2
    cdef public double tind
    cdef public double eqb
    cdef public double eqi1
    cdef public double eqi2
    cdef public double eqd1
    cdef public double eqd2
    cdef public bint negq
@cython.final
cdef class DerivedParameters:
    cdef public numpy.int32_t[:] moy
    cdef public double[:] absfhru
    cdef public double[:,:] kinz
    cdef public double kb
    cdef public double ki1
    cdef public double ki2
    cdef public double kd1
    cdef public double kd2
    cdef public double qbgamax
    cdef public double qfactor
@cython.final
cdef class FixedParameters:
    cdef public double cpwasser
    cdef public double cpeis
    cdef public double rschmelz
@cython.final
cdef class Sequences:
    cdef public InletSequences inlets
    cdef public InputSequences inputs
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
    cdef public double nied
    cdef public int _nied_ndim
    cdef public int _nied_length
    cdef public bint _nied_ramflag
    cdef public double[:] _nied_array
    cdef public bint _nied_diskflag_reading
    cdef public bint _nied_diskflag_writing
    cdef public double[:] _nied_ncarray
    cdef public bint _nied_inputflag
    cdef double *_nied_inputpointer
    cdef public double teml
    cdef public int _teml_ndim
    cdef public int _teml_length
    cdef public bint _teml_ramflag
    cdef public double[:] _teml_array
    cdef public bint _teml_diskflag_reading
    cdef public bint _teml_diskflag_writing
    cdef public double[:] _teml_ncarray
    cdef public bint _teml_inputflag
    cdef double *_teml_inputpointer
    cdef public double pet
    cdef public int _pet_ndim
    cdef public int _pet_length
    cdef public bint _pet_ramflag
    cdef public double[:] _pet_array
    cdef public bint _pet_diskflag_reading
    cdef public bint _pet_diskflag_writing
    cdef public double[:] _pet_ncarray
    cdef public bint _pet_inputflag
    cdef double *_pet_inputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int k
        if self._nied_inputflag:
            self.nied = self._nied_inputpointer[0]
        elif self._nied_diskflag_reading:
            self.nied = self._nied_ncarray[0]
        elif self._nied_ramflag:
            self.nied = self._nied_array[idx]
        if self._teml_inputflag:
            self.teml = self._teml_inputpointer[0]
        elif self._teml_diskflag_reading:
            self.teml = self._teml_ncarray[0]
        elif self._teml_ramflag:
            self.teml = self._teml_array[idx]
        if self._pet_inputflag:
            self.pet = self._pet_inputpointer[0]
        elif self._pet_diskflag_reading:
            self.pet = self._pet_ncarray[0]
        elif self._pet_ramflag:
            self.pet = self._pet_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int k
        if self._nied_diskflag_writing:
            self._nied_ncarray[0] = self.nied
        if self._nied_ramflag:
            self._nied_array[idx] = self.nied
        if self._teml_diskflag_writing:
            self._teml_ncarray[0] = self.teml
        if self._teml_ramflag:
            self._teml_array[idx] = self.teml
        if self._pet_diskflag_writing:
            self._pet_ncarray[0] = self.pet
        if self._pet_ramflag:
            self._pet_array[idx] = self.pet
    cpdef inline set_pointerinput(self, str name, pointerutils.PDouble value):
        if name == "nied":
            self._nied_inputpointer = value.p_value
        if name == "teml":
            self._teml_inputpointer = value.p_value
        if name == "pet":
            self._pet_inputpointer = value.p_value
@cython.final
cdef class FluxSequences:
    cdef public double qz
    cdef public int _qz_ndim
    cdef public int _qz_length
    cdef public bint _qz_ramflag
    cdef public double[:] _qz_array
    cdef public bint _qz_diskflag_reading
    cdef public bint _qz_diskflag_writing
    cdef public double[:] _qz_ncarray
    cdef public bint _qz_outputflag
    cdef double *_qz_outputpointer
    cdef public double qzh
    cdef public int _qzh_ndim
    cdef public int _qzh_length
    cdef public bint _qzh_ramflag
    cdef public double[:] _qzh_array
    cdef public bint _qzh_diskflag_reading
    cdef public bint _qzh_diskflag_writing
    cdef public double[:] _qzh_ncarray
    cdef public bint _qzh_outputflag
    cdef double *_qzh_outputpointer
    cdef public double[:] nkor
    cdef public int _nkor_ndim
    cdef public int _nkor_length
    cdef public int _nkor_length_0
    cdef public bint _nkor_ramflag
    cdef public double[:,:] _nkor_array
    cdef public bint _nkor_diskflag_reading
    cdef public bint _nkor_diskflag_writing
    cdef public double[:] _nkor_ncarray
    cdef public bint _nkor_outputflag
    cdef double *_nkor_outputpointer
    cdef public double[:] tkor
    cdef public int _tkor_ndim
    cdef public int _tkor_length
    cdef public int _tkor_length_0
    cdef public bint _tkor_ramflag
    cdef public double[:,:] _tkor_array
    cdef public bint _tkor_diskflag_reading
    cdef public bint _tkor_diskflag_writing
    cdef public double[:] _tkor_ncarray
    cdef public bint _tkor_outputflag
    cdef double *_tkor_outputpointer
    cdef public double[:] nbes
    cdef public int _nbes_ndim
    cdef public int _nbes_length
    cdef public int _nbes_length_0
    cdef public bint _nbes_ramflag
    cdef public double[:,:] _nbes_array
    cdef public bint _nbes_diskflag_reading
    cdef public bint _nbes_diskflag_writing
    cdef public double[:] _nbes_ncarray
    cdef public bint _nbes_outputflag
    cdef double *_nbes_outputpointer
    cdef public double[:] sbes
    cdef public int _sbes_ndim
    cdef public int _sbes_length
    cdef public int _sbes_length_0
    cdef public bint _sbes_ramflag
    cdef public double[:,:] _sbes_array
    cdef public bint _sbes_diskflag_reading
    cdef public bint _sbes_diskflag_writing
    cdef public double[:] _sbes_ncarray
    cdef public bint _sbes_outputflag
    cdef double *_sbes_outputpointer
    cdef public double[:] et0
    cdef public int _et0_ndim
    cdef public int _et0_length
    cdef public int _et0_length_0
    cdef public bint _et0_ramflag
    cdef public double[:,:] _et0_array
    cdef public bint _et0_diskflag_reading
    cdef public bint _et0_diskflag_writing
    cdef public double[:] _et0_ncarray
    cdef public bint _et0_outputflag
    cdef double *_et0_outputpointer
    cdef public double[:] evpo
    cdef public int _evpo_ndim
    cdef public int _evpo_length
    cdef public int _evpo_length_0
    cdef public bint _evpo_ramflag
    cdef public double[:,:] _evpo_array
    cdef public bint _evpo_diskflag_reading
    cdef public bint _evpo_diskflag_writing
    cdef public double[:] _evpo_ncarray
    cdef public bint _evpo_outputflag
    cdef double *_evpo_outputpointer
    cdef public double[:] evi
    cdef public int _evi_ndim
    cdef public int _evi_length
    cdef public int _evi_length_0
    cdef public bint _evi_ramflag
    cdef public double[:,:] _evi_array
    cdef public bint _evi_diskflag_reading
    cdef public bint _evi_diskflag_writing
    cdef public double[:] _evi_ncarray
    cdef public bint _evi_outputflag
    cdef double *_evi_outputpointer
    cdef public double[:] evb
    cdef public int _evb_ndim
    cdef public int _evb_length
    cdef public int _evb_length_0
    cdef public bint _evb_ramflag
    cdef public double[:,:] _evb_array
    cdef public bint _evb_diskflag_reading
    cdef public bint _evb_diskflag_writing
    cdef public double[:] _evb_ncarray
    cdef public bint _evb_outputflag
    cdef double *_evb_outputpointer
    cdef public double[:] wgtf
    cdef public int _wgtf_ndim
    cdef public int _wgtf_length
    cdef public int _wgtf_length_0
    cdef public bint _wgtf_ramflag
    cdef public double[:,:] _wgtf_array
    cdef public bint _wgtf_diskflag_reading
    cdef public bint _wgtf_diskflag_writing
    cdef public double[:] _wgtf_ncarray
    cdef public bint _wgtf_outputflag
    cdef double *_wgtf_outputpointer
    cdef public double[:] wnied
    cdef public int _wnied_ndim
    cdef public int _wnied_length
    cdef public int _wnied_length_0
    cdef public bint _wnied_ramflag
    cdef public double[:,:] _wnied_array
    cdef public bint _wnied_diskflag_reading
    cdef public bint _wnied_diskflag_writing
    cdef public double[:] _wnied_ncarray
    cdef public bint _wnied_outputflag
    cdef double *_wnied_outputpointer
    cdef public double[:] schmpot
    cdef public int _schmpot_ndim
    cdef public int _schmpot_length
    cdef public int _schmpot_length_0
    cdef public bint _schmpot_ramflag
    cdef public double[:,:] _schmpot_array
    cdef public bint _schmpot_diskflag_reading
    cdef public bint _schmpot_diskflag_writing
    cdef public double[:] _schmpot_ncarray
    cdef public bint _schmpot_outputflag
    cdef double *_schmpot_outputpointer
    cdef public double[:] schm
    cdef public int _schm_ndim
    cdef public int _schm_length
    cdef public int _schm_length_0
    cdef public bint _schm_ramflag
    cdef public double[:,:] _schm_array
    cdef public bint _schm_diskflag_reading
    cdef public bint _schm_diskflag_writing
    cdef public double[:] _schm_ncarray
    cdef public bint _schm_outputflag
    cdef double *_schm_outputpointer
    cdef public double[:] wada
    cdef public int _wada_ndim
    cdef public int _wada_length
    cdef public int _wada_length_0
    cdef public bint _wada_ramflag
    cdef public double[:,:] _wada_array
    cdef public bint _wada_diskflag_reading
    cdef public bint _wada_diskflag_writing
    cdef public double[:] _wada_ncarray
    cdef public bint _wada_outputflag
    cdef double *_wada_outputpointer
    cdef public double[:] qdb
    cdef public int _qdb_ndim
    cdef public int _qdb_length
    cdef public int _qdb_length_0
    cdef public bint _qdb_ramflag
    cdef public double[:,:] _qdb_array
    cdef public bint _qdb_diskflag_reading
    cdef public bint _qdb_diskflag_writing
    cdef public double[:] _qdb_ncarray
    cdef public bint _qdb_outputflag
    cdef double *_qdb_outputpointer
    cdef public double[:] qib1
    cdef public int _qib1_ndim
    cdef public int _qib1_length
    cdef public int _qib1_length_0
    cdef public bint _qib1_ramflag
    cdef public double[:,:] _qib1_array
    cdef public bint _qib1_diskflag_reading
    cdef public bint _qib1_diskflag_writing
    cdef public double[:] _qib1_ncarray
    cdef public bint _qib1_outputflag
    cdef double *_qib1_outputpointer
    cdef public double[:] qib2
    cdef public int _qib2_ndim
    cdef public int _qib2_length
    cdef public int _qib2_length_0
    cdef public bint _qib2_ramflag
    cdef public double[:,:] _qib2_array
    cdef public bint _qib2_diskflag_reading
    cdef public bint _qib2_diskflag_writing
    cdef public double[:] _qib2_ncarray
    cdef public bint _qib2_outputflag
    cdef double *_qib2_outputpointer
    cdef public double[:] qbb
    cdef public int _qbb_ndim
    cdef public int _qbb_length
    cdef public int _qbb_length_0
    cdef public bint _qbb_ramflag
    cdef public double[:,:] _qbb_array
    cdef public bint _qbb_diskflag_reading
    cdef public bint _qbb_diskflag_writing
    cdef public double[:] _qbb_ncarray
    cdef public bint _qbb_outputflag
    cdef double *_qbb_outputpointer
    cdef public double[:] qkap
    cdef public int _qkap_ndim
    cdef public int _qkap_length
    cdef public int _qkap_length_0
    cdef public bint _qkap_ramflag
    cdef public double[:,:] _qkap_array
    cdef public bint _qkap_diskflag_reading
    cdef public bint _qkap_diskflag_writing
    cdef public double[:] _qkap_ncarray
    cdef public bint _qkap_outputflag
    cdef double *_qkap_outputpointer
    cdef public double qdgz
    cdef public int _qdgz_ndim
    cdef public int _qdgz_length
    cdef public bint _qdgz_ramflag
    cdef public double[:] _qdgz_array
    cdef public bint _qdgz_diskflag_reading
    cdef public bint _qdgz_diskflag_writing
    cdef public double[:] _qdgz_ncarray
    cdef public bint _qdgz_outputflag
    cdef double *_qdgz_outputpointer
    cdef public double qah
    cdef public int _qah_ndim
    cdef public int _qah_length
    cdef public bint _qah_ramflag
    cdef public double[:] _qah_array
    cdef public bint _qah_diskflag_reading
    cdef public bint _qah_diskflag_writing
    cdef public double[:] _qah_ncarray
    cdef public bint _qah_outputflag
    cdef double *_qah_outputpointer
    cdef public double qa
    cdef public int _qa_ndim
    cdef public int _qa_length
    cdef public bint _qa_ramflag
    cdef public double[:] _qa_array
    cdef public bint _qa_diskflag_reading
    cdef public bint _qa_diskflag_writing
    cdef public double[:] _qa_ncarray
    cdef public bint _qa_outputflag
    cdef double *_qa_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._qz_diskflag_reading:
            self.qz = self._qz_ncarray[0]
        elif self._qz_ramflag:
            self.qz = self._qz_array[idx]
        if self._qzh_diskflag_reading:
            self.qzh = self._qzh_ncarray[0]
        elif self._qzh_ramflag:
            self.qzh = self._qzh_array[idx]
        if self._nkor_diskflag_reading:
            k = 0
            for jdx0 in range(self._nkor_length_0):
                self.nkor[jdx0] = self._nkor_ncarray[k]
                k += 1
        elif self._nkor_ramflag:
            for jdx0 in range(self._nkor_length_0):
                self.nkor[jdx0] = self._nkor_array[idx, jdx0]
        if self._tkor_diskflag_reading:
            k = 0
            for jdx0 in range(self._tkor_length_0):
                self.tkor[jdx0] = self._tkor_ncarray[k]
                k += 1
        elif self._tkor_ramflag:
            for jdx0 in range(self._tkor_length_0):
                self.tkor[jdx0] = self._tkor_array[idx, jdx0]
        if self._nbes_diskflag_reading:
            k = 0
            for jdx0 in range(self._nbes_length_0):
                self.nbes[jdx0] = self._nbes_ncarray[k]
                k += 1
        elif self._nbes_ramflag:
            for jdx0 in range(self._nbes_length_0):
                self.nbes[jdx0] = self._nbes_array[idx, jdx0]
        if self._sbes_diskflag_reading:
            k = 0
            for jdx0 in range(self._sbes_length_0):
                self.sbes[jdx0] = self._sbes_ncarray[k]
                k += 1
        elif self._sbes_ramflag:
            for jdx0 in range(self._sbes_length_0):
                self.sbes[jdx0] = self._sbes_array[idx, jdx0]
        if self._et0_diskflag_reading:
            k = 0
            for jdx0 in range(self._et0_length_0):
                self.et0[jdx0] = self._et0_ncarray[k]
                k += 1
        elif self._et0_ramflag:
            for jdx0 in range(self._et0_length_0):
                self.et0[jdx0] = self._et0_array[idx, jdx0]
        if self._evpo_diskflag_reading:
            k = 0
            for jdx0 in range(self._evpo_length_0):
                self.evpo[jdx0] = self._evpo_ncarray[k]
                k += 1
        elif self._evpo_ramflag:
            for jdx0 in range(self._evpo_length_0):
                self.evpo[jdx0] = self._evpo_array[idx, jdx0]
        if self._evi_diskflag_reading:
            k = 0
            for jdx0 in range(self._evi_length_0):
                self.evi[jdx0] = self._evi_ncarray[k]
                k += 1
        elif self._evi_ramflag:
            for jdx0 in range(self._evi_length_0):
                self.evi[jdx0] = self._evi_array[idx, jdx0]
        if self._evb_diskflag_reading:
            k = 0
            for jdx0 in range(self._evb_length_0):
                self.evb[jdx0] = self._evb_ncarray[k]
                k += 1
        elif self._evb_ramflag:
            for jdx0 in range(self._evb_length_0):
                self.evb[jdx0] = self._evb_array[idx, jdx0]
        if self._wgtf_diskflag_reading:
            k = 0
            for jdx0 in range(self._wgtf_length_0):
                self.wgtf[jdx0] = self._wgtf_ncarray[k]
                k += 1
        elif self._wgtf_ramflag:
            for jdx0 in range(self._wgtf_length_0):
                self.wgtf[jdx0] = self._wgtf_array[idx, jdx0]
        if self._wnied_diskflag_reading:
            k = 0
            for jdx0 in range(self._wnied_length_0):
                self.wnied[jdx0] = self._wnied_ncarray[k]
                k += 1
        elif self._wnied_ramflag:
            for jdx0 in range(self._wnied_length_0):
                self.wnied[jdx0] = self._wnied_array[idx, jdx0]
        if self._schmpot_diskflag_reading:
            k = 0
            for jdx0 in range(self._schmpot_length_0):
                self.schmpot[jdx0] = self._schmpot_ncarray[k]
                k += 1
        elif self._schmpot_ramflag:
            for jdx0 in range(self._schmpot_length_0):
                self.schmpot[jdx0] = self._schmpot_array[idx, jdx0]
        if self._schm_diskflag_reading:
            k = 0
            for jdx0 in range(self._schm_length_0):
                self.schm[jdx0] = self._schm_ncarray[k]
                k += 1
        elif self._schm_ramflag:
            for jdx0 in range(self._schm_length_0):
                self.schm[jdx0] = self._schm_array[idx, jdx0]
        if self._wada_diskflag_reading:
            k = 0
            for jdx0 in range(self._wada_length_0):
                self.wada[jdx0] = self._wada_ncarray[k]
                k += 1
        elif self._wada_ramflag:
            for jdx0 in range(self._wada_length_0):
                self.wada[jdx0] = self._wada_array[idx, jdx0]
        if self._qdb_diskflag_reading:
            k = 0
            for jdx0 in range(self._qdb_length_0):
                self.qdb[jdx0] = self._qdb_ncarray[k]
                k += 1
        elif self._qdb_ramflag:
            for jdx0 in range(self._qdb_length_0):
                self.qdb[jdx0] = self._qdb_array[idx, jdx0]
        if self._qib1_diskflag_reading:
            k = 0
            for jdx0 in range(self._qib1_length_0):
                self.qib1[jdx0] = self._qib1_ncarray[k]
                k += 1
        elif self._qib1_ramflag:
            for jdx0 in range(self._qib1_length_0):
                self.qib1[jdx0] = self._qib1_array[idx, jdx0]
        if self._qib2_diskflag_reading:
            k = 0
            for jdx0 in range(self._qib2_length_0):
                self.qib2[jdx0] = self._qib2_ncarray[k]
                k += 1
        elif self._qib2_ramflag:
            for jdx0 in range(self._qib2_length_0):
                self.qib2[jdx0] = self._qib2_array[idx, jdx0]
        if self._qbb_diskflag_reading:
            k = 0
            for jdx0 in range(self._qbb_length_0):
                self.qbb[jdx0] = self._qbb_ncarray[k]
                k += 1
        elif self._qbb_ramflag:
            for jdx0 in range(self._qbb_length_0):
                self.qbb[jdx0] = self._qbb_array[idx, jdx0]
        if self._qkap_diskflag_reading:
            k = 0
            for jdx0 in range(self._qkap_length_0):
                self.qkap[jdx0] = self._qkap_ncarray[k]
                k += 1
        elif self._qkap_ramflag:
            for jdx0 in range(self._qkap_length_0):
                self.qkap[jdx0] = self._qkap_array[idx, jdx0]
        if self._qdgz_diskflag_reading:
            self.qdgz = self._qdgz_ncarray[0]
        elif self._qdgz_ramflag:
            self.qdgz = self._qdgz_array[idx]
        if self._qah_diskflag_reading:
            self.qah = self._qah_ncarray[0]
        elif self._qah_ramflag:
            self.qah = self._qah_array[idx]
        if self._qa_diskflag_reading:
            self.qa = self._qa_ncarray[0]
        elif self._qa_ramflag:
            self.qa = self._qa_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._qz_diskflag_writing:
            self._qz_ncarray[0] = self.qz
        if self._qz_ramflag:
            self._qz_array[idx] = self.qz
        if self._qzh_diskflag_writing:
            self._qzh_ncarray[0] = self.qzh
        if self._qzh_ramflag:
            self._qzh_array[idx] = self.qzh
        if self._nkor_diskflag_writing:
            k = 0
            for jdx0 in range(self._nkor_length_0):
                self._nkor_ncarray[k] = self.nkor[jdx0]
                k += 1
        if self._nkor_ramflag:
            for jdx0 in range(self._nkor_length_0):
                self._nkor_array[idx, jdx0] = self.nkor[jdx0]
        if self._tkor_diskflag_writing:
            k = 0
            for jdx0 in range(self._tkor_length_0):
                self._tkor_ncarray[k] = self.tkor[jdx0]
                k += 1
        if self._tkor_ramflag:
            for jdx0 in range(self._tkor_length_0):
                self._tkor_array[idx, jdx0] = self.tkor[jdx0]
        if self._nbes_diskflag_writing:
            k = 0
            for jdx0 in range(self._nbes_length_0):
                self._nbes_ncarray[k] = self.nbes[jdx0]
                k += 1
        if self._nbes_ramflag:
            for jdx0 in range(self._nbes_length_0):
                self._nbes_array[idx, jdx0] = self.nbes[jdx0]
        if self._sbes_diskflag_writing:
            k = 0
            for jdx0 in range(self._sbes_length_0):
                self._sbes_ncarray[k] = self.sbes[jdx0]
                k += 1
        if self._sbes_ramflag:
            for jdx0 in range(self._sbes_length_0):
                self._sbes_array[idx, jdx0] = self.sbes[jdx0]
        if self._et0_diskflag_writing:
            k = 0
            for jdx0 in range(self._et0_length_0):
                self._et0_ncarray[k] = self.et0[jdx0]
                k += 1
        if self._et0_ramflag:
            for jdx0 in range(self._et0_length_0):
                self._et0_array[idx, jdx0] = self.et0[jdx0]
        if self._evpo_diskflag_writing:
            k = 0
            for jdx0 in range(self._evpo_length_0):
                self._evpo_ncarray[k] = self.evpo[jdx0]
                k += 1
        if self._evpo_ramflag:
            for jdx0 in range(self._evpo_length_0):
                self._evpo_array[idx, jdx0] = self.evpo[jdx0]
        if self._evi_diskflag_writing:
            k = 0
            for jdx0 in range(self._evi_length_0):
                self._evi_ncarray[k] = self.evi[jdx0]
                k += 1
        if self._evi_ramflag:
            for jdx0 in range(self._evi_length_0):
                self._evi_array[idx, jdx0] = self.evi[jdx0]
        if self._evb_diskflag_writing:
            k = 0
            for jdx0 in range(self._evb_length_0):
                self._evb_ncarray[k] = self.evb[jdx0]
                k += 1
        if self._evb_ramflag:
            for jdx0 in range(self._evb_length_0):
                self._evb_array[idx, jdx0] = self.evb[jdx0]
        if self._wgtf_diskflag_writing:
            k = 0
            for jdx0 in range(self._wgtf_length_0):
                self._wgtf_ncarray[k] = self.wgtf[jdx0]
                k += 1
        if self._wgtf_ramflag:
            for jdx0 in range(self._wgtf_length_0):
                self._wgtf_array[idx, jdx0] = self.wgtf[jdx0]
        if self._wnied_diskflag_writing:
            k = 0
            for jdx0 in range(self._wnied_length_0):
                self._wnied_ncarray[k] = self.wnied[jdx0]
                k += 1
        if self._wnied_ramflag:
            for jdx0 in range(self._wnied_length_0):
                self._wnied_array[idx, jdx0] = self.wnied[jdx0]
        if self._schmpot_diskflag_writing:
            k = 0
            for jdx0 in range(self._schmpot_length_0):
                self._schmpot_ncarray[k] = self.schmpot[jdx0]
                k += 1
        if self._schmpot_ramflag:
            for jdx0 in range(self._schmpot_length_0):
                self._schmpot_array[idx, jdx0] = self.schmpot[jdx0]
        if self._schm_diskflag_writing:
            k = 0
            for jdx0 in range(self._schm_length_0):
                self._schm_ncarray[k] = self.schm[jdx0]
                k += 1
        if self._schm_ramflag:
            for jdx0 in range(self._schm_length_0):
                self._schm_array[idx, jdx0] = self.schm[jdx0]
        if self._wada_diskflag_writing:
            k = 0
            for jdx0 in range(self._wada_length_0):
                self._wada_ncarray[k] = self.wada[jdx0]
                k += 1
        if self._wada_ramflag:
            for jdx0 in range(self._wada_length_0):
                self._wada_array[idx, jdx0] = self.wada[jdx0]
        if self._qdb_diskflag_writing:
            k = 0
            for jdx0 in range(self._qdb_length_0):
                self._qdb_ncarray[k] = self.qdb[jdx0]
                k += 1
        if self._qdb_ramflag:
            for jdx0 in range(self._qdb_length_0):
                self._qdb_array[idx, jdx0] = self.qdb[jdx0]
        if self._qib1_diskflag_writing:
            k = 0
            for jdx0 in range(self._qib1_length_0):
                self._qib1_ncarray[k] = self.qib1[jdx0]
                k += 1
        if self._qib1_ramflag:
            for jdx0 in range(self._qib1_length_0):
                self._qib1_array[idx, jdx0] = self.qib1[jdx0]
        if self._qib2_diskflag_writing:
            k = 0
            for jdx0 in range(self._qib2_length_0):
                self._qib2_ncarray[k] = self.qib2[jdx0]
                k += 1
        if self._qib2_ramflag:
            for jdx0 in range(self._qib2_length_0):
                self._qib2_array[idx, jdx0] = self.qib2[jdx0]
        if self._qbb_diskflag_writing:
            k = 0
            for jdx0 in range(self._qbb_length_0):
                self._qbb_ncarray[k] = self.qbb[jdx0]
                k += 1
        if self._qbb_ramflag:
            for jdx0 in range(self._qbb_length_0):
                self._qbb_array[idx, jdx0] = self.qbb[jdx0]
        if self._qkap_diskflag_writing:
            k = 0
            for jdx0 in range(self._qkap_length_0):
                self._qkap_ncarray[k] = self.qkap[jdx0]
                k += 1
        if self._qkap_ramflag:
            for jdx0 in range(self._qkap_length_0):
                self._qkap_array[idx, jdx0] = self.qkap[jdx0]
        if self._qdgz_diskflag_writing:
            self._qdgz_ncarray[0] = self.qdgz
        if self._qdgz_ramflag:
            self._qdgz_array[idx] = self.qdgz
        if self._qah_diskflag_writing:
            self._qah_ncarray[0] = self.qah
        if self._qah_ramflag:
            self._qah_array[idx] = self.qah
        if self._qa_diskflag_writing:
            self._qa_ncarray[0] = self.qa
        if self._qa_ramflag:
            self._qa_array[idx] = self.qa
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "qz":
            self._qz_outputpointer = value.p_value
        if name == "qzh":
            self._qzh_outputpointer = value.p_value
        if name == "qdgz":
            self._qdgz_outputpointer = value.p_value
        if name == "qah":
            self._qah_outputpointer = value.p_value
        if name == "qa":
            self._qa_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._qz_outputflag:
            self._qz_outputpointer[0] = self.qz
        if self._qzh_outputflag:
            self._qzh_outputpointer[0] = self.qzh
        if self._qdgz_outputflag:
            self._qdgz_outputpointer[0] = self.qdgz
        if self._qah_outputflag:
            self._qah_outputpointer[0] = self.qah
        if self._qa_outputflag:
            self._qa_outputpointer[0] = self.qa
@cython.final
cdef class StateSequences:
    cdef public double[:] inzp
    cdef public int _inzp_ndim
    cdef public int _inzp_length
    cdef public int _inzp_length_0
    cdef public bint _inzp_ramflag
    cdef public double[:,:] _inzp_array
    cdef public bint _inzp_diskflag_reading
    cdef public bint _inzp_diskflag_writing
    cdef public double[:] _inzp_ncarray
    cdef public bint _inzp_outputflag
    cdef double *_inzp_outputpointer
    cdef public double[:] wats
    cdef public int _wats_ndim
    cdef public int _wats_length
    cdef public int _wats_length_0
    cdef public bint _wats_ramflag
    cdef public double[:,:] _wats_array
    cdef public bint _wats_diskflag_reading
    cdef public bint _wats_diskflag_writing
    cdef public double[:] _wats_ncarray
    cdef public bint _wats_outputflag
    cdef double *_wats_outputpointer
    cdef public double[:] waes
    cdef public int _waes_ndim
    cdef public int _waes_length
    cdef public int _waes_length_0
    cdef public bint _waes_ramflag
    cdef public double[:,:] _waes_array
    cdef public bint _waes_diskflag_reading
    cdef public bint _waes_diskflag_writing
    cdef public double[:] _waes_ncarray
    cdef public bint _waes_outputflag
    cdef double *_waes_outputpointer
    cdef public double[:] bowa
    cdef public int _bowa_ndim
    cdef public int _bowa_length
    cdef public int _bowa_length_0
    cdef public bint _bowa_ramflag
    cdef public double[:,:] _bowa_array
    cdef public bint _bowa_diskflag_reading
    cdef public bint _bowa_diskflag_writing
    cdef public double[:] _bowa_ncarray
    cdef public bint _bowa_outputflag
    cdef double *_bowa_outputpointer
    cdef public double qdgz1
    cdef public int _qdgz1_ndim
    cdef public int _qdgz1_length
    cdef public bint _qdgz1_ramflag
    cdef public double[:] _qdgz1_array
    cdef public bint _qdgz1_diskflag_reading
    cdef public bint _qdgz1_diskflag_writing
    cdef public double[:] _qdgz1_ncarray
    cdef public bint _qdgz1_outputflag
    cdef double *_qdgz1_outputpointer
    cdef public double qdgz2
    cdef public int _qdgz2_ndim
    cdef public int _qdgz2_length
    cdef public bint _qdgz2_ramflag
    cdef public double[:] _qdgz2_array
    cdef public bint _qdgz2_diskflag_reading
    cdef public bint _qdgz2_diskflag_writing
    cdef public double[:] _qdgz2_ncarray
    cdef public bint _qdgz2_outputflag
    cdef double *_qdgz2_outputpointer
    cdef public double qigz1
    cdef public int _qigz1_ndim
    cdef public int _qigz1_length
    cdef public bint _qigz1_ramflag
    cdef public double[:] _qigz1_array
    cdef public bint _qigz1_diskflag_reading
    cdef public bint _qigz1_diskflag_writing
    cdef public double[:] _qigz1_ncarray
    cdef public bint _qigz1_outputflag
    cdef double *_qigz1_outputpointer
    cdef public double qigz2
    cdef public int _qigz2_ndim
    cdef public int _qigz2_length
    cdef public bint _qigz2_ramflag
    cdef public double[:] _qigz2_array
    cdef public bint _qigz2_diskflag_reading
    cdef public bint _qigz2_diskflag_writing
    cdef public double[:] _qigz2_ncarray
    cdef public bint _qigz2_outputflag
    cdef double *_qigz2_outputpointer
    cdef public double qbgz
    cdef public int _qbgz_ndim
    cdef public int _qbgz_length
    cdef public bint _qbgz_ramflag
    cdef public double[:] _qbgz_array
    cdef public bint _qbgz_diskflag_reading
    cdef public bint _qbgz_diskflag_writing
    cdef public double[:] _qbgz_ncarray
    cdef public bint _qbgz_outputflag
    cdef double *_qbgz_outputpointer
    cdef public double qdga1
    cdef public int _qdga1_ndim
    cdef public int _qdga1_length
    cdef public bint _qdga1_ramflag
    cdef public double[:] _qdga1_array
    cdef public bint _qdga1_diskflag_reading
    cdef public bint _qdga1_diskflag_writing
    cdef public double[:] _qdga1_ncarray
    cdef public bint _qdga1_outputflag
    cdef double *_qdga1_outputpointer
    cdef public double qdga2
    cdef public int _qdga2_ndim
    cdef public int _qdga2_length
    cdef public bint _qdga2_ramflag
    cdef public double[:] _qdga2_array
    cdef public bint _qdga2_diskflag_reading
    cdef public bint _qdga2_diskflag_writing
    cdef public double[:] _qdga2_ncarray
    cdef public bint _qdga2_outputflag
    cdef double *_qdga2_outputpointer
    cdef public double qiga1
    cdef public int _qiga1_ndim
    cdef public int _qiga1_length
    cdef public bint _qiga1_ramflag
    cdef public double[:] _qiga1_array
    cdef public bint _qiga1_diskflag_reading
    cdef public bint _qiga1_diskflag_writing
    cdef public double[:] _qiga1_ncarray
    cdef public bint _qiga1_outputflag
    cdef double *_qiga1_outputpointer
    cdef public double qiga2
    cdef public int _qiga2_ndim
    cdef public int _qiga2_length
    cdef public bint _qiga2_ramflag
    cdef public double[:] _qiga2_array
    cdef public bint _qiga2_diskflag_reading
    cdef public bint _qiga2_diskflag_writing
    cdef public double[:] _qiga2_ncarray
    cdef public bint _qiga2_outputflag
    cdef double *_qiga2_outputpointer
    cdef public double qbga
    cdef public int _qbga_ndim
    cdef public int _qbga_length
    cdef public bint _qbga_ramflag
    cdef public double[:] _qbga_array
    cdef public bint _qbga_diskflag_reading
    cdef public bint _qbga_diskflag_writing
    cdef public double[:] _qbga_ncarray
    cdef public bint _qbga_outputflag
    cdef double *_qbga_outputpointer
    cpdef inline void load_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._inzp_diskflag_reading:
            k = 0
            for jdx0 in range(self._inzp_length_0):
                self.inzp[jdx0] = self._inzp_ncarray[k]
                k += 1
        elif self._inzp_ramflag:
            for jdx0 in range(self._inzp_length_0):
                self.inzp[jdx0] = self._inzp_array[idx, jdx0]
        if self._wats_diskflag_reading:
            k = 0
            for jdx0 in range(self._wats_length_0):
                self.wats[jdx0] = self._wats_ncarray[k]
                k += 1
        elif self._wats_ramflag:
            for jdx0 in range(self._wats_length_0):
                self.wats[jdx0] = self._wats_array[idx, jdx0]
        if self._waes_diskflag_reading:
            k = 0
            for jdx0 in range(self._waes_length_0):
                self.waes[jdx0] = self._waes_ncarray[k]
                k += 1
        elif self._waes_ramflag:
            for jdx0 in range(self._waes_length_0):
                self.waes[jdx0] = self._waes_array[idx, jdx0]
        if self._bowa_diskflag_reading:
            k = 0
            for jdx0 in range(self._bowa_length_0):
                self.bowa[jdx0] = self._bowa_ncarray[k]
                k += 1
        elif self._bowa_ramflag:
            for jdx0 in range(self._bowa_length_0):
                self.bowa[jdx0] = self._bowa_array[idx, jdx0]
        if self._qdgz1_diskflag_reading:
            self.qdgz1 = self._qdgz1_ncarray[0]
        elif self._qdgz1_ramflag:
            self.qdgz1 = self._qdgz1_array[idx]
        if self._qdgz2_diskflag_reading:
            self.qdgz2 = self._qdgz2_ncarray[0]
        elif self._qdgz2_ramflag:
            self.qdgz2 = self._qdgz2_array[idx]
        if self._qigz1_diskflag_reading:
            self.qigz1 = self._qigz1_ncarray[0]
        elif self._qigz1_ramflag:
            self.qigz1 = self._qigz1_array[idx]
        if self._qigz2_diskflag_reading:
            self.qigz2 = self._qigz2_ncarray[0]
        elif self._qigz2_ramflag:
            self.qigz2 = self._qigz2_array[idx]
        if self._qbgz_diskflag_reading:
            self.qbgz = self._qbgz_ncarray[0]
        elif self._qbgz_ramflag:
            self.qbgz = self._qbgz_array[idx]
        if self._qdga1_diskflag_reading:
            self.qdga1 = self._qdga1_ncarray[0]
        elif self._qdga1_ramflag:
            self.qdga1 = self._qdga1_array[idx]
        if self._qdga2_diskflag_reading:
            self.qdga2 = self._qdga2_ncarray[0]
        elif self._qdga2_ramflag:
            self.qdga2 = self._qdga2_array[idx]
        if self._qiga1_diskflag_reading:
            self.qiga1 = self._qiga1_ncarray[0]
        elif self._qiga1_ramflag:
            self.qiga1 = self._qiga1_array[idx]
        if self._qiga2_diskflag_reading:
            self.qiga2 = self._qiga2_ncarray[0]
        elif self._qiga2_ramflag:
            self.qiga2 = self._qiga2_array[idx]
        if self._qbga_diskflag_reading:
            self.qbga = self._qbga_ncarray[0]
        elif self._qbga_ramflag:
            self.qbga = self._qbga_array[idx]
    cpdef inline void save_data(self, int idx)  nogil:
        cdef int jdx0
        cdef int k
        if self._inzp_diskflag_writing:
            k = 0
            for jdx0 in range(self._inzp_length_0):
                self._inzp_ncarray[k] = self.inzp[jdx0]
                k += 1
        if self._inzp_ramflag:
            for jdx0 in range(self._inzp_length_0):
                self._inzp_array[idx, jdx0] = self.inzp[jdx0]
        if self._wats_diskflag_writing:
            k = 0
            for jdx0 in range(self._wats_length_0):
                self._wats_ncarray[k] = self.wats[jdx0]
                k += 1
        if self._wats_ramflag:
            for jdx0 in range(self._wats_length_0):
                self._wats_array[idx, jdx0] = self.wats[jdx0]
        if self._waes_diskflag_writing:
            k = 0
            for jdx0 in range(self._waes_length_0):
                self._waes_ncarray[k] = self.waes[jdx0]
                k += 1
        if self._waes_ramflag:
            for jdx0 in range(self._waes_length_0):
                self._waes_array[idx, jdx0] = self.waes[jdx0]
        if self._bowa_diskflag_writing:
            k = 0
            for jdx0 in range(self._bowa_length_0):
                self._bowa_ncarray[k] = self.bowa[jdx0]
                k += 1
        if self._bowa_ramflag:
            for jdx0 in range(self._bowa_length_0):
                self._bowa_array[idx, jdx0] = self.bowa[jdx0]
        if self._qdgz1_diskflag_writing:
            self._qdgz1_ncarray[0] = self.qdgz1
        if self._qdgz1_ramflag:
            self._qdgz1_array[idx] = self.qdgz1
        if self._qdgz2_diskflag_writing:
            self._qdgz2_ncarray[0] = self.qdgz2
        if self._qdgz2_ramflag:
            self._qdgz2_array[idx] = self.qdgz2
        if self._qigz1_diskflag_writing:
            self._qigz1_ncarray[0] = self.qigz1
        if self._qigz1_ramflag:
            self._qigz1_array[idx] = self.qigz1
        if self._qigz2_diskflag_writing:
            self._qigz2_ncarray[0] = self.qigz2
        if self._qigz2_ramflag:
            self._qigz2_array[idx] = self.qigz2
        if self._qbgz_diskflag_writing:
            self._qbgz_ncarray[0] = self.qbgz
        if self._qbgz_ramflag:
            self._qbgz_array[idx] = self.qbgz
        if self._qdga1_diskflag_writing:
            self._qdga1_ncarray[0] = self.qdga1
        if self._qdga1_ramflag:
            self._qdga1_array[idx] = self.qdga1
        if self._qdga2_diskflag_writing:
            self._qdga2_ncarray[0] = self.qdga2
        if self._qdga2_ramflag:
            self._qdga2_array[idx] = self.qdga2
        if self._qiga1_diskflag_writing:
            self._qiga1_ncarray[0] = self.qiga1
        if self._qiga1_ramflag:
            self._qiga1_array[idx] = self.qiga1
        if self._qiga2_diskflag_writing:
            self._qiga2_ncarray[0] = self.qiga2
        if self._qiga2_ramflag:
            self._qiga2_array[idx] = self.qiga2
        if self._qbga_diskflag_writing:
            self._qbga_ncarray[0] = self.qbga
        if self._qbga_ramflag:
            self._qbga_array[idx] = self.qbga
    cpdef inline set_pointeroutput(self, str name, pointerutils.PDouble value):
        if name == "qdgz1":
            self._qdgz1_outputpointer = value.p_value
        if name == "qdgz2":
            self._qdgz2_outputpointer = value.p_value
        if name == "qigz1":
            self._qigz1_outputpointer = value.p_value
        if name == "qigz2":
            self._qigz2_outputpointer = value.p_value
        if name == "qbgz":
            self._qbgz_outputpointer = value.p_value
        if name == "qdga1":
            self._qdga1_outputpointer = value.p_value
        if name == "qdga2":
            self._qdga2_outputpointer = value.p_value
        if name == "qiga1":
            self._qiga1_outputpointer = value.p_value
        if name == "qiga2":
            self._qiga2_outputpointer = value.p_value
        if name == "qbga":
            self._qbga_outputpointer = value.p_value
    cpdef inline void update_outputs(self) nogil:
        if self._qdgz1_outputflag:
            self._qdgz1_outputpointer[0] = self.qdgz1
        if self._qdgz2_outputflag:
            self._qdgz2_outputpointer[0] = self.qdgz2
        if self._qigz1_outputflag:
            self._qigz1_outputpointer[0] = self.qigz1
        if self._qigz2_outputflag:
            self._qigz2_outputpointer[0] = self.qigz2
        if self._qbgz_outputflag:
            self._qbgz_outputpointer[0] = self.qbgz
        if self._qdga1_outputflag:
            self._qdga1_outputpointer[0] = self.qdga1
        if self._qdga2_outputflag:
            self._qdga2_outputpointer[0] = self.qdga2
        if self._qiga1_outputflag:
            self._qiga1_outputpointer[0] = self.qiga1
        if self._qiga2_outputflag:
            self._qiga2_outputpointer[0] = self.qiga2
        if self._qbga_outputflag:
            self._qbga_outputpointer[0] = self.qbga
@cython.final
cdef class LogSequences:
    cdef public double[:,:] wet0
    cdef public int _wet0_ndim
    cdef public int _wet0_length
    cdef public int _wet0_length_0
    cdef public int _wet0_length_1
@cython.final
cdef class AideSequences:
    cdef public double[:] snratio
    cdef public int _snratio_ndim
    cdef public int _snratio_length
    cdef public int _snratio_length_0
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
    cdef public int idx_sim
    cdef public Parameters parameters
    cdef public Sequences sequences
    cpdef inline void simulate(self, int idx)  nogil:
        self.idx_sim = idx
        self.load_data()
        self.update_inlets()
        self.run()
        self.new2old()
        self.update_outlets()
        self.update_outputs()
    cpdef inline void load_data(self) nogil:
        self.sequences.inputs.load_data(self.idx_sim)
    cpdef inline void save_data(self, int idx) nogil:
        self.sequences.inputs.save_data(self.idx_sim)
        self.sequences.fluxes.save_data(self.idx_sim)
        self.sequences.states.save_data(self.idx_sim)
    cpdef inline void new2old(self) nogil:
        cdef int jdx0
        for jdx0 in range(self.sequences.states._inzp_length_0):
            self.sequences.old_states.inzp[jdx0] = self.sequences.new_states.inzp[jdx0]
        for jdx0 in range(self.sequences.states._wats_length_0):
            self.sequences.old_states.wats[jdx0] = self.sequences.new_states.wats[jdx0]
        for jdx0 in range(self.sequences.states._waes_length_0):
            self.sequences.old_states.waes[jdx0] = self.sequences.new_states.waes[jdx0]
        for jdx0 in range(self.sequences.states._bowa_length_0):
            self.sequences.old_states.bowa[jdx0] = self.sequences.new_states.bowa[jdx0]
        self.sequences.old_states.qdgz1 = self.sequences.new_states.qdgz1
        self.sequences.old_states.qdgz2 = self.sequences.new_states.qdgz2
        self.sequences.old_states.qigz1 = self.sequences.new_states.qigz1
        self.sequences.old_states.qigz2 = self.sequences.new_states.qigz2
        self.sequences.old_states.qbgz = self.sequences.new_states.qbgz
        self.sequences.old_states.qdga1 = self.sequences.new_states.qdga1
        self.sequences.old_states.qdga2 = self.sequences.new_states.qdga2
        self.sequences.old_states.qiga1 = self.sequences.new_states.qiga1
        self.sequences.old_states.qiga2 = self.sequences.new_states.qiga2
        self.sequences.old_states.qbga = self.sequences.new_states.qbga
    cpdef inline void run(self) nogil:
        self.calc_qzh_v1()
        self.calc_nkor_v1()
        self.calc_tkor_v1()
        self.calc_et0_wet0_v1()
        self.calc_evpo_v1()
        self.calc_nbes_inzp_v1()
        self.calc_evi_inzp_v1()
        self.calc_snratio_v1()
        self.calc_sbes_v1()
        self.calc_wats_v1()
        self.calc_wgtf_v1()
        self.calc_wnied_v1()
        self.calc_schmpot_v1()
        self.calc_schm_wats_v1()
        self.calc_wada_waes_v1()
        self.calc_evb_v1()
        self.calc_qkap_v1()
        self.calc_qbb_v1()
        self.calc_qib1_v1()
        self.calc_qib2_v1()
        self.calc_qdb_v1()
        self.calc_bowa_v1()
        self.calc_qbgz_v1()
        self.calc_qigz1_v1()
        self.calc_qigz2_v1()
        self.calc_qdgz_v1()
        self.calc_qbga_v1()
        self.update_qdgz_qbgz_qbga_v1()
        self.update_qdgz_qbgz_qbga_v2()
        self.calc_qiga1_v1()
        self.calc_qiga2_v1()
        self.calc_qdgz1_qdgz2_v1()
        self.calc_qdga1_v1()
        self.calc_qdga2_v1()
        self.calc_qah_v1()
        self.calc_qa_v1()
    cpdef inline void update_inlets(self) nogil:
        self.pick_qz_v1()
    cpdef inline void update_outlets(self) nogil:
        self.pass_qa_v1()
    cpdef inline void update_receivers(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_senders(self, int idx) nogil:
        self.idx_sim = idx
        pass
    cpdef inline void update_outputs(self) nogil:
        self.sequences.fluxes.update_outputs()
        self.sequences.states.update_outputs()

    cpdef inline void pick_qz_v1(self)  nogil:
        cdef int idx
        self.sequences.fluxes.qz = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.qz = self.sequences.fluxes.qz + (self.sequences.inlets.q[idx][0])
    cpdef inline void pick_qz(self)  nogil:
        cdef int idx
        self.sequences.fluxes.qz = 0.0
        for idx in range(self.sequences.inlets.len_q):
            self.sequences.fluxes.qz = self.sequences.fluxes.qz + (self.sequences.inlets.q[idx][0])
    cpdef inline void calc_qzh_v1(self)  nogil:
        self.sequences.fluxes.qzh = self.sequences.fluxes.qz / self.parameters.derived.qfactor
    cpdef inline void calc_nkor_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.nkor[k] = self.parameters.control.kg[k] * self.sequences.inputs.nied
    cpdef inline void calc_tkor_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.tkor[k] = self.parameters.control.kt[k] + self.sequences.inputs.teml
    cpdef inline void calc_et0_wet0_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.et0[k] = (                self.parameters.control.wfet0[k] * self.parameters.control.ke[k] * self.sequences.inputs.pet                + (1.0 - self.parameters.control.wfet0[k]) * self.sequences.logs.wet0[0, k]            )
            self.sequences.logs.wet0[0, k] = self.sequences.fluxes.et0[k]
    cpdef inline void calc_evpo_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.evpo[k] = self.parameters.control.fln[self.parameters.control.lnk[k] - 1, self.parameters.derived.moy[self.idx_sim]] * self.sequences.fluxes.et0[k]
    cpdef inline void calc_nbes_inzp_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.nbes[k] = 0.0
                self.sequences.states.inzp[k] = 0.0
            else:
                self.sequences.fluxes.nbes[k] = max(                    self.sequences.fluxes.nkor[k]                    + self.sequences.states.inzp[k]                    - self.parameters.derived.kinz[self.parameters.control.lnk[k] - 1, self.parameters.derived.moy[self.idx_sim]],                    0.0,                )
                self.sequences.states.inzp[k] = self.sequences.states.inzp[k] + (self.sequences.fluxes.nkor[k] - self.sequences.fluxes.nbes[k])
    cpdef inline void calc_evi_inzp_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.evi[k] = self.sequences.fluxes.evpo[k]
                self.sequences.states.inzp[k] = 0.0
            else:
                self.sequences.fluxes.evi[k] = min(self.sequences.fluxes.evpo[k], self.sequences.states.inzp[k])
                self.sequences.states.inzp[k] = self.sequences.states.inzp[k] - (self.sequences.fluxes.evi[k])
    cpdef inline void calc_snratio_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.sequences.fluxes.tkor[k] >= (self.parameters.control.tgr[k] + self.parameters.control.tsp[k] / 2.0):
                self.sequences.aides.snratio[k] = 0.0
            elif self.sequences.fluxes.tkor[k] <= (self.parameters.control.tgr[k] - self.parameters.control.tsp[k] / 2.0):
                self.sequences.aides.snratio[k] = 1.0
            else:
                self.sequences.aides.snratio[k] = (                    (self.parameters.control.tgr[k] + self.parameters.control.tsp[k] / 2.0) - self.sequences.fluxes.tkor[k]                ) / self.parameters.control.tsp[k]
    cpdef inline void calc_sbes_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.sbes[k] = self.sequences.aides.snratio[k] * self.sequences.fluxes.nbes[k]
    cpdef inline void calc_wats_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.states.wats[k] = 0.0
            else:
                self.sequences.states.wats[k] = self.sequences.states.wats[k] + (self.sequences.fluxes.sbes[k])
    cpdef inline void calc_wgtf_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.wgtf[k] = 0.0
            else:
                self.sequences.fluxes.wgtf[k] = self.parameters.control.gtf[k] * (self.sequences.fluxes.tkor[k] - self.parameters.control.treft[k]) * self.parameters.fixed.rschmelz
    cpdef inline void calc_wnied_v1(self)  nogil:
        cdef double d_water
        cdef double d_ice
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.wnied[k] = 0.0
            else:
                d_ice = self.parameters.fixed.cpeis * self.sequences.fluxes.sbes[k]
                d_water = self.parameters.fixed.cpwasser * (self.sequences.fluxes.nbes[k] - self.sequences.fluxes.sbes[k])
                self.sequences.fluxes.wnied[k] = (self.sequences.fluxes.tkor[k] - self.parameters.control.trefn[k]) * (d_ice + d_water)
    cpdef inline void calc_schmpot_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.schmpot[k] = max((self.sequences.fluxes.wgtf[k] + self.sequences.fluxes.wnied[k]) / self.parameters.fixed.rschmelz, 0.0)
    cpdef inline void calc_schm_wats_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.schm[k] = 0.0
            else:
                self.sequences.fluxes.schm[k] = min(self.sequences.fluxes.schmpot[k], self.sequences.states.wats[k])
                self.sequences.states.wats[k] = self.sequences.states.wats[k] - (self.sequences.fluxes.schm[k])
    cpdef inline void calc_wada_waes_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.states.waes[k] = 0.0
                self.sequences.fluxes.wada[k] = self.sequences.fluxes.nbes[k]
            else:
                self.sequences.states.waes[k] = self.sequences.states.waes[k] + (self.sequences.fluxes.nbes[k])
                self.sequences.fluxes.wada[k] = max(self.sequences.states.waes[k] - self.parameters.control.pwmax[k] * self.sequences.states.wats[k], 0.0)
                self.sequences.states.waes[k] = self.sequences.states.waes[k] - (self.sequences.fluxes.wada[k])
    cpdef inline void calc_evb_v1(self)  nogil:
        cdef double d_temp
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE) or self.parameters.control.wmax[k] <= 0.0:
                self.sequences.fluxes.evb[k] = 0.0
            else:
                d_temp = exp(-self.parameters.control.grasref_r * self.sequences.states.bowa[k] / self.parameters.control.wmax[k])
                self.sequences.fluxes.evb[k] = (                    (self.sequences.fluxes.evpo[k] - self.sequences.fluxes.evi[k])                    * (1.0 - d_temp)                    / (1.0 + d_temp - 2.0 * exp(-self.parameters.control.grasref_r))                )
    cpdef inline void calc_qkap_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE)) or (self.parameters.control.wmax[k] <= 0.0):
                self.sequences.fluxes.qkap[k] = 0.0
            elif self.sequences.states.bowa[k] <= self.parameters.control.kapgrenz[k, 0]:
                self.sequences.fluxes.qkap[k] = self.parameters.control.kapmax[k]
            elif self.sequences.states.bowa[k] <= self.parameters.control.kapgrenz[k, 1]:
                self.sequences.fluxes.qkap[k] = self.parameters.control.kapmax[k] * (                    1.0                    - (self.sequences.states.bowa[k] - self.parameters.control.kapgrenz[k, 0])                    / (self.parameters.control.kapgrenz[k, 1] - self.parameters.control.kapgrenz[k, 0])                )
            else:
                self.sequences.fluxes.qkap[k] = 0
    cpdef inline void calc_qbb_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (                (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE))                or (self.sequences.states.bowa[k] <= self.parameters.control.pwp[k])                or (self.parameters.control.wmax[k] <= 0.0)            ):
                self.sequences.fluxes.qbb[k] = 0.0
            elif self.sequences.states.bowa[k] <= self.parameters.control.fk[k]:
                if self.parameters.control.rbeta:
                    self.sequences.fluxes.qbb[k] = 0.0
                else:
                    self.sequences.fluxes.qbb[k] = self.parameters.control.beta[k] * (self.sequences.states.bowa[k] - self.parameters.control.pwp[k])
            else:
                self.sequences.fluxes.qbb[k] = (                    self.parameters.control.beta[k]                    * (self.sequences.states.bowa[k] - self.parameters.control.pwp[k])                    * (                        1.0                        + (self.parameters.control.fbeta[k] - 1.0)                        * (self.sequences.states.bowa[k] - self.parameters.control.fk[k])                        / (self.parameters.control.wmax[k] - self.parameters.control.fk[k])                    )                )
    cpdef inline void calc_qib1_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE)) or (                self.sequences.states.bowa[k] <= self.parameters.control.pwp[k]            ):
                self.sequences.fluxes.qib1[k] = 0.0
            else:
                self.sequences.fluxes.qib1[k] = self.parameters.control.dmin[k] * (self.sequences.states.bowa[k] / self.parameters.control.wmax[k])
    cpdef inline void calc_qib2_v1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (                (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE))                or (self.sequences.states.bowa[k] <= self.parameters.control.fk[k])                or (self.parameters.control.wmax[k] <= self.parameters.control.fk[k])            ):
                self.sequences.fluxes.qib2[k] = 0.0
            else:
                self.sequences.fluxes.qib2[k] = (self.parameters.control.dmax[k] - self.parameters.control.dmin[k]) * (                    (self.sequences.states.bowa[k] - self.parameters.control.fk[k]) / (self.parameters.control.wmax[k] - self.parameters.control.fk[k])                ) ** 1.5
    cpdef inline void calc_qdb_v1(self)  nogil:
        cdef double d_exz
        cdef double d_sfa
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == WASSER:
                self.sequences.fluxes.qdb[k] = 0.0
            elif (self.parameters.control.lnk[k] in (VERS, FLUSS, SEE)) or (self.parameters.control.wmax[k] <= 0.0):
                self.sequences.fluxes.qdb[k] = self.sequences.fluxes.wada[k]
            else:
                if self.sequences.states.bowa[k] < self.parameters.control.wmax[k]:
                    d_sfa = (1.0 - self.sequences.states.bowa[k] / self.parameters.control.wmax[k]) ** (                        1.0 / (self.parameters.control.bsf[k] + 1.0)                    ) - (self.sequences.fluxes.wada[k] / ((self.parameters.control.bsf[k] + 1.0) * self.parameters.control.wmax[k]))
                else:
                    d_sfa = 0.0
                d_exz = self.sequences.states.bowa[k] + self.sequences.fluxes.wada[k] - self.parameters.control.wmax[k]
                self.sequences.fluxes.qdb[k] = d_exz
                if d_sfa > 0.0:
                    self.sequences.fluxes.qdb[k] = self.sequences.fluxes.qdb[k] + (d_sfa ** (self.parameters.control.bsf[k] + 1.0) * self.parameters.control.wmax[k])
                self.sequences.fluxes.qdb[k] = max(self.sequences.fluxes.qdb[k], 0.0)
    cpdef inline void calc_bowa_v1(self)  nogil:
        cdef double d_factor
        cdef double d_rvl
        cdef double d_incr
        cdef double d_decr
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE):
                self.sequences.states.bowa[k] = 0.0
            else:
                d_decr = self.sequences.fluxes.qbb[k] + self.sequences.fluxes.qib1[k] + self.sequences.fluxes.qib2[k] + self.sequences.fluxes.qdb[k]
                d_incr = self.sequences.fluxes.wada[k] + self.sequences.fluxes.qkap[k]
                if self.sequences.fluxes.evb[k] > 0.0:
                    d_decr = d_decr + (self.sequences.fluxes.evb[k])
                else:
                    d_incr = d_incr - (self.sequences.fluxes.evb[k])
                if d_decr > self.sequences.states.bowa[k] + d_incr:
                    d_rvl = (self.sequences.states.bowa[k] + d_incr) / d_decr
                    if self.sequences.fluxes.evb[k] > 0.0:
                        self.sequences.fluxes.evb[k] = self.sequences.fluxes.evb[k] * (d_rvl)
                    self.sequences.fluxes.qbb[k] = self.sequences.fluxes.qbb[k] * (d_rvl)
                    self.sequences.fluxes.qib1[k] = self.sequences.fluxes.qib1[k] * (d_rvl)
                    self.sequences.fluxes.qib2[k] = self.sequences.fluxes.qib2[k] * (d_rvl)
                    self.sequences.fluxes.qdb[k] = self.sequences.fluxes.qdb[k] * (d_rvl)
                    self.sequences.states.bowa[k] = 0.0
                else:
                    self.sequences.states.bowa[k] = (self.sequences.states.bowa[k] + d_incr) - d_decr
                    if self.sequences.states.bowa[k] > self.parameters.control.wmax[k]:
                        d_factor = (self.sequences.states.bowa[k] - self.parameters.control.wmax[k]) / d_incr
                        if self.sequences.fluxes.evb[k] < 0.0:
                            self.sequences.fluxes.evb[k] = self.sequences.fluxes.evb[k] * (d_factor)
                        self.sequences.fluxes.wada[k] = self.sequences.fluxes.wada[k] * (d_factor)
                        self.sequences.fluxes.qkap[k] = self.sequences.fluxes.qkap[k] * (d_factor)
                        self.sequences.states.bowa[k] = self.parameters.control.wmax[k]
    cpdef inline void calc_qbgz_v1(self)  nogil:
        cdef int k
        self.sequences.states.qbgz = 0.0
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == SEE:
                self.sequences.states.qbgz = self.sequences.states.qbgz + (self.parameters.control.fhru[k] * (self.sequences.fluxes.nkor[k] - self.sequences.fluxes.evi[k]))
            elif self.parameters.control.lnk[k] not in (WASSER, FLUSS, VERS):
                self.sequences.states.qbgz = self.sequences.states.qbgz + (self.parameters.control.fhru[k] * (self.sequences.fluxes.qbb[k] - self.sequences.fluxes.qkap[k]))
    cpdef inline void calc_qigz1_v1(self)  nogil:
        cdef int k
        self.sequences.states.qigz1 = 0.0
        for k in range(self.parameters.control.nhru):
            self.sequences.states.qigz1 = self.sequences.states.qigz1 + (self.parameters.control.fhru[k] * self.sequences.fluxes.qib1[k])
    cpdef inline void calc_qigz2_v1(self)  nogil:
        cdef int k
        self.sequences.states.qigz2 = 0.0
        for k in range(self.parameters.control.nhru):
            self.sequences.states.qigz2 = self.sequences.states.qigz2 + (self.parameters.control.fhru[k] * self.sequences.fluxes.qib2[k])
    cpdef inline void calc_qdgz_v1(self)  nogil:
        cdef int k
        self.sequences.fluxes.qdgz = 0.0
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == FLUSS:
                self.sequences.fluxes.qdgz = self.sequences.fluxes.qdgz + (self.parameters.control.fhru[k] * (self.sequences.fluxes.nkor[k] - self.sequences.fluxes.evi[k]))
            elif self.parameters.control.lnk[k] not in (WASSER, SEE):
                self.sequences.fluxes.qdgz = self.sequences.fluxes.qdgz + (self.parameters.control.fhru[k] * self.sequences.fluxes.qdb[k])
    cpdef inline void calc_qbga_v1(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.kb <= 0.0:
            self.sequences.new_states.qbga = self.sequences.new_states.qbgz
        elif self.parameters.derived.kb > 1e200:
            self.sequences.new_states.qbga = self.sequences.old_states.qbga + self.sequences.new_states.qbgz - self.sequences.old_states.qbgz
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.kb)
            self.sequences.new_states.qbga = (                self.sequences.old_states.qbga                + (self.sequences.old_states.qbgz - self.sequences.old_states.qbga) * d_temp                + (self.sequences.new_states.qbgz - self.sequences.old_states.qbgz) * (1.0 - self.parameters.derived.kb * d_temp)            )
    cpdef inline void update_qdgz_qbgz_qbga_v1(self)  nogil:
        cdef double d_qbgz_adj
        cdef double d_temp
        if self.sequences.new_states.qbga > self.parameters.derived.qbgamax:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.kb)
            d_qbgz_adj = self.sequences.old_states.qbgz + (                (self.parameters.derived.qbgamax - self.sequences.old_states.qbga - (self.sequences.old_states.qbgz - self.sequences.old_states.qbga) * d_temp)                / (1.0 - self.parameters.derived.kb * d_temp)            )
            self.sequences.new_states.qbga = self.parameters.derived.qbgamax
            self.sequences.fluxes.qdgz = self.sequences.fluxes.qdgz + (self.sequences.new_states.qbgz - d_qbgz_adj)
            self.sequences.new_states.qbgz = d_qbgz_adj
    cpdef inline void update_qdgz_qbgz_qbga_v2(self)  nogil:
        cdef double d_qbgz_exc
        cdef double d_grad
        d_grad = self.parameters.derived.kb * (self.sequences.new_states.qbga - self.sequences.old_states.qbga)
        if d_grad > self.parameters.control.gsbgrad1:
            if d_grad < self.parameters.control.gsbgrad2:
                d_qbgz_exc = self.sequences.new_states.qbgz * (                    (d_grad - self.parameters.control.gsbgrad1) / (self.parameters.control.gsbgrad2 - self.parameters.control.gsbgrad1)                )
            else:
                d_qbgz_exc = self.sequences.new_states.qbgz
            self.sequences.fluxes.qdgz = self.sequences.fluxes.qdgz + (d_qbgz_exc)
            self.sequences.new_states.qbgz = self.sequences.new_states.qbgz - (d_qbgz_exc)
            self.calc_qbga_v1()
    cpdef inline void calc_qiga1_v1(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.ki1 <= 0.0:
            self.sequences.new_states.qiga1 = self.sequences.new_states.qigz1
        elif self.parameters.derived.ki1 > 1e200:
            self.sequences.new_states.qiga1 = self.sequences.old_states.qiga1 + self.sequences.new_states.qigz1 - self.sequences.old_states.qigz1
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.ki1)
            self.sequences.new_states.qiga1 = (                self.sequences.old_states.qiga1                + (self.sequences.old_states.qigz1 - self.sequences.old_states.qiga1) * d_temp                + (self.sequences.new_states.qigz1 - self.sequences.old_states.qigz1) * (1.0 - self.parameters.derived.ki1 * d_temp)            )
    cpdef inline void calc_qiga2_v1(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.ki2 <= 0.0:
            self.sequences.new_states.qiga2 = self.sequences.new_states.qigz2
        elif self.parameters.derived.ki2 > 1e200:
            self.sequences.new_states.qiga2 = self.sequences.old_states.qiga2 + self.sequences.new_states.qigz2 - self.sequences.old_states.qigz2
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.ki2)
            self.sequences.new_states.qiga2 = (                self.sequences.old_states.qiga2                + (self.sequences.old_states.qigz2 - self.sequences.old_states.qiga2) * d_temp                + (self.sequences.new_states.qigz2 - self.sequences.old_states.qigz2) * (1.0 - self.parameters.derived.ki2 * d_temp)            )
    cpdef inline void calc_qdgz1_qdgz2_v1(self)  nogil:
        if self.sequences.fluxes.qdgz > self.parameters.control.a2:
            self.sequences.states.qdgz2 = (self.sequences.fluxes.qdgz - self.parameters.control.a2) ** 2 / (self.sequences.fluxes.qdgz + self.parameters.control.a1 - self.parameters.control.a2)
            self.sequences.states.qdgz1 = self.sequences.fluxes.qdgz - self.sequences.states.qdgz2
        else:
            self.sequences.states.qdgz2 = 0.0
            self.sequences.states.qdgz1 = self.sequences.fluxes.qdgz
    cpdef inline void calc_qdga1_v1(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.kd1 <= 0.0:
            self.sequences.new_states.qdga1 = self.sequences.new_states.qdgz1
        elif self.parameters.derived.kd1 > 1e200:
            self.sequences.new_states.qdga1 = self.sequences.old_states.qdga1 + self.sequences.new_states.qdgz1 - self.sequences.old_states.qdgz1
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.kd1)
            self.sequences.new_states.qdga1 = (                self.sequences.old_states.qdga1                + (self.sequences.old_states.qdgz1 - self.sequences.old_states.qdga1) * d_temp                + (self.sequences.new_states.qdgz1 - self.sequences.old_states.qdgz1) * (1.0 - self.parameters.derived.kd1 * d_temp)            )
    cpdef inline void calc_qdga2_v1(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.kd2 <= 0.0:
            self.sequences.new_states.qdga2 = self.sequences.new_states.qdgz2
        elif self.parameters.derived.kd2 > 1e200:
            self.sequences.new_states.qdga2 = self.sequences.old_states.qdga2 + self.sequences.new_states.qdgz2 - self.sequences.old_states.qdgz2
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.kd2)
            self.sequences.new_states.qdga2 = (                self.sequences.old_states.qdga2                + (self.sequences.old_states.qdgz2 - self.sequences.old_states.qdga2) * d_temp                + (self.sequences.new_states.qdgz2 - self.sequences.old_states.qdgz2) * (1.0 - self.parameters.derived.kd2 * d_temp)            )
    cpdef inline void calc_qah_v1(self)  nogil:
        cdef double d_epw
        cdef int k
        cdef double d_area
        self.sequences.fluxes.qah = self.sequences.fluxes.qzh + self.sequences.states.qbga + self.sequences.states.qiga1 + self.sequences.states.qiga2 + self.sequences.states.qdga1 + self.sequences.states.qdga2
        if (not self.parameters.control.negq) and (self.sequences.fluxes.qah < 0.0):
            d_area = 0.0
            for k in range(self.parameters.control.nhru):
                if self.parameters.control.lnk[k] in (FLUSS, SEE):
                    d_area = d_area + (self.parameters.control.fhru[k])
            if d_area > 0.0:
                for k in range(self.parameters.control.nhru):
                    if self.parameters.control.lnk[k] in (FLUSS, SEE):
                        self.sequences.fluxes.evi[k] = self.sequences.fluxes.evi[k] + (self.sequences.fluxes.qah / d_area)
            self.sequences.fluxes.qah = 0.0
        d_epw = 0.0
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == WASSER:
                self.sequences.fluxes.qah = self.sequences.fluxes.qah + (self.parameters.control.fhru[k] * self.sequences.fluxes.nkor[k])
                d_epw = d_epw + (self.parameters.control.fhru[k] * self.sequences.fluxes.evi[k])
        if (self.sequences.fluxes.qah > d_epw) or self.parameters.control.negq:
            self.sequences.fluxes.qah = self.sequences.fluxes.qah - (d_epw)
        elif d_epw > 0.0:
            for k in range(self.parameters.control.nhru):
                if self.parameters.control.lnk[k] == WASSER:
                    self.sequences.fluxes.evi[k] = self.sequences.fluxes.evi[k] * (self.sequences.fluxes.qah / d_epw)
            self.sequences.fluxes.qah = 0.0
    cpdef inline void calc_qa_v1(self)  nogil:
        self.sequences.fluxes.qa = self.parameters.derived.qfactor * self.sequences.fluxes.qah
    cpdef inline void calc_qzh(self)  nogil:
        self.sequences.fluxes.qzh = self.sequences.fluxes.qz / self.parameters.derived.qfactor
    cpdef inline void calc_nkor(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.nkor[k] = self.parameters.control.kg[k] * self.sequences.inputs.nied
    cpdef inline void calc_tkor(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.tkor[k] = self.parameters.control.kt[k] + self.sequences.inputs.teml
    cpdef inline void calc_et0_wet0(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.et0[k] = (                self.parameters.control.wfet0[k] * self.parameters.control.ke[k] * self.sequences.inputs.pet                + (1.0 - self.parameters.control.wfet0[k]) * self.sequences.logs.wet0[0, k]            )
            self.sequences.logs.wet0[0, k] = self.sequences.fluxes.et0[k]
    cpdef inline void calc_evpo(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.evpo[k] = self.parameters.control.fln[self.parameters.control.lnk[k] - 1, self.parameters.derived.moy[self.idx_sim]] * self.sequences.fluxes.et0[k]
    cpdef inline void calc_nbes_inzp(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.nbes[k] = 0.0
                self.sequences.states.inzp[k] = 0.0
            else:
                self.sequences.fluxes.nbes[k] = max(                    self.sequences.fluxes.nkor[k]                    + self.sequences.states.inzp[k]                    - self.parameters.derived.kinz[self.parameters.control.lnk[k] - 1, self.parameters.derived.moy[self.idx_sim]],                    0.0,                )
                self.sequences.states.inzp[k] = self.sequences.states.inzp[k] + (self.sequences.fluxes.nkor[k] - self.sequences.fluxes.nbes[k])
    cpdef inline void calc_evi_inzp(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.evi[k] = self.sequences.fluxes.evpo[k]
                self.sequences.states.inzp[k] = 0.0
            else:
                self.sequences.fluxes.evi[k] = min(self.sequences.fluxes.evpo[k], self.sequences.states.inzp[k])
                self.sequences.states.inzp[k] = self.sequences.states.inzp[k] - (self.sequences.fluxes.evi[k])
    cpdef inline void calc_snratio(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.sequences.fluxes.tkor[k] >= (self.parameters.control.tgr[k] + self.parameters.control.tsp[k] / 2.0):
                self.sequences.aides.snratio[k] = 0.0
            elif self.sequences.fluxes.tkor[k] <= (self.parameters.control.tgr[k] - self.parameters.control.tsp[k] / 2.0):
                self.sequences.aides.snratio[k] = 1.0
            else:
                self.sequences.aides.snratio[k] = (                    (self.parameters.control.tgr[k] + self.parameters.control.tsp[k] / 2.0) - self.sequences.fluxes.tkor[k]                ) / self.parameters.control.tsp[k]
    cpdef inline void calc_sbes(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.sbes[k] = self.sequences.aides.snratio[k] * self.sequences.fluxes.nbes[k]
    cpdef inline void calc_wats(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.states.wats[k] = 0.0
            else:
                self.sequences.states.wats[k] = self.sequences.states.wats[k] + (self.sequences.fluxes.sbes[k])
    cpdef inline void calc_wgtf(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.wgtf[k] = 0.0
            else:
                self.sequences.fluxes.wgtf[k] = self.parameters.control.gtf[k] * (self.sequences.fluxes.tkor[k] - self.parameters.control.treft[k]) * self.parameters.fixed.rschmelz
    cpdef inline void calc_wnied(self)  nogil:
        cdef double d_water
        cdef double d_ice
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.wnied[k] = 0.0
            else:
                d_ice = self.parameters.fixed.cpeis * self.sequences.fluxes.sbes[k]
                d_water = self.parameters.fixed.cpwasser * (self.sequences.fluxes.nbes[k] - self.sequences.fluxes.sbes[k])
                self.sequences.fluxes.wnied[k] = (self.sequences.fluxes.tkor[k] - self.parameters.control.trefn[k]) * (d_ice + d_water)
    cpdef inline void calc_schmpot(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            self.sequences.fluxes.schmpot[k] = max((self.sequences.fluxes.wgtf[k] + self.sequences.fluxes.wnied[k]) / self.parameters.fixed.rschmelz, 0.0)
    cpdef inline void calc_schm_wats(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.fluxes.schm[k] = 0.0
            else:
                self.sequences.fluxes.schm[k] = min(self.sequences.fluxes.schmpot[k], self.sequences.states.wats[k])
                self.sequences.states.wats[k] = self.sequences.states.wats[k] - (self.sequences.fluxes.schm[k])
    cpdef inline void calc_wada_waes(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (WASSER, FLUSS, SEE):
                self.sequences.states.waes[k] = 0.0
                self.sequences.fluxes.wada[k] = self.sequences.fluxes.nbes[k]
            else:
                self.sequences.states.waes[k] = self.sequences.states.waes[k] + (self.sequences.fluxes.nbes[k])
                self.sequences.fluxes.wada[k] = max(self.sequences.states.waes[k] - self.parameters.control.pwmax[k] * self.sequences.states.wats[k], 0.0)
                self.sequences.states.waes[k] = self.sequences.states.waes[k] - (self.sequences.fluxes.wada[k])
    cpdef inline void calc_evb(self)  nogil:
        cdef double d_temp
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE) or self.parameters.control.wmax[k] <= 0.0:
                self.sequences.fluxes.evb[k] = 0.0
            else:
                d_temp = exp(-self.parameters.control.grasref_r * self.sequences.states.bowa[k] / self.parameters.control.wmax[k])
                self.sequences.fluxes.evb[k] = (                    (self.sequences.fluxes.evpo[k] - self.sequences.fluxes.evi[k])                    * (1.0 - d_temp)                    / (1.0 + d_temp - 2.0 * exp(-self.parameters.control.grasref_r))                )
    cpdef inline void calc_qkap(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE)) or (self.parameters.control.wmax[k] <= 0.0):
                self.sequences.fluxes.qkap[k] = 0.0
            elif self.sequences.states.bowa[k] <= self.parameters.control.kapgrenz[k, 0]:
                self.sequences.fluxes.qkap[k] = self.parameters.control.kapmax[k]
            elif self.sequences.states.bowa[k] <= self.parameters.control.kapgrenz[k, 1]:
                self.sequences.fluxes.qkap[k] = self.parameters.control.kapmax[k] * (                    1.0                    - (self.sequences.states.bowa[k] - self.parameters.control.kapgrenz[k, 0])                    / (self.parameters.control.kapgrenz[k, 1] - self.parameters.control.kapgrenz[k, 0])                )
            else:
                self.sequences.fluxes.qkap[k] = 0
    cpdef inline void calc_qbb(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (                (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE))                or (self.sequences.states.bowa[k] <= self.parameters.control.pwp[k])                or (self.parameters.control.wmax[k] <= 0.0)            ):
                self.sequences.fluxes.qbb[k] = 0.0
            elif self.sequences.states.bowa[k] <= self.parameters.control.fk[k]:
                if self.parameters.control.rbeta:
                    self.sequences.fluxes.qbb[k] = 0.0
                else:
                    self.sequences.fluxes.qbb[k] = self.parameters.control.beta[k] * (self.sequences.states.bowa[k] - self.parameters.control.pwp[k])
            else:
                self.sequences.fluxes.qbb[k] = (                    self.parameters.control.beta[k]                    * (self.sequences.states.bowa[k] - self.parameters.control.pwp[k])                    * (                        1.0                        + (self.parameters.control.fbeta[k] - 1.0)                        * (self.sequences.states.bowa[k] - self.parameters.control.fk[k])                        / (self.parameters.control.wmax[k] - self.parameters.control.fk[k])                    )                )
    cpdef inline void calc_qib1(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE)) or (                self.sequences.states.bowa[k] <= self.parameters.control.pwp[k]            ):
                self.sequences.fluxes.qib1[k] = 0.0
            else:
                self.sequences.fluxes.qib1[k] = self.parameters.control.dmin[k] * (self.sequences.states.bowa[k] / self.parameters.control.wmax[k])
    cpdef inline void calc_qib2(self)  nogil:
        cdef int k
        for k in range(self.parameters.control.nhru):
            if (                (self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE))                or (self.sequences.states.bowa[k] <= self.parameters.control.fk[k])                or (self.parameters.control.wmax[k] <= self.parameters.control.fk[k])            ):
                self.sequences.fluxes.qib2[k] = 0.0
            else:
                self.sequences.fluxes.qib2[k] = (self.parameters.control.dmax[k] - self.parameters.control.dmin[k]) * (                    (self.sequences.states.bowa[k] - self.parameters.control.fk[k]) / (self.parameters.control.wmax[k] - self.parameters.control.fk[k])                ) ** 1.5
    cpdef inline void calc_qdb(self)  nogil:
        cdef double d_exz
        cdef double d_sfa
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == WASSER:
                self.sequences.fluxes.qdb[k] = 0.0
            elif (self.parameters.control.lnk[k] in (VERS, FLUSS, SEE)) or (self.parameters.control.wmax[k] <= 0.0):
                self.sequences.fluxes.qdb[k] = self.sequences.fluxes.wada[k]
            else:
                if self.sequences.states.bowa[k] < self.parameters.control.wmax[k]:
                    d_sfa = (1.0 - self.sequences.states.bowa[k] / self.parameters.control.wmax[k]) ** (                        1.0 / (self.parameters.control.bsf[k] + 1.0)                    ) - (self.sequences.fluxes.wada[k] / ((self.parameters.control.bsf[k] + 1.0) * self.parameters.control.wmax[k]))
                else:
                    d_sfa = 0.0
                d_exz = self.sequences.states.bowa[k] + self.sequences.fluxes.wada[k] - self.parameters.control.wmax[k]
                self.sequences.fluxes.qdb[k] = d_exz
                if d_sfa > 0.0:
                    self.sequences.fluxes.qdb[k] = self.sequences.fluxes.qdb[k] + (d_sfa ** (self.parameters.control.bsf[k] + 1.0) * self.parameters.control.wmax[k])
                self.sequences.fluxes.qdb[k] = max(self.sequences.fluxes.qdb[k], 0.0)
    cpdef inline void calc_bowa(self)  nogil:
        cdef double d_factor
        cdef double d_rvl
        cdef double d_incr
        cdef double d_decr
        cdef int k
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] in (VERS, WASSER, FLUSS, SEE):
                self.sequences.states.bowa[k] = 0.0
            else:
                d_decr = self.sequences.fluxes.qbb[k] + self.sequences.fluxes.qib1[k] + self.sequences.fluxes.qib2[k] + self.sequences.fluxes.qdb[k]
                d_incr = self.sequences.fluxes.wada[k] + self.sequences.fluxes.qkap[k]
                if self.sequences.fluxes.evb[k] > 0.0:
                    d_decr = d_decr + (self.sequences.fluxes.evb[k])
                else:
                    d_incr = d_incr - (self.sequences.fluxes.evb[k])
                if d_decr > self.sequences.states.bowa[k] + d_incr:
                    d_rvl = (self.sequences.states.bowa[k] + d_incr) / d_decr
                    if self.sequences.fluxes.evb[k] > 0.0:
                        self.sequences.fluxes.evb[k] = self.sequences.fluxes.evb[k] * (d_rvl)
                    self.sequences.fluxes.qbb[k] = self.sequences.fluxes.qbb[k] * (d_rvl)
                    self.sequences.fluxes.qib1[k] = self.sequences.fluxes.qib1[k] * (d_rvl)
                    self.sequences.fluxes.qib2[k] = self.sequences.fluxes.qib2[k] * (d_rvl)
                    self.sequences.fluxes.qdb[k] = self.sequences.fluxes.qdb[k] * (d_rvl)
                    self.sequences.states.bowa[k] = 0.0
                else:
                    self.sequences.states.bowa[k] = (self.sequences.states.bowa[k] + d_incr) - d_decr
                    if self.sequences.states.bowa[k] > self.parameters.control.wmax[k]:
                        d_factor = (self.sequences.states.bowa[k] - self.parameters.control.wmax[k]) / d_incr
                        if self.sequences.fluxes.evb[k] < 0.0:
                            self.sequences.fluxes.evb[k] = self.sequences.fluxes.evb[k] * (d_factor)
                        self.sequences.fluxes.wada[k] = self.sequences.fluxes.wada[k] * (d_factor)
                        self.sequences.fluxes.qkap[k] = self.sequences.fluxes.qkap[k] * (d_factor)
                        self.sequences.states.bowa[k] = self.parameters.control.wmax[k]
    cpdef inline void calc_qbgz(self)  nogil:
        cdef int k
        self.sequences.states.qbgz = 0.0
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == SEE:
                self.sequences.states.qbgz = self.sequences.states.qbgz + (self.parameters.control.fhru[k] * (self.sequences.fluxes.nkor[k] - self.sequences.fluxes.evi[k]))
            elif self.parameters.control.lnk[k] not in (WASSER, FLUSS, VERS):
                self.sequences.states.qbgz = self.sequences.states.qbgz + (self.parameters.control.fhru[k] * (self.sequences.fluxes.qbb[k] - self.sequences.fluxes.qkap[k]))
    cpdef inline void calc_qigz1(self)  nogil:
        cdef int k
        self.sequences.states.qigz1 = 0.0
        for k in range(self.parameters.control.nhru):
            self.sequences.states.qigz1 = self.sequences.states.qigz1 + (self.parameters.control.fhru[k] * self.sequences.fluxes.qib1[k])
    cpdef inline void calc_qigz2(self)  nogil:
        cdef int k
        self.sequences.states.qigz2 = 0.0
        for k in range(self.parameters.control.nhru):
            self.sequences.states.qigz2 = self.sequences.states.qigz2 + (self.parameters.control.fhru[k] * self.sequences.fluxes.qib2[k])
    cpdef inline void calc_qdgz(self)  nogil:
        cdef int k
        self.sequences.fluxes.qdgz = 0.0
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == FLUSS:
                self.sequences.fluxes.qdgz = self.sequences.fluxes.qdgz + (self.parameters.control.fhru[k] * (self.sequences.fluxes.nkor[k] - self.sequences.fluxes.evi[k]))
            elif self.parameters.control.lnk[k] not in (WASSER, SEE):
                self.sequences.fluxes.qdgz = self.sequences.fluxes.qdgz + (self.parameters.control.fhru[k] * self.sequences.fluxes.qdb[k])
    cpdef inline void calc_qbga(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.kb <= 0.0:
            self.sequences.new_states.qbga = self.sequences.new_states.qbgz
        elif self.parameters.derived.kb > 1e200:
            self.sequences.new_states.qbga = self.sequences.old_states.qbga + self.sequences.new_states.qbgz - self.sequences.old_states.qbgz
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.kb)
            self.sequences.new_states.qbga = (                self.sequences.old_states.qbga                + (self.sequences.old_states.qbgz - self.sequences.old_states.qbga) * d_temp                + (self.sequences.new_states.qbgz - self.sequences.old_states.qbgz) * (1.0 - self.parameters.derived.kb * d_temp)            )
    cpdef inline void calc_qiga1(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.ki1 <= 0.0:
            self.sequences.new_states.qiga1 = self.sequences.new_states.qigz1
        elif self.parameters.derived.ki1 > 1e200:
            self.sequences.new_states.qiga1 = self.sequences.old_states.qiga1 + self.sequences.new_states.qigz1 - self.sequences.old_states.qigz1
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.ki1)
            self.sequences.new_states.qiga1 = (                self.sequences.old_states.qiga1                + (self.sequences.old_states.qigz1 - self.sequences.old_states.qiga1) * d_temp                + (self.sequences.new_states.qigz1 - self.sequences.old_states.qigz1) * (1.0 - self.parameters.derived.ki1 * d_temp)            )
    cpdef inline void calc_qiga2(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.ki2 <= 0.0:
            self.sequences.new_states.qiga2 = self.sequences.new_states.qigz2
        elif self.parameters.derived.ki2 > 1e200:
            self.sequences.new_states.qiga2 = self.sequences.old_states.qiga2 + self.sequences.new_states.qigz2 - self.sequences.old_states.qigz2
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.ki2)
            self.sequences.new_states.qiga2 = (                self.sequences.old_states.qiga2                + (self.sequences.old_states.qigz2 - self.sequences.old_states.qiga2) * d_temp                + (self.sequences.new_states.qigz2 - self.sequences.old_states.qigz2) * (1.0 - self.parameters.derived.ki2 * d_temp)            )
    cpdef inline void calc_qdgz1_qdgz2(self)  nogil:
        if self.sequences.fluxes.qdgz > self.parameters.control.a2:
            self.sequences.states.qdgz2 = (self.sequences.fluxes.qdgz - self.parameters.control.a2) ** 2 / (self.sequences.fluxes.qdgz + self.parameters.control.a1 - self.parameters.control.a2)
            self.sequences.states.qdgz1 = self.sequences.fluxes.qdgz - self.sequences.states.qdgz2
        else:
            self.sequences.states.qdgz2 = 0.0
            self.sequences.states.qdgz1 = self.sequences.fluxes.qdgz
    cpdef inline void calc_qdga1(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.kd1 <= 0.0:
            self.sequences.new_states.qdga1 = self.sequences.new_states.qdgz1
        elif self.parameters.derived.kd1 > 1e200:
            self.sequences.new_states.qdga1 = self.sequences.old_states.qdga1 + self.sequences.new_states.qdgz1 - self.sequences.old_states.qdgz1
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.kd1)
            self.sequences.new_states.qdga1 = (                self.sequences.old_states.qdga1                + (self.sequences.old_states.qdgz1 - self.sequences.old_states.qdga1) * d_temp                + (self.sequences.new_states.qdgz1 - self.sequences.old_states.qdgz1) * (1.0 - self.parameters.derived.kd1 * d_temp)            )
    cpdef inline void calc_qdga2(self)  nogil:
        cdef double d_temp
        if self.parameters.derived.kd2 <= 0.0:
            self.sequences.new_states.qdga2 = self.sequences.new_states.qdgz2
        elif self.parameters.derived.kd2 > 1e200:
            self.sequences.new_states.qdga2 = self.sequences.old_states.qdga2 + self.sequences.new_states.qdgz2 - self.sequences.old_states.qdgz2
        else:
            d_temp = 1.0 - exp(-1.0 / self.parameters.derived.kd2)
            self.sequences.new_states.qdga2 = (                self.sequences.old_states.qdga2                + (self.sequences.old_states.qdgz2 - self.sequences.old_states.qdga2) * d_temp                + (self.sequences.new_states.qdgz2 - self.sequences.old_states.qdgz2) * (1.0 - self.parameters.derived.kd2 * d_temp)            )
    cpdef inline void calc_qah(self)  nogil:
        cdef double d_epw
        cdef int k
        cdef double d_area
        self.sequences.fluxes.qah = self.sequences.fluxes.qzh + self.sequences.states.qbga + self.sequences.states.qiga1 + self.sequences.states.qiga2 + self.sequences.states.qdga1 + self.sequences.states.qdga2
        if (not self.parameters.control.negq) and (self.sequences.fluxes.qah < 0.0):
            d_area = 0.0
            for k in range(self.parameters.control.nhru):
                if self.parameters.control.lnk[k] in (FLUSS, SEE):
                    d_area = d_area + (self.parameters.control.fhru[k])
            if d_area > 0.0:
                for k in range(self.parameters.control.nhru):
                    if self.parameters.control.lnk[k] in (FLUSS, SEE):
                        self.sequences.fluxes.evi[k] = self.sequences.fluxes.evi[k] + (self.sequences.fluxes.qah / d_area)
            self.sequences.fluxes.qah = 0.0
        d_epw = 0.0
        for k in range(self.parameters.control.nhru):
            if self.parameters.control.lnk[k] == WASSER:
                self.sequences.fluxes.qah = self.sequences.fluxes.qah + (self.parameters.control.fhru[k] * self.sequences.fluxes.nkor[k])
                d_epw = d_epw + (self.parameters.control.fhru[k] * self.sequences.fluxes.evi[k])
        if (self.sequences.fluxes.qah > d_epw) or self.parameters.control.negq:
            self.sequences.fluxes.qah = self.sequences.fluxes.qah - (d_epw)
        elif d_epw > 0.0:
            for k in range(self.parameters.control.nhru):
                if self.parameters.control.lnk[k] == WASSER:
                    self.sequences.fluxes.evi[k] = self.sequences.fluxes.evi[k] * (self.sequences.fluxes.qah / d_epw)
            self.sequences.fluxes.qah = 0.0
    cpdef inline void calc_qa(self)  nogil:
        self.sequences.fluxes.qa = self.parameters.derived.qfactor * self.sequences.fluxes.qah
    cpdef inline void pass_qa_v1(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.qa)
    cpdef inline void pass_qa(self)  nogil:
        self.sequences.outlets.q[0] = self.sequences.outlets.q[0] + (self.sequences.fluxes.qa)
