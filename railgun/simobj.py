import re
from ctypes import Structure, POINTER, pointer, cast
from ctypes import (c_char, c_short, c_ushort, c_int, c_uint, c_long, c_ulong,
                    c_longlong, c_ulonglong, c_float, c_double, c_longdouble,
                    c_bool, c_size_t)
import platform
import numpy

from railgun.cfuncs import cfdec_parse, choice_combinations, CJOINSTR
from railgun.cdata import cddec_parse
from railgun.cmemsubsets import CMemSubSets
from railgun._helper import (
    dict_override, strset, subdict_by_prefix, subdict_by_filter)
try:
    from railgun import cstyle
except ImportError:
    pass

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
VALTYPE : Value Type
    {'scalar', 'array', 'object'}

"""

CDT2DTYPE = dict(char=numpy.character,
                 short=numpy.short, ushort=numpy.ushort,
                 int=numpy.int32, uint=numpy.uint32,
                 longlong=numpy.longlong, ulonglong=numpy.ulonglong,
                 float=numpy.float32, double=numpy.float,
                 longdouble=numpy.longdouble,  # == numpy.float96
                 ## cfloat=numpy.complex64,
                 ## cdouble=numpy.complex,  # complex128
                 ## clongdouble=numpy.complex192,
                 bool=numpy.bool,
                 )
_architecture = platform.architecture()
if _architecture[0] == '32bit':
    CDT2DTYPE.update(long=numpy.int32, ulong=numpy.uint32)
elif _architecture[0] == '64bit':
    CDT2DTYPE.update(long=numpy.int64, ulong=numpy.uint64)
else:
    raise RuntimeError(
        'Architecture %s is not supported' % str(_architecture))
CDT2DTYPE['size_t'] = CDT2DTYPE['ulong']
CDT2CTYPE = dict(char=c_char,
                 short=c_short, ushort=c_ushort,
                 int=c_int, uint=c_uint,
                 long=c_long, ulong=c_ulong,
                 longlong=c_longlong, ulonglong=c_ulonglong,
                 float=c_float, double=c_double,
                 longdouble=c_longdouble,
                 bool=c_bool, size_t=c_size_t,
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
        return POINTER_nth(POINTER(ct), n - 1)


def as_ndim_pointer(arr, base_POINTER, ctpa, ctpas_remain):
    if ctpas_remain:
        next_ctpa = ctpas_remain[0]
        next_ctpas_remain = ctpas_remain[1:]
        prow = [as_ndim_pointer(row, base_POINTER, next_ctpa,
                                next_ctpas_remain) for row in arr]
        return ctpa(*prow)
    else:
        prow = [row.ctypes.data_as(base_POINTER) for row in arr]
        return ctpa(*prow)


def ctype_getter(arr):
    basetype = CDT2CTYPE[DTYPE2CDT[arr.dtype]]
    base_POINTER = POINTER(basetype)
    if arr.ndim == 1:
        return arr.ctypes.data_as(base_POINTER)
    # make list of pointer type such as: int*, int**, int***, ...
    _P = basetype
    POINTER_list = []
    for dummy in range(arr.ndim - 1):
        _P = POINTER(_P)
        POINTER_list.append(_P)
    # callable to allocate N-dim "rows"
    ctpa_list = []
    for (i, num) in enumerate(arr.shape[:-1]):
        ctpa_list.append(POINTER_list[- 1 - i] * num)
    return as_ndim_pointer(arr, base_POINTER,
                           ctpa_list[0], tuple(ctpa_list[1:]))


def _gene_prop_scalar(key):

    def fget(self):
        return getattr(self._struct_, key)

    def fset(self, val):
        setattr(self._struct_, key, val)
    return property(fget, fset)


def _gene_prop_array(key):

    def fget(self):
        return self._cdatastore_[key]

    def fset(self, v):
        self._cdatastore_[key][:] = v
    return property(fget, fset)


def _gene_prop_object(key):

    def fget(self):
        return self._cdatastore_[key]

    def fset(self, v):
        if not isinstance(v, self._cmems_parsed_[key].cdt):
            raise ValueError('given value is not instance of %r' %
                             self._cmems_parsed_[key].cdt)
        self._cdatastore_[key] = v
        setattr(self._struct_, key, v._cdata_)
    return property(fget, fset)


def check_num_args_kwds(args, kwds, keyorder, func_name, plus=0):
    """
    Raise ValueError if number of arguments is too much

    >>> check_num_args_kwds(range(3), range(3), range(6), 'FUNC_NAME')
    >>> check_num_args_kwds(range(4), range(3), range(6), 'FUNC_NAME')
    Traceback (most recent call last):
        ...
    ValueError: FUNC_NAME() takes exactly 6 arguments (7 given)
    >>> check_num_args_kwds(range(4), range(3), range(6), 'FUNC_NAME', 1)
    Traceback (most recent call last):
        ...
    ValueError: FUNC_NAME() takes exactly 7 arguments (8 given)

    """
    if len(args) + len(kwds) > len(keyorder):
        raise ValueError(
            '%s() takes exactly %d arguments (%d given)'
            % (func_name, plus + len(keyorder), plus + len(args) + len(kwds)))


def check_multiple_values(args, kwds, keyorder, func_name):
    """
    Raise ValueError if arguments in args and kwds specifies same variables

    >>> check_multiple_values([1, 2], dict(c=1, d=2), ['a', 'b'], 'FUNC_NAME')
    >>> check_multiple_values([1, 2], dict(a=1, d=2), ['a', 'b'], 'FUNC_NAME')
    Traceback (most recent call last):
        ...
    ValueError: FUNC_NAME() got multiple values for variable in {a}
    >>> check_multiple_values([1, 2], dict(a=1, b=2), ['a', 'b'], 'FUNC_NAME')
    Traceback (most recent call last):
        ...
    ValueError: FUNC_NAME() got multiple values for variable in {a, b}

    """
    mval_args = set(keyorder[:len(args)]) & set(kwds)
    if mval_args:
        raise ValueError(
            '%s() got multiple values for variable in %s' %
            (func_name, strset(mval_args)))


def get_cfunc_choices(defaults, kwds, keyorder):
    """
    Get list of value in `kwds` or in `defaults` ordered by `keyorder`

    >>> get_cfunc_choices(dict(a=11, b=22), dict(a=1, b=2, c=3), ['b', 'c'])
    [2, 3]
    >>> get_cfunc_choices(dict(a=11, b=22), dict(c=4), ['b', 'c'])
    [22, 4]

    """
    subdict = defaults.copy()
    subdict.update(kwds)
    return [subdict[k] for k in keyorder]


def get_cargs(self, defaults, kwds, keyorder):
    """
    Get values in `kwds` or in `defaults` ordered by `keyorder`

    Value of `defaults` can be name of member of `self`

    >>> from railgun._helper import HybridObj
    >>> obj = HybridObj(a=111, b=222, c=333)
    >>> defaults = dict(A='a', B='b', C='1', D='2.0')
    >>> get_cargs(obj, defaults, {}, 'ABCD')
    [111, 222, 1, 2.0]
    >>> get_cargs(obj, defaults, dict(A=1, B=2), 'ABCD')
    [1, 2, 1, 2.0]

    """
    cargs_dict = {}
    for (k, v) in defaults.iteritems():
        if hasattr(self, v):
            cargs_dict[k] = getattr(self, v)
        else:
            cargs_dict[k] = eval(v)
    cargs_dict.update(kwds)
    return [cargs_dict[k] for k in keyorder]


def gene_cfpywrap(attrs, cfdec):
    """
    Generate python function given an object parsed by `cfuncs.cfdec_parse`
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
        check_num_args_kwds(args, kwds, keyorder, cfdec.fname, 1)  # check #arg
        check_multiple_values(args, kwds, keyorder, cfdec.fname)
        # put `args` and `kwds` all together to `allkwds`
        allkwds = {}
        allkwds.update(zip(keyorder, args))
        allkwds.update(kwds)
        # get cfunc
        cfname = cfdec.fnget(
            *get_cfunc_choices(defaults_choices, allkwds, choiceskeyorder))
        if not self._cmemsubsets_parsed_.cfunc_is_callable(cfname):
            raise ValueError(
                'C function "%s" cannot be executed. Check flags %s.' %
                (cfname, self._cmemsubsets_parsed_.getall()))
        cfunc = self._cfunc_loaded_[cfname]
        # get c-function arguments
        cargs = get_cargs(self, defaults_cargs, allkwds, cfkeyorder)
        # check arguments validity
        self._check_index_in_range(zip(cfdec.args, cargs))
        # call c-function
        rcode = cfunc(self._struct_p_, *cargs)
        if rcode == 0:
            if cfdec.ret:
                return getattr(self, cfdec.ret)
            else:
                return
        else:
            raise RuntimeError('c-function %s() terminates with code %d'
                               % (cfname, rcode))
    cfpywrap.func_name = cfdec.fname
    # wrap it if there is wrap function
    wrap_name = '_cwrap_%s' % cfdec.fname
    if wrap_name in attrs:
        cfpywrap = attrs[wrap_name](cfpywrap)
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
            (name, indexstr, dummy) = ma.groups()  # ('x', '_2_1_2', '_2')
            index = tuple([int(s) for s in indexstr.split(sep)[1:]])
            return (name, index)
    return array_alias


