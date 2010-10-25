# import numpy
# from numpy.testing import assert_equal
from nose.tools import ok_  # , raises, with_setup

from tsutils import eq_
from test_simobj import check_vec
from railgun import SimObject, relpath


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

    def __init__(self, num_i=10, **kwds):
        SimObject.__init__(self, num_i=num_i, **kwds)

    @classmethod
    def another_clib(cls, clibname):
        """
        Generate a class which loads `clibname` instead
        """
        class AnotherClass(cls):
            _cstructname_ = cls.__name__
            _clibname_ = clibname
        return AnotherClass


def test_another_clib():
    clibname = 'vectclac-O3.so'
    AnotherClass = VectCalc.another_clib(clibname)
    vc = AnotherClass()
    ok_(vc._cdll_._name.endswith(clibname))
    check_vec(vc)


def test():
    vc = VectCalc()
    eq_(vc.num_i, 10)
    vc = VectCalc(20)
    eq_(vc.num_i, 20)
    vc = VectCalc(num_i=30)
    eq_(vc.num_i, 30)
    check_vec(vc)
