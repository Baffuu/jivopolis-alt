from loguru import logger
import asyncio
import sys

from aiogram.utils import executor

from .config import log_chat
from .bot import bot, dp
from .database import sqlitedb as db

if sys.version_info < (3, 8, 0):
    logger.critical('your python version is too low')
    sys.exit(1)

loop = asyncio.get_event_loop()

async def on_startup():
    try:
        db.connect_database()
        await bot.send_message(log_chat, '✅ <i>Бот перезагружен\n#bot_reload</i>', parse_mode='html')
        logger.info('bot connected')
    except Exception as e:
        return logger.exception(e)

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, on_startup=on_startup, skip_updates=True, loop=loop)