# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('../README.rst').read())]]]
"""
RailGun: Accelerate your simulation programing
==============================================


.. sidebar:: Links:

   * `Documentation <http://tkf.github.io/railgun/>`_

     - `Examples <http://tkf.github.io/railgun/samples/>`_
     - (`Japanese version <http://tkf.bitbucket.org/railgun-doc-ja/>`_)

   * `Repository <https://github.com/tkf/railgun>`_ (at GitHub)
   * `Issue tracker <https://github.com/tkf/railgun/issues>`_ (at GitHub)
   * `PyPI <http://pypi.python.org/pypi/railgun>`_
   * `Travis CI <https://travis-ci.org/#!/tkf/railgun>`_ |build-status|


Overview
--------

RailGun is a ctypes utilities for faster and easier simulation
programming in C and Python.  It automatically creates Python
class to call C functions easily and safely.  All you need is
a few constraints in C code.

RailGun does more than just exporting C functions to Python world [#]_.
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

.. [#] Well, that's what ctypes does.


Installation
------------
::

    pip install railgun   # using pip
    easy_install railgun  # using setuptools (if you must)


Requirements
------------
- Numpy
- six
- (matplotlib for sample code)


License
-------
See LICENSE.


.. |build-status|
   image:: https://secure.travis-ci.org/tkf/railgun.png?branch=master
   :target: http://travis-ci.org/tkf/railgun
   :alt: Build Status

"""
# [[[end]]]

from .utils import *
from .simobj import SimObject, CDT2DTYPE
from .cdata import cmem

__author__ = "Takafumi Arakaki"
__version__ = "0.1.9.dev3"
__license__ = "MIT License"
