import pytest

from railgun import SimObject, relpath


@pytest.mark.parametrize('cstructname, cfuncprefix', [
    ('VectCalc', None),
    (None, 'VectCalc_'),
])
def test_cstructname_and_cfuncprefix(cstructname, cfuncprefix):
    class ClassNameIsNotVectCalc(SimObject):
        _clibname_ = 'vectclac.so'
        _clibdir_ = relpath('ext/build', __file__)

        _cmembers_ = [
            'num_i',
            'int v1[i]',
            'int v2[i]',
            'int v3[i]',
            'int ans',
            ]

        _cfuncs_ = [
            "vec_{op | plus, minus, times, divide}()",
            "subvec_{op | plus, minus, times, divide}(i i1=0, i< i2=num_i)",
            "fill_{vec | v1, v2, v3}(int s)",
            "ans subvec_dot(i i1=0, i< i2=num_i)",
            ]

        if cstructname is not None:
            _cstructname_ = cstructname
        if cfuncprefix is not None:
            _cfuncprefix_ = cfuncprefix


@pytest.mark.parametrize('raises, cstructname, cfuncprefix', [
    (AttributeError, None, None),
    (AttributeError, 'WrongClassName', None),
    (AttributeError, 'VectCalc', 'WrongPrefix_'),
])
def test_cstructname_and_cfuncprefix_raises(raises, cstructname, cfuncprefix):
    with pytest.raises(raises):
        test_cstructname_and_cfuncprefix(cstructname, cfuncprefix)


def test_empty_cfuncprefix(cfuncprefix=''):
    class ClassNameIsNotVectCalc(SimObject):
        _clibname_ = 'vectclac.so'
        _clibdir_ = relpath('ext/build', __file__)

        _cmembers_ = [
            'num_i',
            'int v1[i]',
            'int v2[i]',
            'int v3[i]',
            'int ans',
            ]

        _cfuncs_ = ['VectCalc_' + f for f in [
            "vec_{op | plus, minus, times, divide}()",
            "subvec_{op | plus, minus, times, divide}(i i1=0, i< i2=num_i)",
            "fill_{vec | v1, v2, v3}(int s)",
            "subvec_dot(i i1=0, i< i2=num_i)",
            ]]

        if cfuncprefix is not None:
            _cfuncprefix_ = cfuncprefix


def test_empty_cfuncprefix_raises():
    with pytest.raises(AttributeError):
        test_empty_cfuncprefix(None)
