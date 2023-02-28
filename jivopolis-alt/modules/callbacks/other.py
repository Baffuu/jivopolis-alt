from ...database.sqlitedb import cur 
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

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

#async def change_rase(user_id: int, message: Message)