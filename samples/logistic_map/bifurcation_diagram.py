from logistic_map import LogisticMap
import pylab

lmap = LogisticMap(1000)

pylab.figure(1)
lmap.plot_bifurcation_diagram(0, 4, 500, sigma=1e-5)
pylab.title(r'$\sigma=10^{-5}$')

pylab.figure(2)
lmap.plot_bifurcation_diagram(0, 4, 500, sigma=1e-3)
pylab.title(r'$\sigma=10^{-3}$')

pylab.figure(3)
lmap.plot_bifurcation_diagram(0, 4, 500, sigma=1e-2)
pylab.title(r'$\sigma=10^{-2}$')

pylab.show()
