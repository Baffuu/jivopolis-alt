from .. import bot, Dispatcher
from ..misc.constants import BETATEST_MINIMUM_RANK
from ..database import cur
from aiogram.types import Message
from ..filters import RequireBetaFilter
import contextlib


async def welcome_new_member(message: Message):
    bot_ = await bot.get_me()
    bot_id = bot_.id
    if message.new_chat_members[0].id == bot_id:
        rank = cur.select('rank', "userdata").where(
            user_id=message.from_user.id).one()
        if rank < BETATEST_MINIMUM_RANK:
            await bot.leave_chat(message.chat.id)

    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1:
        dice = cur.select("filter_join", "clandata").where(
            clan_id=message.chat.id).one()
        if dice:
            with contextlib.suppress(Exception):
                return await message.delete()


async def delete_leave_message(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1:
        dice = cur.select("filter_leave", "clandata").where(
            clan_id=message.chat.id).one()
        if dice:
            with contextlib.suppress(Exception):
                return await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(
            welcome_new_member,
            RequireBetaFilter(),
            content_types=['new_chat_members']
        )
    dp.register_message_handler(
            delete_leave_message,
            RequireBetaFilter(),
            content_types=['left_chat_member']
        )