def latest_attr(iter_of_obj, name, default=None):
    """
    Get a attribute of given name found in latter object in given iterative

    >>> iter_of_dict = [{'a': 1}, {'c': 2}, {'a': 3}, {'c': 4}, {}]
    >>> from railgun._helper import HybridObj
    >>> iter_of_obj = map(HybridObj, iter_of_dict)
    >>> latest_attr(iter_of_obj, 'a')
    3
    >>> latest_attr(iter_of_obj, 'b')
    >>> latest_attr(iter_of_obj, 'b', 'Not Found')
    'Not Found'
    >>> latest_attr(iter_of_obj, 'c')
    4

    """
    for obj in iter_of_obj[::-1]:
        if hasattr(obj, name):
            return getattr(obj, name)
    return default


def attr_from_attrs_or_bases(bases, attrs, name, default=None):
    """
    Get an attribute from `attrs` or from `bases` if not found in `attrs`
    """
    latest = latest_attr(bases, name, default)
    return attrs.get(name, latest)


def parse_cfuncs(cfuncs):
    """Parse `_cfuncs_` using `cfuncs.cfdec_parse`"""
    cfuncs_parsed_list = [cfdec_parse(cfstr) for cfstr in cfuncs]
    cfuncs_parsed = dict(
        (parsed.fname, parsed) for parsed in cfuncs_parsed_list)
    return cfuncs_parsed


