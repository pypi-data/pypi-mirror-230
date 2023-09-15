use baskerville::{Empty, Validator};
use pyo3::prelude::*;

use crate::generate_py_wrapper;

generate_py_wrapper! {
    /// Validates empty values.
    ///
    /// Example:
    ///
    ///    >>> empty = baskerville.Empty()
    ///    >>> empty.validate("")
    ///    True
    ///    >>> empty.validate("Ferris")
    ///    False
    Empty, PyEmpty, "Empty": Clone
}

#[pymethods]
impl PyEmpty {
    #[new]
    fn new() -> Self {
        Self(Empty)
    }

    fn __repr__(&self) -> &'static str {
        "Empty"
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}
