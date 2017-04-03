import pytest

from arrayaccess import check_arrayaccess, check_num
from test_arrayaccess import LIST_CDT, NDIM, LIST_NUM

LIST_CDT_C99 = LIST_CDT + ['longlong', 'ulonglong', 'bool']
del LIST_CDT
# LIST_NUM = [2] * NDIM


@pytest.mark.parametrize('cdt', LIST_CDT_C99)
@pytest.mark.parametrize('dim', range(1, 1 + NDIM))
@pytest.mark.parametrize('calloc', [None, True, False])
def test_arrayaccess_c99(cdt, dim, calloc):
    clibname = 'arrayaccess-c99.so'
    check_arrayaccess(clibname, LIST_NUM, LIST_CDT_C99, cdt, dim, calloc)


def test_num():
    check_num('arrayaccess-c99.so', LIST_NUM, LIST_CDT_C99)
