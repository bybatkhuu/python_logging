# -*- coding: utf-8 -*-

try:
    from beans_logging.logging import logger
    from beans_logging.__version__ import __version__
except ImportError:
    from .logging import logger
    from .__version__ import __version__
