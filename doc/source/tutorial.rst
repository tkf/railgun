RailGun Tutorial
================

How to write C program for RailGun
----------------------------------

RailGun requires your C program to have specific type of style.


You need a `struct` which have the variables you can manipulate from python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is an example of a `struct`:

.. sourcecode:: c

   typedef struct linearode_{
     int num_d, num_s;
     double dt;
     double **a;
     double **x;
   } LinearODE;

Here, variable named as `num_d` has special meaning in RailGun.
This is the size of array along index `d`.

You can have temporary variables in your C code, but if you want to
get the value or set the value of a certain variable from python, you
must add the variable to the `struct`.


Functions used from python
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to use some functions from python, the type function must
take a pointer of the `struct` as first argument, like this:

.. sourcecode:: c

  int NameOfStruct_name_of_function(NameOfStruct *self, ...)

If this function returns non-zero value, RailGun will raise an error.

Here is an example:

.. sourcecode:: c

  int LinearODE_run(LinearODE *self, int s_end)
  {
    int s, d1, d2;
    for (s = 1; s < s_end; ++s){
      for (d1 = 0; d1 < self->num_d; ++d1){
        self->x[s][d1] = self->x[s-1][d1];
        for (d2 = 0; d2 < self->num_d; ++d2){
          self->x[s][d1] += self->dt * self->a[d1][d2] * self->x[s-1][d2];
        }
      }
    }
    return 0;
  }

.. note::

   You don't need to check if `s_end` above is in the range
   *[1, self->num_s]*. You will see you can leave it to RailGun!



How to use your C functions from python using RailGun
-----------------------------------------------------

All you need to import from RailGun is these two::

  from railgun import SimObject, relpath

To load our c function above, all you need to do is define a
class!::

  class LinearODE(SimObject):
      _clibname_ = 'liblode.so'
      _clibdir_ = relpath('.', __file__)
      _cmembers_ = [
          'num_d',
          'num_s = 10000'
          'double dt = 0.001',
          'double a[d][d]',
          'double x[s][d]',
          ]
      _cfuncs_ = ["x run(int s_end=num_s)"]

This is very simple.

Name of the class
    should be same as name of the C struct.
`_clibname_`: a string
    Name of your C shared library.
`_clibdir_`: a string
    Path of the directory where your C library are.
    If you want to specify relative path from where
    this python module file are, you can use
    `relpath('relative/path', __file__)`.
`_cmembers_`: a list of string
    This is the definitions of your C variables.
    **The order must the same as in C struct**.
    For the member named `num_*` you can omit `int`.
    You can set the default value as `double dt = 0.001`.
    Indices of C array have meaning. Size of the first axis of
    `x[s][d]` is `num_s`, and the second is `num_d`.
`_cfuncs_`: a list of string
    This is the definitions of your C functions which
    take the form `ret func_name(arg, ...)` where

    - `ret` is the returned value of the function which you can.
      You can leave it empty.
    - `func_name` is the name of the C function(s).
      You don't need to write the name of the `struct`.
      The name of the `struct` will be automatically added.
      You can specify several functions using special notations.
    - `arg` is definition of the argument of C function(s).
      This is essentially same as function declaration of C,
      but with special features. One of the feature is default
      value. You can specify default value like python:
      `int s_end=num_s` or `int s_start=0`.


Loading several C functions at once: ``func_{key|c1,c2}``-notation
------------------------------------------------------------------

If you have several C functions of *same type* such as:

.. sourcecode:: c

  int NameOfStruct_func_method1(NameOfStruct *self, int a, int b)
  int NameOfStruct_func_method2(NameOfStruct *self, int a, int b)
  int NameOfStruct_func_method3(NameOfStruct *self, int a, int b)

You can load all these functions like this::

  'func_{meth | method1, method2, method3}(int a, int b)'

Generated python function will be like this::

  NameOfStruct.func(a, b, meth='method1')

as you see, you can specify method by option of the python function.


Auto generated consistency check of argument
--------------------------------------------

You can use name of the index as type of argument like this::

  "run(s s_end)"

so that `s_end` is always in the range `[0, num_s)`.

But wait, `s_end` is an "upper bound" of the index. You want
it to be in the range `(0, num_s]`. You can specify this with `<`
like this::

  "run(s< s_end)"
