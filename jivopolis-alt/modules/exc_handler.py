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
            await update.message.reply("🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые комманды вам нужно зарегистрироваться.")
        else:
            await update.message.answer(constants.ERROR_MESSAGE.format(exc_desc))
    if hasattr(update, "callback_query"):
        event = "callback_query"
        if exc_desc == "None type object is not subscriptable":
            logger.exception(exc_desc)
            await update.callback_query.answer("🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые комманды вам нужно зарегистрироваться.", show_alert=True)
    await tglog(f"🐙 Exception:<code> {exc_desc}</code>.", "#exception")
    logger.exception(exc_desc)

