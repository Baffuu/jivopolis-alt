import contextlib
import random
import asyncio

from ... import utils

from ...database import cur
from ...database.functions import (
    achieve, cancel_button, get_weather, Weather, weather_damage
)

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from ...misc import current_time, get_time_units

from ...misc.config import countries, capitals, oscar_levels

from ...resources import RESOURCES
from ...items import ITEMS


async def farm(call: CallbackQuery):
    '''
    Callback for farm menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    cow = cur.select("cow", "userdata").where(user_id=user_id).one()
    milk = cur.select("milk", "userdata").where(user_id=user_id).one()

    if not await utils.check_current(user_id, "Роща", call):
        return

    markup = InlineKeyboardMarkup(row_width=1).add(
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

    if not await utils.check_current(user_id, "Роща", call):
        return

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

    if not await utils.check_current(user_id, "Посёлок Горный", call):
        return

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
        'Здесь вы можете копать полезные материалы. '
        'Процесс добычи занимает не более 1 минуты, при этом у вас '
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

    if not await utils.check_current(user_id, "Посёлок Горный", call):
        return

    if current_time() - cur.select("last_mine", "userdata").where(
            user_id=user_id).one() < 60:
        return await call.answer(
            "😠 Пользоваться шахтой можно не чаще чем раз в минуту",
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
    cur.update("userdata").add(last_mine=current_time()).where(
        user_id=user_id).commit()
    await asyncio.sleep(random.randint(30, 60))

    text = ''
    luck = 0
    for key in RESOURCES:
        resource = RESOURCES[key]
        if not resource.chance:
            continue
        if random.uniform(0, 1) < resource.chance:
            amount = random.randint(1, resource.maximum)
            text += f'\n{resource.ru_name} - <b>{amount}</b>'
            if key in ['iron', 'gold']:
                luck = 1
            elif key in ['gem', 'topaz']:
                luck = 2
            cur.update("userdata").add(**{key: amount}).where(
                user_id=user_id).commit()

    points = random.randint(2, 4)
    cur.update("userdata").add(xp=points).where(
                user_id=user_id).commit()

    if text == '':
        text = '😓 Вы не добыли никаких ископаемых.'
    else:
        match (luck):
            case 0:
                additional_text = 'Вам сегодня не везёт. Вот, что вы добыли:'
            case 1:
                additional_text = 'Вы сегодня в ударе! Вот, что вы добыли:'
            case 2:
                additional_text = 'Вам крупно повезло! Вот, что вы добыли:'
        text = f'<b>{additional_text}</b>\n{text}'

    markup = InlineKeyboardMarkup(row_width=1).add(
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


async def factory(call: CallbackQuery):
    '''
    Callback for factory menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    times = cur.select("gears_today", "userdata").where(user_id=user_id).one()

    await utils.check_places(user_id, call, 'Борисовский завод',
                             'Котайский электрозавод')

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='⚙ Шестерёнки',
            callback_data='play_gears'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    await call.message.answer(
        '<i>🏭 <b>Добро пожаловать на Завод</b>\nЗдесь вы можете заработать'
        ' немного денег.\n\nВыберите мини-игру. Учтите, что у вас должно быть'
        ' не менее $10 на балансе, чтобы играть.\n\nИграть можно не более '
        f'10 раз в день. Сегодня вы уже играли <b>{times}</b> раз</i>',
        reply_markup=markup
    )


