import re
from ctypes import Structure, POINTER, pointer
from ctypes import (c_char, c_short, c_ushort, c_int, c_uint, c_long, c_ulong,
                    c_longlong, c_ulonglong, c_float, c_double, c_longdouble,
                    c_bool)
import platform
import numpy

from railgun.cfuncs import cfdec_parse, choice_combinations, CJOINSTR
from railgun.cdata import cddec_parse
from railgun._helper import dict_override, strset

"""
SimObject, its metaclass (MetaSimObject), and helper functions

Notations of "types" used here:

CDT: C Data Type
    String to indicate data type of C
    (e.g.: int, float, double, char)
DTYPE: numpy data type
    This is used as an argument of numpy functions such as
    `numpy.array`
CTYPE: ctypes data types
    Fundamental data types of `ctypes` such as
    `c_int`, `c_double`, `c_float`, `c_bool`.

"""

CDT2DTYPE = dict(char=numpy.character,
                 short=numpy.short, ushort=numpy.ushort,
                 int=numpy.int32, uint=numpy.uint32,
                 longlong=numpy.longlong, ulonglong=numpy.ulonglong,
                 float=numpy.float32, double=numpy.float,
                 longdouble=numpy.longdouble,  # == numpy.float96
                 ## cfloat=numpy.complex64, cdouble=numpy.complex,  # complex128
                 ## clongdouble=numpy.complex192,
                 bool=numpy.bool,
                 )
_architecture = platform.architecture()
if _architecture[0] == '32bit':
    CDT2DTYPE.update(long=numpy.int32, ulong=numpy.uint32)
elif _architecture[0] == '64bit':
    CDT2DTYPE.update(long=numpy.int64, ulong=numpy.uint64)
else:
    raise RuntimeError (
        'Architecture %s is not supported' % str(_architecture))
CDT2CTYPE = dict(char=c_char,
                 short=c_short, ushort=c_ushort,
                 int=c_int, uint=c_uint,
                 long=c_long, ulong=c_ulong,
                 longlong=c_longlong, ulonglong=c_ulonglong,
                 float=c_float, double=c_double,
                 longdouble=c_longdouble,
                 bool=c_bool,
                 )
DTYPE2CDT = dict((numpy.dtype(v), k) for (k, v) in CDT2DTYPE.iteritems())
DTYPE2CDT.update({
    numpy.dtype(numpy.int32): 'int',  # otherwise 'long' can override this val
    numpy.dtype('|S1'): 'char',
    })


def POINTER_nth(ct, n):
    if not isinstance(n, int):
        raise ValueError("only accept int for n")
    if n == 0:
        return ct
    else:
        return POINTER_nth(POINTER(ct), n-1)


def as_ndim_pointer(arr, basetype, ndim):
    if ndim == 1:
        return arr.ctypes.data_as(POINTER(basetype))
    else:
        ctp = POINTER_nth(basetype, ndim - 1)
        ctpa = ctp * len(arr)
        prow = [as_ndim_pointer(row, basetype, ndim - 1) for row in arr]
        return ctpa(*prow)


def ctype_getter(arr):
    basetype = CDT2CTYPE[DTYPE2CDT[arr.dtype]]
    return as_ndim_pointer(arr, basetype, arr.ndim)


def _gene_porp_scalar(key):
    def fget(self):
        return getattr(self._struct_, key)
    def fset(self, val):
        setattr(self._struct_, key, val)
    return property(fget, fset)


def _gene_porp_array(key):
    def fget(self):
        return self._cdata_[key]
    def fset(self, v):
        self._cdata_[key][:] = v
    return property(fget, fset)


