.. _logistic_map:

Logistic map with additive noise (usage of :func:`railgun.cmem`)
================================================================

You will need the file ``gslctypes_rng.py`` (see :ref:`gslctypes`).

Python code
-----------
``logistic_map.py``:

.. literalinclude:: logistic_map.py
   :language: python

``bifurcation_diagram.py``:

.. literalinclude:: bifurcation_diagram.py
   :language: python

C code
------
``logistic_map.c``:

.. literalinclude:: logistic_map.c
   :language: c

Output
------
.. plot:: samples/logistic_map/bifurcation_diagram.py
