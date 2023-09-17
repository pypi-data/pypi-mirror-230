mod directional;

use pyo3::prelude::*;

/// Directional light source models (Rust and Python)
pub use self::directional::{directional_envmap, py_directional_envmap};

/// All light source models (Python)
pub fn py_light_source(py: Python<'_>, parent_module: &PyModule) -> PyResult<()> {
  let module = PyModule::new(py, "light_source")?;
  module.add_function(wrap_pyfunction!(py_directional_envmap, module)?)?;
  parent_module.add_submodule(module)?;
  Ok(())
}
