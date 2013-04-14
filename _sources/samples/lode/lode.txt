Linear Ordinary Differential Equation
=====================================

Output
------
.. plot:: samples/lode/lode.py

Python code
-----------
.. literalinclude:: lode.py
   :language: python

C code
------
.. literalinclude:: lode.c
   :language: c


Using :attr:`SimObject._cstructname_`
-------------------------------------

Python code
^^^^^^^^^^^
.. literalinclude:: lode_cstructname.py
   :language: python

What is the difference from the normal version? (... just three lines!):

.. literalinclude:: lode_cstructname.diff
   :language: diff


Using :attr:`SimObject._cfuncprefix_`
-------------------------------------
How to omit the name of the struct in the C functions.

Python code
^^^^^^^^^^^
Please notice that ``_cfuncprefix_ = ''`` is added to omit the name of
the struct name.

.. literalinclude:: lode_cfuncprefix.py
   :language: python

C code
^^^^^^
The function is simply ``run`` without the prefix now.

.. literalinclude:: lode_cfuncprefix.c
   :language: c
