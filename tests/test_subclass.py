# import numpy
# from numpy.testing import assert_equal

from railgun import SimObject, relpath
from test_simobj import TestVectCalc


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


class TestVectCalcSubClass(TestVectCalc):
    simclass = VectCalc

    def check_init(self, vc, num_i):
        self.vc = vc
        self.assertEqual(self.vc.num_i, num_i)
        self.test_cfunc_vec()

    def test_init_no_arg(self):
        self.check_init(self.simclass(), 10)

    def test_init_positional(self):
        self.check_init(self.simclass(20), 20)

    def test_init_keyword(self):
        self.check_init(self.simclass(num_i=30), 30)

    def test_another_clib(self):
        clibname = 'vectclac-O3.so'
        AnotherClass = self.simclass.another_clib(clibname)
        self.vc = vc = AnotherClass()
        self.assertTrue(vc._cdll_._name.endswith(clibname))
        self.test_cfunc_vec()
