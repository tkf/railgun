typedef struct arrayaccess_{
  int num_i, num_j, num_k, num_l, num_m;

  char ret_char;
  short ret_short; unsigned short ret_ushort;
  int ret_int; unsigned int ret_uint;
  long ret_long; unsigned long ret_ulong;
  float ret_float; double ret_double; long double ret_longdouble;

  char *char1d, **char2d, ***char3d, ****char4d, *****char5d;
  short *short1d, **short2d, ***short3d, ****short4d, *****short5d;
  unsigned short *ushort1d, **ushort2d, ***ushort3d, ****ushort4d,
    *****ushort5d;
  int *int1d, **int2d, ***int3d, ****int4d, *****int5d;
  unsigned int *uint1d, **uint2d, ***uint3d, ****uint4d, *****uint5d;
  long *long1d, **long2d, ***long3d, ****long4d, *****long5d;
  unsigned long *ulong1d, **ulong2d, ***ulong3d, ****ulong4d, *****ulong5d;

  float *float1d, **float2d, ***float3d, ****float4d, *****float5d;
  double *double1d, **double2d, ***double3d, ****double4d, *****double5d;
  long double *longdouble1d, **longdouble2d, ***longdouble3d,
    ****longdouble4d, *****longdouble5d;
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
l_cdt = ['char', 'short', 'ushort', 'int', 'uint', 'long', 'ulong',
         'float', 'double', 'longdouble']

for cdt in l_cdt:
    for (i, dim) in enumerate(l_dim):
        cog.outl(template % dict(dim=dim, args=args_[i], idx=idx_[i],
                                 cdt=cdt))
]]]*/
int ArrayAccess_get_char1d(ArrayAccess *self, int i){
  self->ret_char = self->char1d[i];
  return 0;
}

int ArrayAccess_get_char2d(ArrayAccess *self, int i, int j){
  self->ret_char = self->char2d[i][j];
  return 0;
}

int ArrayAccess_get_char3d(ArrayAccess *self, int i, int j, int k){
  self->ret_char = self->char3d[i][j][k];
  return 0;
}

int ArrayAccess_get_char4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_char = self->char4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_char5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_char = self->char5d[i][j][k][l][m];
  return 0;
}

int ArrayAccess_get_short1d(ArrayAccess *self, int i){
  self->ret_short = self->short1d[i];
  return 0;
}

int ArrayAccess_get_short2d(ArrayAccess *self, int i, int j){
  self->ret_short = self->short2d[i][j];
  return 0;
}

int ArrayAccess_get_short3d(ArrayAccess *self, int i, int j, int k){
  self->ret_short = self->short3d[i][j][k];
  return 0;
}

int ArrayAccess_get_short4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_short = self->short4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_short5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_short = self->short5d[i][j][k][l][m];
  return 0;
}

int ArrayAccess_get_ushort1d(ArrayAccess *self, int i){
  self->ret_ushort = self->ushort1d[i];
  return 0;
}

int ArrayAccess_get_ushort2d(ArrayAccess *self, int i, int j){
  self->ret_ushort = self->ushort2d[i][j];
  return 0;
}

int ArrayAccess_get_ushort3d(ArrayAccess *self, int i, int j, int k){
  self->ret_ushort = self->ushort3d[i][j][k];
  return 0;
}

int ArrayAccess_get_ushort4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_ushort = self->ushort4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_ushort5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_ushort = self->ushort5d[i][j][k][l][m];
  return 0;
}

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

int ArrayAccess_get_uint1d(ArrayAccess *self, int i){
  self->ret_uint = self->uint1d[i];
  return 0;
}

int ArrayAccess_get_uint2d(ArrayAccess *self, int i, int j){
  self->ret_uint = self->uint2d[i][j];
  return 0;
}

int ArrayAccess_get_uint3d(ArrayAccess *self, int i, int j, int k){
  self->ret_uint = self->uint3d[i][j][k];
  return 0;
}

int ArrayAccess_get_uint4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_uint = self->uint4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_uint5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_uint = self->uint5d[i][j][k][l][m];
  return 0;
}

int ArrayAccess_get_long1d(ArrayAccess *self, int i){
  self->ret_long = self->long1d[i];
  return 0;
}

int ArrayAccess_get_long2d(ArrayAccess *self, int i, int j){
  self->ret_long = self->long2d[i][j];
  return 0;
}

int ArrayAccess_get_long3d(ArrayAccess *self, int i, int j, int k){
  self->ret_long = self->long3d[i][j][k];
  return 0;
}

int ArrayAccess_get_long4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_long = self->long4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_long5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_long = self->long5d[i][j][k][l][m];
  return 0;
}

int ArrayAccess_get_ulong1d(ArrayAccess *self, int i){
  self->ret_ulong = self->ulong1d[i];
  return 0;
}

int ArrayAccess_get_ulong2d(ArrayAccess *self, int i, int j){
  self->ret_ulong = self->ulong2d[i][j];
  return 0;
}

int ArrayAccess_get_ulong3d(ArrayAccess *self, int i, int j, int k){
  self->ret_ulong = self->ulong3d[i][j][k];
  return 0;
}

int ArrayAccess_get_ulong4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_ulong = self->ulong4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_ulong5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_ulong = self->ulong5d[i][j][k][l][m];
  return 0;
}

int ArrayAccess_get_float1d(ArrayAccess *self, int i){
  self->ret_float = self->float1d[i];
  return 0;
}

int ArrayAccess_get_float2d(ArrayAccess *self, int i, int j){
  self->ret_float = self->float2d[i][j];
  return 0;
}

int ArrayAccess_get_float3d(ArrayAccess *self, int i, int j, int k){
  self->ret_float = self->float3d[i][j][k];
  return 0;
}

int ArrayAccess_get_float4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_float = self->float4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_float5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_float = self->float5d[i][j][k][l][m];
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

int ArrayAccess_get_longdouble1d(ArrayAccess *self, int i){
  self->ret_longdouble = self->longdouble1d[i];
  return 0;
}

int ArrayAccess_get_longdouble2d(ArrayAccess *self, int i, int j){
  self->ret_longdouble = self->longdouble2d[i][j];
  return 0;
}

int ArrayAccess_get_longdouble3d(ArrayAccess *self, int i, int j, int k){
  self->ret_longdouble = self->longdouble3d[i][j][k];
  return 0;
}

int ArrayAccess_get_longdouble4d(ArrayAccess *self, int i, int j, int k, int l){
  self->ret_longdouble = self->longdouble4d[i][j][k][l];
  return 0;
}

int ArrayAccess_get_longdouble5d(ArrayAccess *self, int i, int j, int k, int l, int m){
  self->ret_longdouble = self->longdouble5d[i][j][k][l][m];
  return 0;
}

/*[[[end]]]*/
