import pylab
from gslctypes_rng import gsl_rng

method = 'ziggurat'
sigma = 1.0
rng = gsl_rng()
pylab.hist(
    [rng.ran_gaussian(method=method, sigma=sigma) for i in xrange(1000)],
    bins=20, normed=True)
pylab.show()
