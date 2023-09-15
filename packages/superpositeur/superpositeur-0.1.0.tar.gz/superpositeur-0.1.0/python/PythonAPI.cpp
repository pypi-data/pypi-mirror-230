#include "superpositeur/MixedState.hpp"

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "numpy/arrayobject.h"

namespace superpositeur {
namespace python {

struct PyQuantumState {
    PyObject_HEAD
    MixedState state;
};

static void PyQuantumState_dealloc (PyQuantumState *self) {
    self->state.~MixedState();
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *PyQuantumState_new(PyTypeObject *t, PyObject *, PyObject *) {
    PyQuantumState *result = (PyQuantumState *) t->tp_alloc(t, 0);

    if (result != nullptr) {
        result->state = MixedState();
    }

    return (PyObject *) result;
}

static int PyQuantumState_init(PyObject *self, PyObject *, PyObject *) {
    ((PyQuantumState *) self)->state = MixedState();
    return 0;
}

std::optional<Matrix> numpyArrayToMatrix(PyObject *o) {
    auto* shape = PyObject_GetAttrString(o, "shape");

    auto shapeSize = PyTuple_Size(shape);

    if (shapeSize != 2) {
        PyErr_SetString(PyExc_TypeError, "Kraus operators need to be 2-dimensional");
        return std::nullopt;
    }

    auto nRows = static_cast<std::uint64_t>(PyLong_AsLong(PyTuple_GetItem(shape, 0)));
    auto nCols = static_cast<std::uint64_t>(PyLong_AsLong(PyTuple_GetItem(shape, 1)));

    Matrix matrix(nRows, nCols);
    for (std::uint64_t rowIndex = 0; rowIndex < nRows; ++rowIndex) {
        for (std::uint64_t colIndex = 0; colIndex < nCols; ++colIndex) {
            auto* matrixIndex = PyTuple_New(2);
            PyTuple_SetItem(matrixIndex, 0, PyLong_FromLong(rowIndex));
            PyTuple_SetItem(matrixIndex, 1, PyLong_FromLong(colIndex));
            auto* value = PyObject_GetItem(o, matrixIndex);

            auto valueComplex = PyComplex_AsCComplex(value); // FIXME: check, what if those are integers?

            matrix.set(rowIndex, colIndex, std::complex{valueComplex.real, valueComplex.imag});
        }
    }

    return matrix;
}

std::optional<std::vector<QubitIndex>> parseOperands(PyObject *o) {
    // List is already checked by arg parsing.

    std::vector<QubitIndex> result;

    auto listSize = PyObject_Length(o);
    if (listSize < 0) {
        PyErr_BadInternalCall();
        return std::nullopt;
    }
    
    for (std::uint64_t i = 0; i < static_cast<std::uint64_t>(listSize); ++i) {
        auto *key = PyLong_FromUnsignedLong(i);
        if (!key) {
            PyErr_BadInternalCall();
            return std::nullopt;
        }

        auto *item = PyObject_GetItem(o, key);

        if (!item) {
            PyErr_BadInternalCall();
            return std::nullopt;
        }

        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "Operands need to be positive integers");
            return std::nullopt;
        }

        auto val = PyLong_AsLong(item);

        if (val < 0) {
            PyErr_SetString(PyExc_TypeError, "Operands need to be positive integers");
            return std::nullopt;
        }

        result.push_back(QubitIndex{static_cast<std::uint64_t>(val)});
    }

