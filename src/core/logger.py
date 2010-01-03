# -*- coding: utf-8 -*-


import os
import logging
from logging.handlers import RotatingFileHandler

from core.conf import configuration



LOGGING_DIRECTORY = getattr(configuration, 'LOGGING_DIRECTORY', '/tmp/')
LOGGING_LEVELS = getattr(configuration, 'LOGGING_LEVELS', {})
LOGGING_CONFIGURATION = {
        'maxBytes': 1024 * 3,
        'backupCount': 2,
}
LOGGING_CONFIGURATION.update(
        getattr(configuration, 'LOGGING_CONFIGURATION', {}))
LOGGING_HANDLERS = getattr(configuration, 'LOGGING_HANDLERS', [RotatingFileHandler, ])



def get(name):
    """Return logging objects.

    :param name: logger name, that will be used to create log file
    """
    if not os.path.isdir(LOGGING_DIRECTORY):
        os.makedirs(LOGGING_DIRECTORY)
    log_file = os.path.join(LOGGING_DIRECTORY, name)
    if not log_file.endswith('.log'):
        log_file += '.log'
    logger = logging.getLogger(name)
    # set logging level - full log when running in debug mode
    if configuration.DEBUG:
        logger.setLevel(logging.DEBUG)
    elif name in LOGGING_LEVELS:
        logger.setLevel(LOGGING_LEVELS[name])
    for handler in LOGGING_HANDLERS:
        log_handler = handler(log_file, **LOGGING_CONFIGURATION)
        logger.addHandler(log_handler)
    return logger
