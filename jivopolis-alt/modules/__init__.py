from types import ModuleType
from . import (
    callback,
    admin_commands,
    inline_bot,
    on_photo_sent,
    start,
    stickers_handler,
    emoji_handler,
    payments,
    new_member_handler,
    message_handlers
)
from .. import Dispatcher, marketplace


async def register_all(dp: Dispatcher) -> tuple[ModuleType]:  # -> None:
    """
    function to register all bot hadlers

    handlers:
        - callback
        - inline bot
        - photo handler
        - start command
        - stickers handler
        - commands for admins
    """
    marketplace.register(dp)
    start.register(dp)
    callback.register(dp)
    admin_commands.register(dp)
    inline_bot.register(dp)
    on_photo_sent.register(dp)
    stickers_handler.register(dp)
    emoji_handler.register(dp)

    return (
        start,
        callback,
        admin_commands,
        inline_bot,
        on_photo_sent,
        stickers_handler,
        emoji_handler,
        new_member_handler,
        message_handlers,
        payments,
        marketplace
    )
