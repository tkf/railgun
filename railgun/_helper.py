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
    if len(args) == 1 and hasattr(args[0], 'find') and args[0].find(',') != -1:
        # args = ['a, b, c']
        keys = [k.strip() for k in args[0].split(',')]
    else:
        # args = ['a', 'b', 'c']
        keys = args

    return dict([(k, d[k]) for k in keys])


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
