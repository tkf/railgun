import numpy
from numpy.testing import assert_equal, assert_almost_equal
from nose.tools import raises

from railgun import SimObject, relpath

LIST_IDX = list('ijklmnopqrstuvwxyz')
LIST_CDT = ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
            'float', 'double', 'longdouble']
NDIM = 5
LIST_NUM = [11, 7, 5, 3, 2]
# LIST_NUM = [2] * NDIM


def get_str_get_array(cdt, dim):
    """
    Get c-function declaration 'get_{int,double}{1,2,..}d(i, j, ...)'

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


def get_str_cddec(cdt, dim):
    """
    Get c-data declaration '{int, double} {int,double}{1,2,..}[i][j]...'

    >>> get_str_cddec('int', 1)
    'int int1d[i]'
    >>> get_str_cddec('int', 2)
    'int int2d[i][j]'
    >>> get_str_cddec('double', 1)
    'double double1d[i]'
    >>> get_str_cddec('double', 2)
    'double double2d[i][j]'

    """
    args = ']['.join(LIST_IDX[:dim])
    return '%s %s%dd[%s]' % (cdt, cdt, dim, args)


def gene_nums(nd):
    return ['num_%s' % data for data in LIST_IDX[:nd]]


def gene_cmembers(nd, list_cdt):
    return (
        gene_nums(nd) +
        ['%(cdt)s ret_%(cdt)s' % dict(cdt=cdt) for cdt in
         ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
          'float', 'double', 'longdouble']] +
        [get_str_cddec(cdt, dim)
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


def gene_class_ArrayAccess(clibname, nd, _list_cdt):
    class ArrayAccess(SimObject):
        _clibname_ = clibname
        _clibdir_ = relpath('ext/build', __file__)
        _cmembers_ = gene_cmembers(nd, _list_cdt)
        _cfuncs_ = gene_cfuncs(nd, _list_cdt)
        num_names = gene_nums(nd)
        ndim = nd
        list_cdt = _list_cdt

        def get_arr(self, cdt, dim):
            get = getattr(self, 'get_%s%dd' % (cdt, dim))
            arr = getattr(self, '%s%dd' % (cdt, dim))
            garr = numpy.zeros_like(arr)
            for idx in numpy.ndindex(*arr.shape):
                get(*idx)
                garr[idx] = getattr(self, 'ret_%s' % cdt)
            return garr

        def fill(self):
            for cdt in self.list_cdt:
                if cdt == 'char':
                    arange = alpharange
                else:
                    arange = numpy.arange
                for dim in range(1, 1 + self.ndim):
                    arr = getattr(self, '%s%dd' % (cdt, dim))
                    shape = arr.shape
                    arr[:] = arange(numpy.prod(shape)).reshape(shape)
    return ArrayAccess


def check_arrayaccess(clibname, list_num, list_cdt, cdt, dim):
    if cdt in ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong']:
        ass_eq = assert_equal
    elif cdt in ['float', 'double', 'longdouble']:
        ass_eq = assert_almost_equal

    ArrayAccess = gene_class_ArrayAccess(
        clibname, len(list_num), list_cdt)
    num_dict = dict(zip(ArrayAccess.num_names, list_num))  # {num_i: 6, ...}
    aa = ArrayAccess(**num_dict)
    aa.fill()
    garr = aa.get_arr(cdt, dim)
    arr = getattr(aa, '%s%dd' % (cdt, dim))
    ass_eq(garr, arr)
    if cdt == 'char':
        arr.flat = alpharange(100, numpy.prod(arr.shape) + 100)
    else:
        arr += 100
    raises(AssertionError)(assert_equal)(garr, arr)
    garr2 = aa.get_arr(cdt, dim)
    assert_equal(garr2, arr)


def test_arrayaccess():
    for clibname in ['arrayaccess.so', 'arrayaccess-c99.so']:
        for cdt in LIST_CDT:
            for dim in range(1, 1 + NDIM):
                yield (check_arrayaccess, clibname, LIST_NUM, LIST_CDT,
                       cdt, dim)


if __name__ == '__main__':
    from pprint import pprint
    print '_cfuncs_'
    pprint(gene_cfuncs(NDIM, LIST_CDT))
    print
    print '_cmembers_'
    pprint(gene_cmembers(NDIM, LIST_CDT))
