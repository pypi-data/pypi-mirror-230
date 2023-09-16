pub mod structures;
use pyo3::prelude::*;
use structures::logger::Logger;
use structures::logging::Log;

#[pymodule]
#[pyo3(name = "jlogr")]
pub fn jlogr(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(info, m)?)?;
    m.add_function(wrap_pyfunction!(debug, m)?)?;
    m.add_function(wrap_pyfunction!(warning, m)?)?;
    m.add_function(wrap_pyfunction!(error, m)?)?;
    m.add_function(wrap_pyfunction!(parse_list_of_logs, m)?)?;
    m.add_class::<Log>()?;
    m.add_class::<Logger>()?;
    Ok(())
}

#[pyfunction]
#[pyo3(name = "info")]
#[pyo3(signature = (message, module=None, function=None, class_name=None))]
pub fn info(
    message: &str,
    module: Option<&str>,
    function: Option<&str>,
    class_name: Option<&str>,
) -> Log {
    let log = Log::new(message, "info", module, function, class_name);
    log.pretty_print();
    log
}

#[pyfunction]
#[pyo3(name = "debug")]
#[pyo3(signature = (message, module=None, function=None, class_name=None))]
pub fn debug(
    message: &str,
    module: Option<&str>,
    function: Option<&str>,
    class_name: Option<&str>,
) -> Log {
    let log = Log::new(message, "debug", module, function, class_name);
    log.pretty_print();
    log
}

#[pyfunction]
#[pyo3(name = "warning")]
#[pyo3(signature = (message, module=None, function=None, class_name=None))]
pub fn warning(
    message: &str,
    module: Option<&str>,
    function: Option<&str>,
    class_name: Option<&str>,
) -> Log {
    let log = Log::new(message, "warning", module, function, class_name);
    log.pretty_print();
    log
}

#[pyfunction]
#[pyo3(name = "error")]
#[pyo3(signature = (message, module=None, function=None, class_name=None))]
pub fn error(
    message: &str,
    module: Option<&str>,
    function: Option<&str>,
    class_name: Option<&str>,
) -> Log {
    let log = Log::new(message, "error", module, function, class_name);
    log.pretty_print();
    log
}

#[pyfunction]
#[pyo3(name = "parse_list_of_logs")]
#[pyo3(text_signature = "(logs)")]
pub fn parse_list_of_logs(
    logs: Vec<(
        String,
        String,
        Option<String>,
        Option<String>,
        Option<String>,
    )>,
) {
    for log in logs {
        let (message, level, module, function, class_name) = log;
        let log = Log::new(
            message.as_str(),
            level.as_str(),
            module.as_deref(),
            function.as_deref(),
            class_name.as_deref(),
        );
        log.pretty_print();
    }
}
