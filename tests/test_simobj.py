import copy
import unittest

import numpy
from numpy.testing import assert_equal
from nose.tools import raises, ok_  # , with_setup

from tsutils import eq_
from railgun import SimObject, relpath, cmem
from railgun.simobj import CDT2CTYPE, CDT2DTYPE, POINTER


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


def check_vec(vc):
    v1 = vc.v1
    v2 = vc.v2
    v3 = vc.v3
    l1 = range(vc.num_i)
    l2 = range(vc.num_i, vc.num_i * 2)
    vc.v1 = l1
    vc.v2 = l2
    assert_equal(v1, numpy.array(l1, dtype=int))
    assert_equal(v2, numpy.array(l2, dtype=int))

    v3d = v3_desired(vc.v1, vc.v2)
    for key in v3d:
        vc.vec(op=key)
        assert_equal(v3, v3d[key],
                     'comparing result(v3) of vec_%s' % key)


def test_vec():
    vc = VectCalc()
    check_vec(vc)


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


def test_cwrap_with_subvec():
    class VectCalcWithCwrap(VectCalc):
        _cstructname_ = 'VectCalc'

        def _cwrap_subvec(old_subvec):
            def subvec(self, i1=0, i2=None, op='plus'):
                if i2 is None:
                    i2 = self.num_i
                old_subvec(self, i1=i1, i2=i2, op=op)
                return self.v3[i1:i2]
            return subvec

    vc = VectCalcWithCwrap()
    num_i = vc.num_i
    v1 = vc.v1
    v2 = vc.v2
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
                assert_equal(vc.subvec(op=key, i1=i1, i2=i2), v3d[key][i1:i2],
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


def check_init_wo_num(kwds):
    class VectCalc(SimObject):
        _clibname_ = 'vectclac.so'
        _clibdir_ = relpath('ext/build', __file__)

        _cmembers_ = [
            'num_i',
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

    VectCalc(**kwds)


def test_init_wo_num():
    """SimObject.__init__ should raise ValueError if num_* are not specified"""
    yield (raises(ValueError)(check_init_wo_num), {})
    yield (check_init_wo_num, dict(num_i=0))
    yield (check_init_wo_num, dict(num_i=1))


def test_get():
    vc = VectCalc()
    for (v1, v2, v3) in [vc.getv('v1', 'v2', 'v3'), vc.getv('v1, v2, v3')]:
        ok_(v1 is vc.v1)
        ok_(v2 is vc.v2)
        ok_(v3 is vc.v3)


def check_init_kwds(kwds):
    vc = VectCalc(**kwds)
    for (key, desired) in kwds.iteritems():
        if vc.array_alias(key):
            pass
        else:
            actual = vc.getv(key)
            if (isinstance(actual, numpy.ndarray) and
                not isinstance(desired, numpy.ndarray)):
                d = numpy.ones_like(actual) * desired
                assert_equal(actual, d)
            else:
                assert_equal(actual, desired)


def test_init_kwds():
    """Test if SimObject.__init__ works with various keywords"""
    yield (check_init_kwds, {})
    yield (check_init_kwds, dict(num_i=10))
    yield (check_init_kwds, dict(ans=0))
    yield (check_init_kwds, dict(v1=0))
    yield (check_init_kwds, dict(num_i=5, v1=[2,3,5,7,11]))
    yield (raises(ValueError)(check_init_kwds), dict(num_i=5, v1=[2,3,5]))
    yield (check_init_kwds, dict(v1_0=0, v2_0=0, v3_0=0))
    yield (raises(IndexError)(check_init_kwds), dict(num_i=10, v1_10=0))
    yield (raises(IndexError)(check_init_kwds), dict(num_i=10, v2_10=0))
    yield (raises(IndexError)(check_init_kwds), dict(num_i=10, v3_10=0))
    yield (raises(ValueError)(check_init_kwds), dict(undefinedvar=0))


def test_set_array_alias():
    vc = VectCalc(num_i=5)

    desired_v1 = numpy.ones_like(vc.v1)
    desired_v1[:] = [10, 11, 12, 13, 14]
    vc.setv(v1_0=10, v1_1=11, v1_2=12, v1_3=13, v1_4=14)
    assert_equal(vc.v1, desired_v1)

    raises(IndexError)(vc.setv)(v1_5=0)


def check_cstructname_and_cfuncprefix(cstructname, cfuncprefix):
    class ClassNameIsNotVectCalc(SimObject):
        _clibname_ = 'vectclac.so'
        _clibdir_ = relpath('ext/build', __file__)

        _cmembers_ = [
            'num_i',
            'int v1[i]',
            'int v2[i]',
            'int v3[i]',
            'int ans',
            ]

        _cfuncs_ = [
            "vec_{op | plus, minus, times, divide}()",
            "subvec_{op | plus, minus, times, divide}(i i1=0, i< i2=num_i)",
            "fill_{vec | v1, v2, v3}(int s)",
            "ans subvec_dot(i i1=0, i< i2=num_i)",
            ]

        if cstructname is not None:
            _cstructname_ = cstructname
        if cfuncprefix is not None:
            _cfuncprefix_ = cfuncprefix


def test_cstructname_and_cfuncprefix():
    raises_nothing = check_cstructname_and_cfuncprefix
    raises_AttributeError = raises(AttributeError
                                   )(check_cstructname_and_cfuncprefix)
    yield (raises_nothing, 'VectCalc', None)
    yield (raises_AttributeError, None, None)
    yield (raises_AttributeError, 'WrongClassName', None)
    yield (raises_AttributeError, 'VectCalc', 'WrongPrefix_')
    yield (raises_nothing, None, 'VectCalc_')


def check_empty_cfuncprefix(cfuncprefix):
    class ClassNameIsNotVectCalc(SimObject):
        _clibname_ = 'vectclac.so'
        _clibdir_ = relpath('ext/build', __file__)

        _cmembers_ = [
            'num_i',
            'int v1[i]',
            'int v2[i]',
            'int v3[i]',
            'int ans',
            ]

        _cfuncs_ = ['VectCalc_' + f for f in [
            "vec_{op | plus, minus, times, divide}()",
            "subvec_{op | plus, minus, times, divide}(i i1=0, i< i2=num_i)",
            "fill_{vec | v1, v2, v3}(int s)",
            "subvec_dot(i i1=0, i< i2=num_i)",
            ]]

        if cfuncprefix is not None:
            _cfuncprefix_ = cfuncprefix


def test_empty_cfuncprefix():
    raises_nothing = check_empty_cfuncprefix
    raises_AttributeError = raises(AttributeError)(check_empty_cfuncprefix)
    yield (raises_nothing, '')
    yield (raises_AttributeError, None)


def test_fixed_shape():
    """
    Array c-member can have fixed-shape
    """

    class VectCalc(SimObject):
        _clibname_ = 'vectclac.so'
        _clibdir_ = relpath('ext/build', __file__)

        _cmembers_ = [
            'num_i = 5',
            'int v1[0]',
            'int v2[1]',
            'int v3[5]',
            'int ans',
            ]

        _cfuncs_ = []

    for num_i in range(4,7):
        vc = VectCalc(num_i=num_i)
        assert vc.num("i") == num_i, 'vc.num("i") == num_i'
        assert vc.v1.shape == (0,), 'vc.v1.shape != (0,)'
        assert vc.v2.shape == (1,), 'vc.v2.shape != (1,)'
        assert vc.v3.shape == (5,), 'vc.v3.shape != (5,)'


def test_cmemsubset():

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

        _cmemsubsets_ = dict(
            vec=dict(members=['v1', 'v2', 'v3'],
                     funcs=['vec_{plus, minus, times, divide}',
                            'subvec_{plus, minus, times, divide}',
                            'fill_{v1, v2, v3}'],
                     default=False),
            dot=dict(members=['v1', 'v2'],
                     funcs=['subvec_dot'],
                     default=True),
            )

    vc = VectCalc()
    eq_(vc._cmemsubsets_parsed_.getall(), dict(vec=False, dot=True))
    vc.subvec_dot()
    raises(ValueError)(vc.vec)()
    vc.getv('v1, v2')
    raises(KeyError)(vc.getv)('v3')

    vc = VectCalc(_cmemsubsets_dot=False)
    eq_(vc._cmemsubsets_parsed_.getall(), dict(vec=False, dot=False))
    raises(ValueError)(vc.subvec_dot)()
    raises(ValueError)(vc.vec)()
    raises(KeyError)(vc.getv)('v1')
    raises(KeyError)(vc.getv)('v2')
    raises(KeyError)(vc.getv)('v3')

    vc = VectCalc(_cmemsubsets_vec=True)
    eq_(vc._cmemsubsets_parsed_.getall(), dict(vec=True, dot=True))
    vc.subvec_dot()
    vc.vec()
    vc.getv('v1, v2, v3')


def test_cmem_object():

    class Int1DimArrayAsObject(object):
        _ctype_ = POINTER(CDT2CTYPE['int'])
        def __init__(self, *args, **kwds):
            self.arr = arr = numpy.array(*args, dtype=CDT2DTYPE['int'], **kwds)
            self._cdata_ = arr.ctypes.data_as(POINTER(CDT2CTYPE['int']))

    class VectCalc(SimObject):
        _clibname_ = 'vectclac.so'
        _clibdir_ = relpath('ext/build', __file__)

        _cmembers_ = [
            'num_i',
            cmem(Int1DimArrayAsObject, 'v1'),
            cmem(Int1DimArrayAsObject, 'v2'),
            cmem(Int1DimArrayAsObject, 'v3'),
            'int ans',
            ]

        _cfuncs_ = [
            "vec_{op | plus, minus, times, divide}()",
            "subvec_{op | plus, minus, times, divide}(i i1=0, i< i2=num_i)",
            "fill_{vec | v1, v2, v3}(int s)",
            "ans subvec_dot(i i1=0, i< i2=num_i)",
            ]

        def __init__(self, num_i=10, **kwds):
            SimObject.__init__(self, num_i=num_i, **kwds)
            self.v1 = Int1DimArrayAsObject([0] * num_i)
            self.v2 = Int1DimArrayAsObject([0] * num_i)
            self.v3 = Int1DimArrayAsObject([0] * num_i)

    vc = VectCalc()
    for i in [1, 2, 3]:
        vc.fill(i, 'v%d' % i)
        v_i = getattr(vc, 'v%d' % i).arr
        assert_equal(v_i, numpy.array([i] * vc.num_i))


class TestCopy(unittest.TestCase):

    copyfunc = staticmethod(copy.copy)
    clone_v1 = 20

    def test_copy(self):
        orig = VectCalc()
        orig.v1 = 10
        clone = self.copyfunc(orig)
        orig.v1 = 20
        assert_equal(clone.v1, self.clone_v1)


class TestDeepCopy(TestCopy):

    copyfunc = staticmethod(copy.deepcopy)
    clone_v1 = 10
