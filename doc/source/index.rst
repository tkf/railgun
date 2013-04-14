.. RailGun documentation master file, created by
   sphinx-quickstart on Tue Oct 12 20:32:26 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RailGun's documentation!
===================================

.. list-table::

  * - Write less code in *C*

      .. sourcecode:: c

         typedef struct linearode_{
           int num_d, num_s;
           double dt;
           double **a;
           double **x;
         } LinearODE;

         int LinearODE_run(LinearODE *self)
         {
           int s, d1, d2;
           for (s = 1; s < self->num_s; ++s){
             for (d1 = 0; d1 < self->num_d; ++d1){
               self->x[s][d1] = self->x[s-1][d1];
               for (d2 = 0; d2 < self->num_d; ++d2){
                 self->x[s][d1] += self->dt * \
                   self->a[d1][d2] * self->x[s-1][d2];
               }
             }
           }
           return 0;
         }

    - ... *and in Python*! ::

        from railgun import SimObject, relpath


        class LinearODE(SimObject):
            _clibname_ = 'liblode.so'
            _clibdir_ = relpath('.', __file__)
            _cmembers_ = [
                'num_d',
                'num_s = 10000',
                'double dt = 0.001',
                'double a[d][d]',
                'double x[s][d]',
                ]
            _cfuncs_ = ["x run()"]

        lode = LinearODE(num_d=2)
        lode.a = [[0, 1], [-1, 0]]
        lode.x[0] = [1, 0]
        x = lode.run()

        import pylab
        pylab.plot(x)
        pylab.show()


The above pair of C and python code is very short but yet *complete* example!

If you want to write fast program for numerical simulations, you will
always end up with writing it in C (or C++ or FORTRAN, these low-level
languages). Although we have great python packages (not only) for
numerical simulation such as Numpy/Scipy, Pyrex, Cython, Psyco and so
on, sometimes these are not enough. On the other hand, writing code in
C is stressful, especially things like allocating memory and
read/write data which do not require speed so much. So, next thing you
want is to call C function from python and let python do all these
stuff (which python is good at!). Using ctypes, this is very easy.

On top of what ctypes provides, RailGun adds more features to kill
boilerplate that you normally need for simulation coding.

For example, when you write simulation code, you may face situation
like this many times:

    I am accessing array like ``x[i][j]`` and ``y[j][k]``, so I want
    the second axis of the array ``x`` and the first axis of the array
    ``y`` to be of the same length.

RailGun solves this problem by keeping shape of all arrays to be
consistent.  Memory allocation for these arrays is done automatically.

RailGun also provides some value check before passing it to C function.
For example, you may want to pass an index of some array to C function.
When you do that, you need to check if the index is in a certain range,
to avoid segmentation fault.  RailGun provides a short hand notation
to check that automatically.  Also, you can wrap C function to put any
kind of complex value check and pre/post-processing.

With these features and other useful utilities provided by RailGun,
you can really focus on guts of computation in C code.


Installation::

    easy_install railgun  # using setuptools
    pip install railgun   # using pip


Contents:

.. toctree::
   :maxdepth: 2

   tutorial
   simobj
   utils
   samples/index

RailGun's repository is http://bitbucket.org/tkf/railgun/.
See samples in source code or
`here <http://bitbucket.org/tkf/railgun/src/tip/samples/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

