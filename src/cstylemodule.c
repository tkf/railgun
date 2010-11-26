/* -*- c -*- */
#include <Python.h>
#include "structmember.h"
#include <numpy/arrayobject.h>

#define CStyle_MAXDIM 5

typedef struct cstyle_{
  PyObject_HEAD
  PyObject *pyarray;
  Py_ssize_t pointer;
  void *carray;
} CStyle;


static void **
cstyle2d_alloc(PyObject* pyarray)
{
  int i, num0;
  void **carray;

  num0 = PyArray_DIM(pyarray, 0);
  carray = (void**) PyMem_Malloc(sizeof(void*) * num0);
  if (carray == NULL){
    return NULL;
  }
  for (i = 0; i < num0; ++i){
    carray[i] = PyArray_GETPTR2(pyarray, i, 0);
  }
  return carray;
}


static void ***
cstyle3d_alloc(PyObject* pyarray)
{
  int i, j, num0, num1;
  void ***carray, **ptr1;

  num0 = PyArray_DIM(pyarray, 0);
  num1 = PyArray_DIM(pyarray, 1);

  carray = (void***) PyMem_Malloc(sizeof(void*) * (num0 * (1 + num1)));
  if (carray == NULL) return NULL;
  ptr1 = (void**) (carray + num0);

  for (i = 0; i < num0; ++i){
    carray[i] = ptr1 + (i * num1);
    for (j = 0; j < num1; ++j){
      carray[i][j] = PyArray_GETPTR3(pyarray, i, j, 0);
    }
  }
  return carray;
}


static void ****
cstyle4d_alloc(PyObject* pyarray)
{
  int i, j, k, num0, num1, num2;
  void ****carray, ***ptr1, **ptr2;

  num0 = PyArray_DIM(pyarray, 0);
  num1 = PyArray_DIM(pyarray, 1);
  num2 = PyArray_DIM(pyarray, 2);

  carray = (void****)
    PyMem_Malloc(sizeof(void*) * (num0 * (1 + num1 * (1 + num2))));
  if (carray == NULL) return NULL;
  ptr1 = (void***) (carray + num0);
  ptr2 = (void**) (carray + num0 * (1 + num1));

  for (i = 0; i < num0; ++i){
    carray[i] = ptr1 + (i * num1);
    for (j = 0; j < num1; ++j){
      carray[i][j] = ptr2 + (i * num1 * num2) + (j * num2);
      for (k = 0; k < num2; ++k){
        carray[i][j][k] = PyArray_GETPTR4(pyarray, i, j, k, 0);
      }
    }
  }
  return carray;
}


static void *****
cstyle5d_alloc(PyObject* pyarray)
{
  int i, j, k, l, num0, num1, num2, num3;
  void *****carray, ****ptr1, ***ptr2, **ptr3;

  num0 = PyArray_DIM(pyarray, 0);
  num1 = PyArray_DIM(pyarray, 1);
  num2 = PyArray_DIM(pyarray, 2);
  num3 = PyArray_DIM(pyarray, 3);

  carray = (void*****)
    PyMem_Malloc(sizeof(void*) * (num0 * (1 + num1 * (1 + num2 * (1 + num3)))));
  if (carray == NULL) return NULL;
  ptr1 = (void****) (carray + num0);
  ptr2 = (void***) (carray + num0 * (1 + num1));
  ptr3 = (void**) (carray + num0 * (1 + num1 * (1 + num2)));

  for (i = 0; i < num0; ++i){
    carray[i] = ptr1 + (i * num1);
    for (j = 0; j < num1; ++j){
      carray[i][j] = ptr2 + (i * num1 * num2) + (j * num2);
      for (k = 0; k < num2; ++k){
        carray[i][j][k] = ptr3 +
          (i * num1 * num2 * num3) + (j * num2 * num3) + (k * num3);
        for (l = 0; l < num3; ++l){
          carray[i][j][k][l] =
            PyArray_GETPTR4((PyArrayObject*) pyarray, i, j, k, l);
        }
      }
    }
  }
  return carray;
}


static void
CStyle_dealloc(CStyle *self)
{
  if (self->carray != NULL){
    PyMem_Free(self->carray);
    self->carray = NULL;
  }
  Py_XDECREF(self->pyarray);
  self->ob_type->tp_free((PyObject*)self);
}


