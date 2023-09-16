use crate::structures::logging::Log;
use crate::{debug, error, info, warning};
use pyo3::prelude::*;
use std::{fs, io::Write};

/// Handles reading and writing of logs to the file system.
/// Keeps a buffer of logs in memory, but can dump to file.
#[pyclass]
pub struct Logger {
    pub logs_path: String,
    pub logs_buffer: Vec<Log>,
}

#[pymethods]
impl Logger {
    #[new]
    #[pyo3(text_signature = "(logs_path)")]
    #[pyo3(signature = (logs_path))]
    pub fn new(logs_path: String) -> Logger {
        Logger {
            logs_path,
            logs_buffer: Vec::new(),
        }
    }

    #[pyo3(text_signature = "(message, module, function, class)")]
    #[pyo3(signature = (
        message,
        module=None,
        function=None,
        class_name=None))]
    pub fn info(
        &mut self,
        message: &str,
        module: Option<&str>,
        function: Option<&str>,
        class_name: Option<&str>,
    ) {
        let log = info(message, module, function, class_name);
        self.logs_buffer.push(log);
    }

    #[pyo3(text_signature = "(message, module, function, class)")]
    #[pyo3(signature = (
        message,
        module=None,
        function=None,
        class_name=None))]
    pub fn debug(
        &mut self,
        message: &str,
        module: Option<&str>,
        function: Option<&str>,
        class_name: Option<&str>,
    ) {
        let log = debug(message, module, function, class_name);
        self.logs_buffer.push(log);
    }

    #[pyo3(text_signature = "(message, module, function, class)")]
    #[pyo3(signature = (
        message,
        module=None,
        function=None,
        class_name=None))]
    pub fn warning(
        &mut self,
        message: &str,
        module: Option<&str>,
        function: Option<&str>,
        class_name: Option<&str>,
    ) {
        let log = warning(message, module, function, class_name);
        self.logs_buffer.push(log);
    }

    #[pyo3(text_signature = "(message, module, function, class)")]
    #[pyo3(signature = (
        message,
        module=None,
        function=None,
        class_name=None))]
    pub fn error(
        &mut self,
        message: &str,
        module: Option<&str>,
        function: Option<&str>,
        class_name: Option<&str>,
    ) {
        let log = error(message, module, function, class_name);
        self.logs_buffer.push(log);
    }

    #[pyo3(text_signature = "(message, level, module, function, class)")]
    #[pyo3(signature = (
        message,
        level="info",
        module=None,
        function=None,
        class_name=None))]
    pub fn push(
        &mut self,
        message: &str,
        level: &str,
        module: Option<&str>,
        function: Option<&str>,
        class_name: Option<&str>,
    ) {
        let log = Log::new(message, level, module, function, class_name);
        self.logs_buffer.push(log);
    }

    #[pyo3(text_signature = "(log)")]
    #[pyo3(signature = (log))]
    pub fn push_log(&mut self, log: Log) {
        self.logs_buffer.push(log);
    }

    #[pyo3(text_signature = "()")]
    #[pyo3(signature = ())]
    pub fn display(&self) {
        for log in &self.logs_buffer {
            log.pretty_print()
        }
    }

    #[pyo3(text_signature = "()")]
    #[pyo3(signature = ())]
    pub fn load(&mut self) {
        fs::read_to_string(&self.logs_path)
            .unwrap_or_else(|e| {
                eprintln!("Failed to read file: {}", e.to_string());
                return "".to_string();
            })
            .lines()
            .for_each(|line| {
                self.logs_buffer.push(Log::from_log_string(line));
            });
    }

    #[pyo3(text_signature = "()")]
    #[pyo3(signature = ())]
    pub fn sort_by_ctime(&mut self) {
        self.logs_buffer
            .sort_by(|a, b| a.created_at.cmp(&b.created_at));
    }

    #[pyo3(text_signature = "()")]
    #[pyo3(signature = ())]
    pub fn dump(&self) {
        let mut file = fs::OpenOptions::new()
            .create(true)
            .write(true)
            .append(true)
            .open(&self.logs_path)
            .expect("Open to work properly");
        for log in &self.logs_buffer {
            file.write_all(format!("{}\n", log).as_bytes())
                .unwrap_or_else(|e| {
                    eprintln!("Failed to write to file: {}", e.to_string());
                });
        }
        file.sync_all().unwrap_or_else(|e| {
            eprintln!("Failed to sync file: {}", e.to_string());
        });
    }

    #[pyo3(text_signature = "()")]
    #[pyo3(signature = ())]
    pub fn clear_buffer(&mut self) {
        self.logs_buffer.clear();
    }

    #[pyo3(text_signature = "()")]
    #[pyo3(signature = ())]
    pub fn clear_file(&self) {
        fs::write(&self.logs_path, "").unwrap_or_else(|e| {
            eprintln!("Failed to clear file: {}", e.to_string());
        });
    }
}
