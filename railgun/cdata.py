import re

RE_CDDEC = re.compile(
    r'(?:(?P<cdt>[\w]+) )?(?P<vname>\w+)(?P<idx>\[.*\])?'
    r'(?: *= *(?P<default>[\w\.\-+]*))?$',
    )  ## matches 'int a[i][j] = 3'


class _CDataDeclaration(object):
    """
    A class to sotre parsed information of C-data declaration

    Attributes
    ----------
    cdt : str
        C Data Type
    vname : str
        variable name
    valtype : {'scalar', 'array', 'object'}
        type of the variable.
        'object' is not basic c type, but user-defined variable type
    idx : tuple of str
        e.g., `('i', 'j', 'k')` for 'a[i][j][k]'
    ndim : int
        this is `len(idx)`
    default : obj
        default value
    has_default : bool
        True if `default` is specified, False otherwise.
    carrtype : {'iliffe', 'flat'}
        'iliffe'
            array data structure is "Iliffe vector" or "display".
            you can access c array via `a[i][j]`.
            see: http://en.wikipedia.org/wiki/Iliffe_vector
        'flat'
            array data structure is flattened array or one dimensional
            array. you can access c array via `a[i * num_j + j]`.

    """

    def __init__(self):
        self.carrtype = None

    def as_dict(self):
        keys = ["cdt", "vname", "valtype", "idx", "ndim", "default",
                "has_default", "carrtype"]
        return dict((k, getattr(self, k)) for k in keys if hasattr(self, k))

    def _set_valtype_idx_ndim(self, idx):
        if idx:
            self.valtype = 'array'
            (self.idx, self.carrtype) = cddec_idx_parse(idx)
            self.ndim = len(self.idx)
        else:
            self.valtype = 'scalar'
            self.idx = ()
            self.ndim = 0

    def _set_default(self, default):
        if default:
            self.has_default = True
            self.default = eval(default)
        else:
            self.has_default = False
            self.default = None

    def _set_cdt_vname(self, cdt, vname):
        self.cdt = cdt
        self.vname = vname
        if vname.startswith('num_'):
            if not (cdt != 'int' or cdt is not None):
                raise ValueError ("type of '%s' should be int" % vname)
            self.cdt = 'int'

    @classmethod
    def from_string(cls, cdstr):
        """
        Parse declaration of C-data from a string
        """
        if not isinstance(cdstr, basestring) and iscmem(cdstr):
            return cdstr  # already parsed object
        cdstr = cdstr.strip()
        match = RE_CDDEC.match(cdstr)
        if match:
            return cls.from_groupdict(**match.groupdict())
        else:
            raise ValueError("%s is invalid as c-data type declaration" % cdstr)

    @classmethod
    def from_groupdict(cls, cdt, vname, idx, default):
        parsed = cls()
        parsed._set_cdt_vname(cdt, vname)
        parsed._set_valtype_idx_ndim(idx)
        parsed._set_default(default)
        return parsed

    @classmethod
    def from_cdtclass(cls, cdt, vname, **kwds):
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
        parsed = cls()
        parsed.cdt = cdt
        parsed.vname = vname
        parsed.valtype = 'object'
        if "default" in kwds:
            parsed.has_default = True
            parsed.default = kwds["default"]
        else:
            parsed.has_default = False
        return parsed


def cddec_idx_parse(idxtr):
    """Parse string like '[i][j]' to ('i', 'j')"""
    idxtr = idxtr.strip()
    if idxtr == '':
        return ((), None)
    else:
        stripped = idxtr.strip('[]')  # "i][j][k" or "i,j,k"
        if "," in stripped:
            return (tuple(s.strip() for s in stripped.split(",")), "flat")
        else:
            return (tuple(s.strip() for s in stripped.split('][')), "iliffe")


cddec_parse = _CDataDeclaration.from_string
cmem = _CDataDeclaration.from_cdtclass


def iscmem(cmem):
    return isinstance(cmem, _CDataDeclaration)