def gene_cfpywrap(cfdec):
    """
    Generate python function given an object parsed by `cfdec_parse`
    """
    cfkeyorder = [a['aname'] for a in cfdec.args]
    choiceskeyorder = [c['key'] for c in cfdec.choset]
    keyorder = cfkeyorder + choiceskeyorder
    defaults_cargs = dict(
        (a['aname'], a['default']) for a in cfdec.args
        if a['default'] is not None)
    defaults_choices = dict(
        (c['key'], c['choices'][0]) for c in cfdec.choset)
    def cfpywrap(self, *args, **kwds):
        # check #arg
        if len(args) + len(kwds) > len(keyorder):
            raise ValueError ('%s() takes exactly %d arguments (%d given)'
                              % (cfdec.fname,
                                 1 + len(keyorder),
                                 1 + len(args) + len(kwds)))
        # check multiple values
        mval_args = set(keyorder[:len(args)]) & set(kwds)
        if mval_args:
            s = '{%s}' % ''.join(str(x) for x in mval_args)
            raise ValueError (
                '%s() got multiple values for variable in %s' %
                (cfdec.fname, s))
        # put `args` and `kwds` all together to `allkwds`
        allkwds = {}
        allkwds.update(zip(keyorder, args))
        allkwds.update(kwds)
        # set cfname
        choices_dict = defaults_choices.copy()
        choices_dict.update(allkwds)
        cfchoices = [choices_dict[k] for k in choiceskeyorder]
        cfname = cfdec.fnget(*cfchoices)
        # set c-function arguments
        cargs_dict = {}
        for (k, v) in defaults_cargs.iteritems():
            if hasattr(self, v):
                cargs_dict[k] = getattr(self, v)
            else:
                cargs_dict[k] = eval(v)
        cargs_dict.update(allkwds)
        cargs = [cargs_dict[k] for k in cfkeyorder]
        # check arguments validity
        self._check_index_in_range(
            [(a, cargs_dict[a['aname']]) for a in cfdec.args])
        # call c-function
        cfunc = self._cfunc_loaded_[cfname]
        rcode = cfunc(self._struct_p_, *cargs)
        if rcode == 0:
            if cfdec.ret:
                return getattr(self, cfdec.ret)
            else:
                return
        else:
            raise RuntimeError ('c-function %s() terminates with code %d'
                                % (cfname, rcode))
    cfpywrap.func_name = cfdec.fname
    return cfpywrap


def gene_array_alias(array_names, sep="_"):
    """
    Generate `array_alias` for parsing "array alias" such as "a_1_2"

    Usage:

    >>> iaa = gene_array_alias(['a', 'b', 'c'])
    >>> iaa('a_1_2')
    ('a', (1, 2))
    >>> iaa('a12')
    >>> iaa('b_1')
    ('b', (1,))
    >>> iaa('c')
    >>> iaa('c_2_3')
    ('c', (2, 3))
    >>> iaa = gene_array_alias(['a', 'b', 'c'], sep='^')
    >>> iaa('a_1')
    >>> iaa('a^1')
    ('a', (1,))
    """
    ptn = re.compile(r'(%s)((\%s[0-9]+)+)' % ('|'.join(array_names), sep))
    def array_alias(alias):
        ma = ptn.match(alias)
        if ma:
            (name, indexstr, dummy) = ma.groups() ## ('x', '_2_1_2', '_2')
            index = tuple([int(s) for s in indexstr.split(sep)[1:]])
            return (name, index)
    return array_alias


