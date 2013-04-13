import ctypes
from ctypes import (POINTER, c_char_p, c_size_t, c_int, c_long, c_ulong,
                    c_double, c_void_p)
from ctypes.util import find_library


class _c_gsl_rng_type(ctypes.Structure):
    _fields_ = [('name', c_char_p),
                ('max', c_long),
                ('min', c_size_t),
                ('__set', c_void_p),
                ('__get', c_void_p),
                ('__get_double', c_void_p),
                ]
_c_gsl_rng_type_p = POINTER(_c_gsl_rng_type)


class _c_gsl_rng(ctypes.Structure):
    _fields_ = [('type', _c_gsl_rng_type_p),
                ('state', c_void_p)]
_c_gsl_rng_p = POINTER(_c_gsl_rng)


class _GSLFuncLoader(object):

    # see: http://code.activestate.com/recipes/576549-gsl-with-python3/
    gslcblas = ctypes.CDLL(find_library('gslcblas'), mode=ctypes.RTLD_GLOBAL)
    gsl = ctypes.CDLL(find_library('gsl'))

    def _load_1(self, name, argtypes=None, restype=None):
        func = getattr(self.gsl, name)
        if argtypes is not None:
            func.argtypes = argtypes
        if restype is not None:
            func.restype = restype
        setattr(self, name, func)
        return func

    def _load(self, name, argtypes=None, restype=None):
        if isinstance(name ,basestring):
            return self._load_1(name, argtypes, restype)
        else:
            try:
                return [self._load_1(n, argtypes, restype) for n in name]
            except TypeError:
                raise ValueError('name=%r should be a string or iterative '
                                 'of string' % name)


func = _GSLFuncLoader()
func._load('gsl_strerror', [c_int], c_char_p)
func._load('gsl_rng_alloc', [_c_gsl_rng_type_p], _c_gsl_rng_p)
func._load('gsl_rng_set', [_c_gsl_rng_p, c_ulong])
func._load('gsl_rng_free', [_c_gsl_rng_p])
func._load('gsl_rng_types_setup',
           restype=c_void_p)  # POINTER(_c_gsl_rng_p)
func._load(['gsl_ran_gaussian',
            'gsl_ran_gaussian_ziggurat',
            'gsl_ran_gaussian_ratio_method'],
           [_c_gsl_rng_p, c_double],
           c_double)


gsl_strerror = func.gsl_strerror


def _get_gsl_rng_type_p_dict():
    """
    Get all ``gsl_rng_type`` as dict which has pointer to each object

    This is equivalent to C code bellow which is from GSL document:

    .. sourcecode:: c

          const gsl_rng_type **t, **t0;
          t0 = gsl_rng_types_setup ();
          for (t = t0; *t != 0; t++)
            {
              printf ("%s\n", (*t)->name);  /* instead, store t to dict */
            }

    """
    t = func.gsl_rng_types_setup()
    dt = ctypes.sizeof(c_void_p)
    dct = {}
    while True:
        a = c_void_p.from_address(t)
        if a.value is None:
            break
        name = c_char_p.from_address(a.value).value
        dct[name] = ctypes.cast(a, _c_gsl_rng_type_p)
        t += dt
    return dct


class gsl_rng(object):
    _gsl_rng_alloc = func.gsl_rng_alloc
    _gsl_rng_set = func.gsl_rng_set
    _gsl_rng_free = func.gsl_rng_free
    _gsl_rng_type_p_dict = _get_gsl_rng_type_p_dict()
    _ctype_ = _c_gsl_rng_p  # for railgun

    def __init__(self, seed=None, name='mt19937'):
        self._gsl_rng_name = name
        self._gsl_rng_type_p = self._gsl_rng_type_p_dict[name]
        self._cdata_ = self._gsl_rng_alloc(self._gsl_rng_type_p)
        # the name '_cdata_' is for railgun
        if seed is not None:
            self.set(seed)

    def __del__(self):
        self._gsl_rng_free(self._cdata_)

    def set(self, seed):
        self._gsl_rng_set(self._cdata_, seed)

    _gsl_ran_gaussian = {
        '': func.gsl_ran_gaussian,
        'ziggurat': func.gsl_ran_gaussian_ziggurat,
        'ratio_method': func.gsl_ran_gaussian_ratio_method,
        }

    def ran_gaussian(self, sigma=1.0, method=''):
        return self._gsl_ran_gaussian[method](self._cdata_, sigma)
