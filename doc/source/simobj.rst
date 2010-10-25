:class:`SimObject` --- A class loads everything you need from C shared library
==============================================================================

.. module:: railgun


.. class:: SimObject

   A base class used for loading C shared library.
   You will need to define four attribute: :attr:`_clibname_`,
   :attr:`_clibdir_`, :attr:`_cmembers_` and :attr:`_cfuncs_`.

   Example::

       class NameOfCStruct(SimObject):
           _clibname_ = 'name_of_shared_library.so'
           _clibdir_ = 'path/to/shared/library'

           _cmembers_ = [
               'num_i',
               'num_j',
               'int scalar',
               'int vector[i]',
               'int matrix[i][j]',
               ...
               ]

           _cfuncs_ = [
               'name_of_c_function',
               ...
               ]

           def __init__(self, num_i, num_j, **kwds):
               SimObject.__init__(self, num_i=num_i, num_j=num_j, **kwds)

           def some_function(self, ...):
               ...

   - You can override :meth:`SimObject.__init__`.
   - You can define additional python methods or members.
     But be careful with name: :class:`SimObject` will overwrite
     the methods or members of your class with name in
     :attr:`_cmembers_` and :attr:`_cfuncs_`.


   .. attribute:: SimObject._clibname_

      Name of your C shared library.

   .. attribute:: SimObject._clibdir_

      Path of the directory where your C library are.
      If you want to specify relative path from where
      this python module file are, you can use :func:`relpath`.

   .. attribute:: SimObject._cmembers_

      This is a list of the definitions of C variables with
      following syntax::

           [CDT] VAR_NAME[INDEX] [= DEFAULT]

      **VAR_NAME**: name of variable
          You can access the C variable by `obj.VAR_NAME`.

          Name of the member starts with ``num_`` define an index which
          is a letter(s) comes after this. For example, ``num_i`` defines
          index ``i``. Value of ``num_i`` is the size of array(s) along
          the index ``i``. For the member named ``num_*``, you can omit
          **CDT** (``int``).
      **CDT**: C Data Type, (optional if **VAR_NAME** starts with ``num_``)
          Choose CDT from the list in
          `Relationships among C Data Type (CDT), numpy dtype and ctypes`_.
      **INDEX**: index, optional
          If the variable is an array, **INDEX** should be specified.
          For the array with shape ``num_i1`` x ``num_i2`` x ... x `num_iN`,
          **INDEX** should be ``[i1][i2]...[iN]``.
      **DEFAULT**: a number, optional
          A default number for the variable. If **VAR_NAME** is
          an array, it will be filled with this value when it is created.

      .. warning::

         The order must be the same as in the C struct.

      Example::

          _cmembers_ = [
              'num_i', 'num_j', 'num_k',
              'int int_scalar',
              'int int_vector1[i]',
              'int int_vector2[j] = 0',
              'int int_matrix[i][j]',
              'double double_scalar = 0.1',
              'double double_vector[k] = 18.2',
              'double double_matrix[k][i] = -4.1',
              ]

      See also: :func:`cmems`

   .. attribute:: SimObject._cfuncs_

      This is a list of the definitions of C functions with
      following syntax::

          [RETURN_VAR] FUNC_NAME([ARG, ARG, ...])

      **FUNC_NAME**: string
          Name of C function to be loaded.
          You don't need to write the name of the `struct`.
          The name of the `struct` will be automatically added.

          See also: :ref:`choices`.
      **RETURN_VAR**: string, optional
          Name from C struct members.
          If specified, python wrapper function of **FUNC_NAME** will
          returns value of **RETURN_VAR** after **FUNC_NAME** function
          called.
      **ARG**:
          Argument of C function with following syntax::

              CDT_OR_INDEX ARG_NAME [= DEFAULT]

          **CDT_OR_INDEX**: string
              C Data Type or index.
              If index ``i`` (``i<``) is used here, error will be rasied if
              the argument `x` does not satisfy `0 <= x < num_i`
              (`0 < x <= num_i`).
          **ARG_NAME**: string
              Name of the argument.
          **DEFAULT**: a number or member of C struct, optional
              Default value for the argument.

          You don't need to write ``self`` which will be automatically
          added.

      Example::

          _cfuncs_ = [
              "func_spam()",
              "bar func_foo()",
              "func_with_args(int a, double b, i start=0, i< end=num_i)",
              "func_{key | c1, c2, c3}()",
              ]

      See also: :ref:`how_to_write_cfunc`

   .. attribute:: SimObject._cstructname_

      This is optional. This is used to specify the name of C struct
      explicitly::

           class CStructName(SimObject):  # 'CStructName' is name of c-struct
               ...

           class OtherNameForPyClass(SimObject):
               ...
               _cstructname_ = 'CStructName'  # this is name of c-struct


   .. attribute:: SimObject._cfuncprefix_

      This is optional. This is used to specify the prefix of C functions
      explicitly (default is name of C Struct + ``_``)::

           class YourSimObj(SimObject):
               ...
               _cfuncprefix_ = 'MyPrefix'
               _cfuncs_ = [
                   "FuncName()",  # 'MyPrefixFuncName' will be loaded
                   ...
                   ]

           class YourSimObj(SimObject):
               ...
               _cfuncprefix_ = ''
               _cfuncs_ = [
                   "FuncName()",  # 'FuncName' will be loaded
                   ...
                   ]

   .. method:: SimObject.setv(**kwds)

      This is used for setting values of C struct members.

      Following two lines have same effects::

           obj.setv(scalar=1, array=[1, 2, 3])
           obj.scalar = 1; obj.array = [1, 2, 3]

      Alias for element of array is available
      (Following lines have same effects)::

           obj.setv(var_0_1=1)
           obj.var[0][1] = 1


   .. method:: SimObject.getv(*args)

      Get the C variable by specifying the name
      (Following lines have same effects)::

           var = obj.var
           var = obj.getv('var')

      This is useful when you want to load multiple variables to
      local variable at once
      (Following lines have same effects)::

           (a, b, c) = (obj.a, obj.b, obj.c)
           (a, b, c) = obj.getv('a', 'b', 'c')
           (a, c, c) = obj.getv('a, b, c')


   .. method:: SimObject.num(*args)

      Get the size along index
      (Following lines have same effects)::

           num_i = obj.num_i
           num_i = obj.num('i')

      You can specify multiple indices
      (Following lines have same effects)::

           (num_i, num_j, num_k) = (obj.num_i, obj.num_j, obj.num_k)
           (num_i, num_j, num_k) = obj.num('i', 'j', 'k')
           (num_i, num_j, num_k) = obj.num('i, j, k')


