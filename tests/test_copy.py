import copy
import warnings

try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy
import six

from test_simobj import BaseTestVectCalc, TestVectCalc


class MixinCopyTest(object):

    """
    Test that SimObject can be shallow-copied.
    """

    copyfunc = staticmethod(copy.copy)

    def new(self, simclass, *args, **kwds):
        self.orig_vc = super(MixinCopyTest, self).new(simclass, *args, **kwds)
        return self.copyfunc(self.orig_vc)


class TestCopyVectCalc(MixinCopyTest, TestVectCalc):

    # Copying increases refcount.  So some of the resize-related tests
    # do no work with shallow copy:
    test_resize = None
    test_resize_old_values_copied_with_in_place = None

    pass


class MixinDeepCopyTest(MixinCopyTest):

    """
    Test that SimObject can be deep-copied.
    """

    copyfunc = staticmethod(copy.deepcopy)


class TestDeepCopyVectCalc(MixinDeepCopyTest, TestVectCalc):
    pass


class MixinPickleTest(MixinCopyTest):

    """
    Test that SimObject can be pickled.
    """

    @staticmethod
    def copyfunc(obj):
        return pickle.loads(pickle.dumps(obj))


class TestPickleVectCalc(MixinPickleTest, TestVectCalc):

    if six.PY2:
        def _force_owndata(self):
            non_owndata = {}
            for name in ['v1', 'v2', 'v3']:
                val = getattr(self.vc, name)
                if isinstance(val, numpy.ndarray) and not val.flags['OWNDATA']:
                    non_owndata[name] = val.copy()
                    assert non_owndata[name].flags['OWNDATA']
            if non_owndata:
                self.vc.setv(non_owndata, in_place=True)
                warnings.warn(
                    "re-allocating arrays {}, presumably because"
                    "pickle returns numpy array with OWNDATA=False"
                    .format(sorted(non_owndata)))

        def test_resize(self):
            self._force_owndata()
            super(TestPickleVectCalc, self).test_resize()

        def test_resize_old_values_copied_with_in_place(self):
            self._force_owndata()
            super(TestPickleVectCalc, self) \
                .test_resize_old_values_copied_with_in_place()

    pass


class MixinTestCopyTest(object):

    """
    Test that mixin classes work.
    """

    def test(self):
        assert self.orig_vc is not self.vc


class TestCopyTest(MixinTestCopyTest, MixinCopyTest, BaseTestVectCalc):
    pass


class TestDeepCopyTest(MixinTestCopyTest, MixinDeepCopyTest, BaseTestVectCalc):
    pass


class TestPickleTest(MixinTestCopyTest, MixinPickleTest, BaseTestVectCalc):
    pass
