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
    Expand braces taking product of sets

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


class CMemSubSets(object):

    def __init__(self, data, cfuncs, cmems):
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

    def set(self, **kwds):
        """Set flags"""
        for (name, val) in kwds.iteritems():
            self._cmss_[name]['on'] = val

    def get(self, *args):
        """Get flags"""
        ret = [self._cmss_[name]['on'] for name in args]
        if len(ret) == 1:
            return ret[0]
        else:
            return ret

    def cfunc(self, name):
        """
        Check c-function's flag: True if all flag is on, otherwise False
        """
        for mfd in self._cmss_.itervalues():
            if name in mfd['cfuncs_parsed'] and not mfd['on']:
                return False
        return True

    def cmem(self, name):
        """
        Check c-member's flag: True if at least one flag is on, otherwise False
        """
        for mfd in self._cmss_.itervalues():
            if name in mfd['cmems'] and mfd['on']:
                return True
        return False
