import sys
from loguru import logger
from .bot import bot, dp
from aiogram import Dispatcher

if sys.version_info < (3, 10, 0):
    logger.critical('your python version is too low. Install version 3.10+')
    sys.exit(1)

def _debug_only(record):
    return record["level"].name == "DEBUG"
def _not_debug(record):
    return record["level"].name != "DEBUG"
logger.add("debug.log", filter=_debug_only, rotation="10000 MB")
logger.add(".log", filter=_not_debug, rotation="10000 MB")

import time
init_ts = time.perf_counter()
