use std::str::FromStr;

use pyo3::{prelude::*, pyclass::CompareOp, types::{PyType, PyBytes}};

#[pyclass]
#[derive(Clone)]
pub struct EUID(::euid::EUID);

#[pymethods]
impl EUID {
    fn extension(&self) -> Option<u16> {
        self.0.extension()
    }

    fn timestamp(&self) -> u64 {
        self.0.timestamp()
    }

    fn next(&self) -> Option<EUID> {
        match self.0.next() {
            Some(id) => Some(EUID(id)),
            None => None,
        }
    }

    fn encode(&self, checkmod: bool) -> String {
        self.0.encode(checkmod)
    }

    fn __repr__(slf: &PyCell<Self>) -> PyResult<String> {
        let class_name: &str = slf.get_type().name()?;
        Ok(format!("{}({})", class_name, slf.borrow().0.to_string()))
    }

    fn __str__(&self) -> String {
        self.0.to_string()
    }

    fn __richcmp__(&self, other: &Self, op: CompareOp) -> PyResult<bool> {
        Ok(op.matches(self.0.cmp(&other.0)))
    }

    fn __bool__(&self) -> bool {
        self.0 != ::euid::EUID::default()
    }

    fn __bytes__<'a>(&self, py: Python<'a>) -> &'a PyBytes {
        let v: [u8; 16] = From::from(self.0);
        PyBytes::new(py, &v)
    }

    #[classmethod]
    fn create(_cls: &PyType) -> PyResult<Option<EUID>> {
        Ok(::euid::EUID::create().map(|id| EUID(id)))
    }

    #[classmethod]
    fn create_with_extension(_cls: &PyType, ext: i128) -> PyResult<Option<EUID>> {
        if ext < 0 || ext > 0x7fff {
            Ok(Option::None)
        } else {
            Ok(::euid::EUID::create_with_extension(ext as u16).map(|id| EUID(id)))
        }
    }

    #[classmethod]
    fn from_str(_cls: &PyType, str: &str) -> PyResult<Option<EUID>> {
        match ::euid::EUID::from_str(&str) {
            Ok(id) => Ok(Some(EUID(id))),
            Err(_) => Ok(None),
        }
    }
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "euid")]
fn euid_python(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<EUID>()?;
    Ok(())
}
