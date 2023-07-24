from .. import dp, Dispatcher
from ..filters import RequireBetaFilter
from aiogram.types import Message
import contextlib
from ..database import cur


@dp.message_handler(content_types=['voice'])
async def delete_voice_messages(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1:
        dice = cur.select("filter_voice", "clandata").where(
            clan_id=message.chat.id).one()
        if dice:
            with contextlib.suppress(Exception):
                return await message.delete()


@dp.message_handler(content_types=['video_note'])
async def delete_video_messages(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1:
        dice = cur.select("filter_video", "clandata").where(
            clan_id=message.chat.id).one()
        if dice:
            with contextlib.suppress(Exception):
                return await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(
        delete_voice_messages,
        RequireBetaFilter(),
        content_types=['voice']
    )
    dp.register_message_handler(
        delete_video_messages,
        RequireBetaFilter(),
        content_types=['video_note']
    )
