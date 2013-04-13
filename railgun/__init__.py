# [[[cog import cog; cog.outl('"""\n%s\n"""' % file('../README.rst').read())]]]
"""
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

"""
# [[[end]]]

__author__  = "Takafumi Arakaki"
__version__ = "0.1.6"
__license__ = "MIT License"

import os
from railgun.simobj import SimObject, CDT2DTYPE
from railgun._helper import HybridObj
from railgun.cdata import cmem


def relpath(path, fpath):
    """Get path from python module by (getpath('ext/...', __file__))"""
    return os.path.join(os.path.dirname(fpath), path)


def gene_cmem(cdt, funcfmt='%s'):
    """
    Generate function to generate `_cmembers_` for same C type easily

    >>> cm_int = gene_cmem('int', 'cm_%s')
    >>> cm_int('a', 'b', 'c')
    ['int a', 'int b', 'int c']
    >>> cm_int('a, b, c')
    ['int a', 'int b', 'int c']

    """
    def cmem(*args):
        if len(args) == 1:
            if isinstance(args[0], basestring):
                args = args[0].split(',')
            else:
                args = args[0]  # assume the first argument is iterative
        return ['%s %s' % (cdt, v.strip()) for v in args]
    func_name = funcfmt % cdt
    cmem.func_name = func_name
    cmem.__doc__ = """
    Generate `_cmembers_` for same C type easily

    >>> %(func_name)s('a, b, c')
    ['%(cdt)s a', '%(cdt)s b', '%(cdt)s c']
    >>> %(func_name)s('a', 'b', 'c')
    ['%(cdt)s a', '%(cdt)s b', '%(cdt)s c']

    """ % dict(cdt=cdt, func_name=func_name)
    return cmem

cm = HybridObj((cdt, gene_cmem(cdt, 'cm.%s')) for cdt in CDT2DTYPE)
cm.__doc__ = """
Correction of functions to generate `_cmembers_` for same C type easily

>>> cm.int('a', 'b', 'c')
['int a', 'int b', 'int c']
>>> cm.int('a, b, c')
['int a', 'int b', 'int c']
>>> cm['int']('a', 'b', 'c')
['int a', 'int b', 'int c']
>>> print sorted(cm())  #doctest: +NORMALIZE_WHITESPACE
['bool', 'char', 'double', 'float', 'int', 'long', 'longdouble',
 'longlong', 'short', 'uint', 'ulong', 'ulonglong', 'ushort']

"""


def cmems(cdt, *args):
    """
    Generate `_cmembers_` for same C type easily

    >>> cmems('int', 'a', 'b', 'c')
    ['int a', 'int b', 'int c']
    >>> cmems('int', 'a, b, c')
    ['int a', 'int b', 'int c']

    """
    if len(args) == 1:
        args = args[0].split(',')
    return ['%s %s' % (cdt, v.strip()) for v in args]
