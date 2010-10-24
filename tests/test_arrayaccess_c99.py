from test_arrayaccess import check_arrayaccess, LIST_CDT

LIST_CDT = LIST_CDT + ['longlong', 'ulonglong', 'bool']
NDIM = 5
LIST_NUM = [11, 7, 5, 3, 2]
# LIST_NUM = [2] * NDIM

def test_arrayaccess_c99():
    clibname = 'arrayaccess-c99.so'
    for cdt in LIST_CDT:
        for dim in range(1, 1 + NDIM):
            yield (check_arrayaccess, clibname, LIST_NUM, LIST_CDT, cdt, dim)
