#[macro_export]
macro_rules! generate_py_wrapper {
    ( $(#[$attr:meta])*
    $inner: ty, $wrapper: ident, $pyname: literal $(: $( $trait:ident ),+ )? ) => {
        $(#[$attr])*
        #[derive($( $($trait,)* )?)]
        #[pyclass]
        #[pyo3(name = $pyname)]
        pub struct $wrapper (pub $inner);

        impl From<$inner> for $wrapper {
            fn from(inner: $inner) -> Self {
                $wrapper(inner)
            }
        }

        impl From<$wrapper> for $inner {
            fn from($wrapper(inner): $wrapper) -> Self {
                inner
            }
        }
    };
}

pub(crate) use generate_py_wrapper;
