import contextlib
import time
from ...misc import (
    Item, ITEMS,
    lootbox_open, LOOTBOX,
    get_time_units, current_time,
    RESOURCES
)
from ...misc.config import limited_items
from ..start import StartCommand
from ...database import cur
from ...database.functions import itemdata, achieve

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
)


async def itemdesc(call: CallbackQuery, user_id: int):
    '''
    Callback for item info

    :param call - callback:
    :param user_id:
    '''
    try:
        item: Item = ITEMS[call.data]
    except KeyError:
        return await call.answer('Этoт item не существует')

    count = cur.select(call.data, "userdata").where(user_id=user_id).one()

    if count < 1:
        return await call.message.answer(
            '<i>🚫 У вас нет этого предмета</i>',
        )

    mask = cur.select("mask", "userdata").where(user_id=user_id).one()

    markup = InlineKeyboardMarkup()

    match (item.type):
        case 'food':
            markup.add(
                InlineKeyboardButton(
                    text='🍖 Съесть',
                    callback_data=f'eat_{call.data}'
                )
            )
        case 'medicine':
            markup.add(
                InlineKeyboardButton(
                    text='💊 Выпить',
                    callback_data='drink_medicine'
                )
            )
        case 'car':
            markup.add(
                InlineKeyboardButton(
                    text='🚗 В путь!',
                    callback_data='car_menu'
                )
            )
        case 'lootbox':
            markup.add(
                InlineKeyboardButton(
                    text='📦 Открыть',
                    callback_data='open_lootbox'
                )
            )
        case 'rob':
            markup.add(
                InlineKeyboardButton(
                    text='🏦 Ограбить банк',
                    callback_data='rob_bank'
                )
            )
        case 'mask':
            if item.emoji == mask:
                markup.add(
                    InlineKeyboardButton(
                        text='❎ Снять',
                        callback_data='put_mask_off'
                    )
                )
            else:
                markup.add(
                    InlineKeyboardButton(
                        text='👺 Надеть',
                        callback_data=f'put_mask_on_{call.data}'
                    )
                )
        case 'key':
            markup.add(
                InlineKeyboardButton(
                    text='🔐 Чёрный рынок',
                    callback_data='darkweb'
                )
            )
        case 'phone':
            markup.add(
                InlineKeyboardButton(
                    text='📱 Использовать',
                    callback_data='cellphone_menu'
                )
            )
        case 'radio':
            markup.add(
                InlineKeyboardButton(
                    text='📻 Использовать',
                    callback_data='radio_menu'
                )
            )

    description = item.description or (
                '〰 описание предмета отсутствует. Обратитесь в приёмную,'
                ' если считаете, что это ошибка.'
            )

    if call.data in limited_items:
        itemsleft = cur.select(call.data, "globaldata").one()

        if itemsleft > 0:
            itemsleft = (
                f"\n\n🏪 В круглосуточном осталось <b>{itemsleft}</b> "
                "единиц этого товара"
            )
        else:
            itemsleft = "\n\n🚫🏪 В круглосуточном не осталось этого товара"

    else:
        itemsleft = ''

    return await call.message.answer(
        f'<i><b>{item.emoji} {item.ru_name}</b> - {description}{itemsleft}\n'
        f'\nУ вас <b>{count}</b> единиц этого предмета</i>',
        reply_markup=markup
    )


async def inventory(call: CallbackQuery) -> None:
    '''
    Callback for inventory

    :param call - callback:
    '''
    user_id = call.from_user.id
    markup = InlineKeyboardMarkup(row_width=6)

    itemlist = []
    item: str

    for item in ITEMS:
        if (
            await itemdata(user_id, item) != 'emptyslot'
            and await itemdata(user_id, item) is not None
        ):
            itemlist.append(await itemdata(user_id, item))

    if itemlist != []:
        markup.add(*itemlist)
    else:
        markup.add(
            InlineKeyboardButton(
                '🙈 Нет предметов',
                callback_data='no_items_in_inventory'
            )
        )

    if (
        cur.select("mask", "userdata").where(
            user_id=user_id
        ).one()
        not in ["", None]
    ):
        markup.add(
            InlineKeyboardButton(
                text='❎ Снять маску',
                callback_data='put_mask_off'
            )
        )

    markup.add(
        InlineKeyboardButton(
            text='⛰ Полезные ископаемые',
            callback_data='resources'
        )
    )

    markup.add(
        InlineKeyboardButton(
            text='🏪 Круглосуточный магазин',
            callback_data='shop_24'
        )
    )

    await call.message.answer('<i>Ваш инвентарь</i>', reply_markup=markup)