class MetaSimObject(type):

    def __new__(cls, clsname, bases, attrs):
        if not (set(['_clibname_', '_clibdir_',
                     '_cmembers_', '_cfuncs_']) <= set(attrs)):
            return type.__new__(cls, clsname, bases, attrs)
        cstructname = attrs.get('_cstructname_', clsname)
        cfuncprefix = attrs.get('_cfuncprefix_', cstructname + CJOINSTR)
        clibdir = attrs['_clibdir_']
        clibname = attrs['_clibname_']
        cmembers = attrs['_cmembers_']
        cfuncs = attrs['_cfuncs_']
        cfuncs_parsed_list = [cfdec_parse(cfstr) for cfstr in cfuncs]
        cfuncs_parsed = dict(
            (parsed.fname, parsed) for parsed in cfuncs_parsed_list)
        cmems_parsed_list = [cddec_parse(cdstr) for cdstr in cmembers]
        cmems_parsed = dict(
            (parsed.vname, parsed) for parsed in cmems_parsed_list)
        cmems_default_scalar = dict(
            (parsed.vname, parsed.default) for parsed in cmems_parsed_list
            if parsed.default and parsed.ndim == 0)
        cmems_default_array = dict(
            (parsed.vname, parsed.default) for parsed in cmems_parsed_list
            if parsed.default and parsed.ndim > 0)
        idxset = set([vname[4:]  # len('num_') = 4
                      for vname in cmems_parsed if vname.startswith('num_')])
        attrs['_cmems_parsed_'] = cmems_parsed
        attrs['_cmems_default_scalar_'] = cmems_default_scalar
        attrs['_cmems_default_array_'] = cmems_default_array
        attrs['_idxset_'] = idxset

        ## set _struct_type_{,p_}
        fields = [(parsed.vname,
                   POINTER_nth(CDT2CTYPE[parsed.cdt], parsed.ndim))
                  for parsed in cmems_parsed_list]
        # don't use `cmems_parsed.iteritems()` above or
        # order of c-members will be lost!
        class StructClass(Structure):
            _fields_ = fields
        StructClass.__name__ = cstructname + "Struct"
        struct_type_p = POINTER(StructClass)
        attrs.update(
            _struct_type_ = StructClass,
            _struct_type_p_ = struct_type_p,
            )
        array_names = [vname for (vname, parsed) in cmems_parsed.iteritems()
                       if parsed.ndim > 0]
        array_alias = gene_array_alias(array_names)
        attrs['array_alias'] = staticmethod(array_alias)

        ## set getter/setter
        get_gene_prop = (
            lambda ndim: (ndim > 0) and _gene_porp_array or _gene_porp_scalar)
        for (vname, parsed) in cmems_parsed.iteritems():
            gene_prop = get_gene_prop(parsed.ndim)
            attrs[vname] = gene_prop(vname)

        ## load c-functions
        cdll = numpy.ctypeslib.load_library(clibname, clibdir)
        cfunc_loaded = {}
        attrs['_cdll_'] = cdll
        attrs['_cfunc_loaded_'] = cfunc_loaded
        def get_arg_ct(ag):
            if ag['aname'] in idxset:
                return c_int
            elif ag['cdt'] in idxset:
                return c_int
            else:
                return CDT2CTYPE[ag['cdt']]
        for (fname, parsed) in cfuncs_parsed.iteritems():
            for args in choice_combinations(parsed):
                cfname = parsed.fnget(*args)
                cf = cdll[cfuncprefix + cfname]
                cf.restype = c_int
                cf.argtypes = (
                    [struct_type_p] + map(get_arg_ct, parsed['args']))
                cfunc_loaded[cfname] = cf
            attrs[fname] = gene_cfpywrap(parsed)

        return type.__new__(cls, clsname, bases, attrs)


