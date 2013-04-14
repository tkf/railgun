import copy

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
    pass


class MixinDeepCopyTest(MixinCopyTest):

    """
    Test that SimObject can be deep-copied.
    """

    copyfunc = staticmethod(copy.deepcopy)


class TestDeepCopyVectCalc(MixinDeepCopyTest, TestVectCalc):
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
