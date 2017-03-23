from arrayaccess import check_arrayaccess, check_num
from test_arrayaccess import LIST_CDT, NDIM, LIST_NUM

LIST_CDT_C99 = LIST_CDT + ['longlong', 'ulonglong', 'bool']
del LIST_CDT
# LIST_NUM = [2] * NDIM


def test_arrayaccess_c99():
    clibname = 'arrayaccess-c99.so'
    for cdt in LIST_CDT_C99:
        for dim in range(1, 1 + NDIM):
            for _calloc_ in [None, True, False]:
                yield (check_arrayaccess, clibname, LIST_NUM, LIST_CDT_C99,
                       cdt, dim, _calloc_)


def test_num():
    yield (check_num, 'arrayaccess-c99.so', LIST_NUM, LIST_CDT_C99)
