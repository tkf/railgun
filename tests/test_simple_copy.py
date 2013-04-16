import copy
import unittest

from numpy.testing import assert_equal

from test_simobj import VectCalc
from arrayaccess import DefaultArrayAccess


class TestCopy(unittest.TestCase):

    simclass = VectCalc
    copyfunc = staticmethod(copy.copy)
    clone_v1 = [20] * 10

    def check_copy(self, name, value):
        orig = self.simclass()
        setattr(orig, name, 10)
        clone = self.copyfunc(orig)
        setattr(orig, name, 20)
        assert_equal(getattr(clone, name), value)

    def test_copy(self):
        self.check_copy('v1', self.clone_v1)

    def test_identity(self):
        orig = self.simclass()
        clone = self.copyfunc(orig)
        assert clone is not orig

    def test_attrs_identity(self):
        orig = self.simclass()
        orig.some_random_attr = object()
        clone = self.copyfunc(orig)
        # NOTE: name = 'num_i' fails here:
        for name in self.check_attrs_identity_names:
            self.check_attrs_identity(name, clone, orig)

    check_attrs_identity_names = ['v1', 'v2', 'v3', 'some_random_attr']

    def check_attrs_identity(self, name, clone, orig):
        msg = 'clone.{0} is orig.{0}'.format(name)
        assert getattr(clone, name) is getattr(orig, name), msg


class TestDeepCopy(TestCopy):

    copyfunc = staticmethod(copy.deepcopy)
    clone_v1 = [10] * 10

    def check_attrs_identity(self, name, clone, orig):
        msg = 'clone.{0} is not orig.{0}'.format(name)
        assert getattr(clone, name) is not getattr(orig, name), msg


class MixinTestCopy3D(object):
    simclass = DefaultArrayAccess
    check_attrs_identity_names = [
        'char1d', 'int2d', 'double3d', 'some_random_attr']
    clone_int2d = [[20] * 2] * 2

    def test_copy(self):
        self.check_copy('int2d', self.clone_int2d)


class TestCopy3D(MixinTestCopy3D, TestCopy):
    pass


class TestDeepCopy3D(MixinTestCopy3D, TestDeepCopy):
    clone_int2d = [[10] * 2] * 2
