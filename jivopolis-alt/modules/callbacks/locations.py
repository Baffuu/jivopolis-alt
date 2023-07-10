import contextlib
import asyncio

from ...database import cur

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)


async def farm(call: CallbackQuery):
    '''
    Callback for farm menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    cow = cur.select("cow", "userdata").where(user_id=user_id).one()
    milk = cur.select("milk", "userdata").where(user_id=user_id).one()
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place != 'Роща':
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text='🥛 Подоить корову',
            callback_data='milk_cow'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    await call.message.answer(
        '<i>🌾 <b>Добро пожаловать на Ферму!</b>\n\n'
        'Здесь вы можете подоить свою корову и получить молоко. '
        'Процесс дойки занимает примерно 10 секунд, при этом у вас '
        'забирается одна корова. А взамен вы получаете 1 стакан молока, '
        'которое затем можете выпить.\n\n'
        f'У вас:\n 🐄 <b>{cow}</b> коров\n 🥛 <b>{milk}</b> стаканов молока</i>',
        reply_markup=markup
    )


async def milk_cow(call: CallbackQuery):
    '''
    Callback for farm menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    cow = cur.select("cow", "userdata").where(user_id=user_id).one()
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place != 'Роща':
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

    if cow < 1:
        return await call.answer(
                text=(
                    '❌ У вас нет коров. Их можно купить в зоопарке'
                ),
                show_alert=True
            )

    await call.answer(
        text='🥛 Дойка коровы началась... Подождите 10 секунд',
        show_alert=True
    )

    cur.update("userdata").add(cow=-1).where(user_id=user_id).commit()
    await asyncio.sleep(10)
    cur.update("userdata").add(milk=1).where(user_id=user_id).commit()

    with contextlib.suppress(Exception):
        await call.message.delete()
    await farm(call)
