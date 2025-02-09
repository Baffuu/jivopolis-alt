from .. import Dispatcher
from aiogram.types import Message
import contextlib
from ..database import cur
from ..filters import RequireBetaFilter


async def delete_contacts(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1 and (
                cur.select("filter_contact", "clandata")
                .where(clan_id=message.chat.id)
                .one()
            ):
        with contextlib.suppress(Exception):
            return await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(
            delete_contacts,
            RequireBetaFilter(),
            content_types=['contact']
        )
