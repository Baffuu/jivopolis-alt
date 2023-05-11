import asyncio
import time

from typing import Optional, List

from . import dp, Dispatcher, logger, tglog
from ._async_sched import AsyncScheduler
from ._world_updater import update as _update
from .filters import RequireBetaFilter

from aiogram.utils.executor import Executor, _setup_callbacks
from aiogram.utils.exceptions import ChatNotFound

async def update():
    await _update()
    scheduler.enter(60, 1, update)
    logger.debug("World was updated")


async def on_startup(dp : Dispatcher):
    try:    
        from .database import cur, conn
        cur.execute("INSERT INTO globaldata(treasury) VALUES (0)")
        conn.commit()
        try:
            await tglog('🔰 Бот успешно перезагружен.', "#restart")
        except ChatNotFound:
            logger.warning('Log chat not found :(\nprobably you forgot to add bot to the chat')

        logger.info('Bot connected')
        
        from . import modules
        await modules.register_all(dp)
    except Exception as e:
        return logger.exception(e)


async def on_shutdown(dp: Dispatcher):
    from .database import cur, conn
    cur.close(); conn.close()
    await tglog('❗️ Выключаюсь…', '#shutdown')


def start_polling(reset_webhook=None, timeout=20, relax=0.1, fast=True,
                  allowed_updates: Optional[List[str]] = None):
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
    except asyncio.TimeoutError:
        logger.warning("TimeoutError")
    except (KeyboardInterrupt, SystemExit):
        #loop.stop()
        pass
    finally:
        loop.run_until_complete(executor._shutdown_polling())
        logger.warning("Long-polling ended succesfully.")


if __name__ == '__main__':
    dp.filters_factory.bind(
        RequireBetaFilter, 
        event_handlers=[dp.message_handlers]
    )
    scheduler = AsyncScheduler(time.time, asyncio.sleep)
    executor = Executor(dp)
    _setup_callbacks(executor, on_startup, on_shutdown)
    start_polling()
        