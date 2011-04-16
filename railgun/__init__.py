"""
RailGun: Accelerate your simulation programing with "C on Rails"
================================================================

Overview
--------

RailGun is a ctypes utilities for faster and easier simulation
programming in C and Python. It requires just a few constraints to C
library loaded from Python and gives you automatically generated
Python class which calls C functions easily and safely.


Installation
------------
::

    easy_install railgun  # using setuptools
    pip install railgun   # using pip


Usage
-----

Please read
`document <http://tkf.bitbucket.org/railgun-doc/>`_
(`Japanese version <http://tkf.bitbucket.org/railgun-doc-ja/>`_) and
`samples <https://bitbucket.org/tkf/railgun/src/tip/samples/>`_.


Requirement
-----------
- Numpy
- (matplotlib for sample code)
"""

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
            args = args[0].split(',')
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