Relationships among C Data Type (CDT), numpy dtype and ctypes
-------------------------------------------------------------

To specify C-language type of C struct members and C function arguments,
following C Data Types (**CDTs**) are available.

================ ============================== ============= ================
 CDT              C-language type                numpy dtype   ctypes
================ ============================== ============= ================
``char``          :c:type:`char`                 `character`   `c_char`
``short``         :c:type:`short`                `short`       `c_short`
``ushort``        :c:type:`unsigned short`       `ushort`      `c_ushort`
``int``           :c:type:`int`                  `int32`       `c_int`
``uint``          :c:type:`unsigned int`         `uint32`      `c_uint`
``long``          :c:type:`long`                 `int32` or    `c_long`
                                                 `int64`
``ulong``         :c:type:`unsigned long`        `uint32` or   `c_ulong`
                                                 `uint64`
``longlong``      :c:type:`long long`            `longlong`    `c_longlong`
``ulonglong``     :c:type:`unsigned long long`   `ulonglong`   `c_ulonglong`
``float``         :c:type:`float`                `float32`     `c_float`
``double``        :c:type:`double`               `float`       `c_double`
``longdouble``    :c:type:`long double`          `longdouble`  `c_longdouble`
``bool``          :c:type:`bool`                 `bool`        `c_bool`
================ ============================== ============= ================

.. note::

   Corresponding Numpy dtypes of CDTs ``long`` and ``ulong`` are chosen
   based on the variable returned by :func:`platform.architecture`.
