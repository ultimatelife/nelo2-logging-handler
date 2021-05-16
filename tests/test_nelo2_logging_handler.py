import logging
import os
from datetime import datetime

from nelo2_logging_handler import __version__
from nelo2_logging_handler.nelo2_logging_handler import Nelo2LoggingHandler


def test_version():
    assert __version__ == '0.1.0'


def test_nelo2_handler():
    root_logger = logging.getLogger("test_logger")
    root_logger.setLevel("DEBUG")
    root_formatter = logging.Formatter("%(asctime)s - %(name)s:%(lineno)d %(funcName)20s - %(levelname)s - %(message)s")

    nelo2_handler = Nelo2LoggingHandler(project_name=os.environ['PROJECT_NAME'], project_version='0.1',
                                        end_point=os.environ['END_POINT'], )
    nelo2_handler.setFormatter(root_formatter)
    root_logger.addHandler(nelo2_handler)
    # HTTPHandler
    logger = logging.getLogger("test_logger")

    for i in range(10):
        logger.info(f"nelo2 handler info: {datetime.now()}")
        logger.debug(f"nelo2 handler debug: {datetime.now()}")
