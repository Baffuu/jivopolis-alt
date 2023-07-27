import contextlib

from loguru import logger

from ...misc.misc import get_embedded_link, tglog
from ..marketplace.marketplace import market
from ... import bot
from ...database import cur
from ...database.functions import buybutton
from ...items import ITEMS
from typing import Optional
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


async def shop(
    call: CallbackQuery,
    place: Optional[str | list] = None,
    items: Optional[list] = None,
    text: str = 'Что бы вы хотели купить?'
) -> None:
    '''
    Represents callback for any of existing shops

    :param call - callback:
    :param place:
    :param items - items that will be sold in shop
    :param text - text that will be sent
    '''
    place_ = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place is not None and place_ not in place and place_ != place:
        return await call.answer(
            text=(
                '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                'местности'
            ),
            show_alert=True
        )

    if items is not None:
        buttons = [buybutton(item) for item in items]

        markup = InlineKeyboardMarkup(row_width=1).\
            add(*list(filter(lambda item: item is not None, buttons))).\
            add(
                InlineKeyboardButton(
                    text='◀ Назад',
                    callback_data='cancel_action'
                )
               )
    else:
        markup = None

    await call.message.answer(
        text=f'<i>{text}</i>',
        reply_markup=markup,
    )


async def moda_menu(call: CallbackQuery) -> None:
    '''
    Callback for modashop menu

    :param call - callback:
    '''

    place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place != 'ТЦ МиГ':
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
            text='❄️ Новогодний отдел',
            callback_data='xmas_shop'
        ),
        InlineKeyboardButton(
            text='👺 Маскарадный отдел',
            callback_data='mask_clothes'
        )
    )

    await call.message.answer(
        '<i>&#128090; Добро пожаловать в <b>ModaShop</b>! Здесь вы можете '
        'купить любую одежду!</i>',
        reply_markup=markup,
    )


async def mall(call: CallbackQuery) -> None:
    '''
    Callback for mall menu

    :param call - callback:
    :param user_id:
    '''
    place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place != 'ТЦ МиГ':
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
            text='👚 ModaShop',
            callback_data='moda_menu'
        ),
        InlineKeyboardButton(
            text='🍔 Енот Кебаб',
            callback_data='enot_kebab'
        ),
        InlineKeyboardButton(
            text='🍚 Ресторан Япон Енот',
            callback_data='japan_shop'
        )
    )

    await call.message.answer(
        '<i>&#127978; Добро пожаловать в торговый центр!</i>',
        reply_markup=markup
    )


async def ticket_shop(call: CallbackQuery) -> None:
    '''
    Callback for ticket shop menu

    :param call - callback:
    '''
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text='🚇 Метро',
            callback_data='metro_tickets'
        ),
        InlineKeyboardButton(
            text='🚎 Городской троллейбус',
            callback_data='trolleybus_tickets'
        ),
        InlineKeyboardButton(
            text='🚆 Электропоезд экономкласса',
            callback_data='regtrain_tickets'
        ),
        InlineKeyboardButton(
            text='🚅 Скоростной поезд',
            callback_data='train_tickets'
        ),
        InlineKeyboardButton(
            text='🚋 Ридипольский трамвай',
            callback_data='tram_tickets'
        ),
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
        )

    await call.message.answer(
        '<i>🎫 Добро пожаловать в кассу! Билеты на какой вид транспорта'
        ' хотите купить?</i>',
        reply_markup=markup
    )


