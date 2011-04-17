.. module:: yourcode

Runge-Kutta method (usage of :attr:`_cmemsubsets_`)
===================================================

If you are using a lot of intermediate variables and want to check these
variables for debugging, you can use :attr:`YourSimObject._cmemsubsets_` to
allocate memory only when the flag is on.

Python code (``lode_rk4.py``)
-----------------------------

.. literalinclude:: lode_rk4.py
   :language: python


C code (``lode_rk4.c``)
-----------------------
.. literalinclude:: lode_rk4.c
   :language: c


Running on "normal mode"
------------------------
.. literalinclude:: run.py
   :language: python

.. plot:: source/samples/lode_rk4/run.py


Running on "debug mode"
-----------------------
You can create "debug mode" instance by giving ``_cmemsubsets_debug=True``
to your class constructor.

.. literalinclude:: run_debug.py
   :language: python

.. plot:: source/samples/lode_rk4/run_debug.py


Reference
---------

- `Runge–Kutta methods - Wikipedia, the free encyclopedia
  <http://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods>`_