async def play_gears(call: CallbackQuery):
    '''
    Callback for a gears game

    :param call - callback:
    '''
    user_id = call.from_user.id
    times = cur.select("gears_today", "userdata").where(user_id=user_id).one()
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    await utils.check_places(user_id, call, 'Борисовский завод',
                             'Котайский электрозавод')

    if balance < 10:
        return await call.answer(
            text='❌ Вам нужно хотя бы $10, чтобы начать игру',
            show_alert=True
        )

    if times >= 10:
        return await call.answer(
            text=(
                '❌ В Шестерёнки можно играть не более 10 раз в день'
            ),
            show_alert=True
        )
    cur.update("userdata").add(gears_today=1).where(user_id=user_id).commit()

    direction = random.choice(['left', 'right'])
    arrow = '↩' if direction == 'left' else '↪'
    amount = random.randint(2, 7)

    markup = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(
            text='↩',
            callback_data=f'answer_gears left {direction} {amount}'
        ),
        InlineKeyboardButton(
            text='↪',
            callback_data=f'answer_gears right {direction} {amount}'
        )
    )

    question = (
        '<b>В какую сторону будет вращаться белый круг?</b>\n\n'
        f'{arrow}{"⚙"*amount}⚪'
    )
    task_message = await call.message.answer(
        f'<i>{question}</i>',
        reply_markup=markup
    )

    for seconds in range(10):
        if cur.select("task_message", "userdata").where(
                user_id=user_id).one() == task_message['message_id']:
            return
        await task_message.edit_text(
            f'<i>{question}\n\nОтветьте на вопрос, пока все квадратики не '
            f'заполнятся:\n{"🔳"*seconds}{"⬜"*(9-seconds)}\n\n'
            '💲 Награда за верный ответ: <b>$15</b></i>',
            reply_markup=markup
        )
        await asyncio.sleep(1)

    if cur.select("task_message", "userdata").where(
            user_id=user_id).one() != task_message['message_id']:
        no_answer_markup = InlineKeyboardMarkup(row_width=2)
        if (
            (amount % 2 == 1 and dir == 'left')
            or (amount % 2 == 0 and dir == 'right')
        ):
            correct_answer = '↩'
            no_answer_markup.add(
                InlineKeyboardButton(
                    text='↩✅',
                    callback_data='late_answer'
                ),
                InlineKeyboardButton(
                    text='↪❌',
                    callback_data='late_answer'
                )
            )
        else:
            correct_answer = '↪'
            no_answer_markup.add(
                InlineKeyboardButton(
                    text='↩❌',
                    callback_data='late_answer'
                ),
                InlineKeyboardButton(
                    text='↪✅',
                    callback_data='late_answer'
                )
            )
        no_answer_markup.add(
            InlineKeyboardButton(
                text='🔄 Заново',
                callback_data='play_gears'
            )
        )

        cur.update("userdata").add(balance=-10).where(user_id=user_id).commit()

        await task_message.edit_text(
            f'<i>{question}\n\n<b>Правильный ответ: {correct_answer}</b>'
            '\n\n<code>Вы не ответили на вопрос.\n💲 Штраф за отсутствие '
            'ответа: $10</code></i>',
            reply_markup=no_answer_markup
        )
        await call.answer('Раунд закончен')


async def answer_gears(call: CallbackQuery,
                       answer: str, direction: str, amount: int):
    '''
    Callback for a gears game answer

    :param call - callback:
    :param answer - user's answer:
    :param direction - direction of the first arrow in the question:
    :param amount - amount of gears in the question:
    '''
    user_id = call.from_user.id
    times = cur.select("gears_today", "userdata").where(user_id=user_id).one()
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    await utils.check_places(user_id, call, 'Борисовский завод',
                             'Котайский электрозавод')

    if balance < 10:
        return await call.answer(
            text=(
                '❌ Вам нужно хотя бы $10, чтобы начать игру'
            ),
            show_alert=True
        )

    if times >= 10:
        return await call.answer(
            text=(
                '❌ В Шестерёнки можно играть не более 10 раз в день'
            ),
            show_alert=True
        )

    cur.update("userdata").set(task_message=call.message.message_id).where(
        user_id=user_id).commit()

    if amount % 2 == 1:
        correct_answer = direction
    else:
        correct_answer = 'left' if direction == 'right' else 'right'
    correct_arrow = '↩' if correct_answer == 'left' else '↪'
    direction_arrow = '↩' if direction == 'left' else '↪'

    left_text = '↩'
    right_text = '↪'

    if correct_answer == answer:
        if answer == 'left':
            left_text = '↩✅'
        else:
            right_text = '↪✅'
        reward = 15
        reward_text = 'Вы ответили верно.\n💲 Награда: $15'
    else:
        if answer == 'left':
            left_text = '↩❌'
        else:
            right_text = '↪❌'
        reward = -10
        reward_text = 'Вы ответили неверно.\n💲 Штраф: $10'

    markup = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(
            text=left_text,
            callback_data='late_answer'
        ),
        InlineKeyboardButton(
            text=right_text,
            callback_data='late_answer'
        ),
        InlineKeyboardButton(
            text='🔄 Заново',
            callback_data='play_gears'
        )
    )

    cur.update("userdata").add(balance=reward).where(user_id=user_id).commit()

    await call.message.edit_text(
        '<i><b>В какую сторону будет вращаться белый круг?</b>\n\n'
        f'{direction_arrow}{"⚙"*amount}⚪\n\n<b>Правильный ответ: </b>'
        f'{correct_arrow}\n\n<code>{reward_text}</code></i>',
        reply_markup=markup
    )
    await call.answer('Раунд закончен')


