from railgun import SimObject, relpath, cm


class LinearODERK4(SimObject):
    """
    Solve D-dimensional linear ODE using the Runge-Kutta method

    Equation::

        dX/dt(t) = A X(t)
        X: D-dimensional vector
        A: DxD matrix

    """

    _clibname_ = 'liblode_rk4.so'  # name of shared library
    _clibdir_ = relpath('.', __file__)  # library directory
    _cmembers_ = [  # declaring members of struct
        'num_d',  # num_* as size of array (no need to write `int`)
        'num_s',  # setting default value
        'double dt = 0.001',
        'double a[d][d]',  # num_d x num_d array
        'double x[s][d]',  # num_s x num_d array
    ] + (
        cm.double(*['k%s[d]' % s for s in '1234']) +
        cm.double(*['x%s[d]' % s for s in '123']) +
        cm.double(*['k%s_debug[s][d]' % s for s in '1234']) +
        cm.double(*['x%s_debug[s][d]' % s for s in '123'])
    )
    _cfuncs_ = ["x run_{level | normal, debug }()"]
    _cmemsubsets_ = dict(
        debug=dict(
            funcs=['run_debug'],
            members=(['k%s_debug' % s for s in '1234'] +
                     ['x%s_debug' % s for s in '123'])),
        )

    def plot_x(self):
        import pylab
        t = pylab.arange(self.num_s) * self.dt

        for d in range(self.num_d):
            pylab.plot(t, self.x[:,d], label='x%s'% d)
        pylab.legend()

    def plot_k(self):
        import pylab
        t = pylab.arange(self.num_s) * self.dt
        klist = self.getv(*['k%s_debug' % s for s in '1234'])

        for d in range(self.num_d):
            for (i, k) in enumerate(klist):
                pylab.plot(t, k[:,d], label='k%s_%s'% (i, d))
        pylab.legend()
