#include <gsl/gsl_rng.h>
#include <gsl/gsl_randist.h>

typedef struct logisticmap_{
  int num_i;
  double *xt;
  double mu;
  double sigma;
  gsl_rng *rng;
} LogisticMap;


int LogisticMap_gene_seq(LogisticMap *self)
{
  int i;
  double eta;
  for (i = 1; i < self->num_i; ++i){
    eta = gsl_ran_gaussian_ziggurat(self->rng, self->sigma);
    self->xt[i] = self->mu * self->xt[i-1] * (1 - self->xt[i-1]) + eta;
    if (self->xt[i] < 0){
      self->xt[i] = 0;
    }
  }
  return 0;
}

