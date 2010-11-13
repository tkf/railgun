import re
from railgun._helper import HybridObj, iteralt, product

CJOINSTR = '_'

RE_CFDEC_FUNC = re.compile(
    r"(?:(?P<ret>[\w]+) )?(?P<fname>[^\( ][^\(]*)\((?P<args>[^\)]*)\)"
    )  # matches "ret func(a, b, c)" as "RET FNAME(ARGS)"
RE_CFDEC_CHOSET = re.compile(
    r"{(?P<key>[a-zA-Z]\w*) *\| *(?P<choices>[\w, ]+)}",
    )  # matches "{key | a, b, c}" as "{KEY | CHOICES}"
RE_CFDEC_CHOSET_SPLIT = re.compile(
    r"{[a-zA-Z]\w* *\| *[\w, ]+}",
    )  # matches "{key | a, b, c}", used for spliting function name
RE_CFDEC_ARG = re.compile(
    r"(?:(?P<cdt>[\w]*)(?P<ixt><)? )?"
    r"(?P<aname>\w+)(?: *= *(?P<default>[\w\.\-]+))?",
    )  # matches "int a=1" as "CDT NAME=DEFAULT"


def cfdec_args_parse(args):
    """Parse cfdec argument like this: 'int a=1, float x=2.0'"""
    parsed = []
    for a in args.split(','):
        a = a.strip()
        if a != '':
            match = RE_CFDEC_ARG.match(a)
            if match:
                parsed.append(match.groupdict())
            else:
                raise ValueError (
                    '%r in %r does not match to argument pattern' % (a, args))
    return parsed


def cfdec_fname_parse(rawfname):
    """Parse cfdec function name like this: 'func_{k|a,b,c}'"""
    fname_remain = RE_CFDEC_CHOSET.sub('', rawfname)
    fname = CJOINSTR.join(
        f for f in fname_remain.split(CJOINSTR) if f != '')
    choset = []
    for (key, chostr) in RE_CFDEC_CHOSET.findall(rawfname):
        choset.append(
            dict(key=key,
                 choices=[x.strip() for x in chostr.split(',')],
                 ))

    fsplit = RE_CFDEC_CHOSET_SPLIT.split(rawfname)
    def fnget(*args):
        choicelist = args
        return ''.join(iteralt(fsplit, choicelist))
    fnget.func_name = 'fnget_%s' % fname

    return (fname, choset, fnget)


def cfdec_parse(cfstr):
    """
    Parse declaration of a function

    Given declaration of a function,::

        ret func_{k1|x,y,z}_...(int a, ...)

    this function returns dict like this::

        {'args': [{'aname': 'a', 'default': None, 'cdt': 'int'},
                  ...],
         'choset': [{'choices': ['x', 'y', 'z'], 'key': 'k1'},
                     ...],
         'fname': 'func',
         'fnget': <function fnget_func at XXXXXXXXX>
         'ret': 'ret'}

    """
    cfstr = cfstr.strip()  # "'ans' func_{k|a,b,c}(int a, i i=1)"

    match_func = RE_CFDEC_FUNC.match(cfstr)
    if match_func:
        parsed = HybridObj(match_func.groupdict())
        ## ret="ans", fname="func_{k|a,b,c}", args="int a, i i=1"
    else:
        raise ValueError(
            "%s is invalid as c-function cdt declaration" % cfstr)

    (fname, choset, fnget) = cfdec_fname_parse(parsed.fname)
    parsed.fname = fname
    parsed.choset = choset
    parsed.args = cfdec_args_parse(parsed.args)
    parsed.fnget = fnget

    return parsed


def choice_combinations(cfdec):
    return product([c['choices'] for c in cfdec['choset']])
