use crate::generate_py_wrapper;
use pyo3::prelude::*;

use baskerville::{Literal, Text, Validator};

generate_py_wrapper! {
    /// Validates values as text and will therefore always succeed,
    /// collecting information on the longest seen value.
    ///
    /// Example:
    ///
    ///    >>> text = baskerville.Text()
    ///    >>> text.validate("42")
    ///    True
    ///    >>> text.validate("Ferris")
    ///    True
    Text, PyText, "Text": Clone
}

generate_py_wrapper! {
    /// Validates on literal values provided at creation.
    /// For example, you could match on the values ``True`` and ``False`` to implement
    /// a boolean type validator.
    ///
    /// Args:
    ///    values (list[str]): List of literal values that will succeed.
    ///
    /// Example:
    ///
    ///    >>> boolean = baskerville.Literal(["True", "False"])
    ///    >>> boolean.validate("True")
    ///    True
    ///    >>> boolean.validate("Ferris")
    ///    False
    Literal, PyLiteral, "Literal": Clone
}

#[pymethods]
impl PyText {
    #[new]
    fn new() -> Self {
        Self(Text::default())
    }

    fn __repr__(&self) -> String {
        format!(
            "Text(min_length={}, max_length={})",
            self.min_length(),
            self.max_length()
        )
    }

    /// int: The minimum number of bytes of a value this validator has validated successfully.
    #[getter]
    fn min_length(&self) -> usize {
        self.0.min_length.unwrap_or_default()
    }

    /// int: The maximum number of bytes of a value this validator has validated successfully.
    #[getter]
    fn max_length(&self) -> usize {
        self.0.max_length.unwrap_or_default()
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}

#[pymethods]
impl PyLiteral {
    #[new]
    fn new(values: Vec<String>) -> Self {
        Self(Literal::new(values))
    }

    fn __repr__(&self) -> String {
        format!("Literal['{}']", self.0.values.join(" | "))
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}
