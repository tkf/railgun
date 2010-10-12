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

__author__  = "Takafumi Arakaki (aka.tkf@gmail.com)"
__version__ = "0.1.1"
__license__ = "MIT License"

import os
from railgun.simobj import SimObject


def relpath(path, fpath):
    """Get path from python module by (getpath('ext/...', __file__))"""
    return os.path.join(os.path.dirname(fpath), path)
