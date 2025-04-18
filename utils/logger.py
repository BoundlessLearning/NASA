import logging
import os


def get_logger(name=__name__):
    logger = logging.getLogger("NovelTrendRadar")
    logger.propagate = False
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        if not os.path.exists('./log'):
            os.makedirs('./log')
        error_handler = logging.FileHandler('./log/error.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        logger.addHandler(ch)
    return logger