def parse_cmembers(cmembers):
    """Parse `_cmembers_` using `cdata.cddec_parse`"""
    cmems_parsed_list = [cddec_parse(cdstr) for cdstr in cmembers]
    cmems_parsed = dict(
        (parsed.vname, parsed) for parsed in cmems_parsed_list)
    idxset = set([vname[4:]  # len('num_') = 4
                  for vname in cmems_parsed if vname.startswith('num_')])
    return (cmems_parsed, cmems_parsed_list, idxset)


def default_of_cmembers(cmems_parsed_list):
    """Get `cmems_default_{scalar, array}` from `cmems_parsed_list`"""
    cmems_default_scalar = dict(
        (parsed.vname, parsed.default) for parsed in cmems_parsed_list
        if parsed.has_default and parsed.valtype == 'scalar')
    cmems_default_array = dict(
        (parsed.vname, parsed.default) for parsed in cmems_parsed_list
        if parsed.has_default and parsed.valtype == 'array')
    return (cmems_default_scalar, cmems_default_array)


def get_struct_class(cmems_parsed_list, cstructname):
    fields = []
    for parsed in cmems_parsed_list:
        # don't use `cmems_parsed.iteritems()` above or
        # order of c-members will be lost!
        if parsed.valtype == 'object':
            fields.append((parsed.vname, parsed.cdt._ctype_))
        else:
            ctype = POINTER_nth(CDT2CTYPE[parsed.cdt], parsed.ndim)
            fields.append((parsed.vname, ctype))

    class StructClass(Structure):
        _fields_ = fields
    StructClass.__name__ = cstructname + "Struct"
    return StructClass


