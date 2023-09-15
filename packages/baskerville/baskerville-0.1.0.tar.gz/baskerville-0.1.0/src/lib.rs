use field::{display_fields, PyField};
use validators::{
    PyDate, PyDateTime, PyDateTimeFormat, PyEmpty, PyFloat, PyInteger, PyLiteral, PyText, PyTime,
    PyUnique,
};

mod csv;
mod field;
mod macros;
mod validators;
use crate::csv::infer_csv_py;
use pyo3::prelude::*;

#[pymodule]
#[pyo3(name = "baskerville")]
fn baskerville_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(infer_csv_py, m)?)?;
    m.add_function(wrap_pyfunction!(display_fields, m)?)?;
    m.add_class::<PyField>()?;
    m.add_class::<PyEmpty>()?;
    m.add_class::<PyText>()?;
    m.add_class::<PyLiteral>()?;
    m.add_class::<PyInteger>()?;
    m.add_class::<PyFloat>()?;
    m.add_class::<PyUnique>()?;
    m.add_class::<PyDate>()?;
    m.add_class::<PyTime>()?;
    m.add_class::<PyDateTime>()?;
    m.add_class::<PyDateTimeFormat>()?;
    Ok(())
}
