from nose.tools import ok_  #, raises, with_setup
## from pprint import pformat

from tsutils import eq_
from railgun.cdata import RE_CDDEC, cddec_idx_parse, cddec_parse, cmem


def dict_re_cddec(cdt, vname, idx=None, default=None):
    return dict(cdt=cdt, vname=vname, idx=idx, default=default)

DATA_TEST_REGEX = dict(
    RE_CDDEC = (
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


def dict_cdec_parse(cdt, vname, idx=(), ndim=0, default=None, valtype=None):
    if valtype is not None:
        return dict(cdt=cdt, vname=vname, valtype=valtype,
                    has_default=default is not None)
    elif ndim == 0:
        valtype = 'scalar'
    elif ndim > 0:
        valtype = 'array'
    return dict(cdt=cdt, vname=vname, idx=idx, ndim=ndim, default=default,
                has_default=default is not None, valtype=valtype)


class DmyCDT(object):
    """Dummy Class for arbitrary C Data Type"""
    _ctype_ = None


DATA_TEST_CDEC_PARSE = [
    # (cdstr, correct)
    ("int a", dict_cdec_parse('int', 'a')),
    ("int aA1", dict_cdec_parse('int', 'aA1')),
    ("int a[i]", dict_cdec_parse('int', 'a', tuple('i'), 1)),
    ("int a[i][j]", dict_cdec_parse('int', 'a', tuple('ij'), 2)),
    ("int a = 1", dict_cdec_parse('int', 'a', default=1)),
    ("int a[i] =2", dict_cdec_parse('int', 'a', tuple('i'), 1, 2)),
    ("int a[i][j]=3", dict_cdec_parse('int', 'a', tuple('ij'), 2, 3)),
    ('num_i = 10', dict_cdec_parse('int', 'num_i', default=10)),
    (cmem(DmyCDT, 'obj'), dict_cdec_parse(DmyCDT, 'obj', valtype='object')),
    ]


def check_regex(regexname, regexobj, string, correct):
    match = regexobj.match(string)
    if match:
        dct = match.groupdict()
        eq_(dct, correct,
            "%s.match(%r) is not correct" % (regexname, string))
    else:
        ok_(correct is None,
            msg=("%s.match(%r) should not be None\n"
                 "desired = %r" % (regexname, string, correct)
                 ))


def test_regex():
    for (regexname, (regexobj, checklist)) in DATA_TEST_REGEX.iteritems():
        for (string, correct) in checklist:
            yield (check_regex, regexname, regexobj, string, correct)


def check_cddec_idx_parse(idxtr, dimtuple):
    ret = cddec_idx_parse(idxtr)
    eq_(ret, dimtuple,
        msg='cddec_idx_parse(%r) = %r != %r' % (idxtr, ret, dimtuple))


def test_cddec_idx_parse():
    for (idxtr, dimtuple) in DATA_TEST_IDX:
        yield (check_cddec_idx_parse, idxtr, dimtuple)


def check_cddec_parse(cdstr, correct):
    ret = cddec_parse(cdstr)
    dct = ret.as_dict()
    eq_(dct, correct,
        msg='cddec_parse(%s) returns incorrect value' % cdstr)


def test_cddec_parse():
    for (cdstr, correct) in DATA_TEST_CDEC_PARSE:
        yield (check_cddec_parse, cdstr, correct)
