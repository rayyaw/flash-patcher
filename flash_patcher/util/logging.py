from logging import Formatter, StreamHandler, getLogger, INFO

logger = getLogger(__name__)

def logger_setup():
    formatter = Formatter("%(levelname)s: %(message)s")
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.setLevel(INFO)
    logger.addHandler(handler)
