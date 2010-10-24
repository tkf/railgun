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
CDT2CTYPE.update(float='float', double='double', longdouble='long double')


def gene_arrayaccess(filepath, nd, l_cdt):
    codefile = file(filepath, 'w')

    l_dim = range(1, 1 + nd)
    l_idx = LIST_INDEX[:nd]
    args_ = [', '.join('int %s' % i for i in l_idx[:dim]) for dim in l_dim]
    idx_ = ['[%s]' % ']['.join(l_idx[:dim]) for dim in l_dim]
    l_ret = ['%s ret_%s;' % (CDT2CTYPE[cdt], cdt) for cdt in l_cdt]
    l_arr = [
        '%s %s;' % (
            CDT2CTYPE[cdt],
            ', '.join('*' * dim + cdt + '%dd' % dim for dim in l_dim))
        for cdt in l_cdt]
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


def main(filepath):
    nd = 5
    l_cdt = ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
             'float', 'double', 'longdouble']
    gene_arrayaccess(filepath, nd, l_cdt)


if __name__ == '__main__':
    import sys
    filepath = sys.argv[1]
    main(filepath)
