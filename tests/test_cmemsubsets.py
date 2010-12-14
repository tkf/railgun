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
    dict(
        kwds=dict(
            data=dict(
                debug=dict(members=['x_debug_%d' % i for i in range(3)],
                           funcs=['f_{0, 1, 2}', 'g_{0, 1, 2}'],
                           default=False),
                ),
            cfuncs=['%s_%d' % (f, i) for f in 'fgh' for i in range(3)],
            cmems=['%s_%d' % (x, i)
                   for x in ('x', 'x_debug') for i in range(3)]),
        cases=[
            dict(flags=dict(debug=False),
                 cfuncs=dict([('%s_%d' % (f, i), f == 'h')
                              for f in 'fgh' for i in range(3)]),
                 cmems=dict([('%s_%d' % (x, i), x == 'x')
                             for x in ('x', 'x_debug') for i in range(3)])),
            dict(flags=dict(debug=True),
                 cfuncs=dict([('%s_%d' % (f, i), True)
                              for f in 'fgh' for i in range(3)]),
                 cmems=dict([('%s_%d' % (x, i), True)
                             for x in ('x', 'x_debug') for i in range(3)])),
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
            eq_(cmss.cfunc(name), desired,
                msg=('comparing cfuncs "%s" with falgs: %s' %
                     (name, case['flags'])))
        for (name, desired) in case['cmems'].iteritems():
            eq_(cmss.cmem(name), desired,
                msg=('comparing cmems "%s" with falgs: %s' %
                     (name, case['flags'])))


def test_cmemsubsets():
    for kwds in DATA_CMEMSUBSETS:
        yield (check_cmemsubsets, kwds)
