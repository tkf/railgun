__author__  = "Takafumi Arakaki (aka.tkf@gmail.com)"
__version__ = "0.1"
__license__ = "MIT License"

import os
from railgun.simobj import SimObject


def relpath(path, fpath):
    """Get path from python module by (getpath('ext/...', __file__))"""
    return os.path.join(os.path.dirname(fpath), path)
