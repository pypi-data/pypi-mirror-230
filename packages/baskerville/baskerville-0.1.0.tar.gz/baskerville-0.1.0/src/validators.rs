pub mod nullable;
pub mod numeric;
pub mod text;
pub mod time;
pub mod unique;

use baskerville::DataType;
use baskerville_py_macro::IntoPy;
pub use nullable::PyEmpty;
pub use numeric::{PyFloat, PyInteger};
pub use text::{PyLiteral, PyText};
pub use time::{PyDate, PyDateTime, PyDateTimeFormat, PyTime};
pub use unique::PyUnique;

use pyo3::prelude::*;

#[derive(IntoPy, FromPyObject)]
pub enum PyDataType {
    Empty(PyEmpty),
    Text(PyText),
    Literal(PyLiteral),
    Integer(PyInteger),
    Float(PyFloat),
    Unique(PyUnique),
    Date(PyDate),
    Time(PyTime),
    DateTime(PyDateTime),
    Py(PyObject),
}

impl From<PyDataType> for DataType {
    fn from(value: PyDataType) -> Self {
        match value {
            PyDataType::Empty(x) => DataType::Empty(x.into()),
            PyDataType::Text(x) => DataType::Text(x.into()),
            PyDataType::Literal(x) => DataType::Literal(x.into()),
            PyDataType::Integer(x) => DataType::Integer(x.into()),
            PyDataType::Float(x) => DataType::Float(x.into()),
            PyDataType::Unique(x) => DataType::Unique(x.into()),
            PyDataType::Date(x) => DataType::Date(x.into()),
            PyDataType::Time(x) => DataType::Time(x.into()),
            PyDataType::DateTime(x) => DataType::DateTime(x.into()),
            PyDataType::Py(x) => DataType::Py(x),
        }
    }
}

impl From<DataType> for PyDataType {
    fn from(value: DataType) -> Self {
        match value {
            DataType::Empty(x) => PyDataType::Empty(x.into()),
            DataType::Text(x) => PyDataType::Text(x.into()),
            DataType::Literal(x) => PyDataType::Literal(x.into()),
            DataType::Integer(x) => PyDataType::Integer(x.into()),
            DataType::Float(x) => PyDataType::Float(x.into()),
            DataType::Unique(x) => PyDataType::Unique(x.into()),
            DataType::Date(x) => PyDataType::Date(x.into()),
            DataType::Time(x) => PyDataType::Time(x.into()),
            DataType::DateTime(x) => PyDataType::DateTime(x.into()),
            DataType::Py(x) => PyDataType::Py(x),
        }
    }
}
