typedef struct linearode_{
  int num_d, num_s;
  double dt;
  double **a;
  double **x;
} LinearODE;

int run(LinearODE *self, int s_end)
{
  int s, d1, d2;
  for (s = 1; s < s_end; ++s){
    for (d1 = 0; d1 < self->num_d; ++d1){
      self->x[s][d1] = self->x[s-1][d1];
      for (d2 = 0; d2 < self->num_d; ++d2){
        self->x[s][d1] += self->dt * self->a[d1][d2] * self->x[s-1][d2];
      }
    }
  }
  return 0;
}
