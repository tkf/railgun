import re
from itertools import product, izip_longest

from railgun._helper import strset


RE_BRACES = re.compile(r"{[\w, ]+}")


def altconcat(*args):
    """
    Returns ``[a00, a01, a02, ..., a10, a11, a12, ...]``

    >>> ''.join(altconcat('abc', 'ABC'))
    'aAbBcC'
    >>> ''.join(altconcat('abcd', 'ABC'))
    'aAbBcCd'
    >>> ''.join(altconcat('abc', 'ABCD'))
    'aAbBcCD'

    """
    skip = object()
    return [elem
            for lst in izip_longest(*args, fillvalue=skip)
            for elem in lst if elem is not skip]


def expand_braces(rawfname):
    """
    Expand braces taking product of sets of values inside of the braces

    >>> expand_braces('abc_{i,j,k}_def_{x,y}') #doctest: +NORMALIZE_WHITESPACE
    ['abc_i_def_x', 'abc_i_def_y',
     'abc_j_def_x', 'abc_j_def_y',
     'abc_k_def_x', 'abc_k_def_y']
    >>> expand_braces('abc_{ i, j, k }') #doctest: +NORMALIZE_WHITESPACE
    ['abc_i', 'abc_j', 'abc_k']

    """
    braces = RE_BRACES.findall(rawfname)
    remainings = RE_BRACES.split(rawfname)
    cholist = [  # list of "choice list" (from comma separated words)
        [word.strip() for word in br[1:-1].split(',') if not word.isspace()]
        for br in braces]
    return [''.join(altconcat(remainings, cho)) for cho in product(*cholist)]


def concatfunc(func, lst):
    """
    Concatenate returned list of `func(elem)` for `elem` in `lst`
    """
    ret = []
    for elem in lst:
        ret += func(elem)
    return ret


def _cmss_inverse(cmss, key):
    """
    Returns "inverse" dictionary of `cmss` (dict-of-dict-of-list)

    Let `cmss` is (in JSON format)::

        { name1: { cfuncs: [f, g, h], cmems: [x, y] },
          name2: { cfuncs: [f, j, k], cmems: [y, z] } }

    Then `_cmss_inverse(cmss, 'cfuncs')` returns::

        { f: [name1, name2], g: [name1], h: [name1], j: [name2], k: [name2] }

    and `_cmss_inverse(cmss, 'cmems')` returns::

        { x: [name1], y: [name1, name2], z: [name2] }

    Note that although it is written as list, list of "cmss name" above
    is actually set.

    Examples
    --------
    >>> cmss = dict(
    ...     name1=dict(cfuncs=['f', 'g', 'h'], cmems=['x', 'y']),
    ...     name2=dict(cfuncs=['f', 'j', 'k'], cmems=['y', 'z']),
    ...     )
    >>> cfuncs = _cmss_inverse(cmss, 'cfuncs')
    >>> sorted(cfuncs['f'])
    ['name1', 'name2']
    >>> sorted(cfuncs['g'])
    ['name1']
    >>> sorted(cfuncs['j'])
    ['name2']

    """
    inv = {}
    for (cmss_name, mfd) in cmss.iteritems():
        for var in mfd[key]:
            if var in inv:
                var_cmss_set = inv[var]
            else:
                var_cmss_set = set()
                inv[var] = var_cmss_set
            var_cmss_set.add(cmss_name)
    return inv


class CMemSubSets(object):
    """C Member Sub-Sets"""

    def __init__(self, data=None, cfuncs=None, cmems=None):
        if data is None:
            data = {}
        else:
            cfuncs = set(cfuncs)
            cmems = set(cmems)
        cmss = {}
        for (name, mfd) in data.iteritems():
            # mfd: members, funcs, default
            mfd_parsed = dict(
                cfuncs=mfd['funcs'],
                cmems=mfd['members'],
                default=mfd['default'],
                cfuncs_parsed=concatfunc(expand_braces, mfd['funcs']),
                on=mfd['default'],
                )
            setdiff_mems = set(mfd_parsed['cmems']) - cmems
            setdiff_funcs = set(mfd_parsed['cfuncs_parsed']) - cfuncs
            if setdiff_mems:
                raise ValueError(
                    'C-members %s of subset "%s" are not '
                    'recognized' % (strset(setdiff_mems), name))
            if setdiff_funcs:
                raise ValueError(
                    'C-funcs %s of subset "%s" are not '
                    'recognized' % (strset(setdiff_funcs), name))
            cmss[name] = mfd_parsed
        self._cmss_ = cmss
        self._cfunc_to_cmss_ = _cmss_inverse(cmss, 'cfuncs_parsed')
        self._cmem_to_cmss_ = _cmss_inverse(cmss, 'cmems')

    def copy(self):
        cmssnew = self.__class__()
        cmssnew._cmss_ = self._cmss_.copy()
        cmssnew._cfunc_to_cmss_ = self._cfunc_to_cmss_.copy()
        cmssnew._cmem_to_cmss_ = self._cmem_to_cmss_.copy()
        return cmssnew

    def set(self, **kwds):
        """Set flags of c member subset"""
        for (name, val) in kwds.iteritems():
            self._cmss_[name]['on'] = val

    def get(self, *args):
        """Get flags given names of c member subset"""
        ret = [self._cmss_[name]['on'] for name in args]
        if len(ret) == 1:
            return ret[0]
        else:
            return ret

    def cfunc_is_callable(self, name):
        """
        Check if given c-function is callable

        Returned value is True if all flag is on or `name` is not in
        any c member subset, otherwise False.

        For c function to be callable, *all* falg are needed to be on
        otherwise given c function might use unallocated members.

        """
        if name in self._cfunc_to_cmss_:
            cmss = self._cmss_
            return all(cmss[k]['on'] for k in self._cfunc_to_cmss_[name])
        else:
            return True

    def cmem_need_alloc(self, name):
        """
        Check if given c-member should be allocated

        True if at least one flag is on, otherwise False

        """
        if name in self._cmem_to_cmss_:
            cmss = self._cmss_
            return any(cmss[k]['on'] for k in self._cmem_to_cmss_[name])
        else:
            return True
