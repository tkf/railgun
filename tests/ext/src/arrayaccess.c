typedef struct arrayaccess_{
  int num_i, num_j, num_k, num_l, num_m;
  int ret_int;
  double ret_double;
  int *int1d, **int2d, ***int3d, ****int4d, *****int5d;
  double *double1d, **double2d, ***double3d, ****double4d, *****double5d;
} ArrayAccess;

/*[[[cog
import cog

template = """\
int ArrayAccess_get_%(cdt)s%(dim)sd(ArrayAccess *self, %(args)s){
  self->ret_%(cdt)s = self->%(cdt)s%(dim)sd%(idx)s;
  return 0;
}
"""
l_dim = range(1, 6)
l_idx = 'ijklm'
args_ = [', '.join('int %s' % i for i in l_idx[:dim]) for dim in l_dim]
idx_ = ['[%s]' % ']['.join(l_idx[:dim]) for dim in l_dim]
l_cdt = ['int', 'double']

for cdt in l_cdt:
    for (i, dim) in enumerate(l_dim):
        cog.outl(template % dict(dim=dim, args=args_[i], idx=idx_[i],
                                 cdt=cdt))
]]]*/
int ArrayAccess_get_int1d(ArrayAccess *self, int i){
  self->ret_int = self->int1d[i];
  return 0;
}

int ArrayAccess_get_int2d(ArrayAccess *self, int i, int j){
  self->ret_int = self->int2d[i][j];
  return 0;
}

int ArrayAccess_get_int3d(ArrayAccess *self, int i, int j, int k){
  self->ret_int = self->int3d[i][j][k];
  return 0;
}

int ArrayAccess_get_int4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_int = self->int4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_int5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_int = self->int5d[i][j][k][l][m];
  return 0;
}

int ArrayAccess_get_double1d(ArrayAccess *self, int i){
  self->ret_double = self->double1d[i];
  return 0;
}

int ArrayAccess_get_double2d(ArrayAccess *self, int i, int j){
  self->ret_double = self->double2d[i][j];
  return 0;
}

int ArrayAccess_get_double3d(ArrayAccess *self, int i, int j, int k){
  self->ret_double = self->double3d[i][j][k];
  return 0;
}

int ArrayAccess_get_double4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_double = self->double4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_double5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_double = self->double5d[i][j][k][l][m];
  return 0;
}

/*[[[end]]]*/
