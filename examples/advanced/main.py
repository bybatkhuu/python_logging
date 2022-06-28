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

def nested(c):
    try:
        divide(5, c)
    except ZeroDivisionError:
        logger.exception("Show me, what value is wrong:")

nested(0)
