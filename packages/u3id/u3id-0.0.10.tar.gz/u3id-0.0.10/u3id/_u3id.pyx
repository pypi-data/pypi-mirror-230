from typing import Optional, Type

from cpython cimport *
from libc.stdlib cimport calloc, free
from libc.string cimport memset

from fallback import U3ID

cdef extern from "stdint.h":
    ctypedef unsigned long long uint64_t
    ctypedef unsigned long uint32_t

cdef extern from "u3id.h":
    enum _error_code:
        E_SUCCESS,
        E_VALUE_ERROR,
        E_RAND_ERROR

    struct Error:
        _error_code code
        char message[500]

    void generate_u3id_std(
        unsigned char *uuuid_out,
        unsigned int timestamp_integer_part_length_bits,
        unsigned int timestamp_decimal_part_length_bits,
        unsigned int total_length_bits,
        Error *error
    )
    
    
    void generate_u3id_supply_chaotic(
        unsigned char *uuuid_out,
        unsigned int timestamp_integer_part_length_bits,
        unsigned int timestamp_decimal_part_length_bits,
        unsigned int total_length_bits,
        char *chaotic_part_seed,
        unsigned int chaotic_part_seed_length,
        Error *error
    )
    
    

    void generate_u3id_supply_time(
        unsigned char *uuuid_out,
        unsigned int timestamp_integer_part_length_bits,
        unsigned int timestamp_decimal_part_length_bits,
        unsigned int total_length_bits,
        uint64_t integer_time_part,
        uint32_t decimal_time_part_ns,
        Error *error
    );

    void generate_u3id_supply_all(
        unsigned char *uuuid_out,
        unsigned int timestamp_integer_part_length_bits,
        unsigned int timestamp_decimal_part_length_bits,
        unsigned int total_length_bits,
        uint64_t integer_time_part,
        uint32_t decimal_time_part_ns,
        char *chaotic_part_seed,
        unsigned int chaotic_part_seed_length,
        Error *error
    );
    
    void convert_little_to_big_endian(char * buf, unsigned int len)

cdef extern from "u3id_py.h":
    void generate_u3id_supply_chaotic_python(
            unsigned char *uuuid_out,
            unsigned int timestamp_integer_part_length_bits,
            unsigned int timestamp_decimal_part_length_bits,
            unsigned int total_length_bits,
            object chaotic_part_seed,
            Error *error
    )
    
    void generate_u3id_supply_all_python(
            unsigned char *uuuid_out,
            unsigned int timestamp_integer_part_length_bits,
            unsigned int timestamp_decimal_part_length_bits,
            unsigned int total_length_bits,
            uint64_t integer_time_part,
            uint32_t decimal_time_part_ns,
            object chaotic_part_seed,
            Error *error
    )

cdef class U3IDFactory(object):
    cdef unsigned char *u3id_buf
    cdef char *chaotic_part_seed
    cdef unsigned int timestamp_integer_part_length_bits
    cdef unsigned int timestamp_decimal_part_length_bits
    cdef unsigned int total_length_bits
    cdef unsigned int total_length_bytes

    cdef Error error

    def __init__(
            self,
            timestamp_integer_part_length_bits: int = 32,
            timestamp_decimal_part_length_bits: int = 10,
            total_length_bits: int = 128,
    ):
        pass

    def __cinit__(
            self,
            timestamp_integer_part_length_bits: int = 32,
            timestamp_decimal_part_length_bits: int = 10,
            total_length_bits: int = 128,
    ):
        # todo: add value checks here
        self.timestamp_integer_part_length_bits = timestamp_integer_part_length_bits
        self.timestamp_decimal_part_length_bits = timestamp_decimal_part_length_bits
        self.total_length_bits = total_length_bits
        self.total_length_bytes = total_length_bits//8
        self.u3id_buf = <unsigned char*> PyMem_Malloc(self.total_length_bytes)


    def __dealloc__(self):
        PyMem_Free(self.u3id_buf)
        #free(self.u3id_buf)
        self.u3id_buf = NULL

    def check_error(self):
        if self.error.code != E_SUCCESS:
            raise Exception(self.error.message.decode('ascii'))

    def generate(
            self,
            integer_time_part: Optional[int] = None,
            decimal_time_part_nanoseconds: Optional[int] = None,
            chaotic_part_seed: Optional[str] = None,
            float_time_part: Optional[float] = None,
    ):
        # set buffer to zero in case it contains a previously generated id
        memset(self.u3id_buf, 0, self.total_length_bytes)

        if float_time_part is not None and (integer_time_part is not None or decimal_time_part_nanoseconds is not None):
            raise ValueError("You can provide either the float_time_part or both of integer_time_part and decimal_time_part but not all.")

        if float_time_part is not None:
            integer_time_part = int(float_time_part)
            decimal_time_part_nanoseconds = int((float_time_part - integer_time_part) * 1_000_000_000)
        
        if integer_time_part is not None and decimal_time_part_nanoseconds is not None and chaotic_part_seed is not None:
            # user provided everything
            generate_u3id_supply_all_python(
                self.u3id_buf,
                self.timestamp_integer_part_length_bits,
                self.timestamp_decimal_part_length_bits,
                self.total_length_bits,
                <uint64_t>integer_time_part,
                <uint32_t>decimal_time_part_nanoseconds,
                chaotic_part_seed,
                &self.error
            )

            
        elif integer_time_part is not None and decimal_time_part_nanoseconds is not None:
            # user provided time component
            generate_u3id_supply_time(
                self.u3id_buf,
                self.timestamp_integer_part_length_bits,
                self.timestamp_decimal_part_length_bits,
                self.total_length_bits,
                <uint64_t> integer_time_part,
                <uint32_t> decimal_time_part_nanoseconds,
                &self.error
            )
        elif chaotic_part_seed is not None:
            # user provided chaotic component
            # print(PyUnicode_Check(chaotic_part_seed))
            generate_u3id_supply_chaotic_python(
                self.u3id_buf,
                self.timestamp_integer_part_length_bits,
                self.timestamp_decimal_part_length_bits,
                self.total_length_bits,
                chaotic_part_seed,
                &self.error
            )

        else:
            # user provided nothing
        
            generate_u3id_std(
                self.u3id_buf,
                self.timestamp_integer_part_length_bits,
                self.timestamp_decimal_part_length_bits,
                self.total_length_bits,
                &self.error
            )

        self.check_error()

        convert_little_to_big_endian(<char*>self.u3id_buf, self.total_length_bytes)
        return U3ID(PyBytes_FromStringAndSize(<char*>self.u3id_buf, self.total_length_bytes))




# python setup.py build_ext --inplace
