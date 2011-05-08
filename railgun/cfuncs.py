import re
from railgun._helper import iteralt, product

CJOINSTR = '_'

RE_CFDEC_FUNC = re.compile(
    r"(?:(?P<ret>[\w]+) )?(?P<fname>[^\( ][^\(]*)\((?P<args>[^\)]*)\)"
    )  # matches "ret func(a, b, c)" as "RET FNAME(ARGS)"
RE_CFDEC_CHOSET = re.compile(
    r"{ *(?P<key>[a-zA-Z]\w*) *\| *(?P<choices>[\w, ]+)}",
    )  # matches "{key | a, b, c}" as "{KEY | CHOICES}"
RE_CFDEC_CHOSET_SPLIT = re.compile(
    r"{[a-zA-Z]\w* *\| *[\w, ]+}",
    )  # matches "{key | a, b, c}", used for spliting function name
RE_CFDEC_ARG = re.compile(
    r"(?:(?P<cdt>[\w]*)(?P<ixt><)? )?"
    r"(?P<aname>\w+)(?: *= *(?P<default>[\w\.\-]+))?",
    )  # matches "int a=1" as "CDT NAME=DEFAULT"


class _CFunctionDeclaration(object):
    """
    A class to sotre parsed information of C-function declaration

    Attributes
    ----------
    ret : str or None
        returned value
    fname : str
        name of function
    choset : list of {'choices': [str], 'key': str}
        choice set
    args : list of {'aname': [str], 'default': obj, 'cdt': str}
        arguments
    fnget : (str, str, ...) -> str
        function name getter.
        it constructs C function name from given "choices".

    """

    def as_dict(self):
        keys = ["ret", "fname", "choset", "args", "fnget"]
        return dict((k, getattr(self, k)) for k in keys if hasattr(self, k))

    @classmethod
    def from_string(cls, cfstr):
        cfstr = cfstr.strip()  # "'ans' func_{k|a,b,c}(int a, i i=1)"

        match_func = RE_CFDEC_FUNC.match(cfstr)
        # ret="ans", fname="func_{k|a,b,c}", args="int a, i i=1"
        if match_func:
            return cls.from_groupdict(**match_func.groupdict())
        else:
            raise ValueError(
                "%s is invalid as c-function cdt declaration" % cfstr)

    @classmethod
    def from_groupdict(cls, ret, fname, args):
        parsed = cls()
        (fname, choset, fnget) = cfdec_fname_parse(fname)
        parsed.ret = ret
        parsed.fname = fname
        parsed.choset = choset
        parsed.args = cfdec_args_parse(args)
        parsed.fnget = fnget
        return parsed


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


cfdec_parse = _CFunctionDeclaration.from_string


def choice_combinations(cfdec):
    return product([c['choices'] for c in cfdec.choset])
