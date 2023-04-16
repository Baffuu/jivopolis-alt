import sys
from loguru import logger
from .bot import bot, dp
from aiogram import Dispatcher, executor


if sys.version_info < (3, 10, 0):
    logger.critical('your python version is too low. Install version 3.10+')
    sys.exit(1)

def debug_only(record):
    return record["level"].name == "DEBUG"
def not_debug(record):
    return record["level"].name != "DEBUG"
logger.add("debug.log", filter=debug_only, rotation="10000 MB")
logger.add(".log", filter=not_debug, rotation="10000 MB")