import random
from .. import dp, bot, logger 
from ..database.functions import profile
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
        await profile_alias(message)
    else:
        await message.reply(f"<i>{random.choice(['А?', 'Что надо?', 'Чё звал?', 'Ещё раз позовёшь - получишь бан!', 'И тебе привет', 'Да?'])}</i>")
        
@dp.message_handler(Text(startswith="профиль", ignore_case=True))
async def profile_alias(message: Message):
    if message.reply_to_message:
        await profile(message.reply_to_message.from_user.id, message)
    else:
        await profile(message.from_user.id, message)