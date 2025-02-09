from .. import dp, logger, tglog
from ..misc import constants
from aiogram.types import Update


@dp.errors_handler()
async def exception_handler(update: Update, exc_desc: str):
    print(update)
    if hasattr(update, "message"):
        print(update.message)
        event = "message"
        if exc_desc == "None type object is not subscriptable":
            await update.message.reply(
                "🧑‍🎨 <i>Сэр, у вас нет аккаунта в Живополисе. Прежде чем "
                "использовать любые команды, вам нужно зарегистрироваться</i>"
            )
        else:
            await update.message.answer(
                constants.ERROR_MESSAGE.format(exc_desc)
            )

    if hasattr(update, "callback_query"):
        event = "callback_query" # noqa
        if exc_desc == "None type object is not subscriptable":
            logger.exception(exc_desc)
            await update.callback_query.answer(
                "🧑‍🎨 <i>Сэр, у вас нет аккаунта в Живополисе. Прежде чем "
                "использовать любые команды, вам нужно зарегистрироваться</i>",
                show_alert=True
            )
    await tglog(f"🐙 Exception:<code> {exc_desc}</code>.", "#exception")
    logger.exception(exc_desc)
