from nose.tools import eq_

from railgun import cm


def test_cm():
    desired = ['int a', 'int b', 'int c']
    eq_(cm.int('a', 'b', 'c'), desired)
    eq_(cm.int('a, b, c'), desired)
    eq_(cm['int']('a', 'b', 'c'), desired)

    eq_(cm['int'](['a', 'b', 'c']), desired)
    eq_(cm['int'](i for i in ['a', 'b', 'c']), desired)
