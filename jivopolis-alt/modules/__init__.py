from . import (
    callback,
    admin_commands,
    inline_bot,
    on_photo_sent,
    start,
    stickers_handler
)
from .. import Dispatcher

async def register_all(dp: Dispatcher):
    callback.register(dp)
    admin_commands.register(dp)
    inline_bot.register(dp)
    on_photo_sent.register(dp)
    start.register(dp)
    stickers_handler.register(dp)
    