import pytest

from railgun.simobj import CDT2CTYPE
from railgun.cdata import (
    RE_CDDEC, INT_LIKE_CDTS, cddec_idx_parse, cddec_parse, cmem)


def dict_re_cddec(cdt, vname, idx=None, default=None):
    return dict(cdt=cdt, vname=vname, idx=idx, default=default)

DATA_TEST_REGEX = dict(
    RE_CDDEC=(
        RE_CDDEC, [
            ("int a", dict_re_cddec('int', 'a')),
            ("int aA1", dict_re_cddec('int', 'aA1')),
            ("int a[i]", dict_re_cddec('int', 'a', '[i]')),
            ("int a[i][j]", dict_re_cddec('int', 'a', '[i][j]')),
            ("int a = 1", dict_re_cddec('int', 'a', None, '1')),
            ("int a[i] =2", dict_re_cddec('int', 'a', '[i]', '2')),
            ("int a[i][j]=3", dict_re_cddec('int', 'a', '[i][j]', '3')),
            ('num_i = 10', dict_re_cddec(None, 'num_i', None, '10')),
            ("double b = 1.0", dict_re_cddec('double', 'b', None, '1.0')),
            ] + list(
            ("double b = 1%s%s7" % (e, o),
             dict_re_cddec('double', 'b', None, '1%s%s7' % (e, o)))
            for e in ['E', 'e'] for o in ['', '+', '-']
            ),
        ),
    )


DATA_TEST_IDX = [
    ('[n]', ('n',)),
    ('[i][j]', ('i', 'j')),
    ('[abc][xyz][uvw]', ('abc', 'xyz', 'uvw')),
    ('', ()),
    ]


def dict_cdec_parse(cdt, vname, idx=(), ndim=0, default=None, valtype=None,
                    carrtype="iliffe"):
    if valtype is not None:
        return dict(cdt=cdt, vname=vname, valtype=valtype,
                    has_default=default is not None, carrtype=None)
    elif ndim == 0:
        valtype = 'scalar'
        carrtype = None
    elif ndim > 0:
        valtype = 'array'
    return dict(cdt=cdt, vname=vname, idx=idx, ndim=ndim, default=default,
                has_default=default is not None, valtype=valtype,
                carrtype=carrtype)


class DmyCDT(object):
    """Dummy Class for arbitrary C Data Type"""
    _ctype_ = None


DATA_TEST_CDEC_PARSE = [
    # (cdstr, correct)
    ("int a", dict_cdec_parse('int', 'a')),
    ("int aA1", dict_cdec_parse('int', 'aA1')),
    ("int a[i]", dict_cdec_parse('int', 'a', tuple('i'), 1)),
    ("int a[i][j]", dict_cdec_parse('int', 'a', tuple('ij'), 2)),
    ("int a[ i ][ j][k ]", dict_cdec_parse('int', 'a', tuple('ijk'), 3)),
    ("int a = 1", dict_cdec_parse('int', 'a', default=1)),
    ("int a[i] =2", dict_cdec_parse('int', 'a', tuple('i'), 1, 2)),
    ("int a[i][j]=3", dict_cdec_parse('int', 'a', tuple('ij'), 2, 3)),
    ("int a[i,j]", dict_cdec_parse('int', 'a', tuple('ij'), 2,
                                   carrtype="flat")),
    ("int a[i,j]=3", dict_cdec_parse('int', 'a', tuple('ij'), 2, 3,
                                     carrtype="flat")),
    ("int a[ i , j,k ]", dict_cdec_parse('int', 'a', tuple('ijk'), 3,
                                         carrtype="flat")),
    ('num_i = 10', dict_cdec_parse('int', 'num_i', default=10)),
    (cmem(DmyCDT, 'obj'), dict_cdec_parse(DmyCDT, 'obj', valtype='object')),
    ]


@pytest.mark.parametrize('regexname, regexobj, string, correct', [
    (regexname, regexobj, string, correct)
    for (regexname, (regexobj, checklist)) in DATA_TEST_REGEX.items()
    for (string, correct) in checklist
])
def test_regex(regexname, regexobj, string, correct):
    match = regexobj.match(string)
    if match:
        dct = match.groupdict()
        assert dct == correct, \
            "%s.match(%r) is not correct" % (regexname, string)
    else:
        assert correct is None, \
            ("%s.match(%r) should not be None\n"
             "desired = %r" % (regexname, string, correct))


@pytest.mark.parametrize('idxtr, dimtuple', DATA_TEST_IDX)
def test_cddec_idx_parse(idxtr, dimtuple):
    ret = cddec_idx_parse(idxtr)[0]
    assert ret == dimtuple, \
        'cddec_idx_parse(%r) = %r != %r' % (idxtr, ret, dimtuple)


@pytest.mark.parametrize('cdstr, correct', DATA_TEST_CDEC_PARSE)
def test_cddec_parse(cdstr, correct):
    ret = cddec_parse(cdstr)
    dct = ret.as_dict()
    assert dct == correct, 'cddec_parse(%s) returns incorrect value' % cdstr


def test_int_like_cdts():
    assert set(INT_LIKE_CDTS) < set(CDT2CTYPE)