def array_alias_from_cmems_parsed(cmems_parsed):
    array_names = [vname for (vname, parsed) in cmems_parsed.iteritems()
                   if parsed.valtype == 'array']
    array_alias = gene_array_alias(array_names)
    return staticmethod(array_alias)


def load_cfunc(cdll, cfuncs_parsed, struct_type_p, cfuncprefix, idxset):
    cfunc_loaded = {}

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
    return cfunc_loaded


class MetaSimObject(type):
    """
    Meta-class for `SimObject`

    Given Attributes
    ----------------
    _clibname_ : str
        Name of your C shared library
    _clibdir_ : str
        Path of the C library directory
    _cmembers_ : list of str
        List of definition of C member
    _cfuncs_ : list of str
        List of definition of C function to be loaded
    _cstructname_ : str, optional
        Name of C struct (default is class name)
    _cfuncprefix_ : str, optional
        Prefix of C functions (default is ``_cstructname_ + '_'``)
    _cwrap_{CFUNC_NAME} : function, optional
        Wrapper for loaded C function `CFUNC_NAME`
    _cmemsubsets_ : dict of dict of list, optional
        Definition of subset of C members for controlling which
        C members to be loaded. Example::

            { 'name1': { 'cfuncs': ['f', 'g', 'h'], 'cmems': ['x', 'y'] },
              'name2': { 'cfuncs': ['f', 'j', 'k'], 'cmems': ['y', 'z'] } }

        Here, ``name1, name2`` are the name of C member subset,
        ``f, g, h, j, k`` are the name of C functions, and
        ``x, y, z`` are the name of C members.


    Attributes to be set
    --------------------
    _cmems_parsed_ : dict
        Key: name of C member; Value: object parsed by `cdata.cddec_parse`
    _cmems_default_scalar_ : dict
        Key: name of C member (scalar); Value: default value
    _cmems_default_array_ : dict
        Key: name of C member (array); Value: default value
    _idxset_ : set
        set of index
    array_alias : function
        Parser for "array alias" such as "a_1_2"
    _struct_type_ : ctypes obejct
        Subclass of `ctypes.Structure` generated from `_cmembers_`
    _struct_type_p_ : ctypes obejct
        Pointer type of _struct_type_
    _cdll_ : ctypes object
        Loaded C library
    _cfunc_loaded_ : dict
        Loaded C functions.
        Key: Name of C function (without `_cfuncprefix_`);
        Value: ctypes object
    _cmemsubsets_parsed_ : CMemSubSets
        An instance of CMemSubSets generated from `_cmemsubsets_`

    Additionally, C member and C function will be added as attributes.

    """

    def __new__(cls, clsname, bases, attrs):
        clibdir = attr_from_attrs_or_bases(bases, attrs, '_clibdir_')
        clibname = attr_from_attrs_or_bases(bases, attrs, '_clibname_')
        cmembers = attr_from_attrs_or_bases(bases, attrs, '_cmembers_')
        cfuncs = attr_from_attrs_or_bases(bases, attrs, '_cfuncs_')
        if any(c is None for c in [clibdir, clibname, cmembers, cfuncs]):
            return type.__new__(cls, clsname, bases, attrs)
        cstructname = attr_from_attrs_or_bases(
            bases, attrs, '_cstructname_', clsname)
        cfuncprefix = attr_from_attrs_or_bases(
            bases, attrs, '_cfuncprefix_', cstructname + CJOINSTR)
        cmemsubsets = attr_from_attrs_or_bases(bases, attrs, '_cmemsubsets_')

        ## parse _cfuncs_
        cfuncs_parsed = parse_cfuncs(cfuncs)
        ## parse _cmembers_
        (cmems_parsed, cmems_parsed_list, idxset) = parse_cmembers(cmembers)
        (cmems_default_scalar,
         cmems_default_array) = default_of_cmembers(cmems_parsed_list)

        attrs.update(
            _cmems_parsed_=cmems_parsed,
            _cmems_default_scalar_=cmems_default_scalar,
            _cmems_default_array_=cmems_default_array,
            _idxset_=idxset,
            array_alias=array_alias_from_cmems_parsed(cmems_parsed),
            )

        ## set _struct_type_ and _struct_type_p_
        StructClass = get_struct_class(cmems_parsed_list, cstructname)
        struct_type_p = POINTER(StructClass)
        attrs.update(_struct_type_=StructClass, _struct_type_p_=struct_type_p)

        ## set getter/setter
        for (vname, parsed) in cmems_parsed.iteritems():
            if parsed.valtype == 'array':
                attrs[vname] = _gene_prop_array(vname)
            elif parsed.valtype == 'scalar':
                attrs[vname] = _gene_prop_scalar(vname)
            elif parsed.valtype == 'object':
                attrs[vname] = _gene_prop_object(vname)
            else:
                ValueError('valtype "%s" is not recognized' % parsed.valtype)

        ## load c-functions
        cdll = numpy.ctypeslib.load_library(clibname, clibdir)
        cfunc_loaded = load_cfunc(cdll, cfuncs_parsed, struct_type_p,
                                  cfuncprefix, idxset)
        attrs.update(
            _cdll_=cdll,
            _cfunc_loaded_=cfunc_loaded,
            _cmemsubsets_parsed_=CMemSubSets(
                cmemsubsets, set(cfunc_loaded), set(cmems_parsed)),
            )
        for (fname, parsed) in cfuncs_parsed.iteritems():
            attrs[fname] = gene_cfpywrap(attrs, parsed)

        return type.__new__(cls, clsname, bases, attrs)


