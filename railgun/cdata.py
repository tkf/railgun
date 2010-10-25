import re
from railgun._helper import HybridObj

RE_CDDEC = re.compile(
    r'(?:(?P<cdt>[\w]+) )?(?P<vname>\w+)(?P<idx>\[.*\])?'
    r'(?: *= *(?P<default>[\w\.]*))?$',
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
    cdstr = cdstr.strip()
    match = RE_CDDEC.match(cdstr)
    if match:
        parsed = HybridObj(match.groupdict())
        if parsed.idx:
            parsed.idx = cddec_idx_parse(parsed.idx)
            parsed.ndim = len(parsed.idx)
        else:
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
