from ...database.sqlitedb import cur, conn
from ...database.functions import buybutton

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

async def shop(
    call: CallbackQuery,
    place: str | list = None,
    items: list = None,
    text: str = 'Что бы вы хотели купить?'
):
    cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}")

    if cur.fetchone()[0] not in place and cur.fetchone()[0] != place:
        return

    buttons = [buybutton(item) for item in items]
    
    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer(
        text=f'<i>{text}</i>', 
        reply_markup=markup,
        parse_mode='html'
    )


async def moda_menu(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place != 'ТЦ МиГ':
        return

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='❄️ Новогодний отдел', callback_data='xmas_shop'),
                InlineKeyboardButton(text='👺 Маскарадный отдел', callback_data='mask_clothes'))

    return await call.message.answer('<i>&#128090; Добро пожаловать в <b>ModaShop</b>! Здесь вы можете купить любую одежду!</i>', reply_markup = markup, parse_mode = 'html')


async def mall(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'ТЦ МиГ':
        return

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='👚 ModaShop', callback_data='moda_menu'), 
               InlineKeyboardButton(text='🍔 Енот Кебаб', callback_data='enot_kebab'),
               InlineKeyboardButton(text='🍚 Ресторан Япон Енот', callback_data='japan_shop'))

    return await call.message.answer('<i>&#127978; Добро пожаловать в торговый центр!</i>', reply_markup = markup, parse_mode = 'html')


async def shop_24(call: CallbackQuery):
    buttons = [buybutton('bread', 'limited'), 
               buybutton('pelmeni', 'limited'),
               buybutton('soup', 'limited'), 
               buybutton('meat', 'limited'), 
               buybutton('meatcake', 'limited'), 
               buybutton('tea', 'limited')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html')
