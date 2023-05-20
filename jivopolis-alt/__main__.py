# type: ignore
import asyncio
import time

from typing import Optional, List

from . import dp, Dispatcher, logger
from .misc import tglog
from ._async_sched import AsyncScheduler
from ._world_updater import update as _update
from .filters import RequireBetaFilter

from ._executor import Executor, _setup_callbacks, start_polling
from aiogram.utils.exceptions import ChatNotFound


async def update():
    await _update()
    scheduler.enter(60, 1, update)
    logger.debug("World was updated")


async def on_startup(dp: Dispatcher):
    try:
        from .database import cur, conn
        cur.execute("INSERT INTO globaldata(treasury) VALUES (0)")
        conn.commit()
        try:
            await tglog('🔰 Бот успешно перезагружен.', "#restart")
        except ChatNotFound:
            logger.warning(
                'Log chat not found :(\nprobably you forgot to add bot to the'
                ' chat'
            )

        logger.info('Bot connected')

        from . import modules
        await modules.register_all(dp)
    except Exception as e:
        return logger.exception(e)


async def on_shutdown(_: Dispatcher):
    from .database import cur, conn
    cur.close()
    conn.close()
    await tglog('❗️ Выключаюсь…', '#shutdown')


if __name__ == '__main__':
    dp.filters_factory.bind(
        RequireBetaFilter,
        event_handlers=[dp.message_handlers]
    )
    scheduler = AsyncScheduler(time.time, asyncio.sleep)
    executor = Executor(dp)
    _setup_callbacks(executor, on_startup, on_shutdown)
    executor.start_polling()
