import contextlib
import random
import asyncio

from ...database import cur

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from ...misc import current_time, get_time_units

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
    await asyncio.sleep(random.randint(30, 60))

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


async def factory(call: CallbackQuery):
    '''
    Callback for factory menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    times = cur.select("gears_today", "userdata").where(user_id=user_id).one()
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place not in ['Ридипольский завод', 'Котайский электрозавод']:
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
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place not in ['Ридипольский завод', 'Котайский электрозавод']:
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

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
    cur.update("userdata").add(gears_today=1).where(user_id=user_id).commit()

    direction = random.choice(['left', 'right'])
    arrow = '↩' if direction == 'left' else '↪'
    amount = random.randint(2, 7)

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
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

    for seconds in range(0, 10):
        if (
            cur.select("task_message", "userdata").where(
                user_id=user_id).one() != task_message['message_id']
        ):
            await task_message.edit_text(
                f'<i>{question}\n\nОтветьте на вопрос, пока все квадратики не '
                f'заполнятся:\n{"🔳"*seconds}{"⬜"*(9-seconds)}\n\n'
                '💲 Награда за верный ответ: <b>$15</b></i>',
                reply_markup=markup
            )
            await asyncio.sleep(1)
        else:
            return

    if (
        cur.select("task_message", "userdata").where(
            user_id=user_id).one() != task_message['message_id']
    ):
        no_answer_markup = InlineKeyboardMarkup(row_width=2)
        if (amount % 2 == 1 and dir == 'left') or (
                amount % 2 == 0 and dir == 'right'):
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
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place not in ['Ридипольский завод', 'Котайский электрозавод']:
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

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

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
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

    if current_place not in ['Университет', 'Ридипольская гимназия']:
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
            text='➕ Математика',
            callback_data='play_math'
        ) if current_place == 'Ридипольская гимназия' else
        InlineKeyboardButton(
            text='🗺 География',
            callback_data='play_geo'
        ),
        InlineKeyboardButton(
            text='◀ Вернуться в город',
            callback_data='city'
        )
    )

    school_name = 'Университет' if current_place == 'Университет' \
        else 'Гимназию'

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
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place != 'Ридипольская гимназия':
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

    if balance < 10:
        return await call.answer(
                text=(
                    '❌ Вам нужно хотя бы $10, чтобы начать игру'
                ),
                show_alert=True
            )

    if current_time() - last_math < 3600*4:
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

    for seconds in range(0, 10):
        if (
            cur.select("task_message", "userdata").where(
                user_id=user_id).one() != task_message['message_id']
        ):
            await task_message.edit_text(
                f'<i>{question}\n\nОтветьте на вопрос, пока все квадратики не '
                f'заполнятся:\n{"🔳"*seconds}{"⬜"*(9-seconds)}\n\n'
                '💡 Награда за верный ответ: <b>4 очка</b></i>',
                reply_markup=markup
            )
            await asyncio.sleep(1)
        else:
            return

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
                    text='Да✅',
                    callback_data='late_answer'
                ),
                InlineKeyboardButton(
                    text='Нет❌',
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
    Callback for a gears game answer

    :param call - callback:
    :param answer - user's answer:
    :param number_1 - the 1st number:
    :param operator - the operation performed:
    :param number_2 - the 2nd number:
    :param suggestion - the right side of the suggested equation:
    '''
    user_id = call.from_user.id
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place != 'Ридипольская гимназия':
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

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
                f'<b>Верно ли утверждение?</b>\n\n{number_1}{operator}'
                f'{number_2}={suggestion}'
            )
    else:
        question = (
                f'<b>Верно ли утверждение?</b>\n\n{number_1}{operator}'
                f'{number_2}=<s>{suggestion}</s> <b>{correct_number}</b>'
            )

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
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
