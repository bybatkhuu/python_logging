#!/usr/bin/env python
# -*- coding: utf-8 -*-

from beans_logging import logger


logger.trace('Tracing...')
logger.debug('Debugging...')
logger.info('Logging info.')
logger.success('Success.')
logger.warning('Warning something.')
logger.error('Error occured.')
logger.critical('CRITICAL ERROR.')


def divide(a, b):
    _result = a / b
    return _result

try:
    divide(10, 0)
except Exception as err:
    logger.exception("Failed to divide:")
