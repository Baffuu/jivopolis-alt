from ...database.functions import cur, conn, get_mask, bot, log_chat, get_link
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

async def chats(user_id: int, message: Message):
    rase = cur.execute(f"SELECT rase FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    markup = InlineKeyboardMarkup()

    match(rase):
        case '🐱':
            chat = 'Расовый чат Котов'
            url = 'https://t.me/joinchat/mWs48dy5cAo1ZmEy'
        case '🐶':
            chat = 'Расовый чат Собак'
            url = 'https://t.me/joinchat/yQ8X_uD1MydmNWIy'
        case '&#129437':
            chat = 'Расовый чат Енотов'
            url = 'https://t.me/joinchat/vuVCKuUIB2gxZTYy'
        case '&#128056;':
            chat = 'Расовый чат Жаб'
            url = 'https://t.me/joinchat/ACneINZ0hl43YTUy'
        case '&#129417;':
            chat = 'Расовый чат Сов'
            url = 'https://t.me/joinchat/nCt9oB_cX8I3NzMy'
        case _:
            chat = None

    if chat:
        markup.add(InlineKeyboardButton(text=chat, url=url))
    else:
        markup.add(InlineKeyboardButton(text='Выбрать расу', callback_data='change_rase'))
            
    markup.add(InlineKeyboardButton(text='🎮 Игровой клуб', url='https://t.me/+2UuPwVyac6lkYjRi'))
    await message.answer('<i><b>Официальные чаты Живополиса</b>\n&#128221; Приёмная для идей и вопросов: https://t.me/zhivolab\n&#128172; Чат для общения: https://t.me/chatzhivopolisa\n&#128163; Чат для флуда: https://t.me/jivopolis_flood\n&#128176; Рынок Живополиса: t.me/jivopolis_bazar\n&#128572; Посольство Живополиса в Котостане: https://t.me/posolstvo_jivopolis_in_kotostan\n{0}</i>'.format('Вы ещё не выбрали себе расу. Чтобы выбрать, нажмите на кнопку "Выбрать расу"\n' if chat=='' else ''), parse_mode = 'html', reply_markup = markup)

#todo async def change_rase(user_id: int, message: Message)

async def my_refferals(message: Message, user_id: int):
    user_mask = get_mask(user_id)
    nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    count = cur.execute(f"SELECT count(*) FROM userdata WHERE inviter_id = {user_id}").fetchone()[0]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='🖇 Реферальная ссылка', callback_data='reflink'))
    
    if count < 1:
        return await message.answer(f'<i><b><a href="tg://user?id={user_id}">{user_mask}{nick}</a></b>, вы пока никого не пригласили в Живополис :(</i>', parse_mode = 'html', reply_markup=markup)
        
    cur.execute(f"""
    SELECT * FROM userdata 
    WHERE refid = {user_id}
    ORDER BY -lastseen 
    LIMIT 100""")

    ref_num = 0
    users: str 

    for row in cur:
        ref_num += 1
        mask = get_mask(row[1])
        users+=f'\n{ref_num}. <a href = "{get_link(row[1])}">{mask}{row[7]}</a>'
    await message.answer(f'<i>&#128100; Пользователи, привлечённые <b><a href="tg://user?id={user_id}">{user_mask}{nick}</a></b>: <b>{users}</b></i>', parse_mode = 'html', reply_markup=markup)

async def get_cheque(call: CallbackQuery, user_id: int):
    money = int(call.data[6:])
    mask = get_mask(user_id)
    nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={user_id}").fetchone()[0]
    
    cur.execute(f"UPDATE userdata SET balance = balance + {money} WHERE user_id={user_id}"); conn.commit()
    
    if call.message != None:
        await bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'<i><b><a href="{get_link(user_id)}">{mask}{nick}</a></b> забрал <b>${money}</b></i>')
    else:
        await bot.edit_message_text(inline_message_id = call.inline_message_id, text = f'<i><b><a href="{get_link(user_id)}">{mask}{nick}</a></b> забрал <b>${money}</b></i>')
    if money > 0:
        await bot.send_message(log_chat, f'<i><b><a href="{get_link}">{mask}{nick}</a></b> забрал <b>${money}</b>\n#user_getcheck</i>')

async def cellphone_menu(call: CallbackQuery):
    a = call.from_user.id
    phone = cur.execute(f"SELECT phone FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if phone<1:
        return await call.answer('Вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро', show_alert = True)
        
    markup = InlineKeyboardMarkup(row_width = 1)

    markup.add(InlineKeyboardButton(text='📡 GPS', callback_data='gps'),
    InlineKeyboardButton(text='🚚 МиГ.Доставка', callback_data='delivery_app'),
    InlineKeyboardButton(text='🚂 ЖивГорТранс: Билеты', callback_data='tickets'),
    InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))

    await call.message.answer('<i>📱 Телефон - это удобная и современная вещь</i>', parse_mode='html', reply_markup = markup)