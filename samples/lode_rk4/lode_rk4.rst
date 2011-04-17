Runge-Kutta method (usage of :attr:`_cmemsubsets_`)
===================================================

Python code (``lode_rk4.py``)
-----------------------------

.. literalinclude:: lode_rk4.py
   :language: python

C code (``lode_rk4.c``)
-----------------------
.. literalinclude:: lode_rk4.c
   :language: c

Running without intermediate variables
--------------------------------------
.. literalinclude:: run.py
   :language: python

.. plot:: source/samples/lode_rk4/run.py


Running with intermediate variables
-----------------------------------
.. literalinclude:: run_debug.py
   :language: python

.. plot:: source/samples/lode_rk4/run_debug.py