async def university(call: CallbackQuery):
    '''
    Callback for university menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    await utils.check_places(user_id, call, 'Университет',
                             'Борисовская гимназия', 'Средняя школа Смиловичей')

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='🗺 География',
            callback_data='play_geo'
        ) if current_place == 'Университет' else
        InlineKeyboardButton(
            text='➕ Математика',
            callback_data='play_math'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    match(current_place):
        case 'Университет':
            school_name = 'Университет'
        case 'Борисовская гимназия':
            school_name = 'Гимназию'
        case 'Средняя школа Смиловичей':
            school_name = 'Школу'

    await call.message.answer(
        f'<i><b>🏫 Добро пожаловать в {school_name}</b>\nЗдесь вы можете'
        ' получить опыт.\n\nВыберите мини-игру. Учтите, что у вас должно'
        ' быть не менее $10 на балансе, чтобы играть</i>',
        reply_markup=markup
    )


async def play_math(call: CallbackQuery):
    '''
    Callback for a math game

    :param call - callback:
    '''
    user_id = call.from_user.id
    last_math = cur.select("last_math", "userdata").where(
        user_id=user_id).one()
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    await utils.check_places(user_id, call, 'Борисовская гимназия',
                             'Средняя школа Смиловичей')

    if balance < 10:
        return await call.answer(
            text=(
                '❌ Вам нужно хотя бы $10, чтобы начать игру'
            ),
            show_alert=True
        )

    if current_time() - last_math < 3600 * 4:
        hours, minutes, seconds = get_time_units(
            20 * 3600 + current_time() - last_math)
        return await call.answer(
                text=(
                    '❌ Вы были наказаны за неверный ответ. Вы сможете'
                    f' играть только через {hours} часов {minutes} минут'
                    f' {seconds} секунд'
                ),
                show_alert=True
            )

    number_1 = random.randint(25, 300)
    number_2 = random.randint(25, 300)
    operator = random.choice(['+', '-'])
    correct_answer = eval(f'{number_1}{operator}{number_2}')
    if random.uniform(0, 1) < 0.35:
        suggestion = correct_answer
    else:
        suggestion = correct_answer + random.randint(-30, 30)

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(
            text='Да',
            callback_data=f'answer_math yes {number_1} {operator} '
                          f'{number_2} {suggestion}'
        ),
        InlineKeyboardButton(
            text='Нет',
            callback_data=f'answer_math no {number_1} {operator} '
                          f'{number_2} {suggestion}'
        )
    )

    question = (
        '<b>Верно ли утверждение?</b>\n\n'
        f'{number_1}{operator}{number_2}={suggestion}'
    )
    task_message = await call.message.answer(
        f'<i>{question}</i>',
        reply_markup=markup
    )

    for seconds in range(10):
        if (
            cur.select("task_message", "userdata").where(
                user_id=user_id).one() == task_message['message_id']
        ):
            return
        await task_message.edit_text(
            f'<i>{question}\n\nОтветьте на вопрос, пока все квадратики не '
            f'заполнятся:\n{"🔳"*seconds}{"⬜"*(9-seconds)}\n\n'
            '💡 Награда за верный ответ: <b>4 очка</b></i>',
            reply_markup=markup
        )
        await asyncio.sleep(1)

    if (
        cur.select("task_message", "userdata").where(
            user_id=user_id).one() != task_message['message_id']
    ):
        no_answer_markup = InlineKeyboardMarkup(row_width=2)
        if (suggestion == correct_answer):
            answer = 'Да'
            no_answer_markup.add(
                InlineKeyboardButton(
                    text='Да✅',
                    callback_data='late_answer'
                ),
                InlineKeyboardButton(
                    text='Нет❌',
                    callback_data='late_answer'
                )
            )
        else:
            question = (
                f'<b>Верно ли утверждение?</b>\n\n{number_1}{operator}'
                f'{number_2}=<s>{suggestion}</s> <b>{correct_answer}</b>'
            )
            answer = 'Нет'
            no_answer_markup.add(
                InlineKeyboardButton(
                    text='Да❌',
                    callback_data='late_answer'
                ),
                InlineKeyboardButton(
                    text='Нет✅',
                    callback_data='late_answer'
                )
            )
        no_answer_markup.add(
            InlineKeyboardButton(
                text='🔄 Заново',
                callback_data='play_math'
            )
        )

        cur.update("userdata").add(balance=-10).where(user_id=user_id).commit()
        cur.update("userdata").add(last_math=current_time()).where(
            user_id=user_id).commit()

        await task_message.edit_text(
            f'<i>{question}\n\nПравильный ответ: <b>{answer}</b>\n\n'
            '<code>Вы не ответили на вопрос.\n'
            '💲 Штраф за отсутствие ответа: $10</code></i>',
            reply_markup=no_answer_markup
        )
        await call.answer('Раунд закончен')


async def answer_math(call: CallbackQuery,
                      answer: str, number_1: int, operator: str,
                      number_2: str, suggestion: int):
    '''
    Callback for a math game answer

    :param call - callback:
    :param answer - user's answer:
    :param number_1 - the 1st number:
    :param operator - the operation performed:
    :param number_2 - the 2nd number:
    :param suggestion - the right side of the suggested equation:
    '''
    user_id = call.from_user.id
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    await utils.check_places(user_id, call, 'Борисовская гимназия',
                             'Средняя школа Смиловичей')

    if balance < 10:
        return await call.answer(
                text=(
                    '❌ Вам нужно хотя бы $10, чтобы начать игру'
                ),
                show_alert=True
            )

    cur.update("userdata").set(task_message=call.message.message_id).where(
        user_id=user_id).commit()

    correct_number = eval(f'{number_1}{operator}{number_2}')
    correct_answer = 'yes' if correct_number == suggestion else 'no'
    ru_answer = 'Да' if correct_answer == 'yes' else 'Нет'

    left_text = 'Да'
    right_text = 'Нет'

    if correct_answer == answer:
        emoji = "✅"
        reward_text = 'Вы ответили верно.\n💡 Награда: 4 очка'

        cur.update("userdata").add(xp=4).where(user_id=user_id).commit()
    else:
        emoji = "❌"
        reward_text = 'Вы ответили неверно.\n💲 Штраф: $10'

        cur.update("userdata").add(balance=-10).where(
            user_id=user_id).commit()
        cur.update("userdata").add(last_math=current_time()).where(
            user_id=user_id).commit()

    left_text += f' {emoji}' if answer == 'yes' else ""
    right_text += f" {emoji}" if answer == "no" else ""

    if correct_answer == 'yes':
        question = (
            f'<b>Верно ли утверждение?</b>\n\n{number_1}{operator}'
            f'{number_2}={suggestion}'
        )
    else:
        question = (
            f'<b>Верно ли утверждение?</b>\n\n{number_1}{operator}'
            f'{number_2}=<s>{suggestion}</s> <b>{correct_number}</b>'
        )

    markup = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(
            text=left_text,
            callback_data='late_answer'
        ),
        InlineKeyboardButton(
            text=right_text,
            callback_data='late_answer'
        ),
        InlineKeyboardButton(
            text='🔄 Заново',
            callback_data='play_math'
        )
    )

    await call.message.edit_text(
        f'<i>{question}\n\nПравильный ответ: <b>{ru_answer}</b>'
        f'\n\n<code>{reward_text}</code></i>',
        reply_markup=markup
    )
    await call.answer('Раунд закончен')


async def play_geo(call: CallbackQuery):
    '''
    Callback for a geography game

    :param call - callback:
    '''
    user_id = call.from_user.id
    last_geography = cur.select("last_geography", "userdata").where(
        user_id=user_id).one()
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    if not await utils.check_current(user_id, "Университет", call):
        return

    if balance < 10:
        return await call.answer(
            text=(
                '❌ Вам нужно хотя бы $10, чтобы начать игру'
            ),
            show_alert=True
        )

    if current_time() - last_geography < 3600 * 4:
        hours, minutes, seconds = get_time_units(
            20 * 3600 + current_time() - last_geography)
        return await call.answer(
            text=(
                '❌ Вы были наказаны за неверный ответ. Вы сможете'
                f' играть только через {hours} часов {minutes} минут'
                f' {seconds} секунд'
            ),
            show_alert=True
        )

    country = random.randint(0, len(countries) - 1)
    if random.uniform(0, 1) < 0.4:
        capital = country
    else:
        lower_border = country - 6 if country >= 6 else 0
        if country <= len(countries) - 7:
            upper_border = country + 6
        else:
            upper_border = len(countries) - 1
        capital = random.randint(lower_border, upper_border)

    markup = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(
            text='Да',
            callback_data=f'answer_geo yes {country} {capital}'
        ),
        InlineKeyboardButton(
            text='Нет',
            callback_data=f'answer_geo no {country} {capital}'
        )
    )

    question = (
        '<b>Верно ли утверждение?</b>\n\n'
        f'Столица государства {countries[country]} - '
        f'<b>{capitals[capital]}</b>'
    )
    task_message = await call.message.answer(
        f'<i>{question}</i>',
        reply_markup=markup
    )

    for seconds in range(7):
        if (
            cur.select("task_message", "userdata").where(
                user_id=user_id).one() == task_message['message_id']
        ):
            return
        await task_message.edit_text(
            f'<i>{question}\n\nОтветьте на вопрос, пока все квадратики не '
            f'заполнятся:\n{"🔳"*seconds}{"⬜"*(6-seconds)}\n\n'
            '💡 Награда за верный ответ: <b>4 очка</b></i>',
            reply_markup=markup
        )
        await asyncio.sleep(1)

    if cur.select("task_message", "userdata").where(
            user_id=user_id).one() != task_message['message_id']:
        no_answer_markup = InlineKeyboardMarkup(row_width=2)
        if (capital == country):
            answer = 'Да'
            no_answer_markup.add(
                InlineKeyboardButton(
                    text='Да✅',
                    callback_data='late_answer'
                ),
                InlineKeyboardButton(
                    text='Нет❌',
                    callback_data='late_answer'
                )
            )
        else:
            question = (
                '<b>Верно ли утверждение?</b>\n\nСтолица государства '
                f'{countries[country]} - <s>{capitals[capital]}</s> '
                f'<b>{capitals[country]}</b>.\n\n<b>{capitals[capital]}</b> - '
                f'столица государства <b>{countries[capital]}</b>'
            )
            answer = 'Нет'
            no_answer_markup.add(
                InlineKeyboardButton(
                    text='Да❌',
                    callback_data='late_answer'
                ),
                InlineKeyboardButton(
                    text='Нет✅',
                    callback_data='late_answer'
                )
            )
        no_answer_markup.add(
            InlineKeyboardButton(
                text='🔄 Заново',
                callback_data='play_geo'
            )
        )

        cur.update("userdata").add(balance=-10).where(user_id=user_id).commit()
        cur.update("userdata").add(last_geography=current_time()).where(
            user_id=user_id).commit()

        await task_message.edit_text(
            f'<i>{question}\n\nПравильный ответ: <b>{answer}</b>\n\n'
            '<code>Вы не ответили на вопрос.\n'
            '💲 Штраф за отсутствие ответа: $10</code></i>',
            reply_markup=no_answer_markup
        )
        await call.answer('Раунд закончен')


async def answer_geo(call: CallbackQuery,
                     answer: str, country: int, capital: int):
    '''
    Callback for a math game answer

    :param call - callback:
    :param answer - user's answer:
    :param country - index of the country:
    :param capital - index of the capital:
    '''
    user_id = call.from_user.id
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    if not await utils.check_current(user_id, "Университет", call):
        return

    if balance < 10:
        return await call.answer(
            text=(
                '❌ Вам нужно хотя бы $10, чтобы начать игру'
            ),
            show_alert=True
        )

    cur.update("userdata").set(task_message=call.message.message_id).where(
        user_id=user_id).commit()

    correct_answer = 'yes' if country == capital else 'no'
    ru_answer = 'Да' if correct_answer == 'yes' else 'Нет'

    left_text = 'Да'
    right_text = 'Нет'

    if correct_answer == answer:
        if answer == 'yes':
            left_text = 'Да✅'
        else:
            right_text = 'Нет✅'
        reward_text = 'Вы ответили верно.\n💡 Награда: 4 очка'
        cur.update("userdata").add(xp=4).where(user_id=user_id).commit()
    else:
        if answer == 'yes':
            left_text = 'Да❌'
        else:
            right_text = 'Нет❌'
        reward_text = 'Вы ответили неверно.\n💲 Штраф: $10'
        cur.update("userdata").add(balance=-10).where(
            user_id=user_id).commit()
        cur.update("userdata").add(last_math=current_time()).where(
            user_id=user_id).commit()

    if correct_answer == 'yes':
        question = (
            '<b>Верно ли утверждение?</b>\n\n'
            f'Столица государства {countries[country]} - '
            f'<b>{capitals[capital]}</b>'
        )
    else:
        question = (
            '<b>Верно ли утверждение?</b>\n\nСтолица государства '
            f'{countries[country]} - <s>{capitals[capital]}</s> '
            f'<b>{capitals[country]}</b>.\n\n<b>{capitals[capital]}</b> - '
            f'столица государства <b>{countries[capital]}</b>'
        )

    markup = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(
            text=left_text,
            callback_data='late_answer'
        ),
        InlineKeyboardButton(
            text=right_text,
            callback_data='late_answer'
        ),
        InlineKeyboardButton(
            text='🔄 Заново',
            callback_data='play_geo'
        )
    )

    await call.message.edit_text(
        f'<i>{question}\n\nПравильный ответ: <b>{ru_answer}</b>'
        f'\n\n<code>{reward_text}</code></i>',
        reply_markup=markup
    )
    await call.answer('Раунд закончен')


async def fishing(call: CallbackQuery):
    '''
    Callback for fishing menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    rods = cur.select("fishing_rod", "userdata").where(
        user_id=user_id).one()

    if not await utils.check_current(user_id, "Морской", call):
        return

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='🛍 Купить снасти',
            callback_data='rod_shop'
        ),
        InlineKeyboardButton(
            text='🎣 Рыбачить',
            callback_data='go_fishing'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    await call.message.answer(
        '<i>🐟 <b>Добро пожаловать на рыбалку!</b>\n\n'
        'Здесь вы можете поймать еду или сокровища, если повезёт. '
        'Процесс рыбалки занимает не более 30 секунд, при этом у вас '
        'забирается одна удочка. А взамен вы получаете полезные '
        'предметы и опыт.\n\n'
        f'🎣 У вас <b>{rods}</b> удочек</i>',
        reply_markup=markup
    )
    await weather_damage(user_id, call.message.chat.id)


async def go_fishing(call: CallbackQuery):
    '''
    Callback for fishing

    :param call - callback:
    '''
    user_id = call.from_user.id
    rod = cur.select("fishing_rod", "userdata").where(
        user_id=user_id).one()

    if not await utils.check_current(user_id, "Морской", call):
        return

    if current_time() - cur.select("last_fish", "userdata").where(
            user_id=user_id).one() < 60:
        return await call.answer(
            "😠 Рыбачить можно не чаще чем раз в минуту",
            show_alert=True
        )

    if rod < 1:
        return await call.answer(
            text=(
                '❌ У вас нет удочек. Их можно купить в магазине рядом'
            ),
            show_alert=True
        )

    await call.answer(
        text='🎣 Рыбалка началась... Подождите 15-30 секунд',
        show_alert=True
    )

    cur.update("userdata").add(fishing_rod=-1).where(user_id=user_id).commit()
    cur.update("userdata").set(last_fish=current_time()).where(
        user_id=user_id).commit()
    await asyncio.sleep(random.randint(7, 14))
    if await weather_damage(user_id, call.message.chat.id):
        return
    await asyncio.sleep(random.randint(7, 14))

    msg = await call.message.answer(
        "🐟 <i><b>Клюёт!</b> У вас есть 2 секунды, чтобы нажать на кнопку</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="🎣 Потянуть за удочку",
                callback_data="fish_result"
            )
        )
    )
    await asyncio.sleep(2)
    if cur.select("fish_message", "userdata").where(
            user_id=user_id).one() != msg['message_id']:
        await msg.edit_text("😥 <i>Добыча уплыла, вы не успели её поймать</i>")


