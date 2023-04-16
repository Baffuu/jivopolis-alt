from .. import dp, Dispatcher, bot, logger
from ..misc.constants import BETATEST_MINIMUM_RANK
from ..database.sqlitedb import cur
from aiogram.types import Message

@dp.message_handler(content_types=['new_chat_members'])
async def welcome_new_member(message: Message):
    if message.new_chat_members[0].id == bot.id:
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={message.from_user.id}").fetchone()[0]
        if rank < BETATEST_MINIMUM_RANK:
            await bot.leave_chat(message.chat.id)