import numpy
from numpy.testing import assert_equal
from nose.tools import raises  #, ok_, with_setup

from tsutils import eq_
from railgun import SimObject, relpath


class VectCalc(SimObject):
    _clibname_ = 'vectclac.so'
    _clibdir_ = relpath('ext/build', __file__)

    _cmembers_ = [
        'num_i = 10',
        'int v1[i] = 1',
        'int v2[i] = 2',
        'int v3[i]',
        'int ans',
        ]

    _cfuncs_ = [
        "vec_{op | plus, minus, times, divide}()",
        "subvec_{op | plus, minus, times, divide}(i i1=0, i< i2=num_i)",
        "fill_{vec | v1, v2, v3}(int s)",
        "ans subvec_dot(i i1=0, i< i2=num_i)",
        ]


def test_default():
    vc = VectCalc()
    num_i = 10
    eq_(vc.num_i, num_i, 'comparing num_i')
    assert_equal(vc.v1, numpy.ones(num_i, dtype=int) * 1)
    assert_equal(vc.v2, numpy.ones(num_i, dtype=int) * 2)
    assert_equal(vc.v3, numpy.ones(num_i, dtype=int) * 0)


def v3_desired(v1, v2):
    return dict(plus=v1 + v2, minus=v1 - v2, times=v1 * v2, divide=v1 / v2)


def test_vec():
    vc = VectCalc()
    v1 = vc.v1
    v2 = vc.v2
    v3 = vc.v3
    l1 = range(1, 11)
    l2 = range(11, 21)
    vc.v1 = l1
    vc.v2 = l2
    assert_equal(v1, numpy.array(l1, dtype=int))
    assert_equal(v2, numpy.array(l2, dtype=int))

    v3d = v3_desired(vc.v1, vc.v2)
    for key in v3d:
        vc.vec(op=key)
        assert_equal(v3, v3d[key],
                     'comparing result(v3) of vec_%s' % key)


def test_subvec():
    vc = VectCalc()
    num_i = vc.num_i
    v1 = vc.v1
    v2 = vc.v2
    v3 = vc.v3
    l1 = range(1, 11)
    l2 = range(11, 21)
    vc.v1 = l1
    vc.v2 = l2
    assert_equal(v1, numpy.array(l1, dtype=int))
    assert_equal(v2, numpy.array(l2, dtype=int))

    v3d = v3_desired(vc.v1, vc.v2)
    for i1 in range(num_i):
        for i2 in range(i1 + 1, num_i):
            for key in v3d:
                vc.subvec(op=key, i1=i1, i2=i2)
                assert_equal(v3[i1:i2], v3d[key][i1:i2],
                             'comparing result(v3) of subvec_%s(%d, %d)' %
                             (key, i1, i2))


def test_fill():
    vc = VectCalc()
    num_i = vc.num_i
    vc.fill(100)
    assert_equal(vc.v1, numpy.ones(num_i, dtype=int) * 100)
    vc.fill(101, 'v1')
    assert_equal(vc.v1, numpy.ones(num_i, dtype=int) * 101)
    vc.fill(102, 'v2')
    assert_equal(vc.v2, numpy.ones(num_i, dtype=int) * 102)
    vc.fill(103, 'v3')
    assert_equal(vc.v3, numpy.ones(num_i, dtype=int) * 103)


def test_subvec_dot():
    vc = VectCalc()
    num_i = vc.num_i
    v1 = vc.v1
    v2 = vc.v2
    l1 = range(1, 11)
    l2 = range(11, 21)
    vc.v1 = l1
    vc.v2 = l2
    assert_equal(v1, numpy.array(l1, dtype=int))
    assert_equal(v2, numpy.array(l2, dtype=int))

    for i1 in range(num_i):
        for i2 in range(i1 + 1, num_i):
            correct = numpy.dot(v1[i1:i2], v2[i1:i2])
            vc.subvec_dot(i1, i2)
            assert_equal(
                vc.ans, correct,
                'comparing result(ans) of subvec_dot(%d, %d)' % (i1, i2))


def test_check_argument_validity():
    vc = VectCalc()
    num_i = vc.num_i
    def subvec_noerror(kwds):
        return vc.subvec(**kwds)
    subvec_error = raises(ValueError)(subvec_noerror)
    # no error
    yield (subvec_noerror, {})
    yield (subvec_noerror, dict(i1=1, i2=num_i - 2))
    # error
    yield (subvec_error, dict(i1=-1))
    yield (subvec_error, dict(i2=-1))
    yield (subvec_error, dict(i1=num_i + 1))
    yield (subvec_error, dict(i2=num_i + 1))
