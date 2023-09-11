"""Initialization file for the testing_platform package."""
import os
import logging

RAGA_CONFIG_FILE = ".raga/config"

# Get the value of the DEBUG environment variable
debug_mode = os.environ.get('DEBUG')

# Configure the logging format and level based on the DEBUG environment variable
if debug_mode:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
else:
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
if debug_mode:
    # Add a file handler to log messages to a file
    file_handler = logging.FileHandler('debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Add the file handler to the logger
    logger = logging.getLogger(__name__)
    logger.addHandler(file_handler)

from .test_session import *
from .dataset_creds import *
from .dataset import *
from .raga_schema import *
from ._tests import *
from .post_deployment_checks import *
from .model_executor_factory import ModelExecutorFactory