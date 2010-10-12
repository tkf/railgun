from railgun import SimObject, relpath

class LinearODE(SimObject):
    """
    Solve D-dimensional linear ordinary differential equations

    Equation::

        dX/dt(t) = A X(t)
        X: D-dimensional vector
        A: DxD matrix

    """

    _clibname_ = 'liblode.so'  # name of shared library
    _clibdir_ = relpath('.', __file__)  # library directory
    _cmembers_ = [  # declaring members of struct
        'num_d',  # num_* as size of array (no need to write `int`)
        'num_s = 10000',  # setting default value
        'double dt = 0.001',
        'double a[d][d]',  # num_d x num_d array
        'double x[s][d]',  # num_s x num_d array
        ]
    _cfuncs_ = [  # declaring functions to load
        "x run(s< s_end=num_s)"
        # argument `s_end` has index `s` type and default is `num_s`
        # '<' means it is upper bound of the index so the range is [1, num_s]
        # this function returns member x
        ]


def main():
    lode = LinearODE(num_d=2)  # set num_d
    lode.x[0] = [1, 0]  # access c-member via lode.VAR
    lode.a = [[0, 1], [-1, 0]]
    x = lode.run()

    import pylab
    pylab.subplot(211)
    pylab.plot(x[:,0])
    pylab.plot(x[:,1])
    pylab.subplot(212)
    pylab.plot(x[:,0], x[:,1])
    pylab.show()


if __name__ == '__main__':
    main()
