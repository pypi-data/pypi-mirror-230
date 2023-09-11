import logging
import logging.handlers
from pathlib import Path


def _set_level(level: int | str | None, default_level: int | str = "INFO") -> int:
    """Returns a correct level value.

    Parameters
    ----------
    level : int | str | None
        level of the logger, by "INFO"
        Any of the levers of logging can be passed as a string:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        Note that lower case letters can also be used
    default_level : int | str, optional
        default level in case that `level` is incorrect, by default "INFO"

    Returns
    -------
    The level as an int
    """

    if level is None:
        return _set_level(default_level)

    if isinstance(level, str):
        return logging.getLevelName(level.upper())
    elif not isinstance(level, int):
        return logging.INFO
    return level


def init_logger(
    name: str,
    level: int | str = "INFO",
    level_console: int | str | None = None,
    level_file: int | str | None = None,
    output_file: Path | None = None,
    file_size: int = 0,
    propagate: bool = False,
    output_console: bool = True,
    output_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Initializes the logger

    Parameters
    ----------
    name : str
        name of the logger
    level : int | str, optional
        level of the logger, by default "INFO"
        Any of the levers of logging can be passed as a string:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        Note that lower case letters can also be used
    level_console : int | str | None, optional
        level of the console logger, by default None
    level_file : int | str | None, optional
        level of the file logger, by default None
    output_file : Path, optional
        file to output the log, by default None
    file_size : int, optional
        maximum size of the output file in bytes, by default 0 (=unlimited size)
    propagate : bool, optional
        the log messages are passed or not to the parent logger, by default False
    output_console : bool, optional
        output the log to the console, by default True
    output_format : str, optional
        format of the output

    Returns
    -------
    logging.Logger
        logger
    """

    # FIXME Need some way to handle if the passed level string is not correct
    level = _set_level(level)

    level_console = _set_level(level_console, default_level=level)
    level_file = _set_level(level_file, default_level=level)

    level = min([level, level_console, level_file])

    formatter = logging.Formatter(output_format)

    handler_list: list[logging.Handler] = []
    if output_file:
        file_handler = logging.handlers.RotatingFileHandler(filename=output_file, maxBytes=file_size, backupCount=5)
        file_handler.setLevel(level_file)
        file_handler.setFormatter(formatter)
        handler_list.append(file_handler)

    if output_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level_console)
        console_handler.setFormatter(formatter)
        handler_list.append(console_handler)

    logger = logging.getLogger(name)

    # ??? Do I need to set the basicConfig for the root logger?
    # Check if the parent is the root logger
    # if logger.parent == logging.getLogger():
    #     logging.basicConfig(
    #         level=level,
    #         # format=output_format,
    #         handlers=handler_list,
    #     )

    # logger = logging.getLogger(name)

    logger.setLevel(level=level)
    logger.propagate = propagate
    for handler in handler_list:
        logger.addHandler(handler)
    return logger