async def fish_result(call: CallbackQuery):
    '''
    Callback for fishing result.

    :param call - callback:
    '''
    user_id = call.from_user.id

    cur.update("userdata").set(fish_message=call.message.message_id).where(
        user_id=user_id).commit()

    text = ''
    luck = 0
    for key in ITEMS:
        item = ITEMS[key]
        if "FISHING" not in item.tags:
            continue
        chance = float(item.tags[1].replace("CHANCE_", "")) / 100
        match (get_weather()):
            case Weather.SUNNY:
                upper_bound = 0.9
            case Weather.RAINING:
                upper_bound = 0.75
            case Weather.THUNDERSTORM:
                upper_bound = 0.6
            case Weather.HURRICANE:
                upper_bound = 0.5
            case _:
                upper_bound = 1
        if random.uniform(0, upper_bound) < chance:
            if random.randint(0, 1) == 0:
                continue
            name = item.ru_name
            emoji = item.emoji
            text += f'\n{emoji} {name}'
            if chance < 5:
                luck = 2
            elif chance < 50:
                luck = 1
            cur.update("userdata").add(**{key: 1}).where(
                user_id=user_id).commit()
            if key == "seashell":
                await achieve(
                    user_id, call.message.chat.id, "fish_achieve"
                )

    points = random.randint(1, 2)
    cur.update("userdata").add(xp=points).where(
                user_id=user_id).commit()

    if text == '':
        text = '😓 Вы не поймали ничего.'
    else:
        match (luck):
            case 0:
                additional_text = 'Вам сегодня не везёт. Вот, что вы поймали:'
            case 1:
                additional_text = 'Вы сегодня в ударе! Вот, что вы поймали:'
            case 2:
                additional_text = 'Вам сильно повезло! Вот, что вы поймали:'
        text = f'<b>{additional_text}</b>\n{text}'

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='🎣 Заново',
            callback_data='go_fishing'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться',
            callback_data='fishing'
        )
    )
    with contextlib.suppress(Exception):
        await call.message.delete()
    await call.message.answer(
        f'<i>{text}\n\n💡 Полученные очки опыта: <b>{points}</b></i>',
        reply_markup=markup
    )


