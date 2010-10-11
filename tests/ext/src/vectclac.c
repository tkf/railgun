typedef struct vectcalc_{
  int num_i;
  int *v1, *v2, *v3;
  int ans;
} VectCalc;

int VectCalc_vec_plus(VectCalc *self){
  int i;
  for (i = 0; i < self->num_i; ++i){
    self->v3[i] = self->v1[i] + self->v2[i];
  }
  return 0;
}

int VectCalc_vec_minus(VectCalc *self){
  int i;
  for (i = 0; i < self->num_i; ++i){
    self->v3[i] = self->v1[i] - self->v2[i];
  }
  return 0;
}

int VectCalc_vec_times(VectCalc *self){
  int i;
  for (i = 0; i < self->num_i; ++i){
    self->v3[i] = self->v1[i] * self->v2[i];
  }
  return 0;
}

int VectCalc_vec_divide(VectCalc *self){
  int i;
  for (i = 0; i < self->num_i; ++i){
    if (self->v2[i] == 0){
      return 1;
    }
    self->v3[i] = self->v1[i] / self->v2[i];
  }
  return 0;
}

int VectCalc_subvec_plus(VectCalc *self, int i1, int i2){
  int i;
  for (i = i1; i < i2; ++i){
    self->v3[i] = self->v1[i] + self->v2[i];
  }
  return 0;
}

int VectCalc_subvec_minus(VectCalc *self, int i1, int i2){
  int i;
  for (i = i1; i < i2; ++i){
    self->v3[i] = self->v1[i] - self->v2[i];
  }
  return 0;
}

int VectCalc_subvec_times(VectCalc *self, int i1, int i2){
  int i;
  for (i = i1; i < i2; ++i){
    self->v3[i] = self->v1[i] * self->v2[i];
  }
  return 0;
}

int VectCalc_subvec_divide(VectCalc *self, int i1, int i2){
  int i;
  for (i = i1; i < i2; ++i){
    if (self->v2[i] == 0){
      return 1;
    }
    self->v3[i] = self->v1[i] / self->v2[i];
  }
  return 0;
}

void i1d_fill(int *iv, int s, int n){
  int i;
  for (i = 0; i < n; ++i){
    iv[i] = s;
  }
}

int VectCalc_fill_v1(VectCalc *self, int s){
  i1d_fill(self->v1, s, self->num_i);
  return 0;
}

int VectCalc_fill_v2(VectCalc *self, int s){
  i1d_fill(self->v2, s, self->num_i);
  return 0;
}

int VectCalc_fill_v3(VectCalc *self, int s){
  i1d_fill(self->v3, s, self->num_i);
  return 0;
}

int VectCalc_subvec_dot(VectCalc *self, int i1, int i2){
  int i;
  self->ans = 0;
  for (i = i1; i < i2; ++i){
    self->ans += self->v1[i] * self->v2[i];
  }
  return 0;
}
