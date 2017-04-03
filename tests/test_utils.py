from railgun import cm


def test_cm():
    desired = ['int a', 'int b', 'int c']
    assert cm.int('a', 'b', 'c') == desired
    assert cm.int('a, b, c') == desired
    assert cm['int']('a', 'b', 'c') == desired

    assert cm['int'](['a', 'b', 'c']) == desired
    assert cm['int'](i for i in ['a', 'b', 'c']) == desired
