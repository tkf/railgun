import unittest

from railgun import SimObject
from test_simobj import VectCalc


class VectCalcNoCFuncs(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_
    _cmembers_ = VectCalc._cmembers_


class MixinFullCFuncs(object):
    _cfuncs_ = VectCalc._cfuncs_


class MixInEmptyCFuncs(object):
    _cfuncs_ = []


class VectCalcEmptyCFuncs(MixInEmptyCFuncs, MixinFullCFuncs, VectCalcNoCFuncs):
    pass


class VectCalcFullCFuncs(MixinFullCFuncs, MixInEmptyCFuncs, VectCalcNoCFuncs):
    pass


class TestInheritanceFullCFuncs(unittest.TestCase):

    simclass = VectCalcFullCFuncs
    cfuncs = VectCalc._cfuncs_
    cfunc_names = ['vec', 'subvec', 'fill', 'subvec_dot']

    def test_cfuncs(self):
        self.assertEqual(self.simclass._cfuncs_, self.cfuncs)

    def check_cfunc(self, name):
        return hasattr(self.simclass, name)

    def test_defined_methods(self):
        yeses = list(map(self.check_cfunc, self.cfunc_names))
        self.assertTrue(all(yeses))

    def test_processed_by_metaclass(self):
        self.assertTrue(hasattr(self.simclass, 'cinfo'))


class TestInheritanceEmptyCFuncs(TestInheritanceFullCFuncs):

    simclass = VectCalcEmptyCFuncs
    cfuncs = []

    def check_cfunc(self, name):
        return not super(TestInheritanceEmptyCFuncs, self).check_cfunc(name)


class VectCalcFullCFuncs2(MixinFullCFuncs, VectCalcNoCFuncs):
    pass


class VectCalcEmptyCFuncs2(MixInEmptyCFuncs, VectCalcFullCFuncs2):
    pass


class TestInheritanceFullCFuncs2(TestInheritanceFullCFuncs):
    simclass = VectCalcFullCFuncs2


class TestInheritanceEmptyCFuncs2(TestInheritanceFullCFuncs):
# class TestInheritanceEmptyCFuncs2(TestInheritanceEmptyCFuncs):

    r"""
    Test how redefining ``_cfuncs_=[]`` work.

    Inheritance diagram::

        SimObject
              |
        VectCalcNoCFuncs
               \
                `-------------.
                              |
        MixinFullCFuncs   VectCalcNoCFuncs        : _cfuncs_ is not defined
               \              |
                `-----------. |
                             \|
        MixInEmptyCFuncs  VectCalcFullCFuncs2     : _cfuncs_ == [...]
               \              |
                `-----------. |
                             \|
                          VectCalcEmptyCFuncs2    : _cfuncs_ == []

    This test class should inherit from TestInheritanceEmptyCFuncs to
    test that C methods (e.g. `vec`) are not loaded.  However as there
    are Python methods defined at the point of VectCalcFullCFuncs2,
    actually these *Python* methods are defined.  Note that calling
    these function should raise an error, because the corresponding C
    is not loaded.

    """

    simclass = VectCalcEmptyCFuncs2
    cfuncs = []
