import sys
from .bot import logger, bot, dp
from aiogram import Dispatcher, executor

if sys.version_info < (3, 10, 0):
    logger.critical('your python version is too low. Install version 3.10+')
    sys.exit(1)