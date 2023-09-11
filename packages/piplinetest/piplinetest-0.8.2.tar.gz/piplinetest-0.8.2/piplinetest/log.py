import logging


def setup_logger(logger_name: str = "pipline_test") -> logging.Logger:
    logger = logging.getLogger(logger_name)
    # 配置日志
    logformat = logging.Formatter(
        "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(process)d][%(threadName)s] - %(message)s"
    )
    # stream handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logformat)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    logger.setLevel(logging.DEBUG)

    return logger
