from lode_rk4 import LinearODERK4

lode = LinearODERK4(num_s=10000, num_d=2, _cmemsubsets_debug=True)
lode.x[0] = [1, 0]  # access c-member "VAR" via lode.VAR
lode.a = [[-0.5, 1], [-1, 0]]
lode.run(mode='debug')

import pylab
lode.plot_k()
pylab.show()
