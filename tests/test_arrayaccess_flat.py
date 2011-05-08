from arrayaccess import check_arrayaccess, check_num

LIST_CDT = ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
            'float', 'double', 'longdouble', 'size_t']
NDIM = 5
LIST_NUM = [11, 7, 5, 3, 2]
# LIST_NUM = [2] * NDIM


def test_arrayaccess():
    clibname = 'arrayaccess-flat.so'
    _calloc_ = None
    carrtype = "flat"
    for cdt in LIST_CDT:
        for dim in range(1, 1 + NDIM):
            yield (check_arrayaccess, clibname, LIST_NUM, LIST_CDT, cdt,
                   dim, _calloc_, carrtype)


def test_num():
    yield (check_num, 'arrayaccess-flat.so', LIST_NUM, LIST_CDT, "flat")
