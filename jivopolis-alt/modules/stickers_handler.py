from ..database.functions import cur, conn, Message
from ..bot import bot, Dispatcher, logger
from .callbacks.inventory import open_lootbox

async def sticker_handler(message: Message):
    match (message.sticker.emoji):
        case '📦':
            return await open_lootbox(message.from_user.id, message)
    

def register(dp: Dispatcher):
    dp.register_message_handler(sticker_handler, content_types=['sticker'])