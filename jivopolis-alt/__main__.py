from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound

from .config import log_chat
from .bot import bot, dp, Dispatcher, logger

from .database.sqlitedb import connect_database

#loop = asyncio.get_event_loop()

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

        from .modules import start, admin_commands, callback, on_photo_sent, stickers_handler, inline_bot
        start.register(dp)
        admin_commands.register(dp)
        callback.register(dp)
        on_photo_sent.register(dp)
        stickers_handler.register(dp)
        inline_bot.register(dp)
        
    except Exception as e:
        return logger.exception(e)

async def on_shutdown(dp: Dispatcher):
    from .database.sqlitedb import cur, conn
    cur.close(); conn.close()
    await bot.send_message(log_chat, '<i>❗️ Выключаюсь… #shutdown</i>')
    return logger.warning('Goodbye...')

if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)