async def shop_24(call: CallbackQuery) -> None:
    '''
    Callback for 24-hour shop

    :param call - callback:
    '''
    buttons = [buybutton('bread', 'limited'),
               buybutton('pelmeni', 'limited'),
               buybutton('soup', 'limited'),
               buybutton('meat', 'limited'),
               buybutton('meatcake', 'limited'),
               buybutton('tea', 'limited')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer('<i>Что хотите купить?</i>', reply_markup=markup)


async def maximdom(call: CallbackQuery, floor: int) -> None:
    '''
    Callback for Maximdom mall

    :param call - callback:
    :param floor - floor of the mall:
    '''
    place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place != 'Площадь Максима':
        return await call.answer(
            text=(
                '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                'местности'
            ),
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1)
    match (floor):
        case 1:
            markup.add(
                InlineKeyboardButton(
                    text='🧱 Строительный магазин',
                    callback_data='building_shop'
                ),
                InlineKeyboardButton(
                    text='📱 Магазин техники им. Шелби',
                    callback_data='phone_shop'
                )
            )
        case 3:
            markup.add(
                InlineKeyboardButton(
                    text='🍔 Енот Кебаб',
                    callback_data='enot_kebab_shop'
                ),
                InlineKeyboardButton(
                    text='🍚 Ресторан Япон Енот',
                    callback_data='japan_shop'
                )
            )
    markup.add(
        InlineKeyboardButton(
            text='🛗 Лифт',
            callback_data='maximdom_elevator'
        )
    )

    await call.message.answer(
        '<i>🏬 Добро пожаловать в торговый центр Максимдом!'
        f'\n<b>{floor} этаж</b></i>',
        reply_markup=markup
    )


async def maximdom_elevator(call: CallbackQuery) -> None:
    '''
    Callback for Maximdom elevator menu

    :param call - callback:
    '''
    place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place != 'Площадь Максима':
        return await call.answer(
            text=(
                '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                'местности'
            ),
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1)
    for floor in range(1, 4):
        markup.add(
            InlineKeyboardButton(
                text=f'🛗 {floor} этаж',
                callback_data=f'maximdom_floor_{floor}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>🏬 Добро пожаловать в торговый центр Максимдом!</i>',
        reply_markup=markup
    )


class SlotData():
    def __init__(
        self,
        itemname: str,
        money: str,
        user_id: str,
        post_on_market: str,
        temp_id: int
    ) -> None:
        self.itemname = itemname
        self.cost = int(money)
        self.user_id = int(user_id)
        self.post_on_market = post_on_market != "False"
        try:
            self.id = market.get_by_temp(temp_id)
        except RuntimeError:
            self.id = temp_id


async def buyslot(call: CallbackQuery) -> None:
    user_id = call.from_user.id
    message = call.message

    data = call.data.split(' ')
    try:
        data = SlotData(data[1], data[2], data[3], data[4], data[5])
    except TypeError as e:
        logger.exception(e)
    try:
        market.remove(int(data.id))
    except ValueError:
        return await call.answer("🙀 Somebody already bought this product")
    except RuntimeError:
        pass
    if user_id == data.user_id:
        if message is None:
            await bot.edit_message_text(
                inline_message_id=call.inline_message_id,
                text="<i>Слот отменён продавцом</i>"
            )
        else:
            await message.edit_text(
                text='<i>Слот отменён продавцом</i>'
            )
        return cur.update("userdata").add(**{data.itemname: 1}).where(
            user_id=user_id).commit()
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    if balance < data.cost:
        return await call.answer('❌ У вас недостаточно средств', True)

    cur.update("userdata").add(**{data.itemname: 1}).where(
        user_id=user_id).commit()
    cur.update("userdata").add(balance=-data.cost).where(
        user_id=user_id).commit()
    cur.update("userdata").add(balance=data.cost).where(
        user_id=data.user_id).commit()

    item = ITEMS[data.itemname]

    with contextlib.suppress(Exception):
        await bot.send_message(
            data.user_id,
            f'{await get_embedded_link(user_id)} купил у вас <b>{item.emoji} '
            f'{item.ru_name}</b> за <b>${data.cost}</b>'
        )

    if data.cost > 0:
        await tglog(
            f'{await get_embedded_link(user_id)} купил <b>{item.emoji} '
            f'{item.ru_name}</b> за <b>${data.cost}</b>',
            '#user_getitem</i>'
        )

    with contextlib.suppress(Exception):
        await message.edit_text(
            f'<i>{await get_embedded_link(user_id)} купил <b>{item.emoji} '
            f'{item.ru_name}</b> за <b>${item.cost}</b>'
        )

    await call.answer("Спасибо за покупку", show_alert=True)


async def product_info(call: CallbackQuery):
    product_id = call.data.replace("product_info_", "")
    product = market.get_product(product_id)
    item = product.item
    message = (
        f"<b>{item.emoji} {item.ru_name}</b>"
        f"\n>>> <i>{item.description}</i>"
        f"\n            💍 Seller: {await get_embedded_link(product.owner)}&lt;"
    )
    await call.answer("🪡 I send you product info in private messages")
    await bot.send_message(
        call.from_user.id,
        message,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                f"💸 Buy for {product.cost}",
                callback_data=f"slot {item.name} {product.cost} {product.owner} True {product.id}"  # noqa
            )
        )
    )
    return product