    return result;
}

static PyObject *PyQuantumState_apply(PyObject *self, PyObject *args, PyObject *keywds) {
    PyObject *emptyTuple = PyTuple_New(0);
    if (!emptyTuple) {
        PyErr_BadInternalCall();
        return nullptr;
    }

    static char* operandsKey = (char*) "operands";
    static char *kwlist[] = {operandsKey, nullptr};

    PyObject *pyOperands;
    if (!PyArg_ParseTupleAndKeywords(emptyTuple, keywds, "O!", kwlist, &PyList_Type, &pyOperands)) {
        return nullptr;
    }

    Py_ssize_t numberOfKrausOperators = PyTuple_Size(args);
    KrausOperators ks;

    for (Py_ssize_t i = 0; i < numberOfKrausOperators; ++i) {
        PyObject *arg = PyTuple_GetItem(args, i);
        if(arg == nullptr) {
            PyErr_BadInternalCall();
            return nullptr;
        }

        if (!PyArray_Check(arg)) {
            PyErr_SetString(PyExc_TypeError, "Kraus operators need to be instances of np.ndarray");
            return nullptr;
        }

        if (!PyArray_ISNUMBER((PyArrayObject *) arg)) {
            PyErr_SetString(PyExc_TypeError, "Kraus operator arrays need to store numbers");
            return nullptr;
        }
        
        auto matrix = numpyArrayToMatrix(arg);
        if (!matrix) {
            return nullptr;
        }

        ks.push_back(*matrix);
    }

    auto operands = parseOperands(pyOperands);

    if (!operands) {
        return nullptr;
    }

    try {
        CircuitInstruction instruction(ks, *operands);
        ((PyQuantumState *) self)->state(instruction);
    } catch (std::exception const& e) {
        return PyErr_Format(PyExc_RuntimeError, "Simulation error: %s", e.what());
    }

    Py_RETURN_NONE;
}

static PyObject *PyQuantumState_densityMatrix(PyObject *self, PyObject *args) {
    auto operands = parseOperands(args); // This is a tuple.

    if (!operands) {
        return nullptr;
    }

    npy_intp shape[2];
    shape[0] = 1 << operands->size();
    shape[1] = 1 << operands->size();

    PyObject* numpyArray = PyArray_ZEROS(2, shape, NPY_COMPLEX128, 0);
    if (!numpyArray) {
        PyErr_BadInternalCall();
        return nullptr;
    }

    std::vector<bool> mask;
    for (auto op: *operands) {
        mask.resize(std::max(static_cast<std::uint64_t>(mask.size()), op.value + 1), false);
        mask[op.value] = true;
    }

    auto iterator = ((PyQuantumState *) self)->state.getReducedDensityMatrixIterator(mask);
    while (auto densityMatrixEntry = iterator.next()) {
        auto i = std::get<0>(*densityMatrixEntry);
        auto j = std::get<1>(*densityMatrixEntry);
        auto v = std::get<2>(*densityMatrixEntry);

        auto* ij = reinterpret_cast<std::complex<double>*>(PyArray_GETPTR2(reinterpret_cast<PyArrayObject*>(numpyArray), i, j));
        *ij += v;

        if (i != j) {
            auto* ji = reinterpret_cast<std::complex<double>*>(PyArray_GETPTR2(reinterpret_cast<PyArrayObject*>(numpyArray), j, i));
            *ji += std::conj(v);
        }
    }

    return numpyArray;
}

static PyObject *PyQuantumState_densityMatrixDiagonal(PyObject *self, PyObject *args) {
    auto operands = parseOperands(args); // This is a tuple.

    if (!operands) {
        return nullptr;
    }

    npy_intp shape[] = { 1 << operands->size() };

    PyObject* numpyArray = PyArray_ZEROS(1, shape, NPY_COMPLEX128, 0);
    if (!numpyArray) {
        PyErr_BadInternalCall();
        return nullptr;
    }

    std::vector<bool> mask;
    for (auto op: *operands) {
        mask.resize(std::max(static_cast<std::uint64_t>(mask.size()), op.value + 1), false);
        mask[op.value] = true;
    }

    auto iterator = ((PyQuantumState *) self)->state.getReducedDensityMatrixDiagonalIterator(mask);
    while (auto densityMatrixDiagonalEntry = iterator.next()) {
        auto i = std::get<0>(*densityMatrixDiagonalEntry);
        auto v = std::get<1>(*densityMatrixDiagonalEntry);

        auto* c = reinterpret_cast<std::complex<double>*>(PyArray_GETPTR1(reinterpret_cast<PyArrayObject*>(numpyArray), i));
        *c += v;
    }

    return numpyArray;
}

static PyMethodDef PyQuantumState_methods[] = {
    {   "apply",
        (PyCFunction)(void(*)(void)) PyQuantumState_apply,
        METH_VARARGS | METH_KEYWORDS,
        "Apply Kraus operators to quantum state" },
    {   "densityMatrix",
        PyQuantumState_densityMatrix,
        METH_VARARGS,
        "Return reduced density matrix" },
    {   "densityMatrixDiagonal",
        PyQuantumState_densityMatrixDiagonal,
        METH_VARARGS,
        "Return reduced density matrix diagonal" },
    {nullptr}
};

static PyTypeObject PyQuantumState_Type = [] {
    PyTypeObject result { PyVarObject_HEAD_INIT(nullptr, 0) };
    result.tp_name = "superpositeur.QuantumState";
    result.tp_basicsize = sizeof(PyQuantumState);
    result.tp_doc = PyDoc_STR("Superpositeur simulated quantum state");
    result.tp_new = PyQuantumState_new;
    result.tp_init = PyQuantumState_init;
    result.tp_dealloc = (destructor) PyQuantumState_dealloc;
    result.tp_methods = PyQuantumState_methods;

    return result;
}();

static PyModuleDef superpositeurModule = [] {
    PyModuleDef result{ PyModuleDef_HEAD_INIT };
    result.m_name = "superpositeur";
    result.m_doc = "Superpositeur simulator Python API";
    result.m_size = -1;

    return result;
}();

PyMODINIT_FUNC
PyInit_superpositeur(void) {
    import_array();
    
    PyObject *m;
    if (PyType_Ready(&PyQuantumState_Type) < 0) {
        return nullptr;
    }

    m = PyModule_Create(&superpositeurModule);
    if (m == nullptr) {
        return nullptr;
    }

    Py_INCREF(&PyQuantumState_Type);
    if (PyModule_AddObject(m, "QuantumState", (PyObject *) &PyQuantumState_Type) < 0) {
        Py_DECREF(&PyQuantumState_Type);
        Py_DECREF(m);
        return nullptr;
    }

    return m;
}

}
}