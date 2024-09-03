from logging import Formatter, StreamHandler, getLogger, INFO

formatter = Formatter("%(levelname)s: %(message)s")
handler = StreamHandler()
handler.setFormatter(formatter)
logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(handler)
