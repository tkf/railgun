Utility functions
=================

.. module:: railgun

.. function:: relpath(relative_path, __file__)

   Get relative path.

   Let you have source tree like this::

        +- your_module.py
        `- ext/
           +- build/
           |  `- your_clib.so
           +- src/
           |  `- your_clib.c
           `- Makefile

   To load ``your_clib.so`` from ``your_module.py``, you can use
   :func:`relpath` in your class definition in ``your_module.py``
   like this::

        _clibname_ = 'your_clib.so'
        _clibdir_ = relpath('ext/build', __file__)

   Note that `__file__` is a special attribute of python module which is
   the pathname of the file from which the module was loaded.


.. function:: cmems(cdt, *args)

   Generate :attr:`SimObject._cmembers_` for same C Data Type (CDT)
   easily

   Usage:

   >>> cmems('int', 'a', 'b', 'c')
   ['int a', 'int b', 'int c']
   >>> cmems('int', 'a, b, c')
   ['int a', 'int b', 'int c']
   >>> cmems('int', 'a[i]', 'b[i][j]') + cmems('double', 'x[i]', 'y[i][j]')
   ['int a[i]', 'int b[i][j]', 'double x[i]', 'double y[i][j]']
