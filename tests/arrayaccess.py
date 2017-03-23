from __future__ import print_function

import numpy
from numpy.testing import assert_equal, assert_almost_equal
from nose.tools import raises

from tsutils import eq_
from railgun import SimObject, relpath

LIST_IDX = list('ijklmnopqrstuvwxyz')


def get_str_get_array(cdt, dim):
    """
    Get c-function declaration 'get_{int,double,...}{1,2,..}d(i, j, ...)'

    >>> get_str_get_array('int', 1)
    'get_int1d(i)'
    >>> get_str_get_array('int', 2)
    'get_int2d(i, j)'
    >>> get_str_get_array('double', 1)
    'get_double1d(i)'
    >>> get_str_get_array('double', 2)
    'get_double2d(i, j)'

    """
    args = ', '.join(LIST_IDX[:dim])
    return 'get_%s%dd(%s)' % (cdt, dim, args)


def get_str_cddec(cdt, dim, carrtype=None):
    """
    Get c-data declaration '{int,double,...} {int,double,...}{1,2,..}[i][j]...'

    >>> get_str_cddec('int', 1)
    'int int1d[i]'
    >>> get_str_cddec('int', 2)
    'int int2d[i][j]'
    >>> get_str_cddec('int', 2, 'flat')
    'int int2d[i,j]'
    >>> get_str_cddec('double', 1)
    'double double1d[i]'
    >>> get_str_cddec('double', 2)
    'double double2d[i][j]'

    """
    if carrtype == "flat":
        args = ','.join(LIST_IDX[:dim])
    else:
        args = ']['.join(LIST_IDX[:dim])
    return '%s %s%dd[%s]' % (cdt, cdt, dim, args)


def gene_nums(nd):
    """
    Get list of num_* given maximum dimension

    >>> gene_nums(1)
    ['num_i']
    >>> gene_nums(4)
    ['num_i', 'num_j', 'num_k', 'num_l']

    """
    return ['num_%s' % data for data in LIST_IDX[:nd]]


def gene_cmembers(nd, list_cdt, carrtype=None):
    """
    Get cmembers given maximum dimension and list of CDT (c data type)

    >>> gene_cmembers(2, ['int', 'double'])  #doctest: +NORMALIZE_WHITESPACE
    ['num_i', 'num_j', 'int ret_int', 'double ret_double',
     'int int1d[i]', 'int int2d[i][j]',
     'double double1d[i]', 'double double2d[i][j]']
    >>> gene_cmembers(2, ['int', 'double'], 'flat')  #doctest: +NORMALIZE_WHITESPACE
    ['num_i', 'num_j', 'int ret_int', 'double ret_double',
     'int int1d[i]', 'int int2d[i,j]',
     'double double1d[i]', 'double double2d[i,j]']

    """
    return (
        gene_nums(nd) +
        ['%(cdt)s ret_%(cdt)s' % dict(cdt=cdt) for cdt in list_cdt] +
        [get_str_cddec(cdt, dim, carrtype)
         for cdt in list_cdt for dim in range(1, 1 + nd)]
        )


def gene_cfuncs(nd, list_cdt):
    return [get_str_get_array(cdt, dim)
            for cdt in list_cdt for dim in range(1, 1 + nd)]


@numpy.vectorize
def mchr(i):
    return chr(i % 256)


def alpharange(*args):
    return mchr(numpy.arange(*args))


def gene_class_ArrayAccess(clibname, nd, _list_cdt, carrtype=None):
    class ArrayAccess(SimObject):
        _clibname_ = clibname
        _clibdir_ = relpath('ext/build', __file__)
        _cmembers_ = gene_cmembers(nd, _list_cdt, carrtype)
        _cfuncs_ = gene_cfuncs(nd, _list_cdt)
        num_names = gene_nums(nd)
        ndim = nd
        list_cdt = _list_cdt

        def arr(self, cdt, dim):
            """Get array member '{cdt}{dim}d' (e.g., 'int2d')"""
            return getattr(self, '%s%dd' % (cdt, dim))

        def arr_via_ret(self, cdt, dim):
            """Get copy of array using 'get_{cdt}{dim}d' c-function"""
            get = getattr(self, 'get_%s%dd' % (cdt, dim))
            arr = self.arr(cdt, dim)
            garr = numpy.zeros_like(arr)
            for idx in numpy.ndindex(*arr.shape):
                get(*idx)  # call get_* c-func. which store val. in ret_{cdt}
                garr[idx] = getattr(self, 'ret_%s' % cdt)
            return garr

        def fill(self):
            """Fill array members using arange"""
            for cdt in self.list_cdt:
                if cdt == 'char':
                    arange = alpharange
                elif cdt == 'bool':
                    arange = lambda n: numpy.arange(n) % 2
                else:
                    arange = numpy.arange
                for dim in range(1, 1 + self.ndim):
                    arr = self.arr(cdt, dim)
                    arr.flat = arange(arr.size)
    return ArrayAccess


