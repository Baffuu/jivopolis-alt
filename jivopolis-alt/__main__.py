# type: ignore
import asyncio
import time

from . import dp, Dispatcher, logger, FiltersFactory
from .misc import tglog
from ._async_sched import AsyncScheduler
from ._world_updater import update as _update
from .filters import RequireBetaFilter

from aiogram.utils.executor import Executor
from aiogram.utils.exceptions import ChatNotFound


async def update():
    await _update()
    scheduler.enter(60, 1, update)
    logger.debug("World was updated")


def _setup_callbacks(executor: 'Executor', on_startup=None, on_shutdown=None):
    if on_startup is not None:
        executor.on_startup(on_startup)
    if on_shutdown is not None:
        executor.on_shutdown(on_shutdown)


async def on_startup(dp: Dispatcher):
    try:
        from .database import cur, conn
        if not cur.select("count(*)", "globaldata").one():
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


def main():
    """main entrypoint"""
    FiltersFactory.bind(
        RequireBetaFilter,
        event_handlers=[
            dp.message_handlers,
            dp.callback_query_handlers
        ]
    )
    global scheduler
    scheduler = AsyncScheduler(time.time, asyncio.sleep)
    scheduler.enter(10, 1, update)

    loop = asyncio.new_event_loop()
    loop.create_task(scheduler.run())

    executor = Executor(dp, loop=loop)
    _setup_callbacks(executor, on_startup, on_shutdown)

    try:
        loop.run_until_complete(executor._startup_polling())
        loop.create_task(dp.start_polling(
            reset_webhook=None, timeout=20,
            relax=0.1, fast=True, allowed_updates=None)
        )
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        # loop.stop()
        pass
    finally:
        loop.run_until_complete(executor._shutdown_polling())
        logger.warning("Goodbye!")


if __name__ == '__main__':
    main()
