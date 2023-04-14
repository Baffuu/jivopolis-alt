import asyncio
import time

from typing import Optional, List

from . import bot, dp, Dispatcher, logger
from ._async_sched import AsyncScheduler
from .database.sqlitedb import connect_database

from aiogram.utils.executor import Executor, _setup_callbacks
from aiogram.utils.exceptions import ChatNotFound


async def update():
    from ._world_updater import update
    await update()

    print("inside function")
    scheduler.enter(60, 1, update)


async def on_startup(dp : Dispatcher):
    try:
        connect_database()
        
        from .database.sqlitedb import cur, conn
        cur.execute("INSERT INTO globaldata(treasury) VALUES (0)")
        conn.commit()
        try:
            from .misc import OfficialChats
            await bot.send_message(OfficialChats.LOGCHAT, '<i>🔰 Бот успешно перезагружен. #restart</i>')
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
    from .misc import OfficialChats
    await bot.send_message(OfficialChats.LOGCHAT, '<i>❗️ Выключаюсь… #shutdown</i>')


def start_polling(reset_webhook=None, timeout=20, relax=0.1, fast=True,
                  allowed_updates: Optional[List[str]] = None):
    connect_database()
    executor._prepare_polling()
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(executor._startup_polling())
        loop.create_task(
            executor.dispatcher.start_polling(
                reset_webhook=reset_webhook, timeout=timeout,
                relax=relax, fast=fast, allowed_updates=allowed_updates
            )
        )
        scheduler.enter(10, 1, update)
        loop.create_task(scheduler.run())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        # loop.stop()
        pass
    finally:
        loop.run_until_complete(executor._shutdown_polling())
        logger.warning("Goodbye!")


if __name__ == '__main__':
    scheduler = AsyncScheduler(time.time, asyncio.sleep)
    executor = Executor(dp, skip_updates=True)
    _setup_callbacks(executor, on_startup, on_shutdown)
    start_polling()