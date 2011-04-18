from railgun import SimObject, relpath, cmem
import numpy
from gslctypes_rng import gsl_rng

class LogisticMap(SimObject):

    _clibname_ = 'liblogistic_map.so'
    _clibdir_ = relpath('.', __file__)
    _cmembers_ = [
        'num_i',
        'double xt[i]',
        'double mu',
        'double sigma',
        cmem(gsl_rng, 'rng'),
        ]
    _cfuncs_ = ["xt gene_seq()"]

    def __init__(self, num_i, seed=None, **kwds):
        SimObject.__init__(self, num_i=num_i, rng=gsl_rng(seed), **kwds)

    def _cwrap_gene_seq(old_gene_seq):
        def gene_seq(self, **kwds):
            # use the previous "last state" as initial state, but setv
            # may overwrite this by `xt_0=SOMEVAL`
            self.xt[0] = self.xt[-1]
            self.setv(**kwds)
            return old_gene_seq(self)
        return gene_seq

    def bifurcation_diagram(self, mu_start, mu_stop, mu_num, **kwds):
        mu_list = numpy.linspace(mu_start, mu_stop, mu_num)
        self.gene_seq(mu=mu_list[0], **kwds)  # through first steps away
        xt_list = [self.gene_seq(mu=mu).copy() for mu in mu_list]
        return (mu_list, xt_list)

    def plot_bifurcation_diagram(self, mu_start, mu_stop, mu_num, **kwds):
        import pylab
        bd = self.bifurcation_diagram(mu_start, mu_stop, mu_num, **kwds)
        ones = numpy.ones(self.num_i)

        for (mu, x) in zip(*bd):
            pylab.plot(ones * mu, x, 'ko', markersize=0.5)
        pylab.ylim(0, 1)