def check_arrayaccess(clibname, list_num, list_cdt, cdt, dim,
                      _calloc_=None, carrtype=None):
    """Check C side array access"""
    if cdt in ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
               'longlong', 'ulonglong', 'bool', 'size_t']:
        ass_eq = assert_equal
    elif cdt in ['float', 'double', 'longdouble']:
        ass_eq = assert_almost_equal

    ArrayAccess = gene_class_ArrayAccess(
        clibname, len(list_num), list_cdt, carrtype)
    num_dict = dict(zip(ArrayAccess.num_names, list_num))  # {num_i: 6, ...}
    if _calloc_ is not None:
        num_dict.update(_calloc_=_calloc_)
    aa = ArrayAccess(**num_dict)
    aa.fill()
    # arr_via_ret should return same array (garr)
    garr = aa.arr_via_ret(cdt, dim)
    arr = aa.arr(cdt, dim)
    ass_eq(garr, arr)
    # insert completely different value to 'arr'
    if cdt == 'char':
        arr.flat = alpharange(100, numpy.prod(arr.shape) + 100)
    elif cdt == 'bool':
        arr[:] = -arr
    else:
        arr += 100
    raises(AssertionError)(assert_equal)(garr, arr)
    # get array (garr2) via arr_via_ret again
    garr2 = aa.arr_via_ret(cdt, dim)
    assert_equal(garr2, arr)


def check_num(clibname, list_num, list_cdt, carrtype=None):
    """Check SimObject.num()"""
    ArrayAccess = gene_class_ArrayAccess(
        clibname, len(list_num), list_cdt, carrtype)
    num_dict = dict(zip(ArrayAccess.num_names, list_num))
    aa = ArrayAccess(**num_dict)
    nd = len(list_num)
    eq_(tuple(aa.num(*LIST_IDX[:nd])), tuple(list_num))
    eq_(tuple(aa.num(','.join(LIST_IDX[:nd]))), tuple(list_num))
    eq_(tuple(aa.num(', '.join(LIST_IDX[:nd]))), tuple(list_num))


class BaseArrayAccess(SimObject):

    _cstructname_ = 'ArrayAccess'
    _clibdir_ = relpath('ext/build', __file__)

    list_cdt = ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
                'float', 'double', 'longdouble', 'size_t']

    def __init__(self, **kwds):
        for name in self.num_names:
            kwds.setdefault(name, 2)
        super(BaseArrayAccess, self).__init__(**kwds)

    def arr(self, cdt, dim):
        """Get array member '{cdt}{dim}d' (e.g., 'int2d')"""
        return getattr(self, '%s%dd' % (cdt, dim))

    def arr_via_ret(self, cdt, dim):
        """Get copy of array using 'get_{cdt}{dim}d' c-function"""
        get = getattr(self, 'get_%s%dd' % (cdt, dim))
        arr = self.arr(cdt, dim)
        garr = numpy.zeros_like(arr)
        for idx in numpy.ndindex(*arr.shape):
            get(*idx)  # call get_* c-func. which store val. in ret_{cdt}
            garr[idx] = getattr(self, 'ret_%s' % cdt)
        return garr

    def fill(self):
        """Fill array members using arange"""
        for cdt in self.list_cdt:
            if cdt == 'char':
                arange = alpharange
            elif cdt == 'bool':
                arange = lambda n: numpy.arange(n) % 2
            else:
                arange = numpy.arange
            for dim in range(1, 1 + self.ndim):
                arr = self.arr(cdt, dim)
                arr.flat = arange(arr.size)


class DefaultArrayAccess(BaseArrayAccess):

    ndim = 3
    list_cdt = BaseArrayAccess.list_cdt
    carrtype = None  # or 'flat'

    nd = ndim
    _clibname_ = 'arrayaccess.so'
    _cmembers_ = gene_cmembers(nd, list_cdt, carrtype)
    _cfuncs_ = gene_cfuncs(nd, list_cdt)
    num_names = gene_nums(nd)


if __name__ == '__main__':
    from pprint import pprint
    list_cdt = ['char', 'int', 'double']
    ndim = 3
    print('_cfuncs_')
    pprint(gene_cfuncs(ndim, list_cdt))
    print()
    print('_cmembers_')
    pprint(gene_cmembers(ndim, list_cdt))
