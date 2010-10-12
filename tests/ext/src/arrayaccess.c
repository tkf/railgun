typedef struct arrayaccess_{
  int num_i, num_j, num_k;
  int ret_int;
  double ret_double;
  int *int1d, **int2d, ***int3d;
  double *double1d, **double2d, ***double3d;
} ArrayAccess;

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
