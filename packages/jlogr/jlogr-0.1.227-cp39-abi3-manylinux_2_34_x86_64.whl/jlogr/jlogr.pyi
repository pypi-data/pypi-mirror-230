from .jlogr import (
        info as _info,
        debug as _debug,
        warning as _warning,
        error as _error,
        parse_list_of_logs as _parse_list_of_logs,
        Logger as _Logger,
        Log as _Log,
        )

from typing import Optional
from enum import Enum

__all__ = ["info", "debug", "warning", "error", "parse_list_of_logs", "Logger", "Log"]
__doc__ = """
Module for clean and colourful logging in python
This is just how i like my logs, so there aren't formatting options or anything like that.
"""

def info(message: str) -> None:
    """
    Log an info message to stdout

    # Example
    ```python
        import jlogr
        jlogr.info(\"Hello, world!\")
    ```

    # Output
    ```bash
        2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
    ```

    # Parameters
    - message: The message to log
    - module: The module that the message is coming from
    - function: The function that the message is coming from
    - class: The class that the message is coming from

    """
    ...

def debug(message: str) -> None:
    """
    Log a debug message
    # Example
    ```python
        import jlogr
        jlogr.debug(\"Hello, world!\")
    ```

    # Output
    ```bash
        2021-08-15T21:04:05.000000000+00:00 :: [DEBUG] :: Hello, world!
    ```

    # Parameters
    - message: The message to log
    - module: The module that the message is coming from
    - function: The function that the message is coming from
    - class: The class that the message is coming from
    """
    ...

def warning(message: str) -> None:
    """
    Log a message as a warning

    # Example
    ```python
        import jlogr
        jlogr.warning(\"Hello, world!\")
    ```

    # Output
    ```bash
        2021-08-15T21:04:05.000000000+00:00 :: [WARNING] :: Hello, world!
    ```

    # Parameters
    - message: The message to log
    - module: The module that the message is coming from
    - function: The function that the message is coming from
    - class: The class that the message is coming from
    """
    ...

def error(message: str) -> None:
    """
    Log a message as an error

    # Example
    ```python
        import jlogr
        jlogr.error(\"Hello, world!\")
    ```

    # Output
    ```bash
        2021-08-15T21:04:05.000000000+00:00 :: [ERROR] :: Hello, world!
    ```

    # Parameters
    - message: The message to log
    - module: The module that the message is coming from
    - function: The function that the message is coming from
    - class: The class that the message is coming from
    """
    ...

def parse_list_of_logs(
        logs: list[tuple[str, str, Optional[str], Optional[str], Optional[str]]]
        ) -> None:
    """
    Logs should be a list of tuples of strings, where the first string is the message \
            and the second
    string is the log level.

    # Example
    ```python
        import jlogr
        logs = [\
                (\"Hello, world!\", \"info\"), \
                (\"Hello, world!\", \"debug\"), \
                (\"Hello, world!\", \"warning\"), \
                (\"Hello, world!\", \"error\")]
        jlogr.parse_list_of_logs(logs)
    ```

    # Output
    ```bash
        2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        2021-08-15T21:04:05.000000000+00:00 :: [DEBUG] :: Hello, world!
        2021-08-15T21:04:05.000000000+00:00 :: [WARNING] :: Hello, world!
        2021-08-15T21:04:05.000000000+00:00 :: [ERROR] :: Hello, world!
    ```

    # Parameters
    - logs: A list of tuples of strings, where the tuple is structured \
            (message, level, module, function, class)

    """
    ...


class Log:
    """
    A class representing a log

    # Example
    ```python
        import jlogr
        log = jlogr.Log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Log\")
        log.pretty_print()
    ```
    # Output
    ```bash
        2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
    ```

    # Parameters
    - message: The message to log
    - level: The level of the log
    - module: The module that the message is coming from
    - function: The function that the message is coming from
    - class_name: The class that the message is coming from
    """
    def __new__(
        cls,
        message: str,
        level: str,
        module: Optional[str]=None,
        function: Optional[str]=None,
        class_name: Optional[str]=None,
        ) -> Log: ...

    @staticmethod
    def from_log_string(log_string: str) -> Log:
        """
        Create a log from a log string

        # Example
        ```python
            import jlogr
            log_string = \"2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!\"
            log = jlogr.Log.from_log_string(log_string)
            log.pretty_print()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        ```
        # Parameters
        - log_string: The log string to parse
        """
        ...

    def pretty_print(self):
        """
        Print the log to stdout

        # Example
        ```python
            import jlogr
            log = jlogr.Log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Log\")
            log.pretty_print()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        ```
        """
        ...

class LogLevel(Enum):
    """
    An enum representing the log levels

    # Example
    ```python
        import jlogr
        log_level = jlogr.LogLevel.info
        print(log_level)
    ```
    # Output
    ```bash
        LogLevel.info
    ```
    """
    info = 0
    debug = 1
    warning = 2
    error = 3

    def prefix(self) -> str:
        """
        Get the prefix of the log level

        # Example
        ```python
            import jlogr
            log_level = jlogr.LogLevel.info
            print(log_level.prefix())
        ```
        # Output
        ```bash
            [INFO]
        ```
        """
        ...

    @staticmethod
    def from_log_string(level: str) -> LogLevel:
        """
        Get the log level from a log string

        # Example
        ```python
            import jlogr
            log_level = jlogr.LogLevel.from_log_string(\"[INFO]\")
            print(log_level)
        ```
        # Output
        ```bash
            LogLevel.info
        ```
        # Parameters
        - level: The log level string to parse
        """
        ...

