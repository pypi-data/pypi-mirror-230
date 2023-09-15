use crate::generate_py_wrapper;
use pyo3::prelude::*;

use baskerville::{Unique, Validator};

generate_py_wrapper! {
    /// Validates unique values.
    /// If the validator has seen a given value before,
    /// then it will fail to validate.
    ///
    /// Example:
    ///
    ///    >>> unique = baskerville.Unique()
    ///    >>> unique.validate("Ferris")
    ///    True
    ///    >>> unique.validate("Corro")
    ///    True
    ///    >>> unique.validate("Ferris")
    ///    False
    Unique, PyUnique, "Unique": Clone
}

#[pymethods]
impl PyUnique {
    #[new]
    fn new() -> Self {
        Self(Unique::default())
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}
