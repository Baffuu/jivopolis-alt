from .. import Dispatcher
from ..filters import RequireBetaFilter
from aiogram.types import Message
import contextlib
from ..database import cur


async def delete_location(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1 and (
                cur.select("filter_location", "clandata")
                .where(clan_id=message.chat.id)
                .one()
            ):
        with contextlib.suppress(Exception):
            return await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(
        delete_location,
        RequireBetaFilter(),
        content_types=['location']
    )
