use crate::generate_py_wrapper;
use baskerville::validators::time::DateTimeFormat;
use baskerville::{Date, DateTime, Time, Validator};
use pyo3::prelude::*;
use pyo3::pyclass::CompareOp;

generate_py_wrapper! {
    /// Example:
    ///
    /// >>> date = baskerville.Date()
    /// >>> date.validate("2001-01-22")
    /// True
    /// >>> date.formats
    /// ['%Y-%m-%d']
    Date, PyDate, "Date": Clone
}

#[pymethods]
impl PyDate {
    fn __repr__(&self) -> String {
        format!(
            "Date(formats=[{}])",
            self.0
                .formats
                .iter()
                .map(|f| format!("{f:?}"))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }

    #[new]
    #[pyo3(
        signature=(
            formats=None
        )
    )]
    pub fn new(formats: Option<Vec<String>>) -> Self {
        if let Some(formats) = formats {
            Self(Date { formats })
        } else {
            Self(Date::default())
        }
    }

    /// list[str]: List of valid date
    /// `strftime-like <https://docs.rs/chrono/latest/chrono/format/strftime/index.html>`_ format
    /// strings
    ///
    /// Note:
    ///     This will clone the entire list and its elements when retrieved.
    ///     Consider memoizing.
    #[getter]
    fn formats(&self) -> Vec<String> {
        self.0.formats.clone()
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}

generate_py_wrapper! {
    /// Example:
    ///
    /// >>> time = baskerville.Time()
    /// >>> time.validate("12:34:56")
    /// True
    /// >>> time.formats
    /// ['%H:%M:%S']
    Time, PyTime, "Time": Clone
}

#[pymethods]
impl PyTime {
    fn __repr__(&self) -> String {
        format!(
            "Time(formats=[{}])",
            self.0
                .formats
                .iter()
                .map(|f| format!("{f:?}"))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }

    #[new]
    #[pyo3(
        signature=(
            formats=None
        )
    )]
    pub fn new(formats: Option<Vec<String>>) -> Self {
        if let Some(formats) = formats {
            Self(Time { formats })
        } else {
            Self(Time::default())
        }
    }

    /// list[str]: List of valid time
    /// `strftime-like <https://docs.rs/chrono/latest/chrono/format/strftime/index.html>`_ format
    /// strings
    ///
    /// Note:
    ///     This will clone the entire list and its elements when retrieved.
    ///     Consider memoizing.
    #[getter]
    fn formats(&self) -> Vec<String> {
        self.0.formats.clone()
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}

generate_py_wrapper! {
    DateTimeFormat, PyDateTimeFormat, "DateTimeFormat": Clone, PartialEq
}

#[pymethods]
#[allow(non_snake_case)]
impl PyDateTimeFormat {
    fn __repr__(&self) -> String {
        format!("{:?}", self.0)
    }

    fn __richcmp__(&self, other: &Self, op: CompareOp, py: Python<'_>) -> PyObject {
        match op {
            CompareOp::Eq => (self.0 == other.0).into_py(py),
            CompareOp::Ne => (self.0 != other.0).into_py(py),
            _ => py.NotImplemented(),
        }
    }

    #[classattr]
    fn RFC2822() -> Self {
        Self(DateTimeFormat::RFC2822)
    }

    #[classattr]
    fn RFC3339() -> Self {
        Self(DateTimeFormat::RFC3339)
    }

    ///
    /// Args:
    ///    strftime (str): `Strftime-like <https://docs.rs/chrono/latest/chrono/format/strftime/index.html>`_ format string.
    #[staticmethod]
    fn Strftime(strftime: String) -> Self {
        Self(DateTimeFormat::Strftime(strftime))
    }

    /// `Unix timestamp <https://en.wikipedia.org/wiki/Unix_time>`_
    #[classattr]
    fn Unix() -> Self {
        Self(DateTimeFormat::Unix)
    }
}

generate_py_wrapper! {
    /// Validates date-time values.
    ///
    /// Args:
    ///    formats (typing.Optional[list[DateTimeFormat]]): List of date-time formats.
    ///
    /// Example:
    ///
    ///     >>> date_time = baskerville.DateTime()
    ///     >>> date_time.validate("Mon, 22 Jan 2001 00:00:00 GMT")
    ///     True
    ///     >>> date_time.formats
    ///     [RFC2822]
    ///     >>> date_time = baskerville.DateTime(formats=[baskerville.DateTimeFormat.Unix])
    ///     >>> date_time.validate("980121600")
    ///     True
    ///     >>> date_time.validate("Ferris")
    ///     False
    DateTime, PyDateTime, "DateTime": Clone
}

#[pymethods]
impl PyDateTime {
    fn __repr__(&self) -> String {
        format!(
            "DateTime(formats=[{}])",
            self.0
                .formats
                .iter()
                .map(|f| format!("{f:?}"))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }

    #[new]
    #[pyo3(
        signature=(
            formats=None
        )
    )]
    pub fn new(formats: Option<Vec<PyDateTimeFormat>>) -> Self {
        if let Some(formats) = formats {
            Self(DateTime {
                formats: formats.iter().cloned().map(DateTimeFormat::from).collect(),
            })
        } else {
            Self(DateTime::default())
        }
    }

    /// list[DateTimeFormat]: List of valid date-time formats
    ///
    /// Note:
    ///     This will clone the entire list and its elements when retrieved.
    ///     Consider memoizing.
    #[getter]
    fn formats(&self) -> Vec<PyDateTimeFormat> {
        self.0
            .formats
            .iter()
            .cloned()
            .map(PyDateTimeFormat::from)
            .collect()
    }

    fn validate(&mut self, value: &str) -> bool {
        self.0.validate(value)
    }
}
