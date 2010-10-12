from nose.tools import ok_  # , raises, with_setup

from tsutils import eq_
from railgun.cfuncs import (
    cfdec_parse, RE_CFDEC_FUNC, RE_CFDEC_CHOSET, RE_CFDEC_ARG,
    choice_combinations)
from railgun._helper import subdict


def cor_arg(cdt, aname, default=None, ixt=None):
    return dict(cdt=cdt, aname=aname, default=default, ixt=ixt)

DATA_TEST_REGEX = dict(
    RE_CFDEC_FUNC=(
        RE_CFDEC_FUNC, [
            ("ans func(a, b, c)",
             dict(ret="ans", fname="func", args="a, b, c")),
            ("func(a, b, c)",
             dict(ret=None, fname="func", args="a, b, c")),
            ("f()",
             dict(ret=None, fname="f", args='')),
            ("int func(double a, int b=1, i< i0=num_i)",
             dict(ret="int", fname="func",
                  args="double a, int b=1, i< i0=num_i")),
            ("func_{k1|x,y,z}_{k2 | alpha, beta, gamma}(a, b, c)",
             dict(ret=None,
                  fname="func_{k1|x,y,z}_{k2 | alpha, beta, gamma}",
                  args="a, b, c")),
            ],
        ),
    RE_CFDEC_CHOSET=(
        RE_CFDEC_CHOSET, [
            ("{key | a, b, c }",
             dict(key='key', choices='a, b, c ')),
            ("{key|a,b,c}",
             dict(key='key', choices='a,b,c')),
            ],
        ),
    RE_CFDEC_ARG=(
        RE_CFDEC_ARG, [
            ("int a=1", cor_arg('int', 'a', '1' )),
            ("a=1",     cor_arg(None,  'a', '1' )),
            ("int a",   cor_arg('int', 'a')),
            ("a",       cor_arg(None,  'a')),
            ("i a=1",   cor_arg('i',   'a', '1' )),
            ("i< a=1",  cor_arg('i',   'a', '1', '<')),
            ],
        ),
    )

DATA_CFDEC_PARSE = [
    # (cfstr, correct, fnameargslist)
    ("ans func(int a, i< b=0, double c=2.0)",
     dict(ret="ans", fname="func",
          args=[cor_arg('int', 'a'),
                cor_arg('i', 'b', '0', '<'),
                cor_arg('double', 'c', '2.0'),
                ],
          choset=[
              ],
          ),
     [('func', ())],
     ),
    ("func_{k1|x,y,z}_{k2 | alpha, beta, gamma}(int i)",
     dict(ret=None, fname="func",
          args=[cor_arg('int', 'i'),
                ],
          choset=[
              dict(key='k1', choices=['x', 'y', 'z']),
              dict(key='k2', choices=['alpha', 'beta', 'gamma']),
              ],
          ),
     [('func_%s_%s' % (k1, k2), (k1, k2))
      for k1 in ['x', 'y', 'z'] for k2 in ['alpha', 'beta', 'gamma']],
     ),
    ]


def check_regex(regexname, regexobj, string, correct):
    match = regexobj.match(string)
    if match:
        dct = match.groupdict()
        eq_(dct, correct, "%s.match(%r) is not correct" % (regexname, string))
    else:
        ok_(correct is None,
            msg=("%s.match(%r) should not be None\n"
                 "desired = %r" % (regexname, string, correct)))


def test_regex():
    for (regexname, (regexobj, checklist)) in DATA_TEST_REGEX.iteritems():
        for (string, correct) in checklist:
            yield (check_regex, regexname, regexobj, string, correct)


def check_cfdec_parse(cfstr, correct, fnameargslist):
    ret = cfdec_parse(cfstr)
    dct = subdict(ret(), *list(correct))  # exclude 'fnget'
    fnget = ret.fnget
    eq_(correct, dct, 'incorrect return for "%s"' % (cfstr))
    for (fname, args) in fnameargslist:
        fname_ret = fnget(*args)
        eq_(fname_ret, fname,
            '%s%s returns incorrect name' % (ret.fnget.func_name, args))


def test_cfdec_parse():
    for (cfstr, correct, fnameargslist) in DATA_CFDEC_PARSE:
        yield (check_cfdec_parse, cfstr, correct, fnameargslist)


def check_choice_combinations(cfstr, fnameargslist):
    cfdec = cfdec_parse(cfstr)
    clist = [tuple(c) for c in choice_combinations(cfdec)]
    ret = set(clist)
    ok_(len(ret) == len(clist),
        'choice_combinations returns redundant element(s)')
    correct = set(fa[1] for fa in fnameargslist)
    eq_(ret, correct, ('choice_combinations(cfdec_parse(%s)) '
                       'returns incorrect value' % cfstr))


def test_choice_combinations():
    for (cfstr, correct, fnameargslist) in DATA_CFDEC_PARSE:
        yield (check_choice_combinations, cfstr, fnameargslist)
