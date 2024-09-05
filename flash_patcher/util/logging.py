from logging import Formatter, StreamHandler, getLogger, INFO, Logger

logger: Logger = None

def _logger_setup() -> Logger:
    """Sets up the main logger for use."""
    if logger is not None:
        logger.warning("Logger is already initialized.")
        return

    formatter = Formatter("%(levelname)s: %(message)s")
    handler = StreamHandler()
    handler.setFormatter(formatter)
    new_logger = getLogger(__name__)
    new_logger.setLevel(INFO)
    new_logger.addHandler(handler)
    return new_logger

logger = _logger_setup()
