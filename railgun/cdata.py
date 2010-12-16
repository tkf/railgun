import re
from railgun._helper import HybridObj

RE_CDDEC = re.compile(
    r'(?:(?P<cdt>[\w]+) )?(?P<vname>\w+)(?P<idx>\[.*\])?'
    r'(?: *= *(?P<default>[\w\.\-+]*))?$',
    )  ## matches 'int a[i][j] = 3'


def cddec_idx_parse(idxtr):
    """Parse string like '[i][j]' to ('i', 'j')"""
    idxtr = idxtr.strip()
    if idxtr == '':
        return ()
    else:
        return tuple(idxtr.strip('[]').split(']['))


def cddec_parse(cdstr):
    """
    Parse declaration of data from a string
    """
    if not isinstance(cdstr, basestring) and iscmem(cdstr):
        return cdstr  # already parsed object
    cdstr = cdstr.strip()
    match = RE_CDDEC.match(cdstr)
    if match:
        parsed = HybridObj(match.groupdict())
        if parsed.idx:
            parsed.valtype = 'array'
            parsed.idx = cddec_idx_parse(parsed.idx)
            parsed.ndim = len(parsed.idx)
        else:
            parsed.valtype = 'scalar'
            parsed.idx = ()
            parsed.ndim = 0
        if parsed.vname.startswith('num_'):
            if not (parsed.cdt != 'int' or parsed.cdt is not None):
                raise ValueError ("type of '%s' should be int" % parsed.vname)
            parsed.cdt = 'int'
        if parsed.default:
            parsed.has_default = True
            parsed.default = eval(parsed.default)
        else:
            parsed.has_default = False
        return parsed
    else:
        raise ValueError("%s is invalid as c-data type declaration" % cdstr)


def cmem(cdt, vname, **kwds):
    """
    Declaration of C member

    Parameters
    ----------
    cdt : class
        This class must have the following two attributes

        _ctype_ : ctype
            It will be used for field of `SimObject._struct_`
            (subclass of `ctypes.Structure`).
            It must be an attribute of the *class* `cdt`,
            ie., accessible via `cdt._ctype_`.
        _cdata_ : data
            It will be passed to `SimObject._struct_`
            (instance of `ctypes.Structure` subclass).
            This is required only for instance of the class, so that
            you can set this in `cdt.__init__`.
    vname : str
        Name of C member

    """
    if not hasattr(cdt, '_ctype_'):
        raise ValueError('%r (cdt of %s) does not have _ctype_ '
                         'attribute' % (cdt, vname))
    parsed = HybridObj(vname=vname, cdt=cdt, valtype='object', **kwds)
    if 'default' in parsed:
        parsed.has_default = True
    else:
        parsed.has_default = False
    return parsed


def iscmem(cmem):
    return (hasattr(cmem, 'vname') and
            hasattr(cmem, 'cdt') and
            hasattr(cmem, 'has_default'))
