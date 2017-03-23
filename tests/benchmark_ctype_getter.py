from __future__ import print_function

import timeit
import numpy

code_setup = """
import numpy
from railgun.simobj import ctype_getter
shape = %s
arr = numpy.zeros(shape, dtype=bool)
"""

code_stmt = """
ctype_getter(arr)
"""

def main(repeat, number, shape):
    results = numpy.array(timeit.repeat(
        code_stmt, code_setup % shape, repeat=repeat, number=number,
        )) / number
    print("repeat: %d, number: %d, shape: %s" % (repeat, number, shape))
    print("min: %.4g, max: %.4g, mean: %.4g, std: %.4g" % (
        results.min(), results.max(), results.mean(), results.std()))


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-r", "--repeat", type="int", default=5)
    parser.add_option("-n", "--number", type="int", default=20)
    parser.add_option("-s", "--shape", default="(100, 100, 100)")
    (opts, args) = parser.parse_args()

    main(opts.repeat, opts.number, opts.shape)
