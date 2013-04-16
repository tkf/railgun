import copy
import unittest

from numpy.testing import assert_equal

from test_simobj import VectCalc


class TestCopy(unittest.TestCase):

    copyfunc = staticmethod(copy.copy)
    clone_v1 = [20] * 10

    def test_copy(self):
        orig = VectCalc()
        orig.v1 = 10
        clone = self.copyfunc(orig)
        orig.v1 = 20
        assert_equal(clone.v1, self.clone_v1)

    def test_identity(self):
        orig = VectCalc()
        clone = self.copyfunc(orig)
        assert clone is not orig

    def test_attrs_identity(self):
        orig = VectCalc()
        orig.some_random_attr = object()
        clone = self.copyfunc(orig)
        # NOTE: name = 'num_i' fails here:
        for name in ['v1', 'v2', 'v3', 'some_random_attr']:
            self.check_attrs_identity(name, clone, orig)

    def check_attrs_identity(self, name, clone, orig):
        msg = 'clone.{0} is orig.{0}'.format(name)
        assert getattr(clone, name) is getattr(orig, name), msg


class TestDeepCopy(TestCopy):

    copyfunc = staticmethod(copy.deepcopy)
    clone_v1 = [10] * 10

    def check_attrs_identity(self, name, clone, orig):
        msg = 'clone.{0} is not orig.{0}'.format(name)
        assert getattr(clone, name) is not getattr(orig, name), msg
