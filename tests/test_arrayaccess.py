import pytest

from arrayaccess import check_arrayaccess, check_num

LIST_CDT = ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
            'float', 'double', 'longdouble', 'size_t']
NDIM = 5
LIST_NUM = [11, 7, 5, 3, 2]
# LIST_NUM = [2] * NDIM


@pytest.mark.parametrize('cdt', LIST_CDT)
@pytest.mark.parametrize('dim', range(1, 1 + NDIM))
@pytest.mark.parametrize('calloc', [None, True, False])
def test_arrayaccess(cdt, dim, calloc):
    clibname = 'arrayaccess.so'
    check_arrayaccess(clibname, LIST_NUM, LIST_CDT, cdt, dim, calloc)


def test_num():
    check_num('arrayaccess.so', LIST_NUM, LIST_CDT)
