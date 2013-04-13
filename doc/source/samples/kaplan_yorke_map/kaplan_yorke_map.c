typedef struct kaplanyorkemap_{
  int num_i;
  double *xt;
  double *yt;
  double mu;
  double lmd;
} KaplanYorkeMap;

int KaplanYorkeMap_gene_seq(KaplanYorkeMap *self)
{
  int st;
  for (st = 1; st < self->num_i; ++st){
    self->xt[st] = 1 - self->mu * self->xt[st-1] * self->xt[st-1];
    self->yt[st] = self->lmd * self->yt[st-1] + self->xt[st-1];
  }
  return 0;
}