async def resource_factory(call: CallbackQuery):
    '''
    Callback for resource factory menu

    :param call - callback:
    '''
    user_id = call.from_user.id

    if not await utils.check_current(user_id, "Уголь", call):
        return

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='🔁 Начать переработку',
            callback_data='process_resources'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    cobble = cur.select("cobble", "userdata").where(user_id=user_id).one()
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()
    await call.message.answer(
        '<i>🏭 <b>Добро пожаловать на перерабатывающий завод!</b>\n\n'
        'Здесь вы можете переработать булыжник, добытый в шахте, в '
        'более полезные материалы, например железо, золото и уголь.'
        '\nМожно переработать ровно 100 единиц булыжника за раз, это стоит'
        ' <b>$200</b> и длится 100 секунд\n\n'
        f'У вас <b>{cobble}</b> единиц булыжника и <b>${balance}</b></i>',
        reply_markup=markup
    )


async def process_resources(call: CallbackQuery):
    '''
    Callback for fishing

    :param call - callback:
    '''
    user_id = call.from_user.id

    if not await utils.check_current(user_id, "Уголь", call):
        return

    if current_time() - cur.select("last_proc", "userdata").where(
            user_id=user_id).one() < 120:
        return await call.answer(
            "😠 Пользоваться заводом можно не чаще чем раз в 2 минуты",
            show_alert=True
        )

    balance = cur.select("balance", "userdata").where(
        user_id=user_id).one()
    cobble = cur.select("cobble", "userdata").where(
        user_id=user_id).one()
    if cobble < 100:
        return await call.answer(
                text=(
                    '❌ У вас недостаточно булыжника'
                ),
                show_alert=True
            )
    elif balance < 200:
        return await call.answer(
                text=(
                    '❌ У вас недостаточно денег на балансе'
                ),
                show_alert=True
            )

    await call.answer(
        text='🏭 Переработка началась... Подождите 100 секунд',
        show_alert=True
    )

    cur.update("userdata").set(last_proc=current_time()).where(
        user_id=user_id).commit()
    await asyncio.sleep(100)

    coal = random.randint(1, 10)
    text = f'😉 Обработка завершена. Получено:\n\nУголь - <b>{coal}</b>'
    cur.update("userdata").add(coal=coal).where(user_id=user_id).commit()

    points = random.randint(1, 2)
    cur.update("userdata").add(xp=points).where(
        user_id=user_id).commit()
    cur.update("userdata").add(balance=-200).where(
        user_id=user_id).commit()
    cur.update("userdata").add(cobble=-100).where(
        user_id=user_id).commit()

    if iron := random.randint(0, 5):
        text += f'\nЖелезо - <b>{iron}</b>'
        cur.update("userdata").add(iron=iron).where(user_id=user_id).commit()
    if random.randint(1, 15) == 1:
        text += '\nЗолото - <b>1</b>'
        cur.update("userdata").add(gold=1).where(user_id=user_id).commit()
        await achieve(
            user_id, call.message.chat.id, "proc_achieve"
        )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text='🏭 Обработать ещё',
            callback_data='process_resources'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться',
            callback_data='resource_factory'
        )
    )
    with contextlib.suppress(Exception):
        await call.message.delete()
    await call.message.answer(
        f'<i>{text}\n\n💡 Полученные очки опыта: <b>{points}</b></i>',
        reply_markup=markup
    )


