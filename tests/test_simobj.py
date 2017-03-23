import unittest

import numpy
from numpy.testing import assert_equal
from nose.tools import raises, ok_  # , with_setup

from tsutils import eq_
from railgun import SimObject, relpath, cmem
from railgun.simobj import CDT2CTYPE, CDT2DTYPE, POINTER


class Int1DimArrayAsObject(object):
    _ctype_ = POINTER(CDT2CTYPE['int'])

    @property
    def _cdata_(self):
        # Define _cdata_ as a property to make this object deepcopy-able.
        return self.arr.ctypes.data_as(POINTER(CDT2CTYPE['int']))

    def __init__(self, *args, **kwds):
        self.arr = numpy.array(*args, dtype=CDT2DTYPE['int'], **kwds)


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


class VectCalcWithCwrap(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_
    _cmembers_ = VectCalc._cmembers_
    _cfuncs_ = VectCalc._cfuncs_

    def _cwrap_subvec(old_subvec):
        def subvec(self, i1=0, i2=None, op='plus'):
            if i2 is None:
                i2 = self.num_i
            old_subvec(self, i1=i1, i2=i2, op=op)
            return self.v3[i1:i2]
        return subvec


class VectCalcSuperInSubClass(VectCalc):

    def subvec(self, i1=0, i2=None, op='plus'):
        if i2 is None:
            i2 = self.num_i
        super(VectCalcSuperInSubClass, self).subvec(i1=i1, i2=i2, op=op)
        return self.v3[i1:i2]


class BaseVectCalcUsingSuper(SimObject):

    def subvec(self, i1=0, i2=None, op='plus'):
        if i2 is None:
            i2 = self.num_i
        super(BaseVectCalcUsingSuper, self).subvec(i1=i1, i2=i2, op=op)
        return self.v3[i1:i2]
    """
    NOTE: BaseVectCalcUsingSuper.subvec is equivalent to
    VectCalcSuperInSubClass.subvec, but as `super` is different, I can't
    copy it from there.
    """


class VectCalcSuperInBaseClass(BaseVectCalcUsingSuper):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_
    _cmembers_ = VectCalc._cmembers_
    _cfuncs_ = VectCalc._cfuncs_


class VectCalcNoDefaultNumI(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_
    _cmembers_ = ['num_i'] + VectCalc._cmembers_[1:]
    _cfuncs_ = VectCalc._cfuncs_


class VectCalcFixedShape(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_

    _cmembers_ = [
        'num_i = 5',
        'int v1[0]',
        'int v2[1]',
        'int v3[5]',
        'int ans',
        ]

    _cfuncs_ = []


class VectCalcCMemSubSet(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_
    _cmembers_ = VectCalc._cmembers_
    _cfuncs_ = VectCalc._cfuncs_

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


class VectCalcCMemObject(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_
    _cfuncs_ = VectCalc._cfuncs_

    _cmembers_ = [
        'num_i',
        cmem(Int1DimArrayAsObject, 'v1'),
        cmem(Int1DimArrayAsObject, 'v2'),
        cmem(Int1DimArrayAsObject, 'v3'),
        'int ans',
        ]

    def __init__(self, num_i=10, **kwds):
        SimObject.__init__(self, num_i=num_i, **kwds)
        self.v1 = Int1DimArrayAsObject([0] * num_i)
        self.v2 = Int1DimArrayAsObject([0] * num_i)
        self.v3 = Int1DimArrayAsObject([0] * num_i)


class BaseTestVectCalc(unittest.TestCase):

    """
    Test `SimObject` using its example class `VectCalc`.
    """

    VectCalc = VectCalc

    def new(self, simclass, *args, **kwds):
        return simclass(*args, **kwds)

    def make(self, *args, **kwds):
        return self.new(self._simclass, *args, **kwds)

    def setUp(self):
        self._simclass = self.VectCalc
        self.vc = self.make()

        # Make sure subclass does not use self.VectCalc to make objects
        self.VectCalc = None

    def mems(self):
        return [self.vc] + self.vc.getv('num_i', 'v1', 'v2', 'v3')

    def v3_desired(self, vc=None):
        (v1, v2) = (vc or self.vc).getv('v1', 'v2')
        return dict(plus=v1 + v2,
                    minus=v1 - v2,
                    times=v1 * v2,
                    divide=v1 // v2)


class TestVectCalc(BaseTestVectCalc):

    VectCalcWithCwrap = VectCalcWithCwrap
    VectCalcSuperInSubClass = VectCalcSuperInSubClass
    VectCalcSuperInBaseClass = VectCalcSuperInBaseClass
    VectCalcNoDefaultNumI = VectCalcNoDefaultNumI
    VectCalcFixedShape = VectCalcFixedShape
    VectCalcCMemSubSet = VectCalcCMemSubSet
    VectCalcCMemObject = VectCalcCMemObject

    def test_cmembers_default_value(self):
        vc = self.vc
        num_i = 10
        self.assertEqual(vc.num_i, num_i, 'comparing num_i')
        assert_equal(vc.v1, numpy.ones(num_i, dtype=int) * 1)
        assert_equal(vc.v2, numpy.ones(num_i, dtype=int) * 2)
        assert_equal(vc.v3, numpy.ones(num_i, dtype=int) * 0)

    def test_cfunc_vec(self):
        (vc, num_i, v1, v2, v3) = self.mems()
        l1 = range(vc.num_i)
        l2 = range(vc.num_i, vc.num_i * 2)
        vc.v1 = l1
        vc.v2 = l2
        assert_equal(v1, numpy.array(l1, dtype=int))
        assert_equal(v2, numpy.array(l2, dtype=int))

        v3d = self.v3_desired()
        for key in v3d:
            vc.vec(op=key)
            assert_equal(v3, v3d[key],
                         'comparing result(v3) of vec_%s' % key)

    def test_cfunc_subvec(self):
        (vc, num_i, v1, v2, v3) = self.mems()
        (num_i, v1, v2, v3) = vc.getv('num_i', 'v1', 'v2', 'v3')
        l1 = range(1, 11)
        l2 = range(11, 21)
        vc.v1 = l1
        vc.v2 = l2
        assert_equal(v1, numpy.array(l1, dtype=int))
        assert_equal(v2, numpy.array(l2, dtype=int))

        v3d = self.v3_desired()
        for i1 in range(num_i):
            for i2 in range(i1 + 1, num_i):
                for key in v3d:
                    vc.subvec(op=key, i1=i1, i2=i2)
                    assert_equal(v3[i1:i2], v3d[key][i1:i2],
                                 'comparing result(v3) of subvec_%s(%d, %d)' %
                                 (key, i1, i2))

    def test_cfunc_fill(self):
        (vc, num_i, v1, v2, v3) = self.mems()
        vc.fill(100)
        assert_equal(v1, numpy.ones(num_i, dtype=int) * 100)
        vc.fill(101, 'v1')
        assert_equal(v1, numpy.ones(num_i, dtype=int) * 101)
        vc.fill(102, 'v2')
        assert_equal(v2, numpy.ones(num_i, dtype=int) * 102)
        vc.fill(103, 'v3')
        assert_equal(v3, numpy.ones(num_i, dtype=int) * 103)

    def test_cfunc_subvec_dot(self):
        (vc, num_i, v1, v2, v3) = self.mems()
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

    def test_getv(self):
        vc = self.vc
        for (v1, v2, v3) in [vc.getv('v1', 'v2', 'v3'),
                             vc.getv('v1, v2, v3')]:
            ok_(v1 is vc.v1)
            ok_(v2 is vc.v2)
            ok_(v3 is vc.v3)

    def test_check_argument_validity(self):
        (vc, num_i, _, _, _) = self.mems()
        subvec_error = raises(ValueError)(vc.subvec)
        # no error
        vc.subvec()
        vc.subvec(i1=1, i2=num_i - 2)
        # error
        subvec_error(i1=-1)
        subvec_error(i2=-1)
        subvec_error(i1=num_i + 1)
        subvec_error(i2=num_i + 1)

    def check_init_kwds(self, kwds):
        vc = self.make(**kwds)
        for (key, desired) in kwds.items():
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

    def test_init_kwds(self):
        """Test if SimObject.__init__ works with various keywords"""
        self.check_init_kwds({})
        self.check_init_kwds(dict(num_i=10))
        self.check_init_kwds(dict(ans=0))
        self.check_init_kwds(dict(v1=0))
        self.check_init_kwds(dict(num_i=5, v1=[2, 3, 5, 7, 11]))
        self.check_init_kwds(dict(v1_0=0, v2_0=0, v3_0=0))
        raises(ValueError)(self.check_init_kwds)(dict(num_i=5, v1=[2, 3, 5]))
        raises(IndexError)(self.check_init_kwds)(dict(num_i=10, v1_10=0))
        raises(IndexError)(self.check_init_kwds)(dict(num_i=10, v2_10=0))
        raises(IndexError)(self.check_init_kwds)(dict(num_i=10, v3_10=0))
        raises(ValueError)(self.check_init_kwds)(dict(undefinedvar=0))

    def test_set_array_alias(self):
        vc = self.make(num_i=5)

        desired_v1 = numpy.ones_like(vc.v1)
        desired_v1[:] = [10, 11, 12, 13, 14]
        vc.setv(v1_0=10, v1_1=11, v1_2=12, v1_3=13, v1_4=14)
        assert_equal(vc.v1, desired_v1)

        raises(IndexError)(vc.setv)(v1_5=0)

    def test_cwrap_with_subvec(self):
        self.check_subvec_ret_value(self.VectCalcWithCwrap)

    def test_super_in_subclass(self):
        self.check_subvec_ret_value(self.VectCalcSuperInSubClass)

    def test_super_in_baseclass(self):
        self.check_subvec_ret_value(self.VectCalcSuperInBaseClass)

    def check_subvec_ret_value(self, simclass):
        vc = self.new(simclass)
        (num_i, v1, v2, v3) = vc.getv('num_i', 'v1', 'v2', 'v3')
        l1 = range(1, 11)
        l2 = range(11, 21)
        vc.v1 = l1
        vc.v2 = l2
        assert_equal(v1, numpy.array(l1, dtype=int))
        assert_equal(v2, numpy.array(l2, dtype=int))

        v3d = self.v3_desired(vc)
        for i1 in range(num_i):
            for i2 in range(i1 + 1, num_i):
                for key in v3d:
                    assert_equal(
                        vc.subvec(op=key, i1=i1, i2=i2), v3d[key][i1:i2],
                        'comparing result(v3) of subvec_%s(%d, %d)' %
                        (key, i1, i2))

    def check_init_wo_num(self, **kwds):
        self.new(self.VectCalcNoDefaultNumI, **kwds)

    def test_init_wo_num(self):
        """
        SimObject.__init__ should raise ValueError if num_* are not specified.
        """
        raises(ValueError)(self.check_init_wo_num)()
        self.check_init_wo_num(num_i=0)
        self.check_init_wo_num(num_i=1)

    def test_fixed_shape(self):
        """
        Array c-member can have fixed-shape.
        """
        for num_i in range(4, 7):
            vc = self.new(self.VectCalcFixedShape, num_i=num_i)
            assert vc.num("i") == num_i, 'vc.num("i") == num_i'
            assert vc.v1.shape == (0,), 'vc.v1.shape != (0,)'
            assert vc.v2.shape == (1,), 'vc.v2.shape != (1,)'
            assert vc.v3.shape == (5,), 'vc.v3.shape != (5,)'

    def test_cmemsubsets_default(self):
        vc = self.new(self.VectCalcCMemSubSet)
        eq_(vc._cmemsubsets_parsed_.getall(), dict(vec=False, dot=True))
        vc.subvec_dot()
        raises(ValueError)(vc.vec)()
        vc.getv('v1, v2')
        raises(KeyError)(vc.getv)('v3')

    def test_cmemsubsets_dot(self):
        vc = self.new(self.VectCalcCMemSubSet, _cmemsubsets_dot=False)
        eq_(vc._cmemsubsets_parsed_.getall(), dict(vec=False, dot=False))
        raises(ValueError)(vc.subvec_dot)()
        raises(ValueError)(vc.vec)()
        raises(KeyError)(vc.getv)('v1')
        raises(KeyError)(vc.getv)('v2')
        raises(KeyError)(vc.getv)('v3')

    def test_cmemsubsets_vec(self):
        vc = self.new(self.VectCalcCMemSubSet, _cmemsubsets_vec=True)
        eq_(vc._cmemsubsets_parsed_.getall(), dict(vec=True, dot=True))
        vc.subvec_dot()
        vc.vec()
        vc.getv('v1, v2, v3')

    def test_cmemobject(self):
        vc = self.new(self.VectCalcCMemObject)
        for i in [1, 2, 3]:
            vc.fill(i, 'v%d' % i)
            v_i = getattr(vc, 'v%d' % i).arr
            assert_equal(v_i, numpy.array([i] * vc.num_i))

    def setup_reallocation_test(self):
        vc = self.vc
        new_num_i = vc.num_i + 3
        vc.v1[:] = v1old = numpy.arange(vc.num_i) + 10
        return vc, new_num_i, v1old

    def test_reallocation(self):
        vc, new_num_i, _ = self.setup_reallocation_test()
        vc.reallocate(i=new_num_i, in_place=True)
        self.assertEqual(vc.num_i, new_num_i)
        self.assertEqual(vc.v1.shape, (new_num_i,))
        self.assertEqual(vc.v2.shape, (new_num_i,))
        self.assertEqual(vc.v3.shape, (new_num_i,))

    def test_reallocation_cmemobject(self):
        vc = self.new(self.VectCalcCMemObject)
        new_num_i = vc.num_i + 3
        vc.reallocate(i=new_num_i, in_place=True)
        self.assertEqual(vc.num_i, new_num_i)
        # NOTE: vc.v*.arr are uncharged, but that's ok.
        #       It is just to check `vc.reallocate` doesn't fail.

    def test_reallocation_in_place_true(self):
        vc, new_num_i, _ = self.setup_reallocation_test()

        v1 = vc.v1  # get a ref
        with self.assertRaises(ValueError):
            vc.reallocate(i=new_num_i, in_place=True)
        del v1
        # vc.reallocate(i=new_num_i, in_place=True)

    def test_reallocation_in_place_default(self):
        vc, new_num_i, _ = self.setup_reallocation_test()

        v1 = vc.v1  # get a ref
        vc.reallocate(i=new_num_i)
        assert vc.v1 is not v1

    def test_reallocation_old_values_copied_with_in_place(self):
        """
        `SimObject.reallocation` should copy old values when `in_place=True`.
        """
        vc, new_num_i, v1old = self.setup_reallocation_test()
        vc.reallocate(i=new_num_i, in_place=True)
        numpy.testing.assert_equal(vc.v1[:len(v1old)], v1old)

    def test_reallocation_old_values_copied_with_copy(self):
        vc, new_num_i, v1old = self.setup_reallocation_test()
        v1 = vc.v1  # get a ref
        vc.reallocate(i=new_num_i, in_place='or_copy')
        assert vc.v1 is not v1
        numpy.testing.assert_equal(vc.v1[:len(v1old)], v1old)

    def test_reallocation_old_values_not_copied(self):
        """
        `SimObject.reallocation` should fail to copy when referenced.

        When vc.v1.resize cannot be invoked because of an existing
        external reference to vc.v1, the new array would be created.
        In this case, old value would NOT be copied.
        """
        vc, new_num_i, v1old = self.setup_reallocation_test()

        v1 = vc.v1  # get a ref
        vc.reallocate(i=new_num_i)
        del v1
        with self.assertRaises(AssertionError):
            numpy.testing.assert_equal(vc.v1[:len(v1old)], v1old)
