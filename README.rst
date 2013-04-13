RailGun: Accelerate your simulation programing
==============================================


.. sidebar:: Links:

   * `Documentation <http://tkf.bitbucket.org/railgun-doc/>`_

     - `Examples <http://tkf.bitbucket.org/railgun-doc/samples/>`_
     - (`Japanese version <http://tkf.bitbucket.org/railgun-doc-ja/>`_)

   * `Repository <https://github.com/tkf/railgun>`_ (at GitHub)
   * `Issue tracker <https://github.com/tkf/railgun/issues>`_ (at GitHub)
   * `PyPI <http://pypi.python.org/pypi/railgun>`_
   * `Travis CI <https://travis-ci.org/#!/tkf/railgun>`_ |build-status|


Overview
--------

RailGun is a ctypes utilities for faster and easier simulation
programming in C and Python.  It automatically creates Python
calss to call C functions easily and safely.  All you need is
a few constraints in C code.


Installation
------------
::

    easy_install railgun  # using setuptools
    pip install railgun   # using pip


Requirement
-----------
- Numpy
- (matplotlib for sample code)


License
-------
See LICENSE.


.. |build-status|
   image:: https://secure.travis-ci.org/tkf/railgun.png?branch=master
   :target: http://travis-ci.org/tkf/railgun
   :alt: Build Status
