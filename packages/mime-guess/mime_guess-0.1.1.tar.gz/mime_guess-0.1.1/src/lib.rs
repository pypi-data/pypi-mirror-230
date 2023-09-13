use pyo3::prelude::*;
use ::mime_guess::from_path;
/// Formats the sum of two numbers as string.
#[pyfunction]
fn guess_type(path:String) -> PyResult<Option<&'static str>> {
    let result = from_path(path).first_raw();
    Ok(result)
}

/// A Python module implemented in Rust.
#[pymodule]
fn mime_guess(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(guess_type, m)?)?;
    Ok(())
}