class SimObject(object):
    __metaclass__ = MetaSimObject
    _calloc_ = True  # if True, use cstyle.CStyle to allocate memory

    def __init__(self, **kwds):
        """
        Allocate C members to construct `SimObject`

        Parameters
        ----------
        _calloc_ : bool, optional
            If True, use cstyle.CStyle to allocate memory (default: True).
        _cmemsubsets_{FLAG_NAME} : bool, optional
            Set flag of `FLAG_NAME` which is defined by `_cmemsubsets_`
            attribute.

        Other keyword arguments will be name of C member or
        "array alias" of array C member.

        """
        if '_calloc_' in kwds:
            self._calloc_ = kwds['_calloc_']
            del kwds['_calloc_']

        # copy is needed otherwise self._cmemsubsets_parsed_ is shared by
        # all instance of SimObject
        self._cmemsubsets_parsed_ = self._cmemsubsets_parsed_.copy()
        cmemsubsets_kwds = subdict_by_prefix(kwds, '_cmemsubsets_',
                                             remove_original=True)
        self._cmemsubsets_parsed_.set(**cmemsubsets_kwds)

        self._set_all(**kwds)

    def _is_cmem_scalar(self, name):
        return (name in self._cmems_parsed_ and
                self._cmems_parsed_[name].valtype == 'scalar')

    def _is_cmem_array(self, name):
        return (name in self._cmems_parsed_ and
                self._cmems_parsed_[name].valtype == 'array')

    def _is_cmem_object(self, name):
        return (name in self._cmems_parsed_ and
                self._cmems_parsed_[name].valtype == 'object')

    def _set_all(self, **kwds):
        # decompose keyword arguments into its disjoint subsets
        kwds_scalar = subdict_by_filter(kwds, self._is_cmem_scalar, True)
        kwds_array = subdict_by_filter(kwds, self._is_cmem_array, True)
        kwds_array_alias = subdict_by_filter(kwds, self.array_alias, True)
        kwds_object = subdict_by_filter(kwds, self._is_cmem_object, True)
        if kwds:  # there should not be remaining arguments
            raise ValueError(
                "undefined keyword arguments: %s" % kwds)
        # allocate struct
        self._struct_ = self._struct_type_()
        self._struct_p_ = pointer(self._struct_)
        # set scalar variables including num_*
        scalarvals = dict_override(
            self._cmems_default_scalar_, kwds_scalar, addkeys=True)
        numkeyset = set('num_%s' % i for i in self._idxset_)
        num_lack = numkeyset - set(scalarvals)
        if num_lack:
            raise ValueError("%s are mandatory" % strset(num_lack))
        self.setv(**scalarvals)
        # allocate C array data and set the defaults
        self._set_cdata()
        cmems_default_array = self._cmems_default_array_
        array_allocated = filter(  # remove if not allocated
            self._cmemsubsets_parsed_.cmem_need_alloc, cmems_default_array)
        cmems_default_array_allocated = dict((k, cmems_default_array[k])
                                             for k in array_allocated)
        self.setv(**dict_override(
            cmems_default_array_allocated, kwds_array, addkeys=True))
        self.setv(**kwds_array_alias)
        self.setv(**kwds_object)

    def setv(self, **kwds):
        """
        Set variable named 'VAR' by ``set(VAR=VALUE)``

        Alias for element of array ('ARR_0_1' for ``self.ARR[0,1]``)
        is available.

        """
        for (key, val)in kwds.iteritems():
            alias = self.array_alias(key)
            if alias:
                (name, index) = alias
                self._cdatastore_[name][index] = val
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
        """
        Get shape of array (Ni, Nj, ...) along given index ('i', 'j', ...)
        """
        if len(args) == 1:
            args = [a.strip() for a in args[0].split(',')]
        if set(args) > self._idxset_:
            istr = strset(set(args) - self._idxset_)
            raise ValueError("index(es) %s doesn't exist" % istr)
        nums = [getattr(self, 'num_%s' % i) for i in args]
        if len(nums) == 1:
            return nums[0]
        else:
            return nums

    def _set_cdata(self):
        self._cdatastore_ = {}  # keep memory for arrays
        cmem_need_alloc = self._cmemsubsets_parsed_.cmem_need_alloc
        for (vname, parsed) in self._cmems_parsed_.iteritems():
            if parsed.valtype == 'array' and cmem_need_alloc(vname):
                shape = tuple(
                    int(i) if i.isdigit() else getattr(self, 'num_%s' % i)
                    for i in parsed.idx)
                dtype = CDT2DTYPE[parsed.cdt]
                arr = numpy.zeros(shape, dtype=dtype)
                self._cdatastore_[vname] = arr
                if self._calloc_ and 1 < arr.ndim <= cstyle.MAXDIM:
                    cs = cstyle.CStyle(arr)
                    self._cdatastore_['CStyle:%s' % vname] = cs
                    ptr = cast(
                        cs.pointer,
                        POINTER_nth(CDT2CTYPE[parsed.cdt], parsed.ndim))
                else:
                    ptr = ctype_getter(arr)
                setattr(self._struct_, vname, ptr)

    def _check_index_in_range(self, arg_val_list):
        """
        Raise ValueError if index 'i' is bigger than 0 and less than num_'i'

        An argument `aname_cdt_val_list` is list of (`arg`, `value`)-pair.

        """
        for (ag, val) in arg_val_list:
            cdt = ag['cdt']
            aname = ag['aname']
            ixt = ag['ixt']
            if cdt in self._idxset_:
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
                    raise ValueError(
                        'index %s cannot be less than %s where value is %s=%d'
                        % (idx, lower_name, aname, val))
                elif val >= upper_val:
                    raise ValueError(
                        'index %s cannot be larger than or equal to '
                        '%s=%d where value is %s=%d'
                        % (idx, upper_name, upper_val, aname, val))
