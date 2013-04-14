from nose.tools import raises

from railgun import SimObject, relpath


def check_cstructname_and_cfuncprefix(cstructname, cfuncprefix):
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


def test_cstructname_and_cfuncprefix():
    raises_nothing = check_cstructname_and_cfuncprefix
    raises_AttributeError = raises(AttributeError)(raises_nothing)
    yield (raises_nothing, 'VectCalc', None)
    yield (raises_AttributeError, None, None)
    yield (raises_AttributeError, 'WrongClassName', None)
    yield (raises_AttributeError, 'VectCalc', 'WrongPrefix_')
    yield (raises_nothing, None, 'VectCalc_')


def check_empty_cfuncprefix(cfuncprefix):
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


def test_empty_cfuncprefix():
    raises_nothing = check_empty_cfuncprefix
    raises_AttributeError = raises(AttributeError)(raises_nothing)
    yield (raises_nothing, '')
    yield (raises_AttributeError, None)
