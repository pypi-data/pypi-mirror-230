import logging


LOGGER = logging.getLogger()
LEVELS = {
    'critical': LOGGER.critical,
    'error': LOGGER.error,
    'warning': LOGGER.warning,
    'info': LOGGER.info,
    'debug': LOGGER.debug
}


class mlog():
    def __new__(self, message: str, level: str = 'info') -> None:
        self._log(message, level)

    @classmethod
    def _log(cls, message: str, level: str = 'info') -> None:
        message = str(message)
        try:
            LEVELS[level](message)
        except (KeyError, ValueError):
            cls.warning(f'Invalid log level selection, {level}; using "info".')
            LEVELS['info'](message)

    @classmethod
    def critical(cls, message: str) -> None:
        cls._log(message, "critical")
    
    @classmethod
    def error(cls, message: str) -> None:
        cls._log(message, "error")
    
    @classmethod
    def warning(cls, message: str) -> None:
        cls._log(message, "warning")
    
    @classmethod
    def info(cls, message: str) -> None:
        cls._log(message, "info")
    
    @classmethod
    def debug(cls, message: str) -> None:
        cls._log(message, "debug")
