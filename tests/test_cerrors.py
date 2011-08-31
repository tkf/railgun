from nose.tools import assert_raises # , raises, ok_, with_setup
from railgun import SimObject, relpath


class VectCalcBase(SimObject):
    _cstructname_ = 'VectCalc'
    _clibname_ = 'vectclac.so'
    _clibdir_ = relpath('ext/build', __file__)

    _cmembers_ = [
        'num_i = 10',
        'int v1[i] = 1',
        'int v2[i] = 2',
        'int v3[i]',
        'int ans',
        ]

    _cfuncs_ = [
        "vec_{op | plus, minus, times, divide}()",
        "subvec_{op | plus, minus, times, divide}(i i1=0, i< i2=num_i)",
        "fill_{vec | v1, v2, v3}(int s)",
        "ans subvec_dot(i i1=0, i< i2=num_i)",
        ]


def check_error(vc, exception):
    vc.v2.fill(1)
    # no error
    vc.vec(op='divide')
    vc.subvec(op='divide')
    # at least one 0 raises error
    vc.v2[-1] = 0
    # error will be raised
    assert_raises(exception, vc.vec, op='divide')
    assert_raises(exception, vc.subvec, op='divide')


def test_cerros_valueerror():

    class VectCalc(VectCalcBase):
        _cerrors_ = {
            1: ValueError('My error message'),
            100: RuntimeError('This error will not be raised'),
            }

    check_error(VectCalc(), ValueError)


def test_cerros_user_defined():

    class VectCalc(VectCalcBase):

        class UserDefinedError(Exception):
            pass

        _cerrors_ = {
            1: UserDefinedError('My error message'),
            100: RuntimeError('This error will not be raised'),
            }

    check_error(VectCalc(), VectCalc.UserDefinedError)
