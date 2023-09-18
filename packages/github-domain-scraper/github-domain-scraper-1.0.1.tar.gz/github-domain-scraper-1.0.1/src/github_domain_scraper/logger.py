import logging


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_log_handler = logging.StreamHandler()
    console_log_handler.setLevel(logging.INFO)
    console_log_handler.setFormatter(formatter)

    logger.addHandler(console_log_handler)

    return logger
