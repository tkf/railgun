typedef struct linearoderk4_{
  int num_d, num_s;
  double dt;
  double **a, **x;
  double *k1, *k2, *k3, *k4, *x1, *x2, *x3;
  double **k1_debug, **k2_debug, **k3_debug, **k4_debug,
    **x1_debug, **x2_debug, **x3_debug;
} LinearODERK4;


void calc_f(double *y, double *x, double **a, int num_d)
{
  int d1, d2;

  for (d1 = 0; d1 < num_d; ++d1){
    y[d1] = 0;
    for (d2 = 0; d2 < num_d; ++d2){
      y[d1] += a[d1][d2] * x[d2];
    }
  }
}

void calc_xi(double *xi, double *x0, double *ki, double c, double dt,
             int num_d)
{
  int d;
  for (d = 0; d < num_d; ++d){
    xi[d] = x0[d] + dt * c * ki[d];
  }
}


void iterate_once(LinearODERK4 *self, int s)
{
  int d;
  double *x0 = self->x[s-1];

  calc_f(self->k1, x0, self->a, self->num_d);
  calc_xi(self->x1, x0, self->k1, 0.5, self->dt, self->num_d);
  calc_f(self->k2, self->x1, self->a, self->num_d);
  calc_xi(self->x2, x0, self->k2, 0.5, self->dt, self->num_d);
  calc_f(self->k3, self->x2, self->a, self->num_d);
  calc_xi(self->x3, x0, self->k3, 1, self->dt, self->num_d);
  calc_f(self->k4, self->x3, self->a, self->num_d);

  for (d = 0; d < self->num_d; ++d){
    self->x[s][d] = x0[d] + self->dt / 6 *
      (self->k1[d] + 2 * self->k2[d] + 2 * self->k3[d] + self->k4[d]);
  }
}


int LinearODERK4_run_normal(LinearODERK4 *self)
{
  int s;
  for (s = 1; s < self->num_s; ++s){
    iterate_once(self, s);
  }
  return 0;
}


int LinearODERK4_run_debug(LinearODERK4 *self)
{
  int s, d;
  for (s = 1; s < self->num_s; ++s){
    iterate_once(self, s);
    for (d = 0; d < self->num_d; ++d){
      self->k1_debug[s][d] = self->k1[d];
      self->k2_debug[s][d] = self->k2[d];
      self->k3_debug[s][d] = self->k3[d];
      self->k4_debug[s][d] = self->k4[d];
      self->x1_debug[s][d] = self->x1[d];
      self->x2_debug[s][d] = self->x2[d];
      self->x3_debug[s][d] = self->x3[d];
    }
  }
  return 0;
}
