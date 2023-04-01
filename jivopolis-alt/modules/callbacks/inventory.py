import random

from math import ceil
from ...misc import (
    Item, allitems, 
    lootbox_open, LOOTBOX, 
    get_time_units, current_time
)
from ...misc.config import limeteds, ITEMS

from ...database.sqlitedb import cur, conn
from ...database.functions import itemdata

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

async def itemdesc(call: CallbackQuery, user_id: int) -> None:
    '''
    Callback for item info 
    
    :param call - callback:
    :param user_id:
    '''
    try:
        item: Item = allitems[call.data]
    except KeyError:
        return await call.answer('Этot predmet не существует')
    count = cur.execute(f"SELECT {call.data} FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if count < 1:
        return await call.message.answer('<i>🚫 У вас нет этого предмета</i>', reply_markup = markup, parse_mode = 'html')
    
    try:
        mask = cur.execute(f"SELECT mask FROM userdata WHERE user_id={user_id}").fetchone()[0]
    except TypeError:
        mask = None

    markup = InlineKeyboardMarkup()

    match (item.type):
        case 'food': 
            markup.add(InlineKeyboardButton(text='🍖 Съесть', callback_data=f'eat_{call.data}'))
        case 'medicine':
            markup.add(InlineKeyboardButton(text='💊 Выпить', callback_data='drink_medicine'))
        case 'car':
            markup.add(InlineKeyboardButton(text='🚗 В путь!', callback_data='cardrive'))
        case 'lootbox':
            markup.add(InlineKeyboardButton(text='📦 Открыть', callback_data='open_lootbox'))
        case 'rob':
            markup.add(InlineKeyboardButton(text='🏦 Ограбить банк', callback_data='rob_bank'))
        case 'mask':
            if item.emoji == mask:
                markup.add(InlineKeyboardButton(text='❎ Снять', callback_data='put_mask_off'))
            else:
                markup.add(InlineKeyboardButton(text='👺 Надеть', callback_data=f'put_mask_on_{call.data}'))
        case 'key':
            markup.add(InlineKeyboardButton(text='🔐 Чёрный рынок', callback_data='darkweb'))
        case 'phone':
            markup.add(InlineKeyboardButton(text='📱 Использовать', callback_data='cellphone_menu'))

    description = item.description
    
    if not description: 
        description = '〰 описание предмета отсутствует. Обратитесь в приёмную, если считаете, что это ошибка.'
    
    if call.data in limeteds:
        itemsleft = cur.execute(f"SELECT {item} FROM globaldata").fetchone()[0]
        
        if itemsleft > 0:
            itemsleft = f"\n\n🏪 В круглосуточном осталось <b>{itemsleft}</b> единиц этого товара"
        else:
            itemsleft = "\n\n🚫🏪 В круглосуточном не осталось этого товара"

    else:
        itemsleft = ''
    
    return await call.message.answer(f'<i><b>{item.emoji} {item.ru_name}</b> - {description}{itemsleft}\n\nУ вас <b>{count}</b> единиц этого предмета</i>', reply_markup = markup, parse_mode = 'html')


async def inventory(call: CallbackQuery) -> None:
    '''
    Callback for inventory
    
    :param call - callback:
    '''
    user_id = call.from_user.id
    markup = InlineKeyboardMarkup(row_width = 6)

    itemlist = []
    item: str

    for item in ITEMS:
        if await itemdata(user_id, item) != 'emptyslot':
            itemlist.append(await itemdata(user_id, item))

    if itemlist != []:
        markup.add(*itemlist)
    else:
        markup.add(InlineKeyboardButton('🙈 Нет предметов', callback_data='no_items_in_inventory'))
    
    try:
        mask = cur.execute(f"SELECT mask FROM userdata WHERE user_id={user_id}").fetchone()[0]
        print(mask)
    except TypeError:
        mask = ''
    if not mask:
        mask = ''
        
    if mask != '':
        markup.add(InlineKeyboardButton(text='❎ Снять маску', callback_data='put_mask_off'))

    markup.add(InlineKeyboardButton(text='🏪 Круглосуточный магазин', callback_data='shop_24'))
    
    await call.message.answer('<i>Ваш инвентарь</i>', reply_markup = markup, parse_mode = 'html')


async def lootbox_button(user_id: int, message: Message) -> None:
    '''
    Callback for lootbox button
    
    :param call - callback:
    :param user_id:
    '''
    mailbox = cur.execute(f"SELECT last_box FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    difference: float = current_time() - mailbox
    lootbox: int = cur.execute(f"SELECT lootbox FROM userdata WHERE user_id={user_id}").fetchone()[0]
    
    if difference >= 86400:
        cur.execute(f"UPDATE userdata SET last_box = {current_time()} WHERE user_id = {user_id}")
        conn.commit()
    elif lootbox > 0:
        cur.execute(f"UPDATE userdata SET lootbox = lootbox - 1 WHERE user_id = {user_id}")
        conn.commit()
    else:
        hours, minutes, seconds = get_time_units(difference)
        
        markup = InlineKeyboardMarkup().\
            add(InlineKeyboardButton(text='🖇 Пригласить пользователей', callback_data='reflink'))
        
        return await message.answer(
            f'<i>&#10060; Проверять почтовый ящик можно только 1 раз в 24 часа. До следующей проверки осталось {hours} часов {minutes} минут {seconds} секунд.\
            \n\nЧтобы получать внеочередные ящики, приглашайте пользователей в Живополис. За каждого приглашённого пользователя вы получаете лутбокс,\
            с помощью которого можно открыть ящик в любое время</i>', 
            parse_mode='html', 
            reply_markup=markup
        )

    price, price_type = await lootbox_open()

    if isinstance(price, str):
        item = allitems[price]
        cur.execute(f"UPDATE userdata SET {item.name}={item.name}+1 WHERE user_id={user_id}")
        conn.commit()

        return await message.reply(LOOTBOX[price_type].format(f"{item.emoji} {item.ru_name}"))
    return await message.reply(LOOTBOX[price_type].format(price))


async def sellitem(call: CallbackQuery, item: str) -> None:
    '''
    Callback for selling item on central market
    
    :param call - callback:
    :param user_id:
    '''
    user_id = call.from_user.id

    if item not in ITEMS:
        raise ValueError("no such item")

    markup = InlineKeyboardMarkup(row_width = 3)

    coef = 1.5 #todo cur.execute('SELECT coef FROM globaldata').fetchone()[0]
    item_count = cur.execute(f"SELECT {item} FROM userdata WHERE user_id={user_id}").fetchone()[0]
    
    if item_count < 1:
        return await call.answer('❌ У вас недостаточно единиц этого предмета', show_alert = True)
        
    cost = ITEMS[item][3]//coef
    
    cur.execute(f"UPDATE userdata SET {item}={item}-1 WHERE user_id={user_id}"); conn.commit()
    cur.execute(f"UPDATE userdata SET balance=balance+{cost} WHERE user_id={user_id}"); conn.commit()
    
    balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id={user_id}").fetchone()[0]
    await call.answer(f'Продажа прошла успешно. Ваш баланс: ${balance}', show_alert = True)
    
    '''cur.execute('UPDATE userdata SET sold=sold+1 WHERE user_id=?', (a,))
    conn.commit()
    cursor.execute("SELECT sold FROM userdata WHERE user_id=?", (a,))
    sold = cursor.fetchone()[0]
    if sold>=10:
        await achieve(a, call.message.chat.id, 'soldach')'''