class SimObject(object):
    __metaclass__ = MetaSimObject

    def __init__(self, **kwds):
        self._set_all(**kwds)

    def _set_all(self, **kwds):
        # searching invalid keyword arguments
        non_cmem_keys = set(kwds) - set(self._cmems_parsed_)
        cmem_keys = set(kwds) - non_cmem_keys
        cmem_keys_scalar = set(
            [k for k in cmem_keys if self._cmems_parsed_[k].ndim == 0])
        cmem_keys_array = set(
            [k for k in cmem_keys if self._cmems_parsed_[k].ndim > 0])
        undefined_keywords = set()
        for key in non_cmem_keys:
            if not self.array_alias(key):
                undefined_keywords.add(key)
        if undefined_keywords:
            raise ValueError (
                "undefined keyword arguments: %s" % strset(undefined_keywords))
        kwds_cmem_scalar = dict([(k, kwds[k]) for k in cmem_keys_scalar])
        kwds_cmem_array = dict([(k, kwds[k]) for k in cmem_keys_array])
        kwds_non_cmem = dict([(k, kwds[k]) for k in non_cmem_keys])
        # allocate struct
        self._struct_ = self._struct_type_()
        self._struct_p_ = pointer(self._struct_)
        # set scalar variables including num_*
        scalarvals = dict_override(
            self._cmems_default_scalar_, kwds_cmem_scalar, addkeys=True)
        numkeyset = set('num_%s' % i for i in self._idxset_)
        num_lack = numkeyset - set(scalarvals)
        if num_lack:
            raise ValueError ("%s are mandatory" % strset(num_lack))
        self.setv(**scalarvals)
        # allocate C array data and set the defaults
        self._set_cdata()
        self.setv(**dict_override(
            self._cmems_default_array_, kwds_cmem_array, addkeys=True))
        self.setv(**kwds_non_cmem)

    def setv(self, **kwds):
        """
        Set variable named 'VAR' by ``set(VAR=VALUE)``

        Alias for array ('ARR_0_1' for ``self.ARR[0,1]``) is available.
        """
        for (key, val)in kwds.iteritems():
            alias = self.array_alias(key)
            if alias:
                (name, index) = alias
                self._cdata_[name][index] = val
            else:
                setattr(self, key, val)

    def getv(self, *args):
        """
        Get members obj.MEM by obj.getv('MEM')

        These two lines are equivalent::

            a = obj.a
            a = obj.getv('a')

        You can specify multiple members::

            (a, b, c) = (obj.a, obj.b, obj.c)
            (a, b, c) = obj.getv('a', 'b', 'c')
            (a, b, c) = obj.getv('a, b, c')

        """
        if len(args) == 1:
            args = [a.strip() for a in args[0].split(',')]
        mems = [getattr(self, a) for a in args]
        if len(mems) == 1:
            return mems[0]
        else:
            return mems

    def num(self, *args):
        """Get size of array (num_'i') along given index ('i') """
        if len(args) == 1:
            args = [a.strip() for a in args[0].split(',')]
        if set(args) > self.indexset:
            istr = strset(set(args) - self.indexset)
            raise ValueError ("index(es) %s doesn't exist" % istr)
        nums = [getattr(self, 'num_%s'%i) for i in args]
        if len(nums) == 1:
            return nums[0]
        else:
            return nums

    def _set_cdata(self):
        self._cdata_ = {} # keep memory for arrays
        for (vname, parsed) in self._cmems_parsed_.iteritems():
            if parsed.ndim > 0:
                shape = tuple(getattr(self, 'num_%s' % i) for i in parsed.idx)
                dtype = CDT2DTYPE[parsed.cdt]
                arr = numpy.zeros(shape, dtype=dtype)
                self._cdata_[vname] = arr
                self._struct_.__setattr__(vname, ctype_getter(arr))
                ## setattr(self._struct_, vname, ctype_getter(arr))

    def _get_indexset(self):
        """Get set of index as a `set` of string"""
        return self._idxset_
    indexset = property(_get_indexset)

    def _check_index_in_range(self, arg_val_list):
        """
        Raise ValueError if index 'i' is bigger than 0 and less than num_'i'

        An argument `aname_cdt_val_list` is list of (`arg`, `value`)-pair.

        """
        for (ag, val) in arg_val_list:
            cdt = ag['cdt']
            aname = ag['aname']
            ixt = ag['ixt']
            if cdt in self.indexset:
                idx = cdt
                if ixt == '<':
                    lower_name = '1'
                    lower_val = 1
                    upper_name = 'num_%s+1' % idx
                    upper_val = self.num(idx) + 1
                else:
                    lower_name = '0'
                    lower_val = 0
                    upper_name = 'num_%s' % idx
                    upper_val = self.num(idx)
                if val < lower_val:
                    raise ValueError (
                        'index %s cannot bet less than %s '
                        'where value is %s=%d'
                        % (idx, lower_name, aname, val))
                elif val >= upper_val:
                    raise ValueError (
                        'index %s cannot bet larger than or equal to '
                        '%s=%d where value is %s=%d'
                        % (idx, upper_name, upper_val, aname, val))
