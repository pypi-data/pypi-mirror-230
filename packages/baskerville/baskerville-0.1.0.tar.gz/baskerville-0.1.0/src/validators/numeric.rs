use pyo3::prelude::*;

use baskerville::{Float, Integer, Validator};

use crate::generate_py_wrapper;

generate_py_wrapper! {
    /// Represents a 128-bit signed integer and captures the largest and smallest
    /// values seen. These values can then be used to inform a more detailed
    /// inferred type. For example, if the minimum value is 0, then the
    /// field may be representable as an unsigned integer.
    ///
    /// Example:
    ///
    ///    >>> integer = baskerville.Integer()
    ///    >>> integer.validate("+42")
    ///    True
    ///    >>> integer.validate("Ferris")
    ///    False
    Integer, PyInteger, "Integer": Clone
}
generate_py_wrapper! {
    /// Represents a 64-bit floating point number.
    ///
    /// Example:
    ///
    ///    >>> float_ = baskerville.Float()
    ///    >>> float_.validate("4.2")
    ///    True
    ///    >>> float_.validate("42")
    ///    True
    ///    >>> float_.validate("+42e-1")
    ///    True
    ///    >>> float_.validate("Ferris")
    ///    False
    Float, PyFloat, "Float": Clone
}

#[pymethods]
impl PyInteger {
    #[new]
    fn new() -> Self {
        Self(Integer::default())
    }

    fn __repr__(&self) -> String {
        format!(
            "Integer(min_value={}, max_value={}, leading_plus={})",
            self.min_value(),
            self.max_value(),
            self.leading_plus(),
        )
    }

    /// int: Maximum value that this validator has validated successfully.
    #[getter]
    fn max_value(&self) -> i128 {
        self.0.max_value.unwrap_or_default()
    }

    /// int: Minimum value that this validator has validated successfully.
    #[getter]
    fn min_value(&self) -> i128 {
        self.0.min_value.unwrap_or_default()
    }

    /// bool: Whether this validator has seen a value with a leading '+' sign.
    #[getter]
    fn leading_plus(&self) -> bool {
        self.0.leading_plus
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}

#[pymethods]
impl PyFloat {
    #[new]
    fn new() -> Self {
        Self(Float::default())
    }

    fn __repr__(&self) -> String {
        format!(
            "Float(min_value={}, max_value={}, leading_plus={}, e_notation={})",
            self.min_value(),
            self.max_value(),
            self.leading_plus(),
            self.e_notation(),
        )
    }

    /// float: Maximum value that this validator has validated successfully.
    #[getter]
    fn max_value(&self) -> f64 {
        self.0.max_value.unwrap_or_default()
    }

    /// float: Minimum value that this validator has validated successfully.
    #[getter]
    fn min_value(&self) -> f64 {
        self.0.min_value.unwrap_or_default()
    }

    /// bool: Whether this validator has seen a value with a leading '+' sign.
    #[getter]
    fn leading_plus(&self) -> bool {
        self.0.leading_plus
    }

    /// bool: Whether this validator has seen a value written in
    /// `E notation <https://en.wikipedia.org/wiki/Scientific_notation#E_notation>`_.
    ///
    /// Example:
    ///
    ///     >>> float_ = baskerville.Float()
    ///     >>> float_.e_notation
    ///     False
    ///     >>> float_.validate("42e-1")
    ///     True
    ///     >>> float_.e_notation
    ///     True
    #[getter]
    fn e_notation(&self) -> bool {
        self.0.e_notation
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}
