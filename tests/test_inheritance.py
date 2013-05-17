import unittest

from railgun import SimObject
from test_simobj import VectCalc


class VectCalcNoCFuncs(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = VectCalc._clibname_
    _clibdir_ = VectCalc._clibdir_
    _cmembers_ = VectCalc._cmembers_


CFUNC_NAMES = ['vec', 'subvec', 'fill', 'ans']


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
