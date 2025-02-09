from .. import Dispatcher
from aiogram.types import Message
import contextlib
from ..database import cur
from ..filters import RequireBetaFilter


async def delete_files(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1 and (
                cur.select("filter_document", "clandata")
                .where(clan_id=message.chat.id)
                .one()
            ):
        with contextlib.suppress(Exception):
            return await message.delete()


async def delete_gifs(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1 and (
                cur.select("filter_gif", "clandata")
                .where(clan_id=message.chat.id)
                .one()
            ):
        with contextlib.suppress(Exception):
            return await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(
            delete_files,
            RequireBetaFilter(),
            content_types=['document']
        )
    dp.register_message_handler(
            delete_gifs,
            RequireBetaFilter(),
            content_types=['animation']
        )