async def oscar_shop(call: CallbackQuery):
    '''
    Callback for Oscar's shop

    :param call - callback:
    '''
    user_id = call.from_user.id

    if not await utils.check_current(user_id, "Деревня Остинт", call):
        return

    markup = InlineKeyboardMarkup(row_width=1)
    purchases = cur.select("oscar_purchases", "userdata").where(
        user_id=user_id).one()
    for lvl in oscar_levels:
        if purchases < oscar_levels[lvl]:
            break
        level = RESOURCES[lvl].ru_name
        markup.add(
            InlineKeyboardButton(
                text=f"🛍 Отдел {level}",
                callback_data=f"oscar_dept_{lvl}"
            )
        )

    markup.add(
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    await call.message.answer(
        '<i>👋 <b>Добро пожаловать в лавку дяди Оскара!</b>\n\n'
        'Здесь вы можете купить некоторые полезные товары за ресурсы,'
        ' добытые в шахте.\n\nУровень ваших отношений с дядей Оскаром: '
        f'<b>{level}</b> (совершено <b>{purchases}</b> покупок)</i>',
        reply_markup=markup
    )


async def oscar_dept(call: CallbackQuery, dept: str):
    '''
    Callback for Oscar's shop department

    :param call - callback:
    :param dept - level name:
    '''
    user_id = call.from_user.id

    if not await utils.check_current(user_id, "Деревня Остинт", call):
        return

    if cur.select("oscar_purchases", "userdata").where(
            user_id=user_id).one() < oscar_levels[dept]:
        return await call.answer(
            "😑 Вы ещё не достигли такого уровня в ларьке. "
            "Покупайте больше товаров у дяди Оскара!"
        )

    level_name = RESOURCES[dept].ru_name
    markup = InlineKeyboardMarkup(row_width=1)
    oscar_items = filter(
        lambda x: f"OSCAR_SHOP_{dept.upper()}" in ITEMS[x].tags,
        ITEMS
    )
    for item in oscar_items:
        cost = ITEMS[item].cost // RESOURCES[dept].cost
        name = ITEMS[item].ru_name
        emoji = ITEMS[item].emoji
        markup.add(
            InlineKeyboardButton(
                f"{emoji} {name} - {level_name} x{cost}",
                callback_data=f"oscar_buy_{item}"
            )
        )

    markup.add(cancel_button())
    count = cur.select(dept, "userdata").where(user_id=user_id).one()

    await call.message.answer(
        '<i>👋 <b>Добро пожаловать в лавку дяди Оскара!</b>\n'
        f'Отдел <b>{level_name}</b>.\n\nЧто хотите купить? У вас '
        f'<b>{count}</b> единиц ресурса {level_name}</i>',
        reply_markup=markup
    )
