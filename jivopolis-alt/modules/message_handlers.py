import random
from .. import dp, bot, logger 
from ..database.sqlitedb import cur, conn
from ..database.functions import profile
from ..misc import get_embedded_link
from ..misc.config import hellos
from aiogram.types import Message
from aiogram.dispatcher.filters import Text

@dp.message_handler(Text(startswith="живополис", ignore_case=True))
async def chatbot_functions(message: Message):
    text = message.text[9:].lower()
    if text.startswith(', '): text = text[1:]
    if text.__contains__('привет'):
        await message.reply(f'<i>{random.choice(hellos)}</i>')
    elif text.__contains__('как дела'):
        await message.reply(f"<i>{random.choice(['Нормально', 'Нормально. А у тебя?', 'Типа того', 'Норм', 'Ну, нормас типа'])}</i>")
    elif text.__contains__('или'):
        await message.reply(f'<i>{random.choice(text.split(" или "))}</i>')
    elif text.__contains__('профиль'):
        await profile_alias_text(message)
    elif text.__contains__("баланс"):
        await my_balance_text(message)
    else:
        await message.reply(f"<i>{random.choice(['А?', 'Что надо?', 'Чё звал?', 'Ещё раз позовёшь - получишь бан!', 'И тебе привет', 'Да?'])}</i>")
        
@dp.message_handler(Text(startswith="профиль", ignore_case=True))
async def profile_alias_text(message: Message):
    if message.reply_to_message:
        await profile(message.reply_to_message.from_user.id, message)
    else:
        await profile(message.from_user.id, message)

@dp.message_handler(Text(equals='мой баланс', ignore_case=True))
async def my_balance_text(message: Message):
    user_id = message.from_user.id
    money = cur.execute(f'SELECT balance FROM userdata WHERE user_id={user_id}').fetchone()[0]
    await message.answer(f'<i><b>{await get_embedded_link(user_id)}</b> размахивает перед всеми своими накоплениями в количестве <b>${money}</b></i>')