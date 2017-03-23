Change Log
==========

v0.1.9
------

- Python 3.5 and 3.6 are supported now.
- :meth:`.SimObject.reallocate` is added.
- Changing `num_*` raises error, as it could cause segmentation fault.
- :attr:`.SimObject.cinfo` is added.
- Types other than `int` can be used for `num_*`.
- C functions can be accessed via :func:`super`.  This eliminates the
  need of the `cwrap_*` function.
- `cwrap_*` function defined in subclasses are not executed anymore.
  This change is backward-incompatible.

  .. so maybe this is a good timing for bumping to 0.2?

v0.1.8
------

- Fix deep copy / pickle bug with multi-dimensional arrays.

v0.1.7
------

- Shallow copy (:func:`copy.copy`), deep copy (:func:`copy.deepcopy`)
  and pickling (:mod:`pickle`) are supported.
- Documentation is improved.
