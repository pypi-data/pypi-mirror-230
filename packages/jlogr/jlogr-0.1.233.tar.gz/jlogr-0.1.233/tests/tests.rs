use jlogr::structures::logger::Logger;
use jlogr::structures::logging::Log;

const LOGS_PATH: &str = "./tests/logs.log";

#[test]
fn test_info() {
    let log = get_example_info_log();
    log.pretty_print();
}

#[test]
fn test_debug() {
    let log = get_example_debug_log();
    log.pretty_print();
}

#[test]
fn test_warn() {
    let log = get_example_warn_log();
    log.pretty_print();
}

#[test]
fn test_error() {
    let log = get_example_error_log();
    log.pretty_print();
}

#[test]
fn test_list_of_messages() {
    let mut logs: Vec<Log> = Vec::new();
    logs.push(get_example_info_log());
    logs.push(get_example_debug_log());
    logs.push(get_example_warn_log());
    logs.push(get_example_error_log());
    logs.push(get_example_badly_formatted_log());
    for log in logs {
        log.pretty_print();
    }
}

#[test]
fn test_logger_dump_file() {
    let mut logger = Logger::new(LOGS_PATH.to_string());
    logger.clear_file();
    let mut logs: Vec<Log> = Vec::new();
    logs.push(get_example_info_log());
    logs.push(get_example_debug_log());
    logs.push(get_example_warn_log());
    logs.push(get_example_error_log());
    logs.push(get_example_badly_formatted_log());
    logger.logs_buffer = logs;
    logger.dump();
    // Add assertion
    logger.clear_file();
}

#[test]
fn test_pull_logs_from_file() {
    let file_name = LOGS_PATH;
    let mut logger = Logger::new(file_name.to_string());
    logger.clear_file();
    populate_pull_logs_test_file(&mut logger);
    let file_string = std::fs::read_to_string(file_name).unwrap();
    logger.load();
    println!("logs_buffer: {:?}", logger.logs_buffer);
    panic!();
    assert!(
        logger.logs_buffer.len() == file_string.lines().count(),
        "found {} logs in buffer, expected {}",
        logger.logs_buffer.len(),
        file_string.lines().count()
    );
}

fn populate_pull_logs_test_file(logger: &mut Logger) {
    logger.push_log(get_example_info_log());
    logger.push_log(get_example_debug_log());
    logger.push_log(get_example_warn_log());
    logger.push_log(get_example_error_log());
    logger.dump();
    logger.clear_buffer();
}

#[test]
fn test_clear_log_buffer() {
    let mut logger = Logger::new(LOGS_PATH.to_string());
    let mut logs: Vec<Log> = Vec::new();
    logs.push(get_example_info_log());
    logs.push(get_example_debug_log());
    logs.push(get_example_warn_log());
    logs.push(get_example_error_log());
    logs.push(get_example_badly_formatted_log());
    logger.logs_buffer = logs;
    logger.clear_buffer();
    assert!(logger.logs_buffer.len() == 0);
}

#[test]
fn test_clear_log_file() {
    let file_name = LOGS_PATH;
    let mut logger = Logger::new(file_name.to_string());
    let mut logs: Vec<Log> = Vec::new();
    logs.push(get_example_info_log());
    logs.push(get_example_debug_log());
    logs.push(get_example_warn_log());
    logs.push(get_example_error_log());
    logs.push(get_example_badly_formatted_log());
    logger.logs_buffer = logs;
    logger.dump();
    logger.clear_file();
    let file_string = std::fs::read_to_string(file_name).unwrap();
    assert!(file_string.len() == 0, "found {}", file_string);
}

fn get_example_info_log() -> Log {
    Log::new(
        "Hello, world!",
        "info",
        Some("module_name"),
        Some("function_name"),
        Some("class_name"),
    )
}

fn get_example_debug_log() -> Log {
    Log::new(
        "Hello, world!",
        "debug",
        Some("module_name"),
        Some("function_name"),
        Some("class_name"),
    )
}

fn get_example_warn_log() -> Log {
    Log::new(
        "Hello, world!",
        "warning",
        Some("module_name"),
        Some("function_name"),
        Some("class_name"),
    )
}

fn get_example_error_log() -> Log {
    Log::new(
        "Hello, world!",
        "error",
        Some("module_name"),
        Some("function_name"),
        Some("class_name"),
    )
}

fn get_example_badly_formatted_log() -> Log {
    Log::new(
        "Hello, world!",
        "this is not a valid format",
        Some("module_name"),
        Some("function_name"),
        Some("class_name"),
    )
}
