:class:`SimObject` --- A class loads everything you need from C shared library
==============================================================================

.. class:: yourcode.YourSimObject

   To load your C shared library, define a class inheriting
   :class:`railgun.SimObject`.
   You need to define four attribute: :attr:`_clibname_`,
   :attr:`_clibdir_`, :attr:`_cmembers_` and :attr:`_cfuncs_`.

   .. note::

      In this document, :class:`yourcode.YourSimObject` means the class
      *you need to define*.  This class is not in RailGun.

   Example::

       class YourSimObject(SimObject):
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

   - You can override :meth:`railgun.SimObject.__init__`.
   - You can define additional python methods or members.
     But be careful with name: :class:`railgun.SimObject` will overwrite
     the methods or members of your class with name in
     :attr:`_cmembers_` and :attr:`_cfuncs_`.


   .. attribute:: _clibname_

      Name of your C shared library.

   .. attribute:: _clibdir_

      Path to the directory where your C library locates.
      If you want to specify relative path from where
      this python module file are, you can use :func:`relpath`.

   .. attribute:: _cmembers_

      This is a list of the definitions of C variables with
      the following syntax::

           [CDT] VAR_NAME[INDEX] [= DEFAULT]

      **VAR_NAME**: name of variable
          This let you access the C variable by `obj.VAR_NAME`.

          Starting the name of the member with ``num_`` defines an index
          whose name is what comes after this. For example, ``num_i`` defines
          index ``i``. Value of ``num_i`` is the size of array(s) along
          the index ``i``. For the member named ``num_*``, you can omit
          **CDT** (``int``).
      **CDT**: C Data Type, (optional if **VAR_NAME** starts with ``num_``)
          Choose CDT from the list in
          `Relationships between C Data Type (CDT), numpy dtype and ctypes`_.
      **INDEX**: index, optional
          If the variable is an array, **INDEX** should be specified.
          For an array with shape ``num_i1 x num_i2 x ... x num_iN``,
          **INDEX** should be ``[i1][i2]...[iN]`` or ``[i1,i2,...,iN]``.

          ``[i1][i2]...[iN]``: multidimensional array
              You can access ``a[i][j]`` as ``self->a[i][j]`` in C
              code. This array data structure is called "`Iliffe vector`_" or
              "display". Strictly speaking, this is not equivalent to
              multidimensional array, but you can use as if it is.
          ``[i1,i2,...,iN]``: flattened array
              You can access ``a[i][j]`` as ``self->a[i * self->num_j + j]``
              in C code. Specifying correct index in C code is up to
              you.  It is recommended to use macro or inline function.

          .. _`Iliffe vector`: http://en.wikipedia.org/wiki/Iliffe_vector

      **DEFAULT**: a number, optional
          A default number for the variable. If **VAR_NAME** is
          an array, it will be filled with this value when it is created.

      .. warning::

         The order and number of the variables in :attr:`_cmembers_`
         must be the same as in the C struct.

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

      See also: :func:`railgun.cmems`

   .. attribute:: _cfuncs_

      This is a list of the definitions of C functions with
      the following syntax::

          [RETURN_VAR] FUNC_NAME(ARG, [ARG[, ...]])

      **FUNC_NAME**: string
          Name of C function to be loaded.
          You don't need to write the name of the `struct`.
          The name of the `struct` will be automatically prepended.

          See also: :ref:`choices`.
      **RETURN_VAR**: string, optional
          Name from C struct members.
          If specified, python wrapper function named **FUNC_NAME**
          returns value of **RETURN_VAR**.
      **ARG**:
          Argument of C function, specified by the following syntax::

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
          passed as the first argument of C function.

      Example::

          _cfuncs_ = [
              "func_spam()",
              "bar func_foo()",
              "func_with_args(int a, double b, i start=0, i< end=num_i)",
              "func_{key | c1, c2, c3}()",
              ]

      See also: :ref:`how_to_write_cfunc`

   .. attribute:: _cstructname_

      This is optional. This is used to specify the name of C struct
      explicitly::

           class CStructName(SimObject):  # 'CStructName' is name of c-struct
               ...

           class OtherNameForPyClass(SimObject):
               ...
               _cstructname_ = 'CStructName'  # this is name of c-struct


   .. attribute:: _cfuncprefix_

      This is optional. This is used to specify the prefix of C functions
      explicitly (default is name of C Struct + ``_``)::

           class YourSimObject(SimObject):
               ...
               _cfuncprefix_ = 'MyPrefix'
               _cfuncs_ = [
                   "FuncName()",  # 'MyPrefixFuncName' will be loaded
                   ...
                   ]

           class YourSimObject(SimObject):
               ...
               _cfuncprefix_ = ''
               _cfuncs_ = [
                   "FuncName()",  # 'FuncName' will be loaded
                   ...
                   ]

   .. attribute:: _cmemsubsets_

      dict of dict of list, optional.

      It defines the subset of C functions and struct variables to be
      accessible.  It must be of the following format:

      .. sourcecode:: py

         {'<SUBSET_KEY_1>': {
             'funcs': ['<FUNCTION_1>', '<FUNCTION_2>', ...],
             'members': ['<MEMBER_1>', '<MEMBER_2>', ...],
             'default': True,  # optional (default is False)
             },
          '<SUBSET_KEY_2>': {...},
          ...}

      This is useful when some subset of functions needs some
      subset of struct members.  For example, when in "debugging
      mode", you may want to record all temporal variables.  However,
      allocating temporal variables can be wasteful if you are not
      debugging.  Using :attr:`_cmemsubsets_`, you can allocate
      temporal variables when in the debugging mode and make sure
      that the functions that requires temporal variables are callable
      only in the debugging mode.  It helps you to avoid segmentation
      fault due to accessing invalid pointer.  :attr:`_cmemsubsets_`
      can be thought as machinery for "access levels".

      **SUBSET_KEY** : string
          You can pass boolean argument named ``_cmemsubsets_SUBSET_KEY``
          to :meth:`railgun.SimObject.__init__` to enable or disable
          the corresponding subset.

      **FUNCTION** : list of strings
          These functions are accessible from Python when the corresponding
          subset is enabled.
          You can use short-hand notation ``'func_{a, b, c}'`` to
          specify functions ``'func_a'``, ``'func_b'`` and ``'func_c'``.

      **MEMBER** : list of strings
          These struct members are allocated and accessible from Python
          when the corresponding subset is enabled.

      **DEFAULT** : bool, optional
         It is `False` when not specified, meaning that the C members
         in this subset is not accessible.

   .. method:: _cwrap_C_FUNC_NAME(func)

      This is optional. If you want to wrap C function ``C_FUNC_NAME``,
      define this wrapper function.

      Example::

          class YourSimObject(SimObject):

              _clibname_ = '...'
              _clibdir_ = '...'
              _cmembers_ = [
                  'num_i',
                  'int vec[i]',
                  ]
              _cfuncs_ = [
                  'your_c_function',
                  ]

              def _cwrap_your_c_function(old_c_function):
                  def your_c_function(self, *args, **kwds):
                      old_c_function(self, *args, **kwds)
                      return self.vec[:]  # return copy
                  return your_c_function

      After `your_c_function` is loaded from C library, your wrapper function
      will be called like this::

          your_c_function = _cwrap_your_c_function(your_c_function)

   .. attribute:: _cerrors_

      This is optional.
      When C function returns non-zero value, RailGun raises error
      which just tells the value returned (error code).
      To make the error message readable, or to handle the error
      better, you may want to use this attribute.

      If C function returns the non-zero value ``error_code``, and it
      is found ``_cerrors_``, RailGun will raise the error
      ``_cerrors_[error_code]``.

      Examples::

          class YourSimObject(SimObject):

              _clibname_ = '...'
              _clibdir_ = '...'
              _cmembers_ = [...]
              _cfuncs_ = [...]

              class YourExceptionClass(Exception):
                  pass

              _cerrors_ = {
                  # set exception
                  1: RuntimeError('error code 1 is raised'),
                  # you can use your own exception class
                  2: YourExceptionClass('your error message'),
                  }

      .. versionadded:: 0.1.7



