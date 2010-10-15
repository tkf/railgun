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
                'num_s = 10000'
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


The pair of c and python code above is a very short and *complete* example!

If you want to write fast program for numerical simulations, you will
always end up with writing it in C (or C++ or FORTRAN, these low-level
languages). Although we have great python packages (not only) for
numerical simulation such as Numpy/Scipy, Pyrex, Cython, Psyco and so
on, sometimes these are not enough. On the other hand, writing code in
C is stressful, especially things like allocating memory and
read/write data which do not require speed so much. So, next thing you
want is to call C function from python and let python do all these
stuff (which python is good at!). Using ctypes, this is very easy.

But you may want much easier way! RailGun automatically generates a
python class which loads functions from C shared library, allocate
consistent arrays, provide argument checks at python side before the
argument is passed to C function, and let you easily access C
variables via python. All you need to do is to follow certain coding
style when you write C program so that RailGun can load functions
automatically.


Installation::

    easy_install railgun  # using setuptools
    pip install railgun   # using pip


Contents:

.. toctree::
   :maxdepth: 2

   tutorial

RailGun's repository is http://bitbucket.org/tkf/railgun/.
See samples in source code or
`here <http://bitbucket.org/tkf/railgun/src/tip/samples/>`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

