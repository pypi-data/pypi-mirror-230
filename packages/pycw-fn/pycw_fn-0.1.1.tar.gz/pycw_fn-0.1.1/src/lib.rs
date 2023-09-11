use ordered_float::OrderedFloat;
use pcw_fn as rs;
use pyo3::{exceptions::PyRuntimeError, prelude::*, types::PyString};
use rs::{Functor, PcwFn as PcwFn_rs, VecPcwFn};

type Float = f64;

#[pyclass]
#[derive(Debug, Clone)]
/// A piecewise function on the real line
pub struct PcwFn(rs::VecPcwFn<OrderedFloat<Float>, PyObject>);

impl PcwFn {
    pub fn combine(
        &self,
        other: &Self,
        action: impl FnMut(PyObject, PyObject) -> PyResult<PyObject>,
    ) -> PyResult<Self> {
        let internal: VecPcwFn<_, _> = self.clone().0.combine(other.clone().0, action);
        let (jumps, funcs) = internal.into_jumps_and_funcs();
        funcs
            .collect::<Result<Vec<_>, _>>()
            .map(|funcs| PcwFn(rs::VecPcwFn::try_from_iters(jumps, funcs).unwrap()))
    }

    pub fn combine_method1<N>(&self, other: &Self, method_name: N) -> PyResult<Self>
    where
        N: IntoPy<Py<PyString>>,
    {
        let name = Python::with_gil(|py| {
            method_name
                .into_py(py)
                .as_ref(py)
                .to_str()
                .unwrap()
                .to_owned()
        });
        self.combine(other, |l, r| {
            let name: &str = &name;
            Python::with_gil(|py| l.call_method1(py, name, (r,)))
        })
    }

    pub fn fmap(&self, action: impl FnMut(PyObject) -> PyResult<PyObject>) -> PyResult<Self> {
        let internal: VecPcwFn<_, _> = self.clone().0.fmap(action);
        let (jumps, funcs) = internal.into_jumps_and_funcs();
        funcs
            .collect::<Result<Vec<_>, _>>()
            .map(|funcs| PcwFn(rs::VecPcwFn::try_from_iters(jumps, funcs).unwrap()))
    }

    pub fn fmap_method0<N>(&self, method_name: N) -> PyResult<Self>
    where
        N: IntoPy<Py<PyString>>,
    {
        let name = Python::with_gil(|py| {
            method_name
                .into_py(py)
                .as_ref(py)
                .to_str()
                .unwrap()
                .to_owned()
        });
        self.fmap(|l| {
            let name: &str = &name;
            Python::with_gil(|py| l.call_method0(py, name))
        })
    }
}

#[pymethods]
impl PcwFn {
    #[new]
    #[pyo3(signature = (jumps, funcs))]
    /// Create a new piecewise function from collections of jumps and of funcs
    pub fn new(jumps: Vec<Float>, funcs: Vec<PyObject>) -> PyResult<Self> {
        Ok(PcwFn(
            rs::VecPcwFn::try_from_iters(jumps.into_iter().map(OrderedFloat), funcs)
                .or_else(|rust_err| Err(PyRuntimeError::new_err(format!("{:?}", rust_err))))?,
        ))
    }

    pub fn func_at(&self, x: Float) -> &PyObject {
        self.0.func_at(&OrderedFloat(x))
    }

    pub fn __call__(&self, x: Float) -> PyResult<PyObject> {
        let obj = self.func_at(x);
        Python::with_gil(|py| obj.call_method1(py, "__call__", (x,)))
    }

    pub fn __add__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__add__")
    }

    pub fn __sub__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__sub__")
    }

    pub fn __mul__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__mul__")
    }

    pub fn __div__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__div__")
    }

    pub fn __pow__(&self, other: &Self, modulo: Option<PyObject>) -> PyResult<Self> {
        self.combine(other, |l, r| {
            Python::with_gil(|py| l.call_method1(py, "__pow__", (r, &modulo)))
        })
    }

    pub fn __lshift__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__lshift__")
    }

    pub fn __rshift__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__rshift__")
    }

    pub fn __and__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__and__")
    }

    pub fn __xor__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__xor__")
    }

    pub fn __or__(&self, other: &Self) -> PyResult<Self> {
        self.combine_method1(other, "__or__")
    }

    pub fn __neg__(&self) -> PyResult<Self> {
        self.fmap_method0("__neg__")
    }

    pub fn __not__(&self) -> PyResult<Self> {
        self.fmap_method0("__not__")
    }

    pub fn __pos__(&self) -> PyResult<Self> {
        self.fmap_method0("__pos__")
    }

    pub fn __abs__(&self) -> PyResult<Self> {
        self.fmap_method0("__abs__")
    }

    pub fn __invert__(&self) -> PyResult<Self> {
        self.fmap_method0("__invert__")
    }
}

#[pymodule]
fn pycw_fn(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PcwFn>()?;
    Ok(())
}
