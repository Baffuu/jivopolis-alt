from . import (
    callback,
    admin_commands,
    inline_bot,
    on_photo_sent,
    start,
    stickers_handler,
    emoji_handler,
)
from .. import Dispatcher

async def register_all(dp: Dispatcher) -> None:
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
    callback.register(dp)
    admin_commands.register(dp)
    inline_bot.register(dp)
    on_photo_sent.register(dp)
    start.register(dp)
    stickers_handler.register(dp)
    emoji_handler.register(dp)