from aiogram import Bot, Dispatcher
from .config import TOKEN
from aiogram.bot.api import log

logger = log

bot = Bot(token=TOKEN, parse_mode='html', disable_web_page_preview=True)
dp = Dispatcher(bot)