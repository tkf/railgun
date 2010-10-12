.. RailGun documentation master file, created by
   sphinx-quickstart on Tue Oct 12 20:32:26 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RailGun's documentation!
===================================

If you want to write fast program for numerical simulations, you will
always end up with writing it in C (or C++ or FORTRAN, these low-level
languages). Although we have great python packages (not only) for
numerical simulation such as Numpy/Scipy, Pyrex, Cython, Psyco and so
on, sometimes these are not enough. On the other hand, writing code in
C is stressful, especially things like allocating memory and
read/write data which do not require speed so much. So, next thing you
want is to call C function from python and let python do all these
stuff (which python is good at!). Using ctypes, this is very easy.

But you may want much easier way! RailGun automatically generates
python class which load functions from C shared library, allocate
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

