# jlogr

A simple python logger written in Rust.

Logs in one format only:
{timestamp} :: {log level} :: {message}

Example:

```python
    import info from jlogr

    info("hello")
```

If you use the Logger class, you can save to a file.

```python
    import Logger from jlogr

    logger = Logger("my_file.log")
    logger.info("this will go to the file")
```

You might be taking a large amount of logs that you'd like to buffer.

```python
    import Logger from jlogr

    logger = Logger("my_file.log")
    for i in range(1000):
        logger.push(f"this is log of index {i}", "info")
    logger.dump()
```
