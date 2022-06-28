# -*- coding: utf-8 -*-

import unittest

from beans_logging import logger


class TestBeansLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("Starting 'beans_logging' unittest...\n")

    @classmethod
    def tearDownClass(cls):
        logger.success("Successfully tested 'beans_logging'.")


    def test_init(self):
        logger.info("Testing initialization of 'beans_logging' module...")
        self.assertIsNotNone(logger)
        logger.success('Done.\n')

    def test_functions(self):
        logger.info("Testing basic functions of 'beans_logging'...")
        logger.trace('Tracing...')
        logger.debug('Debugging...')
        logger.info('Logging info.')
        logger.success('Success.')
        logger.warning('Warning something.')
        logger.error('Error occured.')
        logger.critical('CRITICAL ERROR.')
        self.assertTrue(True)
        logger.success("Done.\n")
