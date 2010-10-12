import re
from ctypes import (Structure, POINTER, pointer, c_int, c_double)
import numpy

from railgun.cfuncs import cfdec_parse, choice_combinations, CJOINSTR
from railgun.cdata import cddec_parse

"""
SimObject, its metaclass (MetaSimObject), and helper functions

Notations of "types" used here:

CDT: C Data Type
    String to indicate data type of C
    (e.g.: int, float, double, char)
DT/dtype: numpy data type
    This is used as an argument of numpy functions such as
    `numpy.array`
CT/ctype: ctypes data types
    Fundamental data types of `ctypes` such as
    `c_int`, `c_double`, `c_float`, `c_bool`.
PT: python type
    Python type object such as `float` or `int`

"""

CDT2DTYPE = dict(int=numpy.int32, double=numpy.float)
CDT2CTYPE = dict(int=c_int, double=c_double)


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
    if arr.dtype == numpy.int32:
        basetype = c_int
    elif arr.dtype == numpy.float:
        basetype = c_double
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


class BaseSimObject(object):

    def __init__(self, **kwds):
        self._set_all(**kwds)

    def _set_all(self, **kwds):
        self._struct_ = self._struct_type_()
        self._struct_p_ = pointer(self._struct_)
        self.setv(**self._cmems_default_scalar_)
        self.setv(**kwds)
        self._set_cdata()
        self.setv(**self._cmems_default_array_)

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

    def num(self, *args):
        """Get size of array (num_'i') along given index ('i') """
        if set(args) > self.indexset:
            istr = ', '.join(set(args) - self.indexset)
            raise ValueError ("index(es) {%s} doesn't exist" % istr)
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


class MetaSimObject(type):

    def __new__(cls, name, bases, attrs):
        if not (set(['_clibname_', '_clibdir_',
                     '_cmembers_', '_cfuncs_']) <= set(attrs)):
            # DO NOT add BaseSimObject to bases here
            # You will get::
            #   TypeError: Error when calling the metaclass bases
            #      Cannot create a consistent method resolution
            #   order (MRO) for bases SimObject, BaseSimObject
            return type.__new__(cls, name, bases, attrs)
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
        StructClass.__name__ = name + "Struct"
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
                cf = cdll[CJOINSTR.join([name, cfname])]
                cf.restype = c_int
                cf.argtypes = (
                    [struct_type_p] + map(get_arg_ct, parsed['args']))
                cfunc_loaded[cfname] = cf
            attrs[fname] = gene_cfpywrap(parsed)

        return type.__new__(cls, name, (BaseSimObject,) + bases, attrs)


class SimObject(object):
    __metaclass__ = MetaSimObject
