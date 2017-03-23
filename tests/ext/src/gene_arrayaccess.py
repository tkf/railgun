LIST_INDEX = 'ijklmnopqrstuvwxyz'

TEMPLATE_STRUCT = """\
typedef struct arrayaccess_{
  int %(num)s;

  %(ret)s

  %(arr)s
} ArrayAccess;
"""

TEMPLATE_GET = """\
int ArrayAccess_get_%(cdt)s%(dim)sd(ArrayAccess *self, %(args)s){
  self->ret_%(cdt)s = self->%(cdt)s%(dim)sd%(idx)s;
  return 0;
}
"""

NEWLINE_WITH_INDENT = "\n  "

_normal_ints = ['short', 'int', 'long']
CDT2CTYPE = dict(char='char')
CDT2CTYPE.update((c, c) for c in _normal_ints)
CDT2CTYPE.update(('u' + c, 'unsigned ' + c) for c in _normal_ints)
CDT2CTYPE.update(float='float', double='double', longdouble='long double',
                 longlong='long long', ulonglong='unsigned long long',
                 bool='bool', size_t='size_t')


def gene_idx(dim, l_idx):
    """
    >>> gene_idx(1, 'i')
    '[i]'
    >>> gene_idx(2, 'ij')
    '[i][j]'
    """
    return '[%s]' % ']['.join(l_idx[:dim])


def gene_idx_flat(dim, l_idx, prefix):
    """
    >>> gene_idx_flat(1, 'i', 'num_')
    '[i]'
    >>> gene_idx_flat(2, 'ij', 'num_')
    '[(i) * num_j + j]'
    >>> gene_idx_flat(3, 'ijk', 'num_')
    '[((i) * num_j + j) * num_k + k]'
    >>> gene_idx_flat(4, 'ijkl', 'num_')
    '[(((i) * num_j + j) * num_k + k) * num_l + l]'
    >>> gene_idx_flat(2, 'ijkl', 'num_')
    '[(i) * num_j + j]'
    """
    def idxexpr(dim, l_idx, prefix):
        if dim == 1:
            return l_idx[0]
        a = idxexpr(dim - 1, l_idx[:-1], prefix)
        z = l_idx[-1]
        return "(%(a)s) * %(p)s%(z)s + %(z)s" % dict(a=a, z=z, p=prefix)

    return "[%s]" % idxexpr(dim, l_idx[:dim], prefix)


def gene_array_declaration(l_cdt, l_dim):
    """
    >>> gene_array_declaration(['int', 'double'], [1, 2])
    ['int *int1d, **int2d;', 'double *double1d, **double2d;']
    """
    return ['%s %s;' % (CDT2CTYPE[cdt],
                        ', '.join('*' * dim + cdt + '%dd' % dim
                                  for dim in l_dim))
            for cdt in l_cdt]


def gene_array_declaration_flat(l_cdt, l_dim):
    """
    >>> gene_array_declaration_flat(['int', 'double'], [1, 2])
    ['int *int1d, *int2d;', 'double *double1d, *double2d;']
    """
    return ['%s %s;' % (CDT2CTYPE[cdt],
                        ', '.join('*' + cdt + '%dd' % dim for dim in l_dim))
            for cdt in l_cdt]


def gene_arrayaccess(filepath, nd, l_cdt, c99, carrtype=None):
    codefile = open(filepath, 'w')

    l_dim = range(1, 1 + nd)
    l_idx = LIST_INDEX[:nd]
    args_ = [', '.join('int %s' % i for i in l_idx[:dim]) for dim in l_dim]
    l_ret = ['%s ret_%s;' % (CDT2CTYPE[cdt], cdt) for cdt in l_cdt]
    if carrtype == "flat":
        idx_ = [gene_idx_flat(dim, l_idx, "self->num_") for dim in l_dim]
        l_arr = gene_array_declaration_flat(l_cdt, l_dim)
    else:
        idx_ = [gene_idx(dim, l_idx) for dim in l_dim]
        l_arr = gene_array_declaration(l_cdt, l_dim)
    # include
    codefile.write('#include <stdlib.h>\n')
    if c99:
        codefile.write('#include <stdbool.h>\n')
    codefile.write('\n')
    # generate typedef struct arrayaccess_{...} ArrayAccess;
    codefile.write(
        TEMPLATE_STRUCT % dict(
            num=', '.join('num_%s' % i for i in l_idx),
            ret=NEWLINE_WITH_INDENT.join(ret for ret in l_ret),
            arr=NEWLINE_WITH_INDENT.join(arr for arr in l_arr),
            ))
    codefile.writelines(['\n'] * 2)
    # generate ArrayAccess_get_*
    codefile.writelines(
        TEMPLATE_GET % dict(dim=dim, args=args_[i], idx=idx_[i], cdt=cdt)
        for cdt in l_cdt
        for (i, dim) in enumerate(l_dim)
        )


def main(filepath, c99, carrtype):
    nd = 5
    l_cdt = ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
             'float', 'double', 'longdouble', 'size_t']
    if c99:
        l_cdt += ['longlong', 'ulonglong', 'bool']
    gene_arrayaccess(filepath, nd, l_cdt, c99, carrtype)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--c99", default=False, action="store_true")
    parser.add_option("--carrtype")
    (opts, args) = parser.parse_args()
    filepath = args[0]
    main(filepath, opts.c99, opts.carrtype)
