import datetime


def set_log_level(logger, level):
    """Set log level for provided logger.

    :param logger: logger
    :type logger: logging.Logger
    :param level: logging level
    :type level: str
    """
    if level.upper() not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ValueError(f"Unknown log level {level}")
    logger.setLevel(level.upper())


def isodate_now():
    """Return current datetime in ISO-8601.

    :return: str
    """
    return datetime.datetime.utcnow().isoformat() + "Z"
