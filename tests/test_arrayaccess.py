import numpy
from numpy.testing import assert_equal, assert_almost_equal
from nose.tools import raises

from railgun import SimObject, relpath

LIST_IDX = list('ijklm')
LIST_NUM = [11, 7, 5, 3, 2]
LIST_CDT = 'int', 'double'
LIST_DIM = range(1, 6)


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

_CMEMBERS_ = (
    ['num_%s = %d' % data for data in zip(LIST_IDX, LIST_NUM)] +
    ['int ret_int', 'double ret_double'] +
    [get_str_cddec(cdt, dim) for cdt in LIST_CDT for dim in LIST_DIM]
    )
_CFUNCS_ = [
    get_str_get_array(cdt, dim) for cdt in LIST_CDT for dim in LIST_DIM
    ]


class ArrayAccess(SimObject):
    _clibname_ = 'arrayaccess.so'
    _clibdir_ = relpath('ext/build', __file__)
    _cmembers_ = _CMEMBERS_
    _cfuncs_ = _CFUNCS_

    def get_arr(self, cdt, dim):
        get = getattr(self, 'get_%s%dd' % (cdt, dim))
        arr = getattr(self, '%s%dd' % (cdt, dim))
        garr = numpy.zeros_like(arr)
        for idx in numpy.ndindex(*arr.shape):
            get(*idx)
            garr[idx] = getattr(self, 'ret_%s' % cdt)
        return garr

    def fill(self):
        for cdt in LIST_CDT:
            for dim in LIST_DIM:
                arr = getattr(self, '%s%dd' % (cdt, dim))
                shape = arr.shape
                arr[:] = numpy.arange(numpy.prod(shape)).reshape(shape)


def check_arrayaccess(cdt, dim):
    if cdt in ['int']:
        ass_eq = assert_almost_equal
    elif cdt in ['double']:
        ass_eq = assert_almost_equal

    aa = ArrayAccess()
    aa.fill()
    garr = aa.get_arr(cdt, dim)
    arr = getattr(aa, '%s%dd' % (cdt, dim))
    ass_eq(garr, arr)
    arr += 100
    raises(AssertionError)(assert_equal)(garr, arr)
    garr2 = aa.get_arr(cdt, dim)
    assert_equal(garr2, arr)


def test_arrayaccess():
    for cdt in LIST_CDT:
        for dim in LIST_DIM:
            yield (check_arrayaccess, cdt, dim)


if __name__ == '__main__':
    from pprint import pprint
    print '_cfuncs_'
    pprint(_CFUNCS_)
    print
    print '_cmembers_'
    pprint(_CMEMBERS_)
