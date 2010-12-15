"""
Helper/utility functions and classes
"""


class HybridObj(object):
    """
    Object-Dict Hybrid. Access attributes via ``obj.a`` or ``obj['a']``.

    This is originally from [Common_Python_Patterns]_.

    .. [Common_Python_Patterns]
       http://karamatli.com/pages/lang/Common_Python_Patterns/

    Usage
    -----
    >>> obj = HybridObj()
    >>> obj['mykey'] = 'myval'
    >>> obj.mykey
    'myval'
    >>> obj()
    {'mykey': 'myval'}
    >>> 'mykey' in obj
    True
    >>> '__init__' in obj
    False
    >>> list(obj)
    [('mykey', 'myval')]
    >>> len(obj)
    1
    >>> del obj['mykey']
    >>> len(obj)
    0
    >>> obj.mykey = 'anotherval'
    >>> obj['mykey']
    'anotherval'
    >>> del obj.mykey
    >>> len(obj)
    0

    """
    def __init__(self, *args, **kwds):
        self.__dict__ = dict(*args, **kwds)

    def __getitem__(self, name):
        return self.__dict__[name]

    def __setitem__(self, name, value):
        self.__dict__[name] = value

    def __call__(self, *args, **kwds):
        self.__dict__.update(*args, **kwds)
        return self.__dict__

    def __iter__(self):
        return self.__dict__.iteritems()

    def __delitem__(self, x):
        return self.__dict__.__delitem__(x)

    def __contains__(self, x):
        return self.__dict__.__contains__(x)

    def __len__(self):
        return self.__dict__.__len__()


def _parse_csk_args(args):
    """
    Parse comma separated argument (helper function for `get_subdict` etc.)

    >>> _parse_csk_args(('a', 'b'))
    ('a', 'b')
    >>> _parse_csk_args(('a, b',))
    ('a', 'b')

    """
    if len(args) == 1 and hasattr(args[0], 'find') and args[0].find(',') != -1:
        # args = ['a, b, c']
        return tuple([k.strip() for k in args[0].split(',')])
    else:
        # args = ['a', 'b', 'c']
        return tuple(args)


def subdict(d, *args):
    """
    Get sub-dictionary (parts of dictionary) with specified keys.

    Usage
    >>> d = dict(a=1, b=2, d=3, e=4)
    >>> subdict(d, 'a', 'b')
    {'a': 1, 'b': 2}
    >>> subdict(d, 'a, b')
    {'a': 1, 'b': 2}

    """
    keys = _parse_csk_args(args)
    return dict([(k, d[k]) for k in keys])


def valbykey(d, *args):
    """
    Get tuple of values of dictionary with specified keys.

    Usage
    >>> d = dict(a=1, b=2, d=3, e=4)
    >>> valbykey(d, 'a', 'b')
    (1, 2)
    >>> valbykey(d, 'a, b')
    (1, 2)

    """
    keys = _parse_csk_args(args)
    return tuple([d[k] for k in keys])


def subdict_by_prefix(dct, prefix, remove_prefix=True, remove_original=False):
    """
    Construct sub-dictionary from `dct` whose key starts with `prefix`

    >>> dct = dict(a_1=2, a_3=4, a_k=5, a=0, b_0=2)
    >>> subdict_by_prefix(dct, 'a_')['1']
    2
    >>> sorted(subdict_by_prefix(dct, 'a_'))
    ['1', '3', 'k']
    >>> sorted(subdict_by_prefix(dct, 'a_', remove_prefix=False))
    ['a_1', 'a_3', 'a_k']
    >>> sorted(subdict_by_prefix(dct, 'a_', remove_original=True))
    ['1', '3', 'k']
    >>> sorted(dct)
    ['a', 'b_0']

    """
    if remove_prefix:
        len_prefix = len(prefix)
        getkey = lambda k: k[len_prefix:]
    else:
        getkey = lambda k: k
    keylist = [k for k in dct if k.startswith(prefix)]
    subdict = dict((getkey(k), dct[k]) for k in keylist)
    if remove_original:
        for k in keylist:
            del dct[k]
    return subdict


def subdict_by_filter(dct, func, remove_original=False):
    """
    Construct sub-dictionary from `dct` for which func(key) is true

    >>> dct = dict(a_1=2, a_3=4, a_k=5, a=0, b_0=2)
    >>> sorted(subdict_by_filter(dct, lambda x: x.startswith('a_')))
    ['a_1', 'a_3', 'a_k']
    >>> sorted(subdict_by_filter(dct, lambda x: x.startswith('a_'),
    ...                          remove_original=True))
    ['a_1', 'a_3', 'a_k']
    >>> sorted(dct)
    ['a', 'b_0']

    """
    keylist = filter(func, dct)
    subdict = dict((k, dct[k]) for k in keylist)
    if remove_original:
        for k in keylist:
            del dct[k]
    return subdict


def iteralt(l1, l2):
    """
    Iterate two sequences alternately

    >>> list(iteralt([0, 2, 4], [1, 3]))
    [0, 1, 2, 3, 4]
    >>> list(iteralt([0, 2, 4], [1, 3, 5]))
    [0, 1, 2, 3, 4, 5]
    >>> list(iteralt([0, 2, 4, 6], [1, 3]))
    [0, 1, 2, 3, 4]

    """
    i = 0
    j = 0
    try:
        while True:
            yield l1[i]
            yield l2[j]
            i += 1
            j += 1
    except IndexError:
        pass


def product(lists):
    """
    Get product of given list of list (iterative of iterative).

    >>> product([['x', 'y'], [1, 2]])
    [['x', 1], ['x', 2], ['y', 1], ['y', 2]]
    >>> p = product(['ABCD', 'xyz', 'uvw'])
    >>> len(p)
    36
    >>> p[0]
    ['A', 'x', 'u']
    >>> p[1]
    ['A', 'x', 'v']
    >>> p[2]
    ['A', 'x', 'w']

    """
    return reduce(
        lambda prod, list: [x + [y] for x in prod for y in list],
        lists, [[]])


def dict_override(default, override, addkeys=False):
    """
    Get a new dictionary with default values which is updated by `override`

    >>> default = dict(a=1, b=2, c=3)
    >>> newdict = dict_override(default, dict(c=100))
    >>> newdict['c']
    100
    >>> newdict = dict_override(default, dict(a=100, D=0))
    >>> valbykey(newdict, 'a, b, c')
    (100, 2, 3)
    >>> 'D' in newdict
    False
    >>> newdict = dict_override(default, dict(D=4), addkeys=True)
    >>> valbykey(newdict, 'a, b, c, D')
    (1, 2, 3, 4)
    >>> newdict = dict_override(default, {})
    >>> default is not newdict
    True
    >>> default == newdict
    True

    """
    if not addkeys:
        override = dict(
            (k, v) for (k, v) in override.iteritems() if k in default)
    copy = default.copy()
    copy.update(override)
    return copy


def strset(s):
    """Get string like '{a, b, c}' from iterative of string"""
    return '{%s}' % ', '.join(s)