static int
CStyle_init(CStyle *self, PyObject *args, PyObject *kwds)
{
  PyObject *pyarray=NULL, *tmp;
  static char *kwlist[] = {"pyarray", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
                                   &PyArray_Type, &pyarray)){
    return -1;
  }
  /* check dimension (<= CStyle_MAXDIM) */
  if (PyArray_NDIM(pyarray) > CStyle_MAXDIM){
    PyErr_Format(PyExc_ValueError,
                 "ndim of given numpy array (=%d) is larger than %d",
                 PyArray_NDIM(pyarray), CStyle_MAXDIM);
    return -1;
  }else if (PyArray_NDIM(pyarray) == 1){
    PyErr_SetString(PyExc_ValueError,
                    "CStyle is not needed for 1D array!");
    return -1;
  }

  /* set to member */
  if (pyarray) {
    tmp = self->pyarray;
    Py_INCREF(pyarray);
    self->pyarray = pyarray;
    Py_XDECREF(tmp);
  }

  /* Allocate C-array */
  switch (PyArray_NDIM(pyarray)){
  case 2: self->carray = cstyle2d_alloc(self->pyarray); break;
  case 3: self->carray = cstyle3d_alloc(self->pyarray); break;
  case 4: self->carray = cstyle4d_alloc(self->pyarray); break;
  case 5: self->carray = cstyle5d_alloc(self->pyarray); break;
  }

  if (self->carray == NULL){
    PyErr_NoMemory();
    Py_XDECREF(pyarray);
    return -1;
  }
  self->pointer = (Py_ssize_t)self->carray;

  return 0;
}


static PyMemberDef CStyle_members[] = {
  {"pyarray", T_OBJECT_EX, offsetof(CStyle, pyarray), READONLY,
   "numpy array"},
  {"pointer", T_PYSSIZET, offsetof(CStyle, pointer), READONLY,
   "pointer for accessing numpy array in C style (a[i][j][k])"},
  {NULL}  /* Sentinel */
};


static PyTypeObject CStyleType = {
  PyObject_HEAD_INIT(NULL)
  0,                               /*ob_size*/
  "cstyle.CStyle",       /*tp_name*/
  sizeof(CStyle),             /*tp_basicsize*/
  0,                               /*tp_itemsize*/
  (destructor)CStyle_dealloc, /*tp_dealloc*/
  0,                               /*tp_print*/
  0,                               /*tp_getattr*/
  0,                               /*tp_setattr*/
  0,                               /*tp_compare*/
  0,                               /*tp_repr*/
  0,                               /*tp_as_number*/
  0,                               /*tp_as_sequence*/
  0,                               /*tp_as_mapping*/
  0,                               /*tp_hash */
  0,                               /*tp_call*/
  0,                               /*tp_str*/
  0,                               /*tp_getattro*/
  0,                               /*tp_setattro*/
  0,                               /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT,              /*tp_flags*/
  "CStyle object",            /* tp_doc */
  0,                               /* tp_traverse */
  0,                               /* tp_clear */
  0,                               /* tp_richcompare */
  0,                               /* tp_weaklistoffset */
  0,                               /* tp_iter */
  0,                               /* tp_iternext */
  0,                               /* tp_methods */
  CStyle_members,             /* tp_members */
  0,                               /* tp_getset */
  0,                               /* tp_base */
  0,                               /* tp_dict */
  0,                               /* tp_descr_get */
  0,                               /* tp_descr_set */
  0,                               /* tp_dictoffset */
  (initproc)CStyle_init,      /* tp_init */
};


static PyMethodDef module_methods[] = {
  {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initcstyle(void)
{
  PyObject* m;

  CStyleType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&CStyleType) < 0){
    return;
  }

  m = Py_InitModule3("cstyle", module_methods,
                     "this module provides CStyle");

  if (m == NULL){
    return;
  }

  Py_INCREF(&CStyleType);
  PyModule_AddObject(m, "CStyle", (PyObject *)&CStyleType);
  PyModule_AddIntConstant(m, "MAXDIM", CStyle_MAXDIM);

  import_array();  /* NumPy initialization */
}
