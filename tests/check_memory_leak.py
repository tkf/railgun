from __future__ import print_function

import sys
import numpy

from arrayaccess import gene_class_ArrayAccess
from test_arrayaccess import LIST_CDT, LIST_NUM


def main(iter_num, list_num, calloc):
    clibname = 'arrayaccess.so'
    ArrayAccess = gene_class_ArrayAccess(clibname, len(list_num), LIST_CDT)
    ArrayAccess._calloc_ = calloc

    if iter_num <= 10:
        printnow = range(iter_num)
    else:
        printnow = numpy.linspace(
            0, iter_num, num=10, endpoint=False).astype(int)

    num_dict = dict(zip(ArrayAccess.num_names, list_num))  # {num_i: 6, ...}
    assert ArrayAccess._calloc_ is bool(calloc)

    print('[*/%d]:' % iter_num, end=' ')
    sys.stdout.flush()
    for i in range(iter_num):
        ArrayAccess(**num_dict)
        if i in printnow:
            print(i, end=' ')
            sys.stdout.flush()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-n", "--nums", default='100, 10, 10, 10, 10',
                      help="comma separated numbers")
    parser.add_option("-t", "--time", default=1000, type=int)
    parser.add_option("-c", "--calloc", default=1, type=int)
    (opts, args) = parser.parse_args()
    if opts.nums:
        list_num = eval('[%s]' % opts.nums)
        if len(list_num) != len(LIST_NUM):
            raise RuntimeError ('%s numbers are expected. %s given.'
                                % (len(LIST_NUM), len(list_num)))
    else:
        list_num = LIST_NUM

    main(opts.time, list_num, bool(opts.calloc))
