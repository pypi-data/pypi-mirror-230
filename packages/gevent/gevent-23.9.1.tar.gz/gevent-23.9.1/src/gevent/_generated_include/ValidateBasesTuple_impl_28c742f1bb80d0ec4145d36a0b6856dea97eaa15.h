#if CYTHON_COMPILING_IN_CPYTHON || CYTHON_COMPILING_IN_LIMITED_API || CYTHON_USE_TYPE_SPECS
static int __Pyx_validate_bases_tuple(const char *type_name, Py_ssize_t dictoffset, PyObject *bases) {
    Py_ssize_t i, n;
#if CYTHON_ASSUME_SAFE_MACROS
    n = PyTuple_GET_SIZE(bases);
#else
    n = PyTuple_Size(bases);
    if (n < 0) return -1;
#endif
    for (i = 1; i < n; i++)
    {
#if CYTHON_AVOID_BORROWED_REFS
        PyObject *b0 = PySequence_GetItem(bases, i);
        if (!b0) return -1;
#elif CYTHON_ASSUME_SAFE_MACROS
        PyObject *b0 = PyTuple_GET_ITEM(bases, i);
#else
        PyObject *b0 = PyTuple_GetItem(bases, i);
        if (!b0) return -1;
#endif
        PyTypeObject *b;
#if PY_MAJOR_VERSION < 3
        if (PyClass_Check(b0))
        {
            PyErr_Format(PyExc_TypeError, "base class '%.200s' is an old-style class",
                         PyString_AS_STRING(((PyClassObject*)b0)->cl_name));
#if CYTHON_AVOID_BORROWED_REFS
            Py_DECREF(b0);
#endif
            return -1;
        }
#endif
        b = (PyTypeObject*) b0;
        if (!__Pyx_PyType_HasFeature(b, Py_TPFLAGS_HEAPTYPE))
        {
            __Pyx_TypeName b_name = __Pyx_PyType_GetName(b);
            PyErr_Format(PyExc_TypeError,
                "base class '" __Pyx_FMT_TYPENAME "' is not a heap type", b_name);
            __Pyx_DECREF_TypeName(b_name);
#if CYTHON_AVOID_BORROWED_REFS
            Py_DECREF(b0);
#endif
            return -1;
        }
#if !CYTHON_USE_TYPE_SLOTS
        if (dictoffset == 0) {
            PyErr_Format(PyExc_TypeError,
                "extension type '%s.200s': "
                "unable to validate whether bases have a __dict__ "
                "when CYTHON_USE_TYPE_SLOTS is off "
                "(likely because you are building in the limited API). "
                "Therefore, all extension types with multiple bases "
                "must add 'cdef dict __dict__' in this compilation mode",
                type_name);
#if CYTHON_AVOID_BORROWED_REFS
            Py_DECREF(b0);
#endif
            return -1;
        }
#else
        if (dictoffset == 0 && b->tp_dictoffset)
        {
            __Pyx_TypeName b_name = __Pyx_PyType_GetName(b);
            PyErr_Format(PyExc_TypeError,
                "extension type '%.200s' has no __dict__ slot, "
                "but base type '" __Pyx_FMT_TYPENAME "' has: "
                "either add 'cdef dict __dict__' to the extension type "
                "or add '__slots__ = [...]' to the base type",
                type_name, b_name);
            __Pyx_DECREF_TypeName(b_name);
#if CYTHON_AVOID_BORROWED_REFS
            Py_DECREF(b0);
#endif
            return -1;
        }
#endif
#if CYTHON_AVOID_BORROWED_REFS
        Py_DECREF(b0);
#endif
    }
    return 0;
}
#endif

