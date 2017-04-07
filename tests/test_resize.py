import pytest

from arrayaccess import DefaultArrayAccess


@pytest.mark.parametrize('idxs, pre, post', [
    ('i', (3,), (5,)),
    ('i', (5,), (3,)),
    ('ij', (3, 7), (5, 11)),
    ('ij', (5, 7), (3, 11)),
    ('ijk', (3, 7, 13), (5, 11, 17)),
    ('ijk', (5, 7, 13), (3, 11, 17)),
])
@pytest.mark.parametrize('in_place', [False, True, 'or_copy'])
def test_resize_resizes(idxs, pre, post, in_place):
    assert len(idxs) == len(pre) == len(post) <= DefaultArrayAccess.ndim
    num_names = ['num_' + i for i in idxs]
    pre_dict = dict(zip(num_names, pre))
    post_dict = dict(zip(idxs, post))
    aa = DefaultArrayAccess(**pre_dict)
    assert aa.arr("int", len(pre)).shape == pre
    try:
        aa.resize(post_dict, in_place=in_place)
    except ValueError:
        if in_place is True:
            return
        raise
    assert aa.arr("int", len(post)).shape == post
