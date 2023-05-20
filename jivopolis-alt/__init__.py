import sys
import time

from loguru import logger, Record
from .bot import bot, dp, PPT
from aiogram import Dispatcher

if sys.version_info < (3, 10, 0):
    logger.critical('your python version is too low. Install version 3.10+')
    sys.exit(1)

try:
    import asyncio
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except Exception as e:
    raise ImportError("Please, install uvloop.") from e

from .database import cur, conn
from .misc import *  # noqa: F401, F403 # * todo: remove it


def _debug_only(record: Record):
    return record["level"].name == "DEBUG"


def _not_debug(record: Record):
    return record["level"].name != "DEBUG"


logger.add("debug.log", filter=_debug_only, rotation="10000 MB")
logger.add(".log", filter=_not_debug, rotation="10000 MB")

init_ts = time.perf_counter()

__all__ = ["bot", "dp", "PPT", "Dispatcher", "cur", "conn"]
