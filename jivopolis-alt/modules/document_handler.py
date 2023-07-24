from .. import dp, Dispatcher
from aiogram.types import Message
import contextlib
from ..database import cur
from ..filters import RequireBetaFilter


@dp.message_handler(content_types=['document'])
async def delete_files(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1:
        dice = cur.select("filter_document", "clandata").where(
            clan_id=message.chat.id).one()
        if dice:
            with contextlib.suppress(Exception):
                return await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(
            delete_files,
            RequireBetaFilter(),
            content_types=['document']
        )
