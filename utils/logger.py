import logging


def get_logger(name=__name__):
    logger = logging.getLogger("NovelTrendRadar")
    logger.propagate = False
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