class Logger:
    """
    A class representing a Logger

    # Example
    ```python
        import jlogr
        logger = jlogr.Logger(\"/path/to/logs\")
        logger.push_log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Logger\")
        logger.display_list_of_logs()
    ```
    # Output
    ```bash
        2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
    ```

    # Parameters
    - logs_path: The path to the logs file
    """
    def __new__(cls, logs_path: str) -> Logger: ...

    def push(
        self,
        message: str,
        level: str,
        module: Optional[str]=None,
        function: Optional[str]=None,
        class_name: Optional[str]=None,
        ) -> None:
        """
        Construct and push a log to the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.push_log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Logger\")
            logger.display_list_of_logs()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        ```
        # Parameters
        - message: The message to log
        - level: The level of the log
        - module: The module that the message is coming from
        - function: The function that the message is coming from
        - class_name: The class that the message is coming from
        """
        ...

    def push_log(self, log: Log) -> None:
        """
        Push a log to the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            log = jlogr.Log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Logger\")
            logger.push_log_from_log(log)
            logger.display_list_of_logs()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        ```
        # Parameters
        - log: The log to push
        """
        ...

    def info(self, message: str, module: Optional[str]=None, function: Optional[str]=None, class_name: Optional[str]=None) -> None:
        """
        Construct and push an info log to the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.info(\"Hello, world!\", \"jlogr\", \"info\", \"Logger\")
            logger.display_list_of_logs()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        ```
        # Parameters
        - message: The message to log
        - module: The module that the message is coming from
        - function: The function that the message is coming from
        - class_name: The class that the message is coming from
        """
        ...
    def debug(self, message: str, module: Optional[str]=None, function: Optional[str]=None, class_name: Optional[str]=None) -> None:
        """
        Construct and push a debug log to the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.debug(\"Hello, world!\", \"jlogr\", \"info\", \"Logger\")
            logger.display_list_of_logs()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [DEBUG] :: Hello, world!
        ```
        # Parameters
        - message: The message to log
        - module: The module that the message is coming from
        - function: The function that the message is coming from
        - class_name: The class that the message is coming from
        """
        ...

    def warning(self, message: str, module: Optional[str]=None, function: Optional[str]=None, class_name: Optional[str]=None) -> None:
        """
        Construct and push a warning log to the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.warning(\"Hello, world!\", \"jlogr\", \"info\", \"Logger\")
            logger.display_list_of_logs()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [WARNING] :: Hello, world!
        ```
        # Parameters
        - message: The message to log
        - module: The module that the message is coming from
        - function: The function that the message is coming from
        - class_name: The class that the message is coming from
        """
        ...

    def error(self, message: str, module: Optional[str]=None, function: Optional[str]=None, class_name: Optional[str]=None) -> None:
        """
        Construct and push an error log to the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.error(\"Hello, world!\", \"jlogr\", \"info\", \"Logger\")
            logger.display_list_of_logs()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [ERROR] :: Hello, world!
        ```
        # Parameters
        - message: The message to log
        - module: The module that the message is coming from
        - function: The function that the message is coming from
        - class_name: The class that the message is coming from
        """
        ...

    def display(self) -> None:
        """
        Display the logs in the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.push_log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Logger\")
            logger.display_list_of_logs()
        ```

        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        ```
        """
        ...

    def load(self) -> None:
        """
        Pull logs from self.logs_path

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.pull_logs_from_file()
        ```

        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
        ```

        # Parameters
        - logs_path: The path to the logs file
        """
        ...

    def sort_by_ctime(self) -> None:
        """
        Sort the logs in the log buffer by creation time

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.pull_logs_from_file() ## Imagine this pulls 4 logs that are out of order
            logger.sort_logs_by_ctime()
            logger.display_list_of_logs()
        ```
        # Output
        ```bash
            2021-08-15T21:04:05.000000000+00:00 :: [INFO] :: Hello, world!
            2021-08-15T21:04:06.000000000+00:00 :: [INFO] :: Hello, world!
            2021-08-15T21:04:07.000000000+00:00 :: [INFO] :: Hello, world!
            2021-08-15T21:04:08.000000000+00:00 :: [INFO] :: Hello, world!
        ```
        """
        ...

    def dump(self) -> None:
        """
        Dump the logs in the log buffer to a file

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.push_log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Logger\")
            logger.dump_logs_to_file() ## One log would be dumped to the file
        ```
        """
        ...

    def clear_buffer(self) -> None:
        """
        Clear the log buffer

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.push_log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Logger\")
            logger.clear_log_buffer()
            logger.display_list_of_logs() ## Nothing would be displayed
        ```

        # Output
        ```bash
        ```

        """
        ...

    def clear_file(self) -> None:
        """
        Clear the log file

        # Example
        ```python
            import jlogr
            logger = jlogr.Logger(\"/path/to/logs\")
            logger.push_log(\"Hello, world!\", \"info\", \"jlogr\", \"info\", \"Logger\")
            logger.dump_logs_to_file() ## One log would be dumped to the file
            logger.clear_log_file()
            logger.pull_logs_from_file()
            logger.display_list_of_logs() ## Nothing would be displayed
        ```
        # Output
        ```bash
        ```
        """
        ...

    def __str__(self) -> str:
        """
        Return the logger as a string
        """
        ...

    def __repr__(self) -> str:
        """
        Return the logger as a string
        """
        ...
