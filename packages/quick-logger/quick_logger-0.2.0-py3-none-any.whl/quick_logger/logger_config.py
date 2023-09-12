import logging


LOGGER_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
    'notset': logging.NOTSET
}


def init_logger(
    file_path: str = None,
    stream: bool = True,
    level: str = 'info',
    fmt: str = "%(asctime)s:: %(levelname)s:: %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S"
) -> None:
    if not stream and not file_path:
        raise ValueError("Must supply at least one of file_path or stream.")
    try:
        level = LOGGER_LEVELS[level]
    except KeyError:
        print(f'Invalid level selection of {level}, defaulting to "info".')
        level = LOGGER_LEVELS['info']
    formatter = logging.Formatter(fmt, datefmt)
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    handlers = []
    if file_path:
        file_handler = logging.FileHandler(file_path)
        file_handler.setStream(stream=None)
        handlers.append(file_handler)
    if stream:
        handlers.append(logging.StreamHandler())
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)
