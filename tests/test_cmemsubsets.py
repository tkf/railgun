# from nose.tools import raises, ok_, with_setup

from tsutils import eq_
from railgun.cmemsubsets import CMemSubSets


DATA_CMEMSUBSETS = [
    dict(
        kwds=dict(
            data=dict(
                vec=dict(members=['v1', 'v2', 'v3'],
                         funcs=['vec_{plus, minus, times, divide}',
                                'subvec_{plus, minus, times, divide}',
                                'fill_{v1, v2, v3}'],
                         default=False),
                dot=dict(members=['v1', 'v2'],
                         funcs=['subvec_dot'],
                         default=True),
                ),
            cfuncs=(
                ['%s_%s' % (pre, op) for pre in ['vec', 'subvec']
                 for op in ['plus', 'minus', 'times', 'divide']] +
                ['fill_v%d' % i for i in [1, 2, 3]] +
                ['subvec_dot']),
            cmems=['num_i', 'v1', 'v2', 'v3']),
        cases=[
            dict(flags=dict(vec=True, dot=False),
                 cfuncs=dict(vec_plus=True, fill_v1=True, subvec_dot=False),
                 cmems=dict(v1=True, v2=True, v3=True)),
            dict(flags=dict(vec=False, dot=False),
                 cfuncs=dict(vec_plus=False, fill_v1=False, subvec_dot=False),
                 cmems=dict(v1=False, v2=False, v3=False)),
            dict(flags=dict(vec=False, dot=True),
                 cfuncs=dict(vec_plus=False, fill_v1=False, subvec_dot=True),
                 cmems=dict(v1=True, v2=True, v3=False))
            ]
        ),
    ]


def check_cmemsubsets(data):
    kwds = data['kwds']
    cmss = CMemSubSets(**kwds)

    for name in kwds['data']:
        eq_(cmss.get(name), kwds['data'][name].get('default', False),
            msg='comparing default value of flag "%s"' % name)

    for case in data['cases']:
        cmss.set(**case['flags'])
        for (name, desired) in case['cfuncs'].iteritems():
            eq_(cmss.cfunc(name), desired)
        for (name, desired) in case['cmems'].iteritems():
            eq_(cmss.cmem(name), desired)


def test_cmemsubsets():
    for kwds in DATA_CMEMSUBSETS:
        yield (check_cmemsubsets, kwds)
