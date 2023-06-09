from .. import dp, bot
from ..misc.constants import BETATEST_MINIMUM_RANK
from ..database import cur
from aiogram.types import Message


@dp.message_handler(content_types=['new_chat_members'])
async def welcome_new_member(message: Message):
    bot_ = await bot.get_me()
    bot_id = bot_.id
    if message.new_chat_members[0].id == bot_id:
        rank = cur.select('rank', "userdata").where(
            user_id=message.from_user.id).one()
        if rank < BETATEST_MINIMUM_RANK:
            await bot.leave_chat(message.chat.id)
