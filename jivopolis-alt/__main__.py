import asyncio, sched, time

from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound

from .config import log_chat
from . import bot, dp, Dispatcher, logger

from .database.sqlitedb import connect_database

async def on_startup(dp : Dispatcher):
    try:
        connect_database()
        
        from .database.sqlitedb import cur, conn
        cur.execute("INSERT INTO globaldata(treasury) VALUES (0)")
        conn.commit()

        try:
            await bot.send_message(log_chat, '<i>🔰 Бот успешно перезагружен. #restart</i>')
        except ChatNotFound:
            logger.warning('log chat not found :(\nprobably you forgot to add bot to the chat')
        logger.info('bot connected')

        from . import modules
        await modules.register_all(dp)
        #await asyncio.gather(asyncio.create_task(update_loop()))
    except Exception as e:
        return logger.exception(e)


async def on_shutdown(dp: Dispatcher):
    from .database.sqlitedb import cur, conn
    cur.close(); conn.close()
    await bot.send_message(log_chat, '<i>❗️ Выключаюсь… #shutdown</i>')
    return logger.warning('Goodbye...')

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)