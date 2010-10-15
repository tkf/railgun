"""
RailGun: Accelerate your simulation programing with "C on Rails"
================================================================


Installation
------------
::

    easy_install railgun  # using setuptools
    pip install railgun   # using pip


Usage
-----
See samples in
`samples/ <https://bitbucket.org/tkf/railgun/src/tip/samples/>`_


Requirement
-----------
This module only requires Numpy.
"""

__author__  = "Takafumi Arakaki"
__version__ = "0.1.3"
__license__ = "MIT License"

import os
from railgun.simobj import SimObject


def relpath(path, fpath):
    """Get path from python module by (getpath('ext/...', __file__))"""
    return os.path.join(os.path.dirname(fpath), path)


def gene_cmem(cdt):
    """
    Generate function `cm{cdt}` automatically

    >>> cmint = gene_cmem('int')
    >>> cmint('a', 'b', 'c')
    ['int a', 'int b', 'int c']
    >>> cmint('a, b, c')
    ['int a', 'int b', 'int c']

    """
    def cmem(*args):
        if len(args) == 1:
            args = args[0].split(',')
        return ['%s %s' % (cdt, v.strip()) for v in args]
    cmem.func_name = 'cm%s' % cdt
    cmem.__doc__ = """
    Generate `_cmembers_` for same C type easily

    >>> cm%(cdt)s('a, b, c')
    ['%(cdt)s a', '%(cdt)s b', '%(cdt)s c']
    >>> cm%(cdt)s('a', 'b', 'c')
    ['%(cdt)s a', '%(cdt)s b', '%(cdt)s c']

    """ % dict(cdt=cdt)
    return cmem

cmint = gene_cmem('int')
cmdouble = gene_cmem('double')
