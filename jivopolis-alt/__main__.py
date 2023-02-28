from loguru import logger
import sys

from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound

from .config import log_chat
from .bot import bot, dp, Dispatcher

from .database.sqlitedb import connect_database

if sys.version_info < (3, 10, 0):
    logger.critical('your python version is too low. Install version 3.10+')
    sys.exit(1)

#loop = asyncio.get_event_loop()

async def on_startup(dp : Dispatcher):
    try:
        connect_database()
        try:
            await bot.send_message(log_chat, '✅ <i>Бот перезагружен\n#bot_reload</i>')
        except ChatNotFound:
            logger.warning('log chat not found :(\nprobably you forgot to add bot to the chat')
        logger.info('bot connected')

        from .modules import start, sqlrun, callback, on_photo_sent
        start.register(dp)
        sqlrun.register(dp)
        callback.register(dp)
        on_photo_sent.register(dp)
        
    except Exception as e:
        return logger.exception(e)

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, on_startup=on_startup, skip_updates=True)
    