async def resources(call: CallbackQuery) -> None:
    '''
    Callback for mineral data

    :param call - callback:
    '''
    user_id = call.from_user.id
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    text = '<b>⛏ Ваши полезные ископамые</b>\n\n'
    for resourceitem in RESOURCES:
        resource = RESOURCES[resourceitem]
        amount = cur.select(resource.name, "userdata").where(
            user_id=user_id).one()
        name = resource.ru_name
        text += f'{name} - <b>{amount}</b> шт.\n'
    text += '\nПолезные ископаемые можно добывать в шахте в посёлке Гор' +\
            'ный. Для этого сначала нужно купить кирки в Агзамогорске' +\
            ' (при каждом вскапывании забирается одна кирка). ' +\
            'Затем вы можете продать выкопанные ископаемые в Глинянке'

    await call.message.answer(
        f'<i>{text}</i>', reply_markup=markup
    )


async def lootbox_button(user_id: int, message: Message) -> None:
    '''
    Callback for lootbox button

    :param user_id:
    :param message:
    '''
    mailbox = cur.select("last_box", "userdata").where(user_id=user_id).one()
    difference: float = current_time() - mailbox
    lootbox: int = cur.select("lootbox", "userdata").where(
        user_id=user_id).one()

    if difference >= 86400:
        cur.update("userdata").set(last_box=time.time()).where(
            user_id=user_id).commit()
    elif lootbox > 0:
        cur.update("userdata").add(lootbox=-1).where(
            user_id=user_id).commit()
    else:
        hours, minutes, seconds = get_time_units(difference)

        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text='🖇 Пригласить пользователей',
                callback_data='reflink'
            )
        )

        await message.answer(
            (
                "<i>&#10060; Проверять почтовый ящик можно только 1 раз в 24 "
                f"часа. До следующей проверки осталось {hours} часов {minutes}"
                f"  минут {seconds} секунд.\n\nЧтобы получать внеочередные ящики,"  # noqa
                " приглашайте пользователей в Живополис. За каждого приглашённ"
                "ого пользователя вы получаете лутбокс, с помощью которого мож"
                "но открыть ящик в любое время</i>"
            ),
            reply_markup=markup
        )
        return

    price, price_type = await lootbox_open()

    if isinstance(price, str):
        item = ITEMS[price]
        cur.update("userdata").add(**{item.name: 1}).where(
            user_id=user_id).commit()

        await message.answer(
            LOOTBOX[price_type].format(f"{item.emoji} {item.ru_name}")
        )
        return
    elif price_type == "money_steal":
        cur.update("userdata").add(balance=-price).where(
            user_id=user_id).commit()
    elif callable(price):
        return await price(message.chat.id)
    elif isinstance(price, int):
        cur.update("userdata").add(balance=price).where(
            user_id=user_id).commit()

    await message.answer(LOOTBOX[price_type].format(price))

    start = StartCommand()
    text = await start._private_start(user_id, True)
    assert text is not None

    with contextlib.suppress(Exception):
        await message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                *start._start_buttons(user_id)
            )
        )


async def sellitem(call: CallbackQuery, item: str) -> None:
    '''
    Callback for selling item on central market

    :param call - callback:
    :param user_id:
    '''
    user_id = call.from_user.id

    if item not in ITEMS:
        raise ValueError("no such item")

    coef = 1.5  # todo cur.execute('SELECT coef FROM globaldata').fetchone()[0]
    item_count = cur.select(item, "userdata").where(user_id=user_id).one()

    if item_count < 1:
        return await call.answer(
            '❌ У вас недостаточно единиц этого предмета',
            show_alert=True
        )

    cost = ITEMS[item].cost
    assert cost is not None
    cost = cost // coef

    cur.update("userdata").add(**{item: -1}).where(user_id=user_id).commit()
    cur.update("userdata").add(balance=cost).where(user_id=user_id).commit()

    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    await call.answer(
        f'Продажа прошла успешно. Ваш баланс: ${balance}',
        show_alert=True
    )

    await achieve(user_id, call.message.chat.id, "sell_achieve")


async def sellresource(call: CallbackQuery, resource: str) -> None:
    '''
    Callback for selling a mineral in Glinyanka

    :param call - callback:
    :param user_id:
    '''
    user_id = call.from_user.id

    if resource not in RESOURCES:
        raise ValueError("no such resource")

    res_count = cur.select(resource, "userdata").where(user_id=user_id).one()

    if res_count < 1:
        return await call.answer(
            '❌ У вас недостаточно единиц этого ресурса',
            show_alert=True
        )

    cost = RESOURCES[resource].cost
    assert cost is not None

    cur.update("userdata").add(**{resource: -1}).where(
        user_id=user_id).commit()
    cur.update("userdata").add(balance=cost).where(user_id=user_id).commit()

    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    await call.answer(
        f'Продажа прошла успешно. Ваш баланс: ${balance}',
        show_alert=True
    )
