use crate::macros::generate_py_wrapper;
use baskerville::{Field, Fields};
use pyo3::prelude::*;

use crate::validators::PyDataType;

generate_py_wrapper! {
    /// Represents a field and its valid data types.
    Field, PyField, "Field": Clone
}

#[pymethods]
impl PyField {
    pub fn __repr__(&self) -> String {
        Python::with_gil(|py| {
            let name = self
                .name()
                .map_or("None".into(), |name| format!("'{name}'"));
            let valid_types = self
                .valid_types()
                .into_iter()
                .map(|v| v.into_py(py).to_string())
                .collect::<Vec<String>>()
                .join(", ");
            let nullable = self.nullable().into_py(py).to_string();
            format!("Field(name={name}, valid_types=[{valid_types}], nullable={nullable})")
        })
    }

    /// typing.Optional[str]: The name of this field.
    #[getter]
    fn name(&self) -> Option<String> {
        self.0.name.clone()
    }

    /// list[typing.Union[baskerville.Text, baskerville.Literal, baskerville.Integer, baskerville.Float, baskerville.Unique, baskerville.Date, baskerville.Time, baskerville.DateTime, typing.Callable[[str], bool]]]: List of valid types for this field
    ///
    /// Note:
    ///     This will clone the entire list and its elements when retrieved.
    ///     Consider memoizing.
    #[getter]
    fn valid_types(&self) -> Vec<PyDataType> {
        self.0
            .valid_types
            .iter()
            .cloned()
            .map(PyDataType::from)
            .collect()
    }

    /// bool: Whether this field can have nullable values.
    #[getter]
    fn nullable(&self) -> bool {
        self.0.nullable
    }
}

/// Displays a list of fields in a table view with their types.
///
/// Args:
///     fields (list[baskerville.Field]): List of :class:`Field` s.
#[pyfunction]
pub fn display_fields(fields: Vec<&PyAny>) -> PyResult<String> {
    let fields: PyResult<Vec<Field>> = fields
        .clone()
        .into_iter()
        .map(|field| Ok(PyField::into(field.extract()?)))
        .collect();
    Ok(format!("{}", Fields(fields?)))
}