.. class:: railgun.SimObject


   .. method:: setv(**kwds)

      This is used for setting values of C struct members or any other
      Python attributes.

      The following two lines have same effects::

           obj.setv(scalar=1, array=[1, 2, 3])
           obj.scalar = 1; obj.array = [1, 2, 3]

      You can use alias for elements of array.
      The following lines have same effect::

           obj.setv(var_0_1=1)
           obj.var[0][1] = 1


   .. method:: getv(*args)

      Get the C variable by specifying the name or any other
      Python attributes.

      The following lines have same effect::

           var = obj.var
           var = obj.getv('var')

      This is useful when you want to load multiple variables to
      local variable at once.
      The Following lines have same effect::

           (a, b, c) = (obj.a, obj.b, obj.c)
           (a, b, c) = obj.getv('a', 'b', 'c')
           (a, c, c) = obj.getv('a, b, c')


   .. method:: num(*args)

      Get the size along index.
      The Following lines have same effect::

           num_i = obj.num_i
           num_i = obj.num('i')

      You can specify multiple indices.
      The Following lines have same effect::

           (num_i, num_j, num_k) = (obj.num_i, obj.num_j, obj.num_k)
           (num_i, num_j, num_k) = obj.num('i', 'j', 'k')
           (num_i, num_j, num_k) = obj.num('i, j, k')


Relationships between C Data Type (CDT), numpy dtype and ctypes
---------------------------------------------------------------

To specify C-language type of C struct members and C function arguments,
the following C Data Types (**CDTs**) are available.

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

   Numpy dtypes corresponding to CDTs ``long`` and ``ulong`` are chosen
   based on the variable returned by :func:`platform.architecture`.
