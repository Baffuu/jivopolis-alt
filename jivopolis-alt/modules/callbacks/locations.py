import contextlib
import random
import asyncio

from ...database import cur

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from ...resources import RESOURCES


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
    Callback for cow milking

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


async def mineshaft(call: CallbackQuery):
    '''
    Callback for mineshaft menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    pickaxe = cur.select("pickaxe", "userdata").where(user_id=user_id).one()
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place != 'Посёлок Горный':
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
            text='⛏ В шахту',
            callback_data='go_mining'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    await call.message.answer(
        '<i>⛏ <b>Добро пожаловать в Шахту!</b>\n\n'
        'Здесь вы можете подоить свою корову и получить молоко. '
        'Процесс добычи занимает не более 1 минуту, при этом у вас '
        'забирается одна кирка. А взамен вы получаете полезные '
        'ископаемые для продажи и опыт.\n\n'
        f'⛏ У вас <b>{pickaxe}</b> кирок</i>',
        reply_markup=markup
    )


async def go_mining(call: CallbackQuery):
    '''
    Callback for mining

    :param call - callback:
    '''
    user_id = call.from_user.id
    pickaxe = cur.select("pickaxe", "userdata").where(user_id=user_id).one()
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place != 'Посёлок Горный':
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

    if pickaxe < 1:
        return await call.answer(
                text=(
                    '❌ У вас нет кирок. Их можно купить в Агзамогорске'
                ),
                show_alert=True
            )

    await call.answer(
        text='⛏ Поход в шахту начался... Подождите 30-60 секунд',
        show_alert=True
    )

    cur.update("userdata").add(pickaxe=-1).where(user_id=user_id).commit()
    await asyncio.sleep(random.randint(1, 2))

    text = ''
    luck = 0
    for resource in RESOURCES:
        name = RESOURCES[resource].ru_name
        chance = RESOURCES[resource].chance
        maximum = RESOURCES[resource].maximum
        if random.uniform(0, 1) < chance:
            amount = random.randint(1, maximum)
            text += f'\n{name} - <b>{amount}</b>'
            if resource in ['iron', 'gold']:
                luck = 1
            elif resource in ['gem', 'topaz']:
                luck = 2
            cur.update("userdata").add(**{resource: amount}).where(
                user_id=user_id).commit()

    points = random.randint(2, 4)
    cur.update("userdata").add(xp=points).where(
                user_id=user_id).commit()

    if text == '':
        text = (
            '😓 Вы не добыли никаких ископаемых.'
        )
    else:
        match (luck):
            case 0:
                additional_text = 'Вам сегодня не везёт. Вот, что вы добыли:'
            case 1:
                additional_text = 'Вы сегодня в ударе! Вот, что вы добыли:'
            case 2:
                additional_text = 'Вам крупно повезло! Вот, что вы добыли:'
        text = f'<b>{additional_text}</b>\n{text}'

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text='⛏ Заново',
            callback_data='go_mining'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в шахту',
            callback_data='mineshaft'
        )
    )
    with contextlib.suppress(Exception):
        await call.message.delete()
    await call.message.answer(
        f'<i>{text}\n\n💡 Полученные очки опыта: <b>{points}</b></i>',
        reply_markup=markup
    )


async def resource_market(call: CallbackQuery) -> None:
    '''
    Callback for mineral collection point

    :param call - callback:
    '''
    user_id = call.from_user.id
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if place != 'Глинянка':
        return await call.answer(
            text=(
                '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                'местности'
            ),
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1)
    resourcelist = []

    for resource in RESOURCES:
        if isinstance(RESOURCES[resource].cost, int):
            cost = RESOURCES[resource].cost
            assert isinstance(cost, int)
            amount = cur.select(resource, "userdata").where(
                user_id=user_id).one()
            if amount >= 1:
                resourcelist.append(
                    InlineKeyboardButton(
                        text=f'{RESOURCES[resource].ru_name}'
                             f' (x{amount}) - ${cost}',
                        callback_data=f'sellresource_{resource}'
                    )
                )

    if not resourcelist:
        desc = '🚫 У вас нет ресурсов для продажи'
    else:
        markup.add(*resourcelist)
        desc = (
            '<b>🏬 Пункт сбора</b> - место, в котором можно продать '
            'полезные ископаемые, добытые в шахте. Очень удобно!\n\n❗ Зд'
            'есь вы <b>продаёте</b> ресурсы государству, а не покупаете. Де'
            'ньги вы получаете автоматически, а ресурсы никому не достаются'
        )
    markup.add(
        InlineKeyboardMarkup(
            text='◀ Назад в город',
            callback_data='city'
        )
    )
    await call.message.answer(f'<i>{desc}</i>', reply_markup=markup)
