Kaplan-Yorke map
================

Output
------
.. plot:: samples/kaplan_yorke_map/kaplan_yorke_map.py

Python code
-----------
.. literalinclude:: kaplan_yorke_map.py
   :language: python

C code
------
.. literalinclude:: kaplan_yorke_map.c
   :language: c

Definition of the map
---------------------
.. math::

  x_{n+1} &= T(x_{n}) \\
  y_{n+1} &= \lambda y_{n} + h(x_{n}) \\
  T(x) &= 1 - \mu x^2 \\
  h(x) &= x


References
----------

- `Thermodynamics of chaotic systems: an introduction
  By Christian Beck, Friedrich Schlögl - Google Books
  <http://books.google.com/books?id=8G6B3yPpli8C&lpg=PP1&pg=PA12>`_
- `Kaplan–Yorke map - Wikipedia, the free encyclopedia
  <http://en.wikipedia.org/wiki/Kaplan%E2%80%93Yorke_map>`_
