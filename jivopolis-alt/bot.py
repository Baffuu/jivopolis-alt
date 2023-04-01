from aiogram import Bot, Dispatcher
from .misc.config import TOKEN
from loguru import logger

logger = logger

bot = Bot(
    token=TOKEN, 
    parse_mode='html', 
    disable_web_page_preview=True
)
dp = Dispatcher(bot)