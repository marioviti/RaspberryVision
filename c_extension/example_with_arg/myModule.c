#include <Python.h>

int Cfib(int n){
  if (n<2)
    return n;
  else
    return Cfib(n-1) + Cfib(n-2);
}

// Python methods

static PyObject* fib(PyObject* self, PyObject* args) {
  int n;
  if (!PyArg_ParseTuple(args, "i", &n))
    return NULL;
  return Py_BuildValue("i",Cfib(n));
}

static PyObject* version(PyObject* self) {
  return Py_BuildValue("s","version 1.0");
}

// Struttura per il compilatore
static PyMethodDef myMethods[] = {
  //{"python method name", actual methods, tipo di args, docs}
  {"fib",fib,METH_VARARGS,"Calculate fib of n"},
  {"version",(PyCFunction)version,METH_NOARGS,"Return version"},
  {NULL,NULL,0,NULL} //importante
};

PyMODINIT_FUNC initmyModule(void) {
  (void) Py_InitModule("myModule", myMethods);
}
